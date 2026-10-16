# -*- coding: utf-8 -*-
"""
Synchronise the Chinese manuscript with the four analyses added to the English one.

The two files are parallel versions of one submission, and they have drifted: the English
version now carries the subgroup analysis, the disease-annotation cross-check, the
displacement-independent trajectory measures and the positive control, and the Chinese one
does not.  Drift matters at proofing time, when the two are read against each other.

Numbering
    The Chinese file uses its own scheme - its robustness section is 3.4c where the English
    is 3.6, and its expression section is 3.11 where the English is 3.11 too but with a
    different history.  The new sections are therefore placed by their position in the file
    and given numbers that follow the Chinese sequence, not the English one.  Forcing the two
    to share numbers would require renumbering sections the Chinese file already cross-
    references, which is a larger change than this task.

Style
    Full-width brackets and Chinese punctuation, as the rest of the file uses.  Bold is
    reserved for the same claims it emphasises in English.  Numbers, gene names, database
    names and statistics are kept in the form the English version uses so the two can be
    checked against each other mechanically.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

METHODS = """

### 2.12 视神经信号的亚组分析

在性别、年龄段、报告地区与报告时期各分层内重新计算视神经比值比，2×2 构造、ROR 与 Woolf 区间与主分析完全相同，以使分层值与主分析可直接比较。分层之间以**比值比的比值**及其 95% 区间相互比较，而非各自判读区间——因为两个分层可以同时显著、或同时为阴性，却仍然彼此不同，**唯有对比才能检验异质性**。年龄按 0～17、18～44、45～64 与 65 岁及以上分带，且仅对以"岁"记录年龄的报告分带，占去重数据库的 59.7%。性别缺失者占 12.1%，**保留为独立的"未知"分层而未剔除**，因为剔除会改变其他所有分层所对比的分母。报告地区按国家归入美洲、亚洲、欧洲与其余合并组；报告该维度是因为同类文献报告它，而**明确不予解读**，理由见 3.2c 节。

### 2.13 hub 基因的疾病注释交叉核对

检验聚焦层 hub 基因**是否被注释为与眼病相关**——这是功能富集本身无法回答的问题。对每个基因查询两个独立数据库的疾病注释：Open Targets（已用于药物—靶点图谱）与 DisGeNET（经其 REST 接口）。**若任一注释疾病名匹配眼科词干，则计该基因具有眼病关联。** 由于疾病名可能含有眼科词干却指称其他疾病——*keratosis*（角化病）与 *dyskeratosis congenita*（先天性角化不良）均为皮肤病——**故逐一列出全部匹配，并在剔除该类匹配后重做分析，两个数字均予报告**。对照集为同规模的固定无关通路基因集（33 个胰腺外分泌基因），而非与随机期望比较：**文献挖掘所得的 hub 集本身多效性极强，与任何基线比较都会显得富集。** 富集以单侧 Fisher 精确检验评估，方向事先固定。GeneCards 一并尝试但返回 HTTP 403；DisGeNET 在学术计划下仅限人工策展来源（该接口在每次响应中声明），**故所报计数为下界**。

### 2.14 与位移无关的轨迹测量

从既有轨迹计算两项量，二者均**不涉及位移**，因而均不受周期边界处理方式影响。其一为**每残基涨落（RMSF）**，在主链叠合后对 Cα 原子计算，且**仅使用蛋白**，使配体运动不能贡献其中。其二为**配体—蛋白极性接触**，逐帧按最小镜像约定统计 3.5 Å 内的供体—受体原子对；由于轨迹未为配体写入显式氢原子位置，**该量计的是潜在极性接触而非几何枚举的氢键**，故仅作三个靶点间的比较量，而非键数。**交换度**定义为第一帧中存在的具体原子对在第二帧半数时间内仍位于 3.5 Å 以内的比例：接触总数维持而身份大幅更替，表明配体留下并重建相互作用；配体离开则两者同时丧失。

### 2.15 软件与每残基接触定义

每残基接触稳定性以**绝对原子索引到蛋白子集内位置的显式查找表**计算。早期实现使用 `np.searchsorted` 与一个并不成立的边界判断，**将每个结构中的全部残基都报告为与配体接触**——301/301、428/428、841/841——并列出各序列最前端的残基为最持续接触。**该次运行的全部数值已弃用**，修正后的分析内置守卫：**若接触残基数再次等于残基总数，则拒绝写出文件。**
"""

RESULTS_3_7b = """
### 3.7b 信号在全部患者亚组中均存在，唯年龄梯度值得解读

一个经受住全部规定情景的信号会引出两个问题：它是否局限于报告更密集的某个群体；以及是否有哪个群体表现出足以解释它的差异。**二者均经检验**——按性别、年龄、报告地区与报告时期分层重新计算视神经比值比，2×2 构造、ROR 与 Woolf 区间与主分析相同，使数值可直接比较。

| 分层 | 病例数 | 视神经事件 | ROR（95%CI） | 与参照层的比值比之比 |
|---|---|---|---|---|
| **性别** | | | | |
| 女性 | 5 987 | 136 | 44.72（37.65–53.12） | 参照 |
| 男性 | 6 324 | 113 | 50.13（41.45–60.62） | 1.12（0.87–1.45） |
| 未知 | 1 492 | 46 | **97.55**（72.17–131.85） | 2.18（1.54–3.09） |
| **年龄** | | | | |
| 0～17 | 740 | 8 | 21.23（10.49–42.98） | 参照 |
| 18～44 | 3 614 | 79 | 23.55（18.78–29.54） | 1.11（0.53–2.33） |
| 45～64 | 2 931 | 51 | 34.71（26.23–45.93） | 1.63（0.77–3.49） |
| **65 及以上** | 3 247 | 87 | **114.73**（91.91–143.22） | **5.40（2.58–11.32）** |
| 未知 | 3 271 | 70 | 61.91（48.73–78.66） | 2.92（1.38–6.14） |
| **报告地区** | | | | |
| 美洲 | 4 349 | 79 | 55.70（44.49–69.74） | 参照 |
| 亚洲 | 3 583 | 81 | 42.19（33.37–53.34） | 0.76（0.55–1.05） |
| 欧洲 | 3 334 | 108 | 40.12（32.97–48.82） | 0.72（0.53–0.97） |
| 其余地区 | 959 | 6 | 5.62（2.51–12.60） | 0.10（0.04–0.23） |
| 其余／未知 | 1 578 | 21 | 34.51（22.38–53.23） | 0.62（0.38–1.01） |
| **报告时期** | | | | |
| 2004～2016 | 2 506 | 58 | 60.13（46.23–78.22） | 参照 |
| 2017～2026 | 11 297 | 237 | 45.91（40.27–52.34） | 0.76（0.57–1.02） |

**信号在每一个分层中均存在**，这正是真实关联应有的样子，也是本分析作为**一致性检验而非新发现**报告的原因。分层之间相互比较（而非各自孤立判读）后，有五个对比的区间排除 1：未知性别对已知、65 岁及以上与年龄未知两组对最年轻组、欧洲与其余地区合并组对美洲。**其中三个不应读作效应**，理由在此给出而非留给读者。

**性别未知是报告填写稀疏的标志，而非危险因素。** 它的比值在表中最高（97.55），诱人将其作为发现报告。**但它不是**：缺失性别的报告即结构化数据更不完整的报告，而完整度本身与是否记录了严重事件相关。**年龄未知青同样如此**（61.91）。

**报告地区不可解读，理由已在前文确立。** 3.2c 节已表明 FAERS 的国家计数衡量的是**国家报告强度而非患者数量**，故以国家定义的分层必然继承该局限；解读地区列将与本文已提出的论证相矛盾。"其余地区"合并组**仅基于 6 例视神经事件，在任何有意义的意义上都不可估计**。

**年龄梯度是唯一值得解读的对比。** 风险在四个年龄带中单调上升，65 岁及以上组与最年轻组的比值比为 5.40（2.58–11.32）。这与 3.4 节的连续年龄效应一致——每增加一岁，眼部事件的比值增加（校正 OR 1.009，95%CI 1.005～1.012）。**对同一数据库的两次分析相互一致并非独立验证，本文也不如此表述**；它所确立的是：**年龄关联不是"把年龄建模为连续变量"所产生的假象。**

**本分析增补了什么，未增补什么。** 它增补的是一个**阴性结果**——没有任何亚组应为该信号负责，而这恰是审稿人对"在单一人群中测得的关联"所提的问题。**它未增补新的危险因素**：每一个经得起校正的对比，要么是报告假象，要么是不可解读的地理，要么是对已报告年龄效应的复述。
"""

RESULTS_3_8b = """
### 3.8b hub 基因的眼病注释显著多于对照集

富集说明该基因集**关于什么**，却未说明该集**与眼是否相关**。这一点单独检验：对每个 hub 查询其在独立数据库中被注释的疾病，并将 hub 集与同规模的固定无关通路对照集（33 个胰腺外分泌基因）比较。**若任一注释疾病名匹配眼科术语表，则计该基因具有眼病关联。** 检验为单侧 Fisher 精确检验，因为预期是有方向的：**为眼部毒性构建的网络，其眼病注释应比任意基因集更常见。**

**结果完全取决于所查询的数据库，而最初的选择是错的。** 对 Open Targets 与 HPO 注释服务这两个覆盖面窄的人工策展资源，33 个 hub 中 10 个（30%）、33 个对照中 8 个（24%）具有眼病关联——**无富集（Fisher P = 0.39）**。对疾病词表宽得多的 DisGeNET，**33 个 hub 中 20 个（61%）、33 个对照中 4 个（12%）**具有——**比值比 9.95（Fisher P = 4.1 × 10⁻⁵）**。**造成阴性结果的原因看来是选源过窄，而非网络本身。**

**随后对关键词匹配作了假阳性审核**，因为它只会产生假阳性。*keratosis*（角化病）与 *dyskeratosis congenita*（先天性角化不良）是拼写中含有眼科词干的**皮肤病**，*cataract and cardiomyopathy* **则是按心脏特征归类的综合征**。剔除全部此类匹配后，**33 个 hub 中 18 个（55%）、33 个对照中 4 个（12%）**，比值比 7.82，**Fisher P = 2.6 × 10⁻⁴**。富集经得起该修正，**所报为修正后的数字**。

| 数据源 | hub 具眼病注释 | 对照 | Fisher P |
|---|---|---|---|
| Open Targets + HPO | 10/33（30%） | 8/33（24%） | 0.39 |
| DisGeNET，全部匹配 | 20/33（61%） | 4/33（12%） | 4.1 × 10⁻⁵ |
| **DisGeNET，剔除假阳性后** | **18/33（55%）** | **4/33（12%）** | **2.6 × 10⁻⁴** |

**方法的阳性对照得到满足。** OPA1 被注释 13 种眼病，包括显性遗传性视神经萎缩与视神经病变；DNM1L 被注释视神经萎缩 1 型与 5 型；MFN2 被注释视神经萎缩与视网膜营养不良。**这三个基因的蛋白产物作用于线粒体、且是视神经萎缩的公认病因，被该方法如实检出**——故该检验能发现真实存在的东西，而非什么都能匹配。

**而位于所提机制中心的三个基因则缺席，这构成对机制的限定而非支持。** GPX4（注释 15 种疾病）、SLC7A11（1 种）与 ACSL4（15 种）**完全没有眼病注释**。因此**铁死亡的终端机器在所查三个数据源中均未被注释为眼部疾病，而线粒体与炎症节点则被注释**。正确的读法是：**该网络的眼部证据位于其线粒体与炎症分支**——OPA1、DNM1L、MFN2、TNF、TP53——而**铁死亡的发现依赖于 3.5 节的富集分析与 3.11 节的视网膜表达数据，并不依赖于疾病注释**。本文的机制论断不要求 GPX4 是一个眼病基因，**也不应被读作如此**。

**数据源的限制。** GeneCards 经查询返回 HTTP 403；DisGeNET 的 REST 接口在学术计划下仅限人工策展来源（CHEMBL、CLINGEN、CLINPGX、CLINVAR、GENCC、MGD_HUMAN、ORPHANET、PSYGENET、RGD_HUMAN、UNIPROT），该 API 在每次响应中均如此声明。**故上述计数为下界而非完整注释**，获得授权的 DisGeNET 订阅或 GeneCards 许可会将其提高。同类文献的 4 篇对照论文中有 2 篇以 GeneCards 与 DisGeNET 联合构建疾病靶点；**该组合在此不可得，本文如实指明所替换的来源，而非隐去不提。**
"""

RESULTS_3_9b = """
**另有两项测量以不依赖位移的路径检验同一结论。** 其一是**每残基涨落（RMSF）**，它说明结合位点是刚性还是蛋白在其周围呼吸；其二是**配体—蛋白极性接触普查**，它区分"保持原有伙伴的配体"与"留在原地但交换伙伴的配体"。

| 测量项 | NFE2L2 | HMOX1 | MFN2 |
|---|---|---|---|
| 分析的 Cα 残基数 | 301 | 428 | 841 |
| **RMSF 全程均值** | **0.68 Å** | **0.66 Å** | **0.65 Å** |
| RMSF 最大值 | 0.92 Å | 0.86 Å | 0.95 Å |
| 首帧 3.5 Å 内极性接触数 | 63 | 175 | 88 |
| 后半段极性接触数 | **80.0** | **189.2** | 71.7 |
| 全程最大值 | 159 | 215 | 108 |
| **首帧原子对在后半段仍存在** | **0.11** | **0.21** | **0.14** |

**涨落很低，且在三个大小相差极大的蛋白之间几乎相同。** Cα RMSF 均值 0.65～0.68 Å、最大值不足 1 Å，表明与配体接触的区域属于各自结构中较刚性的部分，与主链 RMSD 1.18～1.34 Å 一致。**这对解读有意义：配体并非因为位点在其周围瓦解而丢失。**

**极性接触普查是"重排而非离开"的第三条证据。** 在三个靶点中，配体—蛋白极性接触数在全程**维持或增加**——63 增至 80，175 增至 189——**故配体并未丧失其极性接触**。然而首帧中存在的**具体**原子对，在后半段仍位于 3.5 Å 以内的**仅 11%～21%**。**接触总数维持而身份大幅更替，正是配体留在口袋内并在其中重建相互作用的特征**，与配体 RMSD 及接触存活比例所指示的行为一致。**与那两项不同的是，本测量不涉及位移，故不受轨迹成像方式影响。**

关于极性接触判据应作如下说明：它统计 3.5 Å 内的供体—受体原子对，而非几何枚举氢键，因为轨迹写入时未为配体保留显式氢原子位置，而 3.5 Å 是此类原子对的常规上界。**因此它统计的是潜在极性接触而非已形成的氢键，本文将其用作三个靶点之间的比较量，而非键数。**
"""


def main() -> None:
    text = CN.read_text(encoding="utf-8")
    before = len(text.splitlines())

    # ---- methods: append after 2.11, which is the last methods subsection
    anchor_m = "## 3 结果"
    if "### 2.12" in text:
        print("  methods sections already present")
    else:
        assert anchor_m in text, "could not find the results heading to anchor the methods"
        text = text.replace(anchor_m, METHODS.strip() + "\n\n" + anchor_m, 1)
        print("  inserted methods 2.12-2.15")

    # ---- results 3.7b: before the expression section, which follows the MR section
    anchor_r1 = "### 3.11 网络节点在视网膜中表达"
    if "### 3.7b" in text:
        print("  3.7b already present")
    else:
        assert anchor_r1 in text, "could not find the expression section"
        text = text.replace(anchor_r1, RESULTS_3_7b.strip() + "\n\n" + anchor_r1, 1)
        print("  inserted results 3.7b (subgroup analysis)")

    # ---- results 3.8b: after the enrichment discussion, before the docking section
    anchor_r2 = "### 3.6 分子对接"
    if "### 3.8b" in text:
        print("  3.8b already present")
    else:
        assert anchor_r2 in text, "could not find the docking section"
        text = text.replace(anchor_r2, RESULTS_3_8b.strip() + "\n\n" + anchor_r2, 1)
        print("  inserted results 3.8b (disease annotation)")

    # ---- the trajectory measures belong inside the MD section, before the section ends
    if "RMSF 全程均值" in text:
        print("  trajectory measures already present")
    else:
        anchor_r3 = "### 3.7 遗传学考察"
        assert anchor_r3 in text, "could not find the genetics section"
        text = text.replace(anchor_r3, RESULTS_3_9b.strip() + "\n\n" + anchor_r3, 1)
        print("  inserted trajectory measures before the genetics section")

    CN.write_text(text, encoding="utf-8")
    after = len(text.splitlines())
    print(f"\n  lines: {before} -> {after}  (+{after - before})")

    # ---- verify the numerals the analysis produced are all present
    REQUIRED = ["44.72", "50.13", "97.55", "21.23", "114.73", "5.40", "2.58–11.32",
                "55.70", "60.13", "9.95", "7.82", "2.6 × 10⁻⁴", "4.1 × 10⁻⁵",
                "0.68 Å", "0.65 Å", "189.2", "0.11", "0.21", "0.14",
                "OPA1", "DNM1L", "MFN2", "GPX4", "SLC7A11", "ACSL4",
                "GeneCards", "DisGeNET", "Open Targets"]
    missing = [r for r in REQUIRED if r not in text]
    print(f"  required figures present: {len(REQUIRED) - len(missing)}/{len(REQUIRED)}")
    if missing:
        print(f"  MISSING: {missing}")

    # ---- English and Chinese must agree on every headline figure
    EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
    SHARED = ["159.21", "6.47", "3.28", "13,804", "571.0", "864.6", "27.8",
              "0.020", "1.680", "266", "186", "115"]
    print("\n  agreement between the two versions on shared figures:")
    bad = 0
    for s in SHARED:
        in_en, in_cn = s in EN, s in text
        mark = "both" if in_en and in_cn else ("EN only" if in_en else "CN only")
        if in_en != in_cn:
            bad += 1
            print(f"      {s:12s} {mark}   <-- check")
    if not bad:
        print("      all present in both")


if __name__ == "__main__":
    main()
