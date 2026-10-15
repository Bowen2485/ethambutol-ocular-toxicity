# -*- coding: utf-8 -*-
"""Compute the drug-role distribution of ethambutol cases (for the manuscript)."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(f"file:{ROOT / 'data' / 'derived' / 'faers.sqlite'}?mode=ro",
                      uri=True, timeout=900)
con.execute("PRAGMA cache_size=-800000")

BASE = """
SELECT COUNT(DISTINCT d.caseid) FROM drug d
JOIN dedup_map m ON m.primaryid = d.primaryid
JOIN drugname dn ON dn.primaryid = d.primaryid AND dn.drug_seq = d.drug_seq
WHERE (UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
    OR UPPER(COALESCE(dn.prod_ai,'')) LIKE '%ETHAMBUTOL%')
"""

n_all = con.execute(BASE).fetchone()[0]
n_ps_ss = con.execute(BASE + " AND UPPER(COALESCE(d.role_cod,'')) IN ('PS','SS')").fetchone()[0]
n_ps = con.execute(BASE + " AND UPPER(COALESCE(d.role_cod,'')) = 'PS'").fetchone()[0]
n_ss = con.execute(BASE + " AND UPPER(COALESCE(d.role_cod,'')) = 'SS'").fetchone()[0]

print(f"ethambutol cases overall            : {n_all:,}")
print(f"  ethambutol coded PS or SS         : {n_ps_ss:,} ({100*n_ps_ss/n_all:.1f}%)")
print(f"    PS only                         : {n_ps:,} ({100*n_ps/n_all:.1f}%)")
print(f"    SS only                         : {n_ss:,} ({100*n_ss/n_all:.1f}%)")
print(f"  concomitant / interacting only    : {n_all-n_ps_ss:,}")

# also the same split restricted to the optic-nerve case set
OPTIC = ("'OPTIC NEUROPATHY','OPTIC NEURITIS','OPTIC ATROPHY','OPTIC NERVE DISORDER',"
         "'PAPILLOEDEMA','VISUAL ACUITY REDUCED','BLINDNESS','VISUAL FIELD DEFECT',"
         "'DYSCHROMATOPSIA','SCOTOMA','HEMIANOPIA','CHROMATOPSIA','OCULAR TOXICITY'")
for label, extra in (("all ocular-spectrum optics", ""),
                     ("PS/SS only", " AND UPPER(COALESCE(d.role_cod,'')) IN ('PS','SS')")):
    q = f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
            JOIN dedup_map m ON m.primaryid = d.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE (UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
                OR UPPER(COALESCE(dn.prod_ai,'')) LIKE '%ETHAMBUTOL%'){extra}
              AND d.caseid IN (
                  SELECT DISTINCT r.caseid FROM reac r
                  JOIN dedup_map m2 ON m2.primaryid = r.primaryid
                  WHERE UPPER(r.pt) IN ({OPTIC}))"""
    print(f"optic-nerve-spectrum cases, {label:26s}: {con.execute(q).fetchone()[0]:,}")
con.close()
