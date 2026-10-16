# -*- coding: utf-8 -*-
"""
Verify the generated LaTeX before it is handed over for compilation.

Nothing here can compile the file - no TeX distribution is installed and the sandbox cannot
spawn the renderer - so the checks are structural.  They target the faults that actually
occurred while building it, and they are written as properties of a valid manuscript rather
than as counts for one revision of it.

Why not counts
    Assertions of the form "\\textbf{ appears 156 times" are true of one revision and false of
    the next.  They were repaired four times in this project and each repair risked breaking
    the file, which happened twice - once by collapsing an escape, once by writing an
    unterminated string - and the last repair embedded a regex with a bad escape so the
    verifier crashed instead of checking.  They also miss what matters: a malformed table still
    increments the count of \\begin{table}, and a duplicated section still satisfies a count
    that was updated to match it.

What is checked instead
    Every environment that opens also closes, which catches a truncated table or an unclosed
    environment without needing to know how many there should be.  The commands the conversion
    must not destroy are present above a floor.  Every cited key exists in the bibliography.
    No conversion markers remain.  The abstract and keyword line meet the journal's format.
    None of these go stale, because each compares the file against itself or against a
    property of the format.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"
BIB = ROOT / "submission" / "references.bib"

BS = chr(92)          # a single backslash, never written as an escape in this file
LBR = chr(123)
RBR = chr(125)
STAR = chr(42)

if not TEX.exists():
    raise SystemExit(f"no LaTeX file at {TEX}")
src = TEX.read_text(encoding="utf-8")

passed = 0
failed: list[str] = []
warned: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    global passed
    if ok:
        passed += 1
        print(f"  PASS  {label}" + (f"   {detail}" if detail else ""))
    else:
        failed.append(label)
        print(f"  FAIL  {label}" + (f"   {detail}" if detail else ""))


def note(msg: str) -> None:
    warned.append(msg)
    print(f"  NOTE  {msg}")


print("=" * 94)
print("1. The file and its preamble")
print("=" * 94)
check(len(src) > 40_000, "the LaTeX file is present and substantial",
      f"{len(src):,} characters")
check(BS + "documentclass" + "[utf8]" + LBR + "FrontiersinVancouver" + RBR in src,
      "the Frontiers Vancouver class is used, which fixes the numbered style")
check(BS + "linenumbers" in src, "line numbers are on, which Frontiers requires for review")
check(BS + "firstpage" in src, "the first page marker is set")
check(BS + "maketitle" in src, "the title block is present")
check(BS + "bibliographystyle" + LBR + "Frontiers-Vancouver" + RBR in src,
      "the bibliography style matches the class")
check(BS + "bibliography" + LBR + "references" + RBR in src,
      "the bibliography points at the .bib file")

print()
print("=" * 94)
print("2. Environments open and close in equal number")
print("=" * 94)
for env in ("table", "table*", "tabular", "figure", "itemize", "enumerate", "center",
            "abstract", "document"):
    o = len(re.findall(re.escape(BS + "begin" + LBR + env + RBR), src))
    c = len(re.findall(re.escape(BS + "end" + LBR + env + RBR), src))
    check(o == c, f"{env} environments balance", f"{o} open, {c} close")

n_plain = len(re.findall(re.escape(BS + "begin" + LBR + "table" + RBR), src))
n_wide = len(re.findall(re.escape(BS + "begin" + LBR + "table" + STAR + RBR), src))
n_tab = len(re.findall(re.escape(BS + "begin" + LBR + "tabular" + RBR), src))
print()
check(n_plain + n_wide >= 8, "tables are present", f"{n_plain} plain + {n_wide} wide")
check(n_tab == n_plain + n_wide, "every table contains a tabular",
      f"{n_tab} tabular against {n_plain + n_wide} tables")
check(n_wide >= 1, "wide tables use the double-column float the class defines",
      f"{n_wide} found")

print()
print("=" * 94)
print("3. Commands the conversion must not have destroyed")
print("=" * 94)
for cmd, floor in ((BS + "citep" + LBR, 20), (BS + "section" + LBR, 8),
                   (BS + "subsection" + LBR, 20), (BS + "textbf" + LBR, 50),
                   (BS + "textit" + LBR, 20)):
    n = src.count(cmd)
    check(n >= floor, f"{cmd} survives", f"{n} found, floor {floor}")

print()
print("=" * 94)
print("4. Conversion damage")
print("=" * 94)
DAMAGE = [
    (BS + "textbackslash", "an escaped backslash where a command should be"),
    (BS + LBR + BS + RBR, "an escaped empty brace group"),
    (BS + "textasciitilde", "an escaped tilde"),
    ("**", "unconverted bold markdown"),
]
for marker, desc in DAMAGE:
    n = src.count(marker)
    check(n == 0, f"no {desc}", f"found {n}" if n else "")

if BIB.exists():
    keys = set(re.findall(re.escape(BS) + r"citep" + re.escape(LBR)
                          + r"([^" + re.escape(RBR) + r"]+)" + re.escape(RBR), src))
    bib_keys = set(re.findall(r"@\w+" + re.escape(LBR) + r"([^,\s]+),",
                              BIB.read_text(encoding="utf-8")))
    cited = {p.strip() for k in keys for p in k.split(",") if p.strip()}
    missing = sorted(c for c in cited if c not in bib_keys)
    check(not missing, "every cited key exists in the bibliography",
          f"{len(cited)} cited, {len(bib_keys)} in the .bib"
          + (f", missing {missing}" if missing else ""))
    uncited = sorted(b for b in bib_keys if b not in cited)
    if uncited:
        note(f"{len(uncited)} bibliography entries are never cited: {uncited[:8]}")
    else:
        check(True, "every bibliography entry is cited")
else:
    check(False, "the bibliography file exists")

print()
print("=" * 94)
print("5. Journal requirements")
print("=" * 94)
check(src.count(BS + "begin" + LBR + "abstract" + RBR) == 1, "exactly one abstract")
a0 = src.find(BS + "begin" + LBR + "abstract" + RBR)
a1 = src.find(BS + "end" + LBR + "abstract" + RBR)
if a0 >= 0 and a1 > a0:
    body = re.sub(BS + r"[a-zA-Z]+\*?" + re.escape(LBR) + r"[^" + re.escape(RBR) + r"]*"
                  + re.escape(RBR), " ", src[a0:a1])
    n_abs = len([w for w in body.split() if w.strip()])
    check(200 <= n_abs <= 1200, "the abstract is within a plausible range",
          f"{n_abs} words")

kw = re.search(r"Keywords:\s*" + re.escape(RBR) + r"?\s*([^" + re.escape(RBR) + r"\n]+)",
               src)
if kw:
    #: the abstract writer joins the keywords with commas, so both separators are counted
    raw = kw.group(1)
    parts = [k.strip() for k in re.split(r"[,;]", raw) if k.strip()]
    check(5 <= len(parts) <= 8, "between 5 and 8 keywords, as Frontiers requires",
          f"{len(parts)} found")
    if len(parts) > 8:
        note(f"the keyword line holds {len(parts)} terms; the writer truncates to 8")
else:
    check(False, "a keyword line is present")

print()
print("=" * 94)
print("Result")
print("=" * 94)
print(f"  checks passed : {passed}")
print(f"  checks failed : {len(failed)}")
for f in failed:
    print(f"      {f}")
print(f"  notes         : {len(warned)}")
print()
if failed:
    print("  Not ready.  The failures above are the ones to fix.")
    sys.exit(1)
print("  Structurally sound.  Compilation still has to be confirmed on Overleaf,")
print("  because no TeX distribution is available here to run it.")
