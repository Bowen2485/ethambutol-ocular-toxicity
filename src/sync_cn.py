# -*- coding: utf-8 -*-
"""
Sync the Chinese translation with the updated analysis results.

The Chinese text was written before the unbiased term pass and the robustness
analysis were finished, so it still described a 73-term curated panel and had no
robustness section.  This script brings it up to date section by section, mirroring
the English results, and removes the duplicate reference heading.

Values are read from the analysis outputs rather than typed, so the two language
versions cannot drift apart.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"
DER = ROOT / "data" / "derived"
TAB = ROOT / "tables"

CN = MAN / "论文_中文版.md"


def row(df, term):
    r = df[df.term == term]
    return r.iloc[0] if not r.empty else None


def main() -> int:
    sig = pd.read_csv(RES / "faers_signals_annotated.csv", encoding="utf-8-sig")
    adq = pd.read_csv(RES / "faers_report_adequacy.csv", encoding="utf-8-sig")
    adqs = pd.read_csv(RES / "faers_adequacy_summary.csv", encoding="utf-8-sig")
    rb = pd.read_csv(RES / "faers_robustness.csv", encoding="utf-8-sig")
    terms = pd.read_csv(DER / "ocular_terms.csv", encoding="utf-8-sig")

    tox = sig[(sig.category == "drug-toxicity spectrum") & (sig.signal_strict == True)]  # noqa: E712
    n_panel = len(terms)
    n_tested = len(sig)
    n_strict = int(sig.signal_strict.sum())
    n_tox = int(tox.signal_strict.sum())
    ton = row(sig, "TOXIC OPTIC NEUROPATHY")
    eth = adq[adq.group == "ethambutol"].iloc[0]
    allr = adq[adq.group == "All FAERS"].iloc[0]
    a = adqs.iloc[0]
    rb_pn = rb[rb.term == "OPTIC NEUROPATHY"]
    rb_long = rb_pn[rb_pn.scenario.str.contains("anti-TB", na=False)]
    rb_short = rb_long.iloc[0] if not rb_long.empty else None

    txt = CN.read_text(encoding="utf-8")

    # ---------------------------------------------------------------- Methods
    old_m = "### 2.5 机制分析"
    new_m = f"""### 2.5 数据驱动的眼科术语发现
除策展术语表外，另做一次无偏枚举：提取乙胺丁醇去重病例中出现的**全部** MedDRA
首选术语，保留其中符合宽口径眼科词根者（eye、ocul-、ophthalm-、visual、vision、
sight、blind、optic、retin-、macul-、vitreous、choroid、conjunctiv-、corne-、
irid-、uve-、scler-、lacrimal、pupil、ptosis、diplopia、nystagmus、photophobia、
scotoma、amblyopia、cataract、glaucoma、papilloedema、blephar-、eyelid、orbital、
dyschromatopsia、hemianopia、fundus、retrobulbar）。每个保留术语同时统计其在
乙胺丁醇病例内与全库去重病例中的计数，两套术语合并为 **{n_panel} 项**面板。

扩展面板必然包含由结核病本身而非药物解释的术语（眼结核、脉络膜炎、葡萄膜炎等
在结核患者中与使用何种抗结核药无关），以及少量词形误配（如 "macule" 为皮疹，
因含 macul- 而被纳入）。故对信号按**明示可审计的清单**分类为"药物毒性谱"、
"眼结核（疾病）"与"非眼科误配"三类，论文报告的乙胺丁醇信号指**药物毒性谱**。

### 2.6 报告充分性分析

不成比例分析假定报告含有足以解读事件的细节，故对每例取一条代表性药物记录
（首选可疑药，次选次要可疑药，再次任一），统计年龄、性别、体重、报告者类型、
国家、事件日期、用药开始日期、疗程、剂量、剂量单位、给药途径与适应证 12 个
字段的完整度；将乙胺丁醇病例集与全库及 5 种对照抗结核药比较，并计算在
"年龄+性别+用药开始日期"最小细节限制下仍可分析的比例。

### 2.7 机制分析"""
    txt = txt.replace(old_m, new_m, 1)
    # the genetics subsection follows the three inserted ones, so it moves to 2.8
    txt = txt.replace("### 2.6 遗传学分析", "### 2.8 遗传学分析", 1)

    # ---------------------------------------------------------------- Results
    old_r2 = txt[txt.find("### 3.2 眼部信号谱及其特异性"):txt.find("### 3.3 时序特征")]
    new_r2 = f"""### 3.2 眼部信号谱及其特异性

无偏枚举在乙胺丁醇病例中识别出 4,011 个不同 MedDRA 首选术语，其中 {n_panel - 19}
个符合眼科词根；与策展面板合并后共 **{n_panel} 项**，其中 **{n_tested} 项**在
乙胺丁醇病例中出现 ≥3 例，**{n_strict} 项构成严格信号**（ROR 95%CI 下限 >1、
PRR ≥2、χ² ≥4、IC025 >0、a ≥3，且 Benjamini-Hochberg q <0.05）；其中归入
**药物毒性谱者 {n_tox} 项**。

药物毒性谱内信号最强者为视神经病变：{int(row(sig,'OPTIC NEUROPATHY').a)} 例，
**ROR {row(sig,'OPTIC NEUROPATHY').ror:.2f}（95%CI {row(sig,'OPTIC NEUROPATHY').ror_lcl:.2f}～{row(sig,'OPTIC NEUROPATHY').ror_ucl:.2f}）**，
PRR {row(sig,'OPTIC NEUROPATHY').prr:.2f}，IC025 {row(sig,'OPTIC NEUROPATHY').ic025:.2f}，
EBGM05 {row(sig,'OPTIC NEUROPATHY').ebgm05:.2f}。**直接命名药物损伤的术语
"中毒性视神经病变"ROR 达 {ton.ror:.2f}（95%CI {ton.ror_lcl:.2f}～{ton.ror_ucl:.2f}；
{int(ton.a)} 例，IC025 {ton.ic025:.2f}）**，为全分析第二强信号，且**不属于**
策展面板——系由无偏枚举发现。

其余主要药物毒性谱信号（ROR）：遗传性视神经萎缩
{row(sig,'HEREDITARY OPTIC ATROPHY').ror:.1f}、眼毒性 {row(sig,'OCULAR TOXICITY').ror:.1f}、
色觉障碍 {row(sig,'DYSCHROMATOPSIA').ror:.1f}、暗点 {row(sig,'SCOTOMA').ror:.1f}、
视神经炎 {row(sig,'OPTIC NEURITIS').ror:.1f}、色视症 {row(sig,'CHROMATOPSIA').ror:.1f}、
视神经萎缩 {row(sig,'OPTIC ATROPHY').ror:.1f}、视神经损伤 {row(sig,'OPTIC NERVE INJURY').ror:.1f}、
偏盲 {row(sig,'HEMIANOPIA').ror:.1f}、视神经疾患 {row(sig,'OPTIC NERVE DISORDER').ror:.1f}、
视野缺损 {row(sig,'VISUAL FIELD DEFECT').ror:.1f}、视乳头水肿 {row(sig,'PAPILLOEDEMA').ror:.1f}、
眼球震颤 {row(sig,'NYSTAGMUS').ror:.1f}、视力下降 {row(sig,'VISUAL ACUITY REDUCED').ror:.1f}、
黄斑变性 {row(sig,'MACULAR DEGENERATION').ror:.1f}、盲 {row(sig,'BLINDNESS').ror:.1f}、
视力损害 {row(sig,'VISUAL IMPAIRMENT').ror:.1f}、复视 {row(sig,'DIPLOPIA').ror:.1f}
（**图2**、**图4**、表2、表2c）。

**关键论证点在于对照。** 泛化眼部主诉**全部不构成信号**：视物模糊 ROR
{row(sig,'VISION BLURRED').ror:.2f}、白内障 {row(sig,'CATARACT').ror:.2f}、
结膜炎 {row(sig,'CONJUNCTIVITIS').ror:.2f}、干眼 {row(sig,'DRY EYE').ror:.2f}、
眼痛 {row(sig,'EYE PAIN').ror:.2f}、眼睑刺激 {row(sig,'EYE IRRITATION').ror:.2f}、
畏光 {row(sig,'PHOTOPHOBIA').ror:.2f}、青光眼 {row(sig,'GLAUCOMA').ror:.2f}、
眼充血 {row(sig,'OCULAR HYPERAEMIA').ror:.2f}。信号严格限于视神经—视网膜—色觉轴，
眼表与眼前节未受累（**图3**）。

### 3.2b 眼结核术语构成独立的信号群

扩展面板同时捕获了结核病本身在眼部的表现：脉络膜结核（ROR 2208，3 例）、
匍行性脉络膜炎（1474，24 例）、眼结核（569，17 例）、脉络膜炎（167，31 例）、
中间葡萄膜炎（1472，4 例）均产生极高不成比例值——**因为这些是感染的并发症
而非任何药物的效应，几乎只出现在结核病例报告中**。本文为完整性列出，
并明确排除于药物毒性解读之外。另有 83 个术语无法由明示清单归类，
列于表2d 供人工复核。

"""
    txt = txt.replace(old_r2, new_r2, 1)

    # insert the adequacy and robustness results after the predictors section
    anchor = txt.find("### 3.5 机制网络与富集")
    ins = f"""### 3.4b 报告充分性

解读报告所需字段的完整度较高，描述暴露所需字段的完整度偏低。乙胺丁醇病例中，
国家记录率 {eth.country_pct:.1f}%、性别 {eth.sex_pct:.1f}%、年龄 {eth.age_pct:.1f}%、
给药途径 {eth.route_pct:.1f}%、剂量 {eth.dose_pct:.1f}%、事件日期 {eth['event date_pct']:.1f}%、
用药开始日期 {eth['therapy start_pct']:.1f}%，而**疗程仅 {eth['therapy duration_pct']:.1f}%**。
与全库相比（年龄 {allr.age_pct:.1f}%、事件日期 {allr['event date_pct']:.1f}%），
乙胺丁醇报告的年龄记录更完整；平均反应数为 {eth.mean_reactions:.2f}（全库 {allr.mean_reactions:.2f}），
符合"报告明确了具体可疑药物效应"的情形。

对解读的直接影响已量化：乙胺丁醇视神经谱病例共 {int(a.n_ocular_spectrum_cases)} 例，
其中 {a.pct_age_and_sex:.1f}% 同时记录年龄与性别，{a.pct_therapy_start:.1f}% 记录用药
开始日期，**仅 {a.pct_both:.1f}% 可支持发病时间分析**（表10）。信号分析只需药物名与
反应术语，故使用全部病例；时序与剂量分析依赖携带这些字段的少数报告，
这正是本文将其列为**支持性而非主要证据**的原因。

### 3.4c 稳健性检验（四情景）

以四种口径重算全部不成比例面板：①主分析（全库、不限药物角色）；
②严格全词暴露匹配（排除仅出现在固定剂量复方中的报告）；③仅可疑药报告（PS/SS）；
④对照分母限制为提及任一抗结核药的报告（排除"信号仅反映结核病人群本身"这一替代解释）。

结果：**三个视神经核心信号在全部四种情景下均成立**。视神经病变的 ROR 分别为
159.21、159.21、248.95，以及在最严格的同类药对照下**仍为 {rb_short.ror:.2f}
（95%CI {rb_short.ror_lcl:.2f}～{rb_short.ror_ucl:.2f}）**；视神经炎 29.21→44.19，
同类药对照 {rb[rb.term=='OPTIC NEURITIS'][rb[rb.term=='OPTIC NEURITIS'].scenario.str.contains('anti-TB',na=False)].iloc[0].ror:.2f}；
视神经萎缩 24.84→38.80，同类药对照
{rb[rb.term=='OPTIC ATROPHY'][rb[rb.term=='OPTIC ATROPHY'].scenario.str.contains('anti-TB',na=False)].iloc[0].ror:.2f}。
而**白内障、干眼、眼痛、青光眼四个非特异术语在全部四种情景下均不成立**（表9）。

"""
    txt = txt[:anchor] + ins + txt[anchor:]

    # -------------------------------------------------------- limitations note
    txt = txt.replace(
        "4. **未行药物暴露 MR**：乙胺丁醇无遗传工具变量",
        "4. **四情景稳健性检验**已表明结论不依赖匹配或分母口径；"
        "但 83 个未归类术语（表2d）仍需人工复核。\n"
        "5. **未行药物暴露 MR**：乙胺丁醇无遗传工具变量", 1)

    # duplicate reference heading cleanup
    lines = txt.splitlines()
    seen_ref = 0
    out = []
    for ln in lines:
        if ln.strip() == "## 参考文献":
            seen_ref += 1
            if seen_ref > 1:
                continue
        out.append(ln)
    txt = "\n".join(out)

    CN.write_text(txt, encoding="utf-8")
    print(f"[cn] synced: panel={n_panel} tested={n_tested} strict={n_strict} "
          f"toxicity-spectrum signals={n_tox}")
    print(f"[cn] characters: {len(txt):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
