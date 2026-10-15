# -*- coding: utf-8 -*-
"""
Check why two different outcomes return identical estimates.

Type 2 diabetes gave beta +0.0948 with 54 SNPs against both optic neuritis and optic
atrophy.  Two genuinely different phenotypes cannot have identical summary statistics
across 54 instruments, so either the outcome frames are the same file or the estimates
are being read from one place for both.

The first thing to check is whether the six phenotypes hold different data in this
exposure's cache, because if the scan for optic atrophy happened to be written from the
optic neuritis file, every comparison within that exposure is affected.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"
GID = "ebi-a-GCST006867"                       # type 2 diabetes
PHENOS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
          "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]

print("=" * 96)
print("1. Do the six phenotype caches hold different numbers?")
print("=" * 96)
summary = []
for ph in PHENOS:
    files = sorted(RAW.glob(f"mr_{GID}_{ph}_*.tsv"))
    if not files:
        print(f"  {ph:26s} no files")
        continue
    d = pd.concat([pd.read_csv(f, sep="\t") for f in files], ignore_index=True)
    summary.append({
        "phenotype": ph,
        "files": len(files),
        "rows": len(d),
        "beta_mean": d.beta.mean(),
        "beta_sd": d.beta.std(),
        "sebeta_mean": d.sebeta.mean(),
        "pval_min": d.pval.min(),
        "first_pos": d.pos.iloc[0],
        "first_rsid": d.rsids.iloc[0],
    })
s = pd.DataFrame(summary)
print(s.to_string(index=False))

print()
print("  identical columns across phenotypes would indicate the same data written "
      "twice:")
for col in ("rows", "beta_mean", "beta_sd", "sebeta_mean", "pval_min", "first_pos"):
    vals = s[col].tolist()
    print(f"      {col:12s} distinct values: {len(set(vals))} of {len(vals)}")

print()
print("=" * 96)
print("2. Are the files byte-identical between phenotypes?")
print("=" * 96)
import hashlib
for ph in PHENOS[:3]:
    files = sorted(RAW.glob(f"mr_{GID}_{ph}_*.tsv"))[:2]
    for f in files:
        h = hashlib.md5(f.read_bytes()).hexdigest()[:12]
        print(f"  {ph:26s} {f.name:52s} {h}")

print()
print("=" * 96)
print("3. Compare one window across two phenotypes directly")
print("=" * 96)
a = sorted(RAW.glob(f"mr_{GID}_H7_OPTNEURITIS_*_0.tsv"))
b = sorted(RAW.glob(f"mr_{GID}_H7_OPTATROPHY_*_0.tsv"))
if a and b:
    da, db = pd.read_csv(a[0], sep="\t"), pd.read_csv(b[0], sep="\t")
    print(f"  {a[0].name}: {len(da)} rows")
    print(f"  {b[0].name}: {len(db)} rows")
    same_pos = da.pos.equals(db.pos) if len(da) == len(db) else False
    print(f"  positions identical : {same_pos}")
    if len(da) == len(db):
        print(f"  betas identical     : {da.beta.equals(db.beta)}")
        print(f"  sebeta identical    : {da.sebeta.equals(db.sebeta)}")
        print(f"  pval identical      : {da.pval.equals(db.pval)}")
        diff = (da.beta != db.beta).sum()
        print(f"  betas differing in {diff} of {len(da)} rows")
else:
    print("  window 0 not found for one of the phenotypes")

print()
print("=" * 96)
print("4. Interpretation")
print("=" * 96)
print("""  If the phenotypes hold different values, the identical estimates come from
  somewhere else in the pipeline and the cache is sound.  If they hold the same values,
  the scan-writing step assigned one phenotype's data to another, and every
  within-exposure comparison in that cache is unusable until rewritten.""")
