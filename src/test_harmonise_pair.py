# -*- coding: utf-8 -*-
"""
Test the harmonisation on one exposure-outcome pair before running the whole panel.

The cached coverage file reports zero harmonised variants for most pairs, including
every HbA1c pair, while one T2D pair reached 57 of 118.  A coverage table that old was
written before the scans existed, so it is not evidence about the current cache - but a
genuine zero would make the analysis silently return no estimates, which is the failure
this project already met once with serum creatinine.

The test therefore runs the project's own harmonise() on real files and prints what came
out of each matching route separately, so a failure can be attributed to the key it used
rather than to the whole step.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"

print("=" * 96)
print("1. What an instrument file and a scan file actually contain")
print("=" * 96)
inst_path = RAW / "tophits_ebi-a-GCST90014006_5e-08.tsv"      # HbA1c
print(f"  instrument file: {inst_path.name}")
if inst_path.exists():
    inst = pd.read_csv(inst_path, sep="\t")
    print(f"      {len(inst)} rows, columns {list(inst.columns)[:12]}")
    print(f"      first rsID values: {inst.iloc[:4, inst.columns.get_loc('rsid')].tolist() if 'rsid' in inst.columns else 'no rsid column'}")

hba1c_scans = sorted(RAW.glob("mr_ebi-a-GCST90014006_H7_OPTNEURITIS_*.tsv"))
print()
print(f"  scan files for HbA1c / H7_OPTNEURITIS: {len(hba1c_scans)}")
if hba1c_scans:
    s = pd.read_csv(hba1c_scans[0], sep="\t")
    print(f"      {hba1c_scans[0].name}")
    print(f"      {len(s)} rows, columns {list(s.columns)}")
    print(f"      first rows:")
    for _, r in s.head(3).iterrows():
        print(f"          chr{r['chrom']}:{r['pos']}  {r['ref']}>{r['alt']}  "
              f"rsids={r['rsids']!r}  beta={r['beta']}  sebeta={r['sebeta']}")

    # how many scan rows carry any rsID at all
    n_with = int((s["rsids"].astype(str).str.strip().replace("", pd.NA)
                  .notna()).sum()) if "rsids" in s.columns else 0
    print(f"      rows carrying an rsID: {n_with} of {len(s)}")

print()
print("=" * 96)
print("2. Do the two sides share rsIDs at all?")
print("=" * 96)
if inst_path.exists() and hba1c_scans:
    inst_rs = set(inst["rsid"].astype(str).str.strip()) if "rsid" in inst.columns else set()
    out_rs = set()
    for f in hba1c_scans:
        d = pd.read_csv(f, sep="\t")
        if "rsids" in d.columns:
            for v in d["rsids"].dropna().astype(str):
                for part in v.split(";"):
                    if part.strip():
                        out_rs.add(part.strip())
    print(f"  instrument rsIDs : {len(inst_rs)}")
    print(f"  outcome rsIDs    : {len(out_rs)}")
    print(f"  intersection     : {len(inst_rs & out_rs)}")
    if inst_rs & out_rs:
        print(f"      examples: {sorted(inst_rs & out_rs)[:6]}")

print()
print("=" * 96)
print("3. Run the project's harmonise() on this pair")
print("=" * 96)
from mr_analysis import harmonise       # noqa: E402

exp = inst.rename(columns={"position": "pos", "se": "sebeta"}).copy() \
    if inst_path.exists() else pd.DataFrame()
exp["chrom"] = exp["chr"].astype(str).str.replace("chr", "", regex=False)
exp["pos"] = pd.to_numeric(exp["pos"], errors="coerce")
exp["rsids"] = exp["rsid"].astype(str) if "rsid" in exp.columns else ""
exp = exp.dropna(subset=["pos"])

# concatenate every window for the outcome, then harmonise as the pipeline does
pieces = [pd.read_csv(f, sep="\t") for f in hba1c_scans]
out = pd.concat(pieces, ignore_index=True)
h = harmonise(exp, out)
print(f"  instruments          : {len(exp)}")
print(f"  outcome rows total   : {len(out)}")
print(f"  harmonised variants  : {len(h)}")
if len(h):
    print(f"      columns: {list(h.columns)[:14]}")
    print(h.head(4).to_string(index=False))
else:
    print("      zero - the pair would produce no estimate")

print()
print("=" * 96)
print("4. Which key would work, tested directly")
print("=" * 96)
if len(out) and len(exp):
    exp_rs = set(exp["rsids"].astype(str).str.strip()) - {"", "nan"}
    out_rs_flat = set()
    for v in out["rsids"].dropna().astype(str):
        for part in v.split(";"):
            if part.strip():
                out_rs_flat.add(part.strip())
    print(f"  rsID route            : {len(exp_rs & out_rs_flat)} of {len(exp_rs)} "
          f"instruments match an outcome rsID")
    exp_pos = set(exp["chrom"].astype(str) + ":" + exp["pos"].astype(int).astype(str))
    out_pos = set(out["chrom"].astype(str) + ":" + out["pos"].astype(int).astype(str))
    print(f"  position route        : {len(exp_pos & out_pos)} of {len(exp_pos)} "
          f"instruments match an outcome position")
    print()
    print("  A large rsID overlap with a small position overlap is the expected")
    print("  signature of a build difference, and confirms rsID matching is the right")
    print("  key.  Both small would mean the scan windows do not cover the instruments.")
