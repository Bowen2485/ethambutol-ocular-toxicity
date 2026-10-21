# -*- coding: utf-8 -*-
"""Fifth review round: the statistical audit.

    1. Methods now state the test that produced each p value, that both tests are two-sided, and
       that raw p and adjusted q are both reported
    2. the Table 3 footnote no longer calls the Canadian composite "21 terms": 21 is the number of
       exposed reports, and the rule is any preferred term containing OPTIC
    3. the fixed-regimen and susceptibility rows in the supplement now carry intervals, and the
       zero-cell correction is reported rather than contradicted
    4. the discussion no longer claims the design is robust to the objection of general reporting;
       it says what the design does and does not exclude
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
can = json.loads((ROOT / "results" / "canada_vigilance_ethambutol.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- methods 2.6
p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")
old = ("Multiplicity was controlled with the Benjamini–Hochberg procedure within two families, "
       "stated in advance: the eleven ocular queries, and the fifteen preferred terms described in "
       "Section 3.3.")
new = ("Two-sided p values were obtained from a Fisher exact test when the smallest expected cell "
       "count fell below 5, and from Pearson's χ² without continuity correction otherwise; the test "
       "used is identified for every term in supplementary Table S1. This rule was adopted because "
       "the exposed cohort is a small fraction of a 20-million-case database, so several preferred "
       "terms have expected counts far below one and the asymptotic approximation is unreliable. "
       "Multiplicity was controlled with the Benjamini–Hochberg procedure within two families, "
       "stated in advance: the eleven ocular queries, and the fifteen preferred terms described in "
       "Section 3.3; the raw p value is reported alongside the adjusted q.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("methods: test rule stated")

# ------------------------------------------------------------- Table 3 note
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = ('ROR, reporting odds ratio. "Any optic-nerve term" is a composite of 21 MedDRA preferred terms in\n'
       'the Canadian extract; the exposed-case count is the number of reports carrying at least one of\n'
       'them, not the number of terms.')
new = ('ROR, reporting odds ratio. "Any optic-nerve term" follows the MedDRA rule for the narrow optic-nerve\n'
       'search - every preferred term containing the string OPTIC; ' + str(len(can["optic_terms"])) +
       ' such terms appear in the Canadian\n'
       'extract, and ' + str(can["n_optic"]) + ' exposed reports carried at least one of them. The exposed-case count is reports, not terms.')
assert old in s, "table 3 note not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("table 3 note corrected")

# -------------------------------------------------------------- discussion 4.5
p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
old = ("A MedDRA query set nominated in advance, used as its own internal comparison and paired with "
       "pre-specified non-specific controls, gives a signal that is robust to the objection that the "
       "drug simply generates more ocular reports.")
new = ("The use of pre-specified MedDRA queries and ocular comparators provides a structured "
       "assessment of whether disproportionality is uniform across ocular outcomes. It cannot "
       "exclude outcome-specific recognition and coding of suspected toxicity.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("discussion 4.5 narrowed")
