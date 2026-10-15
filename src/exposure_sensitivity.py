# -*- coding: utf-8 -*-
"""
Compute the two exposure definitions in the same unit, so the footnote is exact.

Earlier comparisons mixed units: one counted caseids, another counted primaryids.  The
manuscript reports caseid-space figures, so both definitions are recomputed here in
caseid space against the whole-database denominator.

  A. strict  - the case is recruited only if ethambutol appears on the surviving
               version of the report (this is what the manuscript reports)
  B. permissive - the case is recruited if ethambutol appears on any version of the
               case; a re-submitted report does not always repeat every drug line, so
               this recovers cases whose later version omits the drug

  For both, events are read from the surviving version so each case is counted once.

Outputs -> results/faers_exposure_sensitivity.csv
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
DB = ROOT / "data" / "derived" / "faers.sqlite"

TERMS = ["OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "OPTIC NEURITIS",
         "OPTIC ATROPHY", "DRY EYE", "EYE PAIN", "CATARACT", "GLAUCOMA"]

# patterns used consistently for both definitions
PATTERNS = ["%ETHAMBUTOL%", "%DEXAMBUTOL%", "%MYAMBUTOL%", "%ETAMBUTOL%"]


def main() -> int:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=2400)
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-1200000")
    N = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
    print(f"de-duplicated database: {N:,} cases (caseid space)\n")

    cond = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ?"] * len(PATTERNS))

    # ---- definition A: drug on the surviving version only
    con.execute("DROP TABLE IF EXISTS temp.expA")
    con.execute(f"""
        CREATE TEMP TABLE expA AS
        SELECT DISTINCT m.caseid AS caseid
        FROM drug d
        JOIN dedup_map m ON m.primaryid = d.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        WHERE {cond}
    """, PATTERNS)

    # ---- definition B: drug on any version of the case
    con.execute("DROP TABLE IF EXISTS temp.expB")
    con.execute(f"""
        CREATE TEMP TABLE expB AS
        SELECT DISTINCT m.caseid AS caseid
        FROM drug d
        JOIN dedup_map m ON m.caseid = d.caseid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        WHERE {cond}
    """, PATTERNS)

    nA = con.execute("SELECT COUNT(*) FROM expA").fetchone()[0]
    nB = con.execute("SELECT COUNT(*) FROM expB").fetchone()[0]
    print(f"  A strict     (drug on surviving version) : {nA:,} cases")
    print(f"  B permissive (drug on any version)       : {nB:,} cases")
    print(f"  added by B                               : {nB - nA:,}\n")

    rows = []
    for term in TERMS:
        con.execute("DROP TABLE IF EXISTS temp.ev")
        con.execute("""
            CREATE TEMP TABLE ev AS
            SELECT DISTINCT m.caseid AS caseid
            FROM reac r JOIN dedup_map m ON m.primaryid = r.primaryid
            WHERE UPPER(r.pt) = ?
        """, (term,))
        n_event = con.execute("SELECT COUNT(*) FROM ev").fetchone()[0]
        for label, tbl in (("A strict", "expA"), ("B permissive", "expB")):
            n_exp, a = con.execute(f"""
                SELECT COUNT(*), SUM(CASE WHEN e2.caseid IS NOT NULL THEN 1 ELSE 0 END)
                FROM {tbl} x LEFT JOIN ev e2 ON e2.caseid = x.caseid
            """).fetchone()
            a = int(a or 0)
            c = n_exp - a
            b = n_event - a
            d = N - n_event - c
            with np.errstate(divide="ignore", invalid="ignore"):
                ror = (a * d) / (b * c) if b * c else np.nan
                se = np.sqrt(1/max(a, .5) + 1/max(b, .5) + 1/max(c, .5) + 1/max(d, .5))
                lcl = np.exp(np.log(ror) - 1.96*se) if ror and ror > 0 else np.nan
                ucl = np.exp(np.log(ror) + 1.96*se) if ror and ror > 0 else np.nan
            try:
                chi2, p, _, _ = stats.chi2_contingency([[a, b], [c, d]], correction=True)
            except Exception:  # noqa: BLE001
                chi2, p = np.nan, np.nan
            rows.append({"term": term, "exposure_definition": label,
                         "n_exposed": n_exp, "a": a, "b": b, "c": c, "d": d,
                         "ror": round(float(ror), 2) if np.isfinite(ror) else np.nan,
                         "ror_lcl": round(float(lcl), 2),
                         "ror_ucl": round(float(ucl), 2),
                         "chi2_yates": round(float(chi2), 1),
                         "p": float(f"{p:.3e}") if np.isfinite(p) else np.nan})
        r1 = rows[-2]
        r2 = rows[-1]
        print(f"  {term:24s} A: a={r1['a']:>4} ROR={r1['ror']:>8.2f}   "
              f"B: a={r2['a']:>4} ROR={r2['ror']:>8.2f}")

    df = pd.DataFrame(rows)
    df["check_sums"] = (df.a + df.b + df.c + df.d == N)
    df.to_csv(RES / "faers_exposure_sensitivity.csv", index=False,
              encoding="utf-8-sig")

    print("\n" + "=" * 74)
    print("VERDICT")
    print("=" * 74)
    on = df[df.term == "OPTIC NEUROPATHY"]
    if len(on) == 2:
        A, B = on.iloc[0], on.iloc[1]
        rel = abs(B.ror - A.ror) / A.ror * 100
        print(f"  optic neuropathy ROR: strict {A.ror:.2f} vs permissive {B.ror:.2f} "
              f"({rel:.1f}% apart)")
    print(f"  all 2x2 tables sum to the database total: {bool(df.check_sums.all())}")
    print(f"  strict definition reproduces the manuscript's a = "
          f"{int(df[(df.term=='OPTIC NEUROPATHY') & (df.exposure_definition=='A strict')].a.iloc[0]):,}")
    print(f"\n-> {RES / 'faers_exposure_sensitivity.csv'}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
