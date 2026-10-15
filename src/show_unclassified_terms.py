# -*- coding: utf-8 -*-
"""
Show the 83 unclassified ocular terms, with the evidence needed to classify them.

The manuscript lists these as awaiting manual review.  Manual review needs the terms and
their disproportionality values side by side, ordered so that the ones which matter for
the argument come first: a term with a strong ratio and a small q contributes to the
signal profile, while a term with a ratio near or below 1 does not, and the two should
not be reviewed as though they were equivalent.

This prints them with group, counts, ratio, interval, q and which criteria flagged them,
before any classification is attempted.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
src = pd.read_csv(ROOT / "results" / "faers_signals_annotated.csv",
                  encoding="utf-8-sig")

print("=" * 104)
print("1. The category column, as the analysis left it")
print("=" * 104)
print(src.category.value_counts().to_string())
print()
print("  Note: 'unclassified ocular' holds the terms the curated lists and the "
      "data-driven")
print("  groups did not place.  The manuscript reports them as awaiting manual review.")

unc = src[src.category == "unclassified ocular"].copy()
unc = unc.sort_values("ror", ascending=False)

print()
print("=" * 104)
print("2. All 83, ordered by reporting odds ratio")
print("=" * 104)
print(f"  {'term':44s} {'a':>5s} {'ror':>9s} {'95% CI':>18s} {'q_bh':>10s} "
      f"{'strict':>6s} {'group':>22s}")
for _, r in unc.iterrows():
    ci = f"{r.ror_lcl:.2f}-{r.ror_ucl:.2f}" if pd.notna(r.ror_lcl) else "-"
    q = f"{r.q_bh:.2e}" if pd.notna(r.q_bh) else "-"
    print(f"  {str(r.term)[:44]:44s} {int(r.a):>5d} {r.ror:>9.2f} {ci:>18s} "
          f"{q:>10s} {'yes' if r.signal_strict else 'no':>6s} "
          f"{str(r.group)[:22]:>22s}")

print()
print("=" * 104)
print("3. How many of them actually carry signal")
print("=" * 104)
strong = unc[unc.signal_strict]
print(f"  total unclassified          : {len(unc)}")
print(f"  strict signals among them   : {len(strong)}")
print(f"  ratio above 1               : {int((unc.ror > 1).sum())}")
print(f"  ratio at or below 1         : {int((unc.ror <= 1).sum())}")
print(f"  q at or below 0.05          : {int((unc.q_bh <= 0.05).sum())}")
print()
if len(strong):
    print("  The strict ones, which are the ones that affect the reported profile:")
    for _, r in strong.iterrows():
        print(f"      {str(r.term)[:56]:58s} ror {r.ror:>8.2f}  q {r.q_bh:.2e}")

print()
print("=" * 104)
print("4. The existing group column, for terms that already have one")
print("=" * 104)
grouped = src[src.category != "unclassified ocular"]
print(grouped.group.value_counts().to_string())
print()
print("  the curated panel terms, which define the groups:")
cur = src[src.source.astype(str).str.contains("Curated", na=False)]
for _, r in cur.sort_values("group").iterrows():
    print(f"      {str(r.group):26s} {str(r.term)[:52]}")
