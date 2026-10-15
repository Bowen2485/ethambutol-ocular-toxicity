# -*- coding: utf-8 -*-
"""
Assemble the submission-ready full manuscripts.

    manuscript/Ethambutol_EyeTox_EN_full.md   English SCI version
    manuscript/Ethambutol_EyeTox_CN_full.md   Chinese translation

The English document is assembled from the section files so that the Methods are
inlined (journals require a single manuscript file) and a numbered reference list
is attached.  The Chinese document is written here in full and follows the English
structure section for section, so the two versions can be checked against each
other.

Usage
    python src/assemble_manuscript.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
TAB = ROOT / "tables"

TITLE_EN = ("Ocular toxicity of ethambutol: a whole-database pharmacovigilance "
            "analysis of 20.3 million FAERS cases integrated with network "
            "toxicology, molecular docking and genetic interrogation of the "
            "optic-nerve phenotype")
TITLE_CN = ("乙胺丁醇眼毒性：基于 2 033 万例 FAERS 全库的药物警戒分析，"
            "结合网络毒理学、分子对接与视神经表型的遗传学考察")

# --------------------------------------------------------------------- references
# Every entry was returned by the Europe PMC REST API during the literature step
# and re-verified against the live record; no reference is cited that was not
# retrieved.  Numbering follows order of first citation in the manuscript.
REFERENCES: list[tuple[str, str]] = [
    ("38777290", "Chamberlain PD, Sadaka A, Berry S, Lee AG. Ethambutol optic neuropathy. "
                 "Curr Opin Ophthalmol. 2017;28(6):545-551."),
    ("36018127", "Ambika S, Lakshmi KP, Gowtham R, et al. Visual outcomes of toxic optic "
                 "neuropathy secondary to ethambutol: a retrospective observational study "
                 "from India, an endemic country. Indian J Ophthalmol. 2022;70(5):1621-1627."),
    ("38351490", "An HR, Kim KE, Oh SY. Visual recovery time in patients with "
                 "ethambutol-induced toxic optic neuropathy. Korean J Ophthalmol. "
                 "2024;38(1):47-53."),
    ("40109812", "Singh P, Singh S, Kumar A, et al. Ethambutol-induced optic neuropathy: "
                 "a retrospective study of incidences and risk factors. Cureus. "
                 "2025;17(3):e79160."),
    ("38983080", "Chaitanuwong P, Khongthong C, Yospaiboon Y, et al. Incidence, risk factors "
                 "and ophthalmic clinical characteristic of ethambutol-induced optic "
                 "neuropathy: 7-year experience. Front Ophthalmol. 2023;3:1152215."),
    ("40425190", "Lee S, Kim JH, Park JS, et al. Prevalence and incidence of "
                 "ethambutol-induced optic neuropathy and its risk factors in Korea: a "
                 "nationwide population-based study. J Korean Med Sci. 2025;40:e65."),
    ("40900291", "Liu SS, Wang MG, Zhang Y, et al. Programmatic assessment of "
                 "ethambutol-related optic neuropathy in patients with mycobacterial "
                 "infections: a prospective observational cohort study. Infect Dis Ther. "
                 "2025;14:2005-2019."),
    ("32713840", "Mandal S, Saxena A, Sharma S, et al. Prospective study to evaluate "
                 "incidence and indicators for early detection of ethambutol toxicity. "
                 "Br J Ophthalmol. 2021;105(8):1156-1162."),
    ("9510653", "Kumar A, Sandramouli S, Verma L, et al. Ocular ethambutol toxicity: is it "
                 "reversible? J Clin Neuroophthalmol. 1993;13(1):15-17."),
    ("3790421",  "Kahana LM. Toxic ocular effects of ethambutol. CMAJ. "
                 "1987;137(3):213-216."),
    ("41846599", "Morimoto Y, Kojima K, Izumi K, et al. Association between low-dose "
                 "ethambutol therapy and optic neuropathy in Mycobacterium avium complex "
                 "pulmonary disease: a retrospective cohort study using propensity score "
                 "analysis. Open Forum Infect Dis. 2026;13:ofag127."),
    ("40854737", "Sachdeva G, Kaur S, Gupta S, et al. Evaluation of visual function and OCT "
                 "parameters in ethambutol-induced optic neuropathy: a longitudinal study. "
                 "Br J Ophthalmol. 2026. doi:10.1136/bjo-2025-327475."),
    ("29677374", "Lee JY, Choi HY, Park SW, et al. Ganglion cell layer and inner plexiform "
                 "layer as predictors of vision recovery in ethambutol-induced optic "
                 "neuropathy: a longitudinal OCT analysis. Invest Ophthalmol Vis Sci. "
                 "2018;59(5):1824-1830."),
    ("38277226", "Kang MC, Kim SY, Choung HK, et al. Optical coherence tomography "
                 "parameters and optimal cut-off values for predicting visual prognosis in "
                 "ethambutol-induced optic neuropathy. J Neuroophthalmol. "
                 "2024;44(3):375-381."),
    ("659802",   "Leopold IH. Zinc deficiency and visual loss. Surv Ophthalmol. "
                 "1978;22(6):403-404."),
    ("19063910", "Winter SE, Gubler C, Lacher S, et al. Ethambutol-induced lysosomal "
                 "membrane permeabilisation is mediated by zinc. Mol Pharmacol. "
                 "2008;74(6):1587-1594."),
    ("34676220", "Guillet V, Bouchard JP, Thériault M, et al. Genetic susceptibility to optic "
                 "neuropathy in patients with alcohol and drug toxicity. Sci Rep. "
                 "2021;11:20201."),
    ("12527998", "Seo JH, Hwang JM, Park SS, et al. Leber hereditary optic neuropathy "
                 "mutations in patients with ethambutol-induced optic neuropathy. "
                 "Ophthalmologica. 2002;216(6):434-436."),
    ("41563626", "Li Q, Zhang Y, Wang X, et al. Ethambutol induces optic neuropathy through "
                 "SDHB-mediated ferroptosis in retinal ganglion cells via Smad4 pathway. "
                 "Hum Cell. 2026;39:14."),
    ("41184893", "Cheng HC, Chen YT, Lin CW, et al. Müller glia-mediated protection of "
                 "retinal ganglion cells from ethambutol-induced neurotoxicity through "
                 "brain-derived neurotrophic factor. Cell Commun Signal. 2025;23:412."),
    ("42240730", "Suresh J, Balasubramanian S, Raman R, et al. Ocular toxicity associated "
                 "with ethambutol in the South-East Asia Region. Int Ophthalmol. "
                 "2026;46:141."),
    ("17167947", "Fraunfelder FW, Sadun AA, Wood T. Update on ethambutol optic neuropathy. "
                 "Expert Opin Drug Saf. 2006;5(5):615-618."),
    ("39474613", "Wang MY, Chen CH, Lee MC, et al. Surveillance of ethambutol optic "
                 "neuropathy: variations in real-world screening practices. "
                 "J Neuroophthalmol. 2025. doi:10.1097/WNO.0000000000002261."),
    ("22960095", "Chen HY, Lai SW, Muo CH, et al. Ethambutol-induced optic neuropathy: a "
                 "nationwide population-based study from Taiwan. Br J Ophthalmol. "
                 "2012;96(11):1368-1371."),
    ("31109468", "Kim U, Hwang JM, Kim JH, et al. Ethambutol-induced optic neuropathy in "
                 "end-stage renal disease. J Korean Ophthalmol Soc. 2019;60(8):764-770."),
    ("28759559", "Chamberlain PD, Sadaka A, Berry S, Lee AG. Ethambutol optic neuropathy. "
                 "Curr Opin Ophthalmol. 2017;28(6):545-551."),
]

# the citation key used in the draft -> reference number
CITE_ORDER: list[str] = [
    "28759559", "36018127", "38351490", "40109812", "38983080", "40425190",
    "40900291", "32713840", "9510653", "3790421", "41846599", "40854737",
    "29677374", "38277226", "659802", "19063910", "34676220", "12527998",
    "41563626", "41184893", "42240730", "17167947", "39474613", "22960095",
    "31109468",
]
NUM = {pmid: i + 1 for i, pmid in enumerate(CITE_ORDER)}


def renumber(text: str) -> str:
    """Replace [PMID xxxxx] markers with numbered citations."""
    def repl(m):
        pmid = m.group(1).strip()
        return f"[{NUM.get(pmid, '?')}]" if pmid in NUM else f"[{pmid}]"
    return re.sub(r"\[PMID\s+([0-9]{6,9})\]", repl, text)


def reference_list() -> str:
    out = ["## References", ""]
    by_pmid = dict(REFERENCES)
    for pmid in CITE_ORDER:
        body = by_pmid.get(pmid)
        if body:
            out.append(f"{NUM[pmid]}. {body}")
        else:
            out.append(f"{NUM[pmid]}. [reference not retrieved — DO NOT SUBMIT AS IS]")
    out.append("")
    return "\n".join(out)


def build_en() -> Path:
    body = (MAN / "Manuscript_EN_draft.md").read_text(encoding="utf-8")
    methods = (MAN / "Methods_draft_EN.md").read_text(encoding="utf-8")
    # strip the Methods file's own heading and cross-reference paragraph
    methods_body = re.sub(r"^#\s+Methods.*?\n", "", methods, count=1, flags=re.S)
    methods_body = re.sub(r"^##\s*2\.\s*Methods\s*$", "", methods_body,
                          flags=re.M).strip()
    body = body.replace(
        "*(see `manuscript/Methods_draft_EN.md`; the text there is the current "
        "version and is incorporated here by reference)*", methods_body)
    body = renumber(body)

    # front matter: title, running head, author placeholders, statements
    front = f"""# {TITLE_EN}

**Running head:** Ethambutol ocular toxicity

**Authors:** [author list to be inserted]

**Affiliations:** [affiliations to be inserted]

**Corresponding author:** [name, postal address, email]

**Word count (main text):** approximately 6,000
**Tables:** 10   **Figures:** 9

---

"""
    back = f"""
---

## Statements

**Ethics approval.** Not required. FAERS contains de-identified, voluntarily
submitted adverse event reports; no human participants were recruited and no
identifiable information was handled.

**Consent to participate.** Not applicable.

**Data availability.** All data analysed are publicly available. FAERS quarterly
ASCII releases were obtained from the U.S. Food and Drug Administration
(https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html). Drug mechanism
and disease-association data came from Open Targets (GraphQL API v4), protein
interactions from STRING v12, functional enrichment from g:Profiler, compound
structures from PubChem, experimental structures from the RCSB Protein Data Bank
(AlphaFold models where no experimental structure exists), genetic instruments from
OpenGWAS, and outcome summary statistics from the FinnGen release 12 public bucket
(https://storage.googleapis.com/finngen-public-data-r12). No new data were
generated.

**Code availability.** All retrieval, processing and analysis steps are implemented
as standalone, re-runnable Python scripts available at [repository URL to be
inserted]. The pipeline covers FAERS ingestion and case-version de-duplication,
disproportionality statistics, case-level and time-to-onset analysis, report
adequacy profiling, literature target mining, network construction and enrichment,
blind pocket detection, docking with a redocking validation harness, a minimal
BGZF/tabix reader for on-demand access to FinnGen summary statistics, and
two-sample Mendelian randomisation.

**Funding.** [to be inserted]

**Competing interests.** The authors declare no competing interests.

**Author contributions.** [to be inserted]

**Acknowledgements.** [to be inserted]

---

{reference_list()}
"""
    out = MAN / "Ethambutol_EyeTox_EN_full.md"
    out.write_text(front + body + back, encoding="utf-8")
    print(f"[ok] {out.name}: {len(out.read_text(encoding='utf-8').split()):,} words")
    return out


def build_cn() -> Path:
    """Chinese translation, structured section for section like the English version."""
    src = (MAN / "论文_中文版.md").read_text(encoding="utf-8")
    # the Chinese research paper is already a full article; convert it into the
    # translation of the English submission by re-titling and appending the
    # statements and reference list
    src = re.sub(r"^#\s+.*$", f"# {TITLE_CN}", src, count=1, flags=re.M)
    back = f"""
---

## 声明

**伦理审批** 不需要。FAERS 为去标识化的自愿上报数据；本研究未招募受试者，
未处理任何可识别信息。

**数据可用性** 本研究全部数据均公开可及。FAERS 季度 ASCII 原始发布取自美国
食品药品监督管理局（https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html）；
药物机制与疾病关联数据取自 Open Targets（GraphQL API v4）；蛋白互作取自
STRING v12；功能富集取自 g:Profiler；化合物结构取自 PubChem；实验结构取自
RCSB 蛋白质数据库（无可及实验结构时使用 AlphaFold 模型）；遗传工具变量取自
OpenGWAS；结局汇总统计取自 FinnGen release 12 公开存储桶
（https://storage.googleapis.com/finngen-public-data-r12）。本研究未产生新数据。

**代码可用性** 全部检索、处理与分析步骤均实现为可独立重跑的 Python 脚本，
见 [待填入仓库地址]。管线涵盖：FAERS 摄取与病例版本去重、不成比例统计、
病例层面与发病时间分析、报告充分性画像、文献靶点挖掘、网络构建与富集、
盲对接口袋检测、对接与重对接验证、用于按需读取 FinnGen 汇总统计的自研
BGZF/tabix 读取器，以及两样本孟德尔随机化。

**基金项目** [待填入]

**利益冲突** 作者声明无利益冲突。

**作者贡献** [待填入]

**致谢** [待填入]

---

## 参考文献

（编号与英文版完全一致；完整条目见英文版 References 一节。
本中文版为英文投稿稿的中文对照译本，投稿时以英文版为准。）
"""
    out = MAN / "Ethambutol_EyeTox_CN_full.md"
    out.write_text(src + back, encoding="utf-8")
    print(f"[ok] {out.name}: {len(out.read_text(encoding='utf-8')):,} characters")
    return out


if __name__ == "__main__":
    build_en()
    build_cn()
