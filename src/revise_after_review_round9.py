# -*- coding: utf-8 -*-
"""Ninth review round: the last four substantive items.

    1. Table 2's P footnote names the tests actually used - Pearson for ten queries, Fisher for
       Scleral disorders - instead of pointing at a supplement that only covers the 15 terms
    2. the dataset that produced GSE294687 is cited (Cheng et al. 2025), the reanalysis is
       described as using a different method from the original, and the TPEN comparator is named
       for what it is (AC16 cardiomyocytes)
    3. the abstract classifies the eleven queries by statistical support rather than by point
       estimate, and marks the onset result as restricted to reports with usable dates
    4. the ocular-infections explanation is softened to confounding by indication
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
d = json.loads((ROOT / "results" / "main_results.json").read_text(encoding="utf-8"))

# ------------------------------------------------- Table 2 footnote (builder)
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = ('    "\\n\\nP, two-sided p value from the test named in Supplementary Table S1, which also gives "\n'
       '    "the narrow-term counts; q, Benjamini–Hochberg adjusted across the eleven queries.")')
new = ('    "\\n\\nP, two-sided P value from Pearson’s χ² test without continuity correction, except for "\n'
       '    "Scleral disorders, where Fisher’s exact test was used because the smallest expected cell "\n'
       '    "count was below 5; the narrow-term counts are in Supplementary Table S1. q, "\n'
       '    "Benjamini–Hochberg adjusted across the eleven ocular queries.")')
assert old in s, "table 2 note not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("table 2 footnote: tests named")

# --------------------------------------------------------------- methods 2.10
p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")
old = ("GSE294687 profiled human induced pluripotent stem cell-derived retinal ganglion-like cells "
       "exposed to ethambutol or vehicle in four paired preparations.")
new = ("Public series GSE294687, from the study by Cheng and colleagues [19], profiled human induced "
       "pluripotent stem cell-derived retinal ganglion-like cells exposed to ethambutol or vehicle "
       "in four paired preparations. The original study analysed these data with a count-based "
       "model; the reanalysis here uses a paired test on log-transformed counts per million, and is "
       "therefore an exploratory reanalysis with a different method rather than a reproduction of "
       "the original differential-expression results.")
assert old in text
text = text.replace(old, new, 1)

old = ("a public TPEN-treated human cell line (GSE318912) was used as an empirical zinc-chelation "
       "reference")
new = ("a public TPEN-treated human cardiomyocyte line, AC16 (GSE318912), was used as an empirical "
       "zinc-chelation reference; the difference in cell type, and the fact that the comparison is "
       "unpaired there against paired here, bound what the correlation can show")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("methods 2.10: dataset citation, method difference, AC16")

# ------------------------------------------------------------------ abstract
p = MAN / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
pairs = [
    ("four lay above unity, three below, four null",
     "four showed positive signals, three were significantly below 1 and four had intervals "
     "spanning 1"),
    ("Median onset was 125 days against 33 for non-ocular events.",
     "Among reports with usable dates, median onset was 125 days for optic-nerve events against 33 "
     "for non-ocular events."),
    # trims to stay inside 300 words
    ("rather than reflecting a general increase in ocular reporting, has not been tested against "
     "MedDRA's queries.",
     "rather than a general increase in ocular reporting, is untested against MedDRA's queries."),
    ("Retrospective disproportionality analysis of case safety reports, with replication in two "
     "systems and exploratory transcriptomics.",
     "Retrospective disproportionality analysis of case safety reports, with replication and "
     "exploratory transcriptomics."),
    ("The optic-nerve query had the highest ROR of the eleven (23.51",
     "The optic-nerve query had the highest ROR (23.51"),
    ("A term-level optic-nerve signal was also seen in JADER",
     "A term-level signal was also seen in JADER"),
    ("The non-specific comparison was possible in FAERS and, at term level, JADER, not Canada.",
     "The non-specific comparison was possible in FAERS and JADER, not Canada."),
    ("Ethambutol reports showed an optic-nerve-predominant pattern in FAERS and an "
     "optic-nerve-related signal in JADER and Canada Vigilance: a safety signal, not an incidence "
     "or causal effect.",
     "Ethambutol reports showed an optic-nerve-predominant pattern in FAERS and an "
     "optic-nerve-related signal in JADER and Canada Vigilance: a safety signal, not an incidence "
     "or causal effect."),
]
for old, new in pairs:
    assert old in text, f"abstract: not found {old[:50]!r}"
    text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
block = text[text.find("## Abstract"):text.find("**Keywords")]
print("abstract words:", len([w for w in re.sub(r"[#*]", " ", block).split() if re.search(r"\w", w)]))

# --------------------------------------------------------------- discussion
p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
old = ("the elevation of the ocular infections query is the clearest example, and it is best "
       "explained by ocular tuberculosis itself rather than by the drug.")
new = ("the elevation of the ocular infections query is the clearest example: it may partly reflect "
       "confounding by indication and channelling, including the underlying ocular infection, "
       "rather than a direct drug effect.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("discussion: ocular-infections explanation softened")

# ----------------------------------------------------------------- reference
p = MAN / "TADS_references.md"
refs = p.read_text(encoding="utf-8").rstrip().splitlines()
if not any(line.startswith("19. ") for line in refs):
    refs.append(
        "19. Cheng HC, Wong YH, Wang AG, Chen SW, Yang YL, Juan HC, et al. Müller glia-mediated "
        "protection of retinal ganglion cells from ethambutol-induced neurotoxicity through "
        "brain-derived neurotrophic factor. Cell Commun Signal. 2025;23(1):474. "
        "doi:10.1186/s12964-025-02478-4.")
p.write_text("\n".join(refs) + "\n", encoding="utf-8")
print("reference 19 added")
