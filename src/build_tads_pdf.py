# -*- coding: utf-8 -*-
"""Render the restructured manuscript to a review-ready PDF.

No journal template is used: Therapeutic Advances in Drug Safety takes a Word or PDF
manuscript, and what a reviewer needs is a double-spaced text with line numbers, Times, the
tables and figures in place.  xelatex is used with a Unicode font so that en dashes, the
multiplication sign and the micro sign are set correctly without a symbol table.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
FIG = ROOT / "results" / "tads_figures"
OUT = ROOT / "submission" / "tads"
OUT.mkdir(parents=True, exist_ok=True)

SRC = MAN / "TADS_manuscript.md"
text = SRC.read_text(encoding="utf-8")
#: the title page is composed in LaTeX below; the Markdown title block would otherwise be
#: rendered a second time as a section heading
text = text[text.find("## Abstract"):]

FIG_FILES = {"Figure 1.": "Figure1_flow", "Figure 2.": "Figure2_smq_forest",
             "Figure 3.": "Figure3_pt_forest", "Figure 4.": "Figure4_sensitivity"}


def esc(s: str) -> str:
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("$", r"\$"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    return s


def inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\textit{\1}", s)
    s = s.replace("`", "")
    return s


def is_table_row(ln: str) -> bool:
    return ln.strip().startswith("|") and ln.strip().endswith("|")


def render_table(block: list[str]) -> list[str]:
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r if c)]
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    #: equal columns wrapped the long labels ("FAERS quarterly ASCII re-leases", "Optic nerve
    #: disor-ders"), so the width of each column follows the longest cell it has to hold, and
    #: every column is set ragged-right: justified text inside a narrow p-column produced
    #: stretched gaps such as "Records  naming  ethambutol".
    weight = []
    for c in range(ncol):
        longest = max(len(inline(r[c])) for r in rows)
        #: the floor is what a cell can actually wrap to: a single unbreakable token such as
        #: "0.00012" overflowed a column sized by average content, so the minimum weight has to
        #: exceed the longest token, not the average cell
        longest_word = max((len(w) for r in rows for w in inline(r[c]).split()), default=4)
        weight.append(min(max(longest, longest_word + 4, 12), 46))
    total = sum(weight)
    #: 0.97 leaves room for the inter-column padding and the rules, which the per-column
    #: subtraction of 2\tabcolsep does not fully account for
    widths = [0.93 * w / total for w in weight]
    colspec = "".join(
        r">{\raggedright\arraybackslash}p{\dimexpr%.4f\textwidth-2\tabcolsep\relax}" % w
        for w in widths)
    #: a short table (Table 4 has six data rows) was splitting with one row on the next page;
    #: reserving its estimated height keeps it whole without forcing a break before the long ones
    need = 1.5 + 0.75 * len(rows)
    prefix = [r"\needspace{%.1fcm}" % need] if len(rows) <= 10 else []
    out = prefix + [r"{\footnotesize\setlength{\tabcolsep}{3.2pt}",
                    r"\begin{longtable}{" + colspec + "}", r"\hline"]
    header = " & ".join(inline(c) for c in rows[0]) + r" \\"
    for i, r in enumerate(rows):
        out.append(" & ".join(inline(c) for c in r) + r" \\")
        if i == 0:
            #: repeat the header on continuation pages; Table 3 runs from one page to the next
            out += [r"\hline", r"\endfirsthead", r"\hline", header, r"\hline", r"\endhead"]
    out += [r"\hline", r"\end{longtable}", "}"]
    return out


body_lines: list[str] = []
ref_group_open = False
tables_done = 0
i = 0
lines = text.splitlines()
while i < len(lines):
    ln = lines[i]
    s = ln.strip()
    if not s:
        body_lines.append("")
        i += 1
        continue
    if is_table_row(ln):
        block = []
        while i < len(lines) and is_table_row(lines[i]):
            block.append(lines[i])
            i += 1
        tables_done += 1
        body_lines += render_table(block)
        continue
    if s.startswith("# "):
        body_lines.append(r"\section*{" + inline(s[2:]) + "}")
        i += 1
        continue
    if s.startswith("## "):
        #: the reference list runs to the last page by a few lines; a smaller size and tighter
        #: paragraph spacing keep it from spilling onto a page of its own
        if s[3:].strip().lower().startswith("references"):
            body_lines.append(r"\begingroup\small\setlength{\parskip}{1pt}"
                              r"\linespread{0.94}\selectfont")
            ref_group_open = True
        body_lines.append(r"\section*{" + inline(s[3:]) + "}")
        i += 1
        continue
    if s.startswith("### "):
        body_lines.append(r"\subsection*{" + inline(s[4:]) + "}")
        i += 1
        continue
    if s in ("---", "***"):
        body_lines.append(r"\bigskip")
        i += 1
        continue
    # paragraph: gather until blank / heading / table / rule
    para = [s]
    i += 1
    while i < len(lines):
        nxt = lines[i]
        ns = nxt.strip()
        if (not ns or ns in ("---", "***") or ns.startswith("#") or is_table_row(nxt)):
            break
        para.append(ns)
        i += 1
    #: reference lines arrive as one block without blank lines; emitted as a single
    #: paragraph they run together, so each entry gets its own hanging-indent paragraph
    if ref_group_open and re.match(r"^\d{1,2}\.\s", para[0]):
        for line in para:
            body_lines.append(r"\par\noindent\hangindent=1.35em\hangafter=1 "
                              + inline(line) + r"\par")
        continue
    joined = " ".join(para)
    #: a table caption is a paragraph of its own; without help it stays on the previous page when
    #: the table is pushed over, which happened to Table 4.  Look ahead for the table that follows
    #: and reserve room for caption plus table.
    if re.match(r"^Table \d+\.", joined):
        k = i
        while k < len(lines) and not is_table_row(lines[k]) and lines[k].strip() != "":
            k += 1
        while k < len(lines) and lines[k].strip() == "":
            k += 1
        if k < len(lines) and is_table_row(lines[k]):
            n_rows = 0
            while k + n_rows < len(lines) and is_table_row(lines[k + n_rows]):
                n_rows += 1
            if n_rows <= 10:
                body_lines.append(r"\needspace{%.1fcm}" % (2.2 + 0.75 * n_rows))
    body_lines.append(inline(joined))

#: the reference group opened above has to be closed at the end of the document, since the
#: references are the last section
if ref_group_open:
    body_lines.append(r"\endgroup")
body = "\n".join(body_lines)
body = re.sub(r"\n{3,}", "\n\n", body)

#: the figure legends are given as text; the images are placed after them, one per page
legend_text = {}
_man = (ROOT / "manuscript" / "TADS_manuscript.md").read_text(encoding="utf-8")
for _m in re.finditer(r"\*\*(Figure (\d+)\.)\*\*\s*(.+?)(?=\n\*\*Figure|\n## |\Z)", _man, re.S):
    legend_text[int(_m.group(2))] = (" ".join(_m.group(3).split()))

def tex_escape(t: str) -> str:
    """Percent, ampersand and underscore are active in LaTeX and truncate or break the caption."""
    return (t.replace("\\", r"\textbackslash{}").replace("%", r"\%")
             .replace("&", r"\&").replace("_", r"\_")
             .replace("#", r"\#").replace("$", r"\$"))


fig_block = []
for key, stem in FIG_FILES.items():
    path = FIG / f"{stem}.pdf"
    if not path.exists():
        print(f"  missing figure {path}")
        continue
    n = int(re.sub(r"[^0-9]", "", key) or 0)
    caption = tex_escape(legend_text.get(n, ""))
    #: an inline figure starts at the top of a fresh page; a [p] float is centred vertically,
    #: which left most of each figure page empty
    fig_block.append(r"\clearpage")
    fig_block.append(r"\noindent\includegraphics[width=0.96\linewidth]{" + str(path.as_posix()) + "}")
    if caption:
        fig_block.append(r"\par\vspace{8pt}")
        fig_block.append(r"{\footnotesize\raggedright\noindent\textbf{Figure " + str(n) + ".} "
                         + caption + r"\par}")

main_start = text.find("## 1. Introduction")
main_end = text.find("## Statements")
main_words = len([w for w in re.sub(r"[#*|]", " ", text[main_start:main_end]).split()
                  if re.search(r"\w", w)])

TEX = r"""
\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
\usepackage[a4paper,top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm]{geometry}
\usepackage{graphicx,longtable,array,setspace,needspace}
\usepackage{lineno}
\usepackage[hidelinks]{hyperref}
\usepackage{microtype}
\onehalfspacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}
\emergencystretch=4em
\renewcommand{\thesection}{}
\begin{document}
\begin{center}
{\large\bfseries __TITLE__}
\end{center}
\vspace{0.4em}
\begin{center}
__AUTHORS__\\[0.3em]
\small __AFFIL__\\[0.2em]
\small Correspondence: __CORR__
\end{center}
\vspace{0.4em}
\begin{center}
\small Main text __NWORDS__ words (Introduction to Conclusion); __NFIG__ figures; __NTAB__ tables; __NREF__ references.
\end{center}
\vspace{0.8em}
\linenumbers
__BODY__
__FIGURES__
\end{document}
"""

title = "Optic-nerve-predominant adverse-event reporting with ethambutol: a multi-database pharmacovigilance study with exploratory transcriptomic analysis"
#: the counts on the title page are derived, not typed: the reference count drifted from 18 to 19
#: when a citation was added, and a hard-coded number then contradicted the reference list
n_refs = len(re.findall(r"^\d{1,2}\.\s+\S", text[text.find("## References"):], re.M))
n_tables = len(re.findall(r"^Table \d+\.", text, re.M))
n_figures = len(FIG_FILES)
TEX = (TEX.replace("__TITLE__", inline(title))
          .replace("__AUTHORS__", inline("Bowen Shi (ORCID 0009-0001-6900-1779), Jing Yan, "
                                         "Zhengzheng Wu, Siyuan Yang, Yaqin Tan, "
                                         "Xuan Wang"))
          .replace("__AFFIL__", inline("Eye Hospital, China Academy of Chinese Medical Sciences, "
                                       "Beijing, China"))
          .replace("__CORR__", inline("Jing Yan, Eye Hospital, China Academy of Chinese Medical "
                                      "Sciences, 33 Lugu Road, Beijing 100040, China; "
                                      "20200121047@bucm.edu.cn"))
          .replace("__NWORDS__", f"{main_words:,}")
          .replace("__NFIG__", str(n_figures))
          .replace("__NTAB__", str(n_tables))
          .replace("__NREF__", str(n_refs))
          .replace("__BODY__", body)
          .replace("__FIGURES__", "\n".join(fig_block)))

tex_path = OUT / "Ethambutol_TADS_manuscript.tex"
tex_path.write_text(TEX, encoding="utf-8")
print(f"written {tex_path.relative_to(ROOT)}")
print(f"tables rendered: {tables_done}; main text {main_words:,} words")

#: the submission PDF is often open in a viewer, which makes xdvipdfmx fail to write it; the
#: document is compiled to a staging name and copied over when the file is free
TARGET = OUT / "Ethambutol_TADS_manuscript.pdf"
STAGE_PDF = OUT / "_build_stage.pdf"
res = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                      "-jobname=_build_stage", tex_path.name], cwd=OUT, capture_output=True,
                     text=True, encoding="utf-8", errors="replace")
if res.returncode != 0:
    print(res.stdout[-3000:])
    raise SystemExit("xelatex failed")
res = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                      "-jobname=_build_stage", tex_path.name], cwd=OUT, capture_output=True,
                     text=True, encoding="utf-8", errors="replace")
log = (OUT / "_build_stage.log").read_text(encoding="utf-8", errors="replace")
try:
    shutil.copy2(STAGE_PDF, TARGET)
    print(f"\nPDF: {TARGET}")
except PermissionError:
    print(f"\nPDF staged at {STAGE_PDF.name} - the submission copy is open in another program")
print(f"overfull: {log.count('Overfull')}   undefined: {log.count('undefined')}")
for m in re.finditer(r"Output written on .*?\((\d+) pages", log):
    print(f"pages: {m.group(1)}")
