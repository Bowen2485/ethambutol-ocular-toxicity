# -*- coding: utf-8 -*-
"""
Step 2 - Materialised exposure / outcome index tables.

A substring match over 98.9 million drug rows is intractable per query, so the
drug->case and reaction->case mappings needed by the signal analysis are computed
once and stored as small index tables.  Every downstream 2x2 cell then comes from
a join against these tables.

Tables created
    drug_case   (drug, caseid)                      one row per exposure
    drug_ps     (drug, caseid)                      primary/secondary suspect only
    ocular_case (term, caseid)                      ocular MedDRA PTs
    term_db     (term, n_cases)                     whole-database term frequency
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DB = DERIVED / "faers.sqlite"

DRUGS = {
    "ethambutol": ["ETHAMBUTOL"],
    "isoniazid": ["ISONIAZID"],
    "rifampicin": ["RIFAMPICIN", "RIFAMPIN"],
    "pyrazinamide": ["PYRAZINAMIDE"],
    "streptomycin": ["STREPTOMYCIN"],
    "linezolid": ["LINEZOLID"],
}


def connect(rw: bool = True) -> sqlite3.Connection:
    con = (sqlite3.connect(DB, timeout=900, isolation_level=None) if rw
           else sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=600))
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1200000")
    return con


def build() -> None:
    con = connect(rw=True)
    t0 = time.time()

    have = con.execute("SELECT name FROM sqlite_master WHERE type='table' "
                       "AND name='dedup_map'").fetchone()
    if not have:
        raise SystemExit("dedup_map missing - build it with faers_signal_analysis.py")
    n_cases = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
    print(f"[base] de-duplicated cases: {n_cases:,}")

    for tbl in ("drug_case", "drug_ps", "ocular_case", "term_db"):
        con.execute(f"DROP TABLE IF EXISTS {tbl}")

    print("[1/4] drug_case ...")
    con.execute("CREATE TABLE drug_case (drug TEXT, caseid TEXT)")
    for drug, subs in DRUGS.items():
        cond = " OR ".join(
            ["UPPER(d.substance) LIKE ? OR UPPER(d.medicinalproduct) LIKE ?"] * len(subs))
        params: list = []
        for s in subs:
            params += [f"%{s.upper()}%", f"%{s.upper()}%"]
        q = f"""INSERT INTO drug_case
                SELECT DISTINCT '{drug}', d.caseid FROM drug d
                JOIN dedup_map m ON d.primaryid = m.primaryid
                WHERE ({cond})"""
        t1 = time.time()
        con.execute(q, params)
        n = con.execute("SELECT COUNT(*) FROM drug_case WHERE drug=?",
                        (drug,)).fetchone()[0]
        print(f"    {drug:14s} {n:>8,} cases   ({time.time()-t1:.0f}s)")
    con.execute("CREATE INDEX ix_dc_drug ON drug_case(drug)")
    con.execute("CREATE INDEX ix_dc_case ON drug_case(caseid)")

    print("[2/4] drug_ps (primary/secondary suspect only) ...")
    con.execute("CREATE TABLE drug_ps (drug TEXT, caseid TEXT)")
    for drug, subs in DRUGS.items():
        cond = " OR ".join(
            ["UPPER(d.substance) LIKE ? OR UPPER(d.medicinalproduct) LIKE ?"] * len(subs))
        params: list = []
        for s in subs:
            params += [f"%{s.upper()}%", f"%{s.upper()}%"]
        q = f"""INSERT INTO drug_ps
                SELECT DISTINCT '{drug}', d.caseid FROM drug d
                JOIN dedup_map m ON d.primaryid = m.primaryid
                WHERE ({cond})
                  AND UPPER(COALESCE(d.role_cod,'')) IN ('PS','SS')"""
        con.execute(q, params)
    con.execute("CREATE INDEX ix_dps_drug ON drug_ps(drug)")

    print("[3/4] ocular_case ...")
    terms = pd.read_csv(DERIVED / "ocular_terms.csv", encoding="utf-8-sig")
    term_list = sorted(set(terms["term"].str.upper()))
    con.execute("CREATE TABLE ocular_case (term TEXT, caseid TEXT)")
    ph = ",".join("?" * len(term_list))
    q = f"""INSERT INTO ocular_case
            SELECT UPPER(r.pt), r.caseid FROM reac r
            JOIN dedup_map m ON r.primaryid = m.primaryid
            WHERE UPPER(r.pt) IN ({ph})"""
    con.execute(q, term_list)
    n = con.execute("SELECT COUNT(*) FROM ocular_case").fetchone()[0]
    print(f"    {len(term_list)} terms, {n:,} term-case rows")
    con.execute("CREATE INDEX ix_oc_term ON ocular_case(term)")
    con.execute("CREATE INDEX ix_oc_case ON ocular_case(caseid)")

    print("[4/4] term_db (whole-database frequency of the ocular terms) ...")
    con.execute("CREATE TABLE term_db (term TEXT PRIMARY KEY, n_cases INTEGER)")
    con.execute(f"""INSERT INTO term_db
                    SELECT UPPER(r.pt), COUNT(DISTINCT r.caseid) FROM reac r
                    JOIN dedup_map m ON r.primaryid = m.primaryid
                    WHERE UPPER(r.pt) IN ({ph})
                    GROUP BY UPPER(r.pt)""", term_list)
    n = con.execute("SELECT COUNT(*) FROM term_db").fetchone()[0]
    print(f"    {n} terms with database counts")

    con.execute("ANALYZE")
    con.close()
    print(f"\n[done] index tables built in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    build()
