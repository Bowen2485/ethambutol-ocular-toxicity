# -*- coding: utf-8 -*-
"""
Write the GeneCards findings into the Chinese manuscript, replacing the section that the
data contradicted.

The English version carried the claim "GPX4, SLC7A11 and ACSL4 carry no eye-disease
annotation at all", taken from DisGeNET.  The Chinese version carries the same sentence, and
GeneCards contradicts it for SLC7A11, so both need the correction rather than only the one
that was edited first.

The replacement adds what the manual pass produced: the arm-by-arm breakdown, the four
disagreements between the two databases, and the measured unreliability of GeneCards'
"Eye diseases" category tag.  Those figures are taken from results/genecards_readings.json
rather than typed, so they cannot drift from the file that holds them.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"
READINGS = ROOT / "results" / "genecards_readings.json"

d = json.loads(READINGS.read_text(encoding="utf-8"))
data = d["data"]
n_genes = len(data)
n_disorders = sum(v["n_disorders"] for v in data.values())
by_cat = sum(v["by_category"] for v in data.values())
by_name = sum(len(v["eye_core"]) for v in data.values())

t = CN.read_text(encoding="utf-8")

#: the sentence that must go, in the form the Chinese file holds it
OLD_ANCHOR = "**而位于所提机制中心的三个基因则缺席，这构成对机制的限定而非支持。**"

#: locate the block to replace: from that paragraph to the start of the next section
start = t.find(OLD_ANCHOR)
if start < 0:
    raise SystemExit("the section to replace was not found in the Chinese manuscript")

#: the block ends where the limitation paragraph ends, before the docking section or the
#: next heading
nxt = t.find("\n### ", start)
if nxt < 0:
    nxt = len(t)
block = t[start:nxt]

REPLACEMENT = f"""**对 33 个 hub 中的 19 个所做的人工 GeneCards 检索，区分了网络哪些部分带有眼部注释、哪些没有。** GeneCards 禁止自动化访问，故每个基因的 Disorders 表均自网页界面读取，逐条记录来源，且所读者为完整表格而非片段。按节点所属过程归类后，分离十分清晰：

| 网络分支 | 已读 | 以眼部疾病为定义特征者 | 基因 |
|---|---|---|---|
| **线粒体** | 9 个中的 3 个 | **3** | MFN2、SLC25A4、SDHB |
| **氧化应激** | 9 个中的 5 个 | **3** | TP53、SOD2、SLC7A11 |
| **炎症反应** | **11 个中的 11 个** | **0** | TNF、IL6、STAT3、NFE2L2、HMOX1、KEAP1、MAPK1、AKT1、BCL2、BAX、CASP3 |
| **铁死亡终端酶** | 3 个中的 3 个 | 1 | 仅 SLC7A11；GPX4 与 ACSL4 均无 |

线粒体节点直接以疾病名称标注：MFN2 被注释为伴视神经萎缩的遗传性运动感觉神经病 VIA 型、视神经萎缩附加综合征、视神经萎缩 1 型、视网膜疾病与视网膜色素变性 1 型；SLC25A4 被注释为伴线粒体 DNA 缺失的进行性眼外肌麻痹，以及 Kearns-Sayre 综合征——**后者的诊断标准即包含色素性视网膜病变**。氧化应激节点标注了眼部肿瘤与糖尿病视网膜病变。**而炎症分支为空，且这一"空"是完整结果而非抽样产物：归入该分支的全部 11 个基因均已读完。**

**此处更正本稿件早先版本中的一句话。** 早先版本称"GPX4、SLC7A11 与 ACSL4 完全没有眼病注释"——该结论取自 DisGeNET，在**所查询的两个数据库范围内**成立，**而 GeneCards 与之矛盾：SLC7A11 被注释为视网膜疾病。** 更正后的表述更窄，且为两库数据共同支持：**本网络的眼部注释位于其线粒体与氧化应激节点；炎症反应基因与铁死亡终端酶（GPX4、ACSL4）均无，而 SLC7A11——一个胱氨酸转运体而非终端酶——有。** 故机制的铁死亡部分依赖于 3.5 节的富集分析与 3.8 节的视网膜表达数据，**并不依赖于疾病注释**，且 **GPX4 无需是一个眼病基因，该论断亦可成立。**

**两库之间的四处分歧本身即具信息量。** SLC7A11 在 GeneCards 中被注释为视网膜疾病，在 DisGeNET 中仅 1 个疾病；HMOX1 在 DisGeNET 中被注释为视网膜疾病，在 GeneCards 中为 6 个非眼部疾病；CASP3 在 DisGeNET 中为糖尿病视网膜病变与视网膜脱离，在 GeneCards 中仅食管癌；GPX4 在 DisGeNET 中无眼病注释，而 GeneCards 给两个**并非眼病**的疾病贴上了眼部类别标签。**四处中两处的方向相反。** 疾病注释既是数据库词表与策展策略的属性，也与生物学同等重要——**这正是本分析并列报告两个数据库、而不合并为单一数字的原因。**

**数据源局限，现已量化而非假设。** GeneCards 为每个疾病分配 Categories 字段，而其中的"Eye diseases"标签**不可靠**：BCL2 页面上它被贴给淋巴瘤，SDHB 页面上贴给黑色素瘤与先天性角化不良，AKT1 页面上贴给自闭症与 Cowden 综合征，MAPK1 页面上贴给 Noonan 综合征。**在所读 19 个基因合计 {n_disorders} 条疾病记录中，该标签标记了 {by_cat} 个"基因—疾病"配对，而按疾病名匹配眼科词干仅得 {by_name} 个——故若采用类别标签，hub 集会显得比实际"眼部"两到三倍。** 因此本文以疾病名为主判据，类别列仅作为警示报告。DisGeNET 的 REST 接口在学术计划下同样仅限于人工策展来源（CHEMBL、CLINGEN、CLINPGX、CLINVAR、GENCC、MGD_HUMAN、ORPHANET、PSYGENET、RGD_HUMAN、UNIPROT），该 API 在每次响应中均如此声明，**故上述计数为下界而非完整注释**。同类文献的 4 篇对照论文中有 2 篇以 GeneCards 与 DisGeNET 联合构建疾病靶点；**此处 GeneCards 不允许自动化检索，故该组合仅对所报告的基因以人工方式完成，未及全部。**"""

t = t[:start] + REPLACEMENT + t[nxt:]
CN.write_text(t, encoding="utf-8")

print(f"  replaced a block of {len(block)} characters")
print(f"  figures taken from the reading file: {n_genes} genes, {n_disorders} disorder "
      f"entries, {by_cat} category tags, {by_name} name matches")
print(f"  Chinese manuscript now {len(t.splitlines())} lines")

# confirm the corrected claim and the removed one
for phrase, expect in (("SLC7A11 被注释为视网膜疾病", True),
                       ("完全没有眼病注释", False)):
    present = phrase in t
    print(f"  {'ok  ' if present == expect else 'CHECK'} {phrase!r} present={present} "
          f"(expected {expect})")
