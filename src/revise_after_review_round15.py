# -*- coding: utf-8 -*-
"""Fifteenth round: the five methodological points in the review.

    1. say what the eleven-query comparison can and cannot support: terms overlap, background
       reporting differs, and an ordering of odds ratios is not a test of difference
    2. carry the exposure-identification limit into the limitations, with its two consequences
    3. keep the onset medians tied to their analysable subset, and say that missing dates are not
       random
    4. name the fixed-regimen analysis a within-class reporting contrast, not a cohort
    5. keep the transcriptomic verdict at "no consistent support" rather than "ferroptosis
       excluded"
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"


def edit_joined(path: Path, marker: str, pairs: list[tuple[str, str]]) -> None:
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    hits = [i for i, b in enumerate(blocks) if marker in b]
    assert len(hits) == 1, f"{path.name}: {marker!r} matched {len(hits)} blocks"
    joined = " ".join(blocks[hits[0]].split())
    for old, new in pairs:
        assert old in joined, f"{path.name}: not found {old[:60]!r}"
        joined = joined.replace(old, new, 1)
    blocks[hits[0]] = joined
    path.write_text("\n\n".join(blocks), encoding="utf-8")


# ---------------------------------------------- 1. what the comparison supports
edit_joined(MAN / "TADS_discussion.md", "The controls bound the conclusion", [
    ("The controls bound the conclusion in both directions.",
     "What the comparison supports is narrower than a ranking of ocular toxicity. The eleven "
     "queries are not independent: preferred terms belong to more than one of them, the background "
     "frequency of each condition differs in the underlying population, and the disease mix of the "
     "reports is not the same across queries. An ordering of odds ratios is therefore a description "
     "of the reporting signal, not a test that ethambutol affects one ocular structure more than "
     "another; no contrast between queries was tested. The controls bound the conclusion in both "
     "directions."),
])
print("4.3: comparison scope stated")

# ------------------------------------------------- 2. exposure identification
edit_joined(MAN / "TADS_discussion.md", "Ethambutol optic neuropathy is managed by stopping", [
    ("It is therefore consistent with a baseline examination and an early first follow-up, and "
     "with the clinical literature in which structural measures predict visual outcome better than "
     "initial acuity [10,11,12,13], but it cannot set the interval, and we do not derive one from "
     "it.",
     "It is therefore consistent with a baseline examination and an early first follow-up, and "
     "with the clinical literature in which structural measures predict visual outcome better than "
     "initial acuity [10,11,12,13], but it cannot set the interval, and we do not derive one from "
     "it. Two further limits apply to these dates. Reports with an incomplete date pair are "
     "excluded, and their exclusion is unlikely to be random: a report that records both the start "
     "of therapy and the date of the event is one where the timing mattered to the reporter, which "
     "probably enriches the subset for events the reporter had already connected to the drug. And "
     "the definition used here is the 17-term case-level one, not the 45-term query, so the medians "
     "describe that subset rather than the main analysis."),
])
print("4.5: onset subset limits stated")

# ------------------------------------------------------------ 3. limitations
edit_joined(MAN / "TADS_discussion.md", "Two designs would move the question forward", [
    ("Two designs would move the question forward, and neither can be built from spontaneous "
     "reports.",
     "Exposure identification carries its own limits. FAERS exposure rests on a single token in "
     "the drug-name fields, and brand and salt variants were not added to it, so a report naming "
     "only a brand product is missed; the three systems also identify exposure differently, from a "
     "drug-name substring, a suspect-drug code and an ingredient table. Two consequences follow: "
     "the ethambutol cohort is probably incomplete in a way that varies by system, and the "
     "cross-database results should be read as agreement in direction and pattern rather than as "
     "comparable odds ratios. Two designs would move the question forward, and neither can be built "
     "from spontaneous reports."),
])
print("4.6 area: exposure limits stated")

# ----------------------------------------------- 4. fixed-regimen naming
edit_joined(MAN / "TADS_discussion.md", "The fixed-regimen contrast", [
    ("The fixed-regimen contrast — rifampicin, isoniazid and pyrazinamide with versus without "
     "ethambutol — holds the background regimen constant but rests on a small unexposed group, and "
     "its interval includes unity; it is reported for completeness rather than as evidence of a "
     "within-class effect.",
     "The fixed-regimen analysis — rifampicin, isoniazid and pyrazinamide with versus without "
     "ethambutol — holds the background regimen constant but is a within-class reporting contrast, "
     "not a matched cohort: treatment duration, dose, disease severity and co-medication are not "
     "held constant, and the denominator is reports rather than treated patients. It rests on a "
     "small unexposed group and its interval includes unity, so it is reported for completeness "
     "rather than as evidence of a within-class effect."),
])
print("4.3: fixed-regimen named")

# ----------------------------------------------------- 5. ferroptosis verdict
edit_joined(MAN / "TADS_discussion.md", "the ferroptosis account", [
    ("so the appropriate conclusion is that selected transcriptional predictions were not "
     "reproduced under these conditions, not that ferroptosis has been excluded.",
     "so the appropriate conclusion is that the data provide no consistent transcriptional support "
     "for the ferroptosis prediction under these conditions; they do not exclude ferroptosis, and "
     "they cannot, because transcript levels are not a flux measurement."),
])
print("4.4: ferroptosis verdict reworded")
