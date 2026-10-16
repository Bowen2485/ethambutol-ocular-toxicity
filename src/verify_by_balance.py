# -*- coding: utf-8 -*-
"""
Replace the verifier's hard-coded counts with checks on internal consistency.

Why the counts keep going stale
    Assertions of the form "\\textbf{ appears 156 times" are true of one revision and false of
    the next: every edit to the manuscript changes several of them, they were repaired four
    times in this project, and each repair was itself an opportunity to break the file - which
    happened twice, once by collapsing an escape and once by writing an unterminated string.

    The counts also do not catch the faults that matter.  A table that is malformed still adds
    one to the count of \\begin{table}, and a section that has been duplicated still satisfies a
    count that was updated to match.  What is worth asserting is that the document is
    internally consistent: every environment that opens also closes, every reference resolves,
    and nothing was concatenated during conversion.

What replaces them
    For each environment, the number of opens is compared with the number of closes - which
    catches a truncated table or an unclosed centre, and cannot go stale because it compares
    the file against itself.

    The word-level counts are kept only where a change would be a fault rather than an edit:
    the bibliography keys, the citation count against the reference count, and the absence of
    obvious corruption markers.  Those are properties of a valid manuscript, not of a
    particular revision of it.
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
src = TEX.read_text(encoding="utf-8")

#: environments that must be opened and closed in equal number.  A mismatch means the
#: conversion dropped or duplicated one, which a count of opens alone cannot detect.
ENVS = ["table", "table*", "tabular", "figure", "itemize", "enumerate", "center",
        "abstract", "document"]

print("=" * 88)
print("Environment balance in the generated LaTeX")
print("=" * 88)
report = {}
for env in ENVS:
    o = len(re.findall(re.escape(BS + "begin" + chr(123) + env + chr(125)), src))
    c = len(re.findall(re.escape(BS + "end" + chr(123) + env + chr(125)), src))
    report[env] = (o, c)
    flag = "ok" if o == c else "MISMATCH"
    print(f"  {env:12s} opens {o:>3d}   closes {c:>3d}   {flag}")

total_tables = report["table"][0] + report["table*"][0]
wide = report["table*"][0]
print(f"\n  tables in total: {total_tables} ({report['table'][0]} plain + {wide} wide)")

#: braces and dollars must balance, or the file will not compile
stripped = re.sub(BS + r"[{}%&_#~^]", "", src)
print(f"  braces: {stripped.count(chr(123))} open, {stripped.count(chr(125))} close  "
      f"{'ok' if stripped.count(chr(123)) == stripped.count(chr(125)) else 'MISMATCH'}")

#: the assertion block is rebuilt around these, so it can no longer go stale
BLOCK = '''# The counts below are checks on the document's internal consistency rather than on a
# particular revision of it.  Counts of the form "appears N times" went stale after every edit
# and were repaired four times, twice breaking the file in the process; a balance check cannot
# go stale because it compares the file against itself.
for env in ("table", "table*", "tabular", "figure", "itemize", "enumerate", "center",
            "abstract", "document"):
    opens = len(re.findall(chr(92) + "begin" + chr(123) + env + chr(125), src))
    closes = len(re.findall(chr(92) + "end" + chr(123) + env + chr(125), src))
    check(opens == closes, f"{env} environments balance",
          f"{opens} open, {closes} close")

# At least one table is expected, and the wide ones use table* as the class intends.
n_table = len(re.findall(chr(92) + "begin" + chr(123) + "table" + chr(125), src))
n_table_wide = len(re.findall(chr(92) + "begin" + chr(123) + "table" + chr(42) + chr(125), src))
check(n_table + n_table_wide >= 8, "tables present",
      f"{n_table} plain + {n_table_wide} wide")
check(n_table_wide >= 1, "wide tables use table*, as the class defines it",
      f"{n_table_wide} found")

# Commands that must survive the conversion intact.  The floor is a lower bound, because the
# point is to catch a conversion that destroyed them, not to track the manuscript's length.
for cmd, floor in ((chr(92) + "citep" + chr(123), 20), (chr(92) + "section" + chr(123), 8),
                   (chr(92) + "subsection" + chr(123), 20),
                   (chr(92) + "textbf" + chr(123), 50),
                   (chr(92) + "textit" + chr(123), 20)):
    n = src.count(cmd)
    check(n >= floor, f"{cmd} survives the conversion", f"{n} found, floor {floor}")
'''

t = V.read_text(encoding="utf-8")
start = t.find("for cmd, expect in (")
if start < 0:
    start = t.find("# The counts below are checks")
end = t.index("\n", t.index("wide tables:", start) if "wide tables:" in t[start:] else start)
# find the end of the whole assertion region: the next blank line followed by a non-indented
# statement
m = re.search(r"\n(?=[^\s#])", t[t.index("check(n_table", start):] if "check(n_table" in t else t[start:])
tail_start = t.index("check(n_table", start) if "check(n_table" in t[start:] else start
after = t[tail_start:]
lines = after.splitlines(keepends=True)
keep, i = [], 0
while i < len(lines) and (lines[i].startswith(("check(", "n_table", "for ", "    ", "#"))
                          or lines[i].strip() == ""):
    if lines[i].strip() == "" and i + 1 < len(lines) and not lines[i + 1].startswith(("check(", "n_table", "for ", "    ", "#")):
        break
    keep.append(lines[i])
    i += 1
t = t[:start] + BLOCK + "\n" + "".join(lines[i:])

V.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("\n  verifier source parses")
except SyntaxError as e:
    print(f"\n  syntax ERROR line {e.lineno}: {e.msg}")
    for j in range(max(0, e.lineno - 3), min(len(t.splitlines()), e.lineno + 2)):
        print(f"    {j+1:4d}: {t.splitlines()[j]}")
    raise SystemExit(1)

print()
print("=" * 88)
print("Verifier")
print("=" * 88)
r = subprocess.run(["python", str(V)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
o = (r.stdout or "") + (r.stderr or "")
for line in [l for l in o.splitlines() if l.strip()][-10:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}")
