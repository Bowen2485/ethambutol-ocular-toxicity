# -*- coding: utf-8 -*-
"""Build a Word version of the manuscript for submission.

The PDF is for review; the journals that require a Word manuscript want the same text in .docx
with real tables.  This converts the assembled Markdown: headings, paragraphs with **bold** runs,
pipe tables as Word tables, and the four figures appended after the legends at 300 dpi.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "manuscript" / "TADS_manuscript.md"
FIG = ROOT / "results" / "tads_figures"
OUT = ROOT / "submission" / "tads" / "Ethambutol_TADS_manuscript.docx"

doc = Document()
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for section in doc.sections:
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)


def add_runs(par, text: str) -> None:
    """Emit **bold** and *italic* spans as runs."""
    for chunk in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            run = par.add_run(chunk[2:-2])
            run.bold = True
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            run = par.add_run(chunk[1:-1])
            run.italic = True
        else:
            par.add_run(chunk)


def add_table(rows: list[list[str]]) -> None:
    ncol = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=ncol)
    table.style = "Table Grid"
    table.autofit = True
    for i, row in enumerate(rows):
        cells = table.add_row().cells
        for j in range(ncol):
            text = row[j] if j < len(row) else ""
            cells[j].text = ""
            par = cells[j].paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            add_runs(par, text)
            for run in par.runs:
                run.font.size = Pt(8.5)
                if i == 0:
                    run.bold = True
    doc.add_paragraph()


lines = SRC.read_text(encoding="utf-8").splitlines()
i = 0
while i < len(lines):
    s = lines[i].strip()
    if not s:
        i += 1
        continue
    if s.startswith("# "):
        h = doc.add_heading(level=1)
        add_runs(h, s[2:])
        i += 1
        continue
    if s.startswith("## "):
        h = doc.add_heading(level=2)
        add_runs(h, s[3:])
        i += 1
        continue
    if s.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                rows.append(cells)
            i += 1
        add_table(rows)
        continue
    para = [s]
    i += 1
    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("#", "|")):
        para.append(lines[i].strip())
        i += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_runs(p, " ".join(para))

# ------------------------------------------------------------------- figures
doc.add_page_break()
for n, name in enumerate(sorted(FIG.glob("*.png")), start=1):
    doc.add_paragraph().add_run(f"Figure {n}").bold = True
    doc.add_picture(str(name), width=Cm(15.5))
    doc.add_paragraph()

doc.save(OUT)
print(f"written {OUT.relative_to(ROOT)}")
print(f"  paragraphs: {len(doc.paragraphs)}, tables: {len(doc.tables)}")
