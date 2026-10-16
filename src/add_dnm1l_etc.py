# -*- coding: utf-8 -*-
"""
Add DNM1L, VDAC1, NQO1, PPARGC1A and HIF1A, and stop the two disorder tables being mixed.

The problem this exposes
    GeneCards shows two lists per gene.  "Disorders associated with" is unified from curated
    and inferred sources and is the shorter one - 22 entries for DNM1L, 7 for HIF1A.  "Inferred
    disorder associations" is the computational list and is far longer - 57 for VDAC1, 59 for
    TXN, 67 for NQO1, 237 for HIF1A.  A gene with a longer list has more chances to include an
    ocular entry, so counting "how many genes have an eye disorder" across a mixture of the two
    tables measures the length of the table as much as the biology.

    The earlier arm analysis did exactly that without saying so: the inflammatory arm was read
    entirely from the unified tables and came out at zero, while TXN and NQO1 were read from
    the inferred tables and had several.  The comparison was therefore not like for like.

    The correction is not to discard either table but to keep them apart.  Every entry now
    records which list it came from, and the summary counts each list separately, so the
    inflammatory arm's zero is reported as a unified-table result - which is what it is - and
    the inferred tables are reported as unread for the genes where they were not opened.

What the additions show
    DNM1L, read from its unified table, names optic atrophy 5, optic atrophy 1, Leber
    hereditary optic neuropathy as a modifier and retinal disease: a strong ocular signal of
    the same kind as MFN2 and SLC25A4.  VDAC1, NQO1 and PPARGC1A were read from inferred
    tables and name ocular disorders there; that is consistent with the biology but is not
    evidence of the same strength, because their unified tables were not seen.  HIF1A's unified
    table names seven disorders, none ocular.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "record_genecards_readings.py"
t = P.read_text(encoding="utf-8")

ADDITIONS = [
    ("DNM1L", 22, 0, "unified",
     ["Optic Atrophy 5", "Optic Atrophy 1",
      "Leber Hereditary Optic Neuropathy, Modifier Of", "Retinal Disease"], [], 6,
     "unified table; four ocular disorders including two optic atrophies, of the same kind "
     "as MFN2 and SLC25A4"),
    ("VDAC1", 0, 57, "inferred",
     ["Kearns-Sayre Syndrome", "Optic Atrophy Plus Syndrome",
      "Leber Hereditary Optic Neuropathy, Modifier Of", "Retinal Disease"], [], 5,
     "inferred table, 57 disorders; the unified table was not seen, so this is not directly "
     "comparable with the unified readings"),
    ("NQO1", 0, 67, "inferred",
     ["Corneal Endothelial Dystrophy", "Retinal Disease",
      "Leber Hereditary Optic Neuropathy, Modifier Of", "Retinoblastoma", "Leigh Disease"],
     [], 6,
     "inferred table, 67 disorders; corneal endothelial dystrophy is the most specific "
     "ocular entry.  The unified table was not seen"),
    ("PPARGC1A", 3, 102, "unified",
     [], ["Macular Degeneration"], 0,
     "unified table holds 3 disorders, none ocular, while the inferred table of 102 opens "
     "with macular degeneration; recorded as incidental because the ocular entry is from the "
     "inferred list"),
    ("HIF1A", 7, 237, "unified", [], [], 0,
     "unified table; phaeochromocytoma, breast cancer, Ollier disease, prostate cancer, "
     "Maffucci syndrome, enchondromatosis, soft tissue sarcoma - none ocular.  Its inferred "
     "table holds 237 disorders and was not read"),
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

#: FOCUS gains the five, and the arms are extended
t = t.replace('"CAT", "GPX1", "TXN",', '"CAT", "GPX1", "TXN", "DNM1L", "VDAC1", "NQO1",\n'
              '         "PPARGC1A", "HIF1A",')
t = t.replace('"mitochondrial": ["MFN2", "SLC25A4", "SDHB", "DNM1L", "OPA1", "SDHA", "CYCS",\n'
              '                      "VDAC1", "APAF1"],',
              '"mitochondrial": ["MFN2", "SLC25A4", "SDHB", "DNM1L", "VDAC1", "OPA1",\n'
              '                      "SDHA", "CYCS", "APAF1"],')
t = t.replace('"oxidative_stress": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", "TXN",\n'
              '                         "NQO1", "GPX4", "ACSL4"],',
              '"oxidative_stress": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", "TXN",\n'
              '                         "NQO1", "GPX4", "ACSL4"],\n'
              '    "metabolic_hypoxia": ["HIF1A", "PPARGC1A", "FTH1", "FTL"],')

#: a guard on the summary, so the two tables can never be silently pooled again
GUARD_ANCHOR = 'print("=" * 104)\nprint("What the network\'s arms look like on this evidence")'
GUARD = '''#: The two disorder tables are not comparable and must not be pooled.  A gene read from its
#: inferred list has a far longer table than one read from its unified list - 237 entries for
#: HIF1A against 7 - so a count of "genes with an eye disorder" across a mixture measures the
#: length of the table.  The summary below therefore reports the two lists separately, and
#: says plainly which genes' inferred tables were never opened.
by_table: dict[str, list[str]] = {}
for g, d in DATA.items():
    if d.get("eye_core"):
        by_table.setdefault(d.get("table", "unified"), []).append(g)
unread = [g for g, d in DATA.items()
          if d.get("table") == "unified" and d.get("n_inferred", 0) > 30]
print()
print("=" * 104)
print("Comparability of the two disorder tables")
print("=" * 104)
for tbl, genes in sorted(by_table.items()):
    print(f"  read from the {tbl:9s} table, with an ocular disorder: "
          f"{len(genes):>2d}  {', '.join(sorted(genes))}")
print(f"  unified-table genes whose inferred table holds more than 30 disorders and was "
      f"not read: {len(unread)}")
print(f"      {', '.join(sorted(unread))}")
print()
print("""  The inflammatory arm's zero is a unified-table result.  Its inferred tables were not
  opened, so it cannot be stated as a property of those genes outright, and the manuscript
  says which table each figure comes from.""")

'''
if GUARD_ANCHOR in t:
    t = t.replace(GUARD_ANCHOR, GUARD + GUARD_ANCHOR, 1)
    print("  guard added to the summary")
else:
    print("  WARNING: guard anchor not found")

P.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("  five genes added, syntax OK")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")
    for i in range(max(0, e.lineno - 3), min(len(t.splitlines()), e.lineno + 2)):
        print(f"    {i+1:4d}: {t.splitlines()[i]}")
    raise SystemExit(1)

import subprocess
r = subprocess.run(["python", str(P)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
start = out.find("Comparability of the two disorder tables")
print(out[start - 4:] if start > 0 else out[-2500:])
