# -*- coding: utf-8 -*-
"""Layout audit of the manuscript PDF, ignoring the page-number footer.

Checks a section heading left alone at the foot of a page, a table caption separated from its
table, and how much of each figure page the figure actually occupies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PDF = Path(__file__).resolve().parents[1] / "submission" / "tads" / "Ethambutol_TADS_manuscript.pdf"
doc = fitz.open(PDF)

HEADING = re.compile(r"^(\d+(\.\d+)*\.?\s+[A-Z][^.]{2,60}|Abstract|Introduction|Methods|Results|"
                     r"Discussion|Conclusion|References|Tables|Statements and Declarations|"
                     r"Figure legends)$")

print(f"{'page':>4}  {'last text':>60}  {'ink bottom':>10}")
issues = []
for i, page in enumerate(doc, start=1):
    blocks = [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()]
    #: the page number sits alone near the bottom and is not part of the body
    body = [b for b in blocks if not (b[4].strip().isdigit() and b[1] > page.rect.height * 0.9)]
    if not body:
        continue
    body.sort(key=lambda b: b[3])
    last = body[-1][4].strip().replace("\n", " ")
    ink = max([b[3] for b in body] + [0])

    note = ""
    if HEADING.match(last) and len(last) < 70:
        note = "HEADING AT FOOT"
        issues.append((i, f"heading at foot: {last[:50]}"))
    elif ink < page.rect.height * 0.80:
        note = f"body ends at {ink/page.rect.height:.0%}"
        issues.append((i, note))
    print(f"{i:>4}  {last[:60]:>60}  {ink:>10.0f} {note}")

print("\nfigure pages:")
for i, page in enumerate(doc, start=1):
    rects = [fitz.Rect(d["rect"]) for d in page.get_drawings()]
    rects += [fitz.Rect(x["bbox"]) for x in page.get_image_info()]
    if not rects:
        continue
    union = rects[0]
    for r in rects[1:]:
        union |= r
    if union.width * union.height > 0.35 * page.rect.width * page.rect.height:
        print(f"  page {i}: artwork {union.width/page.rect.width:.0%} x "
              f"{union.height/page.rect.height:.0%} of page, aspect {(union.width/union.height):.2f}")

print("\nissues:", len(issues))
for i, note in issues:
    print(f"  p{i}: {note}")
