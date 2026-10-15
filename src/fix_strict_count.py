# -*- coding: utf-8 -*-
"""
Correct the strict-signal count and the criteria stated alongside it.

Established from the data, not from memory
    The flags are computed in faers_disproportionality.py as

        signal_strict = signal_ror & signal_prr & signal_ic & (q_bh < 0.05)

    and reading the thresholds off the flag columns gives

        signal_ror    ror_lcl > 1        47 terms
        signal_prr    prr     >= 2       46 terms
        signal_ic     ic025   > 0        80 terms
        signal_strict all three and q_bh < 0.05   45 terms

    The ocular panel holds 152 terms, of which 45 are strict.  This matches
    tables/Table2b_signals_strict.csv exactly.

The two faults being fixed
    The abstract and Section 3.2 say 58.  That figure is real but belongs to the 177-term
    source file (data/derived/faers_2x2.csv), before the twelve ocular-tuberculosis
    manifestations and thirteen non-ocular terms were separated out.  Against the current
    panel it is wrong.

    The criteria are stated as three conditions - ROR lower bound above 1, PRR at least 2,
    cases at least 3 - which omits both IC025 above 0 and the Benjamini-Hochberg q below
    0.05.  That omission is what made RETINAL DETACHMENT look wrongly excluded: its ROR
    lower bound is 1.11 and its PRR is 2.06, so it passes the stated three, but its q is
    0.069 and the fourth condition excludes it correctly.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

# ---------------------------------------------------------------- English
t = EN.read_text(encoding="utf-8")
en_edits = [
    (
        "ocular terms, 58 met strict signal criteria.",
        "ocular terms, 45 met the strict signal criteria.",
    ),
    (
        "cases and **58 met all strict signal criteria** (ROR lower 95% CI > 1, PRR >= 2,",
        "cases and **45 met all strict signal criteria** (ROR lower 95% CI > 1, PRR >= 2, "
        "IC025 > 0 and a Benjamini-Hochberg q < 0.05;",
    ),
]
print("=" * 90)
print("English")
print("=" * 90)
for old, new in en_edits:
    if old in t:
        t = t.replace(old, new)
        print(f"  ok      {old[:70]}")
    else:
        print(f"  ABSENT  {old[:70]}")
EN.write_text(t, encoding="utf-8")

# ---------------------------------------------------------------- Chinese
t = CN.read_text(encoding="utf-8")
cn_edits = [
    (
        "**58 项构成严格信号**（ROR 95%CI 下限 >1、",
        "**45 项构成严格信号**（ROR 95%CI 下限 >1、",
    ),
]
print()
print("=" * 90)
print("Chinese")
print("=" * 90)
for old, new in cn_edits:
    if old in t:
        t = t.replace(old, new)
        print(f"  ok      {old[:70]}")
    else:
        print(f"  ABSENT  {old[:70]}")
CN.write_text(t, encoding="utf-8")

# ---------------------------------------------------------------- report
print()
print("=" * 90)
print("Result")
print("=" * 90)
for label, p, token in (("EN", EN, "45 met the strict"), ("CN", CN, "45 项构成严格信号")):
    s = p.read_text(encoding="utf-8")
    print(f"  {label}: corrected phrase present: {token in s}")
    for bad in ("58 met strict", "58 项构成严格信号", "**58 met all strict"):
        if bad in s:
            print(f"      still contains {bad!r}")
            for i, ln in enumerate(s.splitlines(), 1):
                if bad in ln:
                    print(f"          line {i}: {ln.strip()[:110]}")
