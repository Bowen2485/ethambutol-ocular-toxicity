# -*- coding: utf-8 -*-
"""Build a Word version of the manuscript for submission.

Three faults in the first version are fixed here: the nineteen references were joined into one
4,400-character paragraph, backticks around field names (`CASEID`, `drugname`) were printed
literally, and the title was not styled differently from body text.
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

CODE_FONT = "Consolas"


def add_runs(par, text: str) -> None:
    """Emit **bold**, *italic* and `code` spans as runs."""
    for chunk in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            par.add_run(chunk[2:-2]).bold = True
        elif chunk.startswith("`") and chunk.endswith("`"):
            run = par.add_run(chunk[1:-1])
            run.font.name = CODE_FONT
            run.font.size = Pt(9.5)
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            par.add_run(chunk[1:-1]).italic = True
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
first_heading = True
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

    #: reference entries arrive as consecutive lines; joined they run together, so each one gets
    #: its own paragraph with a hanging indent (Sage Vancouver)
    if len(para) > 1 and all(re.match(r"^\d{1,2}\.\s", x) for x in para):
        for entry in para:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.7)
            p.paragraph_format.first_line_indent = Cm(-0.7)
            p.paragraph_format.space_after = Pt(4)
            add_runs(p, entry)
        continue

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_runs(p, " ".join(para))

legend_text = {}
_md = SRC.read_text(encoding="utf-8")
for _m in re.finditer(r"\*\*(Figure (\d+)\.)\*\*\s*(.+?)(?=\n\*\*Figure|\n## |\Z)", _md, re.S):
    legend_text[int(_m.group(2))] = " ".join(_m.group(3).split())

doc.add_page_break()
for n, name in enumerate(sorted(FIG.glob("*.png")), start=1):
    doc.add_picture(str(name), width=Cm(15.5))
    head = doc.add_paragraph()
    head.add_run(f"Figure {n}. ").bold = True
    head.add_run(legend_text.get(n, ""))
    doc.add_paragraph()

doc.save(OUT)
print(f"written {OUT.relative_to(ROOT)}")
print(f"  paragraphs: {len(doc.paragraphs)}, tables: {len(doc.tables)}")
