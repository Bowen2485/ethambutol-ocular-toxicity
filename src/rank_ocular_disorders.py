# -*- coding: utf-8 -*-
"""
Test whether the rank of the first ocular disorder separates the genes, where a binary
"has an eye disorder" cannot.

Why a new measure is needed
    The binary measure is confounded by table length.  GeneCards' unified table runs to 7
    entries for HIF1A and 49 for OPA1; its inferred table to 30 for SLC7A11 and 237 for HIF1A.
    A gene with a longer table has more chances to contain an ocular entry, so counting "has
    an eye disorder" across genes read from different tables, or even from the same table with
    different lengths, measures the table rather than the biology.

    Rank is not confounded in the same way.  Everything read here was read in the order
    GeneCards returns, which is by relevance - the entries marked with stars and high counts
    come first - so "at what position does the first ocular disorder appear" is comparable
    across genes whose tables differ in length.  A gene whose table opens with an ocular
    disorder or repeats them early is a different proposition from one where a single ocular
    entry appears at position 57 of 67.

What is computed
    For every gene and table where the reading records the position of each ocular entry, the
    rank of the first one and how many appear in the first ten.  Genes are then grouped by
    whether their reading came from the unified or the inferred table, because the two are not
    comparable with each other even on this measure.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINGS = ROOT / "results" / "genecards_readings.json"
d = json.loads(READINGS.read_text(encoding="utf-8"))
data = d["data"]

#: rank of the first ocular disorder, as seen in the screenshots and exports.  None where the
#: reading showed no ocular disorder within the table as it was seen.  A rank of 1 means the
#: table opens with an eye disease.
FIRST_RANK = {
    # unified-table readings
    "OPA1": 1, "FTH1": 2, "FTL": 1, "MFN2": 1, "SLC25A4": 2, "DNM1L": 2,
    "SDHB": 11, "TP53": 3, "SOD2": 1, "HMOX1": None, "NFE2L2": None, "AKT1": None,
    "BCL2": None, "BAX": None, "CASP3": None, "TNF": None, "IL6": None,
    "STAT3": None, "KEAP1": None, "CYCS": 6, "HIF1A": None, "PPARGC1A": None,
    "CAT": None, "GPX1": None, "SLC7A11": 25, "GPX4": None, "ACSL4": None,
    # inferred-table readings
    "TXN": 2, "NQO1": 9, "VDAC1": 17, "APAF1": 33, "BCL2L1": 1,
}
#: how many ocular entries appear in the first ten rows of the table as seen
IN_FIRST_TEN = {
    "OPA1": 9, "FTH1": 8, "FTL": 6, "MFN2": 5, "SLC25A4": 4, "DNM1L": 5,
    "SDHB": 1, "TP53": 3, "SOD2": 1, "HMOX1": 0, "NFE2L2": 0, "AKT1": 0,
    "BCL2": 0, "BAX": 0, "CASP3": 0, "TNF": 0, "IL6": 0, "STAT3": 0,
    "KEAP1": 0, "CYCS": 1, "HIF1A": 0, "PPARGC1A": 0, "CAT": 0, "GPX1": 0,
    "SLC7A11": 0, "GPX4": 0, "ACSL4": 0,
    "TXN": 3, "NQO1": 2, "VDAC1": 1, "APAF1": 0, "BCL2L1": 1,
}

ARMS = {
    "OPA1": "mito", "MFN2": "mito", "SLC25A4": "mito", "DNM1L": "mito",
    "SDHB": "mito", "VDAC1": "mito", "CYCS": "mito", "APAF1": "mito",
    "FTH1": "iron", "FTL": "iron",
    "TP53": "oxredox", "SOD2": "oxredox", "SLC7A11": "oxredox", "GPX1": "oxredox",
    "CAT": "oxredox", "TXN": "oxredox", "NQO1": "oxredox",
    "GPX4": "ferroptosis", "ACSL4": "ferroptosis",
    "TNF": "inflam", "IL6": "inflam", "STAT3": "inflam", "NFE2L2": "inflam",
    "HMOX1": "inflam", "KEAP1": "inflam", "MAPK1": "inflam", "AKT1": "inflam",
    "BCL2": "inflam", "BAX": "inflam", "CASP3": "inflam", "BCL2L1": "inflam",
    "HIF1A": "hypoxia", "PPARGC1A": "hypoxia",
}

print("=" * 96)
print("All genes read, ordered by the rank of their first ocular disorder")
print("=" * 96)
rows = []
for g, d_ in data.items():
    if g not in FIRST_RANK:
        continue
    rows.append((FIRST_RANK[g], g, ARMS.get(g, "?"), d_.get("table", "unified"),
                 IN_FIRST_TEN.get(g, 0), d_.get("n_disorders", 0),
                 d_.get("n_inferred", 0)))

ranked = [r for r in rows if r[0] is not None]
none = [r for r in rows if r[0] is None]
ranked.sort(key=lambda r: r[0])

print(f"  {'rank':>5s} {'gene':10s} {'arm':11s} {'table':9s} {'ocular in first 10':>19s}")
for rank, g, arm, tbl, top10, nu, ni in ranked:
    print(f"  {rank:>5d} {g:10s} {arm:11s} {tbl:9s} {top10:>19d}")
print()
print(f"  no ocular disorder seen in the table as read ({len(none)}):")
for _, g, arm, tbl, top10, nu, ni in sorted(none, key=lambda r: r[2]):
    print(f"        {g:10s} {arm:11s} {tbl:9s}  "
          f"({nu} unified, {ni} inferred entries)")

print()
print("=" * 96)
print("By arm, ranked by the first ocular disorder")
print("=" * 96)
arms = ["mito", "iron", "oxredox", "ferroptosis", "inflam", "hypoxia"]
for arm in arms:
    members = [(FIRST_RANK[g], g, IN_FIRST_TEN.get(g, 0), data[g].get("table", "unified"))
               for g in data if ARMS.get(g) == arm and g in FIRST_RANK]
    have = sorted([m for m in members if m[0] is not None])
    dont = [m[1] for m in members if m[0] is None]
    ranks = [m[0] for m in have]
    med = sorted(ranks)[len(ranks) // 2] if ranks else "-"
    print(f"  {arm:12s} n={len(members):>2d}  ocular present {len(have):>2d}  "
          f"best rank {min(ranks) if ranks else '-':>4}  median rank {str(med):>4}  "
          f"none: {', '.join(dont) if dont else '-'}")

print()
print("=" * 96)
print("Reading")
print("=" * 96)
print("""  The measure does separate.  Genes whose first ocular disorder is at rank 1 to 3 -
  OPA1, FTL, MFN2, SOD2, FTH1, SLC25A4, DNM1L, TP53, TXN - are genes for which an eye disease
  is among the most relevant associations in the database.  Genes at rank 9 and beyond, or
  with no ocular entry in the table as read, are not.

  The assignment to an arm does not track that ranking: the top group contains mitochondrial,
  iron and oxidative-stress genes alike, and the bottom contains inflammatory and ferroptosis
  genes alongside mitochondrial ones such as APAF1 and CYCS.

  So the fair version of the earlier claim is about individual nodes, not arms, and it can be
  stated with a number attached to each: the rank at which eye disease first appears.""")
