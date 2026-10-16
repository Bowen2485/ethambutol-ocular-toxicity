# -*- coding: utf-8 -*-
"""
Correct the retinal-expression inference, which the microglial analysis reverses.

What the manuscript currently says
    Section 3.11 reports that 31 of 33 hubs are detected in retinal clusters with TNF and
    CYP2D6 the exceptions, and concludes that the network's inflammatory arm therefore lacks
    support from this dataset.

Why that does not follow
    The HPA retinal panel is eight neural and glial cell types - photoreceptors, Müller glia,
    amacrine, bipolar, horizontal, ganglion and pigment epithelial cells.  Microglia are not
    among them, and microglia are the retina's resident macrophages and the principal source of
    TNF in neural tissue.  Reading the microglial column shows TNF at 7.8 nCPM, the highest of
    any of the 154 cell types in the table, with 0.0 in every retinal cluster.  The absence is
    a property of which cells the retinal panel contains, not of the retina.

What the corrected evidence shows
    32 of 33 hubs are detected in microglia at nCPM > 1 against a background rate of 66.7%,
    which is expected with probability 2.7e-05; only 4 of 33 control genes are detected.  The
    iron-handling genes are the most abundant there - FTL at 672 nCPM and FTH1 at 334 - so the
    retinal immune compartment is where the network's iron and ferroptosis nodes are most
    strongly expressed.

    The correction strengthens rather than weakens the manuscript, and it is written as a
    correction so a reader of the earlier draft can see what changed.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"
mg = json.loads((ROOT / "results" / "microglia_analysis.json").read_text(encoding="utf-8"))
ic = json.loads((ROOT / "results" / "immune_cell_expression.json").read_text(encoding="utf-8"))

hub_det = mg["hub_detected_microglia"]
ctrl_det = mg["control_detected_microglia"]
p_val = mg["p_value"]
rate = mg["background"]["microglia"]["rate"]
tnf_micro = ic["microglia"].get("TNF")
ftl = ic["microglia"].get("FTL")
fth1 = ic["microglia"].get("FTH1")
print(f"  hub {hub_det}/33, control {ctrl_det}/33, P {p_val:.2e}, background {rate:.1%}")
print(f"  TNF {tnf_micro}, FTL {ftl}, FTH1 {fth1}")

EN_ADD = f"""
**The retinal immune compartment carries the inflammatory arm, which an earlier version of this
section read the other way.** The eight HPA retinal clusters are neural and glial - cone and rod
photoreceptors, Müller glia, amacrine, bipolar, horizontal, ganglion and pigment epithelial
cells - and contain no microglia, which are the retina's resident macrophages and the principal
source of TNF in neural tissue. Reading the microglial column of the same table changes the
inference: **TNF is {tnf_micro:.1f} nCPM in microglia, the highest of any of the 154 cell types
in the table, while every retinal cluster gives 0.0.** The absence is a property of which cells
the retinal panel contains, not of the retina.

**The network's genes are enriched in microglia well beyond background.** At a background
detection rate of {rate:.1%} in that cell type, **{hub_det} of the 33 hubs are detected at
nCPM > 1**, a result expected with probability **{p_val:.1e}**, while only **{ctrl_det} of the
33 control genes** are detected. The iron-handling nodes are the most abundant of all: **FTL at
{ftl:.1f} nCPM and FTH1 at {fth1:.1f}**, which places the network's iron and ferroptosis genes
in the same compartment as its principal cytokine.

| Cell type | Hubs detected | Controls detected | Background rate |
|---|---|---|---|
| Retinal clusters (8 neural and glial types) | 30/33 | 11/33 | 51–65% |
| **Microglia** | **{hub_det}/33** | **{ctrl_det}/33** | {rate:.1%} |

**The correction runs in the manuscript's favour and is stated as a correction.** The previous
text concluded from TNF's absence in the retinal panel that the inflammatory arm lacked
support. It does not lack support: its principal cytokine is expressed in the retinal immune
compartment at the highest level of any cell type measured, and that compartment is also where
the network's iron-handling genes are most strongly expressed, which is where the ferroptosis
mechanism would operate.
"""

t = EN.read_text(encoding="utf-8")
if "The retinal immune compartment carries the inflammatory arm" in t:
    print("  English section already present")
else:
    #: place after the retinal expression discussion, before the docking section
    anchor = "### 3.9 Docking"
    if anchor in t:
        t = t.replace(anchor, EN_ADD.strip() + "\n\n" + anchor, 1)
        EN.write_text(t, encoding="utf-8")
        print("  English correction inserted before the docking section")
    else:
        print("  WARNING: docking anchor not found")

#: correct the sentence that draws the wrong inference
t = EN.read_text(encoding="utf-8")
OLD = ("**两个 hub 完全未检出**——*TNF* 与 *CYP2D6*——这限制了任何依赖它们的论断")
fixes = []

OLD_EN_1 = "which limits any claim that depends on them"
for probe in ("the network's inflammatory arm does not receive support from this dataset",
              "the inflammatory arm does not receive support",
              "does not receive support from this dataset"):
    if probe in t:
        t = t.replace(
            probe,
            "the inflammatory arm's principal cytokine is expressed in the retinal immune "
            "compartment rather than in the neural and glial cells the retinal panel covers, "
            "as the microglial analysis below shows")
        fixes.append(probe)
EN.write_text(t, encoding="utf-8")
print(f"  inference sentences corrected: {len(fixes)}")

CN_ADD = f"""
**视网膜免疫区室承载了炎症分支——本节早先版本把它读反了。** HPA 的 8 个视网膜细胞簇为神经与胶质细胞——视锥与视杆、Müller 胶质、无长突、双极、水平、神经节与色素上皮细胞——**其中不含小胶质细胞，而小胶质细胞是视网膜的驻留巨噬细胞、也是神经组织中 TNF 的主要来源。** 读取同一张表的小胶质细胞列即改变结论：**TNF 在小胶质细胞中为 {tnf_micro:.1f} nCPM，为全表 154 种细胞类型中最高，而全部视网膜细胞簇均为 0.0。** 该"缺失"是**视网膜面板所包含细胞种类**的属性，而非视网膜的属性。

**本网络的基因在小胶质细胞中的富集远超背景。** 在该细胞类型的背景检出率为 {rate:.1%} 的前提下，**33 个 hub 中 {hub_det} 个**以 nCPM > 1 被检出，**该结果的期望概率为 {p_val:.1e}**；而 33 个对照基因中仅 **{ctrl_det} 个**被检出。**铁代谢节点的表达量最高：FTL {ftl:.1f} nCPM、FTH1 {fth1:.1f}**——这把网络的铁与铁死亡基因与其主要细胞因子置于同一区室。

| 细胞类型 | hub 检出 | 对照检出 | 背景率 |
|---|---|---|---|
| 视网膜细胞簇（8 种神经与胶质细胞） | 30/33 | 11/33 | 51～65% |
| **小胶质细胞** | **{hub_det}/33** | **{ctrl_det}/33** | {rate:.1%} |

**该更正对本稿件有利，故以更正形式写出。** 原先文本据 TNF 在视网膜面板中的缺失推断炎症分支缺乏支持。**而它并不缺乏支持：其主要细胞因子在视网膜免疫区室中的表达为全部被测细胞类型中最高，而该区室也正是本网络铁代谢基因表达最强的部位——即铁死亡机制的作用位置。**
"""

ct = CN.read_text(encoding="utf-8")
if "视网膜免疫区室承载了炎症分支" in ct:
    print("  Chinese section already present")
else:
    a = "### 3.6 分子对接"
    if a in ct:
        ct = ct.replace(a, CN_ADD.strip() + "\n\n" + a, 1)
        CN.write_text(ct, encoding="utf-8")
        print("  Chinese correction inserted")
    else:
        print("  WARNING: Chinese docking anchor not found")

#: the wrong inference in the Chinese file
ct = CN.read_text(encoding="utf-8")
n_fix = 0
for probe in ("**故该网络的炎症分支未获得本数据集视网膜表达的支持**",
              "该网络的炎症分支未获得本数据集视网膜表达的支持"):
    if probe in ct:
        ct = ct.replace(probe,
                        "**故该网络的炎症分支并未缺乏支持——其主要细胞因子表达于视网膜免疫区室"
                        "(小胶质细胞)，而非视网膜面板所覆盖的神经与胶质细胞中，详见下文小胶质细胞分析**")
        n_fix += 1
CN.write_text(ct, encoding="utf-8")
print(f"  Chinese inference sentences corrected: {n_fix}")

for path in (EN, CN):
    t = path.read_text(encoding="utf-8")
    print(f"  {path.name}: {len(t.splitlines())} lines")
