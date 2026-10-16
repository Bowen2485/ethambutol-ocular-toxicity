# -*- coding: utf-8 -*-
"""
Draft three reductions of the 378-word abstract to fit the Frontiers limit of about 350 words.

The 378-word version is submission/abstract_rewritten.json.  Its parts run Background 40,
Methods 109, Results 183, Conclusion 46.  Three different places to take the words from are
offered rather than one, because they are not equivalent editorially:

  A  Methods carries the cut.  Every result number survives; the list of techniques and the
     four disproportionality measures are compressed.  Safest for a reviewer who reads results.
  B  Results carries the cut.  Methods stays complete for reproducibility; the six null
     non-specific terms become three and the adequacy proportion goes.  Keeps the methods
     auditable at the cost of some negative-control detail.
  C  Both, plus tightened Background and Conclusion.  Lands well under the limit, which leaves
     room for the journal's own additions, but it is the only one that removes a result.

Word counts use whitespace-split tokens, which is how Frontiers counts.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIG = json.loads((ROOT / "submission" / "abstract_rewritten.json").read_text(encoding="utf-8"))
O = ORIG["parts"]

BG = ("Ethambutol is a first-line antitubercular drug whose optic neuropathy can be "
      "irreversible, and estimates of its frequency vary widely with how cases are "
      "ascertained. No pharmacovigilance analysis has yet profiled the full ocular phenotype "
      "against the other first-line antitubercular drugs.")

BG_C = ("Ethambutol is a first-line antitubercular drug whose optic neuropathy can be "
        "irreversible, and estimates of its frequency vary widely with ascertainment. No "
        "pharmacovigilance analysis has profiled the full ocular phenotype against the other "
        "first-line antitubercular drugs.")

BG_D = ("Ethambutol is a first-line antitubercular drug whose optic neuropathy can be "
        "irreversible, and its frequency estimates vary widely with ascertainment. No "
        "pharmacovigilance analysis has profiled the ocular phenotype against the other "
        "first-line antitubercular drugs.")

M_FULL = O["Methods"]

M_SHORT = (
    "We analysed all 90 FDA Adverse Event Reporting System (FAERS) quarterly releases "
    "(2004Q1-2026Q2), de-duplicating 24,389,966 reports to 20,328,568 unique cases by the FDA "
    "case-version protocol. Four disproportionality measures were computed for 178 ocular "
    "MedDRA preferred terms across ethambutol and five comparator antitubercular drugs, with "
    "Benjamini-Hochberg control and four robustness specifications. We assessed time to onset, "
    "predictors and completeness, then combined Europe PMC, Open Targets and STRING into a "
    "mechanism network, tested enrichment, docked ethambutol against the hub targets, and "
    "interrogated the loci against FinnGen R12 phenotypes.")

M_TIGHT = (
    "We analysed all 90 FDA Adverse Event Reporting System (FAERS) quarterly releases "
    "(2004Q1-2026Q2), de-duplicating 24,389,966 reports to 20,328,568 unique cases by the FDA "
    "case-version protocol. Four disproportionality measures were computed for 178 ocular "
    "MedDRA preferred terms across ethambutol and five comparator antitubercular drugs, with "
    "Benjamini-Hochberg control and four prespecified robustness specifications. We then built "
    "a mechanism network from Europe PMC, Open Targets and STRING, tested enrichment, docked "
    "ethambutol against the hub targets, and interrogated the loci against FinnGen R12 "
    "optic-nerve phenotypes.")

R_FULL = O["Results"]

R_SHORT = (
    "Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475 "
    "(3.44%) an optic-nerve event; 45 of 152 testable ocular terms met strict signal criteria. "
    "The risk was confined to the optic nerve: optic neuropathy gave an ROR of 159.21 (95% CI "
    "134.65-188.25), whereas no non-specific ocular complaint formed a signal in any comparison "
    "(vision blurred 1.15, cataract 0.81, dry eye 0.35, eye pain 0.32, glaucoma 0.18, ocular "
    "hyperaemia 0.18). Within the antitubercular class ethambutol had an ROR of 6.47 "
    "(5.38-7.79) for optic neuropathy, and restricting the comparison to ethambutol-containing "
    "regimens gave a rate ratio of 3.28 (1.03-10.40) against regimens without it. The pattern "
    "replicated in JADER (1,054,239 cases; optic neuropathy ROR 571.0, toxic optic neuropathy "
    "864.6, all control terms null). Median time to an optic-nerve event was 125 days versus 30 "
    "days for non-ocular events. Enrichment converged on ferroptosis and mitochondrial "
    "integrity, and genetically proxied renal function showed no causal effect on any "
    "optic-nerve outcome (all q >= 0.87).")

R_TIGHT = (
    "Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475 "
    "(3.44%) an optic-nerve event; 45 of 152 testable ocular terms met strict signal criteria. "
    "The risk was confined to the optic nerve: optic neuropathy gave an ROR of 159.21 (95% CI "
    "134.65-188.25), whereas no non-specific ocular complaint formed a signal in any comparison "
    "(vision blurred 1.15, cataract 0.81, ocular hyperaemia 0.18). Within the antitubercular "
    "class ethambutol had an ROR of 6.47 (5.38-7.79) for optic neuropathy, and restricting the "
    "comparison to ethambutol-containing regimens gave a rate ratio of 3.28 (1.03-10.40) "
    "against regimens without it. The pattern replicated in JADER (1,054,239 cases; optic "
    "neuropathy ROR 571.0, toxic optic neuropathy 864.6, all control terms null). Median time "
    "to an optic-nerve event was 125 days versus 30 days for non-ocular events. Enrichment "
    "converged on ferroptosis and mitochondrial integrity, and genetically proxied renal "
    "function showed no causal effect on any optic-nerve outcome (all q >= 0.87).")

R_C = (
    "Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475 "
    "(3.44%) an optic-nerve event; 45 of 152 testable ocular terms met strict signal criteria. "
    "The risk was confined to the optic nerve: optic neuropathy gave an ROR of 159.21 (95% CI "
    "134.65-188.25), whereas no non-specific ocular complaint formed a signal in any comparison "
    "(vision blurred 1.15, cataract 0.81, ocular hyperaemia 0.18). Within the class ethambutol "
    "had an ROR of 6.47 (5.38-7.79) for optic neuropathy, and restricting to "
    "ethambutol-containing regimens gave a rate ratio of 3.28 (1.03-10.40) against regimens "
    "without it. The pattern replicated in JADER (1,054,239 cases; optic neuropathy ROR 571.0, "
    "all control terms null). Median time to an optic-nerve event was 125 days versus 30 for "
    "non-ocular events. Enrichment converged on ferroptosis and mitochondrial integrity, and "
    "genetically proxied renal function showed no causal effect on any optic-nerve outcome.")

C_FULL = O["Conclusion"]

C_TIGHT = ("Ethambutol ocular toxicity is a highly specific optic-nerve signal that spares the "
           "ocular surface, is delayed by months, resists every robustness specification "
           "tested, and replicates in an independent national database.")

C_SHORT = ("Ethambutol ocular toxicity is a highly specific optic-nerve signal that spares the "
           "ocular surface, is delayed by months, resists every robustness specification "
           "tested, and replicates in an independent national database. Renal impairment "
           "appears to raise drug exposure rather than to cause optic-nerve degeneration "
           "independently.")

VARIANTS = {
    "A  Methods carries the cut (no result removed)": [BG_D, M_SHORT, R_FULL, C_FULL],
    "B  Results carries the cut (Methods intact)": [BG, M_FULL, R_TIGHT, C_FULL],
    "C  Both, with the framing tightened too": [BG_C, M_TIGHT, R_C, C_SHORT],
}

print("=" * 96)
print(f"original: {ORIG['total']} words "
      f"(Background {ORIG['word_counts']['Background']}, Methods {ORIG['word_counts']['Methods']}, "
      f"Results {ORIG['word_counts']['Results']}, "
      f"Conclusion {ORIG['word_counts']['Conclusion']})")
print("=" * 96)
for name, parts in VARIANTS.items():
    counts = [len(p.split()) for p in parts]
    total = sum(counts)
    verdict = "OK, within 350" if total <= 350 else f"STILL {total - 350} OVER"
    print(f"\n{name}")
    print(f"   Background {counts[0]}  Methods {counts[1]}  Results {counts[2]}  "
          f"Conclusion {counts[3]}   TOTAL {total}   {verdict}")

print()
print("=" * 96)
print("Full text of variant C, as it would read")
print("=" * 96)
for label, p in zip(("Background", "Methods", "Results", "Conclusion"), VARIANTS[
        "C  Both, with the framing tightened too"]):
    print(f"\n{label}: {p}")

#: written out so the choice survives the session rather than living in a transcript
DOC = ROOT / "docs" / "摘要压缩_ABC三方案.md"
lines = [
    "# 摘要压缩：三个方案（待选）",
    "",
    "> 生成：`src/draft_abstract_variants.py`（可重跑；字数按空白分词统计，与 Frontiers 口径一致）",
    f"> 现状：`submission/abstract_rewritten.json`，**{ORIG['total']} 词**"
    f"（Background {ORIG['word_counts']['Background']}／Methods {ORIG['word_counts']['Methods']}／"
    f"Results {ORIG['word_counts']['Results']}／Conclusion {ORIG['word_counts']['Conclusion']}），"
    "Frontiers 上限约 350 词，**超 {} 词**。".format(ORIG["total"] - 350),
    "",
    "| 方案 | 从哪里删 | 删掉了什么 | 字数 |",
    "|---|---|---|---|",
    "| **A** | Methods | 无任何结果数字被删；压缩技术清单与四种不成比例度量 | **349** |",
    "| **B** | Results | Methods 完整保留；六个阴性非特异术语保留三个，删去 27.8% 充分性比例 | **349** |",
    "| **C** | 两处 + 首尾收紧 | B 的删减，另删 JADER 的“中毒性视神经病变 864.6”一项 | **303** |",
    "",
    "三者都保留四个核心断言：信号高度特异并局限于视神经、延迟数月、经全部稳健性检验、"
    "在 JADER 独立复现。区别只在删哪一类信息：**A 删方法细节，B 删阴性对照细节，C 两者都删并留出余量**。",
    "",
]
for name, parts in VARIANTS.items():
    lines += [f"## {name}", ""]
    for label, p in zip(("Background", "Methods", "Results", "Conclusion"), parts):
        lines += [f"**{label}.** {p}", ""]
    lines += [f"*合计 {sum(len(p.split()) for p in parts)} 词*", "", "---", ""]
lines += [
    "## 附：关键词超出上限",
    "",
    "稿件中英文版均列 **10 个**关键词，Frontiers 上限为 **8 个**；",
    "`src/build_latex.py` 里写的是 `[:8]`，即投稿用的 .tex **静默丢掉最后两个**"
    "（*molecular docking*、*Mendelian randomisation*）。",
    "",
    "需要明确选定 8 个，而不是由位置决定。推荐去掉 *signal detection*（与"
    "*disproportionality analysis* 重叠）与 *network toxicology*（框架名，索引价值最低），"
    "保留两个方法词：",
    "",
    "> ethambutol; optic neuropathy; pharmacovigilance; FAERS; disproportionality analysis; "
    "ferroptosis; molecular docking; Mendelian randomisation",
    "",
    "另一种选择是沿用 `submission/abstract_rewritten.json` 里的 8 个"
    "（去掉 *molecular docking* 与 *Mendelian randomisation*），代价是丢掉两个方法词的检索入口。",
    "",
]
DOC.write_text("\n".join(lines), encoding="utf-8")
print()
print(f"-> {DOC}")

