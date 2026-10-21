# -*- coding: utf-8 -*-
"""Second round of review fixes.

    2. the 57-case gap in the period split is stated, with the mechanism found in the data
    3. the fixed-regimen contrast is written into main_results.json, so the sentence that all
       secondary analyses derive from that file is true
    4. Figure 3, its legend and the Table 4 title separate negative controls from non-specific
       comparators
    5. the clinical-monitoring paragraph is narrowed to vigilance rather than a screening
       schedule, and the Plain Language Summary matches the Canadian evidence
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"

cov = json.loads((RES / "audit_period_coverage.json").read_text(encoding="utf-8"))
reg = json.loads((RES / "audit_regimen.json").read_text(encoding="utf-8"))

# ------------------------------------------- 3. regimen into main_results.json
main = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
main["regimen"] = {
    "definition": ("optic-nerve event (optic neuropathy, optic neuritis, optic atrophy, toxic "
                   "optic neuropathy; both spellings) among reports naming rifampicin, isoniazid "
                   "and pyrazinamide, split by whether ethambutol is also named"),
    "with_ethambutol": reg["strata"]["rifampicin+isoniazid+pyrazinamide+ethambutol"],
    "without_ethambutol": reg["strata"]["rifampicin+isoniazid+pyrazinamide"],
    "rate_ratio": reg["rate_ratio"], "rate_ratio_lcl": reg["rate_ratio_lcl"],
    "rate_ratio_ucl": reg["rate_ratio_ucl"],
}
main["period_coverage"] = cov
(RES / "main_results.json").write_text(json.dumps(main, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
print("main_results.json: regimen and period coverage added")

# ------------------------------------------------------------------- results
p = MAN / "TADS_results.md"
text = p.read_text(encoding="utf-8")
old = ("This analysis is within one database and shares its reporting artefacts; it tests "
       "stability across reporting eras, not generalisability.")
new = (f"This analysis is within one database and shares its reporting artefacts; it tests "
       f"stability across reporting eras, not generalisability. The two periods cover "
       f"{cov['N'] - cov['outside_or_unparsed']:,} of the {cov['N']:,} de-duplicated cases: "
       f"{cov['outside_or_unparsed']} cases carry a receipt date before 2004 and fall outside both "
       f"periods, and {cov['span_both_periods']} cases have receipt records on "
       f"both sides of the 2016 boundary and therefore contribute to both (supplementary Table S7).")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("results: coverage sentence added")

# ------------------------------------------------------------------- methods
p = MAN / "TADS_methods.md"
text = p.read_text(encoding="utf-8")
old = ("the optic-nerve contrast was recomputed in each period with that period's own "
       "de-duplicated case count as the reference population; this tests stability across "
       "reporting eras, not generalisability.")
new = ("the optic-nerve contrast was recomputed in each period with that period's own "
       "de-duplicated case count as the reference population; this tests stability across "
       "reporting eras, not generalisability. Cases whose surviving report carries a receipt date "
       "before 2004 fall outside both periods, and a case with receipt records on both sides of "
       "the boundary contributes to both; the numbers and the year distribution are given in "
       "supplementary Table S7.")
assert old in text
text = text.replace(old, new, 1)
old2 = ("The de-duplication map, the 2×2 tables, the query-level results and the preferred-term "
        "results are exported from a single results file (`results/main_results.json`), from "
        "which the tables in this paper are generated, so that no number is transcribed by hand.")
new2 = ("The de-duplication map, the 2×2 tables, the query-level results, the preferred-term "
        "results, the period split and the fixed-regimen contrast are all exported to a single "
        "results file (`results/main_results.json`), from which the tables in this paper are "
        "generated, so that no number is transcribed by hand.")
assert old2 in text
text = text.replace(old2, new2, 1)
p.write_text(text, encoding="utf-8")
print("methods: coverage and reproducibility wording updated")

# --------------------------------------------------------------- plain language
p = MAN / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
old = ("The same pattern appeared in databases from Japan and Canada.")
new = ("A similar optic-nerve signal appeared in databases from Japan and Canada, although the "
       "Canadian data do not allow the same term-by-term comparison of everyday eye complaints.")
assert old in text
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("plain language summary: Canadian evidence narrowed")

# ---------------------------------------------------------------- discussion
p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"The practical value of a reporting signal of this shape.*?examinations that were not performed\.", text, re.S)
assert old, "clinical paragraph not found"
new = ("The practical value of a reporting signal of this shape is that it identifies where to "
       "look, and it should be read as a reason for clinical vigilance rather than as a basis for "
       "a screening schedule. Ethambutol optic neuropathy is managed by stopping the drug, and the "
       "damage becomes irreversible once atrophy is established, so detection before that point is "
       "what matters. In these data the reported time to onset had a median of 125 days, with "
       "11.0% of optic-nerve events reported within 30 days of starting treatment and 23.2% within "
       "60 days. That distribution describes reports with complete dates, not the incidence we "
       "would see in a monitored cohort: reports are a selected subset, the date of onset is "
       "recorded retrospectively, and no examinations that were not performed can appear in it. "
       "It is therefore consistent with a baseline examination and an early first follow-up, and "
       "with the clinical literature in which structural measures predict visual outcome better "
       "than initial acuity [10,11,12,13], but it cannot set the interval, and we do not derive "
       "one from it.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")
print("discussion: clinical paragraph narrowed")

# ------------------------------------------------------------- figure labelling
p = ROOT / "src" / "make_figures_tads.py"
s = p.read_text(encoding="utf-8")
old = ('    rows += [(r["term"].capitalize() + " (control)", r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"])\n'
       '             for r in ctl]')
new = ('    negative = {"Cataract", "Dry eye", "Glaucoma", "Conjunctivitis"}\n'
       '    rows += [(r["term"].capitalize()\n'
       '              + (" (negative control)" if r["term"] in negative else " (non-specific comparator)"),\n'
       '              r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"]) for r in ctl]')
assert old in s, "figure rows code not found"
s = s.replace(old, new, 1)
s = s.replace('"Preferred terms: optic-nerve query (top) and pre-specified controls (bottom)"',
              '"Preferred terms within the optic-nerve query (top), pre-specified negative controls '
              'and non-specific comparators (bottom)"')
p.write_text(s, encoding="utf-8")
print("figure 3: control groups separated")

# --------------------------------------------------------------- table 4 title
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = ("Table 4. Non-specific ocular terms in FAERS (pre-specified controls).")
new = ("Table 4. Pre-specified negative controls (cataract, dry eye, glaucoma, conjunctivitis) and "
       "non-specific comparators (eye pain, vision blurred) in FAERS.")
assert old in s
s = s.replace(old, new, 1)
old_fig3 = ("**Figure 3.** Preferred terms inside the optic-nerve query (upper panel) and the "
            "pre-specified non-specific control terms (lower panel).")
new_fig3 = ("**Figure 3.** Preferred terms within the optic-nerve query, alongside the pre-specified "
            "negative controls and the non-specific ocular comparators.")
assert old_fig3 in s
s = s.replace(old_fig3, new_fig3, 1)
p.write_text(s, encoding="utf-8")
print("table 4 and figure 3 legend relabelled")
