# -*- coding: utf-8 -*-
"""Renumber figures and tables for the consolidated display set, in both languages.

Why a script
    The substitutions collide if they are done by hand: Table 2 must become Table S3
    while Table 2b becomes Table 2, and Table 4 becomes Table 3 while Table 3 becomes
    Table S9.  Every match is therefore replaced with a placeholder token first, and the
    placeholders are resolved once at the end, so no substitution can consume the output
    of another.

What changes
    Figures - the set goes from ten to six main figures plus two supplementary:
        old 3  heat map        -> Figure S1
        old 4  forest plot     -> absorbed into Figure 2 (the volcano and forest panels
                                  plot the same estimates, so they become one figure)
        old 5  network         -> Figure 3
        old 6  enrichment      -> Figure 4
        old 7  docking         -> Figure 5
        old 8  time to onset   -> Figure 6, panel A/B
        old 9  annual trend    -> Figure 6, panel C
        old 10 Venn overlap    -> Figure S2

    Tables - six in the main text, the rest supplementary:
        main  1 stays 1;  2b -> 2;  4 -> 3;  8 -> 4;  9 -> 5;  11 -> 6
        supp  2 -> S3; 2c -> S4; 2d -> S5; 2e -> S6; 2f -> S7; 2g -> S8;
              3 -> S9; 5 -> S10; 6 -> S11; 7 -> S12; 10 -> S13; 12 -> S14
        the existing S1 and S2 keep their numbers, so nothing that already refers to
        them has to move.

    Table 12 is cited in the text but had no caption and no CSV; it is given a caption
    here and backed by results/admet_ethambutol.json, which is where those five rule
    results are computed.

    Filenames are deliberately NOT rewritten: `tables/Table2b_signals_strict.csv` and the
    like keep their names, because they are artefact paths that the repository, the
    audits and the machine-readable list all refer to.  The match requires a space after
    "Table", while those paths have none, so the paths cannot be caught by accident.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
EN = MS / "Ethambutol_EyeTox_EN_full.md"
CN = MS / "Ethambutol_EyeTox_CN_full.md"
BACKUP = ROOT / ".tmp" / "backup_before_renumber"

FIG_MAP = {"3": "S1", "5": "3", "6": "4", "7": "5", "8": "6", "9": "6", "10": "S2"}
TAB_MAP = {
    "2b": "2", "4": "3", "8": "4", "9": "5", "11": "6",
    "2": "S3", "2c": "S4", "2d": "S5", "2e": "S6", "2f": "S7", "2g": "S8",
    "3": "S9", "5": "S10", "6": "S11", "7": "S12", "10": "S13", "12": "S14",
}


def renumber(text: str, fig_word: str, tab_word: str, merge_pairs: list[tuple[str, str]],
             fig_sep: str, tab_sep: str, boundary: bool = True) -> str:
    """Apply both maps to a block of text, via placeholders.

    fig_sep/tab_sep carry the language's spacing: English writes "Figure 3" and
    "Table S3", Chinese writes "图3" and "表S3" with no space.  Rebuilding the reference
    without it silently produced "Figure3", so it is a parameter rather than an
    assumption.
    """
    # the forest plot is merged into the volcano figure rather than renumbered
    for old, new in merge_pairs:
        text = text.replace(old, new)

    def fig_sub(m: re.Match) -> str:
        old = m.group(1)
        return f"\x00F{FIG_MAP[old]}\x00" if old in FIG_MAP else m.group(0)

    def tab_sub(m: re.Match) -> str:
        old = m.group(1)
        return f"\x00T{TAB_MAP[old]}\x00" if old in TAB_MAP else m.group(0)

    # longest key first so "2b" is not read as "2"
    tab_alt = "|".join(sorted(TAB_MAP, key=len, reverse=True))
    fig_alt = "|".join(sorted(FIG_MAP, key=len, reverse=True))
    # \b is correct for the Latin words but wrong for the Chinese ones: Python counts
    # CJK characters as word characters, so "见表2b" has no boundary before 表 and would
    # be skipped silently.
    lb, rb = (r"\b", r"\b") if boundary else ("", "")
    text = re.sub(fr"{lb}{tab_word}\s*({tab_alt}){rb}", tab_sub, text)
    text = re.sub(fr"{lb}{fig_word}\s*({fig_alt}){rb}", fig_sub, text)
    text = re.sub(r"\x00F([0-9A-Z]+)\x00",
                  lambda m: f"{fig_word}{fig_sep}{m.group(1)}", text)
    text = re.sub(r"\x00T([0-9A-Z]+)\x00",
                  lambda m: f"{tab_word}{tab_sep}{m.group(1)}", text)
    return text


EN_CAPTIONS = """## Figures and Tables

**Figure 1** FAERS case-selection flow (90 quarterly ASCII releases → 20.33 million de-duplicated cases → ethambutol-related cases → ocular-term 2×2 construction).

**Figure 2** Disproportionality of ethambutol-associated ocular terms. (A) Volcano plot: abscissa, log₂ reporting odds ratio; ordinate, −log₁₀ Benjamini–Hochberg q; red points are strict signals. (B) Forest plot of the signal terms (reporting odds ratio with 95% CI, n ≥ 3).

**Figure 3** Focus-layer STRING protein–protein interaction network (33 nodes, 191 edges). Red: curated core panel; orange: literature-supported genes; blue: optic-nerve phenotype genes.

**Figure 4** Focus-layer functional enrichment dot plot (GO-BP/CC/MF, KEGG, Reactome, WikiPathways).

**Figure 5** Docking scores of ethambutol against 14 hub targets (AutoDock Vina, kcal/mol).

**Figure 6** Temporal behaviour of ethambutol ocular reporting. (A) Time from starting ethambutol to onset, log-scale histogram by event category. (B) Median times with box plots. (C) Annual report volume and the proportion carrying an optic-nerve term (2013–2026).

**Figure S1** Heat map of ocular reporting odds ratios across six antitubercular drugs (log₂ ROR). Supplementary.

**Figure S2** Overlap of the network's hub genes with DisGeNET ocular disease genes (5 of 33 hubs; 184 ocular genes). Supplementary.

**Table 1** Study population (cases per exposure after FAERS de-duplication).

**Table 2** Strict signals (45 terms).

**Table 3** Multivariable logistic regression.

**Table 4** Two-sample Mendelian randomisation estimates for the primary outcome, optic neuritis, one row per exposure.

**Table 5** Robustness checks (four scenarios).

**Table 6** Optic-nerve odds ratio by patient subgroup, with contrasts between strata.

**Supplementary tables.**

**Table S1** Renal-function Mendelian randomisation estimates (wider harmonisation against the cached FinnGen scans).

**Table S2** The full Mendelian randomisation panel: every exposure against all six optic-nerve and visual outcomes (60 estimates).

**Table S3** Ethambutol ocular signal table (152 terms).

**Table S4** Drug-toxicity-spectrum signals (top 30).

**Table S5** Anatomical grouping of the panel (152 terms).

**Table S6** Ocular tuberculosis manifestations, excluded from the toxicity reading (17 terms).

**Table S7** Non-ocular terms removed from the panel (13 terms).

**Table S8** Other ocular findings, neither drug toxicity nor tuberculosis, excluded from the toxicity reading (15 terms).

**Table S9** Time from starting ethambutol to onset.

**Table S10** Focus-layer hub genes.

**Table S11** Principal enriched pathways.

**Table S12** Molecular docking score matrix.

**Table S13** Report adequacy.

**Table S14** Physicochemical and drug-likeness profile of ethambutol (PubChem descriptors; the five standard rules are evaluated in `results/admet_ethambutol.json`). This table was cited in the text but had no caption; the caption is added here.

**Additional analyses without a numbered table.** Regimen-stratified within-class comparison (`results/faers_regimen_strata.csv`); cumulative-dose (`tables/Table13_cumulative_dose.csv`) and head-to-head comparison (`tables/Table14_headtohead.csv`); within-class signal comparison (`tables/Table2_withinclass.csv`); dose strata (`tables/Table11_dose.csv`); JADER external validation (`results/jader_validation.csv`); temporal split validation (`results/faers_temporal_validation.csv`); redocking validation panel (`results/redocking_validation_final.csv`); tuberculosis burden denominator (`data/derived/faers_tb_denominator.csv` and `data/derived/faers_who_merged.csv`); ligand parameter validation (`results/ligand_parameter_validation.json`).

**Machine-readable table files.** Each numbered table is also provided as a UTF-8 CSV in `tables/`. Main tables: `Table1_cohort.csv` (Table 1), `Table2b_signals_strict.csv` (Table 2), `Table4_logistic.csv` (Table 3), `Table8_mr.csv` (Table 4), `Table9_robustness.csv` (Table 5); the subgroup table (Table 6) is `results/faers_subgroups.csv` with the between-stratum contrasts in `results/faers_subgroup_contrasts.csv`. Supplementary tables: `TableS1_mr_renal.csv` (Table S1), `TableS2_mr_full_panel.csv` (Table S2), `Table2_signals.csv` (Table S3), `Table2c_toxicity_spectrum.csv` (Table S4), `Table2d_panel_anatomical.csv` (Table S5), `Table2e_ocular_tuberculosis.csv` (Table S6), `Table2f_non_ocular_terms.csv` (Table S7), `Table2g_other_ocular.csv` (Table S8), `Table3_tto.csv` (Table S9), `Table5_hubs.csv` (Table S10), `Table6_enrichment.csv` (Table S11), `Table7_docking.csv` (Table S12), `Table10_adequacy.csv` (Table S13); the 178-term derived panel is `Table2_signals_full_panel.csv` and the review of the previously unclassified terms is `Table2d_review_proposed.csv`, with a reason for each entry.
"""

CN_CAPTIONS = """## 图表清单

**图1** FAERS 病例筛选流程（90 个季度 ASCII 原始发布 → 2 033 万例去重病例 → 乙胺丁醇相关病例 → 眼科术语四格表）。

**图2** 乙胺丁醇眼部术语的不成比例分析。（A）火山图：横轴为 log₂ 报告比值比，纵轴为 −log₁₀(Benjamini-Hochberg q)，红点为严格信号；（B）信号术语森林图（报告比值比及 95%CI，n≥3）。

**图3** 聚焦层 STRING 蛋白互作网络（33 节点、191 边）。红色为策展核心面板，橙色为文献支持基因，蓝色为视神经表型基因。

**图4** 聚焦层功能富集点图（GO-BP/CC/MF、KEGG、Reactome、WikiPathways）。

**图5** 乙胺丁醇对 14 个 hub 靶点的对接打分（AutoDock Vina，kcal/mol）。

**图6** 乙胺丁醇眼部报告的时序特征。（A）用药至发病时间的对数刻度直方图（按事件类别）；（B）中位时间的箱线图；（C）年度报告量与视神经术语占比（2013—2026）。

**图S1** 六种抗结核药眼科报告比值比热图（log₂ ROR）。补充材料。

**图S2** 网络 hub 基因与 DisGeNET 眼部疾病基因的重叠（33 个 hub 中 5 个；184 个眼部基因）。补充材料。

**表1** 研究人群（FAERS 去重后各暴露病例数）。

**表2** 严格信号（45 个术语）。

**表3** 多因素 logistic 回归。

**表4** 两样本孟德尔随机化估计：主要结局（视神经炎），每个暴露一行。

**表5** 稳健性检验（四情景）。

**表6** 按患者亚组的视神经比值比及层间对比。

**补充表**

**表S1** 肾功能孟德尔随机化估计（对照缓存 FinnGen 扫描的更宽协调）。

**表S2** 完整孟德尔随机化面板：全部暴露 × 全部 6 个视神经及视觉结局（60 个估计）。

**表S3** 乙胺丁醇眼部信号表（152 个术语）。

**表S4** 药物毒性谱信号（前 30）。

**表S5** 面板的解剖学分组（152 个术语）。

**表S6** 眼结核表现，排除于毒性解读之外（17 个术语）。

**表S7** 移出面板的非眼部术语（13 个术语）。

**表S8** 既非药物毒性亦非结核的其他眼部发现，排除于毒性解读之外（15 个术语）。

**表S9** 用药至发病时间。

**表S10** 聚焦层 hub 基因。

**表S11** 主要富集通路。

**表S12** 分子对接打分矩阵。

**表S13** 报告充分性。

**表S14** 乙胺丁醇的理化与类药性特征（PubChem 描述符；五条标准规则的判定见 `results/admet_ethambutol.json`）。该表此前在正文被引用但没有表题，此处补上。

**无编号表的附加分析。** 方案分层的同类药比较（`results/faers_regimen_strata.csv`）；累积剂量（`tables/Table13_cumulative_dose.csv`）与头对头比较（`tables/Table14_headtohead.csv`）；同类药信号比较（`tables/Table2_withinclass.csv`）；剂量分层（`tables/Table11_dose.csv`）；JADER 外部验证（`results/jader_validation.csv`）；时间切分验证（`results/faers_temporal_validation.csv`）；重对接验证面板（`results/redocking_validation_final.csv`）；结核病人群分母（`data/derived/faers_tb_denominator.csv` 与 `data/derived/faers_who_merged.csv`）；配体参数验证（`results/ligand_parameter_validation.json`）。

**机器可读表文件。** 每个编号表同时以 UTF-8 CSV 形式提供于 `tables/`。正文表：`Table1_cohort.csv`（表1）、`Table2b_signals_strict.csv`（表2）、`Table4_logistic.csv`（表3）、`Table8_mr.csv`（表4）、`Table9_robustness.csv`（表5）；亚组表（表6）为 `results/faers_subgroups.csv`，层间对比见 `results/faers_subgroup_contrasts.csv`。补充表：`TableS1_mr_renal.csv`（表S1）、`TableS2_mr_full_panel.csv`（表S2）、`Table2_signals.csv`（表S3）、`Table2c_toxicity_spectrum.csv`（表S4）、`Table2d_panel_anatomical.csv`（表S5）、`Table2e_ocular_tuberculosis.csv`（表S6）、`Table2f_non_ocular_terms.csv`（表S7）、`Table2g_other_ocular.csv`（表S8）、`Table3_tto.csv`（表S9）、`Table5_hubs.csv`（表S10）、`Table6_enrichment.csv`（表S11）、`Table7_docking.csv`（表S12）、`Table10_adequacy.csv`（表S13）；178 术语的导出面板为 `Table2_signals_full_panel.csv`，先前未归类术语的逐条复核为 `Table2d_review_proposed.csv`（含每条理由）。
"""


def rewrite(path: Path, start: str, end: str, captions: str, fig_word: str,
            tab_word: str, body_end: str, merge_pairs: list[tuple[str, str]],
            fig_sep: str, tab_sep: str, boundary: bool = True) -> None:
    lines = path.read_text(encoding="utf-8").split("\n")
    text = "\n".join(lines)

    i_body_end = text.find(body_end)
    if i_body_end < 0:
        raise SystemExit(f"{path.name}: body boundary {body_end!r} not found")
    i_start = text.find(start)
    i_end = text.find(end, i_start)
    if i_start < 0 or i_end < 0:
        raise SystemExit(f"{path.name}: caption boundaries not found")
    if not i_body_end <= i_start < i_end:
        raise SystemExit(f"{path.name}: boundaries out of order "
                         f"({i_body_end}, {i_start}, {i_end})")

    body = renumber(text[:i_body_end], fig_word, tab_word, merge_pairs,
                    fig_sep, tab_sep, boundary)
    tail = text[i_end:]                      # headings after the caption list, unmapped
    new = body + text[i_body_end:i_start] + captions + "\n" + tail
    BACKUP.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, BACKUP / path.name)
    path.write_text(new, encoding="utf-8")
    print(f"  {path.name}: body renumbered, caption list replaced "
          f"({len(lines)} -> {len(new.split(chr(10)))} lines)")


print("Renumbering the consolidated display set")
rewrite(EN, "## Figures and Tables", "## Reporting checklists", EN_CAPTIONS,
        "Figure", "Table", "\n## References",
        [("Figure 2, Figure 4", "Figure 2")], " ", " ")
rewrite(CN, "## 图表清单", "## 声明", CN_CAPTIONS, "图", "表", "\n## 图表清单",
        [("**图2**、**图4**", "**图2**")], "", "", boundary=False)
print("done")
sys.exit(0)
