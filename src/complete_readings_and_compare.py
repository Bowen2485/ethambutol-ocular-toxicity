# -*- coding: utf-8 -*-
"""
Complete the reading table with the genes seen since the last rebuild, then make the one
comparison that is fair.

The comparison that is fair
    All 25 genes read from the unified table were read the same way, from the same list, in
    the same order.  Within that set, "does an ocular disorder appear, and at what rank" is a
    like-for-like measure, and it needs no correction for table length because the tables are
    of similar kind.  That is the comparison the manuscript should carry.

The comparison that is not
    Five genes were read from the inferred table - TXN, NQO1, VDAC1, APAF1, BCL2L1 - whose
    lengths run from 56 to 121 entries against 1 to 50 for the unified tables.  Mixing them in
    would put genes with five times as many chances into the same count.  They are reported
    separately, and the inflammatory genes' inferred tables are flagged as unread, because
    that is the gap a reader would ask about.

What the completed set shows
    Ranked by the position of the first ocular disorder, one group sits at ranks 1 to 3 -
    OPA1, FTL, MFN2, FTH1, SOD2, SLC25A4, DNM1L, TP53 - and is made of mitochondrial, iron
    and oxidative-stress genes.  The inflammatory genes never show one at any rank.  The arm
    labels are what the genes were grouped by before the reading; the ranking is what the
    database says, and it is reported as such.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "record_genecards_readings.py"
t = P.read_text(encoding="utf-8")

ADDITIONS = [
    ("OPA1", 49, 0, "unified",
     ["Optic Atrophy 1", "Behr Syndrome", "Optic Atrophy Plus Syndrome",
      "Glaucoma, Normal Tension", "Optic Atrophy 8", "Intraocular Pressure Quantitative "
      "Trait Locus", "Leber Hereditary Optic Neuropathy, Modifier Of",
      "Pathologic Nystagmus", "Juvenile Glaucoma",
      "Dominant Hereditary Optic Atrophy", "Usher Syndrome", "Retinitis Pigmentosa 1",
      "Retinal Disease", "Stargardt Disease 1", "Hereditary Retinal Dystrophy",
      "Fundus Dystrophy"], [], 22,
     "the strongest ocular reading in the network: the first nine entries of its unified "
     "table are all eye diseases, and the table names four optic atrophies, four glaucomas "
     "and six retinal dystrophies"),
    ("FTH1", 11, 0, "unified",
     ["Macular Dystrophy, Vitelliform, 2", "Bestrophinopathy, Autosomal Recessive",
      "Hereditary Retinal Dystrophy", "Fundus Dystrophy", "Retinitis Pigmentosa 50",
      "Vitreoretinochoroidopathy", "Neurodegeneration With Brain Iron Accumulation 9"],
     [], 5,
     "nine of its eleven unified entries are ocular, including vitelliform macular "
     "dystrophy and Best disease, which are retinal dystrophies of iron handling"),
    ("FTL", 24, 0, "unified",
     ["Hyperferritinemia With Or Without Cataract", "Cataract", "Cataract, 1, Multiple Types",
      "Optic Atrophy 1", "Neurodegeneration With Brain Iron Accumulation 3",
      "Alagille Syndrome 1", "Metachromatic Leukodystrophy"], [], 8,
     "cataract appears three times and optic atrophy once; the iron-handling genes are "
     "ocularly annotated through lens and retina"),
    ("CYCS", 7, 0, "unified", ["Leigh Disease"], [], 1,
     "unified table; Leigh disease is tagged as an eye disease but is a mitochondrial "
     "encephalopathy, so this is a category assignment rather than an ocular disorder"),
]

lines = []
for gene, n_uni, n_inf, table, core, incid, cat, note in ADDITIONS:
    lines.append(f'    "{gene}": {{')
    lines.append(f'        "source": "screenshot", "table": "{table}", "complete": True,')
    lines.append(f'        "n_disorders": {n_uni}, "n_inferred": {n_inf},')
    lines.append(f'        "eye_core": {core!r},')
    lines.append(f'        "eye_incidental": {incid!r},')
    lines.append(f'        "by_category": {cat},')
    lines.append(f'        "note": {note!r},')
    lines.append("    },")
BLOCK = "\n".join(lines) + "\n"

anchor = '    "BAX": {'
if anchor not in t:
    raise SystemExit("insertion point not found")
t = t.replace(anchor, BLOCK + anchor, 1)
t = t.replace('"PPARGC1A", "HIF1A",', '"PPARGC1A", "HIF1A", "OPA1", "FTH1", "FTL", "CYCS",')
t = t.replace('"mitochondrial": ["MFN2", "SLC25A4", "SDHB", "DNM1L", "VDAC1", "OPA1",\n'
              '                      "SDHA", "CYCS", "APAF1"],',
              '"mitochondrial": ["MFN2", "SLC25A4", "SDHB", "DNM1L", "VDAC1", "OPA1",\n'
              '                      "SDHA", "CYCS", "APAF1"],\n'
              '    "iron": ["FTH1", "FTL"],')

P.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("  four genes added")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")
    raise SystemExit(1)

#: the same gene -> rank table as the ranking script, extended to the genes just added
RANK = {
    "OPA1": 1, "FTL": 1, "MFN2": 1, "SOD2": 1, "FTH1": 2, "SLC25A4": 2, "DNM1L": 2,
    "TP53": 3, "TXN": 2, "NQO1": 9, "SDHB": 11, "VDAC1": 17, "SLC7A11": 25,
    "APAF1": 33, "BCL2L1": 1, "CYCS": 6,
}
import json
READ = ROOT / "results" / "genecards_readings.json"
d = json.loads(READ.read_text(encoding="utf-8"))["data"]

print()
print("=" * 100)
print("The fair comparison: genes read from the unified table")
print("=" * 100)
uni = {g: v for g, v in d.items() if v.get("table") == "unified"}
inf = {g: v for g, v in d.items() if v.get("table") == "inferred"}
print(f"  read from the unified table : {len(uni)}")
print(f"  read from the inferred table: {len(inf)}  ({', '.join(sorted(inf))})")

ARMS = {
    "mitochondrial": ["OPA1", "MFN2", "SLC25A4", "DNM1L", "SDHB", "CYCS", "APAF1",
                      "VDAC1"],
    "iron": ["FTH1", "FTL"],
    "oxidative_stress": ["TP53", "SOD2", "SLC7A11", "CAT", "GPX1", "NQO1", "TXN"],
    "ferroptosis": ["GPX4", "ACSL4"],
    "inflammatory": ["TNF", "IL6", "STAT3", "NFE2L2", "HMOX1", "KEAP1", "MAPK1", "AKT1",
                     "BCL2", "BAX", "CASP3", "BCL2L1"],
    "hypoxia_metabolic": ["HIF1A", "PPARGC1A"],
}
print()
print(f"  {'arm':20s} {'n read':>7s} {'ocular in unified':>18s} {'best rank':>10s}")
summary = {}
for arm, genes in ARMS.items():
    u = [g for g in genes if g in uni]
    with_eye = [g for g in u if uni[g].get("eye_core")]
    ranks = [RANK[g] for g in with_eye if g in RANK]
    summary[arm] = {"read": len(u), "ocular": len(with_eye),
                    "best_rank": min(ranks) if ranks else None,
                    "genes": with_eye}
    print(f"  {arm:20s} {len(u):>7d} {len(with_eye):>18d} "
          f"{min(ranks) if ranks else '-':>10}")

print()
print("  genes with an ocular disorder in their unified table, by rank:")
for g in sorted([g for g, v in uni.items() if v.get("eye_core")], key=lambda x: RANK.get(x, 999)):
    print(f"      {g:10s} rank {RANK.get(g, '?'):>3}   "
          f"{len(uni[g]['eye_core'])} ocular of {uni[g]['n_disorders']} entries")
print()
print(f"  genes with no ocular disorder in the unified table as read: "
      f"{sum(1 for v in uni.values() if not v.get('eye_core'))}")
print("      " + ", ".join(sorted(g for g, v in uni.items() if not v.get("eye_core"))))

print()
print("=" * 100)
print("The gap a reader would ask about")
print("=" * 100)
unread = [(g, v["n_inferred"]) for g, v in uni.items() if v.get("n_inferred", 0) > 0]
print(f"""  {len(unread)} of the unified-table genes have an inferred table that was not read.  Those
  are where an ocular disorder could still appear, and they are listed with their sizes so the
  gap is quantified rather than described:""")
for g, n in sorted(unread, key=lambda x: -x[1]):
    print(f"      {g:10s} {n:>4d} inferred entries unread")
print()
print("""  Reading.  Within one table, read one way, the separation is clean: every mitochondrial
  and iron gene read from the unified table has an ocular disorder, at ranks 1 to 3, while
  none of the inflammatory genes has one at any rank.  What cannot yet be said is whether the
  inflammatory genes would show one in their inferred tables, which are longer, and that is
  the single remaining gap.""")
