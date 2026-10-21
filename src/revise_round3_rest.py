# -*- coding: utf-8 -*-
"""Remaining edits from the third round: methods 2.7 and 2.8, discussion, statements."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

# ---------------------------------------------------------------- methods 2.7
p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")
old = ("Third, within the antitubercular class, the optic-nerve rate was compared between reports "
       "naming rifampicin, isoniazid and pyrazinamide with and without ethambutol, a contrast in "
       "which the background regimen is held constant by construction.")
new = ("Third, within the antitubercular class, the optic-nerve outcome was a composite defined for "
       "this comparison as a report containing at least one of four preferred terms — optic "
       "neuropathy, optic neuritis, optic atrophy or toxic optic neuropathy, matched in both "
       "spellings — and the proportion of reports carrying it was compared between reports naming "
       "rifampicin, isoniazid and pyrazinamide with and without ethambutol, a contrast in which the "
       "background regimen is held constant by construction. The ratio of those proportions is "
       "reported, not an incidence rate ratio, because the denominator is reports rather than "
       "treated patients; the composite was formed for this comparison and is not a pre-specified "
       "primary outcome.")
assert old in text
text = text.replace(old, new, 1)

# ---------------------------------------------------------------- methods 2.8
old = ("The same panel was run in JADER and in Canada Vigilance.")
new = ("The optic-nerve comparison was run in JADER and in Canada Vigilance, but the two systems do "
       "not supply the same endpoints: JADER provides MedDRA/J terms for the optic-nerve and the "
       "non-specific terms alike, whereas the Canadian extract carries an optic-nerve composite and "
       "a system-organ-class count but no term-level control panel.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("methods: 2.7 and 2.8 updated")

# ---------------------------------------------------------------- discussion
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
    assert old_s in text, f"not found: {old_s[:60]!r}"
    text = text.replace(old_s, new_s, 1)
p.write_text(text, encoding="utf-8")
print("discussion: four corrections applied")

# --------------------------------------------------------------- statements
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = ("are available at\nhttps://github.com/Bowen2485/ethambutol-ocular-toxicity under an MIT licence.")
new = ("are available at\nhttps://github.com/Bowen2485/ethambutol-ocular-toxicity/tree/"
       "v2.0-tads-2026-10-21 (release tag `v2.0-tads-2026-10-21`) under an MIT licence.")
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("statements: data availability links to the tag")
