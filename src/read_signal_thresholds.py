# -*- coding: utf-8 -*-
"""
Read the actual thresholds behind the signal flags instead of assuming them.

Four attempts have now failed to reproduce the flagged counts from the criteria, which
means the assumption behind each attempt was wrong rather than the data.  The flags are
built from named boolean columns, so those columns already contain the answer: their rows
can be compared against the numeric columns to read off the threshold each one uses.

Guessing a fifth time would be worse than useless, so this measures instead.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

CANDIDATES = [
    ROOT / "tables" / "Table2_signals.csv",
    ROOT / "tables" / "Table2_signals_full_panel.csv",
    ROOT / "data" / "derived" / "faers_2x2.csv",
]

for p in CANDIDATES:
    if not p.exists():
        continue
    d = pd.read_csv(p)
    print("=" * 94)
    print(f"{p.relative_to(ROOT)}  ({len(d)} rows)")
    print("=" * 94)
    print(f"  columns: {list(d.columns)}")
    print()

    bool_cols = [c for c in d.columns if c.startswith("signal")]
    print(f"  boolean flag columns: {bool_cols}")
    for c in bool_cols:
        print(f"      {c:18s} True in {int((d[c] == True).sum()):>5} rows")  # noqa: E712

    # read the threshold each flag applies by comparing it to the numeric columns
    numerics = [c for c in ("ror", "ror_lcl", "ror_ucl", "prr", "ic025", "ebgm05",
                            "q_bh", "a", "n_drug") if c in d.columns]
    print()
    print("  thresholds implied by each flag")
    for c in bool_cols:
        if c == "signal_any":
            continue
        flag = d[c] == True  # noqa: E712
        if not flag.any():
            continue
        print(f"      {c}:")
        for n in numerics:
            v = pd.to_numeric(d[n], errors="coerce")
            inside = v[flag]
            outside = v[~flag]
            print(f"          {n:8s} within flag: min {inside.min():>12.4f}  "
                  f"max {inside.max():>12.4f}")
            if len(outside):
                print(f"          {'':8s} outside    : min {outside.min():>12.4f}  "
                      f"max {outside.max():>12.4f}")

    # the combination, using the flags themselves
    if all(c in d.columns for c in ("signal_ror", "signal_prr", "signal_ic")):
        combo = d.signal_ror & d.signal_prr & d.signal_ic
        if "q_bh" in d.columns:
            combo_q = combo & (pd.to_numeric(d.q_bh, errors="coerce") < 0.05)
            print()
            print(f"  signal_ror & signal_prr & signal_ic            : {int(combo.sum())}")
            print(f"  ... and q_bh < 0.05                            : {int(combo_q.sum())}")
        if "signal_strict" in d.columns:
            print(f"  signal_strict as stored                        : "
                  f"{int((d.signal_strict == True).sum())}")  # noqa: E712
            diff = combo_q & (d.signal_strict != True)  # noqa: E712
            print(f"  combination true but signal_strict false       : {int(diff.sum())}")
            if diff.any():
                cols = [c for c in ("term", "a", "ror", "prr", "ic025", "q_bh")
                        if c in d.columns]
                print(d[diff][cols].to_string(index=False))
            diff2 = (d.signal_strict == True) & ~combo_q  # noqa: E712
            print(f"  signal_strict true but combination false       : {int(diff2.sum())}")
            if diff2.any():
                cols = [c for c in ("term", "a", "ror", "prr", "ic025", "q_bh")
                        if c in d.columns]
                print(d[diff2][cols].to_string(index=False))
    print()
