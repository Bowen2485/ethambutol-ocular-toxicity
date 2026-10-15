# -*- coding: utf-8 -*-
"""
Add the figure and table citations to the Chinese manuscript.

The Chinese draft described every result in prose but never pointed at the figures,
so the Chinese Word document ended up with no images while the English one had nine.
Figure references are inserted at the paragraph that reports the corresponding
result, mirroring the English text, and a figure-legend section is appended.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

INSERTS = [
    ("（数据见 `tables/Table1_cohort.csv`、`Table2_signals.csv`）",
     "（数据见 `tables/Table1_cohort.csv`、`Table2_signals.csv`；研究流程图见**图1**）"),
    ("**信号高度局限于视神经—视网膜—色觉轴**",
     "**信号高度局限于视神经—视网膜—色觉轴**"),
    ("其余严格信号见下表（节录）：",
     "其余严格信号见下表（节录；完整信号谱见**图2**火山图与**图4**森林图，"
     "跨药物比较见**图3**热图）："),
    ("这一时间差与\"累积性轴索损伤\"而非\"特异性反应\"相符。",
     "这一时间差与\"累积性轴索损伤\"而非\"特异性反应\"相符（**图8**）。"),
    ("亚洲报告者无显著差异（0.924，P=0.389）。",
     "亚洲报告者无显著差异（0.924，P=0.389）。年度报告量与视神经术语占比的变化见**图9**。"),
    ("hub 前 10 位：TP53（度 23）",
     "网络结构见**图5**。hub 前 10 位：TP53（度 23）"),
    ("这与 2026 年实验研究〔PMID 41563626〕完全吻合。",
     "这与 2026 年实验研究〔PMID 41563626〕完全吻合（富集结果见**图6**）。"),
    ("提示可能竞争同一结合位点。",
     "提示可能竞争同一结合位点（**图7**）。"),
]

LEGENDS = """
---

## 图表清单

**图1** FAERS 病例筛选流程（90 个季度 ASCII 原始发布 → 2 033 万例去重病例 → 乙胺丁醇相关病例 → 眼科术语四格表）。

**图2** 乙胺丁醇眼部术语不成比例分析火山图。横轴为 log₂ 报告比值比，纵轴为 −log₁₀(Benjamini-Hochberg q)。红点为严格信号。

**图3** 六种抗结核药眼科报告比值比热图（log₂ ROR）。

**图4** 乙胺丁醇眼部信号森林图（ROR 及 95%CI，n≥3）。

**图5** 聚焦层 STRING 蛋白互作网络（33 节点、191 边）。红色为策展核心面板，橙色为文献支持基因，蓝色为视神经表型基因。

**图6** 聚焦层功能富集点图（GO-BP/CC/MF、KEGG、Reactome、WikiPathways）。

**图7** 乙胺丁醇与中药活性成分对 hub 靶点的对接打分热图（AutoDock Vina，kcal/mol）。

**图8** 用药至发病时间分布（左：按事件类别的对数刻度直方图；右：箱线图与中位时间）。

**图9** 乙胺丁醇年度报告量与视神经术语占比变化（2013—2026）。

**表1** 研究人群（FAERS 去重后各暴露病例数）。
**表2** 乙胺丁醇眼部信号全表（177 个术语）。
**表2b** 严格信号（58 个术语）。
**表2c** 药物毒性谱信号（前 30）。
**表2d** 未归类术语（待人工复核，83 个）。
**表3** 用药至发病时间。
**表4** 多因素 logistic 回归。
**表5** 聚焦层 hub 基因。
**表6** 主要富集通路。
**表7** 分子对接打分矩阵。
**表8** 两样本孟德尔随机化结果。
**表9** 稳健性检验（四情景）。
**表10** 报告充分性。
"""


def main() -> int:
    p = MAN / "论文_中文版.md"
    txt = p.read_text(encoding="utf-8")
    applied, missed = 0, []
    for old, new in INSERTS:
        if old in txt:
            txt = txt.replace(old, new, 1)
            applied += 1
        else:
            missed.append(old[:40])
    if "## 图表清单" not in txt:
        txt = txt.rstrip() + "\n" + LEGENDS
    p.write_text(txt, encoding="utf-8")
    print(f"[cn] {applied}/{len(INSERTS)} figure citations inserted")
    if missed:
        print("  not found (check manually):")
        for m in missed:
            print("   -", m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
