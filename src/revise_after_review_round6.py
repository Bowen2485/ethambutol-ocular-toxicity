# -*- coding: utf-8 -*-
"""Sixth review round.

    1. Canada Vigilance is reclassified: its outcome is a study-specific string match on terms
       containing OPTIC, reported as an exploratory composite, not a re-implementation of the
       45-term query.  The Table 3 footnote's 1,308 is corrected to what it is - reports in the
       whole database, not exposed reports.
    2. Methods stop promising results the supplement does not contain: the PRR/IC025 sentence and
       the multivariable logistic paragraph are removed, and the comparator list is cut to the
       three drugs actually analysed.
    3. The onset term list is cited as Table S9, not S8.
    4. The autophagy sentence no longer claims a flux blockade from static transcripts.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
can = json.loads((ROOT / "results" / "canada_vigilance_ethambutol.json").read_text(encoding="utf-8"))
n_terms = len(can["optic_terms"])

# ================================================================ methods
p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")

pairs = [
    ("Five comparator drugs were defined in the same way for the within-class analysis: isoniazid, "
     "rifampicin, pyrazinamide, streptomycin and linezolid.",
     "Three comparator drugs were defined in the same way for the within-class analysis: isoniazid, "
     "rifampicin and pyrazinamide."),
    ("The proportional reporting ratio with its χ² statistic and the Bayesian information component "
     "(IC025, Norén prior) were computed as complementary measures and are reported in the "
     "supplementary tables. ",
     ""),
    ("Age, sex and reporting region were examined in a multivariable logistic model of an ocular "
     "event within the ethambutol cases. These coefficients are reported in the supplement and are "
     "not interpreted as patient-level risk factors, because the database records reports rather "
     "than patients.",
     "Age, sex and reporting region were described for the cohort; no regression model of an ocular "
     "event is reported, because coefficients from a reports database cannot be read as "
     "patient-level risk factors."),
    ("The optic-nerve comparison was run in JADER and in Canada Vigilance, but the two systems do "
     "not supply the same endpoints: JADER provides MedDRA/J terms for the optic-nerve and the "
     "non-specific terms alike, whereas the Canadian extract carries an optic-nerve composite and "
     "a system-organ-class count but no term-level control panel.",
     "The optic-nerve comparison was run in JADER and in Canada Vigilance, but the two systems do "
     "not supply the same endpoint. JADER provides MedDRA/J terms for the optic-nerve and the "
     "non-specific terms alike, so the FAERS contrast can be repeated at term level. The Canadian "
     "extract carries a composite of every preferred term containing the string OPTIC "
     f"({n_terms} such terms appear in the extract) and a system-organ-class count, but no "
     "term-level control panel. That composite is a study-specific string match, not a "
     "re-implementation of the 45-term query: it includes terms whose clinical meaning differs from "
     "drug-induced optic neuropathy, such as imaging terms and surgical procedures, so the Canadian "
     "analysis is reported as exploratory and is not treated as an equivalent replication."),
]
for old, new in pairs:
    assert old in text, f"methods: not found {old[:60]!r}"
    text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("methods: comparators, PRR/IC025, logistic, Canada definition")

# ================================================================ results
p = MAN / "TADS_results.md"
text = p.read_text(encoding="utf-8")

old_can = re.search(r"In Canada Vigilance, 965 reports named ethambutol.*?lives in the former\.", text, re.S)
assert old_can, "results: Canada paragraph not found"
new_can = (f"In Canada Vigilance, 965 reports named ethambutol, 21 of which carried at least one "
           f"preferred term containing OPTIC, giving an ROR of 21.85 (14.13–33.79); restricted to "
           f"the 460 suspect reports the estimate was 44.63 (28.42–70.10) on 20 cases. That "
           f"composite is broader than the FAERS query and includes terms of different clinical "
           f"meaning, so it is read as an exploratory optic-related signal rather than as a repeat "
           f"of the query. The system-organ-class measure for eye disorders was much weaker, 2.60 "
           f"(2.12–3.18): the organ-system category pools optic-nerve and non-specific events, and "
           f"the association lives in the former.")
text = text[:old_can.start()] + new_can + text[old_can.end():]

old = "(17 preferred terms, supplementary Table S8)"
new = "(17 preferred terms, supplementary Table S9)"
assert old in text
text = text.replace(old, new, 1)

old = ("the pattern of a flux blockade rather than of increased degradation")
new = ("a pattern compatible with an altered autophagy-associated response, although transcript "
       "levels do not establish autophagic flux")
assert old in text
text = text.replace(old, new, 1)

#: the tiering sentence at the end of 3.5
old = ("Across all three systems, an optic-nerve-related disproportionality signal was observed. "
       "The non-specific term comparison was available in FAERS and, for the mapped terms, JADER; "
       "Canada Vigilance supported the direction of the optic-nerve signal but did not permit an "
       "equivalent term-level comparison. Cross-system replication therefore applies to the "
       "optic-nerve signal, whereas the full internal-control pattern was not replicated in all "
       "three systems.")
new = ("The three systems therefore contribute at different levels. FAERS provides the primary "
       "contrast between the eleven ocular queries and the term-level control comparison; JADER "
       "provides term-level external support, with its own exposure-role definition and a "
       "Japanese-to-English mapping; Canada Vigilance provides a broader, string-matched "
       "optic-related composite that points in the same direction but is not an equivalent "
       "replication. Cross-system replication therefore applies to the direction of the "
       "optic-nerve signal, whereas the full internal-control pattern was examined in one database "
       "and, at term level, in a second.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("results: Canada tiered, S9 reference, autophagy wording")

# ================================================================ abstract
p = MAN / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
old = ("An optic-nerve signal was also observed in JADER (optic neuropathy 570.96, 413.50–788.37) "
       "and Canada Vigilance (21.85, 14.13–33.79); the non-specific comparison was possible in "
       "FAERS and, for mapped terms, JADER, not Canada.")
new = ("A term-level optic-nerve signal was also observed in JADER (optic neuropathy 570.96, "
       "413.50–788.37); Canada Vigilance showed a broader string-matched optic composite (21.85, "
       "14.13–33.79). The non-specific comparison was possible in FAERS and, for mapped terms, "
       "JADER, not Canada.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
block = text[text.find("## Abstract"):text.find("**Keywords")]
print("abstract words:", len([w for w in re.sub(r"[#*]", " ", block).split() if re.search(r"\w", w)]))

# ================================================================ discussion
p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
old = ("The optic-nerve-related signal was also observed in JADER and Canada Vigilance, systems "
       "with different reporters, different coding of suspect drugs and different reporting "
       "cultures.")
new = ("The optic-nerve-related signal was also observed in JADER, and in Canada Vigilance under a "
       "broader string-matched definition; the systems differ in reporters, in the coding of "
       "suspect drugs and in reporting culture.")
assert old in text
text = text.replace(old, new, 1)

old = ("In these data the reported time to onset had a median of 125 days, with 11.0% of "
       "optic-nerve events reported within 30 days of starting treatment and 23.2% within 60 days. "
       "That distribution describes reports with complete dates, not the incidence we would see in "
       "a monitored cohort")
new = ("In these data the reported time to onset had a median of 125 days, with 11.0% of "
       "optic-nerve events reported within 30 days of starting treatment and 23.2% within 60 days. "
       "That median comes from the 17-term case-level definition and the 83 reports with complete "
       "dates, not from the 432-case query, and it describes reports with complete dates rather "
       "than the incidence we would see in a monitored cohort")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("discussion: Canada tiering and onset caveat")

# =========================================================== table 3 footnote
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = ('"Any optic-nerve term" follows the MedDRA rule for the narrow optic-nerve\n'
       'search - every preferred term containing the string OPTIC; ')
if old not in s:
    m = re.search(r'ROR, reporting odds ratio\. "Any optic-nerve term".*?\n\n', s, re.S)
    assert m, "table 3 note not found"
    old = m.group(0)
new = (f'ROR, reporting odds ratio. The Canadian outcome is an exploratory composite of every\n'
       f'preferred term containing the string OPTIC ({n_terms} such terms appear in the extract); '
       f'it is not the\n45-term query. A total of {can["n_optic"]:,} reports in the full Canada '
       f'Vigilance database carried at least one\nof these terms, and {can["cells"][0]["a"]} of them '
       f'named ethambutol. The exposed-case count is reports, not terms.\n\n')
if old.endswith("\n\n"):
    s = s.replace(old, new, 1)
else:
    s = s.replace(old, new.strip("\n"), 1)
p.write_text(s, encoding="utf-8")
print("table 3 footnote corrected")
