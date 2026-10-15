# -*- coding: utf-8 -*-
"""
Check which stored MR results were computed from cache files that are now deleted.

The column-contract fault I reported in mr_final.py does not exist - the mappings are
there and harmonise() returns 151 variants on a sound exposure.  But the check that
established this also revealed a stored result for Type 2 diabetes, whose cache was
written during this session with copied phenotype data and has now been removed.

A result computed from that cache is not interpretable: its outcome data was one
phenotype's betas under another phenotype's name.  The question is which stored results
are affected, and whether the manuscript quotes any of them.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")

AFFECTED = {
    "ukb-b-13891": "Zinc supplement use",
    "ieu-b-25": "Cigarettes per day",
    "ieu-b-73": "Alcoholic drinks per week",
    "ieu-b-4877": "Smoking initiation",
    "ebi-a-GCST006867": "Type 2 diabetes",
    "ebi-a-GCST90014006": "HbA1c",
    "ieu-b-40": "Body mass index",
}

print("=" * 96)
print("1. Stored MR result files and which exposures they contain")
print("=" * 96)
for name in ("mr_opengwas_results.csv", "mr_supplementary_results.csv"):
    p = R / name
    if not p.exists():
        continue
    d = pd.read_csv(p)
    print(f"\n  {name}: {len(d)} rows")
    print(f"      columns: {list(d.columns)}")
    # the exposure may be a label or an id, so match on both
    text = d.astype(str).agg(" ".join, axis=1)
    hit = text.str.contains("|".join(AFFECTED.values()), case=False, regex=True)
    for gid in AFFECTED:
        g = d.astype(str).agg(" ".join, axis=1).str.contains(gid)
        hit = hit | g
    print(f"      rows naming an affected exposure: {int(hit.sum())} of {len(d)}")
    if hit.any():
        cols = [c for c in ("exposure", "gwas_id", "outcome", "n_snp", "method",
                            "beta", "se", "p", "p_fdr") if c in d.columns]
        print(d[hit][cols].to_string(index=False))

print()
print("=" * 96)
print("2. What the manuscript says about the genetic analysis")
print("=" * 96)
import re
for label, text in (("EN", EN), ("CN", CN)):
    print(f"  {label}:")
    for kw in ("19 exposure-outcome", "exposure-outcome estimates",
               "186 instruments", "three modifiable", "19 个", "186 个"):
        n = text.count(kw)
        if n:
            print(f"      {kw!r} appears {n} time(s)")
    for m in re.finditer(r"[^\n]{0,110}(19 exposure-outcome|186 instrument)"
                         r"[^\n]{0,110}", text):
        print(f"      ...{m.group(0).strip()[:190]}")

print()
print("=" * 96)
print("3. Which exposures the manuscript's MR section names")
print("=" * 96)
for label, text in (("EN", EN), ("CN", CN)):
    named = [lab for lab in AFFECTED.values() if lab.lower() in text.lower()]
    named += [lab for lab in ("eGFR", "Cystatin C", "Serum creatinine")
              if lab.lower() in text.lower()]
    print(f"  {label}: {named}")

print()
print("=" * 96)
print("4. Reading")
print("=" * 96)
print("""  The stored result files are the record of what the pipeline computed.  Any row
  naming one of the seven affected exposures was computed on outcome data that has since
  been deleted as invalid, so it cannot be quoted.  The manuscript's genetic section
  should be checked for those exposures specifically; results from eGFR, cystatin C and
  serum creatinine rest on caches that were always sound.""")
