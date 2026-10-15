# -*- coding: utf-8 -*-
"""
Work out why the table files disagree with the counts the manuscript quotes.

Table 2 is declared as 177 terms but the file in tables/ has 88 rows; Table 2b is
declared as 58 strict signals but its file has 30.  The authoritative signal table in
results/ has 177 rows with 58 rows flagged strict, so the numbers in the text trace to a
real computation - it is the exported table files that do not match it.

Before rebuilding anything, this compares the files term by term, so the difference is
identified rather than guessed: a subset with a stated rule is fine, a truncated export
is not.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "tables"
R = ROOT / "results"
D = ROOT / "data" / "derived"

src = pd.read_csv(R / "faers_signals_annotated.csv", encoding="utf-8-sig")
print("=" * 96)
print("1. The authoritative signal table")
print("=" * 96)
print(f"  results/faers_signals_annotated.csv: {len(src)} rows")
print(f"  strict signals (signal_strict)     : {int(src.signal_strict.sum())}")
print(f"  categories:")
for k, v in src.category.value_counts().items():
    print(f"      {str(k):34s} {v}")

print()
print("=" * 96)
print("2. Table2_signals.csv - what is in it")
print("=" * 96)
t2 = pd.read_csv(T / "Table2_signals.csv", encoding="utf-8-sig")
print(f"  rows: {len(t2)}   columns: {list(t2.columns)}")
print(f"  distinct drugs: {t2['drug'].nunique() if 'drug' in t2 else 'n/a'}")
if "drug" in t2.columns:
    print(f"  drug counts: {t2['drug'].value_counts().to_dict()}")
if "group" in t2.columns:
    print(f"  groups: {t2['group'].value_counts().to_dict()}")
# is it the subset where the drug is ethambutol only?
if "drug" in t2.columns:
    eth = t2[t2["drug"] == "ethambutol"]
    print(f"  rows for ethambutol: {len(eth)}")
if "term" in src.columns and "term" in t2.columns:
    a, b = set(src.term), set(t2.term)
    print(f"  term overlap with the source: {len(a & b)} of {len(a)}")

print()
print("=" * 96)
print("3. Table2b_signals_strict.csv - what is in it")
print("=" * 96)
t2b = pd.read_csv(T / "Table2b_signals_strict.csv", encoding="utf-8-sig")
print(f"  rows: {len(t2b)}   columns: {list(t2b.columns)}")
strict_src = src[src.signal_strict]
print(f"  strict rows in the source: {len(strict_src)}")
if "term" in t2b.columns:
    a, b = set(strict_src.term), set(t2b.term)
    print(f"  terms shared with the source's strict set: {len(a & b)}")
    print(f"  in the file but not strict in the source: {len(b - a)}")
    print(f"  strict in the source but absent from the file: {len(a - b)}")
    missing = sorted(a - b)
    if missing:
        print("  the missing ones:")
        for m in missing[:12]:
            row = src[src.term == m].iloc[0]
            print(f"      {m[:52]:54s} q={row.q_bh:.3g}  ror={row.ror:.2f}")

print()
print("=" * 96)
print("4. Table2_signals_full_panel.csv against the derived panel")
print("=" * 96)
fp = pd.read_csv(T / "Table2_signals_full_panel.csv", encoding="utf-8-sig")
print(f"  full_panel rows: {len(fp)}")
for name in ("ocular_terms.csv", "faers_2x2.csv", "faers_term_counts.csv"):
    p = D / name
    if p.exists():
        d = pd.read_csv(p, encoding="utf-8-sig")
        print(f"  data/derived/{name}: {len(d)} rows")
        if "term" in d.columns and "term" in fp.columns:
            a, b = set(d.term), set(fp.term)
            print(f"      terms shared with full_panel: {len(a & b)}; "
                  f"only in derived: {len(a - b)}; only in table: {len(b - a)}")
            if a - b:
                print(f"      missing from the table: {sorted(a - b)[:6]}")

print()
print("=" * 96)
print("5. Reading")
print("=" * 96)
print("""  The remedy is to rebuild the exported tables from the authoritative signal table
  under a stated rule, rather than to change the numbers in the text: the text's counts
  are what the analysis produced, and the exports are what drifted.""")
