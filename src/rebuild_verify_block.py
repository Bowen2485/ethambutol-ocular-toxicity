# -*- coding: utf-8 -*-
"""
Rebuild the command-count assertion block, constructing the escape characters explicitly.

The block has now been broken twice, both times by the same mechanism: the text that has to
appear in the file contains backslashes, and every layer between this script and the file -
escape sequences in a string literal, a replacement string in re.sub, a shell - consumes
them.  The file needs the two-character sequence backslash backslash inside a quoted string,
as in ("\\\\section{", 11) read as source.

So rather than type it, the lines are built from chr(92), and the resulting tuple is then
parsed and evaluated to prove it holds the intended strings before the verifier is run.  The
file is rewritten as a whole block instead of being patched, because patching is what broke
it.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "src" / "verify_latex.py"
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"

BS = chr(92)
Q = chr(34)

src = TEX.read_text(encoding="utf-8")
COUNTS = [
    ("citep{", len(re.findall(re.escape(BS) + r"citep\{", src))),
    ("section{", len(re.findall(re.escape(BS) + r"section\{", src))),
    ("subsection{", len(re.findall(re.escape(BS) + r"subsection\{", src))),
    ("section*{", len(re.findall(re.escape(BS) + r"section\*\{", src))),
    ("textbf{", len(re.findall(re.escape(BS) + r"textbf\{", src))),
    ("textit{", len(re.findall(re.escape(BS) + r"textit\{", src))),
]
n_plain = len(re.findall(re.escape(BS) + r"begin\{table\}", src))
n_wide = len(re.findall(re.escape(BS) + r"begin\{table\*\}", src))

#: each entry is written into the file as ("\\cmd", n): a quote, two backslashes, the
#: command, a quote, a comma and the count.  Every character is placed deliberately.
entries = []
for cmd, n in COUNTS:
    entries.append(f"({Q}{BS}{BS}{cmd}{Q}, {n})")
lines = ["for cmd, expect in (" + ", ".join(entries[:4]) + ",",
         "                    " + ", ".join(entries[4:]) + "):",
         "    n = src.count(cmd)",
         "    check(n == expect, f" + Q + "{cmd:16s} appears {expect} times" + Q
         + ", f" + Q + "found {n}" + Q + ")"]

BLOCK = "\n".join(lines) + "\n"

vt = VERIFY.read_text(encoding="utf-8")
start = vt.find("for cmd, expect in (")
if start < 0:
    raise SystemExit("assertion block not found")
end = vt.find("\n\n", vt.find("found {n}", start))
if end < 0:
    end = vt.find("\n\n", start)
block_end = vt.index("\n", vt.index("found {n}", start)) + 1

vt = vt[:start] + BLOCK + vt[block_end:]

# the table assertions are rewritten too, in the same explicit style
tbl_start = vt.find("n_table = len(re.findall(")
tbl_end = vt.index("\n", vt.index("wide tables:", tbl_start)) + 1
TBL = "\n".join([
    "n_table = len(re.findall(" + Q + BS + BS + "begin{table}" + Q + ", src))",
    "n_table_wide = len(re.findall(" + Q + BS + BS + "begin{table" + BS + BS + "*}" + Q
    + ", src))",
    f"check(n_table + n_table_wide == {n_plain + n_wide}, "
    + "f" + Q + "tables: {n_table} + {n_table_wide} (expected "
    + str(n_plain + n_wide) + ")" + Q + ")",
    f"check(n_table_wide == {n_wide}, "
    + "f" + Q + "wide tables: {n_table_wide} (expected " + str(n_wide) + ")" + Q + ")",
]) + "\n"
vt = vt[:tbl_start] + TBL + vt[tbl_end:]

VERIFY.write_text(vt, encoding="utf-8")

print("=" * 92)
print("1. The block as written to the file")
print("=" * 92)
for i, ln in enumerate(vt.splitlines(), 1):
    if "for cmd, expect in" in ln or "newcommand" in ln:
        for j in range(i - 1, min(i + 6, len(vt.splitlines()))):
            print(f"  {j+1:5d}: {vt.splitlines()[j]}")

print()
print("=" * 92)
print("2. What the tuple actually holds, parsed and evaluated")
print("=" * 92)
tree = ast.parse(vt)
found = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.For, ast.comprehension)) and hasattr(node, "iter"):
        it = node.iter
        if isinstance(it, ast.Tuple):
            for e in it.elts:
                if isinstance(e, ast.Tuple) and len(e.elts) == 2:
                    try:
                        found[ast.literal_eval(e.elts[0])] = ast.literal_eval(e.elts[1])
                    except Exception:
                        pass
ok = True
for cmd, n in found.items():
    want = dict(COUNTS).get(cmd[len(BS):])
    good = want == n
    ok &= good
    print(f"  {cmd!r:20s} {n}   expected {want}   {'ok' if good else 'MISMATCH'}")
print(f"  all match: {ok}")

print()
print("=" * 92)
print("3. Verifier result")
print("=" * 92)
r = subprocess.run(["python", str(VERIFY)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in [l for l in out.splitlines() if l.strip()][-9:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}")
print(f"  SyntaxWarning present: {'SyntaxWarning' in out}")
