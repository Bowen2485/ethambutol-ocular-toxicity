# -*- coding: utf-8 -*-
"""
Establish what the existing within-class analysis already contains.

The question is whether to bring in more antitubercular drugs.  Before answering it, the
existing analysis has to be read: which drugs are in it, how they were selected, what
the numbers are, and - most importantly - what the pattern across the class looks like.
If the class already shows a structure rather than a single elevated drug, then the
findings worth reporting may already be present and the work needed is analysis rather
than data collection.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

print("=" * 100)
print("1. The within-class comparison as it stands")
print("=" * 100)
p = RES / "faers_headtohead_optic.csv"
if p.exists():
    d = pd.read_csv(p, encoding="utf-8-sig")
    print(f"  columns: {list(d.columns)}")
    print(f"  drugs: {len(d)}")
    print()
    cols = [c for c in ("drug", "n_cases", "n_panel", "pct_panel",
                        "n_optic_neuropathy", "pct_optic_neuropathy",
                        "n_toxic_optic_neuropathy") if c in d.columns]
    with pd.option_context("display.width", 160):
        print(d[cols].to_string(index=False))
else:
    print("  file not found")

print()
print("=" * 100)
print("2. The signal table by drug and term")
print("=" * 100)
p2 = RES / "faers_withinclass_signals.csv"
if p2.exists():
    s = pd.read_csv(p2, encoding="utf-8-sig")
    print(f"  columns: {list(s.columns)}")
    print(f"  rows: {len(s)}")
    if "drug" in s.columns:
        print(f"  drugs: {sorted(s['drug'].unique())}")
    if "term" in s.columns:
        terms = sorted(s["term"].unique())
        print(f"  terms ({len(terms)}): {terms[:20]}")
else:
    print("  file not found")

print()
print("=" * 100)
print("3. Which drugs appear in the whole-database ranking")
print("=" * 100)
p3 = RES / "faers_drug_ranking_non.csv"
if p3.exists():
    r = pd.read_csv(p3, encoding="utf-8-sig")
    print(f"  columns: {list(r.columns)}")
    print(f"  rows: {len(r):,}")
    tcol = next((c for c in ("term", "pt", "event") if c in r.columns), None)
    if tcol:
        optic = r[r[tcol].astype(str).str.upper().str.contains("OPTIC NEUROPATHY",
                                                              na=False)]
        print(f"  rows for OPTIC NEUROPATHY: {len(optic)}")
        if len(optic):
            show = [c for c in r.columns if c in
                    ("drug", "drugname", "medicinalproduct", "n_cases", "a", "ror",
                     "ror_lcl", "ror_ucl")]
            with pd.option_context("display.width", 160):
                print(optic[show].head(30).to_string(index=False))
else:
    print("  file not found")

print()
print("=" * 100)
print("4. What the antitubercular drug list contains")
print("=" * 100)
for src in ("faers_headtohead.py", "faers_withinclass.py"):
    q = ROOT / "src" / src
    if not q.exists():
        continue
    txt = q.read_text(encoding="utf-8", errors="replace")
    print(f"\n  --- {src} ---")
    inside = False
    for ln in txt.splitlines():
        s_ = ln.strip()
        if any(k in s_ for k in ("DRUGS", "SUBSTANCES", "ANTI_TB", "TOKENS")) and "=" in s_:
            inside = True
        if inside:
            print(f"      {s_[:118]}")
            if s_.endswith("}") or s_.endswith("]"):
                inside = False
