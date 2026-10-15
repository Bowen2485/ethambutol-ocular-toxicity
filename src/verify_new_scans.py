# -*- coding: utf-8 -*-
"""
Verify that a newly fetched scan is structurally identical to a cached one.

The scans produced here have to be indistinguishable from those the pipeline wrote
under WSL, because region_scan reads them back with a plain text read and harmonise
then matches on the columns.  If the header or the column count differed, the
harmonisation would silently return nothing and the exposure would look as though it
had no instruments - the same failure mode that produced a spurious zero for serum
creatinine earlier in this work.

This compares a new file against an existing cached file: header, column count, row
count, and the shape of the values.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

NEW_EXPOSURES = ["ukb-b-13891", "ieu-b-25", "ieu-b-73", "ieu-b-4877",
                 "ebi-a-GCST006867", "ebi-a-GCST90014006", "ieu-b-40"]
OLD_EXPOSURES = ["ebi-a-GCST90103634", "ebi-a-GCST90025945"]

print("=" * 96)
print("A newly fetched scan")
print("=" * 96)
new_files = []
for gid in NEW_EXPOSURES:
    new_files += sorted(RAW.glob(f"mr_{gid}_*.tsv"))
if new_files:
    p = new_files[0]
    print(f"  file: {p.name}  ({p.stat().st_size/1e6:.2f} MB)")
    head = p.read_text(encoding="utf-8", errors="replace").splitlines()[:3]
    for ln in head:
        print(f"      {ln[:150]}")
    print(f"  columns: {len(head[0].split(chr(9)))}")
else:
    print("  no new files yet")

print()
print("=" * 96)
print("An existing cached scan")
print("=" * 96)
old_files = []
for gid in OLD_EXPOSURES:
    old_files += sorted(RAW.glob(f"mr_{gid}_*.tsv"))
if old_files:
    p2 = old_files[0]
    print(f"  file: {p2.name}  ({p2.stat().st_size/1e6:.2f} MB)")
    head2 = p2.read_text(encoding="utf-8", errors="replace").splitlines()[:3]
    for ln in head2:
        print(f"      {ln[:150]}")
    print(f"  columns: {len(head2[0].split(chr(9)))}")

print()
print("=" * 96)
print("Structural comparison")
print("=" * 96)
if new_files and old_files:
    h_new = new_files[0].read_text(encoding="utf-8",
                                   errors="replace").splitlines()[0].split("\t")
    h_old = old_files[0].read_text(encoding="utf-8",
                                   errors="replace").splitlines()[0].split("\t")
    print(f"  header identical      : {h_new == h_old}")
    if h_new != h_old:
        print(f"      new: {h_new}")
        print(f"      old: {h_old}")
    d_new = pd.read_csv(new_files[0], sep="\t")
    d_old = pd.read_csv(old_files[0], sep="\t")
    print(f"  new rows              : {len(d_new):,}")
    print(f"  old rows              : {len(d_old):,}")
    print(f"  same dtypes           : {list(d_new.dtypes) == list(d_old.dtypes)}")
    if list(d_new.dtypes) != list(d_old.dtypes):
        print(f"      new: {list(d_new.dtypes)}")
        print(f"      old: {list(d_old.dtypes)}")
    for c in ("chrom", "pos", "rsids", "beta", "sebeta", "pval"):
        if c in d_new.columns and c in d_old.columns:
            print(f"  column {c:8s} new sample {str(d_new[c].iloc[0])[:26]:28s} "
                  f"old sample {str(d_old[c].iloc[0])[:26]}")

print()
print("=" * 96)
print("Row counts per phenotype for one exposure (they should match exactly)")
print("=" * 96)
import collections
PHENOS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
          "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]
for gid in NEW_EXPOSURES:
    files = sorted(RAW.glob(f"mr_{gid}_*.tsv"))
    if not files:
        continue
    per = collections.Counter()
    for f in files:
        for ph in PHENOS:
            if f"_{ph}_" in f.name:
                per[ph] += 1
                break
    print(f"  {gid:20s} " + " ".join(f"{ph[3:9]}={per.get(ph,0):>3}" for ph in PHENOS))
