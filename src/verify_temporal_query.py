# -*- coding: utf-8 -*-
"""
Confirm the corrected exposure query returns the published case count.

The temporal validation produced zeros for every cell, which means the version that ran
was the one filtering on drug.fda_dt - a column that is empty in all 98,884,686 of its
rows.  Before re-running the analysis this checks the corrected query on its own, so
that a second wasted run is not spent discovering another definition problem.

The query under test is the one now in faers_temporal_validation.ethambutol_cases, with
the receipt year taken from demo joined through dedup_map.  The expected answer is the
paper's 13,804 strict-match cases.
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"

TOKENS = ["ETHAMBUTOL", "MYAMBUTOL"]


def match_sql(alias: str, tokens: list[str]) -> tuple[str, list]:
    conds, params = [], []
    for t in tokens:
        conds.append(f"(UPPER(COALESCE({alias}.drugname,'')) LIKE ? "
                     f"OR UPPER(COALESCE({alias}.prod_ai,'')) LIKE ?)")
        params += [f"%{t}%", f"%{t}%"]
    return "(" + " OR ".join(conds) + ")", params


con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-1000000")

cond, params = match_sql("dn", TOKENS)

print("=" * 84)
print("1. The join chain, step by step")
print("=" * 84)
steps = [
    ("drug rows matching the tokens (no joins)",
     f"SELECT COUNT(*) FROM drugname dn WHERE {cond}"),
    ("... restricted to de-duplicated cases",
     f"""SELECT COUNT(*) FROM drugname dn
         JOIN dedup_map m ON m.primaryid = dn.primaryid
         WHERE {cond}"""),
    ("... with the drug table joined on drug_seq",
     f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
         JOIN dedup_map m ON d.primaryid = m.primaryid
         JOIN drugname dn ON dn.primaryid = d.primaryid
                         AND dn.drug_seq = d.drug_seq
         WHERE {cond}"""),
    ("... and demo joined for the receipt year",
     f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
         JOIN dedup_map m ON d.primaryid = m.primaryid
         JOIN drugname dn ON dn.primaryid = d.primaryid
                         AND dn.drug_seq = d.drug_seq
         JOIN demo dm ON dm.primaryid = m.primaryid
         WHERE {cond}"""),
]
for label, sql in steps:
    t0 = time.time()
    try:
        n = con.execute(sql, params).fetchone()[0]
        print(f"  {n:>10,}   {label}   ({time.time()-t0:.1f}s)")
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED     {label}: {type(exc).__name__}: {str(exc)[:70]}")

print()
print("=" * 84)
print("2. Does the receipt year actually survive the chain?")
print("=" * 84)
q = f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
        JOIN dedup_map m ON d.primaryid = m.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        JOIN demo dm ON dm.primaryid = m.primaryid
        WHERE {cond}
          AND dm.fda_dt IS NOT NULL AND length(dm.fda_dt) >= 4"""
try:
    n = con.execute(q, params).fetchone()[0]
    print(f"  {n:>10,}   with a usable receipt year")
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED: {type(exc).__name__}: {exc}")

print()
print("=" * 84)
print("3. Total cases in each proposed period")
print("=" * 84)
for label, cond2 in [("2004-2018", "substr(d.fda_dt,1,4) <= '2018'"),
                     ("2019-2026", "substr(d.fda_dt,1,4) > '2018'")]:
    q = f"""SELECT COUNT(DISTINCT d.caseid) FROM demo d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            WHERE d.fda_dt IS NOT NULL AND length(d.fda_dt) >= 4 AND {cond2}"""
    n = con.execute(q).fetchone()[0]
    print(f"  {n:>12,}   {label}")

con.close()
print()
print("  The paper reports 13,804 strict-match cases and 15,573 with name variants,")
print("  so the third line above should land in that range.  If it does, the analysis")
print("  can be re-run as it stands.")
