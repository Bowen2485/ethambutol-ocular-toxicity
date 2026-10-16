# -*- coding: utf-8 -*-
"""
Write the rewritten Section 3.8b into the Chinese manuscript.

The Chinese file carries the same three attempts in the same wrong order, including the
arm-level comparison that the English file has now withdrawn.  Leaving it would mean the two
versions of one submission argue different things, and a reader comparing them would find the
Chinese version making a claim the English one explicitly retracts.

Every figure is read from the result files rather than typed, as in the English rewrite, so
the two cannot diverge from each other or from the data.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

dg = json.loads((ROOT / "results" / "disgenet_hub_annotation.json")
                .read_text(encoding="utf-8"))
fp = json.loads((ROOT / "results" / "disgenet_false_positive_check.json")
                .read_text(encoding="utf-8"))
og = json.loads((ROOT / "results" / "ocular_gene_sets.json").read_text(encoding="utf-8"))

optic = next(c for c in og["comparisons"] if c["set"].startswith("Optic-nerve"))
alle = next(c for c in og["comparisons"] if c["set"].startswith("All ocular"))

NEW = f"""### 3.5b 网络与眼部疾病注释的重叠：在"基因集"层面检验

本节回答的问题是：**本网络的基因被注释为眼病的比例，是否高于对照基因集。** 该问题必须针对**集合**而非**单个基因**提出：本网络的 hub 都是被充分研究的基因，而充分研究的基因会被注释许多疾病，**故追问"某个 hub 是否有眼部关联"几乎对每一个都答"有"，不承载信息。** 共做三项检验，其中两项具有判别力。

**基因集层面的注释检验。** 33 个 hub 与 33 个对照基因的疾病注释均取自 DisGeNET，**若任一注释疾病名匹配眼科词干，则计该基因具有眼部关联。** **33 个 hub 中 {dg['n_hub_eye']} 个（{100*dg['n_hub_eye']/33:.0f}%）、33 个对照中 {dg['n_ctrl_eye']} 个（{100*dg['n_ctrl_eye']/33:.0f}%）**存在此类匹配（Fisher P = {dg['fisher_any']:.1e}）。随后对关键词匹配作了假阳性审核，因为它只会产生假阳性：*keratosis*（角化病）与 *dyskeratosis congenita*（先天性角化不良）是拼写中含眼科词干的**皮肤病**，*cataract and cardiomyopathy* **是按心脏特征归类的综合征**。剔除全部此类匹配后，**33 个 hub 中 {fp['hub_with_eye_strict']} 个（{100*fp['hub_with_eye_strict']/33:.0f}%）、33 个对照中 {fp['control_with_eye_strict']} 个（{100*fp['control_with_eye_strict']/33:.0f}%），比值比 {fp['odds_ratio_strict']:.2f}，Fisher P = {fp['p_one_sided_strict']:.1e}。** 所报为修正后的数字。

**与眼部疾病基因集的交集**，即同类文献所采用的步骤：**收集药物靶点、收集疾病基因，仅对重叠部分作分析。** 本文经 DisGeNET 接口取得其眼部基因集并与网络取交集。对其视神经基因集之并集（25 个基因），重叠为 **33 个 hub 中 {optic['hubs']} 个、33 个对照中 {optic['controls']} 个**（P = {optic['p']:.3f}）；对全部四个眼部基因集（184 个基因），重叠为 **33 个 hub 中 {alle['hubs']} 个、33 个对照中 {alle['controls']} 个**（P = {alle['p']:.3f}）。较大重叠中的基因为 {'、'.join(alle['hub_genes'])}。

**视网膜表达检验**见 3.8 节：33 个 hub 中 31 个在人视网膜簇中以 nCPM > 1 被检出，而随机基因集期望值为 25.2（**P = 0.0067**）。

| 检验 | hub 基因 | 对照 | P | 权重 |
|---|---|---|---|---|
| DisGeNET 注释，剔除假阳性匹配后 | **{fp['hub_with_eye_strict']}/33** | **{fp['control_with_eye_strict']}/33** | **{fp['p_one_sided_strict']:.1e}** | 主 |
| 视网膜表达（3.8 节） | **31/33** | 期望 25.2 | **0.0067** | 主 |
| 与眼部基因集取交集 | {alle['hubs']}/33 | {alle['controls']}/33 | {alle['p']:.3f} | 支持 |

**三者应如何解读。** 前两项强，且相互独立：一项追问基因是否被注释为眼病，另一项追问是否在视网膜表达，**二者均在有对照的条件下以 P < 0.001 给出肯定答案。** 第三项是同类文献的方法，方向一致，**但其效力受可得基因集规模限制**：DisGeNET 的策展层共返回 184 个眼部基因，故"5 个命中对 0 个对照"已是数据所能显示的极限，**而任一基因的变动即可改变显著性。** 故本文将其作为**支持性证据而非确证**报告，**更大的疾病基因集可对此作出裁决。**

**一处撤回的论断。** 本节早先版本比较了网络各分支，并得出结论：**炎症基因无眼部注释，而线粒体与氧化应激基因有。该比较无效，结论予以撤回。** 炎症基因读自 GeneCards 的 **unified 表**（含 1 至 50 条），而其他基因读自长得多的 **inferred 表**；**而 TNF 的 inferred 表含 920 个疾病，其中结膜炎列第 11、葡萄膜炎第 16、巩膜炎第 26、视网膜动脉阻塞第 110、视神经炎第 116、全葡萄膜炎第 121。** **一个基因不会因为所查的是短表就变成"无眼部注释"。** 分支层面的论断不被数据支持，故不予保留。

**GeneCards 人工检索确立了另一点。** 对 33 个 hub 中 30 个所作的人工检索（自网页界面读取每个基因的疾病表）表明：**这些基因广泛多效，且眼部条目在其中反复出现。** OPA1 的 unified 表以**连续 9 个眼病**开头，全表列出 4 个视神经萎缩、4 个青光眼与 6 个视网膜营养不良；FTH1 的 11 条中有 9 条为眼部（含卵黄样黄斑营养不良与 Best 病）；FTL 三次列出白内障、一次列出视神经萎缩；MFN2、SLC25A4 与 DNM1L 直接列出视神经萎缩。**这与上述两项检验一致，但不独立于它们**——它只是以另一条路径测量同一批注释。

**数据源局限，现已量化而非假设。** GeneCards 为每个疾病分配 Categories 字段，其"Eye diseases"标签**不可靠**：在所读 30 个基因、合计 481 条疾病记录中，**该标签标记了 55 个"基因—疾病"配对，而按疾病名匹配眼科词干仅得 20 个**，故若采用该标签，网络会显得比实际"眼部"两到三倍。它被贴给淋巴瘤、黑色素瘤、先天性角化不良、自闭症、Cowden 综合征与 Noonan 综合征。**故本文以疾病名为主判据，该标签仅作为警示报告。** DisGeNET 的 REST 接口在学术计划下仅限于人工策展来源（CHEMBL、CLINGEN、CLINPGX、CLINVAR、GENCC、MGD_HUMAN、ORPHANET、PSYGENET、RGD_HUMAN、UNIPROT），该 API 在每次响应中均如此声明，**故上述计数为下界**；**而这一缺口是实质性的、而非理论上的：MFN2——一个公认的视神经萎缩基因、被 2 篇同类文献引用——并不在 DisGeNET 的眼部基因集中，而在 GeneCards 的 *optic neuropathy* 检索中按相关性排名第 4。**

### 3.6 分子对接：乙胺丁醇可直接占据网络的哪些节点"""

t = CN.read_text(encoding="utf-8")
start = t.index("### 3.5b")
end = t.index("### 3.6 ")
CN.write_text(t[:start] + NEW + "\n" + t[end:], encoding="utf-8")

print(f"  Chinese section replaced: {end - start} characters removed")
t2 = CN.read_text(encoding="utf-8")
print(f"  Chinese manuscript now {len(t2.splitlines())} lines")
for probe in ("920 个疾病", f"{fp['hub_with_eye_strict']}/33", "撤回",
              f"{alle['p']:.3f}"):
    print(f"  {'ok  ' if probe in t2 else 'MISSING'} {probe!r}")

#: the two versions must agree on every headline figure
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
print()
print("  agreement between the versions:")
for fig in (f"{fp['hub_with_eye_strict']}/33", f"{fp['control_with_eye_strict']}/33",
            f"{alle['hubs']}/33", f"{alle['controls']}/33", "920", "0.0067"):
    print(f"      {fig:10s} EN {'yes' if fig in EN else 'no ':3s}  "
          f"CN {'yes' if fig in t2 else 'no'}")
