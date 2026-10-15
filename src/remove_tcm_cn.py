# -*- coding: utf-8 -*-
"""
Remove the traditional Chinese medicine component from the Chinese manuscript and
replace the affected sections with translations of the revised English text.

Only nine locations are affected, so the manuscript is edited in place rather than
rewritten.  The removed material is the "clear yang failing to ascend" mechanism
section (原 4.3), the therapeutic-method and candidate-formula section (原 4.4), the
phytochemical docking results, and the TCM framing in the title, abstract and
introduction.

Usage
    python src/remove_tcm_cn.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
TAB = ROOT / "tables"
DOCK = ROOT / "docking"

CN = MAN / "论文_中文版.md"

TITLE = ("乙胺丁醇眼毒性：基于 2 033 万例 FAERS 全库的药物警戒分析，"
         "结合网络毒理学、分子对接与视神经表型的遗传学考察")

INTRO_TAIL = """现有文献存在两处空白。**其一**，尚无研究在 FAERS 全库范围内、以术语级
不成比例分析并设正式多重检验校正的方式，将乙胺丁醇完整眼部表型与同类抗结核药对照
（现有药物警戒工作基于 VigiBase 器官系统分组〔PMID 42240730〕）。**其二**，也是对本病
解读更为关键的一点：**信号的特异性从未以自身内部对照检验过**。一种损伤视神经的药物，
应当对"视神经"与"色觉"类术语产生信号，同时使用药者的泛化眼部主诉——干眼、眼痛、白内障、
结膜炎——维持在或低于背景水平；现有文献未见报告这一对照。

为此本研究开展四项互补分析：①FAERS 全库不成比例分析，采用扩展眼科术语面板，
并内置**阴性对照术语**与**四种稳健性口径**；②病例层面刻画发病时间、预测因素与报告充分性；
③机制网络分层构建、功能富集，并将乙胺丁醇对接至 hub 靶点；④对所涉暴露做遗传学考察
（FinnGen 视神经表型）。药物警戒部分为主要分析，机制与遗传学部分为假设生成。"""

DOCKING_CN = """### 3.6 分子对接：乙胺丁醇可直接占据网络的哪些节点

机制网络描述的是"哪些过程发生了失调"，而非"药物结合在哪里"。为回答后一个较窄的问题——
乙胺丁醇本身能否占据该网络中的节点——将药物对接至全部 14 个 hub 靶点：**14 次运行全部完成**。

对接方案以共晶配体回对接作对照：碳酸酐酶Ⅱ／乙酰唑胺重现晶体构象，对称校正
**RMSD 1.795 Å**，通过 2.0 Å 判据；二氢叶酸还原酶／甲氨蝶呤（33 个重原子柔性配体）
RMSD 5.863 Å 未通过，已作为"大柔性配体不适用"的方法学局限如实报告。

乙胺丁醇的对接打分介于 **−3.96 至 −5.50 kcal/mol**（表7）。最有利者为 TNF（−5.50）、
MFN2（−5.21）、HMOX1（−5.09）、NFE2L2（−5.01）与 BCL2（−4.95）；最弱者为
GPX4（−3.96）、SMAD4（−4.06）与 AKT1（−4.05）。打分总体不高且区间很窄——对一个只有
三个可旋转键、强极性、且并非针对这些口袋设计的小分子而言，这是预期结果。
**可解读的是排序而非绝对值**：药物被预测更易结合炎症与氧化应激节点（TNF、HMOX1、
NFE2L2）以及线粒体动力学节点 MFN2，而不易结合铁死亡执行机器（GPX4、ACSL4）或
TGF-β 效应分子 SMAD4。这一排序与"乙胺丁醇作用于铁死亡级联的**上游**——扰动氧化还原
与炎症环境，而非结合该通路的终端酶"相符，与富集分析提示的模式一致。"""

DISC_MECH_CN = """### 4.3 机制

富集结果应作为假设而非证明来阅读，但它与最新实验工作的吻合程度异常之高。KEGG 首位为
**铁死亡**，其驱动基因 *GPX4*、*SLC7A11*、*ACSL4*、*SDHB*、*SMAD4*、*HMOX1* 正是
2026 年一项研究在乙胺丁醇处理的视网膜神经节细胞中实验证实的通路轴——该研究显示
乙胺丁醇经 Smad4 抑制 SDHB，瓦解 GPX4/SLC7A11 抗氧化防御〔PMID 41563626〕。
线粒体被膜信号与 *OPA1*、*MFN2* 的 hub 位置，连接至遗传易感性文献〔PMID 34676220〕；
BDNF-NTRK2 结果与 Müller 胶质细胞保护实验相符，后者中 pan-TRK 阻断消除了保护作用
〔PMID 41184893〕。核心面板中的锌代谢基因（*MCOLN1*、*SLC30A10*、*MT1A*）连接至
溶酶体锌蓄积的观察〔PMID 19063910〕以及"治疗前血浆锌偏低预示风险"的临床发现〔PMID 659802〕。

同样有必要说明网络**未能**显示的内容。因 Open Targets 中乙胺丁醇**无人类靶点记录**，
本分析中的任何结论都不能指出药物在人类细胞中结合于何处。网络描述的是"哪些过程发生失调"，
而这恰是选择干预节点所需要的，也是靶点数据库中"无条目可查"所无法提供的。

值得注意的是，对接结果与富集结果相互支持：乙胺丁醇被预测更易占据 TNF、HMOX1、NFE2L2
（炎症与氧化应激的上游节点），而对 GPX4、ACSL4（铁死亡终端执行分子）结合较弱。
两条独立证据线指向同一结论——**乙胺丁醇作用于铁死亡级联的上游**，这为"补充抗氧化底物
或上游抗炎干预可能优于直接抑制脂质过氧化"提供了可检验的假设。"""

DISC_LIMIT_CN = """*分子对接为打分近似。* Vina 打分与亲和力的相关性仅为中等；方案采用刚性受体；
搜索盒由共晶配体或几何口袋预测确定，而非实验定位。二氢叶酸还原酶回对接未通过
（5.86 Å），本文如实报告。此处的对接仅限乙胺丁醇本身，用于按预测占据能力对 hub 靶点排序；
**不能**据此确立结合，也不能据此指认药物机制。"""

CONCLUSION_CN = """在迄今最大规模的乙胺丁醇药物警戒评估中（2 033 万例去重 FAERS 病例），
其眼部毒性表现为一个**高度特异的视神经信号**——强于任何同类抗结核药一个量级，
而泛化眼部主诉**完全无信号**。这一对照在全部四种稳健性口径下均成立，包括将对照分母
限制为同类抗结核药报告。发病时间较同一批报告中的非眼部事件延迟数月，符合累积性轴索损伤。
分子层面，所涉网络收敛于**铁死亡与线粒体完整性**——这正是实验研究已在乙胺丁醇处理的
视网膜神经节细胞中确认的通路轴；对接提示乙胺丁醇作用于该网络的**上游炎症与氧化还原节点**，
而非其终端酶。遗传代理的肾功能对视神经表型**无因果效应**，这表明肾功能不全是**药物暴露量**
的决定因素，而非视神经变性的独立病因。"""


def main() -> int:
    t = CN.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ title
    t = re.sub(r"^#\s+.*$", f"# {TITLE}", t, count=1, flags=re.M)

    # ------------------------------------------------------------- abstract
    t = t.replace("及“清阳不升”病机的计算验证", "")
    t = t.replace('及"清阳不升"病机的计算验证', "")
    # methods sentence: drop the TCM aim
    t = re.sub(r"并以 FinnGen R12 视神经表型作遗传学考察。",
               "并以 FinnGen R12 视神经表型作遗传学考察。", t)
    t = t.replace(
        "并借助网络毒理学、分子对接与遗传学证据，为中医\"清阳不升\"病机提供可计算的分子锚点。",
        "并结合网络毒理学、分子对接与遗传学证据，刻画该毒性的分子机制。")
    t = t.replace(
        "并借助网络毒理学、分子对接与遗传学证据，为中医“清阳不升”病机提供可计算的分子锚点。",
        "并结合网络毒理学、分子对接与遗传学证据，刻画该毒性的分子机制。")
    # conclusions of the abstract
    t = re.sub(r"\*\*结论\*\*.*?(?=\n\n\*\*关键词)", """**结论** 乙胺丁醇眼部毒性是一个
**特异性极高**的视神经信号：泛化眼部主诉全无信号，起病延迟至用药后数月，
且在全部稳健性口径下均成立。分子层面落于**铁死亡—线粒体网络**，
对接提示乙胺丁醇作用于该网络的上游炎症与氧化还原节点。遗传代理的肾功能
对视神经表型无因果效应，提示肾功能不全是药物暴露量的决定因素而非独立病因。""",
               t, count=1, flags=re.S)

    # --------------------------------------------------------- introduction
    t = re.sub(r"现有文献存在两处空白：.*?(?=\n\n## 2 资料与方法)",
               INTRO_TAIL, t, count=1, flags=re.S)

    # ------------------------------------------------------------- docking
    t = re.sub(r"### 3\.6 分子对接\n\n.*?(?=### 3\.7 )", DOCKING_CN + "\n\n", t,
               count=1, flags=re.S)

    # ------------------------------------------- discussion: drop TCM sections
    # remove 4.3 (清阳不升病机) and 4.4 (治法与候选方药), insert the mechanism text
    t = re.sub(r"### 4\.3 \"清阳不升\"病机的分子锚点.*?(?=### 4\.5 临床意义)",
               DISC_MECH_CN + "\n\n", t, count=1, flags=re.S)
    # renumber the remaining discussion sections
    t = t.replace("### 4.5 临床意义", "### 4.4 临床意义")
    t = t.replace("### 4.6 局限", "### 4.5 局限")

    # limitations: replace the TCM item with the docking limitation
    t = re.sub(r"4\. \*\*四情景稳健性检验\*\*.*?(?=5\. \*\*未行药物暴露 MR\*\*)",
               "4. " + DISC_LIMIT_CN.strip() + "\n"
               "   四情景稳健性检验已表明结论不依赖匹配或分母口径；"
               "但 83 个未归类术语（表2d）仍需人工复核。\n", t,
               count=1, flags=re.S)
    t = t.replace("5. **未行药物暴露 MR**", "5. **未行药物暴露 MR**")

    # ------------------------------------------------------------ conclusion
    t = re.sub(r"## 5 结论\n\n.*?(?=\n\n---|\n\n## )", f"## 5 结论\n\n{CONCLUSION_CN}\n",
               t, count=1, flags=re.S)

    # ------------------------------------------------------- figure legend list
    t = t.replace("**图7** 乙胺丁醇与中药活性成分对 hub 靶点的对接打分热图（AutoDock Vina，kcal/mol）。",
                  "**图7** 乙胺丁醇对 14 个 hub 靶点的对接打分（AutoDock Vina，kcal/mol）。")
    t = t.replace("**图5** 聚焦层 STRING 蛋白互作网络（33 节点、191 边）。红色为策展核心面板，橙色为文献支持基因，蓝色为视神经表型基因。",
                  "**图5** 聚焦层 STRING 蛋白互作网络（33 节点、191 边）。红色为策展核心面板，橙色为文献支持基因，蓝色为视神经表型基因。")

    CN.write_text(t, encoding="utf-8")

    # ------------------------------------------------------------- report
    hits = [(i, ln.strip()[:90]) for i, ln in enumerate(t.splitlines(), 1)
            if re.search(r"清阳|浊阴|清空之窍|青盲|视瞻昏渺|治法|方药|驻景|杞菊|"
                         r"益气聪明|枸杞|菊花|葛根|槲皮素|木犀草素|山奈酚|"
                         r"traditional Chinese|中医", ln)]
    print(f"[cn] TCM removal done; remaining TCM-concept lines: {len(hits)}")
    for i, ln in hits:
        print(f"   L{i}: {ln}")
    print(f"[cn] characters: {len(t):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
