# -*- coding: utf-8 -*-
"""
Settle the strict-signal count, which the manuscript currently states two ways.

The abstract and Section 3.2 say 58 terms met the strict criteria; Section 3.7 and the
table list say 45.  One of the two is stale, and which one matters because the number is
quoted in the abstract.

History that explains how the disagreement arose
    The ocular panel was originally cut at 177 terms with 58 strict signals.  Twelve
    ocular-tuberculosis manifestations and thirteen non-ocular terms were afterwards moved
    out into their own tables, leaving 152 terms, and the strict count was recomputed
    against that panel.  The table file was rebuilt and the affected sentences were not
    all updated.

Rather than trust either figure, the criteria are re-applied here to the table that
actually exists, so the answer comes from the data.  The stated criteria are a lower 95%
confidence bound above 1 for the ROR, a PRR of at least 2, and at least three cases.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "tables"

print("=" * 92)
print("1. What the table files contain")
print("=" * 92)
for name in ("Table2_signals.csv", "Table2b_signals_strict.csv",
             "Table2_signals_full_panel.csv", "Table2e_ocular_tuberculosis.csv",
             "Table2f_non_ocular_terms.csv"):
    p = TAB / name
    if not p.exists():
        print(f"  {name:36s} absent")
        continue
    d = pd.read_csv(p)
    print(f"  {name:36s} {len(d):>5} rows, {len(d.columns)} cols")
    print(f"      columns: {list(d.columns)[:10]}")

print()
print("=" * 92)
print("2. Re-applying the strict criteria to the panel")
print("=" * 92)
full = TAB / "Table2_signals.csv"
if not full.exists():
    raise SystemExit("  the panel table is absent; cannot verify")

d = pd.read_csv(full)
print(f"  panel: {len(d)} rows")

# locate the columns the criteria need, whatever they are called
cols = {c.lower(): c for c in d.columns}
def find(*names):
    for n in names:
        for lc, orig in cols.items():
            if n in lc:
                return orig
    return None

ror_l = find("ror_l", "lower", "ci_low", "lcl")
prr = find("prr")
a = find("a", "case", "n_case")
print(f"  resolved columns: ror_lower={ror_l!r}  prr={prr!r}  cases={a!r}")

if ror_l and prr:
    mask = (pd.to_numeric(d[ror_l], errors="coerce") > 1) & \
           (pd.to_numeric(d[prr], errors="coerce") >= 2)
    if a:
        mask &= pd.to_numeric(d[a], errors="coerce") >= 3
    n = int(mask.sum())
    print()
    print(f"  rows meeting ROR lower CI > 1 and PRR >= 2"
          f"{' and cases >= 3' if a else ''}: {n}")
    print()
    print(f"  {'that equals the Table 2b row count' if n == 45 else ''}")
    if n != 45:
        print(f"  NOTE: Table 2b holds 45 rows; the criteria applied to the current")
        print(f"  panel give {n}.  Investigate before changing the text.")
else:
    print("  could not resolve the columns; listing them instead:")
    print(f"      {list(d.columns)}")

print()
print("=" * 92)
print("3. Every place the two figures are stated")
print("=" * 92)
for label, p in (("EN", ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"),
                 ("CN", ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md")):
    t = p.read_text(encoding="utf-8").splitlines()
    print(f"\n  {label}")
    for i, ln in enumerate(t, 1):
        s = ln.strip()
        if ("58" in s and ("strict" in s.lower() or "严格" in s)) or \
           ("45" in s and ("strict" in s.lower() or "严格" in s) and "Table" not in s):
            print(f"      line {i:>5d}: {s[:120]}")
