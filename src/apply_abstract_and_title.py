# -*- coding: utf-8 -*-
"""
Apply the reduced abstract, the trimmed keyword list and a corrected title to both manuscripts.

Why the abstract has to be replaced rather than shortened in place
    The manuscripts carry an 867-word structured abstract.  The 378-word rewrite in
    submission/abstract_rewritten.json was prepared but never applied, and it is itself 28 words
    over the journal's limit of about 350.  So the block is replaced outright, in both languages.

The variant applied is A from src/draft_abstract_variants.py: the cut comes from Methods and no
result number is removed.  Two words were then taken out of Methods ("unique" and "then") to
afford a qualifier the earlier draft had dropped and the body requires:

    "all 90 quarterly releases" is not accurate on its own.  The body says the 90 releases
    contributed 24,389,966 submitted reports, and the Methods say 89 were usable, so the count
    is carried as "(2004Q1-2026Q2; 89 usable)".

Title
    The current title is 25 words and the checklist asked for 20 or fewer.  The candidate
    offered in that checklist reads "20.3 million spontaneous reports", which mislabels
    quantities this paper is careful about: 20,328,568 is the number of de-duplicated *cases*,
    while the *reports* number 24,389,966, and by receipt year the releases number 90.  The
    title applied here therefore says "20.3 million FAERS cases".

Keywords
    Both manuscripts listed ten keywords; Frontiers allows eight, and build_latex.py was taking
    the first eight, so molecular docking and Mendelian randomisation were being dropped by
    position.  Eight are now listed deliberately: signal detection goes, because
    disproportionality analysis already carries it, and network toxicology goes as the framework
    name, which leaves both method terms in.

Run:
    python src/apply_abstract_and_title.py            # show what would change
    python src/apply_abstract_and_title.py --write    # write it
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

EN_PARTS = [
    ("Background",
     "Ethambutol is a first-line antitubercular drug whose optic neuropathy can be "
     "irreversible, and its frequency estimates vary widely with ascertainment. No "
     "pharmacovigilance analysis has profiled the ocular phenotype against the other "
     "first-line antitubercular drugs."),
    ("Methods",
     "We analysed all 90 FDA Adverse Event Reporting System (FAERS) quarterly releases "
     "(2004Q1-2026Q2; 89 usable), de-duplicating 24,389,966 reports to 20,328,568 cases by the "
     "FDA case-version protocol. Four disproportionality measures were computed for 178 ocular "
     "MedDRA preferred terms across ethambutol and five comparator antitubercular drugs, with "
     "Benjamini-Hochberg control and four robustness specifications. We assessed time to onset, "
     "predictors and completeness, combined Europe PMC, Open Targets and STRING into a "
     "mechanism network, tested enrichment, docked ethambutol against the hub targets, and "
     "interrogated the loci against FinnGen R12 phenotypes."),
    ("Results",
     "Among 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475 "
     "(3.44%) an optic-nerve event; 45 of 152 testable ocular terms met strict signal criteria. "
     "The risk was confined to the optic nerve: optic neuropathy gave an ROR of 159.21 (95% CI "
     "134.65-188.25), whereas no non-specific ocular complaint formed a signal in the "
     "within-class comparison (vision blurred 1.15, cataract 0.81, dry eye 0.35, eye pain 0.32, "
     "glaucoma 0.18, ocular hyperaemia 0.18). Within the antitubercular class ethambutol had "
     "an ROR of 6.47 "
     "(5.38-7.79) for optic neuropathy, and restricting the comparison to ethambutol-containing "
     "regimens gave a rate ratio of 3.28 (1.03-10.40) against regimens without it, so the "
     "association is not explained by the tuberculosis population. The pattern replicated in "
     "JADER (1,054,239 cases; optic neuropathy ROR 571.0, toxic optic neuropathy 864.6, all "
     "control terms null). Median time to an optic-nerve event was 125 days versus 30 days for "
     "non-ocular events, and only 27.8% of cases carried enough detail for time-to-onset "
     "analysis. Enrichment converged on ferroptosis and mitochondrial integrity, and genetically "
     "proxied renal function showed no causal effect on any optic-nerve outcome (all q >= 0.87)."),
    ("Conclusions",
     "Ethambutol ocular toxicity is a highly specific optic-nerve signal that spares the ocular "
     "surface, is delayed by months, resists every robustness specification tested, and "
     "replicates in an independent national database. Renal impairment appears to act by "
     "raising drug exposure rather than by independently causing optic-nerve degeneration."),
]

CN_PARTS = [
    ("目的",
     "乙胺丁醇是一线抗结核药物，其视神经病变可不可逆；不同病例确认方式下报告的频率差异很大。"
     "尚无药物警戒研究将眼部表型与其它一线抗结核药作对照。"),
    ("方法",
     "分析 FDA 不良事件报告系统（FAERS）全部 90 个季度发布（2004Q1—2026Q2，可用 89 个），"
     "按 FDA 病例版本规则将 24 389 966 份报告去重为 20 328 568 例病例。以乙胺丁醇及 5 种"
     "抗结核药为暴露，对 178 个眼科 MedDRA 首选术语计算四种不成比例度量，"
     "以 Benjamini-Hochberg 法校正并另设四种稳健性口径。分析用药至发病时间、预测因素与报告"
     "充分性；随后将 Europe PMC、Open Targets 与 STRING 整合为机制网络，做功能富集，"
     "将乙胺丁醇对接至 hub 靶点，并以 FinnGen R12 视神经表型作遗传学考察。"),
    ("结果",
     "13 804 例乙胺丁醇病例中，971 例（7.03%）报告眼部事件，475 例（3.44%）报告视神经事件；"
     "152 个可检验眼科术语中 45 个达到严格信号标准。风险局限于视神经：视神经病变 ROR 159.21"
     "（95%CI 134.65～188.25），而全部泛化眼部主诉在同类药内部比较中均不成立（视物模糊 1.15、"
     "白内障 0.81、干眼 0.35、眼痛 0.32、青光眼 0.18、眼充血 0.18）。同类药内部比较中，"
     "乙胺丁醇对视神经病变的 ROR 为 6.47（5.38～7.79）；将比较限定为含乙胺丁醇方案后，"
     "相对不含该药的方案率比为 3.28（1.03～10.40），故该关联不能以结核病人群解释。"
     "该模式在日本 JADER（1 054 239 例）中独立复现：视神经症 ROR 571.0、"
     "中毒性视神经症 864.6，全部对照术语阴性。用药至视神经事件中位 125 d，非眼部事件 30 d；"
     "仅 27.8% 的病例具备足够细节做发病时间分析。富集收敛于铁死亡与线粒体完整性；"
     "遗传代理的肾功能对全部视神经结局无因果效应（q 均 ≥ 0.87）。"),
    ("结论",
     "乙胺丁醇眼部毒性是特异性极高的视神经信号：不累及眼表、延迟数月出现、经全部稳健性口径"
     "检验仍成立，并在独立国家级数据库中复现。肾功能不全的作用是提高药物暴露量，"
     "而非独立导致视神经变性。"),
]

EN_KEYWORDS = ("**Keywords.** ethambutol; optic neuropathy; pharmacovigilance; FAERS; "
               "disproportionality analysis; ferroptosis; molecular docking; "
               "Mendelian randomisation")
CN_KEYWORDS = ("**关键词** 乙胺丁醇；视神经病变；药物警戒；FAERS；不成比例分析；铁死亡；"
               "分子对接；孟德尔随机化")

EN_TITLE = ("**Ocular toxicity of ethambutol in 20.3 million FAERS cases: pharmacovigilance, "
            "network toxicology, molecular docking and genetic interrogation**")
CN_TITLE = ("# 乙胺丁醇眼毒性：2 033 万例 FAERS 病例中的药物警戒、网络毒理学、"
            "分子对接与遗传学考察")

EN_OLD_TITLE_PREFIX = "**Ocular toxicity of ethambutol: a whole-database"
CN_OLD_TITLE_PREFIX = "# 乙胺丁醇眼毒性："

EN = MAN / "Ethambutol_EyeTox_EN_full.md"
CN = MAN / "Ethambutol_EyeTox_CN_full.md"
JSON = ROOT / "submission" / "abstract_rewritten.json"


def word_count(parts) -> int:
    return sum(len(t.split()) for _, t in parts)


def _old_title_words(lines) -> str:
    """Word count of the title being replaced, or a note if it has already been replaced.

    The first version of this script looked the old title up unguarded and raised StopIteration
    on a second run, which made it a one-shot.  Re-running has to be safe: it is the documented
    way to switch variants.
    """
    old = next((ln for ln in lines if ln.startswith(EN_OLD_TITLE_PREFIX)), None)
    if old is None:
        return "already applied"
    return str(len(old.strip("*").split()))


def replace_block(lines, start_prefix, end_prefix, new_block):
    """Replace from the line starting with start_prefix up to (not including) end_prefix."""
    start = next(i for i, ln in enumerate(lines) if ln.startswith(start_prefix))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith(end_prefix))
    return lines[:start] + new_block + lines[end:]


def main(write: bool) -> int:
    en = EN.read_text(encoding="utf-8").split("\n")
    cn = CN.read_text(encoding="utf-8").split("\n")
    total = word_count(EN_PARTS)
    cn_chars = sum(len(t) for _, t in CN_PARTS)

    print("=" * 94)
    print("What will change")
    print("=" * 94)
    print(f"  English abstract   {word_count([(l, t) for l, t in EN_PARTS])} words "
          f"(limit about 350)")
    for label, text in EN_PARTS:
        print(f"      {label:<12} {len(text.split()):>3} words")
    print(f"  Chinese abstract   {cn_chars} characters")
    print(f"  English title      {len(EN_TITLE.strip('*').split())} words "
          f"(was {_old_title_words(en)})")
    print(f"  keywords           8 in each language, was 10")
    print()
    print(f"  EN title -> {EN_TITLE.strip('*')}")
    print(f"  CN title -> {CN_TITLE.lstrip('# ')}")

    if total > 350:
        print(f"\n  REFUSING: the abstract is {total} words, over the limit of 350.")
        return 1

    # placeholders keep the paragraph structure the LaTeX builder expects
    en_block = []
    for label, text in EN_PARTS:
        en_block += [f"**{label}.** {text}", ""]
    cn_block = []
    for label, text in CN_PARTS:
        cn_block += [f"**{label}** {text}", ""]

    en_new = replace_block(en, "**Background.**", "**Keywords.**", en_block)
    en_new = [EN_TITLE if ln.startswith(EN_OLD_TITLE_PREFIX) else ln for ln in en_new]
    en_new = [EN_KEYWORDS if ln.startswith("**Keywords.**") else ln for ln in en_new]

    cn_new = replace_block(cn, "**目的**", "**关键词**", cn_block)
    cn_new = [CN_TITLE if ln.startswith(CN_OLD_TITLE_PREFIX) else ln for ln in cn_new]
    cn_new = [CN_KEYWORDS if ln.startswith("**关键词**") else ln for ln in cn_new]

    print()
    print("=" * 94)
    print("Result")
    print("=" * 94)
    print(f"  English manuscript  {len(en)} -> {len(en_new)} lines")
    print(f"  Chinese manuscript  {len(cn)} -> {len(cn_new)} lines")

    if not write:
        print("\n  dry run; pass --write to apply")
        return 0

    EN.write_text("\n".join(en_new), encoding="utf-8")
    CN.write_text("\n".join(cn_new), encoding="utf-8")
    JSON.write_text(json.dumps({
        "parts": {label: text for label, text in EN_PARTS},
        "keywords": EN_KEYWORDS.replace("**Keywords.** ", ""),
        "word_counts": {label: len(text.split()) for label, text in EN_PARTS},
        "total": total,
        "note": ("Applied to manuscript/Ethambutol_EyeTox_EN_full.md by "
                 "src/apply_abstract_and_title.py. Variant A of "
                 "src/draft_abstract_variants.py; see docs/摘要压缩_ABC三方案.md."),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  written: manuscript/{EN.name}, manuscript/{CN.name}, "
          f"submission/{JSON.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
