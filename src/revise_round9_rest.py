# -*- coding: utf-8 -*-
"""Remaining ninth-round edits: AC16 description, abstract wording, ocular-infections sentence."""
from __future__ import annotations

import re
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


# ------------------------------------------------------------------ methods
edit_joined(MAN / "TADS_methods.md", "TPEN-treated human cell line", [
    ("A public TPEN-treated human cell line (GSE318912) was used as an empirical zinc-chelation "
     "reference; the comparison is reported with the caveat that the two experiments used "
     "different cell types.",
     "A public TPEN-treated human cardiomyocyte line, AC16 (GSE318912), was used as an empirical "
     "zinc-chelation reference; it was analysed unpaired there against paired in GSE294687, and "
     "the difference in cell type and design bounds what the correlation can show."),
])
print("methods: AC16 described")

# ----------------------------------------------------------------- abstract
edit_joined(MAN / "TADS_EN.md", "**Results.** The optic-nerve query", [
    ("four lay above unity, three below, four null",
     "four showed positive signals, three were significantly below 1 and four had intervals "
     "spanning 1"),
    ("Median onset was 125 days against 33 for non-ocular events.",
     "Among reports with usable dates, median onset was 125 days for optic-nerve events against 33 "
     "for non-ocular events."),
    ("The optic-nerve query had the highest ROR of the eleven (23.51",
     "The optic-nerve query had the highest ROR (23.51"),
    ("A term-level optic-nerve signal was also seen in JADER",
     "A term-level signal was also seen in JADER"),
    ("The non-specific comparison was possible in FAERS and, at term level, JADER, not Canada.",
     "The non-specific comparison was possible in FAERS and JADER, not Canada."),
])
edit_joined(MAN / "TADS_EN.md", "**Background.** Ethambutol causes", [
    ("rather than reflecting a general increase in ocular reporting, has not been tested against "
     "MedDRA's queries.",
     "rather than a general increase in ocular reporting, is untested against MedDRA's queries."),
])
edit_joined(MAN / "TADS_EN.md", "**Design.** Retrospective disproportionality", [
    ("with replication in two systems and exploratory transcriptomics.",
     "with replication and exploratory transcriptomics."),
])
block = (MAN / "TADS_EN.md").read_text(encoding="utf-8")
block = block[block.find("## Abstract"):block.find("**Keywords")]
print("abstract words:", len([w for w in re.sub(r"[#*]", " ", block).split() if re.search(r"\w", w)]))

# -------------------------------------------------------------- discussion
edit_joined(MAN / "TADS_discussion.md", "the elevation of the ocular infections query", [
    ("the elevation of the ocular infections query is the clearest example, and it is best "
     "explained by ocular tuberculosis itself rather than by the drug.",
     "the elevation of the ocular infections query is the clearest example: it may partly reflect "
     "confounding by indication and channelling, including the underlying ocular infection, rather "
     "than a direct drug effect."),
])
print("discussion: ocular infections softened")
