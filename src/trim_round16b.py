# -*- coding: utf-8 -*-
"""Second pass of the compression: another ~110 words, same rule.

Remaining cuts remove a repeated three-database summary, one duplicated clause about the 17-term
definition, and shorten two sentences in the transcriptomic paragraph without dropping any
limitation.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

PAIRS = [
    (MAN / "TADS_discussion.md",
     "The optic-nerve signal appeared in all three systems, but at different evidential levels: "
     "FAERS carried the eleven-query comparison and the term-level controls, JADER gave term-level "
     "support for the mapped terms, and Canada Vigilance only a broader string-matched composite.",
     "The optic-nerve signal appeared in all three systems, at different evidential levels."),
    (MAN / "TADS_discussion.md",
     " And the definition used here is the 17-term case-level one, not the 45-term query, so the "
     "medians describe that subset rather than the main analysis.",
     ""),
    (MAN / "TADS_discussion.md",
     "It also does not show that the negative-control events are not caused by the drug: a true "
     "effect that is small relative to background reporting would not appear.",
     "It also cannot exclude a true effect of the drug that is small relative to background "
     "reporting."),
    (MAN / "TADS_discussion.md",
     "Within the query the evidence rested on optic neuropathy and optic neuritis, the two terms "
     "with the largest numbers of exposed cases, rather than on the terms with the largest ratios.",
     "Within the query the evidence rested on optic neuropathy and optic neuritis, the terms with "
     "the largest numbers of exposed cases rather than the largest ratios."),
    (MAN / "TADS_results.md",
     "The ferroptosis account predicts SLC7A11 and GPX4 falling; their transcripts rose, SLC7A11 by "
     "3.80 log2, while the iron-handling genes TFRC (+2.00) and FTH1 (+0.31) rose as that account "
     "also predicts.",
     "The ferroptosis account predicts SLC7A11 and GPX4 falling; both rose, SLC7A11 by 3.80 log2, as "
     "did the iron-handling genes TFRC and FTH1, which that account also predicts."),
    (MAN / "TADS_results.md",
     "TPEN lowered metallothionein (mean −0.17) and raised the SLC39A importers (+0.33), whereas "
     "ethambutol raised metallothionein (+0.31) and left the importers unchanged (+0.04), and the "
     "two fold-change vectors correlated at r = +0.07 across the 12,201 genes both measured; "
     "different cell types and an unpaired design bound what that correlation shows.",
     "TPEN lowered metallothionein (−0.17) and raised the SLC39A importers (+0.33), whereas "
     "ethambutol raised metallothionein (+0.31) and left the importers unchanged (+0.04); the two "
     "fold-change vectors correlated at r = +0.07 across the 12,201 genes both measured, a "
     "correlation bounded by the different cell types and the unpaired design."),
    (MAN / "TADS_discussion.md",
     "Three limits are decisive for how it should be read.",
     "Three limits govern how it should be read."),
]

for path, old, new in PAIRS:
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    hits = [i for i, b in enumerate(blocks) if old in b]
    assert len(hits) == 1, f"{path.name}: {old[:50]!r} matched {len(hits)}"
    blocks[hits[0]] = blocks[hits[0]].replace(old, new, 1)
    path.write_text("\n\n".join(blocks), encoding="utf-8")
print(f"applied {len(PAIRS)} cuts")
