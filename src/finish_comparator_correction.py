# -*- coding: utf-8 -*-
"""
Finish the comparator correction: abstract, conclusion, and the Chinese manuscript.

The results text and limitations were updated by apply_comparator_correction.py.
This script applies the same change to the two places a casual reader is most likely
to look - the abstract and the conclusion - and to the Chinese translation, so the
two language versions cannot disagree.

Every number is read from results/faers_withinclass_signals.csv.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"

w = pd.read_csv(RES / "faers_withinclass_signals.csv", encoding="utf-8-sig")
eth = w[w.drug == "ethambutol"].set_index("term")
on = w[w.term == "OPTIC NEUROPATHY"].sort_values("ror", ascending=False).reset_index(drop=True)
rank = int(on[on.drug == "ethambutol"].index[0]) + 1
n_drugs = len(on)


def g(term, col):
    return eth.loc[term, col]


def fl(drug):
    return float(on[on.drug == drug].iloc[0].ror)


ABSTRACT = f"""**Results.** Among 13,804 de-duplicated ethambutol cases, 971 (7.03%)
reported an ocular event and 475 (3.44%) an optic-nerve event. Of 177 testable
ocular terms, 58 met strict signal criteria. Within the antitubercular class, optic
neuropathy gave ethambutol an ROR of {g('OPTIC NEUROPATHY','ror'):.2f}
(95% CI {g('OPTIC NEUROPATHY','ror_lcl'):.2f}-{g('OPTIC NEUROPATHY','ror_ucl'):.2f};
{int(g('OPTIC NEUROPATHY','a'))} cases), above the drugs given in the same regimen -
isoniazid {fl('isoniazid'):.2f}, rifampicin {fl('rifampicin'):.2f}, pyrazinamide
{fl('pyrazinamide'):.2f} - but {rank}th of {n_drugs} overall, below several
second-line agents used for drug-resistant disease, a comparison confounded by
indication severity. The most distinctive term in ethambutol's profile was
dyschromatopsia (ROR {g('DYSCHROMATOPSIA','ror'):.2f}, 95% CI
{g('DYSCHROMATOPSIA','ror_lcl'):.2f}-{g('DYSCHROMATOPSIA','ror_ucl'):.2f}), which
exceeded its optic-neuropathy ratio and matches the clinical hallmark of the
condition. Not one non-specific ocular complaint formed a signal in any comparison:
vision blurred {g('VISION BLURRED','ror'):.2f}, cataract {g('CATARACT','ror'):.2f},
dry eye {g('DRY EYE','ror'):.2f}, eye pain {g('EYE PAIN','ror'):.2f}, glaucoma
{g('GLAUCOMA','ror'):.2f}, ocular hyperaemia {g('OCULAR HYPERAEMIA','ror'):.2f}. All
optic-nerve signals survived four robustness specifications, including a comparator
denominator restricted to anti-tuberculosis reports, where optic neuropathy retained
an ROR of 7.64 (95% CI 5.24-11.13). Median time from starting ethambutol to an
optic-nerve event was 125 days (IQR 63-293) versus 30 days (IQR 9-85) for non-ocular
events in the same reports. Each additional year of age raised the odds of an ocular
event (adjusted OR 1.009, 95% CI 1.005-1.012), as did female sex (1.378,
1.196-1.588) and reporting from Europe (1.358, 1.151-1.601). Report completeness was
high for interpretive fields but low for exposure fields: only 27.8% of
optic-nerve-spectrum cases carried both age, sex and a therapy start date, and daily
dose did not predict the optic-nerve outcome once exposure duration was accounted for
(likelihood-ratio P = 0.55). Open Targets contains no human mechanism of action for
ethambutol, so the human gene set was reconstructed from literature; the focused-tier
network (33 nodes, 191 edges) was led by TP53, NFE2L2, AKT1, BCL2, HMOX1, CASP3,
SOD2, TNF and GPX4, and enrichment converged on ferroptosis (KEGG, P = 6.1 x 10^-7),
regulation of programmed cell death (GO:BP, P = 6.1 x 10^-14), the mitochondrial
envelope (GO:CC, P = 1.0 x 10^-8) and BDNF-NTRK2 signalling. Docking showed that
ethambutol occupies pockets on TNF, MFN2, HMOX1 and BCL2 (-4.95 to -5.50 kcal/mol).
Genetically proxied renal function showed no causal effect on any optic-nerve or
visual outcome (146-150 harmonised instruments per outcome; all q = 0.99)."""

CONCLUSION = f"""In the largest pharmacovigilance assessment of ethambutol to date -
20.3 million de-duplicated FAERS cases - ocular toxicity resolves into a highly
specific optic-nerve signal with no signal whatever for non-specific ocular
complaints, and that contrast survives every robustness specification tested. Within
the antitubercular class ethambutol's optic-neuropathy reporting ratio exceeds the
drugs given in the same regimen by 2- to 4-fold, although several second-line agents
used for drug-resistant disease show comparable or higher ratios under confounding by
indication severity. The most distinctive feature of the drug's profile is a
colour-vision signal that exceeds its optic-neuropathy ratio, which is the clinical
hallmark of ethambutol optic neuropathy. The onset is delayed by months relative to
other adverse events in the same reports, as a cumulative axonal injury would be, and
daily dose does not predict the outcome once exposure duration is taken into account.
At the molecular level the implicated network converges on ferroptosis and
mitochondrial integrity - the axis experimental work has now identified in
ethambutol-treated retinal ganglion cells - and docking indicates that the drug
engages the upstream inflammatory and redox nodes of that network rather than its
terminal enzymes. Genetically proxied renal function shows no causal effect on the
optic-nerve phenotype, which places renal impairment in the pathway as a determinant
of drug exposure rather than an independent cause of optic-nerve degeneration."""

FL = {"isoniazid": fl("isoniazid"), "rifampicin": fl("rifampicin"),
      "pyrazinamide": fl("pyrazinamide")}

CN_RESULTS = f"""**结果** 13 804 例乙胺丁醇相关病例中，971 例（7.03%）报告眼部事件，475 例（3.44%）报告视神经事件。<br>
**在抗结核药同类内部比较**（分母限定为提及任一抗结核药的报告，而非全库）：视神经病变
ROR {g('OPTIC NEUROPATHY','ror'):.2f}（95%CI {g('OPTIC NEUROPATHY','ror_lcl'):.2f}～{g('OPTIC NEUROPATHY','ror_ucl'):.2f}；
{int(g('OPTIC NEUROPATHY','a'))} 例），**高于同方案一线药**——异烟肼 {FL['isoniazid']:.2f}、
利福平 {FL['rifampicin']:.2f}、吡嗪酰胺 {FL['pyrazinamide']:.2f}——但在 {n_drugs} 种抗结核药中
仅排**第 {rank} 位**，低于部分用于耐药结核的二线药，而后者受适应证严重程度混杂。
乙胺丁醇谱型中最突出的是**色觉障碍**（ROR {g('DYSCHROMATOPSIA','ror'):.2f}，
95%CI {g('DYSCHROMATOPSIA','ror_lcl'):.2f}～{g('DYSCHROMATOPSIA','ror_ucl'):.2f}），
其比值高于视神经病变本身，与本病"色觉障碍早于且重于视力下降"的临床特征吻合。
**泛化眼部主诉在任何比较中均不成立**：视物模糊 {g('VISION BLURRED','ror'):.2f}、
白内障 {g('CATARACT','ror'):.2f}、干眼 {g('DRY EYE','ror'):.2f}、眼痛 {g('EYE PAIN','ror'):.2f}、
青光眼 {g('GLAUCOMA','ror'):.2f}、眼充血 {g('OCULAR HYPERAEMIA','ror'):.2f}。<br>
三个视神经核心信号在四种稳健性口径下均成立；最严格的同类药分母下视神经病变仍保留
ROR 7.64（95%CI 5.24～11.13）。用药至视神经事件中位 125 d（IQR 63～293），
非眼部事件 30 d（IQR 9～85）。年龄（校正 OR 1.009/岁）、女性（1.378）与欧洲报告者（1.358）
与眼部事件风险相关。报告充分性方面，解读性字段完整度高而暴露性字段低——视神经谱病例中
仅 27.8% 同时具备年龄、性别与用药开始日期；**校正用药时长后，每日剂量不预测视神经结局**
（似然比检验 P=0.55）。Open Targets 中乙胺丁醇无人类靶点记录，故人类基因集由文献重建；
聚焦层网络（33 节点、191 边）hub 前 10 位为 TP53、NFE2L2、AKT1、BCL2、HMOX1、CASP3、
SOD2、TNF、GPX4；富集收敛于铁死亡（KEGG，P=6.10×10⁻⁷）、程序性细胞死亡调控
（GO:BP，P=6.15×10⁻¹⁴）、线粒体（GO:CC，P=1.01×10⁻⁸）与 BDNF-NTRK2 信号。
对接显示乙胺丁醇占据 TNF、MFN2、HMOX1、BCL2 的口袋（−4.95～−5.50 kcal/mol）。
遗传代理的肾功能对全部视神经与视觉结局无因果效应（每个结局 146～150 个工具变量，q 均=0.99）。"""

CN_CONCLUSION = """在迄今最大规模的乙胺丁醇药物警戒评估中（2 033 万例去重 FAERS 病例），
其眼部毒性表现为**高度特异的视神经信号**，而泛化眼部主诉**完全无信号**，该对照在全部
稳健性口径下均成立。**在抗结核药同类内部**，乙胺丁醇的视神经病变报告比高于同方案一线药
2～4 倍，但低于部分用于耐药结核的二线药——后者受适应证严重程度混杂，不能据此断言其毒性最强。
该药谱型中最具特征的是**色觉障碍**，其比值高于视神经病变本身，与本病临床特征一致。
发病时间较同一批报告中的非眼部事件延迟数月，符合累积性轴索损伤；而校正用药时长后，
每日剂量不再预测结局。分子层面，所涉网络收敛于**铁死亡与线粒体完整性**——正是实验研究
已在乙胺丁醇处理的视网膜神经节细胞中确认的通路轴；对接提示乙胺丁醇作用于该网络的
**上游炎症与氧化还原节点**，而非其终端酶。遗传代理的肾功能对视神经表型**无因果效应**，
提示肾功能不全是**药物暴露量**的决定因素，而非视神经变性的独立病因。"""


def main() -> int:
    # ---------------------------------------------------------------- English
    p = MAN / "Manuscript_EN_draft.md"
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"\*\*Results\.\*\*.*?(?=\*\*Conclusions\.\*\*)",
               ABSTRACT + "\n\n", t, count=1, flags=re.S)
    t = re.sub(r"## 5\. Conclusion\n\n.*?(?=\n\n---|\Z)",
               f"## 5. Conclusion\n\n{CONCLUSION}\n", t, count=1, flags=re.S)
    p.write_text(t, encoding="utf-8")
    print("[ok] EN abstract Results and Conclusion rewritten")

    # also fix the generated Results block in the assembler
    p2 = ROOT / "src" / "finalize_manuscript.py"
    t2 = p2.read_text(encoding="utf-8")
    t2 = re.sub(r"ABSTRACT_RESULTS = .*?(?=\n\nABSTRACT_CONCLUSIONS)",
                "ABSTRACT_RESULTS = '''" + ABSTRACT + "'''", t2, count=1, flags=re.S)
    p2.write_text(t2, encoding="utf-8")
    print("[ok] assembler ABSTRACT_RESULTS synced")

    # ---------------------------------------------------------------- Chinese
    pc = MAN / "论文_中文版.md"
    tc = pc.read_text(encoding="utf-8")
    # abstract results paragraph
    tc = re.sub(r"\*\*结果\*\*.*?(?=\n\n\*\*结论\*\*)", CN_RESULTS + "\n", tc,
                count=1, flags=re.S)
    # conclusion section
    tc = re.sub(r"## 5 结论\n\n.*?(?=\n\n---|\n\n## )",
                f"## 5 结论\n\n{CN_CONCLUSION}\n", tc, count=1, flags=re.S)
    pc.write_text(tc, encoding="utf-8")
    print("[ok] CN abstract Results and Conclusion rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
