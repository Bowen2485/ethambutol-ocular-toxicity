# -*- coding: utf-8 -*-
"""
Show the schema of the tables a temporal split needs, and the full year distribution.

The split has to be chosen from the data: both halves must carry enough ethambutol
cases and enough optic-nerve events to be analysed on their own, and the receipt-date
distribution is very uneven (about 274,000 cases in 2004 against well over a million a
year recently), so a naive median-year split would not balance the events.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

print("=" * 84)
print("1. Schema of the tables involved")
print("=" * 84)
for t in ("demo", "drug", "reac", "dedup_map", "ocular_case", "term_db"):
    try:
        cols = con.execute(f'PRAGMA table_info("{t}")').fetchall()
    except Exception as exc:  # noqa: BLE001
        print(f"  {t}: unavailable ({type(exc).__name__})")
        continue
    print(f"\n  {t}  ({len(cols)} columns)")
    for c in cols:
        print(f"      {c[1]:22s} {c[2]}")

print()
print("=" * 84)
print("2. Full year distribution of receipt dates")
print("=" * 84)
years = con.execute(
    "SELECT substr(fda_dt,1,4) AS y, COUNT(*) FROM demo "
    "WHERE fda_dt IS NOT NULL AND length(fda_dt) >= 4 "
    "GROUP BY y ORDER BY y").fetchall()
tot = 0
for y, c in years:
    if y and y.isdigit() and 1990 <= int(y) <= 2030:
        print(f"  {y}  {c:>12,}")
        tot += c
print(f"  {'total':>4s}  {tot:>12,}")

print()
print("=" * 84)
print("3. Ethambutol cases and optic-nerve events by year")
print("=" * 84)
# how many ethambutol cases exist per year, and how many carry an optic-nerve term
q = """
SELECT substr(d.fda_dt,1,4) AS y,
       COUNT(DISTINCT d.primaryid) AS n_emb,
       COUNT(DISTINCT CASE WHEN r.pt LIKE '%OPTIC NEUROPATHY%'
                            OR r.pt LIKE '%OPTIC NEURITIS%'
                            OR r.pt LIKE '%OPTIC ATROPHY%'
                           THEN d.primaryid END) AS n_optic
FROM drug d
LEFT JOIN reac r ON r.primaryid = d.primaryid
WHERE d.fda_dt IS NOT NULL
  AND length(d.fda_dt) >= 4
  AND (lower(d.drugname) LIKE '%ethambutol%'
       OR lower(d.drugname) LIKE '%myambutol%')
GROUP BY y ORDER BY y
"""
try:
    rows = con.execute(q).fetchall()
    print(f"  {'year':>6s} {'ethambutol':>12s} {'optic-nerve':>12s}")
    for y, n, k in rows:
        if y and y.isdigit() and int(y) >= 1990:
            print(f"  {y:>6s} {n:>12,} {k:>12,}")
    print(f"  {'total':>6s} {sum(r[1] for r in rows):>12,} {sum(r[2] for r in rows):>12,}")
except Exception as exc:  # noqa: BLE001
    print(f"  query failed: {type(exc).__name__}: {str(exc)[:200]}")

con.close()
