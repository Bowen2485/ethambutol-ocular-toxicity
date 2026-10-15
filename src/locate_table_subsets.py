# -*- coding: utf-8 -*-
"""
Locate or reconstruct the three derived table variants (2b, 2c, 2d).

The manuscript declares an ocular signal table of 177 terms, a strict-signal subset of
58, a drug-toxicity-spectrum subset of the top 30, and 83 terms awaiting manual review.
Only the 177-term file is named as such on disk, so either the subsets are produced at
build time from the big table or they do not exist.  If they can be reproduced by a
stated rule, they are not missing - but the rule has to be the one the manuscript
describes, and the counts have to come out at 58 and 83.

This derives each subset from the full table and reports the count actually obtained,
so a mismatch between the text and the data becomes visible.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
DER = ROOT / "data" / "derived"

print("=" * 100)
print("1. The full signal table and its columns")
print("=" * 100)
p = RES / "faers_signals_annotated.csv"
d = pd.read_csv(p, encoding="utf-8-sig")
print(f"  {p.name}: {len(d)} rows")
print(f"  columns: {list(d.columns)}")
print()
with pd.option_context("display.width", 200, "display.max_columns", 40):
    print(d.head(6).to_string(index=False))

print()
print("=" * 100)
print("2. Candidate subsets, by every rule the column set allows")
print("=" * 100)
for col in d.columns:
    if d[col].dtype == bool or d[col].nunique() <= 6:
        vc = d[col].value_counts(dropna=False).to_dict()
        print(f"  {col:26s} {vc}")
    elif pd.api.types.is_numeric_dtype(d[col]):
        print(f"  {col:26s} min {d[col].min():.4g}  max {d[col].max():.4g}")

print()
print("=" * 100)
print("3. Try to reproduce the declared counts")
print("=" * 100)
TARGETS = {"strict signals": 58, "toxicity spectrum (top 30)": 30,
           "unclassified": 83}
# strict: a q value at or below 0.05 and an ROR above 1 is the usual definition
for qcol in ("q_bh", "q", "q_value", "fdr"):
    if qcol in d.columns:
        for cutoff in (0.05, 0.01):
            n = int((pd.to_numeric(d[qcol], errors="coerce") <= cutoff).sum())
            print(f"  {qcol} <= {cutoff:<5} -> {n} terms"
                  f"   {'<== matches 58' if n == 58 else ''}")
        break
else:
    print("  no q-value column found")

for col in ("signal", "is_signal", "strict", "strict_signal"):
    if col in d.columns:
        try:
            n = int(d[col].astype(bool).sum())
            print(f"  {col} is true -> {n} terms"
                  f"   {'<== matches 58' if n == 58 else ''}")
        except Exception:  # noqa: BLE001
            pass

# unclassified: whatever column holds the category
for col in d.columns:
    if any(k in col.lower() for k in ("categ", "class", "group", "type", "label")):
        vc = d[col].value_counts(dropna=False)
        print(f"\n  category column {col!r}:")
        for k, v in vc.items():
            mark = "   <== matches 83" if v == 83 else ""
            print(f"      {str(k)[:50]:52s} {v:>5}{mark}")

print()
print("=" * 100)
print("4. Is there a build script that writes table 2b/2c/2d?")
print("=" * 100)
hits = []
for src in (ROOT / "src").glob("*.py"):
    t = src.read_text(encoding="utf-8", errors="replace")
    if "2b" in t or "2c" in t or "2d" in t or "unclassified" in t.lower():
        hits.append(src.name)
        for ln in t.splitlines():
            s = ln.strip()
            if ("unclassified" in s.lower() or "table2" in s.lower()
                    or "2b" in s or "2c" in s or "2d" in s):
                print(f"  {src.name}: {s[:104]}")
if not hits:
    print("  no script references the table 2b/2c/2d subsets")
