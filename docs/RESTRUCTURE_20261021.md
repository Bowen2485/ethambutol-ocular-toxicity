# 2026-10-21 重构记录

依据 `乙胺丁醇视神经药物警戒研究_论文重构与投稿方案.pdf`（2026-10-21）完成的重构，以及尚未完成的部分。

## 已完成

### 工作包 1：统计审计（先行，不可跳过）

`src/build_main_results.py` 从仓库直接重算全部主结果，写入 `results/main_results.json`。审计解决了方案点名的三处冲突：

| 冲突 | 结论 |
|---|---|
| optic neuropathy ROR 116.58 vs 105.81 | **116.58 正确**。PT 在 `reac` 中有两种拼写（`Optic neuropathy` 1,626 例、`OPTIC NEUROPATHY` 446 例）；任何只匹配一种拼写的脚本都会得到 a=151、ROR 105.81。稳健性表即属此类漏计。 |
| 乙胺丁醇病例 15,510 vs 14,568 | 15,510 是主队列（任意药物角色）；14,568 是 11 查询药物对照分析用的旧队列，属另一种暴露定义，只能作敏感性。 |
| 时间分层合计 2,554+11,282=13,836 | 该表建于 2026Q2 归档入库之前，仍是旧队列（13,804）。重算后为 4,316+11,194=**15,510**，与主队列一致。 |

重算还使 SMQ 表中少数分母略变（如视神经 25,594→25,600，ROR 23.52→23.51），原因是补上了大写拼写。

**主规格（锁定）**：暴露=任一药物记录出现乙胺丁醇、不限角色；结局=MedDRA 29.0 窄口径 SMQ/PT，双拼写匹配；分母=全部去重病例；指标=ROR（Woolf 95% CI），BH 控制于两个预先声明的家族（11 个查询、15 个 PT）。其余定义一律命名敏感性分析。

### 工作包 2–6 与主文

- 新稿 `manuscript/TADS_manuscript.md`，由 `src/build_tads_manuscript.py` 合并四个分段文件并生成表 1–4、图注与参考文献。
- 标题、摘要（295 词）、Plain Language Summary 按方案 §6 撰写；核心主张采用方案 6.2 原句。
- 网络药理学、分子对接、MM/GBSA、MR 已全部移出主文；转录组压缩为 §3.7 + §4.4 的探索性小节，结论改为"所选转录预测未复现"，不再写"否定铁死亡"。
- 措辞按方案 6.3 全部替换：optic-nerve-predominant reporting、非发病率/非因果，删去 "confined/specific/proves"。
- 图 1–4 由 `src/make_figures_tads.py` 从 `main_results.json` 生成（英文）。
- `docs/READUS-PV_checklist.md`：按官方 32 条逐项填写，并显式列出未满足项（7d/10 无个案评估、14d 未注册）。
- 投稿包 `submission/tads/`：22 页 PDF（双倍行距、行号）、tex、4 图 PDF+PNG、README。

### 校验

`src/audit_tads.py` 16 项全过：引用 18/18 双向一致、摘要 295≤300、正文 4,804≤6,000、无占位符、关键数值与 `main_results.json` 一致。PDF 0 Overfull、0 undefined。

## 尚未完成

1. **PDS 短版（3,000 词）**。建议裁法：删 §3.4 时间分层与固定方案（移补充）、§3.7 转录组整体移补充、§4.4 并入 §4.3；Methods 压缩 2.6–2.10；目标 2,900–3,000 词，摘要 ≤250，加 Five Key Points。
2. **补充材料文件**。正文引用了补充表（完整 PT 面板、全部敏感性口径、JADER 术语映射、转录组方法），尚未汇编成独立文件。
3. **参考文献体例**。18 条有作者/题目/期刊/年/DOI，但部分缺卷期页；投稿前用 DOI 过一遍文献管理器。
4. **中文版**。`manuscript/Ethambutol_EyeTox_CN_full.md` 仍是 Frontiers 结构（20 页），与新稿不对应；若要中文版需按新结构重写，而非逐句翻译。
5. **SDUD 处方分母**。未进入新稿主文（方案未列入证据层级）；若将来补足 2016–2026 年度文件，可作补充分析。

## 旧版处置

Frontiers 版（`manuscript/Ethambutol_EyeTox_EN_full.md`、`submission/Ethambutol_EyeTox_Frontiers.pdf`、
`submission/Ethambutol_EyeTox_CN.pdf`）保持在原处未动，作为历史版本；其 74 项 `final_audit.py`
仍可运行，但不适用于新稿。
