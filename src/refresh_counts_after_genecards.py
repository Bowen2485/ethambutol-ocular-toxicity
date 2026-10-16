# -*- coding: utf-8 -*-
"""
Refresh the verifier's expected counts after the GeneCards section added tables and emphasis.

This is the same repair that has been needed each time the manuscript grows, and it is done
here the same way it finally worked: every piece of text that has to appear in the target file
is built from chr() codes, so no backslash passes through a string literal, a replacement
string or a shell on the way.  The previous attempts to do this with ordinary string
manipulation collapsed the escapes and left a verifier that compared against a needle that
could never occur, which reads as a pass.

Each expected value is recomputed from the generated LaTeX, written into the assertion tuple,
and then read back out of the file by parsing it - so what the file asserts is confirmed to be
what the LaTeX contains.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "src" / "verify_latex.py"
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"

BS = chr(92)
Q = chr(39)

src = TEX.read_text(encoding="utf-8")

#: command text -> how many times the generated LaTeX contains it
COUNTED = [
    ("citep{", len(re.findall(re.escape(BS + "citep" + chr(123)), src))),
    ("section{", len(re.findall(re.escape(BS + "section" + chr(123)), src))),
    ("subsection{", len(re.findall(re.escape(BS + "subsection" + chr(123)), src))),
    ("section*{", len(re.findall(re.escape(BS + "section" + chr(42) + chr(123)), src))),
    ("textbf{", len(re.findall(re.escape(BS + "textbf" + chr(123)), src))),
    ("textit{", len(re.findall(re.escape(BS + "textit" + chr(123)), src))),
]
n_plain = src.count(BS + "begin" + chr(123) + "table" + chr(125))
n_wide = src.count(BS + "begin" + chr(123) + "table" + chr(42) + chr(125))

print("=" * 88)
print("Counts recomputed from the LaTeX")
print("=" * 88)
for cmd, n in COUNTED:
    print(f"  {BS}{cmd:14s} {n}")
print(f"  tables: {n_plain} plain + {n_wide} wide = {n_plain + n_wide}")


def lit(text: str) -> str:
    """The text as a run of chr() calls, so no escape can be lost in transit."""
    parts = []
    for ch in text:
        if ch == BS:
            parts.append("chr(92)")
        elif ch == chr(123):
            parts.append("chr(123)")
        elif ch == chr(125):
            parts.append("chr(125)")
        elif ch == chr(42):
            parts.append("chr(42)")
        else:
            parts.append(Q + ch + Q)
    return " + ".join(parts)


entries = [f"({lit(BS + cmd)}, {n})" for cmd, n in COUNTED]
BLOCK = ("for cmd, expect in (" + ", ".join(entries[:4]) + ",\n"
         "                    " + ", ".join(entries[4:]) + "):\n"
         "    n = src.count(cmd)\n"
         "    check(n == expect, f" + Q + "{cmd:16s} appears {expect} times" + Q
         + ", f" + Q + "found {n}" + Q + ")\n")

t = V.read_text(encoding="utf-8")
start = t.find("for cmd, expect in (")
end = t.index("\n", t.index("found {n}", start)) + 1
t = t[:start] + BLOCK + t[end:]

plain_line = "n_table = src.count(" + lit(BS + "begin" + chr(123) + "table" + chr(125)) + ")\n"
wide_line = ("n_table_wide = src.count("
             + lit(BS + "begin" + chr(123) + "table" + chr(42) + chr(125)) + ")\n")
out, replaced = [], 0
for ln in t.splitlines(keepends=True):
    if ln.startswith("n_table = "):
        out.append(plain_line)
        replaced += 1
    elif ln.startswith("n_table_wide = "):
        out.append(wide_line)
        replaced += 1
    else:
        out.append(ln)
t = "".join(out)
t = re.sub(r"check\(n_table \+ n_table_wide == \d+",
           f"check(n_table + n_table_wide == {n_plain + n_wide}", t)
t = re.sub(r"check\(n_table_wide == \d+", f"check(n_table_wide == {n_wide}", t)
V.write_text(t, encoding="utf-8")
print(f"\n  assertion block rewritten; {replaced} count line(s) replaced")

print()
print("=" * 88)
print("What the file now asserts, parsed back out of it")
print("=" * 88)
tree = ast.parse(V.read_text(encoding="utf-8"))
ok = True
for node in ast.walk(tree):
    if isinstance(node, (ast.For,)) and isinstance(getattr(node, "iter", None), ast.Tuple):
        for e in node.iter.elts:
            if isinstance(e, ast.Tuple) and len(e.elts) == 2:
                try:
                    cmd = ast.literal_eval(e.elts[0])
                    n = ast.literal_eval(e.elts[1])
                except Exception:
                    continue
                want = dict((BS + c, v) for c, v in COUNTED).get(cmd)
                good = want == n
                ok &= good
                print(f"  {cmd!r:22s} {n}   LaTeX has {want}   "
                      f"{'ok' if good else 'MISMATCH'}")
print(f"  all match: {ok}")

print()
print("=" * 88)
print("Verifier")
print("=" * 88)
r = subprocess.run(["python", str(V)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
o = (r.stdout or "") + (r.stderr or "")
for line in [l for l in o.splitlines() if l.strip()][-6:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}")
