# -*- coding: utf-8 -*-
"""Role breakdown for the ethambutol cohort, from the de-duplicated warehouse.

Section 3.1 states how many ethambutol cases carry the drug as a suspect (primary or
secondary) and how many as a concomitant only.  Those three counts were typed from the
89-quarter run and no longer matched the 90-quarter cohort, so they are recomputed here
and written to results/faers_role_breakdown.json for the text to cite.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect((ROOT / "data" / "derived" / "faers.sqlite").as_uri() + "?mode=ro",
                      uri=True)

total = con.execute(
    "SELECT COUNT(*) FROM dedup_map").fetchone()[0]
eth_rows = con.execute(
    "SELECT COUNT(*) FROM drug_case WHERE drug = 'ethambutol'").fetchone()[0]
eth_cases = con.execute(
    "SELECT COUNT(DISTINCT caseid) FROM drug_case WHERE drug = 'ethambutol'").fetchone()[0]
print(f"dedup_map cases          : {total:,}")
print(f"drug_case ethambutol rows: {eth_rows:,}")
print(f"distinct ethambutol cases: {eth_cases:,}")

roles = dict(con.execute(
    "SELECT role_cod, COUNT(DISTINCT caseid) FROM drug_case "
    "WHERE drug = 'ethambutol' GROUP BY role_cod"))
print("role codes (distinct cases):", roles)

#: a case counts as suspect if any of its ethambutol drug records carries PS or SS
suspect = con.execute(
    "SELECT COUNT(DISTINCT caseid) FROM drug_case "
    "WHERE drug = 'ethambutol' AND role_cod IN ('PS','SS')").fetchone()[0]
primary = con.execute(
    "SELECT COUNT(DISTINCT caseid) FROM drug_case "
    "WHERE drug = 'ethambutol' AND role_cod = 'PS'").fetchone()[0]
concomitant_only = eth_cases - suspect

payload = {
    "source": "data/derived/faers.sqlite: drug_case role_cod, distinct caseid",
    "ethambutol_cases": eth_cases,
    "suspect_ps_or_ss": suspect,
    "primary_suspect": primary,
    "concomitant_only": concomitant_only,
    "suspect_percent": round(100 * suspect / eth_cases, 1),
    "role_counts": roles,
}
out = ROOT / "results" / "faers_role_breakdown.json"
out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\nsuspect (PS or SS)      : {suspect:,} ({100*suspect/eth_cases:.1f}%)")
print(f"primary suspect (PS)    : {primary:,}")
print(f"concomitant only        : {concomitant_only:,}")
print(f"written: {out.relative_to(ROOT)}")
