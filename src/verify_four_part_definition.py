# -*- coding: utf-8 -*-
"""
Apply the four-part strict definition and confirm it reproduces the table exactly.

The flag is built in faers_disproportionality.py line 327 as

    signal_strict = signal_ror & signal_prr & signal_ic & (q_bh < 0.05)

that is: ROR lower 95% bound above 1, PRR at least 2, IC025 above 0, and a
Benjamini-Hochberg q below 0.05.  The manuscript states only the first two plus a case
count, which is why RETINAL DETACHMENT looked like a term the criteria should have kept -
its ROR lower bound is 1.11 and its PRR is 2.06, but its q is 0.069, so the fourth
condition excludes it correctly.

Applying all four should return exactly the rows the tables contain.  If it does, the
manuscript's stated criteria are the thing to fix, not the tables.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "tables"

print("=" * 92)
print("1. The four conditions, applied to each artefact")
print("=" * 92)


def strict_mask(d):
    return ((pd.to_numeric(d["ror_lcl"], errors="coerce") > 1)
            & (pd.to_numeric(d["prr"], errors="coerce") >= 2)
            & (pd.to_numeric(d["ic025"], errors="coerce") > 0)
            & (pd.to_numeric(d["q_bh"], errors="coerce") < 0.05))


def three_part(d):
    return ((pd.to_numeric(d["ror_lcl"], errors="coerce") > 1)
            & (pd.to_numeric(d["prr"], errors="coerce") >= 2)
            & (pd.to_numeric(d["a"], errors="coerce") >= 3))


for name in ("Table2_signals.csv", "Table2b_signals_strict.csv",
             "Table2_signals_full_panel.csv"):
    p = TAB / name
    d = pd.read_csv(p)
    four = int(strict_mask(d).sum())
    three = int(three_part(d).sum())
    flagged = int((d["signal_strict"] == True).sum())  # noqa: E712
    print(f"\n  {name}: {len(d)} rows")
    print(f"      flagged in the file           : {flagged}")
    print(f"      four-part definition          : {four}"
          f"{'   <-- matches the flag' if four == flagged else ''}")
    print(f"      three-part (as manuscript says): {three}"
          f"{'   <-- matches the flag' if three == flagged else ''}")

print()
print("=" * 92)
print("2. Source file behind the earlier '58'")
print("=" * 92)
src = ROOT / "data" / "derived" / "faers_2x2.csv"
if src.exists():
    d = pd.read_csv(src)
    eth = d[d.get("drug", "").astype(str).str.upper().str.contains("ETHAMBUTOL",
                                                                  na=False)] \
        if "drug" in d.columns else d
    print(f"  {src.name}: {len(d)} rows total; "
          f"{len(eth)} rows for ethambutol")
    print(f"      flagged signal_strict         : {int((eth['signal_strict'] == True).sum())}")  # noqa: E712
    print(f"      four-part definition          : {int(strict_mask(eth).sum())}")
    print(f"      three-part definition         : {int(three_part(eth).sum())}")

print()
print("=" * 92)
print("3. The count to state, and the criteria to state with it")
print("=" * 92)
panel = pd.read_csv(TAB / "Table2_signals.csv")
n = int(strict_mask(panel).sum())
print(f"""  The ocular panel holds 152 terms, of which {n} meet the strict definition.  The
  manuscript currently says 58 in the abstract and in Section 3.2, which is the count from
  the 177-term source file before the ocular-tuberculosis manifestations and the
  non-ocular terms were separated out, and it states only three of the four conditions.

  Both need correcting: the count to {n}, and the criteria to include IC025 above 0 and a
  Benjamini-Hochberg q below 0.05.""")

print()
print("  terms excluded from the panel by the fourth condition alone:")
d3 = panel[three_part(panel) & ~strict_mask(panel)]
if len(d3):
    cols = [c for c in ("term", "a", "ror", "ror_lcl", "ror_ucl", "prr", "ic025",
                        "q_bh") if c in panel.columns]
    print(d3[cols].to_string(index=False))
else:
    print("      none")
