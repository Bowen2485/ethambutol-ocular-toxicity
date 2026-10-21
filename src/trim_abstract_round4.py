# -*- coding: utf-8 -*-
"""Trim the abstract back under 300 words after the fourth-round additions."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "manuscript" / "TADS_EN.md"
text = p.read_text(encoding="utf-8")

pairs = [
    ("its ocular reporting signal is well recognised", "its ocular signal is well recognised"),
    ("Whether that signal is concentrated in the optic nerve, rather than reflecting a general "
     "increase in ocular reporting, has not been tested against MedDRA's own ocular queries.",
     "Whether it is concentrated in the optic nerve, rather than reflecting a general increase in "
     "ocular reporting, has not been tested against MedDRA's own queries."),
    ("with replication in two further national systems and a short exploratory transcriptomic "
     "reanalysis",
     "with replication in two national systems and an exploratory transcriptomic reanalysis"),
    ("with Benjamini–Hochberg control across the eleven, and described the preferred terms inside "
     "the optic-nerve query against pre-specified control terms.",
     "with Benjamini–Hochberg control, and described the terms inside the optic-nerve query against "
     "pre-specified controls."),
    ("Exposure role, reporting period and a fixed-regimen contrast were examined as sensitivity "
     "analyses,",
     "Exposure role, period and a fixed-regimen contrast were sensitivity analyses,"),
    ("and optic neuritis (156 cases; 23.67, 20.19–27.75) carried the evidence",
     "and optic neuritis (156; 23.67, 20.19–27.75) carried the evidence"),
    ("An optic-nerve-related signal was also observed in JADER (optic neuropathy 570.96, "
     "413.50–788.37) and Canada Vigilance (composite outcome 21.85, 14.13–33.79); the non-specific "
     "comparison was assessable in FAERS and, for mapped terms, JADER, but not in Canada.",
     "An optic-nerve signal was also observed in JADER (optic neuropathy 570.96, 413.50–788.37) and "
     "Canada Vigilance (21.85, 14.13–33.79); the non-specific comparison was possible in FAERS and, "
     "for mapped terms, JADER, but not in Canada."),
    ("In the exploratory transcriptomic analysis, selected ferroptosis-related predictions were not "
     "reproduced, and their clinical relevance remains uncertain.",
     "Exploratory transcriptomic analysis did not reproduce selected ferroptosis-related "
     "predictions; their clinical relevance remains uncertain."),
    ("Across three spontaneous-reporting systems, ethambutol showed a reproducible "
     "optic-nerve-predominant reporting pattern",
     "Across three reporting systems, ethambutol showed a reproducible optic-nerve-predominant "
     "reporting pattern"),
]
for old, new in pairs:
    assert old in text, f"not found: {old[:60]!r}"
    text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")

block = text[text.find("## Abstract"):text.find("**Keywords")]
words = len([w for w in re.sub(r"[#*]", " ", block).split() if re.search(r"\w", w)])
print(f"abstract now {words} words")
