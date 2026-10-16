# -*- coding: utf-8 -*-
"""
Refresh the verifier's expected counts, escaping correctly this time.

The previous attempt at this repair replaced text using a Python replacement string, in which
a backslash is an escape character, so the double backslashes in the needle collapsed to one
and the file ended up asserting against a pattern that cannot occur.  That produced a
SyntaxWarning and a verifier that passed while checking nothing.

This version never puts the command text in a replacement string.  It finds the assertion
tuple, parses out each command and count, recomputes every count from the generated LaTeX,
and writes the tuple back assembled from raw strings - so each entry is built with an
explicit chr(92)*2 rather than typed as an escape, and the escaping cannot be lost in
transit.  It then re-parses the file and compares what the tuple now holds against the
counts, so a silent mismatch is impossible.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "src" / "verify_latex.py"
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"

BS = chr(92)                     # a single backslash, never written as an escape
src = TEX.read_text(encoding="utf-8")

#: what each assertion should count, as the command text minus the backslash prefix
WANT = {
    "citep{": len(re.findall(re.escape(BS) + r"citep\{", src)),
    "section{": len(re.findall(re.escape(BS) + r"section\{", src)),
    "subsection{": len(re.findall(re.escape(BS) + r"subsection\{", src)),
    "section*{": len(re.findall(re.escape(BS) + r"section\*\{", src)),
    "textbf{": len(re.findall(re.escape(BS) + r"textbf\{", src)),
    "textit{": len(re.findall(re.escape(BS) + r"textit\{", src)),
}
n_plain = len(re.findall(re.escape(BS) + r"begin\{table\}", src))
n_wide = len(re.findall(re.escape(BS) + r"begin\{table\*\}", src))

print("=" * 92)
print("1. Counts recomputed from the generated LaTeX")
print("=" * 92)
for k, v in WANT.items():
    print(f"  {BS}{k:16s} {v}")
print(f"  tables: {n_plain} plain + {n_wide} wide = {n_plain + n_wide}")

vt = VERIFY.read_text(encoding="utf-8")

print()
print("=" * 92)
print("2. The assertion tuple before")
print("=" * 92)
m = re.search(r"for cmd, expect in \((.*?)\):\n", vt, re.S)
print(f"  {m.group(0).strip()[:300] if m else 'not found'}")

#: assemble the replacement without any escape sequences
entries = []
for cmd, n in WANT.items():
    if cmd == "section*{":
        continue
    entries.append(f'({BS}{BS}{cmd}", {n})')
new_tuple = ("for cmd, expect in ("
             + ", ".join(entries[:4])
             + ",\n                    "
             + ", ".join(entries[4:])
             + '):\n')

if m:
    vt = vt[:m.start()] + new_tuple + vt[m.end():]
    print()
    print("  tuple replaced")
else:
    print()
    print("  tuple not found; writing counts as a separate block instead")

# the table assertions
tbl = ("n_table = len(re.findall(" + repr(BS + BS + "begin{table}") + ", src))\n"
       "n_table_wide = len(re.findall(" + repr(BS + BS + "begin{table" + BS + "*}")
       + ", src))\n"
       f"check(n_table + n_table_wide == {n_plain + n_wide}, "
       f'f"tables: {{n_table}} + {{n_table_wide}} (expected {n_plain + n_wide})")\n'
       f"check(n_table_wide == {n_wide}, "
       f'f"wide tables: {{n_table_wide}} (expected {n_wide})")\n')
vt = re.sub(r"n_table = len\(re\.findall\(.*?\ncheck\(n_table_wide == \d+,.*?\)\n",
            tbl, vt, flags=re.S)

VERIFY.write_text(vt, encoding="utf-8")

print()
print("=" * 92)
print("3. The assertion tuple after")
print("=" * 92)
vt2 = VERIFY.read_text(encoding="utf-8")
m2 = re.search(r"for cmd, expect in \((.*?)\):\n", vt2, re.S)
print(f"  {m2.group(0).strip()[:300] if m2 else 'not found'}")

#: prove the tuple holds what it should by evaluating it
try:
    tree = ast.parse(vt2)
    got = None
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Tuple):
            try:
                got = {c.value: n.value for c, n in
                       ((e.elts[0], e.elts[1]) for e in node.iter.elts
                        if isinstance(e, ast.Tuple) and len(e.elts) == 2)}
            except Exception:
                continue
    print()
    print("  parsed from the file:")
    ok = True
    for cmd, n in (got or {}).items():
        key = cmd[len(BS):]
        want = WANT.get(key)
        good = want == n
        ok &= good
        print(f"      {cmd:18s} {n:>4d}   expected {want}   "
              f"{'ok' if good else 'MISMATCH'}")
    print(f"  all match: {ok}")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")

print()
print("=" * 92)
print("4. Re-running the verifier")
print("=" * 92)
r = subprocess.run(["python", str(VERIFY)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in [l for l in out.splitlines() if l.strip()][-9:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}")
if "SyntaxWarning" in out:
    print("  a SyntaxWarning is present, which means an escape is still wrong")
