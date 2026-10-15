# -*- coding: utf-8 -*-
"""
Add the exposure-definition footnote to both manuscripts.

What the footnote has to say
    Two case counts appear in the paper and they are not the same quantity:

      13,804 - the drug line must match the string ETHAMBUTOL (this is the case set
               behind the whole-database odds ratios and the case-level models)
      15,573 - the same restriction but with the salt and brand variants of the same
               molecule merged (DEXAMBUTOL, MYAMBUTOL, ETHAMBUTOL HYDROCHLORIDE,
               ETHAMBUTOL DIHYDROCHLORIDE, ETHAMBUTOL HCL, ETAMBUTOL), which is what
               the within-class comparison needs so that one molecule is not split
               across several entries

    Merging the variants adds 1,769 cases and 18 optic-neuropathy cases, and moves
    the whole-database odds ratio from 159.21 to 121.43 (a 24% reduction) without
    changing any conclusion.  The permissive alternative of also accepting the drug
    on a non-surviving report version was tested and rejected: joining on caseid
    rather than primaryid inflates the exposed set to 251,793 cases, which is an
    artefact of the join and not a valid exposure definition.

Where it goes
    * Methods 2.3 (drug exposure), as the definitional note
    * Results 3.1, where the two counts first appear
    * the Chinese translation, same two places

Usage
    python src/add_exposure_footnote.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"

EN_NOTE = """**Note on the two case counts reported in this paper.** Two ethambutol case
counts appear and they are not the same quantity. The toxicological analyses use
13,804 de-duplicated cases in which a drug line matches the string ETHAMBUTOL; this
is the case set behind the whole-database odds ratios and all case-level models. The
within-class comparison uses 15,573 cases, because comparing drugs with each other
requires the salt and brand variants of one molecule to be merged - DEXAMBUTOL,
MYAMBUTOL, ETHAMBUTOL HYDROCHLORIDE, ETHAMBUTOL DIHYDROCHLORIDE, ETHAMBUTOL HCL and
ETAMBUTOL - otherwise a single molecule is split across several entries and its rank
is driven by whichever variant happens to carry the most events. Merging adds 1,769
cases and 18 optic-neuropathy cases, and reduces the whole-database odds ratio for
optic neuropathy from 159.21 to 121.43; no conclusion depends on the choice. A third,
more permissive definition - also accepting the drug when it appears on a
non-surviving version of a re-submitted report - was tested and rejected: establishing
exposure through a caseid join rather than through the surviving report inflates the
exposed set to 251,793 cases, which is an artefact of the join rather than a valid
exposure definition. The sensitivity analysis is in
results/faers_exposure_sensitivity.csv."""

CN_NOTE = """**关于本文出现的两个病例数口径。** 文中出现两个乙胺丁醇病例数，二者并非同一量。
毒理分析使用 **13,804** 例去重病例（药物记录名称匹配字符串 ETHAMBUTOL），
这是全库比值比与全部病例层面模型所用的病例集。同类药比较使用 **15,573** 例，
因为药物间对比必须合并同一分子的盐型与商品名——DEXAMBUTOL、MYAMBUTOL、
ETHAMBUTOL HYDROCHLORIDE、ETHAMBUTOL DIHYDROCHLORIDE、ETHAMBUTOL HCL、ETAMBUTOL——
否则同一分子被拆分为多个条目，其排名取决于哪个变体恰好携带最多事件。
合并后增加 1,769 例病例与 18 例视神经病变病例，并使视神经病变的全库比值比
由 159.21 降至 121.43；**无任何结论依赖此选择**。第三种更宽松的口径
（同时接受药物出现在同一病例的非存活版本中）经检验后**予以否决**：
以 caseid 而非存活报告建立暴露会使暴露集膨胀至 251,793 例，
这是联接方式产生的假象而非有效的暴露定义。敏感性分析见
`results/faers_exposure_sensitivity.csv`。"""


def insert_after(text: str, anchor: str, addition: str) -> tuple[str, bool]:
    i = text.find(anchor)
    if i < 0:
        return text, False
    j = text.find("\n\n", i)
    if j < 0:
        return text, False
    return text[:j] + "\n\n" + addition + text[j:], True


def main() -> int:
    ok = []

    # ------------------------------------------------------------------ English
    p = ROOT / "src" / "finalize_manuscript.py"
    t = p.read_text(encoding="utf-8")
    # Methods 2.3 in the methods source file
    pm = MAN / "Methods_draft_EN.md"
    tm = pm.read_text(encoding="utf-8")
    if "two case counts" not in tm:
        tm = tm.rstrip() + "\n\n" + EN_NOTE + "\n"
        pm.write_text(tm, encoding="utf-8")
        ok.append("Methods_draft_EN.md note appended")

    # Results 3.1 in the assembler
    anchor = ("Within the ethambutol cases, **971 (7.03%)** reported at least one "
              "ocular event")
    if anchor in t and "two case counts" not in t:
        t, done = insert_after(t, "median age was 51 years", EN_NOTE)
        if not done:
            t = t.replace("### 3.2 The ocular phenotype", EN_NOTE +
                          "\n\n### 3.2 The ocular phenotype", 1)
        ok.append("assembler Results note inserted")
    p.write_text(t, encoding="utf-8")

    # ------------------------------------------------------------------ Chinese
    pc = MAN / "论文_中文版.md"
    tc = pc.read_text(encoding="utf-8")
    if "两个病例数口径" not in tc:
        marker = "### 3.2 眼部信号谱及其特异性"
        if marker in tc:
            tc = tc.replace(marker, CN_NOTE + "\n\n" + marker, 1)
        else:
            tc = tc.rstrip() + "\n\n" + CN_NOTE + "\n"
        pc.write_text(tc, encoding="utf-8")
        ok.append("CN note inserted")

    print("applied:")
    for x in ok:
        print("  -", x)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
