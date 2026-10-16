# -*- coding: utf-8 -*-
"""
Convert the Frontiers manuscript from Markdown to LaTeX.

The target is the official Frontiers template, whose structure was read from the
distributed files rather than recalled:

    \\documentclass[utf8]{FrontiersinVancouver}   Frontiers in Pharmacology is numbered
    \\usepackage[numbers,round]{natbib}           loaded by the class
    \\citep{key}                                  the citation command it expects
    \\bibliographystyle{Frontiers-Vancouver}
    \\def\\firstAuthorLast, \\def\\Authors, \\def\\Address, \\def\\corrAuthor, \\def\\corrEmail
    \\section{} in the preamble of the manuscript, \\subsection{} below it
    \\begin{abstract} ... \\section{Background} ... \\end{abstract}   a structured
        abstract, because the class makes \\section run-in inside that environment
    \\section*{Conflict of Interest Statement} and the other starred declarations
    tables placed at the end, figures referenced but supplied as separate files

Conversion rules
    ## / ### become \\section and \\subsection
    **bold** and *italic* become \\textbf and \\textit
    <sub>x</sub> becomes $_{x}$, which is how the template writes subscripts
    10^-7 becomes $10^{-7}$
    [12] and [3-5] become \\citep{...} using submission/citation_map.json
    | a | b | rows become tabular environments
    LaTeX specials are escaped, but not inside maths or inside a \\citep argument
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
OUT = ROOT / "submission"
OUT.mkdir(parents=True, exist_ok=True)

CMAP: dict[str, str] = json.loads((OUT / "citation_map.json").read_text(encoding="utf-8"))
LINES = SRC.read_text(encoding="utf-8").splitlines()


# ---------------------------------------------------------------- front matter
def field(label: str) -> str:
    """Return the value of a **Label:** line, searching the whole head of the file.

    The first line of the manuscript is also a '# ' heading - it is the truncated running
    title - so a scan that accepts any top-level heading picks the wrong one.  The
    explicit labels are used instead.
    """
    for ln in LINES[:40]:
        if ln.startswith(f"**{label}"):
            return ln.split("**", 2)[2].strip().lstrip(":").strip()
    return ""


running_head = field("Running head") or "Ethambutol ocular toxicity"
title_raw = ""
for i, ln in enumerate(LINES[:30]):
    if ln.startswith("## Title"):
        for j in range(i + 1, min(i + 12, len(LINES))):
            cand = LINES[j].strip()
            if cand and not cand.startswith("#") and cand != "---":
                title_raw = cand.strip("*").strip()
                break
        break

authors_raw = field("Authors")
affil_raw = field("Affiliation")
corr_raw = field("Corresponding author")

# "Bowen Shi¹, Jing Yan¹*, ..."  ->  "Bowen Shi$^{1,*}$, Jing Yan$^{1}$, ..."
SUP = {"¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5"}


def convert_author_block(s: str) -> tuple[str, str]:
    """Return (author list for \\Authors, first author's surname for the running head)."""
    s = s.replace(" and ", ", ")
    out = []
    for part in [p.strip() for p in s.split(",") if p.strip()]:
        marks = "".join(SUP[c] for c in part if c in SUP)
        name = "".join(c for c in part if c not in SUP).strip()
        star = "*" in name
        name = name.replace("*", "").strip()
        if marks:
            tag = marks + (",*" if star else "")
            out.append(f"{name}\\,$^{{{tag}}}$")
        else:
            out.append(name)
    first = out[0] if out else "First Author"
    surname = first.split("\\,")[0].split()[-1] if first.split() else "Author"
    return ", ".join(out), surname


authors_tex, first_surname = convert_author_block(authors_raw)
corr_name = corr_raw.split(",")[0].strip() if corr_raw else "Corresponding Author"
email_m = re.search(r"[\w.\-]+@[\w.\-]+", corr_raw or "")
email = email_m.group(0) if email_m else "email@example.edu"

# the affiliation line: keep the street address for \corrAuthor, trim for \Address
affil_tex = affil_raw.replace("¹", "").strip()
affil_short = affil_tex
street_m = re.search(r",\s*\d+.*$", affil_short)
street = street_m.group(0).strip(" ,") if street_m else affil_short
affil_short = affil_short[: street_m.start()].strip() if street_m else affil_short


# ---------------------------------------------------------------- inline conversion
def protect_math(s: str) -> tuple[str, list[str]]:
    """Lift $...$ spans out so the escaper cannot touch them."""
    store: list[str] = []

    def take(m):
        store.append(m.group(0))
        return f"\x00M{len(store)-1}\x00"

    return re.sub(r"\$[^$]+\$", take, s), store


def escape_latex(s: str) -> str:
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}")):
        s = s.replace(a, b)
    return s


#: Non-ASCII characters that pdflatex cannot typeset as they stand.
#:
#: The class declares utf8, but it does not load inputenc with a font that carries these
#: glyphs, and no TeX distribution is available here to test compilations.  Rather than
#: depend on xeCJK - which is not guaranteed to be installed and would fail under
#: pdflatex, the engine Overleaf uses by default - the symbols are written as commands and
#: the Japanese term list is romanised.  The romanisation is stated as such in the text so
#: that a reader is not misled about what the source data contain.
UNICODE_MAP = {
    "\u2013": "--",            # en dash
    "\u2014": "---",           # em dash
    "\u2212": "$-$",           # minus sign
    "\u00b1": r"$\pm$",        # plus-minus
    "\u00d7": r"$\times$",     # multiplication
    "\u00f7": r"$\div$",
    "\u2265": r"$\geq$",
    "\u2264": r"$\leq$",
    "\u2248": r"$\approx$",
    "\u2192": r"$\rightarrow$",
    "\u2190": r"$\leftarrow$",
    "\u00b0": r"$^{\circ}$",
    "\u00b2": r"$^{2}$",       # superscript two, as in chi-squared
    "\u00b3": r"$^{3}$",
    "\u207b": r"$^{-}$",
    "\u2078": r"$^{8}$",
    "\u2077": r"$^{7}$",
    "\u00c5": r"\AA{}",        # angstrom sign
    "\u00e5": r"\aa{}",
    "\u00b5": r"\textmu{}",    # micro sign (needs textcomp, loaded by the class)
    "\u03bc": r"$\mu$",
    "\u03c7": r"$\chi$",       # chi, as in the chi-squared test
    "\u03b1": r"$\alpha$",
    "\u03b2": r"$\beta$",
    "\u2026": r"\ldots{}",
    "\u00a0": "~",
    # Japanese terms quoted from MedDRA/J, romanised so that the file stays English-only
    "\u8996\u795e\u7d4c\u75c7": "shishinkeisyou (optic neuropathy)",
    "\u8996\u795e\u7d4c\u708e": "shishinkei-en (optic neuritis)",
    "\u8996\u795e\u7d4c\u840e\u7e2e": "shishinkei-ishuku (optic atrophy)",
    "\u4e2d\u6bd2\u6027\u8996\u795e\u7d4c\u75c7": "chuudokusei shishinkeisyou "
                                                 "(toxic optic neuropathy)",
    "\u8996\u529b\u4f4e\u4e0b": "shiryoku-teika (visual acuity reduced)",
    "\u8996\u91ce\u6b20\u640d": "shiya-kesson (visual field defect)",
    "\u8272\u899a\u7570\u5e38": "shikikaku-ijou (colour vision deficiency)",
    "\u767d\u5185\u969c": "hakunaishou (cataract)",
    "\u7dd1\u5185\u969c": "ryokunaishou (glaucoma)",
    "\u30c9\u30e9\u30a4\u30a2\u30a4": "dorai-ai (dry eye)",
    "\u88ab\u7591\u85ac": "higiyaku (suspect drug)",
}


def fold_unicode(s: str, store: list[str]) -> str:
    """Replace characters pdflatex cannot set, holding the replacements behind markers.

    The replacements are LaTeX commands or maths, so they must not pass through the
    escaper.  An earlier version called this before escape_latex and returned the commands
    directly, which turned every "\\geq" into "\\textbackslash{}geq" and every brace of
    "$^{2}$" into "\\{\\}" - the same mistake that destroyed \\citep, made a second time.
    The longest keys are applied first so that a multi-character term is romanised as a
    whole and not character by character.
    """
    for k in sorted(UNICODE_MAP, key=len, reverse=True):
        if k not in s:
            continue
        repl = UNICODE_MAP[k]
        while k in s:
            store.append(repl)
            s = s.replace(k, f"\x03U{len(store)-1}\x03", 1)
    return s


def inline(s: str) -> str:
    s, math = protect_math(s)

    # Citations are converted first and then held behind placeholders, because the
    # escaper runs afterwards and would otherwise destroy the command it produced:
    # "\citep{pd2017}" came out of an earlier build as
    # "\textbackslash\{\}citep\{pd2017\}".  The placeholder uses ASCII 1, which cannot
    # occur in the source, so it cannot collide with the maths placeholders.
    cite_store: list[str] = []

    # Citation brackets.  The manuscript writes [1], [17,18] and [3-5]; the range has to
    # be alternated rather than put in a character class, because "-" inside [...] is a
    # literal hyphen and "3-5" would then be read as the three characters and not match.
    def cite(m):
        body = m.group(1)
        keys: list[str] = []
        for chunk in body.split(","):
            chunk = chunk.strip()
            rng = re.match(r"^(\d+)\s*[-\u2013]\s*(\d+)$", chunk)
            if rng:
                lo, hi = int(rng.group(1)), int(rng.group(2))
                for k in range(lo, hi + 1):
                    if str(k) in CMAP:
                        keys.append(CMAP[str(k)])
            elif chunk.isdigit() and chunk in CMAP:
                keys.append(CMAP[chunk])
        if not keys:
            return m.group(0)
        seen, uniq = set(), []
        for k in keys:
            if k not in seen:
                seen.add(k)
                uniq.append(k)
        cite_store.append(r"\citep{" + ",".join(uniq) + "}")
        return f"\x01C{len(cite_store)-1}\x01"

    s = re.sub(r"\[(\d+(?:\s*[,\u2013-]\s*\d+)*)\]", cite, s)

    # HTML sub- and superscripts.  These must also be held behind placeholders, because
    # the escaper runs next and turns the braces of "$_{D}$" into "\{D\}"; an earlier
    # build produced "n$_{\{D\}}$" in Table 1 for exactly that reason.
    script_store: list[str] = []
    uni_store: list[str] = []

    def sub(m):
        script_store.append("$_{" + m.group(1) + "}$")
        return f"\x02S{len(script_store)-1}\x02"

    def sup(m):
        script_store.append("$^{" + m.group(1) + "}$")
        return f"\x02S{len(script_store)-1}\x02"

    s = re.sub(r"<sub>(.*?)</sub>", sub, s)
    s = re.sub(r"<sup>(.*?)</sup>", sup, s)

    # Characters pdflatex cannot set are folded to commands or romanised, and the
    # replacements are held behind markers so that the escaper cannot damage them.
    s = fold_unicode(s, uni_store)

    s = escape_latex(s)

    # emphasis
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s, flags=re.S)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\\textit{\1}", s)
    s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)

    # powers that were written in plain text
    s = re.sub(r"10\^\{?(-?\d+)\}?", r"$10^{\1}$", s)

    # a few typographic symbols the class handles natively
    s = s.replace("\u2192", r"$\rightarrow$").replace("\u00d7", r"$\times$")

    # restore the protected commands: citations, scripts, folded unicode, then maths
    for i, c in enumerate(cite_store):
        s = s.replace(f"\x01C{i}\x01", c)
    for i, c in enumerate(script_store):
        s = s.replace(f"\x02S{i}\x02", c)
    for i, c in enumerate(uni_store):
        s = s.replace(f"\x03U{i}\x03", c)
    for i, m in enumerate(math):
        s = s.replace(f"\x00M{i}\x00", m)
    return s


# ---------------------------------------------------------------- table conversion
def is_row(ln: str) -> bool:
    return ln.strip().startswith("|") and ln.strip().endswith("|")


def convert_table(block: list[str]) -> list[str]:
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r if c)]
    if not rows:
        return []
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    # The Frontiers class sets a text width of 42pc and is typeset in two columns, so an
    # ordinary table gets roughly half of that and a wider one is clipped rather than
    # erroring.  The class defines table* as a double-column float, so tables of five or
    # more columns use it.  The preprint built from this file is one column, which is why
    # the problem would not be visible locally.
    env = "table*" if ncol >= 5 else "table"
    out = [r"\begin{" + env + "}[htbp]", r"\centering",
           r"\begin{tabular}{" + "l" * ncol + "}", r"\hline"]
    for i, r in enumerate(rows):
        out.append(" & ".join(inline(c) for c in r) + r" \\")
        if i == 0:
            out.append(r"\hline")
    out += [r"\hline", r"\end{tabular}", r"\end{" + env + "}", ""]
    return out


# ---------------------------------------------------------------- walk the document
body_start = next((i for i, ln in enumerate(LINES)
                   if ln.startswith("## 1. Introduction")), 107)
body_end = next((i for i, ln in enumerate(LINES)
                 if ln.startswith("## References")), len(LINES))

out: list[str] = []
i = body_start
while i < body_end:
    ln = LINES[i]
    stripped = ln.strip()

    if is_row(ln):
        block = []
        while i < body_end and is_row(LINES[i]):
            block.append(LINES[i])
            i += 1
        out += convert_table(block)
        continue

    if stripped in ("---", "***", "___"):
        i += 1
        continue

    if stripped.startswith("### "):
        out.append(r"\subsection{" + inline(stripped[4:]) + "}")
        out.append("")
        i += 1
        continue

    if stripped.startswith("## "):
        out.append(r"\section{" + inline(stripped[3:]) + "}")
        out.append("")
        i += 1
        continue

    if stripped.startswith("# "):
        out.append(r"\section{" + inline(stripped[2:]) + "}")
        out.append("")
        i += 1
        continue

    if not stripped:
        out.append("")
        i += 1
        continue

    out.append(inline(ln))
    i += 1

body_tex = "\n".join(out)
body_tex = re.sub(r"\n{3,}", "\n\n", body_tex)


# ---------------------------------------------------------------- abstract
abs_start = next((i for i, ln in enumerate(LINES) if ln.startswith("## Abstract")), 23)
abs_end = next((i for i, ln in enumerate(LINES) if ln.startswith("**Keywords")), 100)
abs_lines = [l for l in LINES[abs_start + 1:abs_end] if l.strip()]
abs_parts: list[str] = []
for l in abs_lines:
    m = re.match(r"^\*\*(.+?)\.\*\*\s*(.*)$", l.strip())
    if m:
        abs_parts.append(r"\section{" + m.group(1) + "} " + inline(m.group(2)))
    else:
        abs_parts.append(inline(l.strip()))
kw_line = LINES[abs_end] if abs_end < len(LINES) else ""
kw = re.sub(r"^\*\*Keywords\.\*\*\s*", "", kw_line).strip()
kw = kw.replace(";", ",")
keywords = [k.strip() for k in kw.split(",") if k.strip()][:8]

# ---------------------------------------------------------------- figure captions
# The template allows the figures to be embedded, in which case they are placed after the
# bibliography with their captions.  They are also uploaded separately, because Frontiers
# requires the individual files regardless.
FIG_SRC = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
fig_caps: dict[str, str] = {}
_fm = FIG_SRC.read_text(encoding="utf-8")
for m in re.finditer(r"\*\*Figure (\d)\*\*\s*(.+?)(?=\n\*\*|\Z)", _fm, re.S):
    fig_caps[m.group(1)] = " ".join(m.group(2).split())

FIG_FILES = {
    "1": "Figure1_flow.pdf", "2": "Figure2_volcano.pdf", "3": "Figure3_heatmap.pdf",
    "4": "Figure4_forest.pdf", "5": "Figure5_network.pdf",
    "6": "Figure6_enrichment.pdf", "7": "Figure7_docking.pdf",
    "8": "Figure8_tto.pdf", "9": "Figure9_trend.pdf",
}
fig_block: list[str] = []
for n in sorted(FIG_FILES):
    cap = fig_caps.get(n, "")
    fig_block.append(r"\begin{figure}[htbp]")
    fig_block.append(r"\centering")
    fig_block.append(r"\includegraphics[width=\linewidth]{" + FIG_FILES[n][:-4] + "}")
    fig_block.append(r"\caption{" + inline(cap) + "}")
    fig_block.append(r"\label{fig:" + n + "}")
    fig_block.append(r"\end{figure}")
    fig_block.append("")
figures_tex = "\n".join(fig_block)

# ---------------------------------------------------------------- emit
TEX = f"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Ocular toxicity of ethambutol
% Prepared for Frontiers in Pharmacology using the official Frontiers LaTeX class.
%
% When submitting, upload: this .tex file, the compiled PDF, references.bib, and
% every figure file named below.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\documentclass[utf8]{{FrontiersinVancouver}}
% Vancouver (numbered) is the style Frontiers in Pharmacology uses.

\\usepackage{{url,hyperref,lineno,microtype,subcaption}}
\\usepackage[onehalfspacing]{{setspace}}

\\linenumbers

\\def\\keyFont{{\\fontsize{{8}}{{11}}\\helveticabold }}
\\def\\firstAuthorLast{{{first_surname} {{et~al.}}}}
\\def\\Authors{{{authors_tex}}}
\\def\\Address{{$^{{1}}${affil_short}, China}}
\\def\\corrAuthor{{{corr_name}, {street}}}
\\def\\corrEmail{{{email}}}

\\begin{{document}}
\\onecolumn
\\firstpage{{1}}

\\title[Ethambutol ocular toxicity in 20.3 million FAERS cases]{{{inline(title_raw)}}}

\\author[\\firstAuthorLast ]{{\\Authors}}
\\address{{}}
\\correspondance{{}}

\\extraAuth{{}}

\\maketitle

\\begin{{abstract}}
{chr(10).join(abs_parts)}

\\tiny
 \\keyFont{{ \\section{{Keywords:}} {", ".join(keywords)}}}
\\end{{abstract}}

{body_tex}

\\section*{{Conflict of Interest Statement}}

The authors declare that the research was conducted in the absence of any commercial
or financial relationships that could be construed as a potential conflict of interest.

\\section*{{Author Contributions}}

BS: Conceptualization, Methodology, Software, Validation, Formal analysis, Resources,
Data curation, Writing -- original draft. YT: Investigation. SY: Writing -- review and
editing. XW: Visualization. ZW: Supervision. JY: Project administration, Funding
acquisition, Supervision. All authors contributed to the article and approved the
submitted version.

\\section*{{Funding}}

This research received no specific grant from any funding agency in the public,
commercial, or not-for-profit sectors.

\\section*{{Data Availability Statement}}

The datasets analysed in this study are publicly available. FDA FAERS quarterly
extracts were obtained from the FDA FAERS file repository; JADER from the
Pharmaceuticals and Medical Devices Agency of Japan; and the FinnGen and OpenGWAS
summary statistics from their respective public portals. The derived tables, figures
and all analysis code are openly available at
\\url{{https://github.com/Bowen2485/ethambutol-ocular-toxicity}}.

\\section*{{Ethics Statement}}

This study used only publicly available, de-identified aggregate data. No
patient-identifiable information was accessed, and ethics approval was therefore not
required.

\\section*{{Supplementary Material}}

The Supplementary Material for this article is supplied separately and comprises the
STROBE and RECORD-PE checklists, the full signal panel, and the machine-readable
tables.

\\bibliographystyle{{Frontiers-Vancouver}}
\\bibliography{{references}}

\\clearpage
{figures_tex}

\\end{{document}}
"""

(OUT / "Ethambutol_EyeTox_Frontiers.tex").write_text(TEX, encoding="utf-8")

print(f"  written: submission/Ethambutol_EyeTox_Frontiers.tex")
print(f"  lines: {len(TEX.splitlines()):,}   characters: {len(TEX):,}")
print()
print("  front matter:")
print(f"      title      : {title_raw[:70]}")
print(f"      authors    : {authors_tex[:70]}")
print(f"      first last : {first_surname}")
print(f"      address    : {affil_short[:70]}")
print(f"      corr author: {corr_name}  <{email}>")
print(f"      keywords   : {len(keywords)}")
print()
print("  structural counts:")
# Counted with plain substring searches, not regexes.  A regex written as
# r"\\citep\{" looks for a literal backslash followed by "citep", which never occurs,
# and that mistake made an earlier version of this report claim zero citations in a file
# that contained eighteen.
cite_hits = body_tex.count("\\citep{")
print(f"      body_tex contains \\citep{{        : {cite_hits}")
print(f"      TEX      contains \\citep{{        : {TEX.count(chr(92) + 'citep{')}")
print(f"      TEX length {len(TEX):,}   body_tex length {len(body_tex):,}")
for needle, label in (("\\section{", "sections (numbered)"),
                      ("\\subsection{", "subsections"),
                      ("\\section*{", "starred declarations"),
                      ("\\begin{table}", "tables"),
                      ("\\begin{abstract}", "abstract env"),
                      ("\\textbf{", "bold runs"),
                      ("\\textit{", "italic runs")):
    print(f"      {label:24s} {TEX.count(needle)}")

cited: set[str] = set()
for m in re.finditer(r"\\citep\{([^}]*)\}", TEX):
    cited.update(k.strip() for k in m.group(1).split(",") if k.strip())
uncited = [k for k in CMAP.values() if k not in cited]

print()
print(f"  references in .bib: {len(CMAP)}   cited in text: {len(cited)}")
print(f"  never cited: {uncited if uncited else 'none'}")

# left-over square-bracket citations would not be typeset as references at all
leftover = re.findall(r"\[\d+(?:\s*[,\u2013-]\s*\d+)*\]", body_tex)
print(f"  unconverted [n] brackets remaining: {len(leftover)}"
      f"{'  ' + str(leftover[:6]) if leftover else ''}")
