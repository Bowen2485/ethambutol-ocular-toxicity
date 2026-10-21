# -*- coding: utf-8 -*-
"""Sync the checklist item 6c and the S1 sheet note with the final Methods."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

p = ROOT / "docs" / "READUS-PV_checklist.md"
t = p.read_text(encoding="utf-8")
old = ("Exposure by substance/medicinalproduct substring; any role in main, suspect-only as "
       "sensitivity; events grouped by MedDRA's own narrow query sets, not by a list assembled "
       "here; queries overlap and are not claimed exhaustive")
new = ("Exposure from the drug-name fields (drugname, prod_ai) with a single-token substring match; "
       "any role in main, suspect-only as sensitivity; events grouped by MedDRA's own narrow query "
       "sets, not by a list assembled here; queries overlap and are not claimed exhaustive. The "
       "time-to-onset analysis additionally used a 17-term case-level definition, provided in "
       "Supplementary Table S9")
assert old in t, "checklist 6c not found"
t = t.replace(old, new, 1)
p.write_text(t, encoding="utf-8")
print("checklist 6c updated")

p = ROOT / "src" / "build_supplement_v2.py"
s = p.read_text(encoding="utf-8")
old = ("p from the exact test stated in column 'Test'; q is Benjamini-Hochberg across the 15 terms.")
new = ("P values were calculated using the tests specified in the 'Test' column; q values are "
       "Benjamini-Hochberg adjusted across the 15 terms.")
assert old in s, "S1 note not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("S1 note updated")
