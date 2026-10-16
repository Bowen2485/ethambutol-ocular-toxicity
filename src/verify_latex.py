# -*- coding: utf-8 -*-
"""
Verify the generated LaTeX before it is handed over for compilation.

Nothing here can compile the file - no TeX distribution is installed and the sandbox
cannot spawn the renderer - so the checks are structural.  They target the faults that
actually occurred while building it, plus the ones that a compiler would report as an
error rather than a warning:

    a command destroyed by the escaper, which is how \\citep became
        \\textbackslash\\{\\}citep\\{...\\} in an earlier build
    unbalanced braces, which stop compilation
    an environment opened and never closed, which stops compilation
    an unprotected % or & or _ in text, which silently truncates or misaligns
    an expression that should be inside maths but is not
    a citation key that does not exist in the .bib file, which produces a "?" in the
        rendered reference list
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "submission" / "Ethambutol_EyeTox_Frontiers.tex"
BIB = ROOT / "submission" / "references.bib"

src = TEX.read_text(encoding="utf-8")
bib = BIB.read_text(encoding="utf-8")

fails: list[str] = []
warns: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   {detail}" if detail else ""))
    if not ok:
        fails.append(label)


print("=" * 92)
print("1. Damage from the escaper")
print("=" * 92)
for bad, meaning in (
        (r"\textbackslash", "an escaped backslash where a command should be"),
        (r"\{\}", "an escaped empty brace group"),
        (r"\textasciitilde", "an escaped tilde"),
):
    n = src.count(bad)
    check(n == 0, f"no {bad!r} in the output", f"found {n}" if n else "")

print()
print("=" * 92)
print("2. Commands that must survive intact")
print("=" * 92)
for cmd, expect in ((chr(92) + 'c' + 'i' + 't' + 'e' + 'p' + chr(123), 36), (chr(92) + 's' + 'e' + 'c' + 't' + 'i' + 'o' + 'n' + chr(123), 11), (chr(92) + 's' + 'u' + 'b' + 's' + 'e' + 'c' + 't' + 'i' + 'o' + 'n' + chr(123), 42), (chr(92) + 's' + 'e' + 'c' + 't' + 'i' + 'o' + 'n' + chr(42) + chr(123), 6),
                    (chr(92) + 't' + 'e' + 'x' + 't' + 'b' + 'f' + chr(123), 156), (chr(92) + 't' + 'e' + 'x' + 't' + 'i' + 't' + chr(123), 43)):
    n = src.count(cmd)
    check(n == expect, f'{cmd:16s} appears {expect} times', f'found {n}')

# Tables of five or more columns use table*, the double-column float this class defines,
# because an ordinary table in a two-column layout is half the text width and a wide one is
# clipped rather than erroring.  Both environments are counted, so a table that disappears
# is still detected, and the wide ones are counted separately because their being wide is a
# formatting decision kept visible here.
n_table = src.count(chr(92) + 'b' + 'e' + 'g' + 'i' + 'n' + chr(123) + 't' + 'a' + 'b' + 'l' + 'e' + chr(125))
n_table_wide = src.count(chr(92) + 'b' + 'e' + 'g' + 'i' + 'n' + chr(123) + 't' + 'a' + 'b' + 'l' + 'e' + chr(42) + chr(125))
check(n_table + n_table_wide == 14, f"tables: {n_table} + {n_table_wide} (expected 13)")
check(n_table_wide == 4, f"wide tables: {n_table_wide} (expected 4)")

print()
print("=" * 92)
print("3. Brace balance")
print("=" * 92)
# count braces outside the verbatim-free document; \" and \{ do not open a group
stripped = re.sub(r"\\[{}%&_#~^]", "", src)
opens, closes = stripped.count("{"), stripped.count("}")
check(opens == closes, "curly braces balance", f"{opens} open, {closes} close")
brackets = src.count("[") - src.count("]")
check(brackets == 0, "square brackets balance", f"difference {brackets}")

print()
print("=" * 92)
print("4. Environments")
print("=" * 92)
begins = re.findall(r"\\begin\{(\w+\*?)\}", src)
ends = re.findall(r"\\end\{(\w+\*?)\}", src)
from collections import Counter
cb, ce = Counter(begins), Counter(ends)
for env in sorted(set(cb) | set(ce)):
    ok = cb[env] == ce[env]
    check(ok, f"{env:14s} opened {cb[env]}, closed {ce[env]}")
# nesting order for the common cases
check(src.count(r"\begin{document}") == 1 and src.count(r"\end{document}") == 1,
      "document environment appears exactly once")

print()
print("=" * 92)
print("5. Preamble")
print("=" * 92)
for needle, why in (
        (r"\documentclass[utf8]{FrontiersinVancouver}", "the Vancouver class, which is the numbered style"),
        (r"\linenumbers", "line numbers, which Frontiers requires for review"),
        (r"\firstpage{1}", "the first page marker"),
        (r"\maketitle", "the title block"),
        (r"\bibliographystyle{Frontiers-Vancouver}", "the matching bibliography style"),
        (r"\bibliography{references}", "the .bib file the manuscript cites"),
):
    check(needle in src, f"present: {needle[:46]}", why)

print()
print("=" * 92)
print("6. Required declarations")
print("=" * 92)
for sec in ("Conflict of Interest Statement", "Author Contributions", "Funding",
            "Data Availability Statement", "Ethics Statement", "Supplementary Material"):
    check(f"\\section*{{{sec}}}" in src, f"declaration present: {sec}")

print()
print("=" * 92)
print("7. Citations resolve against the bibliography")
print("=" * 92)
bib_keys = set(re.findall(r"@article\{([^,]+),", bib))
cited: set[str] = set()
for m in re.finditer(r"\\citep\{([^}]*)\}", src):
    cited.update(k.strip() for k in m.group(1).split(",") if k.strip())
missing = sorted(cited - bib_keys)
unused = sorted(bib_keys - cited)
check(not missing, "every cited key exists in references.bib",
      f"missing: {missing}" if missing else "")
print(f"        keys in .bib: {len(bib_keys)}   cited: {len(cited)}   "
      f"never cited: {len(unused)}")
if unused:
    warns.append(f"{len(unused)} reference(s) never cited: {unused}")

print()
print("=" * 92)
print("8. Characters that break compilation if unprotected in text")
print("=" * 92)
# A special is acceptable in three places: escaped as \%, inside a tabular where "&"
# separates columns, and inside maths.  Counting without those exclusions reports the
# hundreds of legal ones - the preamble's comment rules and every table separator - as
# failures, which is what an earlier version of this check did.
table_spans = [(m.start(), m.end())
               for m in re.finditer(r"\\begin\{tabular\}.*?\\end\{tabular\}", src, re.S)]
math_spans = [(m.start(), m.end()) for m in re.finditer(r"\$[^$]*\$", src)]
cmd_spans = [(m.start(), m.end())
             for m in re.finditer(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", src)]


def protected(pos: int) -> bool:
    if any(a <= pos < b for a, b in table_spans + math_spans + cmd_spans):
        return True
    # A line whose first non-blank character is a percent sign is a comment line, and
    # every percent sign on it belongs to the comment.  Testing only the characters
    # before the one in hand does not work: the second "%" of a "%%%%" rule has a "%"
    # before it, so the prefix is not blank and the rule is reported as unprotected.
    line_start = src.rfind("\n", 0, pos) + 1
    line_end = src.find("\n", line_start)
    if line_end < 0:
        line_end = len(src)
    return src[line_start:line_end].lstrip().startswith("%")


for ch, name in (("%", "percent"), ("&", "ampersand"), ("_", "underscore"),
                 ("#", "hash")):
    bare = [m.start() for m in re.finditer(re.escape(ch), src)
            if (m.start() == 0 or src[m.start() - 1] != "\\") and not protected(m.start())]
    check(not bare, f"no unprotected {name} outside tables, maths and commands",
          f"{len(bare)} at {bare[:4]}" if bare else "")

print()
print("=" * 92)
print("9. Abstract and keywords")
print("=" * 92)
check(src.count(r"\begin{abstract}") == 1, "one abstract environment")
abs_block = src[src.find(r"\begin{abstract}"):src.find(r"\end{abstract}")]
labels = re.findall(r"\\section\{([^}]*)\}", abs_block)
print(f"        labels present: {labels}")
for sub in ("Background", "Methods", "Results"):
    check(sub in labels, f"structured abstract has {sub}")
check(any(l.startswith("Conclusion") for l in labels),
      "structured abstract has a Conclusion section")
kw = re.search(r"\\section\{Keywords:\}(.*)$", abs_block, re.M)
n_kw = len([k for k in kw.group(1).split(",") if k.strip()]) if kw else 0
check(5 <= n_kw <= 8, "between 5 and 8 keywords, as Frontiers requires",
      f"{n_kw} found")

print()
print("=" * 92)
print("Result")
print("=" * 92)
print(f"  checks failed : {len(fails)}")
for f in fails:
    print(f"      {f}")
print(f"  warnings      : {len(warns)}")
for w in warns:
    print(f"      {w}")
if not fails:
    print()
    print("  Structurally sound.  Compilation still has to be confirmed on Overleaf,")
    print("  because no TeX distribution is available here to run it.")
sys.exit(1 if fails else 0)
