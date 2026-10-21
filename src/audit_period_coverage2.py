# -*- coding: utf-8 -*-
"""Pin down the 57: are they cases or demo rows, and how many distinct cases?

dedup_map has 20,692,683 rows; the joins are on demo, which can carry several rows per surviving
primaryid.  This reports both counts so the manuscript can say which it means.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect((ROOT / "data" / "derived" / "faers.sqlite").as_uri() + "?mode=ro",
                      uri=True, timeout=30)
con.execute("CREATE TEMP TABLE dm AS SELECT caseid, primaryid FROM dedup_map")
con.execute("CREATE INDEX temp.ix_dm_pid ON dm(primaryid)")

n_rows = con.execute("SELECT COUNT(*) FROM dm").fetchone()[0]
n_cases = con.execute("SELECT COUNT(DISTINCT caseid) FROM dm").fetchone()[0]
print(f"dedup_map rows {n_rows:,}   distinct caseids {n_cases:,}")

pre2004_cases = con.execute(
    "SELECT COUNT(*) FROM (SELECT m.caseid FROM dm m JOIN demo de ON de.primaryid = m.primaryid "
    "GROUP BY m.caseid HAVING MAX(substr(de.fda_dt,1,4)) < '2004')").fetchone()[0]
pre2004_rows = con.execute(
    "SELECT COUNT(*) FROM dm m JOIN demo de ON de.primaryid = m.primaryid "
    "WHERE substr(de.fda_dt,1,4) < '2004'").fetchone()[0]
inrange_cases = con.execute(
    "SELECT COUNT(DISTINCT m.caseid) FROM dm m JOIN demo de ON de.primaryid = m.primaryid "
    "WHERE substr(de.fda_dt,1,4) BETWEEN '2004' AND '2026'").fetchone()[0]
print(f"cases whose every receipt year is before 2004: {pre2004_cases:,} (rows {pre2004_rows:,})")
print(f"cases with at least one year in 2004-2026 : {inrange_cases:,}")
print(f"cases + pre-2004 cases = {inrange_cases + pre2004_cases:,} vs distinct {n_cases:,}")

payload = {"dedup_rows": n_rows, "distinct_caseids": n_cases,
           "pre2004_cases": pre2004_cases, "pre2004_rows": pre2004_rows,
           "inrange_cases": inrange_cases}
(ROOT / "results" / "audit_period_coverage.json").write_text(json.dumps(payload, indent=2),
                                                             encoding="utf-8")
print("written results/audit_period_coverage.json")
con.close()
