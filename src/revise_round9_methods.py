# -*- coding: utf-8 -*-
"""Ninth review round, applied block by block.

The manuscript sources are hard-wrapped, so replacements are made on the joined text of the
paragraph that contains a marker; only the changed paragraph is reflowed to a single line.
"""
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


# --------------------------------------------------------------- methods 2.10
edit_joined(MAN / "TADS_methods.md", "GSE294687 profiled human", [
    ("GSE294687 profiled human induced pluripotent stem cell-derived retinal ganglion-like cells "
     "exposed to ethambutol or vehicle in four paired preparations.",
     "Public series GSE294687, from the study by Cheng and colleagues [19], profiled human induced "
     "pluripotent stem cell-derived retinal ganglion-like cells exposed to ethambutol or vehicle in "
     "four paired preparations. The original study analysed these data with a count-based model; "
     "the reanalysis here uses a paired test on log-transformed counts per million, and is "
     "therefore an exploratory reanalysis with a different method rather than a reproduction of "
     "the original differential-expression results."),
])
print("methods 2.10: dataset citation and method difference")

print("checking the TPEN sentence:")
t = (MAN / "TADS_methods.md").read_text(encoding="utf-8")
i = t.find("TPEN")
print("  ", repr(t[max(0, i - 200):i + 320]))
