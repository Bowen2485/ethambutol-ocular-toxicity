# -*- coding: utf-8 -*-
"""
Find the non-ASCII characters in the generated LaTeX and say which will compile.

The Frontiers class declares \\documentclass[utf8]{...}, but no TeX distribution is
installed here, so whether the class loads inputenc and whether its fonts carry the
needed glyphs cannot be tested by compiling.  What can be established is exactly which
characters are present, which of them are safe under pdflatex with the OT1 font encoding,
and which have to be written as a command instead.

pdflatex cannot typeset arbitrary Unicode.  Accented Latin letters, the Scandinavian
letters and a few typographic marks are provided by inputenc, but symbols such as the
angstrom sign, the micro sign and the relational operators are not: they need \\AA,
\\textmu, $\\geq$ and so on.  Leaving them in place produces either a missing-glyph
warning and a blank in the PDF, or an outright error.
"""
from __future__ import annotations

import collections
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"
src = TEX.read_text(encoding="utf-8")

#: characters pdflatex handles with inputenc, and the command to use if it does not
REPLACEMENTS = {
    "\u00c5": r"\AA{}",           # angstrom sign
    "\u00e5": r"\aa{}",
    "\u00b5": r"\textmu{}",       # micro sign
    "\u03bc": r"$\mu$",           # greek small mu
    "\u2265": r"$\geq$",
    "\u2264": r"$\leq$",
    "\u2248": r"$\approx$",
    "\u00b1": r"$\pm$",
    "\u00d7": r"$\times$",
    "\u00f7": r"$\div$",
    "\u2192": r"$\rightarrow$",
    "\u2190": r"$\leftarrow$",
    "\u2212": r"$-$",             # minus sign
    "\u2013": "--",               # en dash
    "\u2014": "---",              # em dash
    "\u2018": "`", "\u2019": "'",
    "\u201c": "``", "\u201d": "''",
    "\u2026": r"\ldots{}",
    "\u00a0": "~",
}

#: characters inputenc handles directly, so they may stay
SAFE = set("áàâäãåéèêëíìîïóòôöõúùûüýÿñçÁÀÂÄÃÅÉÈÊËÍÌÎÏÓÒÔÖÕÚÙÛÜÝÑÇ"
           "øØæÆœŒßšŠžŽłŁđĐ")

nonascii = collections.Counter(ch for ch in src if ord(ch) > 127)
print("=" * 92)
print("1. Non-ASCII characters present")
print("=" * 92)
print(f"  distinct characters: {len(nonascii)}   total occurrences: {sum(nonascii.values())}")
print()
print(f"  {'char':8s} {'code':8s} {'count':>6s}  {'name':38s} disposition")
to_replace: list[str] = []
for ch, n in nonascii.most_common():
    cp = f"U+{ord(ch):04X}"
    try:
        name = unicodedata.name(ch)
    except ValueError:
        name = "?"
    if ch in REPLACEMENTS:
        disp = f"REPLACE with {REPLACEMENTS[ch]}"
        to_replace.append(ch)
    elif ch in SAFE:
        disp = "safe with inputenc"
    elif ch.isalpha():
        disp = "accented letter, likely safe"
    else:
        disp = "REVIEW"
        to_replace.append(ch)
    print(f"  {ch!r:8s} {cp:8s} {n:>6d}  {name[:38]:38s} {disp}")

print()
print("=" * 92)
print("2. What the manuscript uses in place of symbols")
print("=" * 92)
for cmd, meaning in ((r"$\geq$", "greater-or-equal"), (r"$\leq$", "less-or-equal"),
                     (r"$\mu$", "micro"), (r"\AA{}", "angstrom")):
    print(f"  {cmd:12s} {src.count(cmd):>5d}   {meaning}")

print()
print("=" * 92)
print("3. Decision")
print("=" * 92)
if to_replace:
    print(f"  {len(set(to_replace))} character(s) should be written as a command:")
    for ch in sorted(set(to_replace)):
        print(f"      {ch!r} ({unicodedata.name(ch, '?')})  ->  {REPLACEMENTS.get(ch, '?')}")
else:
    print("  every non-ASCII character present is safe with inputenc.")
