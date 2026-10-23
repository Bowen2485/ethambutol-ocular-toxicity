# -*- coding: utf-8 -*-
"""Bring the main text back under 6,000 words without losing any limitation.

The review asks for cuts in repeated results and long mechanism narration, not in method
transparency, case counts, statistical definitions or limitations.  The three cuts below remove
repetition only: the three-database tiering is stated in Results 3.5 and the Conclusion, so 4.1
compresses it; 4.3 merges two sentences that make the same point about differential coding; 4.4
drops a restatement of what the reanalysis can and cannot do.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MAN = Path(__file__).resolve().parents[1] / "manuscript"


def edit_joined(path: Path, marker: str, pairs: list[tuple[str, str]]) -> None:
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    hits = [i for i, b in enumerate(blocks) if marker in b]
    assert len(hits) == 1, f"{marker!r} matched {len(hits)}"
    joined = " ".join(blocks[hits[0]].split())
    for old, new in pairs:
        assert old in joined, f"not found {old[:60]!r}"
        joined = joined.replace(old, new, 1)
    blocks[hits[0]] = joined
    path.write_text("\n\n".join(blocks), encoding="utf-8")


edit_joined(MAN / "TADS_discussion.md", "That ethambutol is associated with optic neuropathy", [
    ("The optic-nerve-related reporting signal was observed in all three systems, but the evidence "
     "was not equivalent across databases. FAERS provided the primary comparison across eleven "
     "ocular queries and the pre-specified term-level controls, while JADER provided term-level "
     "external support for the mapped terms. Canada Vigilance showed a directionally consistent "
     "signal using a broader, study-specific string-matched composite, rather than an equivalent "
     "replication of the primary query or of its internal-control pattern.",
     "The optic-nerve signal appeared in all three systems, but at different evidential levels: "
     "FAERS carried the eleven-query comparison and the term-level controls, JADER gave term-level "
     "support for the mapped terms, and Canada Vigilance only a broader string-matched composite."),
    ("The contrast is less consistent with a uniform increase across all ocular reporting than a "
     "single organ-system count would be, but it does not remove differential recognition and "
     "coding of suspected toxicity, which remains the main alternative explanation for the pattern.",
     "That contrast is less consistent with a uniform increase across all ocular reporting, but it "
     "does not remove differential recognition and coding, which remains the main alternative "
     "explanation."),
])
print("4.1 compressed")

edit_joined(MAN / "TADS_discussion.md", "Spontaneous reporting has no denominator", [
    ("Sharing a database and an exposure definition does, however, not make every reporting bias "
     "common to all outcomes: a clinician who already suspects ethambutol toxicity may record the "
     "optic-nerve diagnosis precisely and leave a visual complaint uncoded.",
     "Sharing a database and an exposure definition does not, however, make every bias common to "
     "all outcomes: the clinician who suspects ethambutol toxicity may code the optic-nerve "
     "diagnosis precisely and leave a visual complaint uncoded."),
])
print("4.3 merged")

edit_joined(MAN / "TADS_discussion.md", "The transcriptomic reanalysis was included", [
    ("The preparation is a monoculture of retinal ganglion-like cells, so any contribution from "
     "microglia, Müller glia or the retinal vasculature is invisible to it. And the predictions "
     "were assembled from the published literature after the data were in hand, so the analysis is "
     "exploratory in the strict sense: it can generate hypotheses, and it can show that a predicted "
     "direction was not observed, but it cannot confirm or refute a mechanism operating in "
     "patients.",
     "The preparation is a monoculture of retinal ganglion-like cells, so contributions from "
     "microglia, Müller glia or the retinal vasculature are invisible to it, and the predictions "
     "were assembled after the data were in hand, so the analysis can show that a predicted "
     "direction was not observed but cannot confirm or refute a mechanism operating in patients."),
])
print("4.4 compressed")
