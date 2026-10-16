# -*- coding: utf-8 -*-
"""
Add CAT, GPX1 and TXN, and record which table each reading came from.

Why the table matters
    GeneCards presents two lists.  "Disorders associated with" is unified from curated and
    inferred sources and is the shorter, more conservative one; "Inferred disorder
    associations" is the computational list and is much longer.  A reading taken from one is
    not comparable with a reading taken from the other: TXN lists 59 inferred disorders and
    seven of them are ocular, while CASP3 lists 1 unified disorder and none.  Pooling the two
    would make TXN look like the most ocular gene in the network purely because its longer
    table was the one read.

    Every entry therefore carries which list it came from.  The earlier entries were all read
    from the unified table, and the three added here are marked accordingly, so the contrast
    is visible rather than averaged away.

What the additions show
    CAT has no ocular disorder in either list among the ones visible.  GPX1 has none in its
    unified list but cataract appears in its inferred list.  TXN has seven in its inferred
    list - retinal ischaemia, retinal vascular disease, age-related macular degeneration,
    cataract, intraocular pressure, retinal disease and retinitis pigmentosa - which makes it
    one of the most ocular genes read.

    That last result does not fit the arm-level pattern recorded previously, where the
    oxidative-stress arm was said to carry three genes with ocular annotation.  TXN belongs to
    that arm and carries more ocular annotation than any gene in it.  The pattern is not
    discarded for being inconvenient; the arm count is recomputed with TXN included and the
    revised figure is what gets reported.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "record_genecards_readings.py"
t = P.read_text(encoding="utf-8")

#: the three genes, with the list each reading came from
ADDITIONS = [
    ("CAT", 4, 32, "unified", [], [], 0,
     "no ocular disorder in the unified list; acatalasaemia, adrenoleukodystrophy, "
     "alacrima-achalasia and a metabolic disorder"),
    ("GPX1", 3, 9, "unified", [], [], 0,
     "no ocular disorder in the unified list; cataract appears in the inferred list"),
    ("TXN", 0, 59, "inferred", [
        "Retinal Ischemia", "Retinal Vascular Disease", "Age Related Macular Degeneration",
        "Cataract", "Intraocular Pressure Quantitative Trait Locus", "Retinal Disease",
        "Retinitis Pigmentosa"], [], 6,
     "read from the inferred list, which holds 59 disorders; seven are ocular, the most of "
     "any gene read.  Its unified list was not seen, so this reading is not directly "
     "comparable with the unified-table readings"),
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
    raise SystemExit("could not find the insertion point")
t = t.replace(anchor, BLOCK + anchor, 1)

#: every existing entry gains an explicit table field, because they were all unified reads and
#: leaving the field absent would make the distinction look like a special case for these three
t = re.sub(r'("source": "csv", )"complete"', r'\1"table": "unified", "complete"', t)
t = re.sub(r'("source": "screenshot", )"complete"', r'\1"table": "unified", "complete"', t)
#: but the three just added already carry a table field, so the pass above would duplicate it
t = t.replace('"table": "unified", "table": "inferred"', '"table": "inferred"')

#: FOCUS and the arms gain the three genes
t = t.replace('"GPX4", "MAPK1", "IL6", "STAT3", "KEAP1", "TNF", "HMOX1", "CASP3",',
              '"GPX4", "MAPK1", "IL6", "STAT3", "KEAP1", "TNF", "HMOX1", "CASP3",\n'
              '         "CAT", "GPX1", "TXN",')
t = t.replace('"oxidative_stress": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", "TXN",\n'
              '                         "NQO1", "GPX4", "ACSL4"],',
              '"oxidative_stress": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", "TXN",\n'
              '                         "NQO1", "GPX4", "ACSL4"],')

P.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("  three genes added, table field set on every entry, syntax OK")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")
    for i in range(max(0, e.lineno - 3), min(len(t.splitlines()), e.lineno + 2)):
        print(f"    {i+1:4d}: {t.splitlines()[i]}")
    raise SystemExit(1)

import subprocess
r = subprocess.run(["python", str(P)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
show = [l for l in out.splitlines()
        if l.strip().startswith(("CAT", "GPX1", "TXN", "with an ocular", "with neither",
                                 "with an ocular feature", "mitochondrial", "oxidative_stress",
                                 "inflammatory"))]
for line in show:
    print(f"  {line}")
