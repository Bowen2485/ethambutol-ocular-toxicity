# -*- coding: utf-8 -*-
"""
Within-class disproportionality: ethambutol against the antitubercular class.

Why this is needed
    The manuscript's Figure 3 and its comparator sentence used the whole FAERS
    database as the denominator for every drug.  For antitubercular drugs that
    denominator is dominated by non-tuberculosis reports, so the resulting ratio
    mostly measures tuberculosis patients against everyone else.  It is not a
    drug-versus-drug comparison.  The within-class analysis restricts the
    denominator to reports mentioning any antitubercular drug, which is the
    comparison the manuscript actually needs.

Method
    For each drug and each ocular term:
        a = cases with the drug and the term
        b = cases with the drug and not the term
        c = cases with another antitubercular drug and the term
        d = cases with another antitubercular drug and not the term
    ROR = a*d / (b*c) with a Woolf log-normal confidence interval, and a
    Benjamini-Hochberg adjustment across the terms tested for that drug.

Outputs -> results/faers_withinclass_signals.csv,
           tables/Table2_withinclass.csv, tables/Table14_headtohead.csv
"""
from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
RES = ROOT / "results"
TAB = ROOT / "tables"
DB = DER / "faers.sqlite"

DRUGS: dict[str, list[str]] = {
    "ethambutol": ["%ETHAMBUTOL%", "%DEXAMBUTOL%", "%MYAMBUTOL%", "%ETAMBUTOL%"],
    "cycloserine": ["%CYCLOSERINE%", "%SEROMYCIN%", "%TERIZIDONE%"],
    "isoniazid": ["%ISONIAZID%", "%ISONICOTINYLHYDRAZINE%"],
    "rifampicin": ["%RIFAMPICIN%", "%RIFAMPIN%", "%RIFADIN%"],
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

# the strongest terms plus the informative negative controls
TERMS = ["OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "OPTIC NEURITIS",
         "OPTIC ATROPHY", "OPTIC NERVE DISORDER", "PAPILLOEDEMA",
         "DYSCHROMATOPSIA", "VISUAL FIELD DEFECT", "VISUAL ACUITY REDUCED",
         "BLINDNESS", "OCULAR TOXICITY",
         "CATARACT", "DRY EYE", "EYE PAIN", "GLAUCOMA", "CONJUNCTIVITIS",
         "VISION BLURRED", "OCULAR HYPERAEMIA"]


def main() -> int:
    t0 = time.time()
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=2400)
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-1200000")

    print("[1] restricting to anti-tuberculosis reports ...")
    all_like = [p for v in DRUGS.values() for p in v]
    cond = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ?"] * len(all_like))
    con.execute("DROP TABLE IF EXISTS temp.tb_case")
    con.execute(f"""
        CREATE TEMP TABLE tb_case AS
        SELECT DISTINCT m.caseid AS caseid
        FROM drugname dn JOIN dedup_map m ON m.primaryid = dn.primaryid
        WHERE {cond}
    """, all_like)
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_tb ON tb_case(caseid)")
    n_tb = con.execute("SELECT COUNT(*) FROM tb_case").fetchone()[0]
    print(f"    {n_tb:,} anti-tuberculosis reports ({time.time()-t0:.0f}s)")

    print("[2] per-term case flags inside that population ...")
    ph = ",".join("'" + t + "'" for t in TERMS)
    con.execute("DROP TABLE IF EXISTS temp.term_case")
    cols = ", ".join(
        f"MAX(CASE WHEN UPPER(r.pt) = '{t}' THEN 1 ELSE 0 END) AS t{i}"
        for i, t in enumerate(TERMS))
    con.execute(f"""
        CREATE TEMP TABLE term_case AS
        SELECT m.caseid AS caseid, {cols}
        FROM reac r
        JOIN dedup_map m ON m.primaryid = r.primaryid
        JOIN tb_case tb ON tb.caseid = m.caseid
        WHERE UPPER(r.pt) IN ({ph})
        GROUP BY m.caseid
    """)
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_tc ON term_case(caseid)")
    print(f"    {con.execute('SELECT COUNT(*) FROM term_case').fetchone()[0]:,} "
          f"cases carry at least one of the terms ({time.time()-t0:.0f}s)")

    print("[3] per-drug case sets ...")
    drug_cases: dict[str, set[str]] = {}
    for drug, pats in DRUGS.items():
        cond = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ?"] * len(pats))
        ids = {r[0] for r in con.execute(f"""
            SELECT DISTINCT m.caseid FROM drugname dn
            JOIN dedup_map m ON m.primaryid = dn.primaryid
            JOIN tb_case tb ON tb.caseid = m.caseid
            WHERE {cond}
        """, pats)}
        drug_cases[drug] = ids
        print(f"    {drug:26s} {len(ids):>7,} cases")

    # term flags per case, as a dict for fast lookup
    print("[4] loading term flags ...")
    flags: dict[str, int] = {}
    q = f"SELECT caseid, {', '.join('t'+str(i) for i in range(len(TERMS)))} "\
        f"FROM term_case"
    for row in con.execute(q):
        cid = row[0]
        v = 0
        for i, x in enumerate(row[1:]):
            if x:
                v |= (1 << i)
        flags[cid] = v
    con.close()
    print(f"    {len(flags):,} cases have at least one flagged term")

    print("[5] computing within-class RORs ...")
    rows = []
    for drug, ids in drug_cases.items():
        n_drug = len(ids)
        if n_drug < 100:
            continue
        others = set()
        for other, oids in drug_cases.items():
            if other != drug:
                others |= oids
        n_other = len(others)
        for i, term in enumerate(TERMS):
            mask = 1 << i
            a = sum(1 for c in ids if flags.get(c, 0) & mask)
            c_ev = sum(1 for c in others if flags.get(c, 0) & mask)
            if a + c_ev == 0:
                continue
            b = n_drug - a
            d = n_other - c_ev
            with np.errstate(divide="ignore", invalid="ignore"):
                ror = (a * d) / (b * c_ev) if b * c_ev else np.inf
                se = np.sqrt(1 / max(a, .5) + 1 / max(b, .5)
                             + 1 / max(c_ev, .5) + 1 / max(d, .5))
                lcl = np.exp(np.log(ror) - 1.96 * se) if ror > 0 else np.nan
                ucl = np.exp(np.log(ror) + 1.96 * se) if ror > 0 else np.nan
            # Yates chi-square
            try:
                chi2, p, _, _ = stats.chi2_contingency([[a, b], [c_ev, d]],
                                                       correction=True)
            except Exception:  # noqa: BLE001
                chi2, p = np.nan, np.nan
            rows.append({"drug": drug, "term": term, "a": a, "b": b,
                         "c": c_ev, "d": d,
                         "pct_drug": round(100 * a / n_drug, 4),
                         "pct_other": round(100 * c_ev / max(n_other, 1), 4),
                         "ror": round(float(ror), 3) if np.isfinite(ror) else np.inf,
                         "ror_lcl": round(float(lcl), 3),
                         "ror_ucl": round(float(ucl), 3),
                         "chi2_yates": round(float(chi2), 2),
                         "p": float(f"{p:.3e}") if np.isfinite(p) else np.nan,
                         "n_drug_cases": n_drug})
    df = pd.DataFrame(rows)

    # Benjamini-Hochberg within each drug
    df["q_bh"] = np.nan
    for drug, g in df.groupby("drug"):
        pv = g.p.values.astype(float)
        ok = np.isfinite(pv)
        q = np.full(len(g), np.nan)
        if ok.sum():
            order = np.argsort(pv[ok])
            m = ok.sum()
            ranked = pv[ok][order] * m / (np.arange(m) + 1)
            ranked = np.minimum.accumulate(ranked[::-1])[::-1]
            tmp = np.empty(m)
            tmp[order] = np.clip(ranked, 0, 1)
            q[ok] = tmp
        df.loc[g.index, "q_bh"] = q
    df["signal"] = ((df.ror_lcl > 1) & (df.a >= 3) & (df.q_bh < 0.05))

    df.to_csv(RES / "faers_withinclass_signals.csv", index=False,
              encoding="utf-8-sig")

    # ---------------------------------------------------- ethambutol's ranking
    print("\n=== within-class ROR for the optic-nerve terms, by drug ===")
    grid = df[df.term.isin(["OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY",
                            "OPTIC NEURITIS", "OPTIC ATROPHY",
                            "PAPILLOEDEMA"])]
    piv = grid.pivot_table(index="drug", columns="term", values="ror")
    piv = piv.sort_values("OPTIC NEUROPATHY", ascending=False)
    print(piv.round(2).to_string())

    eth = df[df.drug == "ethambutol"].set_index("term")
    print("\n=== ethambutol, within-class, by term ===")
    show = eth.loc[[t for t in TERMS if t in eth.index],
                   ["a", "pct_drug", "pct_other", "ror", "ror_lcl", "ror_ucl",
                    "q_bh", "signal"]]
    print(show.to_string())

    # where does ethambutol rank among the drugs on optic neuropathy?
    on = df[df.term == "OPTIC NEUROPATHY"].sort_values("ror", ascending=False) \
        .reset_index(drop=True)
    on["rank"] = np.arange(1, len(on) + 1)
    print("\n=== ethambutol's rank on 'optic neuropathy' within the class ===")
    for _, r in on.iterrows():
        mark = "  <== ethambutol" if r.drug == "ethambutol" else ""
        print(f"    {int(r['rank']):>2}. {r.drug:26s} ROR={r.ror:>8.2f} "
              f"({r.ror_lcl:>6.2f}-{r.ror_ucl:>7.2f})  a={int(r.a):>4}{mark}")

    on.to_csv(TAB / "Table2_withinclass.csv", index=False, encoding="utf-8-sig")
    grid.to_csv(TAB / "Table14_headtohead.csv", index=False, encoding="utf-8-sig")
    print(f"\n[done] {time.time()-t0:.0f}s")
    print(f"-> {RES / 'faers_withinclass_signals.csv'}")
    print(f"-> {TAB / 'Table2_withinclass.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
