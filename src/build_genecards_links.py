# -*- coding: utf-8 -*-
"""
Build the clickable search list for the manual GeneCards pass.

Why a file rather than instructions
    Sixty-six gene pages is enough work that a wrong link costs real time, and a list the user
    has to assemble from a CSV is a list that will produce transcription errors in the very
    identifiers the analysis keys on.  The links are therefore generated from the identifiers
    already verified against NCBI Gene, and each entry carries the symbol next to the link so a
    page that opens the wrong gene is visible immediately.

Two links per gene
    The GeneCards page carries the Disorders section under Disease and Clinical Annotation.
    The MalaCards page is linked from it and lists the diseases in a table with relevance
    scores, which is easier to read than the GeneCards layout and is the same underlying
    annotation, so having both means whichever renders better can be used.

The order
    Hubs first, in descending network degree, then the controls.  If the pass cannot be
    finished, a partial set that covers the highest-degree hubs and an equal number of
    controls is still analysable; an arbitrary partial set is not, because the comparison
    needs both sides.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "results" / "genecards_search_list.csv"

#: network degree from the manuscript's Table 5, used to order the hubs so a partial pass is
#: still balanced
DEGREE = {"TP53": 23, "NFE2L2": 22, "AKT1": 22, "BCL2": 20, "HMOX1": 20, "CASP3": 20,
          "SOD2": 19, "PPARG": 18, "TNF": 18, "BAX": 17, "GPX4": 17, "MFN2": 14,
          "SDHB": 13, "BDNF": 12, "TFEB": 10, "SMAD4": 9, "SLC7A11": 7, "NTRK2": 7,
          "ACSL4": 6, "SLC25A4": 5, "KEAP1": 5, "MAPK1": 5, "IL6": 5, "STAT3": 5,
          "CAT": 4, "GPX1": 4, "TXN": 4, "NQO1": 4, "HIF1A": 4, "PPARGC1A": 3,
          "DNM1L": 3, "VDAC1": 3, "CYCS": 3, "APAF1": 3, "BCL2L1": 2, "FTH1": 2,
          "FTL": 2}

rows = list(csv.DictReader(WORK.open(encoding="utf-8-sig")))
hubs = [r for r in rows if r["group"] == "hub"]
ctrl = [r for r in rows if r["group"] == "control"]
hubs.sort(key=lambda r: -DEGREE.get(r["symbol"], 0))

lines = []
lines.append("# GeneCards 手动检索清单")
lines.append("")
lines.append("共 66 个基因：33 个 hub（按网络连接度降序）+ 33 个对照。")
lines.append("")
lines.append("**每个基因只需看一件事**：`Disorders` 分区里有没有眼病（视网膜、视神经、"
             "黄斑、青光眼、葡萄膜炎、白内障、角膜等）。")
lines.append("")
lines.append("**记录格式**（填回 `results/genecards_search_list.csv`）：")
lines.append("")
lines.append("| 列 | 填法 |")
lines.append("|---|---|")
lines.append("| `genecards_eye_related` | `yes` / `no` |")
lines.append("| `genecards_diseases` | 眼病名称，多个用 `;` 分隔 |")
lines.append("| `genecards_score` | 相关性评分（可选） |")
lines.append("")
lines.append("**若你懒得填表**：直接把看到的内容贴给我（任意格式），我来整理。")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 一、hub 基因（33 个，按连接度降序）")
lines.append("")
lines.append("| # | 基因 | 连接度 | GeneCards | MalaCards 疾病 |")
lines.append("|---|---|---|---|---|")

for i, r in enumerate(hubs, 1):
    s = r["symbol"]
    gc = f"[{s}](https://www.genecards.org/cgi-bin/carddisp.pl?gene={s})"
    mc = f"[疾病列表](https://www.malacards.org/search/results?query={s})"
    lines.append(f"| {i} | **{s}** | {DEGREE.get(s, '')} | {gc} | {mc} |")
    lines.append(f"| | | | NCBI ID {r['ncbi_gene_id']} | {r['description']} |")

lines.append("")
lines.append("## 二、对照基因（33 个）")
lines.append("")
lines.append("| # | 基因 | GeneCards | MalaCards 疾病 |")
lines.append("|---|---|---|---|")
for i, r in enumerate(ctrl, 1):
    s = r["symbol"]
    gc = f"[{s}](https://www.genecards.org/cgi-bin/carddisp.pl?gene={s})"
    mc = f"[疾病列表](https://www.malacards.org/search/results?query={s})"
    lines.append(f"| {i} | **{s}** | {gc} | {mc} |")
    lines.append(f"| | | NCBI ID {r['ncbi_gene_id']} | {r['description']} |")

lines.append("")
lines.append("---")
lines.append("")
lines.append("## 已有的 DisGeNET 结果（供你对照）")
lines.append("")
lines.append("我已完成 DisGeNET 那次检验，结果是 **hub 18/33（55%）vs 对照 4/33（12%）**，")
lines.append("Fisher P = 2.6×10⁻⁴。**阳性对照通过**：OPA1（13 种眼病）、DNM1L、MFN2 均被")
lines.append("检出为视神经萎缩相关。")
lines.append("")
lines.append("**GeneCards 这一遍的目的是独立复现**。所以：")
lines.append("")
lines.append("- **不要参考我的结果去填** —— 若你按 DisGeNET 的预期填，就不构成独立检验")
lines.append("- **按页面上实际显示的填** —— 包括与我结果不一致的情况")
lines.append("- **若某个基因在 GeneCards 上有眼病而 DisGeNET 上没有（或反之），照实记录**")

out = ROOT / "docs" / "GeneCards检索清单.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), encoding="utf-8")
print(f"  written: {out.relative_to(ROOT)}")
print(f"  links: {len(hubs) + len(ctrl)} genes")
print()
print("  first few hub entries:")
for ln in lines[24:30]:
    print(f"      {ln[:96]}")
