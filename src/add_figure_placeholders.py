# -*- coding: utf-8 -*-
"""Add the figure placeholder notes the journal requires.

Figures are created outside Word, so the manuscript carries a note at the point where each one is
first cited; the legends section keeps the full captions.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "tads" / "Ethambutol_TADS_manuscript.docx"

doc = Document(OUT)
placed = {1: False, 2: False, 3: False, 4: False}

for p in list(doc.paragraphs):
    text = p.text
    if text.strip().startswith("Figure ") and "." in text[:12]:
        continue  # legends section, not a citation
    for n in (1, 2, 3, 4):
        if placed[n] or f"Figure {n}" not in text:
            continue
        new_p = OxmlElement("w:p")
        p._p.addnext(new_p)
        para = Paragraph(new_p, p._parent)
        run = para.add_run(f"[Figure {n} near here]")
        run.italic = True
        placed[n] = True
        break

doc.save(OUT)
print("placeholders placed:", placed)
