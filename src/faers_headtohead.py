# -*- coding: utf-8 -*-
"""
Head-to-head comparison of ethambutol against the other antitubercular drugs.

Why this replaces the whole-database comparison
    The manuscript originally reported ethambutol's optic-neuropathy ROR against the
    whole FAERS database as 159.21 and described it as an order of magnitude above
    the other antitubercular drugs.  That framing is wrong, and the robustness
    analysis already contained the evidence: restricting the comparator to
    anti-tuberculosis reports collapsed the same figure to 7.64.  The
    whole-database ratio is dominated by the contrast between tuberculosis patients
    and everyone else, not by the contrast between ethambutol and its comparators.

    The correct comparison is within anti-tuberculosis reports: of the patients
    exposed to a given antitubercular drug, what fraction have an optic-nerve event
    recorded, and how does ethambutol compare with each alternative drug.  This
    step computes that directly, term by term, with the same 2x2 machinery used
    elsewhere in the analysis.

A second correction made here
    Drug names in FAERS are free text including the salt and the brand, so a single
    molecule is split across entries (ethambutol appears as ETHAMBUTOL,
    ETHAMBUTOL HYDROCHLORIDE, DEXAMBUTOL and others).  All variants are merged.

Outputs -> results/faers_headtohead_optic.csv, tables/Table14_headtohead.csv
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
RES = ROOT / "results"
TAB = ROOT / "tables"
DB = DER / "faers.sqlite"

# every name variant that denotes the same molecule, merged before comparison
DRUGS: dict[str, list[str]] = {
    "ethambutol": ["%ETHAMBUTOL%", "%DEXAMBUTOL%", "%MYAMBUTOL%", "%ETAMBUTOL%"],
    "cycloserine": ["%CYCLOSERINE%", "%SEROMYCIN%", "%TERIZIDONE%"],
    "isoniazid": ["%ISONIAZID%", "%ISONICOTINYLHYDRAZINE%", "%INH%"],
    "rifampicin": ["%RIFAMPICIN%", "%RIFAMPIN%", "%RIFADIN%", "%RIFAMYCIN%"],
    "pyrazinamide": ["%PYRAZINAMIDE%"],
    "streptomycin": ["%STREPTOMYCIN%"],
    "linezolid": ["%LINEZOLID%", "%ZYWOX%"],
    "clofazimine": ["%CLOFAZIMINE%", "%LAMPRENE%"],
    "bedaquiline": ["%BEDAQUILINE%", "%SIRTURO%"],
    "ethionamide": ["%ETHIONAMIDE%", "%TRECATOR%"],
    "prothionamide": ["%PROTHIONAMIDE%"],
    "capreomycin": ["%CAPREOMYCIN%", "%CAPASTAT%"],
    "amikacin": ["%AMIKACIN%", "%AMIKIN%"],
    "para-aminosalicylic acid": ["%AMINOSALICYLIC%", "%PASER%"],
    "delamanid": ["%DELAMANID%", "%DELTYBA%"],
    "pretomanid": ["%PRETOMANID%"],
    "moxifloxacin": ["%MOXIFLOXACIN%", "%AVELOX%"],
    "levofloxacin": ["%LEVOFLOXACIN%", "%LEVAQUIN%"],
}

# the optic-nerve term panel, plus the two index terms reported separately
OPTIC_PANEL = ["OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "OPTIC NEURITIS",
               "OPTIC ATROPHY", "OPTIC NERVE DISORDER", "OPTIC NERVE INJURY",
               "PAPILLOEDEMA"]


def main() -> int:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=2400)
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-1200000")

    print("[1] classifying optic-nerve events ...")
    ph = ",".join("'" + t + "'" for t in OPTIC_PANEL)
    con.execute("DROP TABLE IF EXISTS temp.optic")
    con.execute(f"""
        CREATE TEMP TABLE optic AS
        SELECT m.caseid AS caseid,
               MAX(CASE WHEN UPPER(r.pt) = 'OPTIC NEUROPATHY' THEN 1 ELSE 0 END) AS on_any,
               MAX(CASE WHEN UPPER(r.pt) = 'TOXIC OPTIC NEUROPATHY' THEN 1 ELSE 0 END) AS on_toxic,
               MAX(CASE WHEN UPPER(r.pt) = 'OPTIC NEURITIS' THEN 1 ELSE 0 END) AS on_neuritis,
               MAX(CASE WHEN UPPER(r.pt) = 'OPTIC ATROPHY' THEN 1 ELSE 0 END) AS on_atrophy,
               1 AS in_panel
        FROM reac r JOIN dedup_map m ON m.primaryid = r.primaryid
        WHERE UPPER(r.pt) IN ({ph})
        GROUP BY m.caseid
    """)
    print(f"    {con.execute('SELECT COUNT(*) FROM optic').fetchone()[0]:,} cases "
          f"with any optic-nerve term")

    print("[2] building the anti-tuberculosis report union ...")
    all_like = [p for v in DRUGS.values() for p in v]
    cond = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ?"] * len(all_like))
    con.execute("DROP TABLE IF EXISTS temp.tb_case")
    con.execute(f"""
        CREATE TEMP TABLE tb_case AS
        SELECT DISTINCT m.caseid AS caseid
        FROM drugname dn JOIN dedup_map m ON m.primaryid = dn.primaryid
        WHERE {cond}
    """, all_like)
    n_tb = con.execute("SELECT COUNT(*) FROM tb_case").fetchone()[0]
    print(f"    {n_tb:,} cases mention any antitubercular drug")

    print("[3] per-drug counts ...")
    rows = []
    for drug, pats in DRUGS.items():
        cond = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ?"] * len(pats))
        q = f"""
            SELECT COUNT(DISTINCT m.caseid) AS n,
                   COUNT(DISTINCT o.caseid) AS n_optic,
                   SUM(CASE WHEN o.on_any = 1 THEN 1 ELSE 0 END) AS on_any,
                   SUM(CASE WHEN o.on_toxic = 1 THEN 1 ELSE 0 END) AS on_toxic,
                   SUM(CASE WHEN o.on_neuritis = 1 THEN 1 ELSE 0 END) AS on_neuritis,
                   SUM(CASE WHEN o.on_atrophy = 1 THEN 1 ELSE 0 END) AS on_atrophy
            FROM drugname dn
            JOIN dedup_map m ON m.primaryid = dn.primaryid
            LEFT JOIN optic o ON o.caseid = m.caseid
            WHERE {cond}
        """
        n, n_optic, on_any, on_toxic, on_neur, on_atr = con.execute(
            q, pats).fetchone()
        if not n or n < 100:
            continue
        rows.append({"drug": drug, "n_cases": int(n), "n_panel": int(n_optic or 0),
                     "pct_panel": round(100 * (n_optic or 0) / n, 3),
                     "n_optic_neuropathy": int(on_any or 0),
                     "pct_optic_neuropathy": round(100 * (on_any or 0) / n, 3),
                     "n_toxic_optic_neuropathy": int(on_toxic or 0),
                     "n_optic_neuritis": int(on_neur or 0),
                     "n_optic_atrophy": int(on_atr or 0)})
        print(f"    {drug:26s} {n:>7,} cases, {int(n_optic or 0):>5,} with an "
              f"optic-nerve term")

    df = pd.DataFrame(rows).sort_values("pct_panel", ascending=False)
    print("\n[4] optic-nerve event fraction within each drug's own reports")
    print(df[["drug", "n_cases", "n_panel", "pct_panel", "pct_optic_neuropathy"]]
          .to_string(index=False))

    # ------------------------------------------- head-to-head vs ethambutol
    print("\n[5] ethambutol versus each other drug (same-population comparison)")
    eth = df[df.drug == "ethambutol"]
    if eth.empty:
        print("    ethambutol row missing")
        con.close()
        return 1
    e = eth.iloc[0]
    a1, n1 = int(e.n_optic_neuropathy), int(e.n_cases)
    out = []
    for _, r in df.iterrows():
        if r.drug == "ethambutol":
            continue
        a2, n2 = int(r.n_optic_neuropathy), int(r.n_cases)
        # 2x2: ethambutol vs this drug, optic neuropathy as outcome
        tab = [[a1, n1 - a1], [a2, n2 - a2]]
        try:
            orr, p = stats.fisher_exact(tab)
        except Exception:  # noqa: BLE001
            orr, p = np.nan, np.nan
        # Woolf interval
        with np.errstate(divide="ignore", invalid="ignore"):
            b1, c2, d2 = n1 - a1, n2 - a2, None
            se = np.sqrt(1 / max(a1, .5) + 1 / max(n1 - a1, .5)
                         + 1 / max(a2, .5) + 1 / max(n2 - a2, .5))
            lcl = np.exp(np.log(orr) - 1.96 * se) if orr and orr > 0 else np.nan
            ucl = np.exp(np.log(orr) + 1.96 * se) if orr and orr > 0 else np.nan
        out.append({"comparator": r.drug,
                    "ethambutol_pct": round(100 * a1 / n1, 3),
                    "comparator_pct": round(100 * a2 / n2, 3),
                    "odds_ratio": round(float(orr), 3) if np.isfinite(orr) else np.nan,
                    "or_lcl": round(float(lcl), 3), "or_ucl": round(float(ucl), 3),
                    "fisher_p": float(f"{p:.3g}") if np.isfinite(p) else np.nan,
                    "n_ethambutol": n1, "n_comparator": n2})
    h2h = pd.DataFrame(out).sort_values("odds_ratio", ascending=False)
    print(h2h.to_string(index=False))
    print("\n  OR > 1 means ethambutol has MORE optic-neuropathy reports than that "
          "drug; OR < 1 means fewer.")

    df.to_csv(RES / "faers_headtohead_optic.csv", index=False,
              encoding="utf-8-sig")
    df.to_csv(TAB / "Table14_headtohead.csv", index=False, encoding="utf-8-sig")
    h2h.to_csv(RES / "faers_headtohead_pairs.csv", index=False,
               encoding="utf-8-sig")
    print(f"\n-> {RES / 'faers_headtohead_optic.csv'}")
    print(f"-> {RES / 'faers_headtohead_pairs.csv'}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
