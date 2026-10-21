# -*- coding: utf-8 -*-
"""Correct the period-coverage sentences with the figures now verified.

The first draft of these sentences said 57 cases fell outside the periods and that some cases
straddled the boundary.  The verified numbers are: 57 cases whose every receipt date is before
2004, 20,692,626 with at least one date in 2004-2026, and no case on both sides of 2016.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
cov = json.loads((ROOT / "results" / "audit_period_coverage.json").read_text(encoding="utf-8"))

p = MAN / "TADS_results.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"This analysis is within one database.*?supplementary Table S7\)\.", text, re.S)
assert old, "coverage sentence not found"
new = (f"This analysis is within one database and shares its reporting artefacts; it tests "
       f"stability across reporting eras, not generalisability. The two periods cover "
       f"{cov['inrange_cases']:,} of the {cov['dedup_rows']:,} de-duplicated cases; the remaining "
       f"{cov['pre2004_cases']} carry receipt dates before 2004 and fall outside both periods "
       f"(supplementary Table S7).")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("results coverage sentence corrected")

p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"Cases whose surviving report carries a receipt date before 2004.*?Table S7\.", text, re.S)
assert old, "methods coverage sentence not found"
new = (f"Cases whose every receipt date precedes 2004 fall outside both periods "
       f"({cov['pre2004_cases']} of {cov['dedup_rows']:,}); the year distribution is given in "
       f"supplementary Table S7.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("methods coverage sentence corrected")
