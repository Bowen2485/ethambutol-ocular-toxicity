# -*- coding: utf-8 -*-
"""
Read the optic-nerve vocabulary out of JADER instead of guessing it.

The first dump of "ocular" terms used too loose a character set: 膜 appears in 腹膜炎
(peritonitis) and 球 in 好中球 (neutrophils), so the list was dominated by haematology
and oncology terms and the optic-nerve entries were buried.

This searches on 視神経 (optic nerve), which cannot appear in a non-ocular term, and on
視力 and 視野, and reports every distinct MedDRA/J preferred term containing them with
its frequency.  The Japanese spelling of each needed term can then be read off and
matched to the English terms the FAERS analysis uses.
"""
from __future__ import annotations

import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JADER = ROOT / "data" / "raw" / "jader"
ENC = "shift_jis"

NEEDLES = {
    "視神経": "optic nerve",
    "視力": "visual acuity",
    "視野": "visual field",
    "色覚": "colour vision",
    "複視": "diplopia",
    "白内障": "cataract",
    "緑内障": "glaucoma",
    "ドライアイ": "dry eye",
    "眼痛": "eye pain",
}

cnt = {k: collections.Counter() for k in NEEDLES}
cases_with = {k: set() for k in NEEDLES}
n = 0
with (JADER / "reac202609.csv").open(encoding=ENC, errors="replace", newline="") as fh:
    rd = csv.reader(fh)
    next(rd)
    for row in rd:
        n += 1
        if len(row) < 4:
            continue
        term = row[3].strip()
        if not term:
            continue
        for key in NEEDLES:
            if key in term:
                cnt[key][term] += 1
                cases_with[key].add(row[0].strip())

print(f"reaction rows: {n:,}")
print()
for key, gloss in NEEDLES.items():
    print("=" * 96)
    print(f"{key}  ({gloss})   {len(cnt[key])} distinct terms, "
          f"{len(cases_with[key]):,} cases")
    print("=" * 96)
    if not cnt[key]:
        print("    none")
    for term, c in cnt[key].most_common(30):
        print(f"    {c:>7,}  {term}")
    print()

print("=" * 96)
print("Overlap between the optic-nerve case sets")
print("=" * 96)
sets = {k: cases_with[k] for k in ("視神経", "視力", "視野", "色覚")}
for a in sets:
    for b in sets:
        if a < b:
            print(f"  {a} ∩ {b}: {len(sets[a] & sets[b]):,}")
