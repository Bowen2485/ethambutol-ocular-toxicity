# -*- coding: utf-8 -*-
"""
Correct the case-version folding comparison.

The first attempt compared "drug on the surviving version" against "drug on any
primaryid", which are not the same unit: the second counted primaryids, not cases,
and returned 252,205.  This version computes both sides in CASEID space, which is
the unit the manuscript reports.

Both definitions read the outcome from the surviving version, so every case is
counted exactly once and the only thing that varies is how exposure is established.

Outputs -> results/faers_version_folding.csv
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
DB = ROOT / "data" / "derived" / "faers.sqlite"

OPTIC = ["OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "OPTIC NEURITIS",
         "OPTIC ATROPHY", "OPTIC NERVE DISORDER", "OPTIC NERVE INJURY",
         "PAPILLOEDEMA"]
OCULAR = OPTIC + ["VISUAL ACUITY REDUCED", "BLINDNESS", "VISUAL FIELD DEFECT",
                  "DYSCHROMATOPSIA", "SCOTOMA", "CHROMATOPSIA", "OCULAR TOXICITY",
                  "HEMIANOPIA"]


def q_list(items):
    return ",".join("'" + t + "'" for t in items)


def main() -> int:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=2400)
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-1200000")

    print("[1] outcome flags, read from the surviving version of each case ...")
    con.execute("DROP TABLE IF EXISTS temp.flag")
    con.execute(f"""
        CREATE TEMP TABLE flag AS
        SELECT m.caseid AS caseid,
               MAX(CASE WHEN UPPER(r.pt) IN ({q_list(OPTIC)}) THEN 1 ELSE 0 END)
                   AS optic,
               MAX(CASE WHEN UPPER(r.pt) IN ({q_list(OCULAR)}) THEN 1 ELSE 0 END)
                   AS ocular
        FROM reac r JOIN dedup_map m ON m.primaryid = r.primaryid
        GROUP BY m.caseid
    """)
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_flag ON flag(caseid)")
    n_flag = con.execute("SELECT COUNT(*) FROM flag").fetchone()[0]
    print(f"    {n_flag:,} cases have at least one ocular term")

    # --- definition A: drug must be on the surviving version
    con.execute("DROP TABLE IF EXISTS temp.exp_surv")
    con.execute("""
        CREATE TEMP TABLE exp_surv AS
        SELECT DISTINCT d.caseid AS caseid
        FROM drug d
        JOIN dedup_map m ON m.primaryid = d.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
           OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%'
    """)

    # --- definition B: drug on ANY version, outcome still from the surviving one
    con.execute("DROP TABLE IF EXISTS temp.exp_any")
    con.execute("""
        CREATE TEMP TABLE exp_any AS
        SELECT DISTINCT d.caseid AS caseid
        FROM drug d
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
           OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%'
    """)

    rows = []
    sets = {}
    for label, tbl in (("A. drug on the surviving version", "exp_surv"),
                       ("B. drug on any version of the case", "exp_any")):
        n = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        n_optic = con.execute(f"""
            SELECT COUNT(*) FROM {tbl} e JOIN flag f ON f.caseid = e.caseid
            WHERE f.optic = 1""").fetchone()[0]
        n_oc = con.execute(f"""
            SELECT COUNT(*) FROM {tbl} e JOIN flag f ON f.caseid = e.caseid
            WHERE f.ocular = 1""").fetchone()[0]
        sets[label] = {r[0] for r in con.execute(f"SELECT caseid FROM {tbl}")}
        rows.append({"definition": label, "n_cases": n, "n_optic": n_optic,
                     "pct_optic": round(100 * n_optic / n, 3),
                     "n_ocular": n_oc, "pct_ocular": round(100 * n_oc / n, 3)})
        print(f"\n    {label:38s} cases={n:>7,}  optic={n_optic:>5,} "
              f"({100*n_optic/n:.2f}%)  ocular={n_oc:>5,} ({100*n_oc/n:.2f}%)")

    A, B = rows[0], rows[1]
    only_b = len(sets["B. drug on any version of the case"] -
                 sets["A. drug on the surviving version"])
    only_a = len(sets["A. drug on the surviving version"] -
                 sets["B. drug on any version of the case"])
    print(f"\n    cases added by definition B : {only_b:,}")
    print(f"    cases lost by definition B  : {only_a:,}")

    # how many of the added cases carry the events?
    con.execute("DROP TABLE IF EXISTS temp.onlyb")
    con.execute("""
        CREATE TEMP TABLE onlyb AS
        SELECT e.caseid AS caseid FROM exp_any e
        WHERE NOT EXISTS (SELECT 1 FROM exp_surv s WHERE s.caseid = e.caseid)
    """)
    add_optic = con.execute("""SELECT COUNT(*) FROM onlyb o
        JOIN flag f ON f.caseid = o.caseid WHERE f.optic = 1""").fetchone()[0]
    add_oc = con.execute("""SELECT COUNT(*) FROM onlyb o
        JOIN flag f ON f.caseid = o.caseid WHERE f.ocular = 1""").fetchone()[0]
    print(f"    of those, with an optic-nerve event : {add_optic:,}")
    print(f"    of those, with any ocular event     : {add_oc:,}")

    df = pd.DataFrame(rows)
    df.to_csv(RES / "faers_version_folding.csv", index=False,
              encoding="utf-8-sig")

    print("\n" + "=" * 72)
    print("VERDICT")
    print("=" * 72)
    print(f"  definition A (surviving version) : {A['n_cases']:,} cases, "
          f"{A['n_optic']:,} optic events")
    print(f"  definition B (any version)       : {B['n_cases']:,} cases, "
          f"{B['n_optic']:,} optic events")
    print(f"  the exposure rule changes the optic-event yield by "
          f"{B['n_optic']-A['n_optic']:+,} "
          f"({100*(B['n_optic']-A['n_optic'])/max(A['n_optic'],1):+.1f}%)")
    if abs(B["n_optic"] - A["n_optic"]) / max(A["n_optic"], 1) < 0.10:
        print("  -> the two definitions agree closely on events; the difference is")
        print("     concentrated in cases without the outcomes of interest, so the")
        print("     choice does not materially change the case-level results and can")
        print("     be disclosed in a single sentence")
    else:
        print("  -> the definitions differ materially and the case-level analyses")
        print("     should be regenerated under the union definition")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
