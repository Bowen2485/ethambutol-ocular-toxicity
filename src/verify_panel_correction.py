# -*- coding: utf-8 -*-
"""
Confirm the panel correction landed in both manuscripts and in the table files.

The panel counts changed from 177 terms and 58 strict signals to 152 and 45, with two
new separate tables.  Both language versions and four exported files had to move
together, so this checks all six places rather than assuming the edits took.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")
T = ROOT / "tables"

print("=" * 96)
print("1. Table files and their row counts")
print("=" * 96)
WANT = {
    "Table2_signals.csv": 152,
    "Table2b_signals_strict.csv": 45,
    "Table2e_ocular_tuberculosis.csv": 12,
    "Table2f_non_ocular_terms.csv": 13,
    "Table2c_toxicity_spectrum.csv": 30,
    "Table2d_panel_anatomical.csv": 5,
    "Table2_signals_full_panel.csv": 178,
}
ok = True
for name, expected in WANT.items():
    p = T / name
    if not p.exists():
        print(f"  {name:34s} MISSING")
        ok = False
        continue
    n = len(pd.read_csv(p, encoding="utf-8-sig"))
    good = n == expected
    ok &= good
    print(f"  {name:34s} {n:>4} rows, expected {expected:>4}  "
          f"{'ok' if good else 'MISMATCH'}")

print()
print("=" * 96)
print("2. Text claims in both versions")
print("=" * 96)
STALE = ["177 terms", "58 terms", "177 个术语", "58 个术语",
         "awaiting manual review, 83", "待人工复核，83"]
FRESH_EN = ["152 terms", "45", "Table 2e", "Table 2f", "152 terms, of which 45",
            "Thirteen terms are removed", "152 ocular terms"]
FRESH_CN = ["152 个术语", "45 个", "表2e", "表2f", "13 个术语"]
for label, text, fresh in (("EN", EN, FRESH_EN), ("CN", CN, FRESH_CN)):
    print(f"  {label}:")
    for k in STALE:
        if k in text:
            print(f"      STALE STILL PRESENT: {k}")
    for k in fresh:
        print(f"      {'ok     ' if k in text else 'MISSING'}  {k}")

print()
print("=" * 96)
print("3. The panel composition, recomputed from the files")
print("=" * 96)
oc = pd.read_csv(T / "Table2_signals.csv", encoding="utf-8-sig")
tb = pd.read_csv(T / "Table2e_ocular_tuberculosis.csv", encoding="utf-8-sig")
no = pd.read_csv(T / "Table2f_non_ocular_terms.csv", encoding="utf-8-sig")
print(f"  ocular panel        : {len(oc):>4} terms, "
      f"{int(oc.signal_strict.sum()):>3} strict")
print(f"  ocular tuberculosis : {len(tb):>4} terms, "
      f"{int(tb.signal_strict.sum()):>3} strict")
print(f"  non-ocular          : {len(no):>4} terms, "
      f"{int(no.signal_strict.sum()):>3} strict")
print(f"  total accounted for : {len(oc) + len(tb) + len(no)} of 177")
print()
print(f"  anatomical groups in the ocular panel:")
for g, n in oc.group.value_counts().items():
    print(f"      {str(g):28s} {n:>4}")

print()
print("=" * 96)
print("4. The argument's key terms survived the correction")
print("=" * 96)
KEY = ["OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "DYSCHROMATOPSIA",
       "COLOUR BLINDNESS", "VISION BLURRED", "DRY EYE", "CATARACT",
       "EYE PAIN", "GLAUCOMA"]
for t in KEY:
    row = oc[oc.term == t]
    if len(row):
        r = row.iloc[0]
        print(f"  {t:26s} present  a={int(r.a):>4d}  ror={r.ror:>8.2f}  "
              f"{'strict' if r.signal_strict else 'not strict'}")
    else:
        print(f"  {t:26s} NOT IN THE PANEL - check")

print()
print("=" * 96)
print("Overall")
print("=" * 96)
print("  consistent" if ok else "  at least one file disagrees with the text")
