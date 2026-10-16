# -*- coding: utf-8 -*-
"""
Add the four missing references and insert the three findings that depend on them.

Fixes to the previous attempt
    That script had a stray comma inside the methods dictionary, which is a syntax error, and
    it wrote placeholder citation keys such as [ref_thai] into the manuscript.  Placeholders
    would not resolve in the bibliography and would render as question marks, so the citations
    are now written with the keys the .bib file will actually carry, and the keys are created
    in the same run.

Which references are new
    Of the five papers supplied, only the Thai cohort is already in the bibliography, under
    the key p2023.  The Korean cohort, the 2026 meta-analysis, the OCT vessel-density study
    and the fluoxetine method paper are added here.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
BIB = ROOT / "submission" / "references.bib"

#: key -> bibtex entry.  The keys follow the naming the file already uses: a first-author
#: initial, a year, and a letter where the year repeats.
NEW = {
    "l2008": """@article{l2008,
  author = {Lee, Eun Ji and Kim, Seong-Joon and Choung, Ho Kyung and Kim, Jeong Hun and Yu, Young Suk},
  title = {Incidence and clinical features of ethambutol-induced optic neuropathy in Korea},
  journal = {J Neuroophthalmol},
  year = {2008},
  volume = {28},
  number = {4},
  pages = {269--277},
  doi = {10.1097/WNO.0b013e31818e3c6b}
}""",
    "c2026": """@article{c2026,
  title = {Risk factors for ethambutol-induced optic neuropathy: a systematic review and meta-analysis of comparative studies},
  journal = {Can J Ophthalmol},
  year = {2026},
  doi = {10.1016/j.jcjo.2026.03.004},
  note = {Systematic review and meta-analysis; eleven studies, 370 patients}
}""",
    "su2022": """@article{su2022,
  author = {Su, Li and Li, Qi and Zhu, Liwei and others},
  title = {Characterisation of macular superficial vessel density alteration in preclinical ethambutol-induced optic neuropathy using optical coherence tomography angiography},
  journal = {Br J Ophthalmol},
  year = {2022},
  volume = {106},
  number = {3},
  pages = {422--426},
  doi = {10.1136/bjophthalmol-2020-317742}
}""",
    "f2026": """@article{f2026,
  title = {Deciphering the molecular mechanisms of fluoxetine-induced sexual dysfunction: evidence from pharmacovigilance, network toxicology, and molecular docking},
  journal = {Prog Neuropsychopharmacol Biol Psychiatry},
  year = {2026},
  doi = {10.1016/j.pnpbp.2026.111773},
  note = {Same genre as this analysis: disproportionality plus network toxicology plus docking}
}""",
}

bib = BIB.read_text(encoding="utf-8")
added = []
for key, entry in NEW.items():
    if re.search(r"@" + r"\w+" + r"\{" + re.escape(key) + r",", bib):
        print(f"  {key} already present")
        continue
    bib = bib.rstrip() + "\n\n" + entry + "\n"
    added.append(key)
BIB.write_text(bib, encoding="utf-8")
print(f"  added to references.bib: {added if added else 'none'}")

n_entries = len(re.findall(r"@\w+\{", bib))
print(f"  bibliography now holds {n_entries} entries")

# ---------------------------------------------------------------- manuscript additions
t = EN.read_text(encoding="utf-8")
changes = []

# smoking result, placed before the serum-creatinine paragraph
if "Smoking was tested as a genetic exposure" not in t:
    import pandas as pd
    mr = pd.read_csv(ROOT / "results" / "mr_opengwas_results.csv", encoding="utf-8-sig")
    sm = mr[mr.exposure.isin(["smoking_initiation", "cigarettes_per_day"])]
    n_si = int(sm[sm.exposure == "smoking_initiation"].n_snp.iloc[0])
    n_cd = int(sm[sm.exposure == "cigarettes_per_day"].n_snp.iloc[0])
    qmin = float(sm.p_fdr.min())
    rows = []
    for out in sorted(sm.outcome.unique()):
        sub = sm[sm.outcome == out]
        si = sub[sub.exposure == "smoking_initiation"]
        cd = sub[sub.exposure == "cigarettes_per_day"]
        if si.empty or cd.empty:
            continue
        si, cd = si.iloc[0], cd.iloc[0]
        rows.append(f"| {out.replace('H7_', '')} | {si['or']:.2f} ({si.or_lcl:.2f}–"
                    f"{si.or_ucl:.2f}) | {si.p_fdr:.2f} | {cd['or']:.2f} "
                    f"({cd.or_lcl:.2f}–{cd.or_ucl:.2f}) | {cd.p_fdr:.2f} |")
    table = "\n".join(rows)
    SMOKE = f"""**Smoking was tested as a genetic exposure and shows no effect.** The panel carries
two smoking traits and neither is associated with any of the six optic-nerve or visual outcomes
after Benjamini-Hochberg correction (all q ≥ {qmin:.2f}). Smoking initiation is the stronger of
the two, with {n_si} instruments:

| Outcome | Smoking initiation, OR (95% CI) | q | Cigarettes per day, OR (95% CI) | q |
|---|---|---|---|---|
{table}

This is reported because a cohort of 4,141 ethambutol recipients found smoking an independent
risk factor for optic neuropathy on adjusted logistic regression (OR 7.06, p = 0.01) [p2023].
The two are not in direct conflict — a genetic instrument estimates lifelong liability to
smoke, whereas an adjusted estimate in a treated cohort captures current smoking together with
whatever it correlates with — but they do not corroborate each other either. **The result is an
absence of a detectable effect rather than a demonstration of none**: smoking initiation is
powered at {n_si} instruments and its estimates sit near unity with intervals that include it,
while cigarettes per day, at {n_cd} instruments, is weaker still and its intervals are
correspondingly wide."""
    anchor = "Serum creatinine deserves a note"
    if anchor in t:
        t = t.replace(anchor, SMOKE + "\n\n" + anchor, 1)
        changes.append("smoking MR result")
    else:
        print("  WARNING: smoking anchor not found")

# dose opposition, before the subgroup section
if "The dose finding disagrees with part of the clinical literature" not in t:
    DOSE = """**The dose finding disagrees with part of the clinical literature, and the reason is
report completeness.** This analysis found that daily dose did not predict the optic-nerve
outcome once exposure duration was accounted for (likelihood-ratio P = 0.55), whereas the
Korean cohort of 1,000 patients reports the opposite ordering: renal dysfunction and the daily
dose contributed, but not the duration of treatment [l2008]. A 2026 systematic review of eleven
studies and 370 patients resolves the same question the other way, finding longer duration the
principal factor and giving a dose gradient — prevalence 1% below 15 mg/kg/day, threefold higher
at 20 mg/kg/day [c2026].

Both can hold, and the reason this analysis is the weakest of the three on dose is stated in
Section 3.7: only 27.8% of the optic-nerve reports carry age, sex and a therapy start date
together, so the dose model is fitted on the minority of cases with complete exposure fields
and has little power to detect a dose effect. **The dose result is therefore inconclusive rather
than negative**, and the clinical literature is left to carry the dose question."""
    anchor = "### 3.7b"
    if anchor in t:
        t = t.replace(anchor, DOSE + "\n\n" + anchor, 1)
        changes.append("dose opposition")

# reversibility, in the discussion before the limitations
if "Reversibility, which this study cannot measure" not in t:
    REV = """**Reversibility, which this study cannot measure, is where the clinical literature is
most useful.** Two cohorts report it and they differ. Among 4,141 ethambutol recipients in a
Thai cohort, 60% of the 20 who developed optic neuropathy improved by at least two Snellen
lines over a mean of 6.9 months, and improvement was unrelated to demographics, past medical
history, smoking or ethambutol dosing [p2023]. In the Korean cohort fewer than a third improved
after the drug was stopped, the latency to recovery was 5.38 ± 1.71 months, and no patient who
had optic disc pallor at diagnosis recovered any visual function [l2008].

The last observation is the clinically decisive one, and it fixes the timescale this analysis
implies. The median time from starting ethambutol to an optic-nerve event here is 125 days
against 30 days for non-ocular events in the same reports, so the toxic effect is slow and the
window in which it can be detected precedes the appearance of disc pallor — after which the
Korean data indicate that recovery does not occur. A pharmacovigilance database records events
rather than outcomes, so this study cannot add to the reversibility figures; what it contributes
is the timing that makes surveillance worthwhile. Optical coherence tomography angiography
detects reduced macular superficial vessel density before clinical onset [su2022], which is the
kind of measure that would fit inside that window."""
    m = re.search(r"\n### 4\.\d+ [Ll]imitation", t)
    if m:
        t = t[:m.start()] + "\n" + REV + "\n" + t[m.start():]
        changes.append("reversibility")
    else:
        m2 = re.search(r"\n## 5\.? Conclusion", t)
        if m2:
            t = t[:m2.start()] + "\n" + REV + "\n" + t[m2.start():]
            changes.append("reversibility (before conclusions)")
        else:
            print("  WARNING: no discussion anchor for reversibility")

EN.write_text(t, encoding="utf-8")
print()
print(f"  English manuscript additions: {', '.join(changes) if changes else 'none'}")
print(f"  now {len(t.splitlines())} lines")
for probe in ("Smoking was tested as a genetic exposure",
              "The dose finding disagrees",
              "Reversibility, which this study cannot measure",
              "[l2008]", "[c2026]", "[su2022]", "[p2023]"):
    print(f"  {'ok  ' if probe in t else 'MISSING'} {probe[:52]!r}")
