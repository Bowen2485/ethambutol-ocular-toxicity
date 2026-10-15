# -*- coding: utf-8 -*-
"""Establish the exact number of MR estimates across the published and supplementary files."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

pub = pd.read_csv(RES / "mr_opengwas_results.csv", encoding="utf-8-sig")
sup = pd.read_csv(RES / "mr_supplementary_results.csv", encoding="utf-8-sig")

print("=== published results file ===")
print(f"  estimates: {len(pub)}")
for e, g in pub.groupby("exposure"):
    outs = sorted(g.outcome.unique())
    short = [o.replace("H7_", "") for o in outs]
    print(f"  {e:24s} {len(outs)} outcome(s): {short}")

print()
print("=== supplementary results file ===")
print(f"  estimates: {len(sup)}")
for e, g in sup.groupby("exposure"):
    outs = sorted(g.outcome.unique())
    short = [o.replace("H7_", "") for o in outs]
    print(f"  {e:24s} {len(outs)} outcome(s): {short}")

print()
print("=== combined, distinct exposure-outcome pairs ===")
comb = pd.concat([pub[["exposure", "outcome"]], sup[["exposure", "outcome"]]])
comb = comb.drop_duplicates()
print(f"  total distinct pairs: {len(comb)}")
for e, g in comb.groupby("exposure"):
    print(f"  {e:24s} {len(g)}")

print()
print("=== what the manuscript can honestly claim ===")
n_pub = len(pub)
n_new = len(sup[sup.exposure == "Serum creatinine"])
print(f"  published estimates (eGFR 6, cystatin C 6, type 2 diabetes 1): {n_pub}")
print(f"  new serum creatinine estimates: {n_new}")
print(f"  combined distinct pairs: {len(comb)}")
print()
print("  NOT every exposure has all six outcomes: type 2 diabetes appears for optic")
print("  neuritis only.  So a flat 'exposures x six outcomes' total would overstate it.")
