# 摘要压缩：三个方案

> **✅ 已采用方案 A（2026-10-16）**，并已写入中英两版稿件与 `submission/abstract_rewritten.json`；
> 应用脚本 `src/apply_abstract_and_title.py`（可重跑）。
> 2026-10-17 再删 10 词后为 **343 词**（对 `manuscript/Ethambutol_EyeTox_EN_full.md` 摘要段按空白分词统计）；
> 按 `src/check_frontiers_limits.py` 口径为 347 词、上限 350 内（余 3 词）；超出下表的原因是把摘要里的"在任何比较中"改为
> **"在同类药内部比较中"**——1.15 这组数值出自 `faers_withinclass_signals.csv`，
> 而 Table 2 与正文 §3.2 引用的 1.82 出自全库比较；原来的措辞会让读者以为摘要写错了。
> 若需要留出余量，改用 C（303 词）只需替换 `apply_abstract_and_title.py` 中的 EN_PARTS／CN_PARTS。
>
> 生成：`src/draft_abstract_variants.py`（可重跑；字数按空白分词统计，与 Frontiers 口径一致）
> 原状：`submission/abstract_rewritten.json`，**378 词**（Background 40／Methods 109／Results 183／Conclusion 46），Frontiers 上限约 350 词，**超 28 词**。

| 方案 | 从哪里删 | 删掉了什么 | 字数 |
|---|---|---|---|
| **A** | Methods | 无任何结果数字被删；压缩技术清单与四种不成比例度量 | **349** |
| **B** | Results | Methods 完整保留；六个阴性非特异术语保留三个，删去 27.8% 充分性比例 | **349** |
| **C** | 两处 + 首尾收紧 | B 的删减，另删 JADER 的“中毒性视神经病变 864.6”一项 | **303** |

三者都保留四个核心断言：信号高度特异并局限于视神经、延迟数月、经全部稳健性检验、在 JADER 独立复现。区别只在删哪一类信息：**A 删方法细节，B 删阴性对照细节，C 两者都删并留出余量**。

## A  Methods carries the cut (no result removed)

**Background.** Ethambutol is a first-line antitubercular drug whose optic neuropathy can be irreversible, and its frequency estimates vary widely with ascertainment. No pharmacovigilance analysis has profiled the ocular phenotype against the other first-line antitubercular drugs.

**Methods.** We analysed all 90 FDA Adverse Event Reporting System (FAERS) quarterly releases (2004Q1-2026Q2), de-duplicating 24,389,966 reports to 20,328,568 unique cases by the FDA case-version protocol. Four disproportionality measures were computed for 178 ocular MedDRA preferred terms across ethambutol and five comparator antitubercular drugs, with Benjamini-Hochberg control and four robustness specifications. We assessed time to onset, predictors and completeness, then combined Europe PMC, Open Targets and STRING into a mechanism network, tested enrichment, docked ethambutol against the hub targets, and interrogated the loci against FinnGen R12 phenotypes.

**Results.** Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475 (3.44%) an optic-nerve event; 45 of 152 testable ocular terms met strict signal criteria. The risk was confined to the optic nerve: optic neuropathy gave an ROR of 159.21 (95% CI 134.65-188.25), whereas no non-specific ocular complaint formed a signal in any comparison (vision blurred 1.15, cataract 0.81, dry eye 0.35, eye pain 0.32, glaucoma 0.18, ocular hyperaemia 0.18). Within the antitubercular class ethambutol had an ROR of 6.47 (5.38-7.79) for optic neuropathy, and restricting the comparison to ethambutol-containing regimens gave a rate ratio of 3.28 (1.03-10.40) against regimens without it, so the association is not explained by the tuberculosis population. The pattern replicated in JADER (1,054,239 cases; optic neuropathy ROR 571.0, toxic optic neuropathy 864.6, all control terms null). Median time to an optic-nerve event was 125 days versus 30 days for non-ocular events, and only 27.8% of cases carried enough detail for time-to-onset analysis. Enrichment converged on ferroptosis and mitochondrial integrity, and genetically proxied renal function showed no causal effect on any optic-nerve outcome (all q >= 0.87).

**Conclusion.** Ethambutol ocular toxicity is a highly specific optic-nerve signal that spares the ocular surface, is delayed by months, resists every robustness specification tested, and replicates in an independent national database. Renal impairment appears to act by raising drug exposure rather than by independently causing optic-nerve degeneration.

*合计 349 词*

---

## B  Results carries the cut (Methods intact)

**Background.** Ethambutol is a first-line antitubercular drug whose optic neuropathy can be irreversible, and estimates of its frequency vary widely with how cases are ascertained. No pharmacovigilance analysis has yet profiled the full ocular phenotype against the other first-line antitubercular drugs.

**Methods.** We analysed all 90 FDA Adverse Event Reporting System (FAERS) quarterly releases (2004Q1-2026Q2) and de-duplicated 24,389,966 reports to 20,328,568 unique cases using the FDA case-version protocol. Reporting odds ratios (ROR), proportional reporting ratios (PRR), information component lower bounds (IC025) and empirical Bayes geometric means (EBGM05) were computed for 178 ocular MedDRA preferred terms across ethambutol and five comparator antitubercular drugs, with Benjamini-Hochberg control and four prespecified robustness specifications. We assessed time to onset, predictors and report completeness, then built a mechanism network from Europe PMC literature, Open Targets and STRING, tested enrichment with g:Profiler, docked ethambutol against the hub targets, and interrogated the loci against FinnGen R12 optic-nerve phenotypes.

**Results.** Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475 (3.44%) an optic-nerve event; 45 of 152 testable ocular terms met strict signal criteria. The risk was confined to the optic nerve: optic neuropathy gave an ROR of 159.21 (95% CI 134.65-188.25), whereas no non-specific ocular complaint formed a signal in any comparison (vision blurred 1.15, cataract 0.81, ocular hyperaemia 0.18). Within the antitubercular class ethambutol had an ROR of 6.47 (5.38-7.79) for optic neuropathy, and restricting the comparison to ethambutol-containing regimens gave a rate ratio of 3.28 (1.03-10.40) against regimens without it. The pattern replicated in JADER (1,054,239 cases; optic neuropathy ROR 571.0, toxic optic neuropathy 864.6, all control terms null). Median time to an optic-nerve event was 125 days versus 30 days for non-ocular events. Enrichment converged on ferroptosis and mitochondrial integrity, and genetically proxied renal function showed no causal effect on any optic-nerve outcome (all q >= 0.87).

**Conclusion.** Ethambutol ocular toxicity is a highly specific optic-nerve signal that spares the ocular surface, is delayed by months, resists every robustness specification tested, and replicates in an independent national database. Renal impairment appears to act by raising drug exposure rather than by independently causing optic-nerve degeneration.

*合计 349 词*

---

## C  Both, with the framing tightened too

**Background.** Ethambutol is a first-line antitubercular drug whose optic neuropathy can be irreversible, and estimates of its frequency vary widely with ascertainment. No pharmacovigilance analysis has profiled the full ocular phenotype against the other first-line antitubercular drugs.

**Methods.** We analysed all 90 FDA Adverse Event Reporting System (FAERS) quarterly releases (2004Q1-2026Q2), de-duplicating 24,389,966 reports to 20,328,568 unique cases by the FDA case-version protocol. Four disproportionality measures were computed for 178 ocular MedDRA preferred terms across ethambutol and five comparator antitubercular drugs, with Benjamini-Hochberg control and four prespecified robustness specifications. We then built a mechanism network from Europe PMC, Open Targets and STRING, tested enrichment, docked ethambutol against the hub targets, and interrogated the loci against FinnGen R12 optic-nerve phenotypes.

**Results.** Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475 (3.44%) an optic-nerve event; 45 of 152 testable ocular terms met strict signal criteria. The risk was confined to the optic nerve: optic neuropathy gave an ROR of 159.21 (95% CI 134.65-188.25), whereas no non-specific ocular complaint formed a signal in any comparison (vision blurred 1.15, cataract 0.81, ocular hyperaemia 0.18). Within the class ethambutol had an ROR of 6.47 (5.38-7.79) for optic neuropathy, and restricting to ethambutol-containing regimens gave a rate ratio of 3.28 (1.03-10.40) against regimens without it. The pattern replicated in JADER (1,054,239 cases; optic neuropathy ROR 571.0, all control terms null). Median time to an optic-nerve event was 125 days versus 30 for non-ocular events. Enrichment converged on ferroptosis and mitochondrial integrity, and genetically proxied renal function showed no causal effect on any optic-nerve outcome.

**Conclusion.** Ethambutol ocular toxicity is a highly specific optic-nerve signal that spares the ocular surface, is delayed by months, resists every robustness specification tested, and replicates in an independent national database. Renal impairment appears to raise drug exposure rather than to cause optic-nerve degeneration independently.

*合计 303 词*

---

## 附：关键词超出上限

稿件中英文版均列 **10 个**关键词，Frontiers 上限为 **8 个**；
`src/build_latex.py` 里写的是 `[:8]`，即投稿用的 .tex **静默丢掉最后两个**（*molecular docking*、*Mendelian randomisation*）。

需要明确选定 8 个，而不是由位置决定。推荐去掉 *signal detection*（与*disproportionality analysis* 重叠）与 *network toxicology*（框架名，索引价值最低），保留两个方法词：

> ethambutol; optic neuropathy; pharmacovigilance; FAERS; disproportionality analysis; ferroptosis; molecular docking; Mendelian randomisation

另一种选择是沿用 `submission/abstract_rewritten.json` 里的 8 个（去掉 *molecular docking* 与 *Mendelian randomisation*），代价是丢掉两个方法词的检索入口。
