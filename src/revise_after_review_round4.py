# -*- coding: utf-8 -*-
"""Fourth review round.

    1. Results 3.3 now reports the four negative controls and the two non-specific comparators as
       the Methods defines them; the previous text called conjunctivitis a comparator and counted
       only three negative controls
    2. Discussion 4.3 states the vision-blurred exception and stops short of claiming anatomical
       specificity
    3. the onset section names the ocular group (157, of which 74 are neither optic-nerve nor
       non-ocular) and says the primary comparison is optic-nerve vs non-ocular
    4. the abstract separates the optic-nerve replication from the control-term comparison, and
       summarises the transcriptomic result
    5. the declarations become "Statements and Declarations" with separate items and explicit
       "Not applicable" where nothing applies; a Plain Language Title is added
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"

d = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
pt = {r["term"]: r for r in d["pt"]}
tto = pd.read_csv(RES / "faers_tto.csv", encoding="utf-8-sig")


def ci(term: str) -> str:
    r = pt[term]
    return f"{r['ror']:.2f} ({r['ror_lcl']:.2f}–{r['ror_ucl']:.2f})"


# ------------------------------------------------------------------- 3.3
p = MAN / "TADS_results.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"The three negative controls were at or below background.*?as the optic-nerve terms\.", text, re.S)
assert old, "3.3 paragraph not found"
new = (f"The four pre-specified negative controls showed no positive disproportionality signal: "
       f"cataract {ci('Cataract')}, conjunctivitis {ci('Conjunctivitis')}, dry eye "
       f"{ci('Dry eye')} and glaucoma {ci('Glaucoma')}. The two non-specific comparators behaved "
       f"differently from one another: eye pain was reported less often than expected "
       f"({ci('Eye pain')}), whereas vision blurred showed a modest excess ({ci('Vision blurred')} "
       f"on {pt['Vision blurred']['a']} cases). This pattern is less consistent with a uniform "
       f"increase across all ocular reporting, although outcome-specific recognition and coding "
       f"cannot be excluded, and the excess for vision blurred is reported rather than set aside.")
text = text[:old.start()] + new + text[old.end():]

# ------------------------------------------------------------------- 3.6
old = re.search(r"The absolute number is therefore not comparable with the 432 exposed cases of "
                r"the query, which use a different term set\.", text, re.S)
assert old, "3.6 sentence not found"
n_ocular = int(tto[tto.group.str.startswith("Ocular event")].n.iloc[0])
n_optic = int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0])
med_o = tto[tto.group.str.startswith("Ocular event")].median_days.iloc[0]
lo_o = tto[tto.group.str.startswith("Ocular event")].q25_days.iloc[0]
hi_o = tto[tto.group.str.startswith("Ocular event")].q75_days.iloc[0]
new = (f"The absolute number is therefore not comparable with the 432 exposed cases of the query, "
       f"which use a different term set. Ocular events as a whole numbered {n_ocular}, of which "
       f"{n_optic} were optic-nerve and {n_ocular - n_optic} were other ocular events; that group "
       f"had a median of {med_o:.0f} days (IQR {lo_o:.0f}–{hi_o:.0f}), and the primary comparison "
       f"reported here is optic-nerve against non-ocular events.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("results: 3.3 regrouped; 3.6 ocular group added")

# ---------------------------------------------------------------- discussion
p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"The controls bound the conclusion in both directions\..*?not a toxicity profile\.", text, re.S)
assert old, "4.3 controls paragraph not found"
new = ("The controls bound the conclusion in both directions. The four negative-control terms did "
       "not show positive disproportionality signals, whereas the non-specific comparators were "
       "not uniformly null: eye pain was below unity, but vision blurred showed a modest elevation "
       f"({ci('Vision blurred')}). The absence of comparable elevations for the negative-control "
       "terms is less consistent with a uniform increase in ocular reporting. The vision-blurred "
       "signal, and the possibility of outcome-specific recognition and coding, mean that the "
       "internal contrast cannot establish anatomical specificity or exclude reporting bias. It "
       "also does not show that the negative-control events are not caused by the drug: a true "
       "effect that is small relative to background reporting would not appear. The result is a "
       "statement about the shape of the reporting signal, not a toxicity profile.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("discussion: 4.3 now carries the vision-blurred exception")

# ------------------------------------------------------------------- abstract
p = MAN / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
old = ("Control terms were mostly at or below background, but vision blurred showed a modest excess "
       "(1.50, 1.28–1.76). The pattern replicated in JADER (optic neuropathy 570.96, 413.50–788.37) "
       "and Canada Vigilance (21.85, 14.13–33.79). Median onset was 125 days, against 33 days for "
       "non-ocular events. The transcriptomic reanalysis was consistent with an antioxidant and "
       "autophagic response but did not reproduce selected ferroptosis predictions.")
assert old in text, "abstract results block not found"
new = ("The four negative controls showed no positive signal, but vision blurred did (1.50, "
       "1.28–1.76). An optic-nerve-related signal was also observed in JADER (optic neuropathy "
       "570.96, 413.50–788.37) and Canada Vigilance (composite outcome 21.85, 14.13–33.79); the "
       "non-specific comparison was assessable in FAERS and, for mapped terms, JADER, but not in "
       "Canada. Median onset was 125 days against 33 for non-ocular events. In the exploratory "
       "transcriptomic analysis, selected ferroptosis-related predictions were not reproduced, and "
       "their clinical relevance remains uncertain.")
text = text.replace(old, new, 1)

#: a plain-language title is a separate submission field, not the paper title
if "**Plain Language Title.**" not in text:
    marker = "**Keywords.**"
    plt_ = ("**Plain Language Title.** How side-effect reports describe eye problems with the "
            "tuberculosis drug ethambutol\n\n")
    text = text.replace(marker, plt_ + marker, 1)
p.write_text(text, encoding="utf-8")
print("abstract: replication split and transcriptome added; plain-language title inserted")

# --------------------------------------------------------------- declarations
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
start = s.index('STATEMENTS = """')
end = s.index('"""', start + len('STATEMENTS = """')) + 3
NEW = '''STATEMENTS = """
## Statements and Declarations

**Ethics approval and consent to participate.** Not applicable. The study used publicly available,
de-identified aggregate data from pharmacovigilance databases and public gene-expression series. No
human participants were recruited, no identifiable information was accessed, and no ethics
approval was therefore required.

**Consent for publication.** Not applicable. No individual person's data are reported.

**Availability of data and materials.** FAERS quarterly ASCII releases are available from the U.S.
Food and Drug Administration
(https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html); JADER from the Pharmaceuticals
and Medical Devices Agency of Japan; Canada Vigilance from Health Canada (cvponline); GSE294687 and
GSE318912 from NCBI GEO. The derived tables that support the findings — the de-duplication map, the
2×2 tables, `results/main_results.json` and the code that generates every table and figure — are
available at https://github.com/Bowen2485/ethambutol-ocular-toxicity/tree/v2.0-tads-2026-10-21
(release tag `v2.0-tads-2026-10-21`) under an MIT licence.

**Code availability.** All analysis scripts, the data dictionary and the results file are in the
repository named above, under the same release tag. The scripts record the software versions and
random seeds used.

**Funding.** This research received no specific grant from any funding agency in the public,
commercial, or not-for-profit sectors.

**Declaration of conflicting interests.** The authors declare no competing interests.

**Author contributions.** Bowen Shi: conceptualisation, methodology, software, formal analysis,
writing — original draft. Jing Yan: conceptualisation, supervision, writing — review and editing.
Zhengzheng Wu: supervision. Siyuan Yang: writing — review and editing. Yaqin Tan: investigation.
Xuan Wang: visualisation. All authors read and approved the final manuscript.

**Acknowledgements.** None.
"""'''
s = s[:start] + NEW + s[end:]
p.write_text(s, encoding="utf-8")
print("statements: reformatted as Statements and Declarations")
