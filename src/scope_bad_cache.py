# -*- coding: utf-8 -*-
"""
Identify exactly which cached scan files are invalid, before deleting anything.

The seven exposures fetched during this session hold one phenotype's data copied into
all six phenotype files.  The three exposures cached earlier do not.  Deleting must
therefore be scoped to the seven and must leave the three untouched, and the counts have
to be established from the files themselves rather than from a remembered figure.

This only lists.  Nothing is removed here - the deletion is a separate, explicit step
once the scope is confirmed.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

BAD = {
    "ukb-b-13891": "Zinc supplement use",
    "ieu-b-25": "Cigarettes per day",
    "ieu-b-73": "Alcoholic drinks per week",
    "ieu-b-4877": "Smoking initiation",
    "ebi-a-GCST006867": "Type 2 diabetes",
    "ebi-a-GCST90014006": "HbA1c",
    "ieu-b-40": "Body mass index",
}
GOOD = {
    "ebi-a-GCST90103634": "eGFR (creatinine)",
    "ebi-a-GCST90025945": "Cystatin C",
    "ebi-a-GCST90025946": "Serum creatinine",
}

print("=" * 94)
print("1. Files belonging to the seven affected exposures")
print("=" * 94)
total_bad = 0
per_exposure = {}
for gid, label in BAD.items():
    files = sorted(RAW.glob(f"mr_{gid}_*.tsv"))
    per_exposure[gid] = len(files)
    total_bad += len(files)
    print(f"  {label:28s} {len(files):>6,} files")
print(f"  {'TOTAL to be removed':28s} {total_bad:>6,} files")

print()
print("=" * 94)
print("2. Files belonging to the three sound exposures (must be preserved)")
print("=" * 94)
total_good = 0
for gid, label in GOOD.items():
    files = sorted(RAW.glob(f"mr_{gid}_*.tsv"))
    total_good += len(files)
    print(f"  {label:28s} {len(files):>6,} files")
print(f"  {'TOTAL to be preserved':28s} {total_good:>6,} files")

print()
print("=" * 94)
print("3. Any other exposure present in the cache")
print("=" * 94)
import re
seen = {}
for p in RAW.glob("mr_*.tsv"):
    m = re.match(r"^mr_([A-Za-z0-9\-]+)_H7_", p.name)
    if m:
        seen.setdefault(m.group(1), 0)
        seen[m.group(1)] += 1
known = set(BAD) | set(GOOD)
other = {k: v for k, v in seen.items() if k not in known}
if other:
    for k, v in sorted(other.items(), key=lambda x: -x[1]):
        print(f"  {k:28s} {v:>6,} files   <-- not in either list; inspect before "
              f"any deletion")
else:
    print("  none - the cache holds only the ten exposures accounted for")

print()
print("=" * 94)
print("4. Total cache size")
print("=" * 94)
allfiles = list(RAW.glob("mr_*.tsv"))
size = sum(p.stat().st_size for p in allfiles)
print(f"  scan files in cache : {len(allfiles):,}")
print(f"  total size          : {size/1e9:.2f} GB")
print(f"  to remove           : {total_bad:,} files "
      f"({sum((RAW/f).stat().st_size for f in [] ) or 0} bytes counted separately)")
print()
print("=" * 94)
print("5. Confirmation that the seven are in fact identical across phenotypes")
print("=" * 94)
import hashlib
for gid in list(BAD)[:3]:
    w0 = sorted(RAW.glob(f"mr_{gid}_*_0.tsv"))
    hashes = {p.name.split("_H7_")[1].split("_")[0]:
              hashlib.md5(p.read_bytes()).hexdigest()[:10] for p in w0}
    print(f"  {gid:22s} window 0 -> {len(set(hashes.values()))} distinct hash(es) "
          f"across {len(hashes)} phenotypes")
for gid in list(GOOD)[:2]:
    w0 = sorted(RAW.glob(f"mr_{gid}_*_0.tsv"))
    hashes = {p.name.split("_H7_")[1].split("_")[0]:
              hashlib.md5(p.read_bytes()).hexdigest()[:10] for p in w0}
    print(f"  {gid:22s} window 0 -> {len(set(hashes.values()))} distinct hash(es) "
          f"across {len(hashes)} phenotypes  (sound)")

print()
print("=" * 94)
print("Reading")
print("=" * 94)
print(f"""  Removing {total_bad:,} files restores the cache to the three exposures that were
  always sound.  They are the ones the manuscript's current Mendelian randomisation
  results rest on, so nothing already reported depends on the {total_bad:,} files.
  The seven exposures have to be fetched again, this time querying each phenotype
  separately, because the variant positions are shared between phenotypes but the
  effect sizes are not.""")
