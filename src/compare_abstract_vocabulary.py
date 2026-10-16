# -*- coding: utf-8 -*-
"""
Compare the wording of the manuscript's abstract with the four peer abstracts.

The purpose is not to copy phrasing but to see how far the manuscript currently reads like
the literature it is being submitted alongside.  A submission whose abstract shares almost
no vocabulary with the recent papers in its own journal reads as an outlier regardless of
its quality, and that is a fixable problem.

How the comparison is made
    Function words are removed and the remaining terms are compared.  Two measures are
    reported: the share of the manuscript's content words that also appear in at least one
    peer abstract, and the same in reverse.  Cosine similarity over term counts is given as
    a single number for orientation.  None of this detects a good abstract; it detects
    vocabulary that is idiosyncratic to this manuscript.
"""
from __future__ import annotations

import json
import math
import re
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIT = ROOT / "docs" / "literature_peers" / "text"
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")

STOP = set("""a an the and or but if then than that this these those of in on at to for from
by with without as is are was were be been being it its their there here which who whom whose
we our us they them he she his her not no nor so such can may might must shall should will
would could have has had do does did done also more most less least other others into over
under between among during after before while because however therefore thus both each any
all some only very well same different new used using use""".split())


def terms(s: str) -> collections.Counter:
    words = re.findall(r"[a-z][a-z\-]{2,}", s.lower())
    return collections.Counter(w for w in words if w not in STOP)


# ---- the manuscript abstract
a0 = EN.find("## Abstract")
a1 = EN.find("**Keywords", a0)
manuscript_abs = EN[a0:a1]
mt = terms(manuscript_abs)
print(f"  manuscript abstract: {len(manuscript_abs.split())} words, "
      f"{len(mt)} distinct content terms")

# ---- the peers
peers: dict[str, collections.Counter] = {}
meta = json.loads((ROOT / "docs" / "literature_peers" / "peer_summary.json")
                  .read_text(encoding="utf-8"))

for key in ("PMID42577260", "PLOSONE_2026_Leukotriene-EGPA", "ang", "PMID42379941"):
    p = LIT / f"{key}.xml"
    if p.exists():
        xml = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"<abstract\b.*?</abstract>", xml, re.S)
        if not m:
            continue
        body = re.sub(r"<[^>]+>", " ", m.group(0))
    else:
        p = LIT / f"{key}.txt"
        if not p.exists():
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        # the abstract precedes the Introduction heading
        cut = re.search(r"\bIntroduction\b", body)
        body = body[: cut.start()] if cut else body[:4000]
    peers[key] = terms(body)
    print(f"  {key:32s} {len(peers[key])} distinct content terms")

if not peers:
    raise SystemExit("no peer abstract could be read")

# ---- vocabulary overlap
peer_vocab = set().union(*(set(c) for c in peers.values()))
m_vocab = set(mt)
shared = m_vocab & peer_vocab
print()
print("=" * 96)
print("1. Vocabulary overlap with the peer abstracts")
print("=" * 96)
print(f"  manuscript terms also used by a peer : {len(shared)}/{len(m_vocab)} "
      f"({100*len(shared)/len(m_vocab):.0f}%)")
print(f"  peer terms also used by the manuscript: {len(shared)}/{len(peer_vocab)} "
      f"({100*len(shared)/len(peer_vocab):.0f}%)")

print()
print("  terms the manuscript uses that no peer uses (the most frequent first):")
unique = [(w, n) for w, n in mt.most_common() if w not in peer_vocab]
print(f"      {len(unique)} of {len(m_vocab)} terms")
for w, n in unique[:25]:
    print(f"          {w:26s} x{n}")

print()
print("  terms the peers use that the manuscript does not (top 20 by total count):")
pool = sum(peers.values(), collections.Counter())
missing = [(w, n) for w, n in pool.most_common() if w not in m_vocab]
for w, n in missing[:20]:
    print(f"          {w:26s} x{n}")

print()
print("=" * 96)
print("2. Cosine similarity, manuscript against each peer abstract")
print("=" * 96)


def cosine(a: collections.Counter, b: collections.Counter) -> float:
    keys = set(a) | set(b)
    num = sum(a[k] * b[k] for k in keys)
    da = math.sqrt(sum(a[k] ** 2 for k in keys))
    db = math.sqrt(sum(b[k] ** 2 for k in keys))
    return num / (da * db) if da and db else 0.0


for key, c in peers.items():
    sim = cosine(mt, c)
    topic = meta.get(key, {}).get("topic", "")
    print(f"  {key:32s} {sim:.3f}   {topic}")

print()
print("=" * 96)
print("3. What the peers' abstracts lead with")
print("=" * 96)
for key in peers:
    if key in meta:
        print(f"  {key:32s} {meta[key].get('topic','')}")

print()
print("  Read the overlap figures as orientation, not as a score.  A high share means the")
print("  manuscript speaks the vocabulary of its target literature; a low share means a")
print("  reader arriving from those papers will not recognise the framing, whatever the")
print("  quality of the work.")
