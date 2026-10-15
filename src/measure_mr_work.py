# -*- coding: utf-8 -*-
"""
Measure how much of the MR scan work is done and how much remains.

The MR loop caches one file per (exposure, outcome, chromosome, window).  Because the
instrument fetch stage completed for all ten exposures before the job was
interrupted, everything still outstanding is outcome-side scanning, which is the
slow part.  This step counts what exists so the remaining cost can be estimated
instead of guessed.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"
TAB = ROOT / "data" / "raw" / "finngen"

EXPOSURES = {
    "ebi-a-GCST90103634": "eGFR (creatinine)",
    "ebi-a-GCST90025945": "Cystatin C",
    "ebi-a-GCST90025946": "Serum creatinine",
    "ebi-a-GCST006867": "Type 2 diabetes",
    "ebi-a-GCST90014006": "HbA1c",
    "ieu-b-4877": "Smoking initiation",
    "ieu-b-25": "Cigarettes per day",
    "ieu-b-73": "Alcoholic drinks per week",
    "ukb-b-13891": "Zinc supplement use",
    "ieu-b-40": "Body mass index",
}

print("=" * 74)
print("1. Instruments already retrieved (these persist in the tophits cache)")
print("=" * 74)
total_inst = 0
for gid, label in EXPOSURES.items():
    p = RAW / f"tophits_{gid}_5e-08.tsv"
    if p.exists():
        n = max(p.read_text(encoding="utf-8", errors="replace").count("\n") - 1, 0)
        total_inst += n
        print(f"  {label:24s} {n:>5,} instruments")
    else:
        print(f"  {label:24s} not fetched")
print(f"  {'TOTAL':24s} {total_inst:>5,} instruments across the panel")

print()
print("=" * 74)
print("2. Outcome scan cache")
print("=" * 74)
scans = list(RAW.glob("mr_*.tsv"))
print(f"  scan files present: {len(scans):,}")
by_exp = Counter()
by_out = Counter()
for p in scans:
    parts = p.stem.split("_")
    # mr_<gwasid>_<phenotype>_<chrom>_<window>
    if len(parts) >= 5:
        by_exp[parts[1]] += 1
        by_out[parts[2]] += 1
print("\n  by exposure:")
for gid, n in by_exp.most_common():
    print(f"      {EXPOSURES.get(gid, gid):24s} {n:>6,} scans")
print("\n  by outcome:")
for ph, n in by_out.most_common():
    print(f"      {ph:28s} {n:>6,} scans")

print()
print("=" * 74)
print("3. What the remaining work looks like")
print("=" * 74)
# a scan covers one chromosome-window; 22 autosomes and a window count that depends
# on the instrument span, so estimate from what has been observed
per_exp_chrom = defaultdict(set)
for p in scans:
    parts = p.stem.split("_")
    if len(parts) >= 5:
        per_exp_chrom[parts[1]].add((parts[2], parts[3]))
print("  distinct (outcome, chromosome) pairs completed per exposure:")
for gid, s in per_exp_chrom.items():
    print(f"      {EXPOSURES.get(gid, gid):24s} {len(s):>5,}")
print("\n  A complete panel needs every exposure x 6 outcomes x 22 autosomes, so the")
print("  realistic requirement is on the order of 10 x 6 x 22 = 1,320 scans at the")
print("  minimum, and more where instruments span several windows.")

print()
print("=" * 74)
print("4. FinnGen index files (the outcome sources)")
print("=" * 74)
for p in sorted(TAB.glob("*.tbi")):
    print(f"  {p.name}  ({p.stat().st_size/1024:.0f} KB)")
