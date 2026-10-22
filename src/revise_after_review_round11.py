# -*- coding: utf-8 -*-
"""Eleventh round: reference order, Table 2 footnote, and reference-list spacing.

    Cheng et al. (GSE294687) is first cited in Methods 2.10, Li et al. (ferroptosis) only in
    Discussion 4.4, so the list has to put Cheng at 18 and Li at 19.

    The Table 2 footnote said the narrow-term counts were in S1, but S1 holds the 9 optic-nerve
    terms with >=3 cases and the 6 controls, not the 45-term query list.  The sentence now says
    what S1 actually contains.

    The reference list is set tighter so its last lines do not occupy a page of their own.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

# ------------------------------------------------------- swap references 18/19
refs_path = MAN / "TADS_references.md"
lines = refs_path.read_text(encoding="utf-8").rstrip().splitlines()
by_num = {}
for ln in lines:
    m = re.match(r"^(\d{1,2})\.\s+(.*)$", ln)
    assert m, f"unparsed reference line: {ln[:40]}"
    by_num[int(m.group(1))] = m.group(2)
assert "Li Q" in by_num[18] and "Cheng HC" in by_num[19], (by_num[18][:40], by_num[19][:40])
by_num[18], by_num[19] = by_num[19], by_num[18]
refs_path.write_text("\n".join(f"{n}. {by_num[n]}" for n in sorted(by_num)) + "\n", encoding="utf-8")
print("references 18 and 19 swapped")

# ------------------------------------------------------------- in-text markers
swapped = 0
for name in ("TADS_EN.md", "TADS_methods.md", "TADS_results.md", "TADS_discussion.md"):
    p = MAN / name
    text = p.read_text(encoding="utf-8")
    if "[18]" not in text and "[19]" not in text:
        continue
    text = text.replace("[18]", "[@TMP@]").replace("[19]", "[18]").replace("[@TMP@]", "[19]")
    p.write_text(text, encoding="utf-8")
    swapped += 1
    print(f"  {name}: citations swapped")

# ------------------------------------------------------ Table 2 footnote (builder)
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = '    "count was below 5; the narrow-term counts are in Supplementary Table S1. q, "'
new = ('    "count was below 5. Term-level estimates for the nine optic-nerve preferred terms with at "\n'
       '    "least three exposed cases and the six pre-specified controls are in Supplementary Table "\n'
       '    "S1. q, "')
assert old in s, "table 2 note not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("table 2 footnote corrected")

# ---------------------------------------------------- reference list set tighter
p = ROOT / "src" / "build_tads_pdf.py"
s = p.read_text(encoding="utf-8")
old = '''    if s.startswith("## "):
        body_lines.append(r"\\section*{" + inline(s[3:]) + "}")
        i += 1
        continue'''
new = '''    if s.startswith("## "):
        #: the reference list runs to the last page by a few lines; a smaller size and tighter
        #: paragraph spacing keep it from spilling onto a page of its own
        if s[3:].strip().lower().startswith("references"):
            body_lines.append(r"\\begingroup\\small\\setlength{\\parskip}{2pt}")
        elif s[3:].strip().lower().startswith("tables"):
            body_lines.append(r"\\endgroup")
        body_lines.append(r"\\section*{" + inline(s[3:]) + "}")
        i += 1
        continue'''
assert old in s, "heading branch not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("reference list wrapped in a smaller, tighter group")
