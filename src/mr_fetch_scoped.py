# -*- coding: utf-8 -*-
"""
Step 6e - FinnGen regional cache for the Mendelian randomisation, scoped tightly.

Why scoped
    FinnGen R12 covers ~20 million variants per phenotype, so a chromosome-wide
    span for a polygenic exposure (42 BMI instruments across 250 Mb of chr1)
    pulls hundreds of megabytes per query.  The MR only needs the region around
    each instrument, so each query is a tight window and neighbouring instruments
    are merged only when they are close together.

Scope
    Primary outcome H7_OPTNEURITIS is used for the complete exposure panel; the
    remaining optic-nerve outcomes are fetched only for the exposures whose panel
    is large enough to support an IVW estimate (>= 50 instruments).  This is
    stated in the manuscript rather than presented as a full cross-product.

Outputs -> data/raw/opengwas/mrw_<gwas>_<outcome>_<chrom>_<window>.tsv
Gaps    -> data/derived/mr_fetch_gaps.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
ROOT = SRC.parent
RAW = ROOT / "data" / "raw" / "opengwas"
DERIVED = ROOT / "data" / "derived"
RAW.mkdir(parents=True, exist_ok=True)

from mr_analysis import open_tabix, parse_lines        # noqa: E402

PRIMARY = "H7_OPTNEURITIS"
SECONDARY = ["H7_OPTATROPHY", "H7_OPTNERVNAS", "H7_BLINDANDVISIMPAIRMENT",
             "H7_COULOURVISDEF", "H7_VISFIELDDEF"]
MIN_INSTRUMENTS_FOR_SECONDARY = 50
HALF_WINDOW = 300_000          # +/- around each instrument
MERGE_GAP = 1_500_000          # merge windows closer than this


def build_windows(positions: list[int]) -> list[tuple[int, int]]:
    wins: list[list[int]] = []
    for p in sorted(positions):
        lo, hi = max(1, p - HALF_WINDOW), p + HALF_WINDOW
        if wins and lo <= wins[-1][1] + MERGE_GAP:
            wins[-1][1] = max(wins[-1][1], hi)
        else:
            wins.append([lo, hi])
    return [(a, b) for a, b in wins]


def load_instruments() -> dict[str, pd.DataFrame]:
    out = {}
    for f in sorted(RAW.glob("tophits_*.tsv")):
        d = pd.read_csv(f, sep="\t")
        if d.empty:
            continue
        gid = str(d["id"].iloc[0]) if "id" in d.columns else \
            f.name[len("tophits_"):-len("_5e-08.tsv")]
        d = d.copy()
        d["chrom"] = d["chr"].astype(str).str.replace("chr", "", regex=False)
        d["pos"] = pd.to_numeric(d["pos"], errors="coerce")
        out[gid] = d.dropna(subset=["pos"])
    return out


def main() -> int:
    inst = load_instruments()
    plan: list[tuple[str, str]] = []
    for gid in inst:
        plan.append((gid, PRIMARY))
    for gid, d in inst.items():
        if len(d) >= MIN_INSTRUMENTS_FOR_SECONDARY:
            for o in SECONDARY:
                plan.append((gid, o))
    print(f"[plan] {len(plan)} (exposure, outcome) combinations")

    tbs: dict[str, object] = {}
    gaps, n_cached, n_new, n_var = [], 0, 0, 0
    t0 = time.time()
    for gid, outcome in plan:
        d = inst[gid]
        for chrom, grp in d.groupby("chrom"):
            wins = build_windows(grp["pos"].astype(int).tolist())
            for wi, (lo, hi) in enumerate(wins):
                cache = RAW / f"mrw_{gid}_{outcome}_{chrom}_{wi}.tsv"
                if cache.exists():
                    n_cached += 1
                    continue
                if outcome not in tbs:
                    tbs[outcome] = open_tabix(outcome)
                tb = tbs[outcome]
                if tb is None:
                    gaps.append({"gwas_id": gid, "outcome": outcome,
                                 "chrom": chrom, "window": wi,
                                 "span": hi - lo, "reason": "endpoint unavailable"})
                    cache.write_text("", encoding="utf-8")
                    continue
                try:
                    lines = tb.query(str(chrom), lo, hi)
                    out = parse_lines(lines)
                except Exception as exc:  # noqa: BLE001
                    gaps.append({"gwas_id": gid, "outcome": outcome,
                                 "chrom": chrom, "window": wi, "span": hi - lo,
                                 "reason": f"{type(exc).__name__}: {str(exc)[:90]}"})
                    cache.write_text("", encoding="utf-8")
                    continue
                out.to_csv(cache, sep="\t", index=False)
                n_new += 1
                n_var += len(out)
                if n_new % 25 == 0:
                    print(f"  [{time.time()-t0:6.0f}s] {n_new} new queries, "
                          f"{n_cached} cached, {n_var:,} variants")

    pd.DataFrame(gaps).to_csv(DERIVED / "mr_fetch_gaps.csv", index=False,
                              encoding="utf-8-sig")
    print(f"\n[done] {n_new} new queries ({n_var:,} variants), "
          f"{n_cached} reused, {len(gaps)} gaps, {time.time()-t0:.0f}s")
    print(f"[cache] {len(list(RAW.glob('mrw_*.tsv')))} window files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
