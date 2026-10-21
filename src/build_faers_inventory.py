# -*- coding: utf-8 -*-
"""Write results/faers_inventory.json from the warehouse and the de-duplication table.

Why this file exists
    Three numbers that the manuscript and Figure 1 both quote - the number of quarterly
    releases, the number of submitted reports and the number removed as superseded
    versions - were previously typed by hand.  They drifted: the text still carried the
    89-quarter totals (24,389,966 reports, 4,061,398 duplicates) after the 90-quarter
    rerun, and Figure 1 carried an older pair again.  Deriving them once, here, lets both
    the text audit and the figure read one file.

Source of each value
    quarters, submitted reports, duplicate versions   data/derived/faers.sqlite
    de-duplicated cases, ethambutol cases             results/faers_dedup_summary.csv
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
OUT = ROOT / "results" / "faers_inventory.json"

con = sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True)
submitted = int(con.execute("SELECT COUNT(*) FROM demo").fetchone()[0])
quarters = [r[0] for r in con.execute("SELECT DISTINCT quarter FROM demo ORDER BY quarter")]
dedup = pd.read_csv(ROOT / "results" / "faers_dedup_summary.csv", encoding="utf-8-sig")
cases = int(dedup[dedup.drug == "FAERS_ALL"].n_cases.iloc[0])
eth = int(dedup[dedup.drug == "ethambutol"].n_cases.iloc[0])
con.close()

payload = {
    "source": "data/derived/faers.sqlite (demo) and results/faers_dedup_summary.csv",
    "first_quarter": quarters[0].upper(),
    "last_quarter": quarters[-1].upper(),
    "n_quarters": len(quarters),
    "submitted_reports": submitted,
    "superseded_versions": submitted - cases,
    "deduplicated_cases": cases,
    "ethambutol_cases": eth,
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"quarters            : {payload['n_quarters']} "
      f"({payload['first_quarter']}-{payload['last_quarter']})")
print(f"submitted reports   : {submitted:,}")
print(f"superseded versions : {submitted - cases:,}")
print(f"de-duplicated cases : {cases:,}")
print(f"ethambutol cases    : {eth:,}")
print(f"\nwritten: {OUT.relative_to(ROOT)}")
