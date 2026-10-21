# -*- coding: utf-8 -*-
"""Final round: name the release tag in the manuscript, and bring PROGRESS.md up to date.

The review asked for a locatable version because the paper promised one.  A tag is created on the
final commit after this change; the manuscript names it, so the promise and the repository agree.
PROGRESS.md is a long historical archive whose header still described 89 quarters; a current-state
block is prepended and the rest is explicitly labelled as history.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")
old = ("The code, the derived tables and a data dictionary are available at the repository given "
       "in the Statements, under a tagged release that corresponds to this manuscript.")
new = ("The code, the derived tables and a data dictionary are available at the repository given "
       "in the Statements, under the release tag `v2.0-tads-2026-10-21`, which identifies the "
       "commit from which the numbers, tables and figures in this manuscript were generated.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("methods: release tag named")

REPO = Path(r"C:\Users\20200\Downloads\论文\投稿\ethambutol-ocular-toxicity")
prog = REPO / "PROGRESS.md"
text = prog.read_text(encoding="utf-8")
banner = """# 乙胺丁醇眼毒性项目 — 进度存档

> ## 当前状态（2026-10-21 重构后）
>
> 本文件下方自 2026-10-12 起的记录属于**历史存档**，其中"89 个季度""2026Q2 待补齐"
> "20,328,568 例""13,804 例"等表述反映的是当时的中间状态，**不是当前论文的数字**。
>
> 当前论文（Therapeutic Advances in Drug Safety 投稿版）的口径：
>
> - FAERS 90 个季度，2004Q1–2026Q2；提交报告 24,812,425 份，去重后 20,692,683 例
> - 命名乙胺丁醇 15,510 例（一级或二级可疑药 9,024 例）
> - 视神经查询 432 例，ROR 23.51（21.35–25.89）；视神经病变 165 例，ROR 116.58（99.36–136.78）
> - 分期敏感性：2004–2016 年 ROR 131.72，2017–2026 年 111.66（各期用自身分母）
> - 固定方案比较：76/6,167 对 7/1,098，率比 1.93（0.89–4.18），区间含 1
> - 网络药理学、分子对接、分子动力学与孟德尔随机化**不用于当前论文**
>
> 全部数字由 `src/build_main_results.py` 生成并写入 `results/main_results.json`；
> 稿件为 `manuscript/TADS_manuscript.md`，PDF 为 `submission/Ethambutol_TADS_manuscript.pdf`。
> 对应版本标签：`v2.0-tads-2026-10-21`。
"""
if "当前状态（2026-10-21 重构后）" not in text:
    text = text.replace("# 乙胺丁醇眼毒性项目 — 进度存档\n", banner, 1)
    prog.write_text(text, encoding="utf-8")
    print("PROGRESS.md: current-state block prepended")
else:
    print("PROGRESS.md: already updated")
