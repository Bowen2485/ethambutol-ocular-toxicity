# -*- coding: utf-8 -*-
"""
Find why the temporal validation returned zero ethambutol cases.

The analysis reported 0 ethambutol cases against the paper's 13,804, so the exposure
query matched nothing.  Two candidate causes:

  a) drug.fda_dt is largely empty, so the receipt-year filter removed every row
  b) the drug -> drugname join does not line up

The counts below separate them.  demo.fda_dt is known to be populated (the yearly
distribution came from it), so if drug.fda_dt is sparse the fix is to take the year
from demo, joined on primaryid, and keep everything else as it is.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-1000000")


def scalar(sql: str):
    try:
        return con.execute(sql).fetchone()[0]
    except Exception as exc:  # noqa: BLE001
        return f"ERROR {type(exc).__name__}: {str(exc)[:70]}"


MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%' "
         " OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%')")

print("=" * 84)
print("1. Is drug.fda_dt populated?")
print("=" * 84)
n_drug = scalar("SELECT COUNT(*) FROM drug")
n_drug_dated = scalar("SELECT COUNT(*) FROM drug WHERE fda_dt IS NOT NULL "
                      "AND length(fda_dt) >= 4")
n_dn = scalar("SELECT COUNT(*) FROM drugname")
n_dn_dated = scalar("SELECT COUNT(*) FROM drugname WHERE fda_dt IS NOT NULL "
                    "AND length(fda_dt) >= 4")
n_demo_dated = scalar("SELECT COUNT(*) FROM demo WHERE fda_dt IS NOT NULL "
                      "AND length(fda_dt) >= 4")
print(f"  drug rows                                  {n_drug:>14,}")
print(f"  drug rows with fda_dt non-empty            {n_drug_dated:>14,}")
print(f"  drugname rows                              {n_dn:>14,}")
print(f"  drugname rows with fda_dt non-empty        {n_dn_dated:>14,}")
print(f"  demo rows with fda_dt non-empty            {n_demo_dated:>14,}")

print()
print("=" * 84)
print("2. The exposure query, with and without the year filter")
print("=" * 84)
base = f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
           JOIN dedup_map m ON d.primaryid = m.primaryid
           JOIN drugname dn ON dn.primaryid = d.primaryid
                           AND dn.drug_seq = d.drug_seq
           WHERE {MATCH}"""
print(f"  no date filter                             {scalar(base):>14,}")
print(f"  filtering on drug.fda_dt                   "
      f"{scalar(base + ' AND d.fda_dt IS NOT NULL AND length(d.fda_dt) >= 4'):>14,}")
print(f"  filtering on drugname.fda_dt               "
      f"{scalar(base + ' AND dn.fda_dt IS NOT NULL AND length(dn.fda_dt) >= 4'):>14,}")
with_demo = f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
                JOIN dedup_map m ON d.primaryid = m.primaryid
                JOIN drugname dn ON dn.primaryid = d.primaryid
                                AND dn.drug_seq = d.drug_seq
                JOIN demo dm ON dm.primaryid = m.primaryid
                WHERE {MATCH}
                  AND dm.fda_dt IS NOT NULL AND length(dm.fda_dt) >= 4"""
print(f"  year taken from demo, joined on primaryid  {scalar(with_demo):>14,}")

print()
print("=" * 84)
print("3. Does the paper's 13,804 include name variants?")
print("=" * 84)
for label, cond in [
    ("ETHAMBUTOL only",
     "UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%' "
     "OR UPPER(COALESCE(dn.prod_ai,'')) LIKE '%ETHAMBUTOL%'"),
    ("ETHAMBUTOL or MYAMBUTOL",
     "UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%' "
     "OR UPPER(COALESCE(dn.prod_ai,'')) LIKE '%ETHAMBUTOL%' "
     "OR UPPER(COALESCE(dn.drugname,'')) LIKE '%MYAMBUTOL%'"),
]:
    q = f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE ({cond})"""
    print(f"  {label:26s} {scalar(q):>12,}")

print()
print("=" * 84)
print("4. A sample of the matching drugname rows")
print("=" * 84)
try:
    rows = con.execute(
        "SELECT drugname, prod_ai, COUNT(*) FROM drugname "
        "WHERE UPPER(COALESCE(drugname,'')) LIKE '%ETHAMBUTOL%' "
        "GROUP BY drugname, prod_ai ORDER BY 3 DESC LIMIT 12").fetchall()
    for dn_, ai, n in rows:
        print(f"  {n:>7,}  drugname={str(dn_)[:34]:34s} prod_ai={str(ai)[:28]}")
except Exception as exc:  # noqa: BLE001
    print(f"  failed: {type(exc).__name__}: {exc}")

con.close()
