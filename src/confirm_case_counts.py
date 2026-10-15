# -*- coding: utf-8 -*-
"""
Confirm the exact definition of the two case counts before they are footnoted.

  13,804 - the main pharmacovigilance analysis: de-duplicated cases in which
           ethambutol appears on a drug line (any role)
  15,573 - the within-class comparison: the same restriction but computed over the
           anti-tuberculosis report union

If the two differ, the footnote has to say why; if they are the same quantity
measured slightly differently the footnote must not invent a distinction.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"

ETH = ("%ETHAMBUTOL%", "%DEXAMBUTOL%", "%MYAMBUTOL%", "%ETAMBUTOL%")


def main() -> int:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=1800)
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-1200000")

    cond = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ?"] * len(ETH))

    print("=" * 72)
    print("A. Cases where ethambutol appears on any drug line")
    print("=" * 72)
    n_any = con.execute(f"""
        SELECT COUNT(DISTINCT m.caseid) FROM drugname dn
        JOIN dedup_map m ON m.primaryid = dn.primaryid
        WHERE {cond}
    """, ETH).fetchone()[0]
    print(f"  by drug NAME only                     : {n_any:,}")

    n_sub = con.execute(f"""
        SELECT COUNT(DISTINCT m.caseid) FROM drugname dn
        JOIN dedup_map m ON m.primaryid = dn.primaryid
        WHERE ({cond})
          AND UPPER(COALESCE(dn.drugname,'')) <> ''
    """, ETH).fetchone()[0]
    print(f"  (identical, names are non-empty)      : {n_sub:,}")

    print()
    print("=" * 72)
    print("B. The main-analysis count: ethambutol on a drug line, product name")
    print("   OR active substance")
    print("=" * 72)
    n_main = con.execute(f"""
        SELECT COUNT(DISTINCT m.caseid) FROM drug d
        JOIN dedup_map m ON m.primaryid = d.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
           OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%'
    """).fetchone()[0]
    print(f"  drugname OR prod_ai, ETHAMBUTOL only  : {n_main:,}")

    print()
    print("=" * 72)
    print("C. Difference between the two definitions")
    print("=" * 72)
    print(f"  {n_any:,} (name-based union, includes DEXAMBUTOL and MYAMBUTOL)")
    print(f"  {n_main:,} (substance-indexed, ETHAMBUTOL substring)")
    print(f"  difference: {n_any - n_main:,}")

    # which extra names drive the difference?
    rows = con.execute(f"""
        SELECT UPPER(TRIM(dn.drugname)) AS drug,
               COUNT(DISTINCT m.caseid) AS n
        FROM drugname dn JOIN dedup_map m ON m.primaryid = dn.primaryid
        WHERE {cond}
          AND UPPER(COALESCE(dn.drugname,'')) NOT LIKE '%ETHAMBUTOL%'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 12
    """, ETH).fetchall()
    print("\n  names matched by the union but not by the 'ETHAMBUTOL' substring:")
    tot = 0
    for d, n in rows:
        print(f"      {str(d)[:52]:54s} {n:>6,}")
        tot += n
    if not rows:
        print("      (none)")

    # how many cases have ethambutol as a suspect drug?
    print()
    print("=" * 72)
    print("D. Drug-role breakdown for the main-analysis case set")
    print("=" * 72)
    for label, extra in (("primary suspect (PS)", "AND UPPER(COALESCE(d.role_cod,''))='PS'"),
                         ("PS or secondary suspect", "AND UPPER(COALESCE(d.role_cod,'')) IN ('PS','SS')"),
                         ("concomitant or interacting",
                          "AND UPPER(COALESCE(d.role_cod,'')) NOT IN ('PS','SS')")):
        q = f"""
            SELECT COUNT(DISTINCT m.caseid) FROM drug d
            JOIN dedup_map m ON m.primaryid = d.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE (UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
                OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%')
              {extra}
        """
        print(f"  {label:30s} {con.execute(q).fetchone()[0]:>8,}")

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
