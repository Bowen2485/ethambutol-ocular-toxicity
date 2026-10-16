# -*- coding: utf-8 -*-
"""
Build the submission-ready Word manuscripts.

    manuscript/Ethambutol_EyeTox_EN.docx   English SCI version
    manuscript/Ethambutol_EyeTox_CN.docx   Chinese translation

Layout follows the conventions of the target journals: Times New Roman 12 pt
(English) / 宋体 10.5 pt with Times New Roman for Latin runs (Chinese), 1.5 line
spacing, continuous line numbering in the margin, figures embedded at their point
of first citation with numbered captions, and a numbered reference list.

Usage
    python src/build_docx.py            # both documents
    python src/build_docx.py en         # English only
    python src/build_docx.py cn         # Chinese only
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
FIG = ROOT / "figures"
TAB = ROOT / "tables"
OUT = MAN

#: Six main figures after the consolidation.  The heat map and the Venn overlap moved to
#: supplementary (Figure S1/S2) and the volcano and forest panels were merged, so the
#: supplied filenames are not the ones a "Figure n" key used to imply.  Supplementary
#: figures are deliberately absent: they belong in the supplementary file, not in the
#: manuscript body.
FIG_MAP = {
    "figure 1": "Figure1_flow.png",
    "figure 2": "Figure2_disproportionality.png",
    "figure 3": "Figure3_network.png",
    "figure 4": "Figure4_enrichment.png",
    "figure 5": "Figure5_docking.png",
    "figure 6": "Figure6_temporal.png",
    "图1": "Figure1_flow.png",
    "图2": "Figure2_disproportionality.png",
    "图3": "Figure3_network.png",
    "图4": "Figure4_enrichment.png",
    "图5": "Figure5_docking.png",
    "图6": "Figure6_temporal.png",
}


# --------------------------------------------------------------------- helpers
def set_run_font(run, latin="Times New Roman", east="Times New Roman",
                 size=12, bold=False, italic=False, colour=None):
    run.font.name = latin
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if colour:
        run.font.color.rgb = colour
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)
    rfonts.set(qn("w:eastAsia"), east)


def add_line_numbers(section) -> None:
    """Continuous line numbering in the margin (most journals require it)."""
    sect_pr = section._sectPr
    ln = sect_pr.find(qn("w:lnNumType"))
    if ln is None:
        ln = OxmlElement("w:lnNumType")
        sect_pr.append(ln)
    ln.set(qn("w:countBy"), "1")
    ln.set(qn("w:restart"), "continuous")
    ln.set(qn("w:distance"), "360")


INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`[^`]+`|\$[^$]+\$|_[^_]+_)")


def add_rich_text(doc, text: str, size: float = 12, east: str = "Times New Roman",
                  align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after: float = 6,
                  first_line_indent: float = 0.0):
    """Add a paragraph, honouring **bold**, *italic* and `code` markers."""
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    if first_line_indent:
        pf.first_line_indent = Cm(first_line_indent)
    text = text.replace("$", "").replace("\\", "")
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            set_run_font(r, size=size, bold=True, east=east)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = p.add_run(part[1:-1])
            set_run_font(r, size=size, italic=True, east=east)
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            set_run_font(r, latin="Consolas", east=east, size=size - 1)
        else:
            r = p.add_run(part)
            set_run_font(r, size=size, east=east)
    return p


def add_heading(doc, text: str, level: int, east: str = "Times New Roman"):
    sizes = {1: 15, 2: 13, 3: 12, 4: 11.5}
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(14 if level <= 2 else 10)
    pf.space_after = Pt(6)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, size=sizes.get(level, 11.5), bold=True, east=east)
    return p


def add_table_from_csv(doc, csv_path: Path, caption: str | None = None,
                       max_rows: int = 40, east: str = "Times New Roman",
                       size: float = 9):
    import pandas as pd
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    if df.empty:
        return
    #: A long table is truncated for the Word manuscript, and the truncation is stated in the
    #: caption rather than left silent.  Table 8 reached 60 rows when the MR panel was completed;
    #: an unqualified head() there would have printed half the panel with nothing to say so.
    total = len(df)
    df = df.head(max_rows)
    if caption:
        if total > max_rows:
            caption = (f"{caption}  (Showing the first {max_rows} of {total} rows; the complete "
                       f"table is in {csv_path.name}.)")
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(caption)
        set_run_font(r, size=size + 1, bold=True, east=east)
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(str(col))
        set_run_font(r, size=size, bold=True, east=east)
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for i, col in enumerate(df.columns):
            v = row[col]
            s = "" if pd.isna(v) else (f"{v:.4g}" if isinstance(v, float) else str(v))
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(s)
            set_run_font(r, size=size, east=east)
    doc.add_paragraph()


def embed_figures(doc, text: str, east: str = "Times New Roman",
                  size: float = 10):
    """Place each figure after the paragraph that first mentions it."""
    done: set[str] = set()
    for m in re.finditer(r"(Figure\s*\d{1,2}|图\s*\d{1,2})", text):
        key = m.group(0).lower().replace(" ", "")
        if key in done:
            continue
        done.add(key)
        fname = FIG_MAP.get(key) or FIG_MAP.get(m.group(0).lower())
        if not fname or not (FIG / fname).exists():
            continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(str(FIG / fname), width=Cm(15.5))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cap.paragraph_format.space_after = Pt(10)
        r = cap.add_run(f"{m.group(0)}. See the figure legend in the text.")
        set_run_font(r, size=size - 1, italic=True, east=east)


def add_page_numbers(section, latin="Times New Roman", east="Times New Roman"):
    footer = section.footer
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_run_font(run, size=9, east=east)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._element.append(fld)


# ------------------------------------------------------------------ documents
def build(md_path: Path, out_path: Path, title: str, east_font: str,
          base_size: float, figure_after: bool = True) -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(base_size)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), east_font)

    sec = doc.sections[0]
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    add_line_numbers(sec)
    add_page_numbers(sec, east=east_font)

    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # running head
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run("Running head: Ethambutol ocular toxicity")
    set_run_font(r, size=9, italic=True, east=east_font)

    # title block
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run(title)
    set_run_font(r, size=base_size + 3, bold=True, east=east_font)

    i = 0
    in_code = False
    in_legends = False
    while i < len(lines):
        ln = lines[i].rstrip()
        stripped = ln.strip()

        # once the figure-legend list starts, stop embedding images: the legends
        # name every figure again, which would insert each one a second time
        if stripped.startswith("## 图表清单") or stripped.startswith("## Figure legends"):
            in_legends = True
        if stripped.startswith("###") and in_legends:
            in_legends = False

        if stripped.startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(ln)
            set_run_font(r, latin="Consolas", east=east_font, size=base_size - 1.5)
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        # skip the document's own title/meta scaffolding: the title block is
        # written by this builder, so repeating it here would duplicate it
        if stripped.startswith("# ") or stripped.startswith("Short running title"):
            i += 1
            continue
        if stripped.lower().startswith("**running head"):
            i += 1
            continue
        if stripped in ("---", "***"):
            i += 1
            continue

        m = re.match(r"^(#{2,5})\s+(.*)$", stripped)
        if m:
            add_heading(doc, m.group(2), len(m.group(1)) - 1, east=east_font)
            i += 1
            continue

        # markdown tables
        if stripped.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = [[c.strip() for c in r0.strip("|").split("|")]
                    for r0 in block if not re.match(r"^\|[\s\-:|]+\|$", r0)]
            if rows:
                t = doc.add_table(rows=0, cols=len(rows[0]))
                t.style = "Table Grid"
                for ri, row in enumerate(rows):
                    cells = t.add_row().cells
                    for ci, val in enumerate(row[:len(cells)]):
                        cells[ci].text = ""
                        run = cells[ci].paragraphs[0].add_run(
                            val.replace("**", "").replace("*", ""))
                        set_run_font(run, size=base_size - 2.5,
                                     bold=(ri == 0), east=east_font)
                doc.add_paragraph()
            continue

        # bullet / numbered lists
        mb = re.match(r"^([-*])\s+(.*)$", stripped)
        mn = re.match(r"^(\d+)[.)]\s+(.*)$", stripped)
        if mb:
            add_rich_text(doc, "•  " + mb.group(2), size=base_size, east=east_font,
                          align=WD_ALIGN_PARAGRAPH.LEFT)
            i += 1
            continue
        if mn:
            add_rich_text(doc, f"{mn.group(1)}.  {mn.group(2)}", size=base_size,
                          east=east_font, align=WD_ALIGN_PARAGRAPH.LEFT)
            i += 1
            continue

        if stripped.startswith("**Keywords"):
            add_rich_text(doc, stripped, size=base_size, east=east_font)
            i += 1
            continue

        add_rich_text(doc, stripped, size=base_size, east=east_font)
        if (figure_after and not in_legends
                and re.search(r"(Figure\s*\d|图\s*\d)", stripped)):
            embed_figures(doc, stripped, east=east_font, size=base_size)
        i += 1

    doc.save(out_path)
    print(f"[ok] {out_path.name}: {out_path.stat().st_size/1024:.0f} KB")


# key tables to embed in the manuscript, in the order the text cites them.
#: Six main tables after the consolidation.  The panel-description tables, the time-to-
#: onset table, the hub and enrichment tables, the docking matrix and the adequacy table
#: all moved to supplementary material, so they are no longer appended here; paths are
#: relative to the project root because Table 6 lives under results/ rather than tables/.
KEY_TABLES = [
    ("tables/Table1_cohort.csv",
     "Table 1. Study population: de-duplicated FAERS cases by exposure."),
    ("tables/Table2b_signals_strict.csv",
     "Table 2. Strict ocular signals for ethambutol (ROR lower 95% CI > 1, PRR >= 2, "
     "chi-square >= 4, IC025 > 0, >= 3 cases; Benjamini-Hochberg q < 0.05)."),
    ("tables/Table4_logistic.csv",
     "Table 3. Multivariable logistic regression for any ocular adverse event."),
    ("tables/Table8_mr.csv",
     "Table 4. Two-sample Mendelian randomisation estimates for the primary outcome, "
     "optic neuritis, one row per exposure."),
    ("tables/Table9_robustness.csv",
     "Table 5. Robustness of the disproportionality conclusions across four "
     "specifications."),
    ("results/faers_subgroups.csv",
     "Table 6. Optic-nerve odds ratio by patient subgroup."),
    ("results/faers_subgroup_contrasts.csv",
     "Table 6 (continued). Contrasts between strata."),
]

CN_TABLE_TITLES = {
    "tables/Table1_cohort.csv": "表1 研究人群：FAERS 去重后各暴露病例数",
    "tables/Table2b_signals_strict.csv": "表2 乙胺丁醇的严格眼部信号",
    "tables/Table4_logistic.csv": "表3 多因素 logistic 回归（因变量：任一眼部不良事件）",
    "tables/Table8_mr.csv": "表4 两样本孟德尔随机化估计：主要结局（视神经炎），每个暴露一行",
    "tables/Table9_robustness.csv": "表5 四情景稳健性检验",
    "results/faers_subgroups.csv": "表6 按患者亚组的视神经比值比",
    "results/faers_subgroup_contrasts.csv": "表6（续）层间对比",
}


def append_tables(doc_path: Path, east: str, size: float,
                  cn: bool = False) -> None:
    """Append the key result tables to an already-built manuscript."""
    doc = Document(doc_path)
    add_heading(doc, "表格" if cn else "Tables", 1, east=east)
    for fname, en_caption in KEY_TABLES:
        p = ROOT / fname
        if not p.exists():
            continue
        caption = CN_TABLE_TITLES.get(fname, en_caption) if cn else en_caption
        #: Every row is printed.  The limit was 30, which silently halved Tables 5, 6, 9 and -
        #: once the MR panel was completed - Table 8; a submission table that reads "first 30 of
        #: 60 rows" is worse than a long one, and the caption now discloses any cut that the
        #: limit does impose, so the limit is set above the longest table in the set.
        add_table_from_csv(doc, p, caption, max_rows=80, east=east,
                           size=size - 2)
    doc.save(doc_path)
    print(f"[ok] tables appended to {doc_path.name}")


def main() -> int:
    which = sys.argv[1:] or ["en", "cn"]
    if "en" in which:
        build(
            MAN / "Ethambutol_EyeTox_EN_full.md",
            OUT / "Ethambutol_EyeTox_EN.docx",
            "Ocular toxicity of ethambutol in 20.3 million FAERS cases: "
            "pharmacovigilance, network toxicology, molecular docking and "
            "genetic interrogation",
            east_font="Times New Roman", base_size=12)
        append_tables(OUT / "Ethambutol_EyeTox_EN.docx", "Times New Roman", 12,
                      cn=False)
    if "cn" in which:
        build(
            MAN / "Ethambutol_EyeTox_CN_full.md",
            OUT / "Ethambutol_EyeTox_CN_中文版.docx",
            "乙胺丁醇眼毒性：2 033 万例 FAERS 病例中的药物警戒、"
            "网络毒理学、分子对接与遗传学考察",
            east_font="宋体", base_size=10.5)
        append_tables(OUT / "Ethambutol_EyeTox_CN_中文版.docx", "宋体", 10.5,
                      cn=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
