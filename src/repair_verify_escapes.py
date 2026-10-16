# -*- coding: utf-8 -*-
"""
Repair the expected-count assertions, which the previous edit broke by dropping a backslash.

The tuple in verify_latex.py has to read

    for cmd, expect in (("\\\\citep{", 36), ("\\\\section{", 11), ...)

because each entry is a Python string literal holding a single backslash, written in the
source as two.  The previous script substituted using a replacement string in which the
backslash was consumed, so the file now holds ("\\section{", 11) - a literal backslash
followed by "section" - and the verifier warns about an invalid escape sequence and then
compares against a needle that never occurs.

The repair is done on the exact bytes, listing them first so the change can be checked
rather than trusted, and the file is re-parsed afterwards.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "verify_latex.py"

#: what each assertion should be, as the literal text to appear in the file.  Note the
#: doubled backslash: the file must contain a two-character sequence backslash-backslash.
WANT = [
    (r'("\\citep{", 36)', 36),
    (r'("\\section{", 11)', 11),
    (r'("\\subsection{", 42)', 42),
    (r'("\\section*{", 6)', 6),
    (r'("\\begin{table}", 12)', 12),
    (r'("\\textbf{", 142)', 142),
    (r'("\\textit{", 43)', 43),
]
#: the single-backslash form the broken edit produced
BROKEN = [
    ('("\\citep{", 36)', r'("\\citep{", 36)'),
    ('("\\section{", 11)', r'("\\section{", 11)'),
    ('("\\subsection{", 42)', r'("\\subsection{", 42)'),
    ('("\\section*{", 6)', r'("\\section*{", 6)'),
    ('("\\begin{table}", 12)', r'("\\begin{table}", 12)'),
    ('("\\textbf{", 142)', r'("\\textbf{", 142)'),
    ('("\\textit{", 43)', r'("\\textit{", 43)'),
]

t = P.read_text(encoding="utf-8")

print("=" * 90)
print("1. The assertion line as it now stands")
print("=" * 90)
for i, ln in enumerate(t.splitlines(), 1):
    if "for cmd, expect in" in ln or ("citep" in ln and "36" in ln):
        print(f"  {i:5d}: {ln}")

print()
print("=" * 90)
print("2. Repairing")
print("=" * 90)
fixed = 0
for broken, want in BROKEN:
    if broken in t:
        t = t.replace(broken, want)
        fixed += 1
        print(f"  repaired {broken!r}")
    elif want in t:
        print(f"  already correct {want!r}")
    else:
        print(f"  not found: {broken!r}")
P.write_text(t, encoding="utf-8")

print()
print("=" * 90)
print("3. The assertion line after repair")
print("=" * 90)
for i, ln in enumerate(P.read_text(encoding="utf-8").splitlines(), 1):
    if "for cmd, expect in" in ln or ("citep" in ln and "36" in ln):
        print(f"  {i:5d}: {ln}")

print()
print("=" * 90)
print("4. Parsing and re-running")
print("=" * 90)
try:
    ast.parse(P.read_text(encoding="utf-8"))
    print("  syntax: OK")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")

r = subprocess.run(["python", str(P)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in [l for l in out.splitlines() if l.strip()][-10:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}   repaired {fixed} assertion(s)")
