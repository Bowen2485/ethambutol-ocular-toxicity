# -*- coding: utf-8 -*-
"""
Inspect the FAERS database so a temporal validation split can be designed.

The paper rests on a single data source, which is its main external-validity weakness:
FAERS is subject to stimulated reporting, duplicate reports and drifting reporting
habits, so a signal found in the pooled database could in principle be an artefact of
one period rather than a property of the drug.  Splitting the 20.3 million cases by
receipt date and testing the optic-nerve signal independently in each period answers
that directly, and needs no new data.

This reports what the database actually contains: the tables, the date range, the
yearly case counts and where the ethambutol cases fall, so the split point is chosen
from the data rather than assumed.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"

print("=" * 84)
print("1. Database")
print("=" * 84)
if not DB.exists():
    raise SystemExit(f"{DB} not found")
print(f"  path : {DB}")
print(f"  size : {DB.stat().st_size/1e9:.2f} GB")

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

print()
print("=" * 84)
print("2. Tables and views")
print("=" * 84)
rows = con.execute(
    "SELECT type, name FROM sqlite_master WHERE type IN ('table','view') "
    "ORDER BY type, name").fetchall()
for t, n in rows:
    try:
        c = con.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0]
        print(f"  {t:5s} {n:28s} {c:>15,} rows")
    except Exception as exc:  # noqa: BLE001
        print(f"  {t:5s} {n:28s} count failed: {type(exc).__name__}")

# find the table that holds case-level dates
print()
print("=" * 84)
print("3. Columns available for a date split")
print("=" * 84)
date_tables = []
for t, n in rows:
    if t != "table":
        continue
    try:
        cols = [r[1] for r in con.execute(f'PRAGMA table_info("{n}")').fetchall()]
    except Exception:  # noqa: BLE001
        continue
    hits = [c for c in cols if any(k in c.lower()
                                  for k in ("fda_dt", "receipt", "date", "year"))]
    if hits:
        date_tables.append((n, cols, hits))
        print(f"  {n:28s} date-like columns: {hits}")

print()
print("=" * 84)
print("4. Case counts by year, and the ethambutol subset")
print("=" * 84)
if not date_tables:
    print("  no date column found; the split cannot be built from this database")
else:
    tbl, cols, hits = date_tables[0]
    col = hits[0]
    print(f"  using {tbl}.{col}")
    # FAERS dates are usually YYYYMMDD strings; take the first four characters
    try:
        q = (f'SELECT substr("{col}",1,4) AS y, COUNT(*) FROM "{tbl}" '
             f'WHERE "{col}" IS NOT NULL AND length("{col}") >= 4 '
             f'GROUP BY y ORDER BY y')
        yrs = con.execute(q).fetchall()
    except Exception as exc:  # noqa: BLE001
        print(f"  year grouping failed: {type(exc).__name__}: {exc}")
        yrs = []
    if yrs:
        print(f"  {'year':>6s} {'cases':>14s}")
        for y, c in yrs:
            if y and y.isdigit() and 1990 <= int(y) <= 2030:
                print(f"  {y:>6s} {c:>14,}")
        tot = sum(c for y, c in yrs if y and y.isdigit())
        print(f"  {'total':>6s} {tot:>14,}")

con.close()
print()
print("=" * 84)
print("Next step")
print("=" * 84)
print("""  With the yearly distribution known, a split can be chosen so that both halves
  carry enough ethambutol cases and enough optic-nerve events to be analysed
  independently.  The same disproportionality panel is then computed separately in
  each half and the two are compared: replication in an independent period, on the
  same database, is the cheapest available answer to the single-source criticism.""")
