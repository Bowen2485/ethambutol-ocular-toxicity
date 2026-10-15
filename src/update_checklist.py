# -*- coding: utf-8 -*-
"""
Update the manual-task checklist after the TCM component was removed.

The checklist was written while the manuscript still carried the TCM mechanism
chapter and a phytochemical docking panel.  Those items are now obsolete, so they
are replaced with the tasks that actually remain, and the journal-strategy warning
is rewritten for the repositioned paper.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "docs" / "需人工完成清单.md"
t = P.read_text(encoding="utf-8")

# C1: the TCM-keep-or-cut decision is settled
t = re.sub(
    r"\| C1 \| \*\*是否保留中医章节\*\*[^\n]*\n",
    "| C1 | ~~是否保留中医章节~~ | **已决定：不保留。** 中医机制章节、候选方药、"
    "中药成分对接面板与图7热图均已移除（原文件见 `archive/tcm_removed/`）。"
    "论文现为纯计算药物警戒与机制研究，投稿方向见 "
    "`docs/期刊推荐与投稿信_重定位版.md` |\n", t)

# C3: table/figure count changed
t = re.sub(
    r"\| C3 \| 图表数量取舍 \|[^\n]*\n",
    "| C3 | 图表数量取舍 | 当前 9 图 10 表。多数期刊限制 6–8 个图表，需合并"
    "（建议将图3、图4 合并，表2b–2d、表10 移入补充材料） |\n", t)

# E4/E5: TCM review items are gone
t = re.sub(r"\| E4 \| 复核中医病机章节的学术表述 \|[^\n]*\n",
           "| E4 | 复核术语归类（**重要**） | 见 E1；此外请复核表7 中"
           "\"实验结构 vs AlphaFold 模型\"的标注是否与你的理解一致 |\n", t)
t = re.sub(r"\| E5 \| 决定中药成分清单是否需替换 \|[^\n]*\n",
           "| E5 | 决定是否补做 ethambutol 的分子动力学验证 | 当前仅做对接打分；"
           "若审稿人要求更强结合证据，可补 MD 模拟（需装 OpenMM，本环境 pip 受限） |\n", t)

# F4: phytochemical target prediction no longer applies
t = re.sub(r"\| F4 \| 中药成分的靶点预测[^\n]*\n",
           "| F4 | 乙胺丁醇的人类靶点实验数据 | Open Targets 中无人类靶点记录，"
           "故网络为下游效应网络。若你能获得实验靶点数据（如 ChemProteoBase、"
           "DrugBank 实验栏），可显著加强机制部分 |\n", t)

# G5: ADMET item no longer applies
t = re.sub(r"\| G5 \| 补做中药成分的 ADMET 预测[^\n]*\n",
           "| G5 | 补做化合物的 ADMET 预测 | 已无中药成分，此项可改为对乙胺丁醇本身的"
           "药代参数整理（可选） |\n", t)

# the closing risk warning must reflect the repositioned paper
t = re.sub(
    r"\*\*其一，中医部分的可发表性。\*\*.*?(?=\*\*其二)",
    "**其一，期刊选择已随之改变。** 去掉中医后，本文不再是民族药理类论文，"
    "不应投 *Journal of Ethnopharmacology* 一类期刊；应投药物警戒/药物流行病学"
    "或药理毒理类刊。完整的选刊建议与投稿信见 "
    "`docs/期刊推荐与投稿信_重定位版.md`。\n\n", t, flags=re.S)

P.write_text(t, encoding="utf-8")

hits = [(i, ln.strip()[:90]) for i, ln in enumerate(t.splitlines(), 1)
        if re.search(r"清阳|浊阴|清空之窍|中医|中药|民族药理", ln)]
print(f"stale TCM lines remaining: {len(hits)}")
for i, ln in hits:
    print(f"  L{i}: {ln}")
print(f"checklist characters: {len(t):,}")
