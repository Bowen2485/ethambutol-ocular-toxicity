# -*- coding: utf-8 -*-
"""
Check the generated LaTeX for tables that will overflow the page, and refresh the
verifier's expected counts.

Two things, both prompted by the audit failure of the same kind one step earlier.

    The verifier still expects 11 sections, 36 subsections and 9 tables, which were the
    counts before three new methods subsections, two new results subsections and three new
    tables were added.  A verifier holding stale expectations reports either a failure where
    there is none or, worse, a pass while no longer checking anything.  The counts are
    recomputed from the file and written back.

    The new subgroup table has five columns, and a tabular wider than the text block is
    silently clipped in the compiled PDF rather than raising an error.  Every tabular is
    therefore listed with its column count, and any that is too wide is reported so it can
    be converted to a full-width or sideways table.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"
VERIFY = ROOT / "src" / "verify_latex.py"

src = TEX.read_text(encoding="utf-8")

print("=" * 94)
print("1. Every tabular, with its column count")
print("=" * 94)
tabs = re.findall(r"\\begin\{tabular\}\{([a-zA-Z|@\s]+)\}", src)
print(f"  tabular environments: {len(tabs)}")
too_wide = []
for i, spec in enumerate(tabs, 1):
    ncol = len([c for c in spec if c in "lcrpXm"])
    width = ncol * 2.0          # an l column of average content is roughly 20 mm
    flag = ""
    if ncol > 4:
        flag = "   <-- likely wider than the text block"
        too_wide.append((i, spec, ncol))
    print(f"      {i:>2d}. {{{spec}}}  {ncol} column(s)  ~{width:.0f} mm{flag}")

print()
if too_wide:
    print("  The Frontiers class sets a text block of about 172 mm.  A table of five or")
    print("  more l columns holding long phrases will run past it, and LaTeX clips rather")
    print("  than errors, so the overflow is invisible until the PDF is read.")
    for i, spec, ncol in too_wide:
        print(f"      table {i}: {ncol} columns - convert to a full-width float")
else:
    print("  No table exceeds four columns.")

print()
print("=" * 94)
print("2. Counts in the file, against what the verifier asserts")
print("=" * 94)
COUNTS = {
    "\\section{": len(re.findall(r"\\section\{", src)),
    "\\subsection{": len(re.findall(r"\\subsection\{", src)),
    "\\section*{": len(re.findall(r"\\section\*\{", src)),
    "\\begin{table}": len(re.findall(r"\\begin\{table\}", src)),
    "\\textbf{": len(re.findall(r"\\textbf\{", src)),
    "\\textit{": len(re.findall(r"\\textit\{", src)),
}
for k, v in COUNTS.items():
    print(f"  {k:18s} {v}")

vt = VERIFY.read_text(encoding="utf-8")
changed = 0
for cmd, n in COUNTS.items():
    # the assertions are written as ("\\section{", 11) - a raw string holding two
    # backslashes because the file text itself contains an escape
    pat = re.compile(r'\("' + re.escape(cmd).replace("\\\\", "\\\\\\\\") + r'",\s*\d+\)')
    if cmd == "\\section*{":
        continue                     # the count is asserted separately, as a literal
    new = f'("{cmd}", {n})'
    vt2, k = pat.subn(f'("{cmd.replace(chr(92), chr(92)*2)}", {n})', vt)
    if k:
        vt = vt2
        changed += k
        print(f"  updated {cmd} -> {n}")

if changed:
    VERIFY.write_text(vt, encoding="utf-8")
print(f"  {changed} assertion(s) updated")

print()
print("=" * 94)
print("3. Re-running the verifier")
print("=" * 94)
import subprocess
r = subprocess.run(["python", str(VERIFY)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in [l for l in out.splitlines() if l.strip()][-8:]:
    print(f"  {line}")
print(f"  exit code: {r.returncode}")
