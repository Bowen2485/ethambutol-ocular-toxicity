# -*- coding: utf-8 -*-
"""
Add the positive control paragraph to the Chinese manuscript.

The alignment check showed three figures present in English and absent in Chinese: 1.680,
266 and 115.  The first is the body-mass-index positive control result and the other two are
its instrument count and cystatin C's.  All three come from the same paragraph, which was
written into the English file when the control was reported and has no Chinese counterpart.

This is not a stylistic choice about translation order.  The manuscript's claim that the
renal nulls are interpretable rests on the control having behaved, so a version without it
is not a translation of the argument - it is a different, weaker argument.  Both files are
submitted together and will be read against each other.

What is deliberately NOT changed
    The renal effect estimates themselves.  The Chinese section reports cystatin C on optic
    neuritis as OR 1.026 (0.865-1.216) with "150-186 instruments", and the English reports
    the same, while the pooled re-run gives 1.054 (0.886-1.254) with 115 instruments.  The
    two versions agree with each other, which is what this script is for; moving both to the
    pooled values is a separate decision about which analysis the paper presents, and it has
    not been taken.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

PARA = """
**本面板设有阳性对照，且其表现符合预期。** 纳入体质指数正是因为**较高质量指数是视神经表型的公认危险因素**，故其表现检验的是**本流程能否检出真实效应**，还是无论暴露为何都返回阴性。以 **266 个**协调工具变量，它对视神经炎给出 **OR 1.680（95%CI 1.265～2.231），p = 3.4 × 10⁻⁴，q = 0.020**——在所检验的 **60** 个"暴露×结局"配对中**唯一**经 Benjamini-Hochberg 校正后仍显著者——且 MR-Egger 截距不显著（p = 0.92），Steiger 方向性正确。**这一区分正是肾功能结果可被解读的前提**：此规模的工具变量集、经此流程分析，**确实能在一个存在效应的地方检出效应**，故肾功能的阴性是**效应的缺失，而非把握度的缺失**。若一个面板对全部暴露都返回阴性，那些阴性结果将无法解读——这正是设置该对照的理由。
"""


def main() -> None:
    t = CN.read_text(encoding="utf-8")
    if "阳性对照" in t and "1.680" in t:
        print("  the positive control paragraph is already present")
        return

    anchor = "**未检出因果效应。**"
    if anchor not in t:
        anchor = "校正后，肾功能暴露具有充分把握度"
        if anchor not in t:
            raise SystemExit("could not find the MR section anchor")

    if "**未检出因果效应。**" in t:
        # insert after the paragraph that contains this sentence
        i = t.index("**未检出因果效应。**")
        j = t.index("\n\n", i)
        t = t[:j] + "\n" + PARA.strip() + "\n" + t[j:]
        print("  inserted after the 'no causal effect detected' paragraph")
    else:
        i = t.index(anchor)
        j = t.index("\n\n", i)
        t = t[:j] + "\n" + PARA.strip() + "\n" + t[j:]
        print("  inserted after the power paragraph")

    CN.write_text(t, encoding="utf-8")
    print(f"  lines now: {len(t.splitlines())}")

    EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
    SHARED = ["1.680", "266", "0.020", "1.265", "2.231", "60", "0.92",
              "1.054", "115", "1.026", "0.865", "1.216", "150-186", "150～186"]
    print("\n  agreement on the Mendelian randomisation figures:")
    for s in SHARED:
        print(f"      {s:10s} EN {'yes' if s in EN else 'no ':3s}  "
              f"CN {'yes' if s in t else 'no'}")
    print()
    print("  Note: 1.054/115 appear only in the pooled result and 1.026/0.865-1.216 in the")
    print("  version both manuscripts report.  That choice is unchanged here.")


if __name__ == "__main__":
    main()
