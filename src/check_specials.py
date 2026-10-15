# -*- coding: utf-8 -*-
"""
Distinguish escaped specials from bare ones, and check the abstract's structure.

Two failures need separating, and they are different in kind.

    The special characters.  If a percent sign is genuinely bare, LaTeX discards the rest
    of its line, which would silently truncate the manuscript - so this matters.  The
    earlier check could not tell an escaped "\\%" from a bare one, because its regex for
    stripping commands did not allow for the one-character escapes.  This counts the two
    forms separately and shows any that are genuinely bare.

    The abstract.  The generator adds a Conclusion section only if the source abstract has
    one, so the check may be asserting a structure the manuscript does not use.  The
    section labels actually present are read from the source rather than assumed.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"
SRC = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"

tex = TEX.read_text(encoding="utf-8")
md = SRC.read_text(encoding="utf-8")

print("=" * 92)
print("1. Escaped versus bare specials")
print("=" * 92)
print(f"  {'char':6s} {'escaped':>9s} {'bare':>9s}   note")
notes = {"%": "a bare one truncates the rest of the line",
         "&": "a bare one breaks alignment outside a table",
         "_": "a bare one is a maths subscript outside maths",
         "#": "a bare one is a macro parameter"}
for ch in ("%", "&", "_", "#"):
    escaped = len(re.findall(re.escape("\\" + ch), tex))
    # a bare special is one not preceded by a backslash; the backslash itself may be
    # escaped, so a simple negative lookbehind is enough here
    bare_positions = [m.start() for m in re.finditer(re.escape(ch), tex)
                      if m.start() == 0 or tex[m.start() - 1] != "\\"]
    print(f"  {ch:6s} {escaped:>9d} {len(bare_positions):>9d}   {notes[ch]}")
    if bare_positions and ch in "%&_":
        print(f"         first few bare positions: {bare_positions[:5]}")
        for p in bare_positions[:3]:
            lo = max(0, p - 60)
            print(f"           ...{tex[lo:p + 40]!r}")

print()
print("=" * 92)
print("2. Where the bare ones sit")
print("=" * 92)
# inside a tabular the & is the column separator and is correct
table_spans = [(m.start(), m.end()) for m in re.finditer(r"\\begin\{tabular\}.*?\\end\{tabular\}",
                                                         tex, re.S)]
math_spans = [(m.start(), m.end()) for m in re.finditer(r"\$[^$]*\$", tex)]
cmd_spans = [(m.start(), m.end()) for m in re.finditer(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?",
                                                       tex)]


def inside(pos: int, spans) -> bool:
    return any(a <= pos < b for a, b in spans)


tally = {"in tabular": 0, "in maths": 0, "in a command": 0, "GENUINELY BARE": 0}
examples = []
for ch in ("%", "&", "_"):
    for m in re.finditer(re.escape(ch), tex):
        p = m.start()
        if p > 0 and tex[p - 1] == "\\":
            continue
        if inside(p, table_spans):
            tally["in tabular"] += 1
        elif inside(p, math_spans):
            tally["in maths"] += 1
        elif inside(p, cmd_spans):
            tally["in a command"] += 1
        else:
            tally["GENUINELY BARE"] += 1
            if len(examples) < 6:
                lo = max(0, p - 70)
                examples.append(f"{ch!r} at {p}: ...{tex[lo:p + 30]!r}")
for k, v in tally.items():
    print(f"  {k:20s} {v:>6d}")
for e in examples:
    print(f"      {e}")

print()
print("=" * 92)
print("3. The abstract's section labels, as they are in the source")
print("=" * 92)
abs_src_start = md.find("## Abstract")
abs_src_end = md.find("**Keywords", abs_src_start)
for m in re.finditer(r"^\*\*(.+?)\.\*\*", md[abs_src_start:abs_src_end], re.M):
    print(f"  source label: {m.group(1)}")
abs_block = tex[tex.find(r"\begin{abstract}"):tex.find(r"\end{abstract}")]
print()
for m in re.finditer(r"\\section\{([^}]*)\}", abs_block):
    print(f"  rendered label: {m.group(1)}")
print()
print("  Frontiers asks for Background, Methods, Results and Conclusion where the")
print("  article type requires a structured abstract.  Whether a Conclusion label is")
print("  present in the source is a matter for the manuscript, not for the converter.")
