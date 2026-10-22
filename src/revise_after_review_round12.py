# -*- coding: utf-8 -*-
"""Twelfth round.

    1. S8 becomes two coherent blocks: group totals with usable/missing dates, then the
       composition of the analysable interval.  The old sheet mixed "n" as a cohort size and as a
       subset size in the same column, and put "83" in a column that elsewhere held "yes".
    2. Methods 2.8 no longer claims the supplement lists unmapped terms: every analysed term had a
       Japanese equivalent, and S10 says so.
    3. references are set one per paragraph with a hanging indent instead of running together.
    4. the READUS-PV table repeats its header row across pages.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"


def edit_joined(path: Path, marker: str, pairs: list[tuple[str, str]]) -> None:
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    hits = [i for i, b in enumerate(blocks) if marker in b]
    assert len(hits) == 1, f"{path.name}: marker matched {len(hits)} blocks"
    joined = " ".join(blocks[hits[0]].split())
    for old, new in pairs:
        assert old in joined, f"{path.name}: not found {old[:60]!r}"
        joined = joined.replace(old, new, 1)
    blocks[hits[0]] = joined
    path.write_text("\n\n".join(blocks), encoding="utf-8")


# ------------------------------------------------------------------- methods
edit_joined(MAN / "TADS_methods.md", "the mapping is published in the supplement", [
    ("the mapping is published in the supplement, together with the terms that could not be "
     "mapped.",
     "the mapping is published in the supplement. Every analysed term had a Japanese equivalent, "
     "so no term was excluded for mapping failure."),
])
print("methods 2.8: mapping sentence corrected")

# ---------------------------------------------------------------------- S8
p = ROOT / "src" / "build_supplement_v2.py"
s = p.read_text(encoding="utf-8")
start = s.index("s8 = pd.DataFrame([")
end = s.index("# ------------------------------------------------------- S9")
new_s8 = '''s8 = pd.DataFrame([
    {"Group": "All ethambutol cases", "Total cases": n_cases,
     "Cases with a usable interval": int(tto.iloc[0].n),
     "Cases with missing or unusable dates": n_cases - int(tto.iloc[0].n)},
    {"Group": "Cases carrying at least one of the 17 optic-nerve terms", "Total cases": int(prof.any_optic.sum()),
     "Cases with a usable interval": int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0]),
     "Cases with missing or unusable dates": int(prof.any_optic.sum())
                                                - int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0])},
    {"Group": "", "Total cases": "", "Cases with a usable interval": "", "Cases with missing or unusable dates": ""},
    {"Group": "Composition of the 2,446 cases with a usable interval",
     "Total cases": "", "Cases with a usable interval": "", "Cases with missing or unusable dates": ""},
    {"Group": "  optic-nerve event", "Total cases": "",
     "Cases with a usable interval": int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0]),
     "Cases with missing or unusable dates": ""},
    {"Group": "  other ocular event", "Total cases": "",
     "Cases with a usable interval": int(tto[tto.group.str.startswith("Ocular event")].n.iloc[0])
                                        - int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0]),
     "Cases with missing or unusable dates": ""},
    {"Group": "  non-ocular event", "Total cases": "",
     "Cases with a usable interval": int(tto[tto.group.str.startswith("No ocular")].n.iloc[0]),
     "Cases with missing or unusable dates": ""},
])

'''
s = s[:start] + new_s8 + s[end:]

#: S10 gains an explicit statement that nothing was left unmapped
old = ('s10 = pd.DataFrame(map_rows)')
new = ('map_rows.append({"English preferred term": "(no analysed term failed to map)",\n'
       '                     "Japanese MedDRA/J term": "", "Mapped": "not applicable",\n'
       '                     "Note": "every analysed term had a Japanese equivalent, so no term was "\n'
       '                             "excluded for mapping failure"})\n'
       's10 = pd.DataFrame(map_rows)')
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("S8 restructured; S10 note added")

# ------------------------------------------------------- references, per entry
p = ROOT / "src" / "build_tads_pdf.py"
s = p.read_text(encoding="utf-8")
old = "    joined = \" \".join(para)\n"
new = ("    #: reference lines arrive as one block without blank lines; emitted as a single\n"
       "    #: paragraph they run together, so each entry gets its own hanging-indent paragraph\n"
       "    if ref_group_open and re.match(r\"^\\d{1,2}\\.\\s\", para[0]):\n"
       "        for line in para:\n"
       "            body_lines.append(r\"\\par\\noindent\\hangindent=1.35em\\hangafter=1 \"\n"
       "                              + inline(line) + r\"\\par\")\n"
       "        continue\n"
       "    joined = \" \".join(para)\n")
assert old in s, "paragraph join not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("references: hanging indent per entry")

# ------------------------------------------------ checklist table header repeats
p = ROOT / "src" / "build_readus_docx.py"
s = p.read_text(encoding="utf-8")
old = 'widths = [Pt(24), Pt(150), Pt(80), Pt(210)]'
new = ('''#: the checklist runs over several pages; without a repeating header row the continuation
#: pages start mid-table with no column names
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

hdr_row = table.rows[0]
trPr = hdr_row._tr.get_or_add_trPr()
tblHeader = OxmlElement("w:tblHeader")
tblHeader.set(qn("w:val"), "true")
trPr.append(tblHeader)
can_split = OxmlElement("w:cantSplit")
trPr.append(can_split)

widths = [Pt(24), Pt(150), Pt(80), Pt(210)]''')
assert old in s, "widths line not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("checklist: header row repeats")
