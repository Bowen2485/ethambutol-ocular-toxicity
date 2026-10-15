# -*- coding: utf-8 -*-
"""Append the TCM-removal record to PROGRESS.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "PROGRESS.md"
t = P.read_text(encoding="utf-8")

ADD = """
---

## 七、重定位：移除中医内容（2026-10-12 追加）

**作者决定不保留中医内容**，论文重新定位为**纯计算药物警戒与机制研究**。

### 7.1 移除范围（两版稿件已同步）

| 位置 | 处理 |
|---|---|
| 标题 | 去掉「清阳不升病机的计算验证」，改为「结合网络毒理学、分子对接与视神经表型的遗传学考察」 |
| 摘要 | 目的/方法/结果/结论四段全部重写；结果段追加报告充分性与 MR 结果 |
| 关键词 | 删「清阳不升」，增「孟德尔随机化」「信号挖掘」 |
| 引言 | 研究空白段重写为「特异性从未以自身内部对照检验过」 |
| 结果 3.9（对接） | 由「中药活性成分 vs 乙胺丁醇」改为**仅乙胺丁醇**对 14 个 hub 靶点 |
| 讨论 4.3（清阳不升病机） | 删除，替换为机制讨论（含铁死亡/线粒体/锌的网络证据） |
| 讨论 4.4（治法与候选方药） | 删除 |
| 局限 | 删「中医整合属诠释性工作」条目，改为对接方法学局限 |
| 结论 | 重写，去掉中医表述 |

### 7.2 图表变动

- **图7 重绘**：原为「乙胺丁醇与中药活性成分对接打分热图」→
  现为「乙胺丁醇对 14 个 hub 靶点的对接打分条形图」（深色＝实验结构，浅色＝AlphaFold 模型）
- **表7 重建**：仅含乙胺丁醇的 14 次对接（此前含 12 配体 × 14 靶点 = 168 次）
- 图1–6、图8–9 与表1–6、表8–10 未受影响

### 7.3 归档（未删除）

`archive/tcm_removed/` 保存：

- `中医机制章节_清阳不升.md`（15 KB）
- `tcm_optic_neuropathy_background.md`（62 KB，72 PMID）
- `README.md`（说明移除原因与范围，并警告：直接复制回稿件会导致编号错乱）

### 7.4 新增文件

- **`docs/期刊推荐与投稿信_重定位版.md`** —— 按新定位重写的选刊建议 ＋ 中英文投稿信模板
  （原《投稿材料_期刊建议与投稿信.md》针对中医理论稿，已不适用）

### 7.5 验证

- 全文 TCM 残留扫描（Markdown ＋ DOCX 正文 ＋ 表格单元格）：**0 命中**
- `src/final_audit.py`：**60 项通过**（期望文件清单已更新，移除中医文件）
- `src/audit_crosslanguage.py`：**33 项通过**（中英两版数值一致性）
- 正文由 9,128 词降至 **8,644 词**
"""

if "## 七、重定位" not in t:
    t = t.rstrip() + ADD
    P.write_text(t, encoding="utf-8")
    print(f"PROGRESS.md updated: {len(t):,} chars")
else:
    print("PROGRESS.md already contains the repositioning record")
