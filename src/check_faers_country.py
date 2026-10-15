# -*- coding: utf-8 -*-
"""
Check whether the FAERS country field can support a rate-per-treated-patient analysis.

A tuberculosis burden denominator can only be joined to the reports if each report
carries a country and a year.  The receipt year is already used in the temporal
validation; the country is what would link to WHO tuberculosis estimates.  If
reporter_country is mostly empty, the whole idea fails at the first step and there is no
point building it.

This reports the fill rate for the de-duplicated database, for the ethambutol cases
specifically, and the distribution across the countries that carry most of the reports.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-2000000")

print("=" * 88)
print("1. Country field fill rate")
print("=" * 88)
q_total = """SELECT COUNT(*) FROM demo d
             JOIN dedup_map m ON d.primaryid = m.primaryid"""
n_total = con.execute(q_total).fetchone()[0]

q_filled = """SELECT COUNT(*) FROM demo d
              JOIN dedup_map m ON d.primaryid = m.primaryid
              WHERE d.reporter_country IS NOT NULL
                AND TRIM(d.reporter_country) <> ''"""
n_filled = con.execute(q_filled).fetchone()[0]
print(f"  de-duplicated cases            : {n_total:,}")
print(f"  with a reporter country        : {n_filled:,}  "
      f"({100*n_filled/max(n_total,1):.1f}%)")

# the same for the ethambutol cases, using the pipeline's substance patterns
MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")
pats = ["%ETHAMBUTOL%", "%MYAMBUTOL%", "%DEXAMBUTOL%", "%ETAMBUTOL%"]
cond = " OR ".join([MATCH] * len(pats))
params = [p for pat in pats for p in (pat, pat)]
q_emb = f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE {cond}"""
n_emb = con.execute(q_emb, params).fetchone()[0]
q_emb_c = f"""SELECT COUNT(DISTINCT d.caseid) FROM drug d
              JOIN dedup_map m ON d.primaryid = m.primaryid
              JOIN drugname dn ON dn.primaryid = d.primaryid
                              AND dn.drug_seq = d.drug_seq
              JOIN demo dm ON dm.primaryid = m.primaryid
              WHERE {cond}
                AND dm.reporter_country IS NOT NULL
                AND TRIM(dm.reporter_country) <> ''"""
n_emb_c = con.execute(q_emb_c, params).fetchone()[0]
print(f"  ethambutol cases               : {n_emb:,}")
print(f"  with a reporter country        : {n_emb_c:,}  "
      f"({100*n_emb_c/max(n_emb,1):.1f}%)")

print()
print("=" * 88)
print("2. Where the ethambutol reports come from")
print("=" * 88)
q_by_country = f"""SELECT UPPER(TRIM(dm.reporter_country)) AS cc,
                          COUNT(DISTINCT d.caseid) AS n
                   FROM drug d
                   JOIN dedup_map m ON d.primaryid = m.primaryid
                   JOIN drugname dn ON dn.primaryid = d.primaryid
                                   AND dn.drug_seq = d.drug_seq
                   JOIN demo dm ON dm.primaryid = m.primaryid
                   WHERE {cond}
                     AND dm.reporter_country IS NOT NULL
                     AND TRIM(dm.reporter_country) <> ''
                   GROUP BY cc ORDER BY n DESC LIMIT 25"""
rows = con.execute(q_by_country, params).fetchall()
print(f"  {'country':8s} {'ethambutol cases':>18s}")
for cc, n in rows:
    print(f"  {str(cc):8s} {n:>18,}")
print(f"  distinct countries: "
      f"{con.execute(f'''SELECT COUNT(DISTINCT UPPER(TRIM(dm.reporter_country)))
                        FROM drug d
                        JOIN dedup_map m ON d.primaryid = m.primaryid
                        JOIN drugname dn ON dn.primaryid = d.primaryid
                                        AND dn.drug_seq = d.drug_seq
                        JOIN demo dm ON dm.primaryid = m.primaryid
                        WHERE {cond}''', params).fetchone()[0]}")

print()
print("=" * 88)
print("3. Optic-neuropathy events within those reports, by country")
print("=" * 88)
q_optic = f"""SELECT UPPER(TRIM(dm.reporter_country)) AS cc,
                     COUNT(DISTINCT CASE WHEN UPPER(r.pt) = 'OPTIC NEUROPATHY'
                                         THEN d.caseid END) AS n_optic,
                     COUNT(DISTINCT d.caseid) AS n_emb
              FROM drug d
              JOIN dedup_map m ON d.primaryid = m.primaryid
              JOIN drugname dn ON dn.primaryid = d.primaryid
                              AND dn.drug_seq = d.drug_seq
              JOIN demo dm ON dm.primaryid = m.primaryid
              LEFT JOIN reac r ON r.primaryid = d.primaryid
              WHERE {cond}
                AND dm.reporter_country IS NOT NULL
                AND TRIM(dm.reporter_country) <> ''
              GROUP BY cc HAVING n_emb >= 50 ORDER BY n_emb DESC"""
for cc, n_optic, n_emb in con.execute(q_optic, params).fetchall():
    pct = 100 * n_optic / max(n_emb, 1)
    print(f"  {str(cc):8s} {n_emb:>7,} ethambutol cases  {n_optic:>5} optic  "
          f"({pct:>5.2f}%)")

con.close()
print()
print("=" * 88)
print("Reading")
print("=" * 88)
print("""  If the country field is well populated for the ethambutol cases, a tuberculosis
  burden denominator can be attached and the analysis can report reports per estimated
  treated patient rather than a proportion of reports.  If it is largely empty, the
  analysis cannot be built and the paper keeps its current framing.""")
