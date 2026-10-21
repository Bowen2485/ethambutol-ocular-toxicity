# -*- coding: utf-8 -*-
"""Trim the abstract to 295 words and fix two supplement details flagged in the review.

    S1 column header "p (exact test)" implied that every p came from an exact test; the test is
    named per row, so the header becomes "P value".
    S11 described the Canadian rule as the MedDRA narrow-search rule; it is a study-specific
    string match, and the sheet now says so.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

p = ROOT / "manuscript" / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
pairs = [
    ("A term-level optic-nerve signal was also observed in JADER", "A term-level optic-nerve signal was also seen in JADER"),
    ("Canada Vigilance showed a broader string-matched optic composite", "Canada Vigilance showed a broader string-matched composite"),
    ("and whether that pattern replicates in independent systems", "and whether it replicates in independent systems"),
    ("has not been tested against MedDRA's own queries", "has not been tested against MedDRA's queries"),
    ("four queries lay above unity, three below, four null", "four lay above unity, three below, four null"),
    ("selected ferroptosis-related predictions, whose clinical relevance is uncertain",
     "selected ferroptosis-related predictions, of uncertain clinical relevance"),
]
for old, new in pairs:
    assert old in text, f"not found: {old[:50]!r}"
    text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
block = text[text.find("## Abstract"):text.find("**Keywords")]
print("abstract words:", len([w for w in re.sub(r"[#*]", " ", block).split() if re.search(r"\w", w)]))

# ------------------------------------------------------------ supplement tweaks
p = ROOT / "src" / "build_supplement_v2.py"
s = p.read_text(encoding="utf-8")
s = s.replace('"p (exact test)": r["p_display"]', '"P value": r["p_display"]')
old = ('{"Rule": "Any preferred term containing the string OPTIC",\n'
       '     "Rationale": ("the MedDRA narrow optic-nerve search is defined as all terms containing "\n'
       "                   \"'optic'; the Canadian extract is coded to MedDRA 29.0, so the rule is applied \"\n"
       '                   "directly"),')
new = ('{"Rule": "Any preferred term containing the string OPTIC (study-specific composite)",\n'
       '     "Rationale": ("this is a string match built for this analysis, not a re-implementation "\n'
       '                   "of the 45-term Optic nerve disorders query; it includes terms of "\n'
       '                   "different clinical meaning, such as imaging terms and surgical "\n'
       '                   "procedures, so the Canadian result is exploratory"),')
assert old in s, "S11 rule text not found"
s = s.replace(old, new, 1)
s = s.replace('"Rule": "Any preferred term containing the string OPTIC"', '"Rule": "Any preferred term containing OPTIC (study-specific)"')
p.write_text(s, encoding="utf-8")
print("supplement builder updated: P value header, S11 rationale")
