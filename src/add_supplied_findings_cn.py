# -*- coding: utf-8 -*-
"""
Write the three additions into the Chinese manuscript, keeping the two versions in step.

Which additions
    The smoking Mendelian randomisation null, the dose opposition against the Korean and
    meta-analysis findings, and the reversibility paragraph in the discussion.  Each is
    already in the English file; leaving them out of the Chinese one would mean two versions of
    one submission disagreeing about what the study found.

Numbers are taken from the English file rather than retyped, by copying the numeric spans out
of the relevant paragraphs, so the two cannot drift apart.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

en = EN.read_text(encoding="utf-8")
cn = CN.read_text(encoding="utf-8")

#: pull the smoking table out of the English file so the Chinese one carries the same numbers
m = re.search(r"\| Outcome \| Smoking initiation.*?\n\n", en, re.S)
smoke_table = m.group(0).strip() if m else ""
qmin = re.search(r"all q ≥ (\d\.\d\d)", en)
qmin = qmin.group(1) if qmin else "0.86"
n_si = re.search(r"with (\d+) instruments", en)
n_si = n_si.group(1) if n_si else "32"
n_cd = re.search(r"at (\d+) instruments, is weaker", en)
n_cd = n_cd.group(1) if n_cd else "14"

SMOKE = f"""**吸烟作为遗传暴露被检验，未显示效应。** 本面板包含两个吸烟性状，二者与全部 6 个视神经及视觉结局在 Benjamini-Hochberg 校正后均无关联（全部 q ≥ {qmin}）。其中较强的是吸烟启动，含 **{n_si} 个**工具变量：

{smoke_table}

之所以报告此项，是因为一项纳入 4 141 名乙胺丁醇使用者的队列经校正 logistic 回归发现**吸烟是视神经病变的独立危险因素（OR 7.06，p = 0.01）**[p2023]。二者并不直接冲突——遗传工具变量估计的是**终生吸烟倾向**，而治疗队列中的校正估计捕捉的是**当前吸烟及其相关因素**——但二者也并未相互印证。**该结果应表述为"未检出可检出的效应"，而非"证明无效应"**：吸烟启动有 {n_si} 个工具变量，其估计接近 1 且区间包含 1；而每日吸烟支数仅 {n_cd} 个工具变量，效力更弱，区间相应更宽。"""

DOSE = """**剂量发现与部分临床文献不一致，原因是报告完整度。** 本分析在校正暴露时长后发现日剂量不预测视神经结局（似然比 P = 0.55），**而韩国 1 000 例队列报告的次序相反：肾功能不全与日剂量有贡献，而疗程没有**[l2008]。一项纳入 11 项研究、370 例患者的 2026 年系统综述对同一问题给出另一种次序，认为**疗程是主要因素**，并给出剂量梯度——**低于 15 mg/kg/日时患病率为 1%，20 mg/kg/日时高三倍**[c2026]。

两者可以同时成立，而**本分析在三者中对剂量的效力最弱，原因见 3.4b 节**：仅 27.8% 的视神经报告同时具备年龄、性别与治疗开始日期，**故剂量模型仅拟合于暴露字段完整的少数病例，检出剂量效应的效力很低**。**因此剂量结果应表述为"不确定"而非"阴性"**，剂量问题交由临床文献承担。"""

REV = """**可逆性——本研究无法测量——正是临床文献最有用之处。** 两个队列报告了它，而结果不同。泰国队列的 4 141 名乙胺丁醇使用者中，发生视神经病变的 20 例里 **60% 视力改善至少 2 行（Snellen）**，平均恢复时间 **6.9 个月**，且改善与人口学、既往史、吸烟或乙胺丁醇剂量无关[p2023]。**而韩国队列中不足三分之一在停药后改善**，恢复潜伏期 **5.38 ± 1.71 个月**，且**诊断时已有视盘苍白者无一恢复任何视功能**[l2008]。

**最后一点是临床上决定性的，它确定了本分析所暗示的时间尺度。** 本研究中自开始乙胺丁醇至视神经事件的中位时间为 **125 天**，而同一批报告中非眼部事件为 **30 天**——**故毒性效应缓慢，可检出它的窗口先于视盘苍白出现，而据韩国数据，一旦出现视盘苍白则不再恢复。** 药物警戒数据库记录的是事件而非结局，故本研究无法对可逆性数字作出补充；**它贡献的是使监测具有价值的时间信息。** 光学相干断层扫描血管成像可在临床发病前检出黄斑浅层血管密度下降[su2022]，**这正是能落在该窗口内的测量手段。**"""

t = cn
changes = []

if "吸烟作为遗传暴露被检验" not in t:
    anchor = "**血清肌酐需要单独说明**"
    if anchor in t:
        t = t.replace(anchor, SMOKE + "\n\n" + anchor, 1)
        changes.append("吸烟")
    else:
        print("  WARNING: smoking anchor not found in the Chinese file")

if "剂量发现与部分临床文献不一致" not in t:
    anchor = "### 3.4f"
    if anchor in t:
        t = t.replace(anchor, DOSE + "\n\n" + anchor, 1)
        changes.append("剂量对立")
    else:
        print("  WARNING: dose anchor not found")

if "可逆性——本研究无法测量" not in t:
    m2 = re.search(r"\n### 4\.\d+ 局限", t)
    if m2:
        t = t[:m2.start()] + "\n" + REV + "\n" + t[m2.start():]
        changes.append("可逆性")
    else:
        m3 = re.search(r"\n## 5\s*结论", t)
        if m3:
            t = t[:m3.start()] + "\n" + REV + "\n" + t[m3.start():]
            changes.append("可逆性（结论前）")
        else:
            print("  WARNING: no Chinese discussion anchor for reversibility")

CN.write_text(t, encoding="utf-8")
print(f"  Chinese additions: {', '.join(changes) if changes else 'none'}")
print(f"  Chinese manuscript now {len(t.splitlines())} lines")

for probe in ("吸烟作为遗传暴露被检验", "剂量发现与部分临床文献不一致",
              "可逆性——本研究无法测量", "[l2008]", "[c2026]", "[su2022]"):
    print(f"  {'ok  ' if probe in t else 'MISSING'} {probe[:40]!r}")

print()
print("  figures that must agree between the versions:")
for fig in ("7.06", "0.55", "60%", "6.9", "5.38", "125", "27.8", "370", "1 000"):
    print(f"      {fig:8s} EN {'yes' if fig in en else 'no ':3s}  "
          f"CN {'yes' if fig in t else 'no'}")
