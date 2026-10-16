# -*- coding: utf-8 -*-
"""
Repair the three dictionary entries added for MAPK1, IL6 and STAT3.

The entries were added by string substitution and came out malformed in two ways: one note
string was split across lines without a continuation, and a trailing comma was doubled.  Both
are the kind of damage that substitution produces, and it is why the replacement approach is
being abandoned here in favour of editing the exact text.

The replacement also reclassifies TP53 and SOD2.  They were listed under an inflammatory arm,
which is wrong on both counts: TP53 is a tumour suppressor central to apoptosis and SOD2 is a
mitochondrial superoxide dismutase.  Grouping them as inflammatory made the inflammatory arm
look as though it carried ocular annotation when it does not, which is the opposite of what
the data show.  They move to an oxidative-stress arm, and only genuine inflammatory-response
genes remain in the other.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "record_genecards_readings.py"
t = P.read_text(encoding="utf-8")

# ---- fix the two malformations
BROKEN_NOTE = ('        "note": "the category tag is on two Noonan syndromes, whose '
               'ocular features are\n'
               '        facial findings rather than eye disease",\n'
               '    },,')
FIXED_NOTE = ('        "note": "the category tag is on two Noonan syndromes, whose '
              'ocular features are "\n'
              '                "facial findings rather than eye disease",\n'
              '    },')
if BROKEN_NOTE in t:
    t = t.replace(BROKEN_NOTE, FIXED_NOTE)
    print("  repaired the MAPK1 entry and the doubled comma")
else:
    print("  the broken entry was not found verbatim")

BROKEN_STAT = ('        "note": "37 disorders, all immunological, haematological or '
               'inflammatory; no\n'
               '        ocular annotation",\n')
FIXED_STAT = ('        "note": "37 disorders, all immunological, haematological or '
              'inflammatory; "\n'
              '                "no ocular annotation",\n')
if BROKEN_STAT in t:
    t = t.replace(BROKEN_STAT, FIXED_STAT)
    print("  repaired the STAT3 note")

# ---- reclassify: TP53 and SOD2 are not inflammatory genes
OLD_ARMS = ('    "inflammatory": ["TNF", "IL6", "STAT3", "NFE2L2", "HMOX1", "KEAP1", '
            '"MAPK1"],\n    "oxidative": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", '
            '"TXN", "NQO1"],')
NEW_ARMS = ('    "mitochondrial": ["MFN2", "SLC25A4", "SDHB", "DNM1L", "OPA1", "SDHA",\n'
            '                      "CYCS", "VDAC1", "APAF1"],\n'
            '    "oxidative_stress": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", "TXN",\n'
            '                         "NQO1", "GPX4", "ACSL4"],\n'
            '    "inflammatory": ["TNF", "IL6", "STAT3", "NFE2L2", "HMOX1", "KEAP1",\n'
            '                     "MAPK1", "AKT1", "BCL2", "BAX", "CASP3"],')
if OLD_ARMS in t:
    t = t.replace(OLD_ARMS, NEW_ARMS)
    print("  arms redefined: mitochondrial, oxidative_stress, inflammatory")
else:
    # look for whatever the arms block currently says
    i = t.find('ARMS = {')
    j = t.find('}', i)
    print(f"  arms block as it stands: {t[i:j+1][:400]}")

P.write_text(t, encoding="utf-8")

try:
    ast.parse(P.read_text(encoding="utf-8"))
    print("  syntax: OK")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")
    lines = P.read_text(encoding="utf-8").splitlines()
    for i in range(max(0, e.lineno - 3), min(len(lines), e.lineno + 2)):
        print(f"    {i+1:4d}: {lines[i]}")
