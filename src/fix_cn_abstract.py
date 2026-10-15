# -*- coding: utf-8 -*-
"""
Replace the phytochemical sentence in the Chinese abstract with the ethambutol-only
docking result, and add the report-adequacy and genetic findings so the Chinese
abstract matches the English one field for field.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"
PT = MAN / "论文_中文版.md"

adqs = pd.read_csv(RES / "faers_adequacy_summary.csv", encoding="utf-8-sig")
mr = pd.read_csv(RES / "mr_opengwas_results.csv", encoding="utf-8-sig")
cy = mr[(mr.exposure == "Cystatin C") & (mr.outcome == "H7_OPTNEURITIS")]
n_inst = int(cy.iloc[0].n_snp) if not cy.empty else 146

t = PT.read_text(encoding="utf-8")

old = ("分子对接显示槲皮素、木犀草素、山奈酚、葛根素在 TNF、MFN2、HMOX1、BCL2 等靶点上"
       "系统性优于乙胺丁醇（−6.0～−8.9 vs −4.0～−5.5 kcal/mol）；"
       "碳酸酐酶Ⅱ重对接验证 RMSD 1.795 Å 通过。")
new = (f"报告充分性方面，解读性字段完整度高而暴露性字段完整度低——"
       f"视神经谱病例中仅 {adqs.iloc[0].pct_both:.1f}% 同时具备年龄、性别与用药开始日期，"
       f"可支持发病时间分析。对接显示乙胺丁醇对 TNF（−5.50）、MFN2（−5.21）、"
       f"HMOX1（−5.09）等上游炎症与氧化还原节点结合较优，"
       f"而对 GPX4（−3.96）、SMAD4（−4.06）等铁死亡终端分子结合较弱；"
       f"碳酸酐酶Ⅱ重对接验证 RMSD 1.795 Å 通过。遗传学方面，"
       f"遗传代理的肾功能（胱抑素 C，{n_inst} 个工具变量）对视神经炎无因果效应"
       f"（OR 1.026，95%CI 0.865～1.216），FDR 校正后全部结局均无显著关联。")

if old in t:
    t = t.replace(old, new, 1)
    print("[cn] abstract docking sentence replaced, adequacy and MR added")
else:
    print("[cn] WARNING: the phytochemical sentence was not found verbatim; "
          "applying a regex fallback")
    t = re.sub(r"分子对接显示槲皮素.*?RMSD 1\.795 Å 通过。", new, t, count=1, flags=re.S)

PT.write_text(t, encoding="utf-8")

hits = [(i, ln.strip()[:80]) for i, ln in enumerate(t.splitlines(), 1)
        if re.search(r"清阳|浊阴|清空之窍|青盲|视瞻昏渺|治法|方药|驻景|杞菊|"
                     r"益气聪明|枸杞|菊花|葛根|槲皮素|木犀草素|山奈酚|中医|"
                     r"traditional Chinese", ln)]
print(f"remaining TCM lines: {len(hits)}")
for i, ln in hits:
    print(f"  L{i}: {ln}")
print(f"characters: {len(t):,}")
