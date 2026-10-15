# -*- coding: utf-8 -*-
"""
Where does ethambutol sit among all drugs for ocular reporting risk?

The manuscript currently compares ethambutol with five antitubercular drugs, which
answers "is it the worst of its class" but not "how does it rank overall".  This
step computes the ocular reporting odds ratio for every drug in the de-duplicated
database and reports ethambutol's rank, both on the optic-nerve phenotype and on a
non-specific ocular phenotype.

Method notes
    Exposure is taken from the drug-name index (98.9 million rows) grouped by name
    and matched to de-duplicated cases.  Very large groups are kept; groups with
    fewer than MIN_CASES cases are dropped because their ratios are unstable and
    they dominate any naive top-N list.  A drug is included only if at least
    MIN_EVENTS of its cases report the phenotype, so the ranking is not driven by
    single-case signals.

Outputs -> results/faers_drug_ranking.csv, tables/Table12_drug_ranking.csv
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

MIN_CASES = 100        # a drug needs this many de-duplicated cases to be ranked
MIN_EVENTS = 5         # and this many events for the ratio to be stable
PHENOTYPES = {
    "optic": ("OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
              "OPTIC NERVE DISORDER", "OPTIC NERVE INJURY",
              "TOXIC OPTIC NEUROPATHY", "PAPILLOEDEMA"),
    "ocular_nonspecific": ("DRY EYE", "EYE PAIN", "EYE IRRITATION", "CATARACT",
                           "CONJUNCTIVITIS", "OCULAR HYPERAEMIA",
                           "VISION BLURRED", "PHOTOPHOBIA", "GLAUCOMA"),
}


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=3600)
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-1500000")
    return con


def main() -> int:
    t0 = time.time()
    con = connect()

    # ---------------------------------------------------- phenotype case sets
    print("[1] building the phenotype case sets ...")
    con.execute("DROP TABLE IF EXISTS temp.case_ph")
    cols = ", ".join(
        f"MAX(CASE WHEN UPPER(r.pt) IN ({','.join(chr(39)+t+chr(39) for t in terms)})"
        f" THEN 1 ELSE 0 END) AS {k}" for k, terms in PHENOTYPES.items())
    con.execute(f"""
        CREATE TEMP TABLE case_ph AS
        SELECT m.caseid AS caseid, {cols}
        FROM reac r
        JOIN dedup_map m ON m.primaryid = r.primaryid
        GROUP BY m.caseid
    """)
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_cph ON case_ph(caseid)")
    n_case = con.execute("SELECT COUNT(*) FROM case_ph").fetchone()[0]
    print(f"    {n_case:,} cases classified ({time.time()-t0:.0f}s)")

    # ------------------------------------------- per-drug, per-phenotype counts
    print("[2] aggregating drug names to case level (this is the slow step) ...")
    con.execute("DROP TABLE IF EXISTS temp.drug_case")
    con.execute("""
        CREATE TEMP TABLE drug_case AS
        SELECT UPPER(TRIM(dn.drugname)) AS drug, m.caseid AS caseid,
               MAX(COALESCE(cp.optic, 0))            AS optic,
               MAX(COALESCE(cp.ocular_nonspecific,0)) AS nonspec
        FROM drugname dn
        JOIN dedup_map m ON m.primaryid = dn.primaryid
        JOIN case_ph cp ON cp.caseid = m.caseid
        WHERE COALESCE(dn.drugname, '') <> ''
        GROUP BY UPPER(TRIM(dn.drugname)), m.caseid
    """)
    n_dc = con.execute("SELECT COUNT(*) FROM drug_case").fetchone()[0]
    print(f"    {n_dc:,} drug-case pairs ({time.time()-t0:.0f}s)")
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_dc ON drug_case(drug)")

    print("[3] computing per-drug totals ...")
    agg = pd.read_sql_query("""
        SELECT drug,
               COUNT(*)                AS n_cases,
               SUM(optic)              AS n_optic,
               SUM(nonspec)            AS n_nonspec
        FROM drug_case
        WHERE LENGTH(drug) BETWEEN 3 AND 60
        GROUP BY drug
        HAVING COUNT(*) >= ?
    """, con, params=(MIN_CASES,))
    print(f"    {len(agg):,} drugs meet the >= {MIN_CASES} case threshold "
          f"({time.time()-t0:.0f}s)")

    con.execute("DROP TABLE IF EXISTS temp.drug_case")
    con.execute("DROP TABLE IF EXISTS temp.case_ph")
    con.close()

    # ------------------------------------------------------------- metrics
    totals = agg[["n_cases", "n_optic", "n_nonspec"]].sum()
    N = int(totals.n_cases)          # drug-case pairs, used as the denominator base
    print(f"[4] computing ROR for {len(agg):,} drugs over {N:,} drug-case pairs ...")

    def metrics(ev_col: str) -> pd.DataFrame:
        a = agg[ev_col].astype(float)
        d = agg["n_cases"].astype(float) - a
        # comparator = all other drug-case pairs
        b = float(agg[ev_col].sum() - a.sum()) * np.ones(len(agg)) if False else None
        b = (agg[ev_col].sum() - a)
        c = (agg["n_cases"].sum() - agg[ev_col].sum()) - d
        out = pd.DataFrame({"drug": agg.drug, "n_cases": agg.n_cases.astype(int),
                            "n_events": agg[ev_col].astype(int)})
        with np.errstate(divide="ignore", invalid="ignore"):
            out["ror"] = (a * c) / (b * d)
            se = np.sqrt(1 / np.maximum(a, 0.5) + 1 / np.maximum(b, 0.5)
                         + 1 / np.maximum(c, 0.5) + 1 / np.maximum(d, 0.5))
            out["ror_lcl"] = np.exp(np.log(out["ror"]) - 1.96 * se)
            out["ror_ucl"] = np.exp(np.log(out["ror"]) + 1.96 * se)
        return out[(out.n_events >= MIN_EVENTS) & np.isfinite(out.ror)]

    optic = metrics("n_optic")
    nonspec = metrics("n_nonspec")

    for name, df in (("optic-nerve", optic), ("non-specific ocular", nonspec)):
        df = df.sort_values("ror", ascending=False).reset_index(drop=True)
        df["rank"] = np.arange(1, len(df) + 1)
        eth = df[df.drug.str.contains("ETHAMBUTOL", na=False)]
        print(f"\n=== {name} phenotype: {len(df):,} rankable drugs ===")
        if not eth.empty:
            r = eth.iloc[0]
            print(f"  ETHAMBUTOL rank {int(r['rank'])}/{len(df)}  "
                  f"ROR={r.ror:.2f} ({r.ror_lcl:.2f}-{r.ror_ucl:.2f})  "
                  f"n_cases={int(r.n_cases):,}  n_events={int(r.n_events):,}")
        print(f"  top 12:")
        for _, r in df.head(12).iterrows():
            mark = " <== ethambutol" if "ETHAMBUTOL" in str(r.drug) else ""
            print(f"    {int(r['rank']):>4}. {str(r.drug)[:38]:40s} "
                  f"ROR={r.ror:>8.2f}  events={int(r.n_events):>5,}"
                  f"  cases={int(r.n_cases):>7,}{mark}")
        df.to_csv(RES / f"faers_drug_ranking_{name.split('-')[0]}.csv",
                  index=False, encoding="utf-8-sig")
        if name == "optic-nerve":
            df.to_csv(TAB / "Table12_drug_ranking.csv", index=False,
                      encoding="utf-8-sig")

    print(f"\n[done] {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
