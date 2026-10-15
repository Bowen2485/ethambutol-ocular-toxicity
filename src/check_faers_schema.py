# -*- coding: utf-8 -*-
"""
Check the column names the temporal validation script relies on, before it runs.

The first attempt failed with "no such column: dm.fda_dt" because dedup_map holds only
(caseid, primaryid).  This verifies every table and column the script touches, and
prints the row counts it will work with, so a schema mistake surfaces in seconds rather
than after minutes of table building.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"

NEEDED = {
    "dedup_map": ["caseid", "primaryid"],
    "demo": ["primaryid", "fda_dt"],
    "drugname": ["primaryid", "drugname", "prod_ai"],
    "reac": ["primaryid", "pt"],
}

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
ok = True
print("=" * 84)
print("Column check")
print("=" * 84)
for table, cols in NEEDED.items():
    have = [r[1] for r in con.execute(f'PRAGMA table_info("{table}")').fetchall()]
    if not have:
        print(f"  {table:12s} TABLE MISSING")
        ok = False
        continue
    missing = [c for c in cols if c not in have]
    status = "OK" if not missing else f"MISSING {missing}"
    if missing:
        ok = False
    print(f"  {table:12s} {status}")
    print(f"      has : {have}")

print()
print("=" * 84)
print("Row counts and the ethambutol match")
print("=" * 84)
for t in NEEDED:
    try:
        n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"  {t:12s} {n:>15,} rows")
    except Exception as exc:  # noqa: BLE001
        print(f"  {t:12s} count failed: {type(exc).__name__}")

print()
# verify the joins the script performs actually return rows
checks = [
    ("dedup_map joined to demo on primaryid",
     "SELECT COUNT(*) FROM dedup_map dm JOIN demo d ON d.primaryid = dm.primaryid"),
    ("cases with a usable receipt year",
     "SELECT COUNT(*) FROM dedup_map dm JOIN demo d ON d.primaryid = dm.primaryid "
     "WHERE d.fda_dt IS NOT NULL AND length(d.fda_dt) >= 4"),
    ("drugname rows matching ETHAMBUTOL",
     "SELECT COUNT(*) FROM drugname WHERE UPPER(COALESCE(drugname,'')) "
     "LIKE '%ETHAMBUTOL%'"),
    ("drugname prod_ai rows matching ETHAMBUTOL",
     "SELECT COUNT(*) FROM drugname WHERE UPPER(COALESCE(prod_ai,'')) "
     "LIKE '%ETHAMBUTOL%'"),
    ("distinct ethambutol caseids",
     "SELECT COUNT(DISTINCT primaryid) FROM drugname "
     "WHERE UPPER(COALESCE(drugname,'')) LIKE '%ETHAMBUTOL%' "
     "   OR UPPER(COALESCE(prod_ai,''))  LIKE '%ETHAMBUTOL%'"),
    ("reac rows for OPTIC NEURITIS",
     "SELECT COUNT(*) FROM reac WHERE UPPER(pt) = 'OPTIC NEURITIS'"),
    ("reac rows for OPTIC NEUROPATHY",
     "SELECT COUNT(*) FROM reac WHERE UPPER(pt) = 'OPTIC NEUROPATHY'"),
    ("reac rows for TOXIC OPTIC NEUROPATHY",
     "SELECT COUNT(*) FROM reac WHERE UPPER(pt) = 'TOXIC OPTIC NEUROPATHY'"),
]
for label, sql in checks:
    try:
        n = con.execute(sql).fetchone()[0]
        print(f"  {label:48s} {n:>14,}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label:48s} FAILED: {type(exc).__name__}: {str(exc)[:60]}")
        ok = False

print()
# what the actual optic-nerve preferred terms look like, so the term list can be fixed
print("=" * 84)
print("Preferred terms containing OPTIC (the exact spellings present)")
print("=" * 84)
rows = con.execute(
    "SELECT UPPER(pt) AS p, COUNT(*) FROM reac WHERE UPPER(pt) LIKE '%OPTIC%' "
    "GROUP BY p ORDER BY 2 DESC LIMIT 25").fetchall()
for p, n in rows:
    print(f"  {n:>10,}  {p}")

con.close()
print()
print("RESULT:", "the schema matches what the script expects" if ok
      else "FIX THE MISMATCHES ABOVE BEFORE RUNNING")
