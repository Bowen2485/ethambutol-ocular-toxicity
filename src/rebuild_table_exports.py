# -*- coding: utf-8 -*-
"""
Rebuild the exported table files from the authoritative signal table.

Why rebuild rather than adjust the text
    The manuscript quotes 177 ocular terms of which 58 are strict signals.  Both numbers
    are what the analysis produced: results/faers_signals_annotated.csv has 177 rows and
    58 rows with signal_strict set.  The files in tables/ are what drifted - Table 2 held
    an 88-term subset and Table 2b held 30 of the 58 strict rows, so a reader opening
    them would find a third of the strict signals missing and no indication why.
    Correcting the exports leaves the analysis untouched.

What is written
    Table 2     all 177 terms, ethambutol against the whole database
    Table 2b    the 58 strict signals
    Table 2c    the drug-toxicity-spectrum rows, top 30 by ROR as the manuscript states
    Table 2d    the 83 unclassified terms, unchanged in content but re-exported
    Table 2 full panel  the 178-term derived panel, so PTOSIS is restored

    The previous column layouts are preserved so anything downstream that reads these
    files keeps working; only the row sets change.
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
print("Source")
print("=" * 96)
print(f"  {len(src)} terms, {int(src.signal_strict.sum())} strict, "
      f"categories {src.category.value_counts().to_dict()}")

#: the column order the existing exports use, so downstream readers are unaffected
COLS_T2 = ["drug", "term", "group", "a", "n_drug", "n_event", "ror", "ror_lcl",
           "ror_ucl", "prr", "chi2_yates", "ic025", "ebgm05", "q_bh",
           "signal_ror", "signal_prr", "signal_ic", "signal_strict"]
COLS_T2B = ["term", "group", "a", "n_drug", "n_event", "ror", "ror_lcl", "ror_ucl",
            "prr", "chi2_yates", "ic025", "ebgm05", "q_bh",
            "signal_ror", "signal_prr", "signal_ic", "signal_strict"]


def take(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df[[c for c in cols if c in df.columns]].copy()


print()
print("=" * 96)
print("Writing the exports")
print("=" * 96)

# ---- Table 2: every term
t2_old = pd.read_csv(T / "Table2_signals.csv", encoding="utf-8-sig")
t2 = take(src, COLS_T2)
t2.to_csv(T / "Table2_signals.csv", index=False, encoding="utf-8-sig")
print(f"  Table2_signals.csv            {len(t2_old):>4} -> {len(t2):>4} rows")

# ---- Table 2b: every strict signal
t2b_old = pd.read_csv(T / "Table2b_signals_strict.csv", encoding="utf-8-sig")
t2b = take(src[src.signal_strict].sort_values("q_bh"), COLS_T2B)
t2b.to_csv(T / "Table2b_signals_strict.csv", index=False, encoding="utf-8-sig")
print(f"  Table2b_signals_strict.csv    {len(t2b_old):>4} -> {len(t2b):>4} rows")

# ---- Table 2c: the drug-toxicity spectrum, top 30 by ROR as the manuscript states
t2c_old = pd.read_csv(T / "Table2c_toxicity_spectrum.csv", encoding="utf-8-sig")
spec = src[src.category == "drug-toxicity spectrum"].sort_values("ror", ascending=False)
t2c = take(spec.head(30), COLS_T2)
t2c.to_csv(T / "Table2c_toxicity_spectrum.csv", index=False, encoding="utf-8-sig")
print(f"  Table2c_toxicity_spectrum.csv {len(t2c_old):>4} -> {len(t2c):>4} rows "
      f"(of {len(spec)} in the category)")

# ---- Table 2d: the unclassified terms
t2d_old = pd.read_csv(T / "Table2d_unclassified_terms.csv", encoding="utf-8-sig")
unc = src[src.category == "unclassified ocular"].sort_values("q_bh")
t2d = take(unc, COLS_T2) if set(COLS_T2) <= set(unc.columns) else \
    take(unc, list(t2d_old.columns))
t2d.to_csv(T / "Table2d_unclassified_terms.csv", index=False, encoding="utf-8-sig")
print(f"  Table2d_unclassified_terms.csv{len(t2d_old):>4} -> {len(t2d):>4} rows")

# ---- the full derived panel, so PTOSIS is restored
fp_old = pd.read_csv(T / "Table2_signals_full_panel.csv", encoding="utf-8-sig")
derived = pd.read_csv(D / "ocular_terms.csv", encoding="utf-8-sig")
merged = derived.copy()
if "term" in merged.columns and "term" in src.columns:
    keep = [c for c in src.columns if c in merged.columns and c != "term"]
    merged = merged.drop(columns=keep, errors="ignore").merge(
        src[[c for c in src.columns if c in fp_old.columns or c == "term"]],
        on="term", how="left")
merged.to_csv(T / "Table2_signals_full_panel.csv", index=False,
              encoding="utf-8-sig")
print(f"  Table2_signals_full_panel.csv {len(fp_old):>4} -> {len(merged):>4} rows")

print()
print("=" * 96)
print("Verification after writing")
print("=" * 96)
CHECKS = [
    ("Table2_signals.csv", 177, "all terms"),
    ("Table2b_signals_strict.csv", 58, "strict signals"),
    ("Table2c_toxicity_spectrum.csv", 30, "spectrum, top 30"),
    ("Table2d_unclassified_terms.csv", 83, "unclassified"),
    ("Table2_signals_full_panel.csv", 178, "derived panel"),
]
ok = True
for name, expected, what in CHECKS:
    d = pd.read_csv(T / name, encoding="utf-8-sig")
    good = len(d) == expected
    ok &= good
    print(f"  {name:32s} {len(d):>4} rows  expected {expected:>4}  "
          f"{'ok' if good else 'MISMATCH'}   ({what})")
print()
print("  all table exports consistent with the text" if ok
      else "  at least one export still disagrees; inspect before submitting")

# the text's counts, for the record
print()
print("  manuscript states: Table 2 = 177 terms, Table 2b = 58, Table 2c = top 30,")
print("                     Table 2d = 83 awaiting review")
