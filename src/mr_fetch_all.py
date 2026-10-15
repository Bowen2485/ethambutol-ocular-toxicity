# -*- coding: utf-8 -*-
"""
Step 6e - Complete the FinnGen regional cache for all MR exposures.

The first fetch loop queried one small window at a time and, for each outcome,
re-read overlapping regions; that generated thousands of range requests.  With the
tabix reader fixed, whole-chromosome spans can be fetched in one go, so this
script downloads one cache file per (exposure, outcome, chromosome) covering the
full instrument span, then the estimates are assembled from the cache by
mr_assemble.py.

It is resumable: a cache file that already exists is reused.

Outputs -> data/raw/opengwas/mrbig_<gwas>_<outcome>_<chrom>.tsv
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

from mr_analysis import open_tabix, parse_lines        # noqa: E402

OUTCOMES = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
            "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]


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
    print(f"[plan] {len(inst)} exposures x {len(OUTCOMES)} outcomes")

    tbs: dict[str, object] = {}
    total = 0
    t0 = time.time()
    for gid, d in inst.items():
        for outcome in OUTCOMES:
            for chrom, grp in d.groupby("chrom"):
                cache = RAW / f"mrbig_{gid}_{outcome}_{chrom}.tsv"
                if cache.exists() and cache.stat().st_size > 1:
                    continue
                if outcome not in tbs:
                    tbs[outcome] = open_tabix(outcome)
                tb = tbs[outcome]
                if tb is None:
                    continue
                lo = max(1, int(grp["pos"].min()) - 250_000)
                hi = int(grp["pos"].max()) + 250_000
                try:
                    lines = tb.query(str(chrom), lo, hi)
                except Exception as exc:  # noqa: BLE001
                    print(f"  [fail] {gid} {outcome} chr{chrom}: "
                          f"{type(exc).__name__} {str(exc)[:80]}")
                    cache.write_text("", encoding="utf-8")
                    continue
                out = parse_lines(lines)
                out.to_csv(cache, sep="\t", index=False)
                total += len(out)
                print(f"  [{time.time()-t0:6.0f}s] {gid[:18]:18s} {outcome:26s} "
                      f"chr{chrom:>2} span={hi-lo:>10,} -> {len(out):>7,} variants")
    print(f"\n[done] {total:,} new variants cached in {time.time()-t0:.0f}s")
    n = len(list(RAW.glob("mrbig_*.tsv")))
    print(f"[cache] {n} cache files present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
