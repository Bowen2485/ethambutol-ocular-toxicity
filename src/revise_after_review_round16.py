# -*- coding: utf-8 -*-
"""Sixteenth round: compress to about 5,750 words by removing repeated caveats.

The discussion states "a reporting pattern is not a risk estimate" in several places.  Four of
those restatements go; the bias explanations, the case counts, the statistical definitions and the
limitations all stay.  The Plain Language Summary ending is also rewritten so that it asks for
vigilance and existing monitoring guidance rather than implying a validated follow-up window.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

PAIRS = [
    # 4.2: the caveat is made in full in 4.3
    (MAN / "TADS_discussion.md",
     " That contrast is less consistent with a uniform increase across all ocular reporting, but it "
     "does not remove differential recognition and coding, which remains the main alternative "
     "explanation.",
     ""),
    # 4.3: restatement of the same caveat
    (MAN / "TADS_discussion.md",
     " The absence of comparable elevations for the negative-control terms is less consistent with "
     "a uniform increase in ocular reporting.",
     ""),
    # 4.3: the point is already made by the paragraph opening
    (MAN / "TADS_discussion.md",
     " The result is a statement about the shape of the reporting signal, not a toxicity profile.",
     ""),
    # 4.3: merged into the sentence that follows it
    (MAN / "TADS_discussion.md",
     " The comparison narrows the range of explanations; it does not eliminate outcome-specific "
     "reporting. Differential coding is the more serious concern:",
     " The comparison narrows the range of explanations but does not eliminate outcome-specific "
     "reporting: differential coding is the more serious concern,"),
    # 3.2: restates the table and 4.1
    (MAN / "TADS_results.md",
     " The queries covering the ocular surface and anterior segment therefore showed no excess, "
     "while the query covering the optic nerve showed the largest one.",
     ""),
    # 4.5: shorter framing of the same idea
    (MAN / "TADS_discussion.md",
     "The practical value of a reporting signal of this shape is that it identifies where to look, "
     "and it should be read as a reason for clinical vigilance rather than as a basis for a "
     "screening schedule.",
     "A signal of this shape identifies where to look; it is a reason for vigilance, not a basis "
     "for a screening schedule."),
    # 4.2: one clause instead of two
    (MAN / "TADS_discussion.md",
     "in either design, a drug that produces a specific optic-nerve injury and a drug that produces "
     "a general increase in ocular reporting look alike",
     "in either design a specific optic-nerve injury and a general increase in ocular reporting "
     "look alike"),
    # 3.7: the flux caveat is kept, the wording shortened
    (MAN / "TADS_results.md",
     "(SQSTM1 +1.42, MAP1LC3B +1.03; mean +0.797), a pattern compatible with an altered "
     "autophagy-associated response, although transcript levels do not establish autophagic flux, "
     "and the respiratory-chain subunits fell",
     "(SQSTM1 +1.42, MAP1LC3B +1.03; mean +0.797), compatible with an altered "
     "autophagy-associated response without establishing flux, and the respiratory-chain subunits "
     "fell"),
]

for path, old, new in PAIRS:
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    hits = [i for i, b in enumerate(blocks) if old in b]
    assert len(hits) == 1, f"{path.name}: {old[:50]!r} matched {len(hits)}"
    blocks[hits[0]] = blocks[hits[0]].replace(old, new, 1)
    path.write_text("\n\n".join(blocks), encoding="utf-8")
print(f"applied {len(PAIRS)} cuts")

# ------------------------------------------------------- Plain Language Summary
e = MAN / "TADS_EN.md"
text = e.read_text(encoding="utf-8")
old = ("That pattern supports watching vision carefully in people taking ethambutol, especially in "
       "the first months of treatment.")
new = ("What the pattern supports is vigilance rather than a timetable: clinicians should ask about "
       "and watch for visual symptoms in people taking ethambutol and follow existing clinical "
       "guidance on monitoring. This study did not test any particular follow-up interval, and the "
       "125-day median describes reports with complete dates, not the point at which damage usually "
       "begins.")
assert old in text, "PLS ending not found"
text = text.replace(old, new, 1)
e.write_text(text, encoding="utf-8")
print("Plain Language Summary ending rewritten")
