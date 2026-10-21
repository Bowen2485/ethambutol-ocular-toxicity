# -*- coding: utf-8 -*-
"""Seventh review round.

    1. Discussion 4.2 no longer says the internal contrast replicates in all three systems, and the
       abstract and conclusion are tightened to match Results 3.5
    2. Methods remove the isoniazid-only strata sentence, which no table reports
    3. the fixed-regimen interval and the transcriptomic test are specified
    4. a pre-specification caveat separates "fixed before the analyses" from "prospectively
       registered"
    5. the READUS-PV checklist is brought into line with the final Methods
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

# ---------------------------------------------------------------- discussion
p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
old = ("That contrast is what replicates across the three systems, and it is less consistent with a "
       "uniform increase across all ocular reporting than a single organ-system count would be. It "
       "does not remove differential recognition and coding of suspected toxicity, which remains "
       "the main alternative explanation for the pattern.")
new = ("The optic-nerve-related reporting signal was observed in all three systems, but the evidence "
       "was not equivalent across databases. FAERS provided the primary comparison across eleven "
       "ocular queries and the pre-specified term-level controls, while JADER provided term-level "
       "external support for the mapped terms. Canada Vigilance showed a directionally consistent "
       "signal using a broader, study-specific string-matched composite, rather than an equivalent "
       "replication of the primary query or of its internal-control pattern. The contrast is less "
       "consistent with a uniform increase across all ocular reporting than a single organ-system "
       "count would be, but it does not remove differential recognition and coding of suspected "
       "toxicity, which remains the main alternative explanation for the pattern.")
assert old in text
text = text.replace(old, new, 1)

old = ("Across three spontaneous-reporting systems, ethambutol showed a reproducible "
       "optic-nerve-predominant adverse-event reporting pattern.")
new = ("Across three spontaneous-reporting systems, ethambutol reports showed an "
       "optic-nerve-predominant pattern in FAERS and an optic-nerve-related signal in JADER and "
       "Canada Vigilance; the internal-control comparison was available in FAERS and, at term "
       "level, in JADER.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("discussion: 4.2 and 4.6 tightened")

# ------------------------------------------------------------------ abstract
p = MAN / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
old = ("Across three reporting systems, ethambutol showed a reproducible optic-nerve-predominant "
       "reporting pattern: a safety signal, not the incidence or causal effect of the drug.")
new = ("Ethambutol reports showed an optic-nerve-predominant pattern in FAERS and an "
       "optic-nerve-related signal in JADER and Canada Vigilance: a safety signal, not the "
       "incidence or causal effect of the drug.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
block = text[text.find("## Abstract"):text.find("**Keywords")]
print("abstract words:", len([w for w in re.sub(r"[#*]", " ", block).split() if re.search(r"\w", w)]))

# ------------------------------------------------------------------- methods
p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")

# 2.7: drop the unreported strata sentence
old = (" Strata in which the groups differ in disease state — in particular isoniazid-only reports, "
       "largely latent-infection prophylaxis — are reported but not used as evidence.")
assert old in text
text = text.replace(old, "", 1)

# 2.7: name the interval method
old = ("The ratio of those proportions is reported, not an incidence rate ratio, because the "
       "denominator is reports rather than treated patients;")
new = ("The ratio of those proportions, with a 95% confidence interval from the Katz log method "
       "(standard error computed from the four cell counts), is reported rather than an incidence "
       "rate ratio, because the denominator is reports rather than treated patients;")
assert old in text
text = text.replace(old, new, 1)

# 2.10: specify the transcriptomic test
old = ("The series was reanalysed with a paired test on log2 counts per million, and genes were "
       "called differentially expressed at a Benjamini–Hochberg q below 0.05.")
new = ("Counts were converted to counts per million from the column sums and log2-transformed after "
       "adding one; genes with CPM ≥ 1 in at least four samples were retained. Each gene was tested "
       "with a paired t-test across the four ethambutol–vehicle pairs, and Benjamini–Hochberg "
       "adjustment was applied across every gene tested; genes were called differentially expressed "
       "at q < 0.05.")
assert old in text
text = text.replace(old, new, 1)

# 2.5: pre-specification caveat
old = ("The eleven queries are Optic nerve disorders, Retinal disorders, Glaucoma, Lens disorders, "
       "Lacrimal disorders, Corneal disorders, Conjunctival disorders, Scleral disorders, "
       "Periorbital and eyelid disorders, Ocular infections and Ocular motility disorders.")
new = ("The eleven queries are Optic nerve disorders, Retinal disorders, Glaucoma, Lens disorders, "
       "Lacrimal disorders, Corneal disorders, Conjunctival disorders, Scleral disorders, "
       "Periorbital and eyelid disorders, Ocular infections and Ocular motility disorders. The "
       "query set and the control terms were fixed before the disproportionality analyses were run, "
       "but the analysis was not prospectively registered and those selections were made after the "
       "database data were available.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("methods: strata sentence removed, interval and DE test specified, pre-specification caveat")
