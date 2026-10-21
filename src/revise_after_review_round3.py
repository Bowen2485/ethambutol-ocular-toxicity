# -*- coding: utf-8 -*-
"""Third review round: narrow the replication claim, and fix the four remaining defects.

    1. cross-system replication now applies to the optic-nerve signal only; the internal-control
       pattern is claimed for FAERS and JADER, not for Canada Vigilance
    2. the 6.21%/3.04% proportions inherited from the previous version are deleted, because the
       current Results define neither endpoint and a report proportion is not an incidence
    3. the fixed-regimen outcome is defined as the four-term composite it actually is, and the
       effect measure is called a ratio of reporting proportions rather than a rate ratio
    4. the onset analysis reports its group sizes, its missingness and its term definition, and
       explains why 83 is not 432
    5. 23.52 becomes 23.51, the "absence of a signal" wording is corrected for a non-specific
       comparator, and the data-availability statement links to the tagged version
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"

# ------------------------------------------------------------------- numbers
tto = pd.read_csv(RES / "faers_tto.csv", encoding="utf-8-sig")
n_total = int(tto[tto.group.str.startswith("All")].n.iloc[0])
n_optic = int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0])
n_non = int(tto[tto.group.str.startswith("No ocular")].n.iloc[0])
med_o = tto[tto.group.str.startswith("Optic-nerve")].median_days.iloc[0]
q25_o = tto[tto.group.str.startswith("Optic-nerve")].q25_days.iloc[0]
q75_o = tto[tto.group.str.startswith("Optic-nerve")].q75_days.iloc[0]
med_n = tto[tto.group.str.startswith("No ocular")].median_days.iloc[0]
q25_n = tto[tto.group.str.startswith("No ocular")].q25_days.iloc[0]
q75_n = tto[tto.group.str.startswith("No ocular")].q75_days.iloc[0]
profile = pd.read_csv(RES / "faers_cases_profile.csv", encoding="utf-8-sig", low_memory=False)
n_any_optic = int(profile["any_optic"].sum())
n_cases = len(profile)
assert (n_total, n_optic, n_non, n_any_optic, n_cases) == (2446, 83, 2289, 472, 15510), \
    (n_total, n_optic, n_non, n_any_optic, n_cases)
missing = n_cases - n_total

# ------------------------------------------------------------------ point 1
p = MAN / "TADS_results.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"What replicates across the three systems is the pattern.*?double checks\.|"
                r"What replicates across the three systems is the pattern.*?hundreds\.", text, re.S)
assert old, "replication sentence not found"
new = ("Across all three systems, an optic-nerve-related disproportionality signal was observed. "
       "The non-specific term comparison was available in FAERS and, for the mapped terms, "
       "JADER; Canada Vigilance supported the direction of the optic-nerve signal but did not "
       "permit an equivalent term-level comparison. Cross-system replication therefore applies to "
       "the optic-nerve signal, whereas the full internal-control pattern was not replicated in "
       "all three systems. Case counts are shown alongside every estimate because a large ratio "
       "computed on a handful of cases is not the same finding as a moderate ratio computed on "
       "hundreds.")
text = text[:old.start()] + new + text[old.end():]

# also fix the onset paragraph (point 4) in the same file
old = re.search(r"Time from starting ethambutol to the reported event could be computed.*?rather than by sampling\.", text, re.S)
assert old, "onset paragraph not found"
new = (f"Time from starting ethambutol to the reported event could be computed in {n_total:,} of "
       f"the {n_cases:,} ethambutol cases ({100*n_total/n_cases:.1f}%). In this analysis an "
       f"optic-nerve event was defined by the case-level term list (17 preferred terms, "
       f"supplementary Table S8), which is wider than the 45-term query: {n_any_optic} cases "
       f"carried at least one of those terms and {n_optic} had a usable interval, against "
       f"{n_non:,} cases in the non-ocular group. The absolute number is therefore not comparable "
       f"with the {432} exposed cases of the query, which use a different term set. Median interval "
       f"was {med_o:.0f} days (IQR {q25_o:.0f}–{q75_o:.0f}) for optic-nerve events and {med_n:.0f} "
       f"days (IQR {q25_n:.0f}–{q75_n:.0f}) for non-ocular events. The remaining {missing:,} cases "
       f"({100*missing/n_cases:.1f}%) lacked a therapy start date, an event date, or an interval "
       f"within the accepted range, so the analysis rests on the subset with complete dates and "
       f"that subset is defined by completeness rather than by sampling.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("results: replication narrowed; onset paragraph rewritten")

# ------------------------------------------------------------------ point 3
p = MAN / "TADS_results.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"Within the antitubercular class, the one comparison.*?within-class claim\.", text, re.S)
assert old, "regimen paragraph not found"
reg = json.loads((RES / "audit_regimen.json").read_text(encoding="utf-8"))
w = reg["strata"]["rifampicin+isoniazid+pyrazinamide+ethambutol"]
o = reg["strata"]["rifampicin+isoniazid+pyrazinamide"]
new = (f"Within the antitubercular class, the one comparison in which the background regimen is "
       f"held constant — reports naming rifampicin, isoniazid and pyrazinamide, partitioned by "
       f"whether ethambutol is also named — used a composite optic-nerve outcome defined as a report "
       f"containing at least one of four preferred terms: optic neuropathy, optic neuritis, optic "
       f"atrophy or toxic optic neuropathy. The proportion of reports carrying that composite was "
       f"{100*w['n_optic']/w['n']:.2f}% ({w['n_optic']}/{w['n']:,}) when ethambutol was named, "
       f"against {100*o['n_optic']/o['n']:.2f}% ({o['n_optic']}/{o['n']:,}) when it was not, a "
       f"ratio of reporting proportions of {reg['rate_ratio']:.2f} "
       f"({reg['rate_ratio_lcl']:.2f}–{reg['rate_ratio_ucl']:.2f}). The interval includes unity, "
       "the unexposed group is small, and the composite was assembled for this comparison rather "
       "than fixed as a primary outcome, so the contrast is reported as a supporting analysis and "
       "not as a within-class effect.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("results: fixed-regimen outcome defined")

p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"Within the antitubercular class, the optic-nerve rate was compared.*?not used as evidence\.", text, re.S)
assert old, "methods regimen sentence not found"
new = ("Within the antitubercular class, the optic-nerve outcome was a composite defined for this "
       "comparison as a report containing at least one of four preferred terms — optic neuropathy, "
       "optic neuritis, optic atrophy or toxic optic neuropathy, matched in both spellings — and "
       "the proportion of reports carrying it was compared between reports naming rifampicin, "
       "isoniazid and pyrazinamide with and without ethambutol. The ratio of those proportions is "
       "reported, not an incidence rate ratio, because the denominator is reports rather than "
       "treated patients; the composite was formed for this comparison and is not a pre-specified "
       "primary outcome. Strata in which the groups differ in disease state — in particular "
       "isoniazid-only reports, largely latent-infection prophylaxis — are reported but not used "
       "as evidence.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("methods: fixed-regimen definition added")

# ------------------------------------------------------------------ point 2/5 discussion
p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
pairs = [
    ("The design also changes what can be claimed. A signal that is concentrated in one anatomical "
     "category, in three systems, is a stronger basis for a safety hypothesis than a single elevated "
     "organ-system count, and it is the kind of pattern that can be checked in other databases. It "
     "is not evidence of incidence, and the absolute proportions reported here — 6.21% of ethambutol "
     "cases with any ocular event, 3.04% with an optic-nerve event — sit at the upper end of the "
     "published clinical range because stimulated reporting for a well-known adverse effect inflates "
     "the numerator and the denominator is reports rather than exposures.",
     "The design also changes what can be claimed. A signal concentrated in one anatomical category, "
     "reproduced in an independent national system, is a stronger basis for a safety hypothesis than "
     "a single elevated organ-system count, and it is the kind of pattern that can be checked in "
     "other databases. It is not evidence of incidence, and no proportion in this analysis can be "
     "set against a clinical incidence, because the denominator is reports rather than treated "
     "patients and stimulated reporting for a well-known adverse effect inflates the numerator."),
    ("The same pattern — a strong optic-nerve signal with no excess in the non-specific terms — "
     "appeared in JADER and in Canada Vigilance, systems with different reporters, different coding "
     "of suspect drugs and different reporting cultures.",
     "The optic-nerve-related signal was also observed in JADER and Canada Vigilance, systems with "
     "different reporters, different coding of suspect drugs and different reporting cultures. The "
     "non-specific term contrast was reproduced in FAERS and, for the mapped terms, JADER, whereas "
     "Canada Vigilance provided supporting evidence only for the optic-nerve signal."),
    ("at 23.52 against 4.13 for the next", "at 23.51 against 4.13 for the next"),
    ("The controls bound the conclusion in both directions. The absence of a signal for cataract, "
     "dry eye, eye pain and glaucoma makes a general increase in ocular reporting an unlikely "
     "explanation for the optic-nerve result,",
     "The controls bound the conclusion in both directions. No excess reporting was observed for "
     "the selected terms — cataract 0.89, dry eye 0.28, glaucoma 0.28 and eye pain 0.66 — which "
     "makes a general increase in ocular reporting an unlikely explanation for the optic-nerve "
     "result,"),
]
for old_s, new_s in pairs:
    assert old_s in text, f"discussion: not found {old_s[:60]!r}"
    text = text.replace(old_s, new_s, 1)
p.write_text(text, encoding="utf-8")
print("discussion: replication boundary, proportions and wording corrected")

# -------------------------------------------------------- data availability
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = "are available at\nhttps://github.com/Bowen2485/ethambutol-ocular-toxicity under an MIT licence."
new = ("are available at\nhttps://github.com/Bowen2485/ethambutol-ocular-toxicity/tree/"
       "v2.0-tads-2026-10-21 (release tag `v2.0-tads-2026-10-21`) under an MIT licence.")
assert old in s, "data availability sentence not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("statements: data availability links to the tag")

print(f"\nonset: {n_total:,}/{n_cases:,} cases, optic {n_optic}, non-ocular {n_non:,}, "
      f"17-term optic set {n_any_optic}, missing {missing:,}")
