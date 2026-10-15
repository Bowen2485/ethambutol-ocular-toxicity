# -*- coding: utf-8 -*-
"""
Re-check whether mr_final.py really has the column-contract fault.

The previous conclusion - that mr_final.py omits the ea/nea/p mappings and so makes
harmonise() return nothing for every pair - was reached from a test script that built
the exposure frame itself, without those lines.  Reading mr_final.py shows the mappings
are present, so the fault was in the test, not the pipeline.

That matters because the remedy differs: if the pipeline is sound, the Mendelian
randomisation results already produced from the three cached exposures are valid and
nothing needs re-running for that reason; if it is not, they do not.  This checks the
pipeline's own output and re-runs its normalisation path on a real instrument file to
settle it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"

print("=" * 96)
print("1. What the pipeline already produced")
print("=" * 96)
for name in ("mr_opengwas_results.csv", "mr_supplementary_results.csv",
             "mr_scan_coverage.csv"):
    p = ROOT / "results" / name
    if not p.exists():
        print(f"  {name:34s} absent")
        continue
    d = pd.read_csv(p)
    print(f"  {name:34s} {len(d)} rows, columns {list(d.columns)[:9]}")
    if "n_snp" in d.columns:
        print(f"      n_snp: min {d.n_snp.min()}, max {d.n_snp.max()}, "
              f"zero-snp rows {int((d.n_snp == 0).sum())} of {len(d)}")

print()
print("=" * 96)
print("2. The pipeline's own normalisation lines")
print("=" * 96)
txt = (ROOT / "src" / "mr_final.py").read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(txt, 1):
    s = ln.strip()
    if any(k in s for k in ('exp["alt"]', 'exp["ref"]', 'exp["pval"]',
                            'exp["rsids"]', 'exp["af_alt"]', 'exp["chrom"]',
                            'exp["pos"]')):
        print(f"  line {i:4d}: {s[:100]}")

print()
print("=" * 96)
print("3. Apply exactly those lines to a real instrument file and harmonise")
print("=" * 96)
import numpy as np
from mr_analysis import harmonise           # noqa: E402

inst = pd.read_csv(RAW / "tophits_ebi-a-GCST90103634_5e-08.tsv", sep="\t")
exp = inst.copy()
exp["chrom"] = exp["chr"].astype(str).str.replace("chr", "", regex=False)
exp["pos"] = pd.to_numeric(exp["pos"], errors="coerce")
exp["alt"] = exp["ea"].astype(str).str.upper()
exp["ref"] = exp["nea"].astype(str).str.upper()
exp["rsids"] = exp["rsid"].astype(str)
exp["beta"] = pd.to_numeric(exp["beta"], errors="coerce")
exp["sebeta"] = pd.to_numeric(exp["sebeta"], errors="coerce")
exp["af_alt"] = pd.to_numeric(exp.get("eaf"), errors="coerce")
exp["pval"] = pd.to_numeric(exp["p"], errors="coerce")
exp = exp.dropna(subset=["pos", "beta", "sebeta"])
print(f"  exposure columns after the pipeline's normalisation:")
print(f"      {[c for c in exp.columns][:18]}")
print(f"      alt present: {'alt' in exp.columns}   "
      f"ref present: {'ref' in exp.columns}   "
      f"pval present: {'pval' in exp.columns}")

scans = sorted(RAW.glob("mr_ebi-a-GCST90103634_H7_OPTNEURITIS_*.tsv"))
if scans:
    out = pd.concat([pd.read_csv(f, sep="\t") for f in scans], ignore_index=True)
    h = harmonise(exp, out)
    print(f"  instruments {len(exp)}   outcome rows {len(out)}   "
          f"harmonised {len(h)}")
    if len(h):
        from mr_analysis import ivw
        b, se, q = ivw(h.beta_exp.values, h.se_exp.values,
                       h.beta_out.values, h.se_out.values)
        print(f"      IVW beta {b:+.4f}  se {se:.4f}  Q {q:.1f}")
        print()
        print("  => the pipeline's normalisation does satisfy harmonise(), so the")
        print("     earlier 'column contract' fault was in the test script, not here.")
    else:
        print("  => still zero; the fault is real and needs locating properly")
else:
    print("  no cached scan for this exposure/outcome")

print()
print("=" * 96)
print("4. Does the pipeline's stored result match a fresh run?")
print("=" * 96)
p = ROOT / "results" / "mr_opengwas_results.csv"
if p.exists():
    d = pd.read_csv(p)
    keep = [c for c in ("exposure", "outcome", "n_snp", "method", "beta", "se", "p")
            if c in d.columns]
    print(d[keep].head(14).to_string(index=False))
