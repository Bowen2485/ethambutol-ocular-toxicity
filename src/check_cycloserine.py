# -*- coding: utf-8 -*-
"""
Check the cycloserine finding before it is allowed to change the manuscript.

The whole-database ranking put CYCLOSERINE at rank 6 for the optic-nerve phenotype
with 53 events across 922 cases, more events than the largest single ethambutol
name entry.  If that is real it contradicts the manuscript's statement that
ethambutol sits an order of magnitude above the other antitubercular drugs, so it
has to be verified directly with the 2x2 machinery used for the main analysis
rather than taken from the ranking output.

Also quantifies how much the ranking was distorted by splitting one drug across
salt and brand names.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
RES = ROOT / "results"
DB = DER / "faers.sqlite"

OPTIC = ("OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
         "OPTIC NERVE DISORDER", "OPTIC NERVE INJURY",
         "TOXIC OPTIC NEUROPATHY", "PAPILLOEDEMA")

# drug-name variants that mean the same molecule
ETHAMBUTOL_ALIASES = ["ETHAMBUTOL", "DEXAMBUTOL", "MYAMBUTOL", "ETAMBUTOL",
                      "ETHAMBUTOL DIHYDROCHLORIDE", "ETHAMBUTOL HYDROCHLORIDE",
                      "ETHAMBUTOL HCL"]


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=1800)
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-1200000")
    return con


def main() -> int:
    con = connect()

    ph = ",".join("'" + t + "'" for t in OPTIC)
    con.execute("DROP TABLE IF EXISTS temp.optic_case")
    con.execute(f"""
        CREATE TEMP TABLE optic_case AS
        SELECT DISTINCT m.caseid AS caseid, 1 AS optic
        FROM reac r JOIN dedup_map m ON m.primaryid = r.primaryid
        WHERE UPPER(r.pt) IN ({ph})
    """)
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_oc ON optic_case(caseid)")
    n_total = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
    n_ev = con.execute("SELECT COUNT(*) FROM optic_case").fetchone()[0]
    print(f"database: {n_total:,} de-duplicated cases, "
          f"{n_ev:,} with an optic-nerve event")

    # ------------------------------------------------- combined ethambutol
    cond = " OR ".join(
        ["UPPER(COALESCE(dn.drugname,'')) = ?"] * len(ETHAMBUTOL_ALIASES) +
        ["UPPER(COALESCE(dn.drugname,'')) LIKE ?"] * 2)
    params = ETHAMBUTOL_ALIASES + ["%ETHAMBUTOL%", "%DEXAMBUTOL%"]
    q = f"""
        SELECT COUNT(DISTINCT m.caseid) AS n_cases,
               COUNT(DISTINCT CASE WHEN o.optic = 1 THEN m.caseid END) AS n_optic
        FROM drugname dn
        JOIN dedup_map m ON m.primaryid = dn.primaryid
        LEFT JOIN optic_case o ON o.caseid = m.caseid
        WHERE {cond}
    """
    n_eth, n_eth_optic = con.execute(q, params).fetchone()

    # ------------------------------------------------------- cycloserine
    q2 = """
        SELECT COUNT(DISTINCT m.caseid) AS n_cases,
               COUNT(DISTINCT CASE WHEN o.optic = 1 THEN m.caseid END) AS n_optic
        FROM drugname dn
        JOIN dedup_map m ON m.primaryid = dn.primaryid
        LEFT JOIN optic_case o ON o.caseid = m.caseid
        WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%CYCLOSERINE%'
           OR UPPER(COALESCE(dn.drugname,'')) LIKE '%SEROMYCIN%'
    """
    n_cyc, n_cyc_optic = con.execute(q2).fetchone()

    # ------------------------------------------------- other antituberculars
    others = {
        "isoniazid": "%ISONIAZID%", "rifampicin": "%RIFAMPICIN%",
        "rifampin": "%RIFAMPIN%", "pyrazinamide": "%PYRAZINAMIDE%",
        "streptomycin": "%STREPTOMYCIN%", "linezolid": "%LINEZOLID%",
        "clofazimine": "%CLOFAZIMINE%", "bedaquiline": "%BEDAQUILINE%",
        "prothionamide": "%PROTHIONAMIDE%", "ethionamide": "%ETHIONAMIDE%",
        "para-aminosalicylic acid": "%AMINOSALICYLIC%",
        "amikacin": "%AMIKACIN%", "capreomycin": "%CAPREOMYCIN%",
    }
    rows = []
    for label, like in [("ethambutol (all names)", None),
                        ("cycloserine", None)] + list(others.items()):
        if label == "ethambutol (all names)":
            a, ae = n_eth, n_eth_optic
        elif label == "cycloserine":
            a, ae = n_cyc, n_cyc_optic
        else:
            r = con.execute("""
                SELECT COUNT(DISTINCT m.caseid),
                       COUNT(DISTINCT CASE WHEN o.optic = 1 THEN m.caseid END)
                FROM drugname dn
                JOIN dedup_map m ON m.primaryid = dn.primaryid
                LEFT JOIN optic_case o ON o.caseid = m.caseid
                WHERE UPPER(COALESCE(dn.drugname,'')) LIKE ?
            """, (like,)).fetchone()
            a, ae = r
        if not a:
            continue
        b = n_eth_optic if label.startswith("ethambutol") else n_ev - ae
        c = a - ae
        d = None
        # standard 2x2 against the whole database
        A, B = ae, n_ev - ae
        C, D = a - ae, n_total - n_ev - (a - ae)
        with np.errstate(divide="ignore", invalid="ignore"):
            ror = (A * D) / (B * C) if B * C else np.inf
            se = np.sqrt(1 / max(A, 0.5) + 1 / max(B, 0.5)
                         + 1 / max(C, 0.5) + 1 / max(D, 0.5))
            lcl = np.exp(np.log(ror) - 1.96 * se) if ror > 0 else np.nan
            ucl = np.exp(np.log(ror) + 1.96 * se) if ror > 0 else np.nan
        prr = (A / (A + C)) / (B / (B + D)) if (A + C) and (B + D) else np.nan
        chi2 = np.nan
        try:
            chi2, _, _ = stats.chi2_contingency([[A, B], [C, D]])
        except Exception:  # noqa: BLE001
            pass
        rows.append({"drug": label, "n_cases": a, "n_optic": ae,
                     "pct_optic": round(100 * ae / a, 2),
                     "ror": round(float(ror), 2) if np.isfinite(ror) else np.inf,
                     "ror_lcl": round(float(lcl), 2), "ror_ucl": round(float(ucl), 2),
                     "prr": round(float(prr), 2),
                     "chi2_yates": round(float(chi2), 1) if np.isfinite(chi2) else None})

    df = pd.DataFrame(rows).sort_values("ror", ascending=False)
    print("\n=== optic-nerve disproportionality, antitubercular drugs "
          "(all name variants merged) ===")
    print(df.to_string(index=False))

    df.to_csv(RES / "faers_antitb_optic_check.csv", index=False,
              encoding="utf-8-sig")
    print(f"\n-> {RES / 'faers_antitb_optic_check.csv'}")

    # how badly did name splitting distort the ranking?
    print("\n=== effect of name splitting on the ethambutol entries ===")
    r = con.execute("""
        SELECT UPPER(TRIM(dn.drugname)) AS drug,
               COUNT(DISTINCT m.caseid) AS n_cases,
               COUNT(DISTINCT CASE WHEN o.optic = 1 THEN m.caseid END) AS n_optic
        FROM drugname dn
        JOIN dedup_map m ON m.primaryid = dn.primaryid
        LEFT JOIN optic_case o ON o.caseid = m.caseid
        WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
           OR UPPER(COALESCE(dn.drugname,'')) LIKE '%DEXAMBUTOL%'
        GROUP BY 1 HAVING COUNT(DISTINCT m.caseid) >= 20
        ORDER BY 2 DESC
    """).fetchall()
    for drug, c_, o_ in r:
        print(f"    {str(drug)[:46]:48s} cases={c_:>7,}  optic={o_:>5,}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
