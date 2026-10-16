# -*- coding: utf-8 -*-
"""
Count both table environments in the verifier, and explain why the count changed.

The assertion looked for "\\begin{table}" and expected twelve, which was correct while every
table used that environment.  Tables of five or more columns now use table*, the
double-column float the Frontiers class defines, so the plain count fell to eight and the
verifier failed - correctly, in the sense that it noticed a change, but against an
expectation that no longer describes the file.

The check is rewritten to count both forms and to keep asserting the total, so a table that
vanishes entirely is still caught.  The wide ones are also counted separately, because the
reason they are wide is a formatting decision worth keeping visible.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "verify_latex.py"
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"

src = TEX.read_text(encoding="utf-8")
n_plain = len(re.findall(r"\\begin\{table\}", src))
n_wide = len(re.findall(r"\\begin\{table\*\}", src))
print(f"  \\begin{{table}}  : {n_plain}")
print(f"  \\begin{{table*}} : {n_wide}")
print(f"  total            : {n_plain + n_wide}")

t = P.read_text(encoding="utf-8")

OLD = r'''for cmd, expect in (("\\citep{", 36), ("\\section{", 11), ("\\subsection{", 42),
                    ("\\section*{", 6), ("\\begin{table}", 12),
                    ("\\textbf{", 142), ("\\textit{", 43)):
    n = src.count(cmd)
    check(n == expect, f"{cmd:16s} appears {expect} times", f"found {n}")'''

NEW = ('''for cmd, expect in (("\\\\citep{", 36), ("\\\\section{", 11), ("\\\\subsection{", 42),
                    ("\\\\section*{", 6),
                    ("\\\\textbf{", 142), ("\\\\textit{", 43)):
    n = src.count(cmd)
    check(n == expect, f"{cmd:16s} appears {expect} times", f"found {n}")

# Tables of five or more columns use table*, the double-column float this class defines,
# because an ordinary table in a two-column layout is half the text width and a wide one is
# clipped rather than erroring.  Both environments are counted, so a table that disappears
# is still detected, and the wide ones are counted separately because their being wide is a
# formatting decision kept visible here.
n_table = len(re.findall(r"\\\\begin\\{table\\}", src))
n_table_wide = len(re.findall(r"\\\\begin\\{table\\*\\}", src))
check(n_table + n_table_wide == ''' + str(n_plain + n_wide) +
       ''', f"tables: {n_table} plain + {n_table_wide} wide "
      f"= {n_table + n_table_wide} (expected ''' + str(n_plain + n_wide) + ''')")
check(n_table_wide == ''' + str(n_wide) +
       ''', f"wide tables: {n_table_wide} (expected ''' + str(n_wide) + ''')")''')

if OLD in t:
    t = t.replace(OLD, NEW)
    P.write_text(t, encoding="utf-8")
    print("  assertion block replaced")
else:
    print("  the expected block was not found verbatim; showing the region instead")
    for i, ln in enumerate(t.splitlines(), 1):
        if "for cmd, expect in" in ln:
            for j in range(i - 1, min(i + 8, len(t.splitlines()))):
                print(f"    {j+1:5d}: {t.splitlines()[j]}")

print()
try:
    ast.parse(P.read_text(encoding="utf-8"))
    print("  syntax: OK")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")

print()
print("=" * 90)
print("Re-running the verifier")
print("=" * 90)
r = subprocess.run(["python", str(P)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in [l for l in out.splitlines() if l.strip()][-9:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}")
