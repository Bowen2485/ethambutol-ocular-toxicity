# -*- coding: utf-8 -*-
"""Second pass at the 6,000-word limit, plus one factual fix.

Results 3.7 still called GSE318912 "a TPEN-treated human cell line" after Methods had been
corrected to the AC16 cardiomyocyte line; it now matches.  Edits are applied per paragraph,
located by the sentence being replaced rather than by a section marker.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

PAIRS: list[tuple[Path, str, str]] = [
    (MAN / "TADS_results.md",
     "The NRF2 antioxidant programme was the strongest: NFE2L2 itself rose 1.02 log2 and its "
     "targets — HMOX1 (+0.98), GCLM (+0.95), TXNRD1, SRXN1, NQO1, SQSTM1 and FTH1 — moved with it, "
     "seven of the ten genes significantly, for a mean of +1.045.",
     "The NRF2 antioxidant programme was the strongest: NFE2L2 rose 1.02 log2 and its targets "
     "(HMOX1 +0.98, GCLM +0.95, with TXNRD1, SRXN1, NQO1, SQSTM1 and FTH1) moved with it, seven of "
     "the ten significantly, mean +1.045."),
    (MAN / "TADS_results.md",
     "The zinc-chelation account was tested against an empirical reference, a TPEN-treated human "
     "cell line (GSE318912):",
     "The zinc-chelation account was tested against an empirical reference, the TPEN-treated AC16 "
     "cardiomyocyte line (GSE318912):"),
    (MAN / "TADS_results.md",
     "and the two fold-change vectors correlated at r = +0.07 across the 12,201 genes both "
     "experiments measured. The two experiments used different cell types, so that correlation "
     "bounds rather than settles the comparison.",
     "and the two fold-change vectors correlated at r = +0.07 across the 12,201 genes both "
     "measured; different cell types and an unpaired design bound what that correlation shows."),
    (MAN / "TADS_results.md",
     "None of this establishes a mechanism in patients. The predictions were assembled from the "
     "literature rather than fixed before our own data were examined, there is no protein "
     "measurement, no genotype and no microglial or Müller glial compartment in the preparation, "
     "and the concentration is far above therapeutic exposure.",
     "None of this establishes a mechanism in patients: the predictions were assembled from the "
     "literature after our data were examined, there is no protein measurement, no genotype and no "
     "glial compartment, and the concentration is far above therapeutic exposure."),
    (MAN / "TADS_results.md",
     "What it does show is that selected transcriptional predictions of the ferroptosis account "
     "were not reproduced under these conditions, which is a weaker statement than a refutation "
     "and is reported as such.",
     "What it shows is that selected ferroptosis predictions were not reproduced here, which is "
     "weaker than a refutation and is reported as such."),
    (MAN / "TADS_discussion.md",
     "For regulators and for those who build pharmacovigilance workflows, the transferable point "
     "is methodological. The use of pre-specified MedDRA queries and ocular comparators provides a "
     "structured assessment of whether disproportionality is uniform across ocular outcomes. It "
     "cannot exclude outcome-specific recognition and coding of suspected toxicity. The same "
     "design can be applied to other drugs with a suspected site-specific toxicity, and it "
     "requires no data beyond what spontaneous reporting systems already publish.",
     "For regulators and those who build pharmacovigilance workflows, the transferable point is "
     "methodological: pre-specified MedDRA queries and ocular comparators give a structured "
     "assessment of whether disproportionality is uniform across ocular outcomes, without "
     "excluding outcome-specific recognition and coding. The design applies to any drug with a "
     "suspected site-specific toxicity and needs no data beyond what reporting systems publish."),
]

for path, old, new in PAIRS:
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    hits = [i for i, b in enumerate(blocks) if old in b]
    assert len(hits) == 1, f"{path.name}: {old[:50]!r} matched {len(hits)} blocks"
    blocks[hits[0]] = blocks[hits[0]].replace(old, new, 1)
    path.write_text("\n\n".join(blocks), encoding="utf-8")
print(f"applied {len(PAIRS)} replacements")
