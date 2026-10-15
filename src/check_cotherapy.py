# -*- coding: utf-8 -*-
"""
Check whether the antitubercular drugs are co-administered in the reports.

This decides whether the existing within-class comparison means what it appears to mean.
If ethambutol is nearly always reported alongside isoniazid and rifampicin - which is
what a RIPE regimen implies - then "ethambutol reports" and "isoniazid reports" are
largely the same patients, and comparing the two is not a drug-versus-drug contrast at
all.  It would instead be a comparison between two labellings of the same exposure.

The check is a simple one: among cases that mention ethambutol, what fraction also
mention each of the other antitubercular agents?  A high fraction for the first-line
drugs would show that the naive within-class comparison is confounded by regimen, and
would point to the analyses that are actually valid.

Usage
    python src/check_cotherapy.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"

# the same substance patterns the pipeline uses
DRUGS = {
    "ethambutol": ["%ETHAMBUTOL%", "%DEXAMBUTOL%", "%MYAMBUTOL%", "%ETAMBUTOL%"],
    "isoniazid": ["%ISONIAZID%", "%ISONICOTINYLHYDRAZINE%", "%INH%"],
    "rifampicin": ["%RIFAMPICIN%", "%RIFAMPIN%", "%RIFADIN%", "%RIFAMYCIN%"],
    "pyrazinamide": ["%PYRAZINAMIDE%"],
    "streptomycin": ["%STREPTOMYCIN%"],
    "linezolid": ["%LINEZOLID%", "%ZYWOX%"],
    "clofazimine": ["%CLOFAZIMINE%", "%LAMPRENE%"],
    "bedaquiline": ["%BEDAQUILINE%", "%SIRTURO%"],
    "moxifloxacin": ["%MOXIFLOXACIN%", "%AVELOX%"],
    "levofloxacin": ["%LEVOFLOXACIN%", "%LEVAQUIN%"],
    "amikacin": ["%AMIKACIN%", "%AMIKIN%"],
    "ethionamide": ["%ETHIONAMIDE%", "%TRECATOR%"],
}

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-1000000")

MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")


def cases_for(pats: list[str]) -> set[str]:
    cond = " OR ".join([MATCH] * len(pats))
    params = [p for pat in pats for p in (pat, pat)]
    q = f"""SELECT DISTINCT d.caseid FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE {cond}"""
    return {r[0] for r in con.execute(q, params)}


print("[" + "collecting case sets" + "]")
sets = {k: cases_for(v) for k, v in DRUGS.items()}
for k, v in sorted(sets.items(), key=lambda x: -len(x[1])):
    print(f"    {k:24s} {len(v):>9,} cases")

emb = sets["ethambutol"]
print()
print("=" * 92)
print("Among ethambutol cases, how often is each other drug also present?")
print("=" * 92)
print(f"  {'co-reported drug':24s} {'cases':>9s} {'% of ethambutol cases':>22s}")
rows = []
for k, v in sorted(sets.items(), key=lambda x: -len(emb & x[1])):
    if k == "ethambutol":
        continue
    n = len(emb & v)
    pct = 100 * n / max(len(emb), 1)
    rows.append({"drug": k, "n": n, "pct_of_ethambutol_cases": round(pct, 2)})
    print(f"  {k:24s} {n:>9,} {pct:>21.1f}%")

print()
print("=" * 92)
print("The mirror question: among each drug's cases, how often is ethambutol present?")
print("=" * 92)
print(f"  {'drug':24s} {'its cases':>10s} {'with ethambutol':>16s} {'%':>7s}")
for k, v in sorted(sets.items(), key=lambda x: -len(x[1])):
    if k == "ethambutol":
        continue
    n = len(v & emb)
    pct = 100 * n / max(len(v), 1)
    print(f"  {k:24s} {len(v):>10,} {n:>16,} {pct:>6.1f}%")

print()
print("=" * 92)
print("Regimen patterns within the ethambutol cases")
print("=" * 92)
import collections  # noqa: E402
first_line = ["isoniazid", "rifampicin", "pyrazinamide"]
combos = collections.Counter()
for c in emb:
    present = tuple(sorted(k for k in first_line if c in sets[k]))
    combos[present] += 1
print(f"  {'first-line drugs also present':44s} {'cases':>9s} {'%':>7s}")
for combo, n in combos.most_common():
    label = " + ".join(combo) if combo else "(ethambutol only)"
    print(f"  {label:44s} {n:>9,} {100*n/max(len(emb),1):>6.1f}%")

con.close()
print()
print("=" * 92)
print("Reading")
print("=" * 92)
print("""  A high co-reporting fraction for isoniazid and rifampicin means the naive
  within-class comparison contrasts two labels on the same patients, not two exposures.
  The analyses that remain valid are those that hold the regimen fixed: comparing
  ethambutol within reports that share a regimen, and using isoniazid monotherapy for
  latent tuberculosis as an active comparator, since that exposure carries the same
  indication and the same health system without ethambutol.""")
