# -*- coding: utf-8 -*-
"""
Find why 70 bold markers survived the markdown-to-LaTeX conversion.

The verifier reported them and they are real: the generated .tex contains ** where \textbf
belongs.  LaTeX will render them literally, so the submitted PDF would show asterisks in the
middle of sentences.

The converter is not failing generally - it produced 151 \textbf commands - so the question is
what distinguishes the runs it missed.  Each surviving pair is printed with the line of the
markdown source it came from, so the pattern can be seen rather than guessed at.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"
EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"

src = TEX.read_text(encoding="utf-8")
md = EN.read_text(encoding="utf-8").splitlines()

print("=" * 96)
print("1. Where the surviving markers are, and whether they straddle a line break")
print("=" * 96)
straddle = 0
inline = 0
samples = []
for m in re.finditer(r"\*\*", src):
    #: the text between this marker and the next one, if any
    nxt = src.find("**", m.end())
    seg = src[m.end():nxt] if nxt > 0 else ""
    crosses = "\n" in seg
    if crosses:
        straddle += 1
    else:
        inline += 1
    if len(samples) < 14:
        samples.append((m.start(), crosses, seg[:80].replace("\n", " / ")))
print(f"  markers whose pair straddles a line break: {straddle}")
print(f"  markers closed on the same line           : {inline}")
print()
for pos, crosses, seg in samples:
    tag = "STRADDLES" if crosses else "same line"
    print(f"  {tag:10s} {seg!r}")

print()
print("=" * 96)
print("2. Lines in the markdown whose bold did not convert")
print("=" * 96)
#: collect every markdown line that contains bold, then see which of its text reached the
#: LaTeX still wrapped in asterisks
missed = []
for i, ln in enumerate(md, 1):
    if "**" not in ln:
        continue
    #: the plain text inside the first bold run on this line
    m = re.search(r"\*\*(.+?)\*\*", ln)
    if not m:
        continue
    inner = m.group(1).strip()
    if len(inner) < 12:
        continue
    probe = inner[:40]
    #: is that text present in the LaTeX, and is a ** adjacent to it
    j = src.find(probe)
    if j < 0:
        continue
    window = src[max(0, j - 6):j + len(probe) + 6]
    if "**" in window:
        missed.append((i, inner[:70], window.replace("\n", " / ")[:110]))

print(f"  markdown lines whose bold survived as asterisks: {len(missed)}")
print()
for ln_no, inner, window in missed[:20]:
    print(f"  md line {ln_no}")
    print(f"      inner   : {inner!r}")
    print(f"      in tex  : {window!r}")

print()
print("=" * 96)
print("3. What the converter does with bold")
print("=" * 96)
conv = ROOT / "src" / "build_latex.py"
ct = conv.read_text(encoding="utf-8")
for i, ln in enumerate(ct.splitlines(), 1):
    if "textbf" in ln or ("**" in ln and "sub" in ln):
        print(f"  {i:5d}: {ln[:118]}")
