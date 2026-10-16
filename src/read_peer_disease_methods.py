# -*- coding: utf-8 -*-
"""
Read what the comparator papers actually did with their disease-target data.

Why this should have come first
    Several rounds have been spent inventing a way to analyse the GeneCards and DisGeNET
    disease annotations - binary presence, then the proportion of ocular entries, then the rank
    of the first one - and each attempt failed for a different reason.  The papers in this
    genre have already settled on a method, and the method they use is visible in their
    methods sections.  Reading it costs one pass over four files and would have saved the
    preceding work.

What is extracted
    The sentences that describe how disease targets were collected and, more importantly, what
    was done with them: whether a count was reported, whether an overlap with drug targets was
    taken, whether any statistical test was applied, and what the resulting number was used
    for.  The last point matters most, because it determines whether the disease list is
    evidence or merely an input to the network.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIT = ROOT / "docs" / "literature_peers" / "text"

#: the phrases that mark a statement about how disease targets were handled
KEYS = [
    r"disease[- ]associated genes",
    r"disease targets",
    r"targets were (?:retrieved|collected|obtained|identified)",
    r"overlap",
    r"Venn",
    r"intersect",
    r"common targets",
    r"shared targets",
    r"were considered",
    r"were retained",
    r"relevance score",
    r"GeneCards",
    r"DisGeNET",
    r"OMIM",
    r"CTD",
]

for key in ("ang", "PMID42379941", "PLOSONE_2026_Leukotriene-EGPA", "PMID42577260"):
    p = LIT / f"{key}.xml"
    if p.exists():
        body = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
    else:
        p = LIT / f"{key}.txt"
        if not p.exists():
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"\s+", " ", body)

    print("=" * 104)
    print(f"{key}")
    print("=" * 104)

    #: collect the sentences that mention how disease targets were handled
    sentences = re.split(r"(?<=[.!?])\s+", body)
    hits = []
    for s in sentences:
        if any(re.search(k, s, re.I) for k in KEYS) and len(s) < 700:
            hits.append(s.strip())
    seen = set()
    for s in hits:
        k = s[:70]
        if k in seen:
            continue
        seen.add(k)
        print(f"  {s}")
        print()
    print()
