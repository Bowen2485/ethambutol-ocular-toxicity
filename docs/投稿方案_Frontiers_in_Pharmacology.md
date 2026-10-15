# 投稿方案：Frontiers in Pharmacology（定稿）

> 编制日期：2026-10-15　　稿件：`manuscript/Ethambutol_EyeTox_EN_full.md`（1,291 行 / 17,552 词）
> 中文版：`manuscript/Ethambutol_EyeTox_CN_full.md`（724 行 / 18,385 汉字）
> 目标期刊：**Frontiers in Pharmacology**（ISSN 1663-9812）

---

## 一、为何该刊是最佳选择（基于实时检索的证据）

### 证据一：该刊 2026 年仍在发表方法学精密的 FAERS 研究

| 论文 | 时间 | 与我稿的关联 |
|---|---|---|
| *Confounding-aware disproportionality analysis reveals disease-inherent versus drug-attributable endocrine safety signals of immune checkpoint inhibitors*（PMID **42416835**） | **2026 年 6 月** | **"混杂感知的不成比例分析"** —— 与我稿"按方案分层的类内比较"是同一思路 |
| *Posterior reversible encephalopathy syndrome across 22 VEGF-pathway inhibitors in the FAERS*（PMID **42494530**） | 2026 | 多药 FAERS 信号分析 |
| *A real-world pharmacovigilance study of FAERS events for bictegravir/emtricitabine/tenofovir alafenamide*（DOI 10.3389/fphar.2026.1945154） | **2026** | 抗感染药物的 FAERS 研究，**与乙胺丁醇同属抗感染药领域** |

**结论：该刊未关闭此领域，反而在发表更严格的方法学工作。** 这与 Expert Opinion on Drug Safety 的全面停收形成对照。

来源：[Retraction Watch 关于期刊政策变化的报道](https://retractionwatch.com/2025/09/16/exclusive-journal-bans-drug-safety-database-papers-as-they-flood-the-literature/)

### 证据二：我稿恰好满足该刊新增的独立验证要求

该报道指出 Frontiers 已**开始要求使用公共数据集的研究提供独立验证**。在一批缺少验证的投稿中，我稿的验证充分度构成**明确的相对优势**：

| 该刊新要求 | 我稿已具备 |
|---|---|
| **独立验证（独立数据源）** | **JADER（日本国家自发报告数据库）完整复现**：视神经病变 ROR 571（95%CI 414–788）、中毒性视神经病变 865（426–1753），而白内障 1.40、青光眼 1.26 无信号 |
| 时间稳定性 | 按接收年份分段（2016 为界），**两期独立复现**（81.9 与 86.9），对照术语两期均无信号 |
| **内部阴性对照** | **6 个非特异眼部术语在任何比较中均无信号**：视物模糊 1.15、白内障 0.81、干眼 0.35、眼痛 0.32、青光眼 0.18、眼部充血 0.18 |
| 混杂控制 | **按治疗方案分层**，解决共用药混杂：含乙胺丁醇方案 67/5,757（1.16%）对不含者 3/845（0.36%），率比 **3.28（95%CI 1.03–10.40）** |
| 与既有监管知识一致 | **与 FDA 说明书交叉核对**：乙胺丁醇、异烟肼、利奈唑胺、普托马尼的视神经警告与信号方向一致 |
| 主动交代自身局限 | 报告充分性量化（仅 **27.8%** 视神经病例可做时序分析）、日剂量不预测结局（**P = 0.55**）、铁死亡类别检验的**阴性结果也报告** |

---

## 二、投稿设置（投稿系统内需选择）

| 项目 | 建议 | 说明 |
|---|---|---|
| **期刊** | Frontiers in Pharmacology | |
| **栏目（Section）** | **Drug Safety**（首选） | 该刊设有专门发表药物警戒与药物不良反应研究的栏目。**若系统中无此确切名称**，次选 *Pharmacology of Anti-infective Drugs*（抗感染药理学，与乙胺丁醇领域直接对应）。**两者均可，选错会延迟处理 —— 投稿界面会列出全部可选栏目，以界面实际显示为准。** |
| **文章类型** | **Original Research** | 该刊原创研究的标准类型 |
| **摘要格式** | 结构化（Background / Methods / Results / Conclusion） | **我稿摘要已为结构化，无需改动** |
| **APC** | **需在投稿时确认** | Frontiers 的 APC 按期刊与文章类型分档。**我无法从官网可靠读取当前金额**（官网为 JS 渲染，抓取失败），**请在投稿系统中查看实际金额**，并询问是否可申请减免 |

---

## 三、投稿信定稿（Frontiers in Pharmacology 专用）

> 以下为可直接使用的版本，已将四个候选期刊的适配段落替换为 Frontiers 专用段落。

```
Bowen Shi, Jing Yan, Zhengzheng Wu, Siyuan Yang, Yaqin Tan, Xuan Wang
Eye Hospital, China Academy of Chinese Medical Sciences
33 Lugu Road, Shijingshan District, Beijing 100040, China

[Date]

The Editorial Office
Frontiers in Pharmacology

Dear Editors,

We submit for your consideration the manuscript entitled "Ocular toxicity of
ethambutol: a whole-database pharmacovigilance analysis of 20.3 million FAERS
cases with network toxicology, molecular docking and genetic interrogation", for
consideration as an Original Research article.

Ethambutol is a first-line antitubercular drug whose optic neuropathy is
irreversible in a substantial minority of those affected. The central difficulty
in studying it is not establishing that a signal exists but separating it from
the reporting behaviour of a tuberculosis population, in which the drug is
almost always co-prescribed with other agents that are themselves associated with
ocular events.

We designed the study around that problem, and we believe its approach answers
the expectation your journal has set for studies based on public datasets:
rather than reporting statistical associations on their own, every claim we make
is tested against an independent source.

What we did

We ingested all 90 FDA FAERS quarterly releases and de-duplicated 24,389,966
submitted reports to 20,328,568 unique cases using the FDA case-version rule.
Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event
and 475 (3.44%) an optic-nerve event; of 152 ocular terms tested, 45 met strict
signal criteria.

How the central claim is independently validated

1. Internal negative control. Not one non-specific ocular complaint formed a
   signal in any comparison - vision blurred 1.15, cataract 0.81, dry eye 0.35,
   eye pain 0.32, glaucoma 0.18, ocular hyperaemia 0.18 - while optic neuropathy
   reached an ROR of 159.21 (95% CI 134.65-188.25). A reporting artefact would
   not spare every vague symptom and single out one diagnosis.

2. The comparator is the same regimen, not the whole database. Because
   antitubercular drugs are co-prescribed, the whole-database ratio is confounded
   by the underlying disease. Stratifying by regimen, optic-nerve events occurred
   in 67 of 5,757 ethambutol-containing regimens (1.16%) against 3 of 845
   regimens without it (0.36%) - a rate ratio of 3.28 (95% CI 1.03-10.40). The
   within-class ratio is 6.47 (95% CI 5.38-7.79; 171 cases), and it survives a
   denominator restricted to anti-tuberculosis reports (ROR 7.64, 95% CI
   5.24-11.13).

3. Replication in an independent national system. The analysis was repeated in
   JADER, Japan's spontaneous reporting database, using two different coding
   systems and independent reporters. Optic neuropathy gives an ROR of 571 (95%
   CI 414-788) and toxic optic neuropathy 865 (95% CI 426-1753), with cataract
   (1.40) and glaucoma (1.26) null. The magnitudes are not comparable between the
   two systems, and we state that; the pattern replicates.

4. Replication across reporting eras. Splitting the database by receipt year
   reproduced the signal independently in both periods (optic neuropathy ROR 81.9
   for 2004-2016 and 86.9 for 2017-2026), with negative controls null in both.

5. Agreement with regulatory labelling. Current product labelling was retrieved
   for 13 of the 18 antitubercular drugs. Ethambutol carries an explicit
   optic-nerve warning and returns the strongest signal in the panel; the same
   agreement holds for isoniazid, linezolid and pretomanid.

What we report that the data cannot support

We quantify report adequacy rather than assuming it: only 27.8% of optic-nerve
cases carry enough detail for time-to-onset analysis, and on that basis we present
the temporal result as supporting rather than primary. Daily dose does not predict
optic outcome (likelihood-ratio P = 0.55), and we report that null. A two-sample
Mendelian randomisation interrogation found no causal effect of renal function on
any optic-nerve or visual phenotype (150-186 harmonised instruments per outcome
across three renal measures; all q >= 0.87), which we interpret as locating renal
impairment in exposure rather than in causation. We also report a designed test
that failed: a class-level analysis of ferroptosis inducers could not adjudicate
the mechanism, and rather than omit it we present it as evidence about the limits
of the method.

The mechanism component

This is presented as hypothesis generation, not as established mechanism.
Ethambutol has no recorded human target in Open Targets, so the network we built
is a downstream effect network rather than a target network. Its functional
enrichment converges on ferroptosis and mitochondrial integrity, which agrees with
independent experimental work on SDHB and Smad4 (Li et al., 2026). Single-cell
retinal expression data show 31 of the 33 network hubs expressed in retinal
clusters (empirical P = 0.0067 against random gene sets of the same size), with
the ferroptosis machinery - GPX4, SLC7A11, ACSL4, SDHB - abundantly represented.
Docking ranked four hubs highest at affinities of only -4.95 to -5.50 kcal/mol, and
all-atom molecular dynamics in three of those sites kept the ligand in contact
with the protein throughout the simulated window. We state plainly that the
mechanism does not depend on direct occupancy of any of these nodes.

Statements

All data are from public sources (FDA FAERS, JADER, Open Targets, STRING,
g:Profiler, Human Protein Atlas, FinnGen, OpenGWAS, PubChem, RCSB PDB). No
patient-identifiable information was accessed and no ethics approval was
required. The manuscript is original, is not under consideration elsewhere, and
all authors have approved its submission. We declare no competing interests. The
analysis code, derived tables and figures are openly available at
https://github.com/Bowen2485/ethambutol-ocular-toxicity.

We confirm that this submission has not been published previously and is not
being considered by any other journal, and that all authors meet the journal's
authorship criteria.

Yours sincerely,

Jing Yan
Eye Hospital, China Academy of Chinese Medical Sciences
[email]
```

---

## 四、投稿信中文对照

```
施博文、闫晶、吴铮铮、杨思远、谭亚琴、王璇
中国中医科学院眼科医院
北京市石景山区鲁谷路 33 号，100040

[日期]

Frontiers in Pharmacology 编辑部

尊敬的编辑：

现提交原创研究论文《乙胺丁醇的眼毒性：2 033 万例 FAERS 全库药物警戒分析结合网络毒理学、
分子对接与遗传学考察》。

乙胺丁醇是一线抗结核药物，其视神经病变在相当一部分患者中不可逆。研究该毒性的核心困难
不在于确认信号是否存在，而在于把信号与结核病人群的报告行为区分开——在这一人群中，该药
几乎总与其他本身即与眼部事件相关的药物联合处方。

本研究即围绕这一问题设计。我们相信其做法回应了贵刊对使用公共数据集的研究所提出的期望：
**不停留于报告统计学关联，而是让每一项主张都接受独立来源的检验。**

研究内容

我们纳入了全部 90 个 FDA FAERS 季度发布包，按 FDA 病例版本规则将 24 389 966 份提交报告
去重为 20 328 568 例唯一病例。在 13 804 例去重乙胺丁醇病例中，971 例（7.03%）报告了眼部
事件，475 例（3.44%）报告了视神经事件；152 个受检眼部术语中 45 个符合严格信号标准。

核心主张如何获得独立验证

一、内部阴性对照。在任何比较中，没有任何非特异性眼部主诉构成信号——视物模糊 1.15、
白内障 0.81、干眼 0.35、眼痛 0.32、青光眼 0.18、眼部充血 0.18——而视神经病变 ROR 达
159.21（95%CI 134.65–188.25）。报告偏倚不会放过所有含糊症状而单独挑出一个诊断。

二、对照是同一方案，而非全库。由于抗结核药联合处方，全库比值受基础疾病混杂。按方案分层后，
含乙胺丁醇方案中视神经事件为 67/5 757（1.16%），不含者为 3/845（0.36%），率比 3.28
（95%CI 1.03–10.40）。类内比值 6.47（95%CI 5.38–7.79；171 例），且在分母限定为抗结核
报告时仍然成立（ROR 7.64，95%CI 5.24–11.13）。

三、在独立国家系统中复现。分析在日本 JADER 中重复进行，该系统使用不同的术语编码体系与
独立的报告者。视神经病变 ROR 571（95%CI 414–788），中毒性视神经病变 865（95%CI
426–1753），而白内障（1.40）与青光眼（1.26）无信号。两系统数值量级不可直接比较，我们已
明确说明；复现的是模式。

四、跨报告时期复现。按接收年份分段后，两个时期均独立复现（视神经病变 ROR 2004–2016 年
为 81.9，2017–2026 年为 86.9），阴性对照在两期均无信号。

五、与监管说明书一致。18 种抗结核药中 13 种的现行说明书可获取。乙胺丁醇含明确的视神经
警告且给出面板中最强信号；异烟肼、利奈唑胺与普托马尼呈现同样的一致。

我们报告数据无法支持的部分

我们量化而非假定报告充分性：仅 **27.8%** 的视神经病例具备足够细节做发病时间分析，据此
我们把时序结果作为支持性而非主要证据呈现。日剂量不预测视神经结局（似然比检验 P = 0.55），
该阴性结果已报告。两样本孟德尔随机化未发现肾功能对任何视神经或视觉表型的因果效应（三个
肾功能指标各覆盖每个结局 150–186 个协调工具变量；全部 q ≥ 0.87），我们将其解读为把肾功能
不全定位在暴露环节而非因果环节。我们也报告了一项**失败的设计检验**：铁死亡诱导剂的类别
层面分析无法裁决该机制，我们没有略去它，而是作为方法局限的证据呈现。

机制部分

该部分作为**假设生成**呈现，而非既定机制。乙胺丁醇在 Open Targets 中无人类靶点记录，故
所建网络是下游效应网络而非靶点网络。其功能富集收敛于铁死亡与线粒体完整性，与 SDHB、Smad4
的独立实验研究一致（Li 等，2026）。单细胞视网膜表达数据显示 33 个网络 hub 中 31 个在
视网膜细胞簇中表达（对同规模随机基因集的经验 P = 0.0067），铁死亡机器——GPX4、SLC7A11、
ACSL4、SDHB——高表达。对接将四个 hub 排在前列，但亲和力仅 −4.95 至 −5.50 kcal/mol；
在这四个位点中的三个所做的全原子分子动力学在整个模拟窗口内保持配体与蛋白接触。我们明确
说明，本文机制不依赖药物对任一节点的直接占据。

声明

全部数据来自公开来源（FDA FAERS、JADER、Open Targets、STRING、g:Profiler、
Human Protein Atlas、FinnGen、OpenGWAS、PubChem、RCSB PDB）。未接触任何可识别患者
身份的信息，无需伦理批准。本文为原创，未同时投递他刊，全体作者已同意投稿。声明无利益
冲突。分析代码、派生表格与图件均公开可用，地址为
https://github.com/Bowen2485/ethambutol-ocular-toxicity。

我们确认本文未曾发表、亦未在他刊审稿中，且全体作者符合贵刊作者资格标准。

此致

闫晶
中国中医科学院眼科医院
[邮箱]
```

---

## 五、投稿前必须完成的事项

### 必须由你提供或确认

| 项目 | 状态 | 说明 |
|---|---|---|
| **通讯作者邮箱** | ⚠️ **需确认** | 稿件用 `20200121047@bucm.edu.cn`（**北京中医药大学**域名），单位为**中国中医科学院眼科医院**。**Frontiers 会验证通讯作者邮箱**，且域名与机构不一致可能被编辑注意。若有机构邮箱请替换 |
| **ORCID** | ⚠️ **未提供** | **Frontiers 要求通讯作者提供 ORCID**，这是投稿系统的必填项 |
| **APC 金额与经费** | ⚠️ **需确认** | 你声明无资助。Frontiers 为 OA，**请先在投稿系统中查看实际金额**，并询问减免政策。**若无法承担，应改投 Drug Safety（订阅制）** |
| **伦理批准** | ⚠️ **需机构确认** | 稿件声明无需批准（仅公开匿名数据），请确认贵院伦理委员会无异议 |
| **栏目选择** | ⚠️ **投稿界面确认** | 优先 *Drug Safety*，次选 *Pharmacology of Anti-infective Drugs*；以界面实际列表为准 |

### 我已完成的准备

| 材料 | 位置 |
|---|---|
| 正文（英文，投稿用） | `manuscript/Ethambutol_EyeTox_EN_full.md` |
| 正文（中文对照） | `manuscript/Ethambutol_EyeTox_CN_full.md` |
| 结构化摘要 | 已符合 Frontiers 要求 |
| 投稿信（英/中） | 本文件第三节、第四节 |
| STROBE / RECORD-PE 清单 | `docs/STROBE_RECORD_checklist.md` |
| 全部表格（CSV） | `tables/` |
| 全部图件（PDF + PNG） | `figures/` |
| 派生结果表 | `results/` |
| 分析代码 | `src/`（公开仓库） |
| 代码仓库 | https://github.com/Bowen2485/ethambutol-ocular-toxicity |

---

## 六、Frontiers 投稿的实操要点

| 环节 | 说明 |
|---|---|
| **投稿系统** | Frontiers 使用自有系统，需逐位作者填写信息并确认（**每位共同作者都会收到确认邮件**，请提前通知） |
| **稿件格式** | Frontiers 有指定模板；**我稿为 Markdown，投稿时需转换**。主要结构（标题、结构化摘要、关键词、正文、声明、参考文献）已齐备 |
| **参考文献格式** | 我稿参考文献为编号制（28 条）。**Frontiers 使用编号制引用，格式兼容**，但需核对具体样式 |
| **图件要求** | 需单独上传图件文件。**我稿已有 PDF 与 PNG 两种格式**，PDF 通常符合矢量图要求 |
| **审稿模式** | Frontiers 为**互动式审稿**，审稿人姓名公开，作者可直接回复。**这要求回复时格外严谨** |
| **常见退稿原因** | Frontiers 因 FAERS 论文泛滥而收紧。**退稿理由很可能是"缺乏独立验证"** —— 而这正是我稿的强项，投稿信已将此置于显著位置 |

---

## 七、若被拒稿

**很可能出现的意见及应对：**

| 可能意见 | 应对 |
|---|---|
| 要求补充实验验证机制 | 机制部分已明确标注为假设生成；引用 Li 2026（PMID 41563626）的 SDHB/Smad4 铁死亡实验研究作为独立实验支持 |
| 质疑 JADER 数值量级与 FAERS 不可比 | **稿件已明确说明**，并指出复现的是模式而非量级（JADER 中 51.6% 病例将乙胺丁醇编码为可疑药，FAERS 中比例低得多） |
| 质疑 MD 仅一个完整靶点 | **三个独立位点一致**（受体骨架 RMSD 1.18–1.34 Å、最小距离 1.76–1.18 Å），已列入局限 |
| 质疑铁死亡类别检验的阴性结果 | **已作为方法局限报告**，说明类别层面分析无法裁决细胞类型特异机制 |
| 认为机制部分可移入补充材料 | 可接受此要求，保留药物警戒主体 |

**转投顺序**：BMJ Open Ophthalmology（有 FAERS+JADER 双库设计的直接先例，2025 年发表）→ Drug Safety（订阅制，APC 低，方法学要求对口）→ Therapeutic Advances in Drug Safety
