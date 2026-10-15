# -*- coding: utf-8 -*-
"""Final cleanup of the Chinese manuscript after TCM removal."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PT = ROOT / "manuscript" / "论文_中文版.md"
t = PT.read_text(encoding="utf-8")

# 1. drop the superseded limitation item 4 (it still refers to TCM compounds)
t = t.replace(
    "4. **对接为打分近似**：二氢叶酸还原酶回对接未通过（RMSD 5.86 Å），"
    "说明方法对大柔性配体不可靠；本文引用的中药成分为小分子黄酮，"
    "属较可靠区间，仍需湿实验验证。\n", "")
t = t.replace(
    "4. **对接为打分近似**：二氢叶酸还原酶回对接未通过（RMSD 5.86 Å），"
    "说明方法对大柔性配体不可靠；本文引用的中药成分为小分子黄酮，属较可靠区间，"
    "仍需湿实验验证。\n", "")

# 2. drop the TCM-integration limitation item
t = re.sub(r"\n6\. \*\*中医整合属诠释性工作\*\*[^\n]*\n", "\n", t)

# 3. keywords: swap the TCM term for the study's actual methods
t = t.replace("分子对接；清阳不升", "分子对接；孟德尔随机化；不成比例分析")

# 4. reference note: remove the TCM background file reference
t = re.sub(r"完整索引见\s*`[^`]+`\s*与\s*`[^`]+`",
           "完整索引见英文版 References 一节", t)

# 5. renumber the limitation list so it runs 1..n
lines = t.splitlines()
out, in_lim, n = [], False, 0
for ln in lines:
    if ln.strip() == "### 4.5 局限":
        in_lim, n = True, 0
        out.append(ln)
        continue
    if in_lim and re.match(r"^\d+\.\s", ln):
        n += 1
        out.append(re.sub(r"^\d+\.", f"{n}.", ln))
        continue
    if in_lim and ln.startswith("## "):
        in_lim = False
    out.append(ln)
t = "\n".join(out)

# 6. make the MR scope item reflect that only renal exposures were completed
t = t.replace(
    "5. **未行药物暴露 MR**：乙胺丁醇无遗传工具变量，本文 MR 针对的是可修饰危险因素而非药物本身；"
    "且因抓取耗时，最终仅纳入 3 个暴露（原拟 10 个），罕见结局把握度有限，"
    "结论应表述为\"未检出效应\"。",
    "**未行药物暴露 MR**：乙胺丁醇无遗传工具变量，本文 MR 针对的是可修饰危险因素而非药物本身；"
    "且因抓取耗时，最终仅纳入 3 个暴露（原拟 10 个），罕见结局把握度有限，"
    "结论应表述为\"未检出效应\"。")

PT.write_text(t, encoding="utf-8")

hits = [(i, ln.strip()[:100]) for i, ln in enumerate(t.splitlines(), 1)
        if re.search(r"清阳|浊阴|清空之窍|青盲|视瞻昏渺|治法|方药|驻景|杞菊|"
                     r"益气聪明|枸杞|菊花|葛根|槲皮素|木犀草素|山奈酚|中医|"
                     r"traditional Chinese", ln)]
print(f"remaining TCM lines: {len(hits)}")
for i, ln in hits:
    print(f"  L{i}: {ln}")
print(f"characters: {len(t):,}")
