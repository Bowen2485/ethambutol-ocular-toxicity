# -*- coding: utf-8 -*-
"""
Repair the table-count lines in verify_latex.py by building them from character codes only.

Why this has failed repeatedly
    The lines that must appear in verify_latex.py contain a backslash inside a Python string
    literal:

        n_table = src.count('\\begin{table}')

    as it must be read in the file's own source.  Every route to writing that text - a string
    literal in this script, a replacement passed through re.sub, a shell here-string - consumes
    the backslash at least once, so the file has ended up holding a slightly different string
    each time and the count has silently been zero.  The debug print proved the file was being
    read correctly (136,194 characters, and the same expression computed by hand gives 9), so
    the fault has always been in what got written, not in what is measured.

The approach now
    This script is a file, not an inline command, so there is no shell layer.  Inside it, no
    backslash appears in any literal: the character is obtained with chr(92), the braces with
    chr(123) and chr(125), and the quotes with chr(39).  The written lines therefore cannot be
    altered in transit.  The result is then read back and executed to confirm it computes the
    right numbers before the verifier is trusted.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "src" / "verify_latex.py"
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"

BS = chr(92)
Q = chr(39)          # single quote
LBR = chr(123)       # {
RBR = chr(125)       # }
STAR = chr(42)       # *

#: the literal LaTeX opening this counts
PLAIN = BS + "begin" + LBR + "table" + RBR
WIDE = BS + "begin" + LBR + "table" + STAR + RBR

#: how a str.count call for that literal is written in the target file.  The literal is
#: expressed with chr() so no escape can be lost between here and there.
def count_line(var: str, text: str) -> str:
    parts = []
    for ch in text:
        if ch == BS:
            parts.append("chr(92)")
        elif ch == LBR:
            parts.append("chr(123)")
        elif ch == RBR:
            parts.append("chr(125)")
        elif ch == STAR:
            parts.append("chr(42)")
        else:
            parts.append(Q + ch + Q)
    return var + " = src.count(" + " + ".join(parts) + ")" + chr(10)


src_tex = TEX.read_text(encoding="utf-8")
n_plain = src_tex.count(PLAIN)
n_wide = src_tex.count(WIDE)
print(f"  expected plain {n_plain}, wide {n_wide}")

lines = V.read_text(encoding="utf-8").splitlines(keepends=True)
out, replaced, dropped = [], [], 0
for ln in lines:
    if ln.startswith("n_table = "):
        out.append(count_line("n_table", PLAIN))
        replaced.append("n_table")
    elif ln.startswith("n_table_wide = "):
        out.append(count_line("n_table_wide", WIDE))
        replaced.append("n_table_wide")
    elif ln.lstrip().startswith("print(f\"  DEBUG"):
        dropped += 1                      # remove the diagnostic added while debugging
    else:
        out.append(ln)

V.write_text("".join(out), encoding="utf-8")
print(f"  replaced: {replaced}   removed debug lines: {dropped}")

print()
print("=" * 90)
print("Lines as they now stand")
print("=" * 90)
for i, ln in enumerate(V.read_text(encoding="utf-8").splitlines(), 1):
    if "n_table" in ln:
        print(f"  {i:4d}: {ln}")

print()
print("=" * 90)
print("Executing those two lines to confirm the numbers")
print("=" * 90)
ns = {"src": src_tex}
for i, ln in enumerate(V.read_text(encoding="utf-8").splitlines(), 1):
    if ln.startswith(("n_table = ", "n_table_wide = ")):
        exec(ln, ns)                                       # noqa: S102
print(f"  n_table      = {ns.get('n_table')}   (file has {n_plain})")
print(f"  n_table_wide = {ns.get('n_table_wide')}   (file has {n_wide})")
ok = ns.get("n_table") == n_plain and ns.get("n_table_wide") == n_wide
print(f"  counts correct: {ok}")

print()
print("=" * 90)
print("Verifier")
print("=" * 90)
r = subprocess.run(["python", str(V)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
o = (r.stdout or "") + (r.stderr or "")
for line in [l for l in o.splitlines() if l.strip()][-7:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}")
