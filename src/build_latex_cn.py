# -*- coding: utf-8 -*-
"""Build a Chinese PDF of the manuscript with XeLaTeX.

Why a separate builder rather than a flag on build_latex.py
    The English build targets the Frontiers class under pdflatex.  Chinese needs a CJK
    engine, and the Frontiers class is not written for one, so this produces a companion
    document with ctexart instead.  It is a reference translation, not the submission
    file, so it is typeset for reading rather than for the journal's layout.

    Everything is Unicode-capable here, which removes most of build_latex.py's work: the
    accented letters and symbols that had to be folded into commands for pdflatex pass
    through untouched.  Only the super/subscript digits are still folded, because the
    CJK fonts do not carry those glyphs - log2 and log10 would otherwise print with a
    blank box where the digit belongs.

Outputs
    submission/Ethambutol_EyeTox_CN.tex      the generated source
    submission/Ethambutol_EyeTox_CN.pdf      the compiled document
    submission/build_cn/                     scratch: aux files, logs, copied figures

    The scratch directory sits under submission/build_cn so that the existing
    .gitignore rule for submission/build_*/ keeps every intermediate file out of the
    repository while the two deliverables are published beside the English ones.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"
BUILD = ROOT / "submission" / "build_cn"
DEST = ROOT / "submission"
FIGS = ROOT / "figures"

FIG_FILES = {
    "1": "Figure1_flow", "2": "Figure2_disproportionality", "3": "Figure3_network",
    "4": "Figure4_enrichment", "5": "Figure5_docking", "6": "Figure6_temporal",
    "S1": "FigureS1_heatmap", "S2": "FigureS2_venn",
}

#: the CJK fonts lack these glyphs, so they become maths before anything else runs
SUPERSCRIPT = {
    "\u2070": "0", "\u00b9": "1", "\u00b2": "2", "\u00b3": "3", "\u2074": "4",
    "\u2075": "5", "\u2076": "6", "\u2077": "7", "\u2078": "8", "\u2079": "9",
    "\u207a": "+", "\u207b": "-",
}
SUBSCRIPT = {
    "\u2080": "0", "\u2081": "1", "\u2082": "2", "\u2083": "3", "\u2084": "4",
    "\u2085": "5", "\u2086": "6", "\u2087": "7", "\u2088": "8", "\u2089": "9",
    "\u208a": "+", "\u208b": "-",
}


SUP_RUN = re.compile("[" + re.escape("".join(SUPERSCRIPT)) + "]+")
SUB_RUN = re.compile("[" + re.escape("".join(SUBSCRIPT)) + "]+")


def escape(s: str) -> str:
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in (("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    return s


def inline(s: str) -> str:
    """Markdown emphasis, code spans and super/subscripts.

    Every replacement is parked behind a marker and restored after escape(), because the
    replacements are LaTeX.  An earlier version folded the super/subscripts straight into
    the string and then escaped, which turned the maths delimiters themselves into text:
    the affiliations printed as a literal "$^{1}$".
    """
    store: list[str] = []

    def park(latex: str) -> str:
        store.append(latex)
        return f"\x00X{len(store)-1}\x00"

    def wrap(pattern: str, template: str):
        return re.sub(pattern, lambda m: park(template.format(escape(m.group(1)))), s)

    # super/subscripts first, so the digits become one maths group
    s = SUP_RUN.sub(lambda m: park("$^{" + "".join(SUPERSCRIPT[c] for c in m.group(0)) + "}$"), s)
    s = SUB_RUN.sub(lambda m: park("$_{" + "".join(SUBSCRIPT[c] for c in m.group(0)) + "}$"), s)
    s = wrap(r"`([^`]+)`", r"\texttt{{{}}}")
    s = wrap(r"\*\*([^*]+)\*\*", r"\textbf{{{}}}")
    s = wrap(r"\*([^*]+)\*", r"\textit{{{}}}")

    s = escape(s)
    # A formatted run followed by a space keeps a visible space.  In CJK text a literal
    # space between two CJK characters is dropped, which ran the abstract labels straight
    # into the sentence ("目的乙胺丁醇是...").  The placeholder is matched as a group and
    # referred to as \1: putting its literal NUL bytes in the replacement is rejected by
    # re as a bad escape.
    s = re.sub(r"(\x00X\d+\x00) ", r"\1\\ ", s)
    return re.sub(r"\x00X(\d+)\x00", lambda m: store[int(m.group(1))], s)


def split_row(line: str) -> list[str]:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"[\s|:-]+", line.strip())) and "-" in line


def render_table(rows: list[list[str]]) -> list[str]:
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    colspec = "".join(r"p{\dimexpr\textwidth/%d-2\tabcolsep\relax}" % ncol
                      for _ in range(ncol))
    out = [r"\begin{center}", r"\small", r"\begin{longtable}{" + colspec + "}", r"\hline"]
    for i, r in enumerate(rows):
        out.append(" & ".join(inline(c) for c in r) + r" \\")
        if i == 0:
            out.append(r"\hline")
    out += [r"\hline", r"\end{longtable}", r"\end{center}", ""]
    return out


def figure_float(num: str, caption: str) -> list[str]:
    stem = FIG_FILES.get(num)
    if not stem or not (FIGS / f"{stem}.pdf").exists():
        return [inline(f"**图{num}** {caption}"), ""]
    width = "0.98\\linewidth" if num.startswith("S") else "0.92\\linewidth"
    out = [r"\begin{figure}[htbp]", r"\centering",
           rf"\includegraphics[width={width}]{{{stem}}}"]
    if num.startswith("S"):
        # The supplementary figures come after the six main ones, so LaTeX would number
        # them 7 and 8 while the text refers to them as S1 and S2.  The printed number is
        # forced to the label the body actually uses.
        out += [r"\begingroup",
                r"\renewcommand{\thefigure}{" + num + "}",
                r"\caption{" + inline(caption) + r"}",
                r"\endgroup"]
    else:
        out += [r"\caption{" + inline(caption) + r"}"]
    out += [r"\end{figure}", ""]
    return out


def main() -> int:
    lines = SRC.read_text(encoding="utf-8").split("\n")
    BUILD.mkdir(parents=True, exist_ok=True)
    for p in FIGS.glob("Figure*.pdf"):
        shutil.copy2(p, BUILD / p.name)

    body: list[str] = []
    title = "乙胺丁醇眼毒性"
    author_line = affil_line = corresp_line = ""
    in_abstract = False
    in_figures = False
    table_buf: list[list[str]] = []
    para_buf: list[str] = []

    def flush_para() -> None:
        if para_buf:
            body.append(inline(" ".join(para_buf)))
            body.append("")
            para_buf.clear()

    def flush_table() -> None:
        if table_buf:
            body.extend(render_table(table_buf))
            table_buf.clear()

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        # ---- pipe tables (collected across consecutive table lines)
        if stripped.startswith("|"):
            flush_para()
            if not is_separator(stripped):
                table_buf.append(split_row(stripped))
            continue
        flush_table()

        if not stripped:
            flush_para()
            continue

        if stripped == "---":
            flush_para()
            continue

        # ---- title / authorship.  The author line goes in \author{}; the affiliation and
        # the corresponding author do not fit there - a long affiliation in \author{}
        # overflowed the right margin - so they are set as a block after \maketitle.
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue
        if stripped.startswith("**作者**"):
            author_line = inline(stripped.replace("**作者**", "").strip())
            continue
        if stripped.startswith("**单位**"):
            affil_line = inline(stripped.replace("**单位**", "").strip())
            continue
        if stripped.startswith("**通讯作者**"):
            corresp_line = inline("通讯作者：" + stripped.replace("**通讯作者**", "").strip())
            continue

        # ---- abstract block
        if stripped.startswith("**摘要**"):
            flush_para()
            body.append(r"\begin{abstract}")
            in_abstract = True
            continue
        if stripped.startswith("**关键词**"):
            flush_para()
            body.append(r"\end{abstract}")
            body.append("")
            body.append(r"\noindent " + inline(stripped))
            body.append("")
            in_abstract = False
            continue

        # ---- headings.  The source numbers its own sections ("## 1 引言", "### 3.2c ...")
        # and the text cross-references them by that number ("原因见 3.4b 节"), so the
        # source numbers are printed and LaTeX's own numbering is switched off in the
        # preamble.  Letting LaTeX number them printed "3.4 3.2c ..." and would have
        # broken every in-text section reference.
        if stripped.startswith("### "):
            flush_para()
            body += [r"\subsection{" + inline(stripped[4:].strip()) + "}", ""]
            continue
        if stripped.startswith("## "):
            flush_para()
            name = stripped[3:].strip()
            in_figures = name.startswith("图表清单")
            body += [r"\section{" + inline(name) + "}", ""]
            continue

        # ---- figure and table captions in the list
        m = re.match(r"^\*\*(图S?\d+)\*\*\s*(.*)$", stripped)
        if m and in_figures:
            flush_para()
            body.extend(figure_float(m.group(1).lstrip("图"), m.group(2)))
            continue
        if re.match(r"^\*\*表S?\d+\*\*", stripped) and in_figures:
            flush_para()
            body += [r"\noindent " + inline(stripped), ""]
            continue

        para_buf.append(stripped)

    flush_para()
    flush_table()
    if in_abstract:
        body.append(r"\end{abstract}")

    tex = "\n".join([
        r"% Generated by src/build_latex_cn.py from manuscript/Ethambutol_EyeTox_CN_full.md",
        r"\documentclass[UTF8,fontset=windows,11pt]{ctexart}",
        r"\usepackage[a4paper,margin=2.4cm]{geometry}",
        r"\usepackage{graphicx,longtable,array}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{newunicodechar}",
        r"\usepackage{pifont}",
        r"\usepackage{setspace}",
        r"\usepackage[hidelinks]{hyperref}",
        # Eleven characters have no glyph in either the Latin main font or the CJK fonts,
        # and would otherwise print as blank boxes: the maths relations, the Greek letters
        # of the pathway names, the Roman numeral of type II diabetes, and the circled
        # digits used to enumerate the robustness specifications.  Mapping them
        # explicitly is deterministic, unlike leaving it to a font fallback.
        r"\newunicodechar{" + "\u2265" + r"}{\ensuremath{\geq}}",
        r"\newunicodechar{" + "\u2264" + r"}{\ensuremath{\leq}}",
        r"\newunicodechar{" + "\u03b1" + r"}{\ensuremath{\alpha}}",
        r"\newunicodechar{" + "\u03b2" + r"}{\ensuremath{\beta}}",
        r"\newunicodechar{" + "\u03b3" + r"}{\ensuremath{\gamma}}",
        r"\newunicodechar{" + "\u03c7" + r"}{\ensuremath{\chi}}",
        r"\newunicodechar{" + "\u2161" + r"}{II}",
        r"\newunicodechar{" + "\u2460" + r"}{\ding{172}}",
        r"\newunicodechar{" + "\u2461" + r"}{\ding{173}}",
        r"\newunicodechar{" + "\u2462" + r"}{\ding{174}}",
        r"\newunicodechar{" + "\u2463" + r"}{\ding{175}}",
        r"\onehalfspacing",
        # The manuscript carries its own section numbers and refers to them in the text,
        # so LaTeX must not add a second set.
        r"\setcounter{secnumdepth}{-2}",
        r"\setlength{\parindent}{2em}",
        r"\setlength{\parskip}{0.35em}",
        r"\title{" + inline(title) + "}",
        r"\author{" + author_line + "}",
        r"\date{}",
        "",
        r"\begin{document}",
        r"\maketitle",
        "",
        r"\begin{center}\small",
        affil_line + r"\\",
        corresp_line,
        r"\end{center}",
        r"\vspace{1.2em}",
        "",
        "\n".join(body),
        "",
        r"\end{document}",
        "",
    ])

    tex_path = BUILD / "Ethambutol_EyeTox_CN.tex"
    tex_path.write_text(tex, encoding="utf-8")
    print(f"  written: {tex_path.relative_to(ROOT)}  ({len(tex):,} chars)")

    # Remove the previous PDF and latexmk's state before building.  latexmk refuses to
    # re-run after a failure and leaves the old PDF in place, and an earlier version of
    # this script reported "PDF produced" from that stale file - a broken build looked
    # like a good one.  Deleting first makes the check below meaningful.
    pdf = BUILD / "Ethambutol_EyeTox_CN.pdf"
    for stale in (pdf, BUILD / "Ethambutol_EyeTox_CN.fdb_latexmk"):
        if stale.exists():
            stale.unlink()
    started = time.time()

    print("  compiling with xelatex ...")
    last = None
    for _ in range(3):
        last = subprocess.run(
            ["latexmk", "-xelatex", "-interaction=nonstopmode", "-file-line-error",
             tex_path.name],
            cwd=BUILD, capture_output=True, text=True, encoding="utf-8", errors="replace")

    log = BUILD / "Ethambutol_EyeTox_CN.log"
    if log.exists():
        text = log.read_text(encoding="utf-8", errors="replace")
        missing = re.findall(r"Missing character: There is no (.+?) in font", text)
        print(f"  missing glyphs: {len(missing)}"
              + (f"  (e.g. {sorted(set(missing))[:5]})" if missing else ""))
        errs = re.findall(r"^!.*$", text, flags=re.M)
        print(f"  TeX errors    : {len(errs)}" + (f"  {errs[:3]}" if errs else ""))

    fresh = pdf.exists() and pdf.stat().st_mtime >= started - 1
    if fresh:
        shutil.copy2(tex_path, DEST / "Ethambutol_EyeTox_CN.tex")
        shutil.copy2(pdf, DEST / "Ethambutol_EyeTox_CN.pdf")
        print(f"  PDF: submission/Ethambutol_EyeTox_CN.pdf  "
              f"({pdf.stat().st_size/1024:.0f} KB)")
        return 0

    print("  NO FRESH PDF PRODUCED")
    if last is not None:
        print("  latexmk exit:", last.returncode)
        print((last.stdout or "")[-1200:])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
