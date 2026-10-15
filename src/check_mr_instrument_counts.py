# -*- coding: utf-8 -*-
"""
Check the MR instrument counts actually reported against the harmonisation coverage.

Why this matters
    The manuscript states that the renal exposures used 146-150 instruments, and that
    harmonisation recovered 13.5% of instrument-outcome pairs.  results/mr_scan_coverage.csv
    shows recovery rates far below that for the exposures that did run later (type 2
    diabetes recovered 57 of 118 for one outcome and 0 for the other five; HbA1c
    recovered 0 of 403).  A recovery of 0 across the board is not a property of the data,
    it is a failure of retrieval, so the reported instrument counts have to be checked
    against what the pipeline actually harmonised.

    The result rows carry the SNP list used for each estimate, so the true count is
    recoverable directly from results/mr_opengwas_results.csv - n_snp is the instrument
    count for that estimate.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

print("=" * 84)
print("1. Instrument counts as reported in the results file")
print("=" * 84)
r = pd.read_csv(RES / "mr_opengwas_results.csv", encoding="utf-8-sig")
if "n_snp" not in r.columns:
    raise SystemExit(f"no n_snp column; have {list(r.columns)}")
print(f"  columns: n_snp present, {len(r)} estimates")
agg = (r.groupby("exposure")["n_snp"]
        .agg(["count", "min", "median", "max"]).round(0).astype(int))
print()
print(agg.to_string())

print()
print("=" * 84)
print("2. Harmonisation coverage recorded during the runs")
print("=" * 84)
cov_p = RES / "mr_scan_coverage.csv"
if cov_p.exists():
    c = pd.read_csv(cov_p, encoding="utf-8-sig")
    print(f"  rows: {len(c)}   columns: {list(c.columns)}")
    c["rate"] = (c["harmonised"] / c["instruments"].replace(0, pd.NA)).astype(float)
    print()
    print(c[["exposure", "outcome", "instruments", "harmonised", "not_found"]]
          .to_string(index=False))
    print()
    tot_i = int(c["instruments"].sum())
    tot_h = int(c["harmonised"].sum())
    print(f"  TOTAL instruments nominated : {tot_i:,}")
    print(f"  TOTAL harmonised            : {tot_h:,}")
    print(f"  overall recovery            : {tot_h/tot_i*100:.2f}%")
else:
    print("  coverage file not found")

print()
print("=" * 84)
print("3. Consistency check")
print("=" * 84)
if cov_p.exists():
    for exp in agg.index:
        sub = c[c.exposure == exp]
        if not len(sub):
            continue
        rep = agg.loc[exp, "max"]
        rec = int(sub["harmonised"].max())
        flag = "CONSISTENT" if abs(rep - rec) <= 2 else "MISMATCH"
        print(f"  {exp:26s} reported n_snp max {rep:>4}   coverage max {rec:>4}   {flag}")
    print()
    print("  The eGFR and Cystatin C rows are the ones the manuscript leans on.  If their")
    print("  recovery rates are in the tens of percent while type 2 diabetes and HbA1c sit")
    print("  at zero, the difference is retrieval, not biology: the same pipeline called")
    print("  the same FinnGen endpoints, so an exposure-independent failure cannot depend")
    print("  on which exposure supplied the instruments.")
