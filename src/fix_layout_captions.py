# -*- coding: utf-8 -*-
"""Fix two layout faults found by the audit.

    1. page 21 held only the last line of reference 19, leaving a page that was 20% full
    2. the figure pages carried no caption, so a reader arriving at a figure had to find the
       legends section to know what it was

Both builders get the captions: the PDF figure floats and the Word file each print the legend
under the image, and the reference block is set slightly tighter so it ends on page 20.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------- PDF: references
p = ROOT / "src" / "build_tads_pdf.py"
s = p.read_text(encoding="utf-8")
old = 'body_lines.append(r"\\begingroup\\small\\setlength{\\parskip}{2pt}")'
new = ('body_lines.append(r"\\begingroup\\small\\setlength{\\parskip}{1pt}"\n'
       '                              r"\\linespread{0.94}\\selectfont")')
assert old in s, "reference group not found"
s = s.replace(old, new, 1)

# ---------------------------------------------------------------- PDF: captions
old = '''fig_block = []
for key, stem in FIG_FILES.items():
    path = FIG / f"{stem}.pdf"
    if not path.exists():
        print(f"  missing figure {path}")
        continue
    fig_block.append(r"\\begin{figure}[p]")
    fig_block.append(r"\\centering")
    fig_block.append(r"\\includegraphics[width=\\linewidth]{" + str(path.as_posix()) + "}")
    fig_block.append(r"\\end{figure}")'''
new = '''legend_text = {}
_man = (ROOT / "manuscript" / "TADS_manuscript.md").read_text(encoding="utf-8")
for _m in re.finditer(r"\\*\\*(Figure (\\d+)\\.)\\*\\*\\s*(.+?)(?=\\n\\*\\*Figure|\\n## |\\Z)", _man, re.S):
    legend_text[int(_m.group(2))] = (" ".join(_m.group(3).split()))

fig_block = []
for key, stem in FIG_FILES.items():
    path = FIG / f"{stem}.pdf"
    if not path.exists():
        print(f"  missing figure {path}")
        continue
    n = int(re.sub(r"[^0-9]", "", key) or 0)
    caption = legend_text.get(n, "")
    fig_block.append(r"\\begin{figure}[p]")
    fig_block.append(r"\\centering")
    fig_block.append(r"\\includegraphics[width=0.94\\linewidth]{" + str(path.as_posix()) + "}")
    if caption:
        fig_block.append(r"\\par\\vspace{8pt}")
        fig_block.append(r"\\begin{minipage}{0.90\\linewidth}\\footnotesize\\raggedright")
        fig_block.append(r"\\textbf{Figure " + str(n) + ".} " + caption)
        fig_block.append(r"\\end{minipage}")
    fig_block.append(r"\\end{figure}")'''
assert old in s, "figure block not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("PDF: references tightened, figure captions added")

# --------------------------------------------------------------- Word: captions
p = ROOT / "src" / "build_manuscript_docx.py"
s = p.read_text(encoding="utf-8")
old = '''doc.add_page_break()
for n, name in enumerate(sorted(FIG.glob("*.png")), start=1):
    doc.add_paragraph().add_run(f"Figure {n}").bold = True
    doc.add_picture(str(name), width=Cm(15.5))
    doc.add_paragraph()'''
new = '''legend_text = {}
_md = SRC.read_text(encoding="utf-8")
for _m in re.finditer(r"\\*\\*(Figure (\\d+)\\.)\\*\\*\\s*(.+?)(?=\\n\\*\\*Figure|\\n## |\\Z)", _md, re.S):
    legend_text[int(_m.group(2))] = " ".join(_m.group(3).split())

doc.add_page_break()
for n, name in enumerate(sorted(FIG.glob("*.png")), start=1):
    doc.add_picture(str(name), width=Cm(15.5))
    head = doc.add_paragraph()
    head.add_run(f"Figure {n}. ").bold = True
    head.add_run(legend_text.get(n, ""))
    doc.add_paragraph()'''
assert old in s, "word figure block not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("Word: figure captions added")
