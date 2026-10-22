# -*- coding: utf-8 -*-
"""Tenth round: README entry and file list for the figure-legends file."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8")

if "Figure_legends.docx" not in text:
    text = text.replace(
        "| `READUS-PV_checklist.docx` |",
        "| `Figure_legends.docx` | Standalone Figure 1–4 legends |\n| `READUS-PV_checklist.docx` |", 1)

block = """

## Tenth review round (2026-10-22)

1. **Title-page counts are now computed**, not typed: 4 figures, 4 tables and 19 references are
   read from the manuscript and the reference list, so the count cannot drift again.
2. **The figure legends were missing.** The round-four rewrite of the declarations block replaced
   the whole block and dropped the legends that followed it, which is why the PDF showed images
   without legend text. They are restored after the declarations (page 17) and also supplied as
   `Figure_legends.docx`.
3. **Table 4 no longer splits**: short tables reserve their estimated height, and a caption now
   reserves room for the table that follows, so caption and rows sit together on page 19.
4. PDF: 25 pages, 0 overfull.
"""
if "Tenth review round" not in text:
    text = text.rstrip() + block
p.write_text(text, encoding="utf-8")
print("README updated")
