# -*- coding: utf-8 -*-
"""Round twelve: README entry, file list and sync entry for the Word manuscript."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- sync list
p = ROOT / "src" / "sync_repository.py"
s = p.read_text(encoding="utf-8")
if "Ethambutol_TADS_manuscript.docx" not in s:
    old = '    ("submission/tads/Figure_legends.docx", "submission/Figure_legends.docx"),'
    new = ('    ("submission/tads/Ethambutol_TADS_manuscript.docx",\n'
           '     "submission/Ethambutol_TADS_manuscript.docx"),\n' + old)
    assert old in s
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print("sync list: Word manuscript added")

# ------------------------------------------------------------------- README
p = ROOT / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8")
if "Ethambutol_TADS_manuscript.docx" not in text:
    text = text.replace(
        "| `Figure_legends.docx` |",
        "| `Ethambutol_TADS_manuscript.docx` | Word manuscript (text, 4 tables, 4 figures) |\n"
        "| `Figure_legends.docx` |", 1)

block = """

## Twelfth review round (2026-10-23)

1. **S8 rebuilt** as two coherent blocks: group totals with usable and missing dates (15,510 /
   2,446 / 13,064; 472 / 83 / 389), then the composition of the analysable interval (83 optic-nerve,
   74 other ocular, 2,289 non-ocular). The old sheet used one column for both a cohort size and a
   subset size and put "83" where the column elsewhere read "yes".
2. **S10 and Methods 2.8** now agree: every analysed term had a Japanese equivalent, and nothing
   was excluded for mapping failure. Methods no longer promises a list of unmapped terms.
3. **References set as Sage Vancouver entries**: one paragraph each with a hanging indent, instead
   of one continuous block.
4. **READUS-PV table repeats its header row** on continuation pages.
5. **Word manuscript added** (`Ethambutol_TADS_manuscript.docx`): same text, four real tables, four
   figures at the end. The PDF remains the review copy; the figures for upload are the vector PDFs
   and 300-dpi PNGs in `figures/`.
"""
if "Twelfth review round" not in text:
    text = text.rstrip() + block
p.write_text(text, encoding="utf-8")
print("README updated")
