# -*- coding: utf-8 -*-
"""Verify the odds ratios quoted for serum creatinine in the manuscript."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "results" / "mr_supplementary_results.csv", encoding="utf-8-sig")
s = d[d.exposure == "Serum creatinine"].copy()

print("=== Serum creatinine: OR and 95% CI ===")
for _, r in s.iterrows():
    or_ = np.exp(r.beta)
    lo = np.exp(r.beta - 1.96 * r.se)
    hi = np.exp(r.beta + 1.96 * r.se)
    print(f"  {r.outcome:28s} n={int(r.n_snp):>4}  "
          f"OR {or_:.3f} (95% CI {lo:.3f}-{hi:.3f})  p={r.p:.3f}  q={r.p_fdr:.3f}")

r = s[s.outcome == "H7_OPTNEURITIS"].iloc[0]
print()
print("  manuscript states : optic neuritis OR 0.944, 95% CI 0.724-1.231, p = 0.67")
print(f"  computed          : OR {np.exp(r.beta):.3f}, "
      f"95% CI {np.exp(r.beta - 1.96 * r.se):.3f}-"
      f"{np.exp(r.beta + 1.96 * r.se):.3f}, p = {r.p:.2f}")
imin = s.p.idxmin()
print(f"  smallest p        : {s.p.min():.4f} ({s.loc[imin, 'outcome']}), "
      f"q = {s.loc[imin, 'p_fdr']:.4f}")

print()
print("=== All three renal exposures, optic neuritis ===")
for exp in ("eGFR (creatinine)", "Cystatin C", "Serum creatinine"):
    r = d[(d.exposure == exp) & (d.outcome == "H7_OPTNEURITIS")].iloc[0]
    print(f"  {exp:22s} n={int(r.n_snp):>4}  OR {np.exp(r.beta):.3f} "
          f"({np.exp(r.beta - 1.96 * r.se):.3f}-{np.exp(r.beta + 1.96 * r.se):.3f})"
          f"  p={r.p:.3f}")
print()
print(f"  estimates across all three exposures and six outcomes: {len(d)}")
print(f"  significant after FDR: {(d.p_fdr < 0.05).sum()}")
print(f"  minimum q overall: {d.p_fdr.min():.4f}")
