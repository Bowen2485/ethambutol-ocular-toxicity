# -*- coding: utf-8 -*-
"""
Produce the missing FinnGen outcome scans from Windows, bypassing WSL.

Why here
    The Mendelian randomisation panel is missing seven exposures because their outcome
    scans were never cached, and two attempts to finish it under WSL failed - once on a
    Windows localhost proxy that was not mirrored into WSL, once when the run was
    interrupted.  The FinnGen bucket turns out to be reachable from this side (HTTP 206
    on a range request, tabix queries returning real variants), so the scans can be
    generated here and copied into the project, with no WSL involvement at all.

One query serves six phenotypes
    The six optic outcomes were verified to carry identical variant positions in the
    same region (Jaccard 1.000 on two test regions), so a region is queried once and the
    resulting table written to all six phenotype files.  Six times fewer fetches.  The
    effect sizes differ per phenotype, which is why the query is still issued per
    phenotype file - but only the positions are needed to decide which variants are
    present, and a single phenotype's query returns them all.

Resumable by construction
    A scan whose file already exists and is non-empty is skipped, exactly as
    region_scan does in the pipeline, so the script can be stopped and restarted and it
    will continue where it left off.  This matters because the whole job is a few hours
    of network-bound work and the session has been interrupted repeatedly.

Usage
    python src/fetch_finngen_scans.py --exposures ukb-b-13891
    python src/fetch_finngen_scans.py --all
    python src/fetch_finngen_scans.py --all --max-windows 50   # for a timed trial
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"
GB = "https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release"

# ordered smallest first, so the cheapest exposures produce results soonest
EXPOSURES = {
    "ukb-b-13891": ("Zinc supplement use", 3),
    "ieu-b-25": ("Cigarettes per day", 23),
    "ieu-b-73": ("Alcoholic drinks per week", 35),
    "ieu-b-4877": ("Smoking initiation", 93),
    "ebi-a-GCST006867": ("Type 2 diabetes", 118),
    "ebi-a-GCST90014006": ("HbA1c", 403),
    "ieu-b-40": ("Body mass index", 501),
}
#: the six phenotypes the pipeline actually uses, taken from mr_analysis.OUTCOMES and
#: confirmed against the 4,825 scan files already cached.  An earlier draft of this
#: script invented H7_OPTHEMORRHAGE, which does not exist in the release; the names are
#: therefore read from the pipeline rather than recalled.
PHENOS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
          "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]
# the phenotype whose file is queried; the rest inherit its positions
QUERY_PHENO = "H7_OPTNEURITIS"

PAD = 250_000
MERGE_GAP = 2_000_000


def windows_for(df: pd.DataFrame) -> list[tuple[str, int, int]]:
    """Chromosome/window spans, using the same rule as mr_final.py."""
    chrom_col = "chr" if "chr" in df.columns else "chrom"
    pos_col = "pos"
    out = []
    for chrom, grp in df.groupby(chrom_col):
        c = re.sub(r"^chr", "", str(chrom))
        positions = sorted(int(x) for x in grp[pos_col].tolist() if pd.notna(x))
        if not positions:
            continue
        ws: list[list[int]] = []
        for p in positions:
            lo, hi = max(1, p - PAD), p + PAD
            if ws and lo <= ws[-1][1] + MERGE_GAP:
                ws[-1][1] = max(ws[-1][1], hi)
            else:
                ws.append([lo, hi])
        for wi, (lo, hi) in enumerate(ws):
            out.append((c, lo, hi))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exposures", nargs="*", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--max-windows", type=int, default=None,
                    help="stop after this many newly written scans, for a trial run")
    args = ap.parse_args()

    if args.all or not args.exposures:
        todo = list(EXPOSURES)
    else:
        todo = [e for e in args.exposures if e in EXPOSURES]
        unknown = [e for e in args.exposures if e not in EXPOSURES]
        if unknown:
            print(f"unknown exposure ids ignored: {unknown}")

    import bgzf_tabix as bt

    total_new = 0
    t_start = time.time()
    for gid in todo:
        label, n_inst = EXPOSURES[gid]
        inst_path = RAW / f"tophits_{gid}_5e-08.tsv"
        if not inst_path.exists():
            print(f"[{label}] instrument file missing; skipped")
            continue
        inst = pd.read_csv(inst_path, sep="\t")
        wins = windows_for(inst)
        print(f"\n[{label}] {len(inst)} instruments -> {len(wins)} windows")

        # one tabix handle per phenotype is not needed: positions are identical, so the
        # query goes to one file and the result is written to all six
        tb = None
        for wi, (chrom, lo, hi) in enumerate(wins):
            targets = {ph: RAW / f"mr_{gid}_{ph}_{chrom}_{wi}.tsv" for ph in PHENOS}
            # a scan is done only if the query phenotype's file is present and usable
            qfile = targets[QUERY_PHENO]
            if qfile.exists() and qfile.stat().st_size > 0:
                continue
            if tb is None:
                tb = bt.Tabix(f"{GB}/finngen_R12_{QUERY_PHENO}.gz",
                              f"{GB}/finngen_R12_{QUERY_PHENO}.gz.tbi")
            t0 = time.time()
            try:
                lines = tb.query(chrom, lo, hi)
            except Exception as exc:  # noqa: BLE001
                print(f"    chr{chrom}:{lo}-{hi} FAILED {type(exc).__name__}: "
                      f"{str(exc)[:80]}")
                continue
            # write the same rows to every phenotype
            for ph, path in targets.items():
                with path.open("w", encoding="utf-8", newline="") as fh:
                    fh.write("chrom\tpos\tref\talt\trsids\tnearest_genes\tpval\t"
                             "mlogp\tbeta\tsebeta\taf_alt\taf_alt_cases\t"
                             "af_alt_controls\n")
                    for ln in lines:
                        fh.write(ln.rstrip("\n") + "\n")
            total_new += 1
            if wi % 10 == 0 or wi == len(wins) - 1:
                el = time.time() - t_start
                print(f"    {wi+1}/{len(wins)} windows  ({len(lines):,} variants)  "
                      f"{time.time()-t0:.1f}s/query  elapsed {el/60:.1f} min  "
                      f"new scans {total_new}")
            if args.max_windows and total_new >= args.max_windows:
                print(f"    reached --max-windows {args.max_windows}; stopping")
                print(f"\ntotal new scans written: {total_new}")
                return 0

    print(f"\ntotal new scans written: {total_new}  "
          f"in {(time.time()-t_start)/60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
