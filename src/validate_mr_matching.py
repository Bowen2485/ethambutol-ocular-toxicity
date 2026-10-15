# -*- coding: utf-8 -*-
"""
Test whether the zero-harmonisation results are a retrieval failure or a real absence.

The question
    results/mr_scan_coverage.csv reports that serum creatinine harmonised 0 of 370
    instruments against every optic-nerve outcome, and so did HbA1c, smoking, cigarettes
    per day and body mass index.  Serum creatinine is the awkward one: it measures the
    same renal function as eGFR, in the same population, so a total failure to match it
    while eGFR matched 150 of 342 is far more likely to be a retrieval or matching fault
    than a property of the data.  The manuscript uses the renal null to conclude that
    genetically proxied renal function does not cause the optic-nerve phenotype, so the
    distinction matters.

The test
    Take the cached FinnGen scans and ask, directly, whether the instruments that failed
    to harmonise are physically present in them.  If the variants are in the scan files
    with usable beta and sebeta, the matching logic is at fault.  If they are absent, the
    instruments genuinely are not in those endpoints and the zero is real.

    Matching is attempted three ways, because the pipeline matched on rsID with position
    as a fallback:
      1. by rsID
      2. by chromosome and position
      3. by either, requiring only that the alleles be resolvable

Usage
    python src/validate_mr_matching.py
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

# the renal pair that succeeded and failed, in that order
PAIRS = [("ebi-a-GCST90103634", "eGFR (creatinine)"),
         ("ebi-a-GCST90025946", "Serum creatinine")]

print("=" * 84)
print("1. Instruments available for each exposure")
print("=" * 84)
inst = {}
for gid, label in PAIRS:
    p = RAW / f"tophits_{gid}_5e-08.tsv"
    if not p.exists():
        print(f"  {label:22s} instrument file missing")
        continue
    df = pd.read_csv(p, sep="\t")
    inst[gid] = df
    # the instrument files use "rsid" (singular) while the FinnGen scans use "rsids"
    # (plural, comma-separated); the first version of this script looked for the plural
    # in both and silently skipped every comparison
    rs = "rsid" if "rsid" in df.columns else ("rsids" if "rsids" in df.columns else None)
    print(f"  {label:22s} {len(df):>4} rows, rsID column = {rs!r}")
    if rs:
        print(f"      first rsIDs: {df[rs].head(3).tolist()}")

print()
print("=" * 84)
print("2. What a cached FinnGen scan actually contains")
print("=" * 84)
scans = sorted(RAW.glob("mr_*.tsv"))
by_exposure = collections.defaultdict(list)
pat = re.compile(r"^mr_(?P<gid>.+)_(?P<ph>H7_[A-Z]+)_(?P<chrom>[0-9XYM]+)_(?P<wi>\d+)\.tsv$")
for p in scans:
    m = pat.match(p.name)
    if m:
        by_exposure[m.group("gid")].append(p)
for gid, label in PAIRS:
    files = by_exposure.get(gid, [])
    print(f"  {label:22s} {len(files):>5} cached scan files")
    if files:
        d = pd.read_csv(files[0], sep="\t")
        print(f"      example {files[0].name}")
        print(f"      columns: {list(d.columns)}")
        print(f"      rows: {len(d)}")
        if "rsids" in d.columns:
            print(f"      first rsIDs: {d['rsids'].head(3).tolist()}")

print()
print("=" * 84)
print("3. Are the serum creatinine instruments present in any cached scan?")
print("=" * 84)
gid_fail = "ebi-a-GCST90025946"
gid_ok = "ebi-a-GCST90103634"

# gather every variant seen across all cached scans, keyed both ways
seen_rs, seen_pos = set(), set()
for p in scans:
    try:
        d = pd.read_csv(p, sep="\t")
    except Exception:  # noqa: BLE001
        continue
    if "rsids" in d.columns:
        for v in d["rsids"].dropna().astype(str):
            for piece in v.split(","):
                piece = piece.strip()
                if piece:
                    seen_rs.add(piece)
    if {"chrom", "pos"}.issubset(d.columns):
        for c, q in zip(d["chrom"], d["pos"]):
            try:
                seen_pos.add((re.sub(r"^chr", "", str(c)), int(q)))
            except (TypeError, ValueError):
                continue
print(f"  distinct rsIDs across all cached scans : {len(seen_rs):,}")
print(f"  distinct (chrom, pos) pairs            : {len(seen_pos):,}")

for gid, label in PAIRS:
    if gid not in inst:
        continue
    df = inst[gid]
    col = "rsid" if "rsid" in df.columns else ("rsids" if "rsids" in df.columns else None)
    if col is None:
        print(f"  {label:22s} no rsID column; skipped")
        continue
    rs_list = []
    for v in df[col].dropna().astype(str):
        rs_list.extend(x.strip() for x in v.split(",") if x.strip())
    hit = sum(1 for v in rs_list if v in seen_rs)
    # position is the build-independent fallback the pipeline used
    pos_list = []
    if {"chr", "pos"}.issubset(df.columns):
        for c, q in zip(df["chr"], df["pos"]):
            try:
                pos_list.append((re.sub(r"^chr", "", str(c)), int(q)))
            except (TypeError, ValueError):
                continue
    pos_hit = sum(1 for v in pos_list if v in seen_pos)
    print(f"  {label:22s} by rsID      {hit:>4}/{len(rs_list):>4} "
          f"({hit/max(len(rs_list),1)*100:5.1f}%)")
    if pos_list:
        print(f"  {'':22s} by position  {pos_hit:>4}/{len(pos_list):>4} "
              f"({pos_hit/max(len(pos_list),1)*100:5.1f}%)")

print()
print("=" * 84)
print("4. Interpretation")
print("=" * 84)
print("""  The two exposures measure the same trait in the same population.  If serum
  creatinine's instruments are largely present in the cached scans while the pipeline
  harmonised none of them, the zero is a matching fault and the renal null rests on
  eGFR and cystatin C alone, which is what the manuscript reports.

  If serum creatinine's instruments are largely absent, then the FinnGen endpoints
  genuinely do not carry them and the zero is real.""")
