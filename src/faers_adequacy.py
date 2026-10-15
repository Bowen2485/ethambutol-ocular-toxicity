# -*- coding: utf-8 -*-
"""
Step 11 - Report adequacy of the ethambutol cases.

Disproportionality analysis assumes reports carry enough detail to interpret the
event.  FAERS reports differ enormously in completeness, so this step quantifies
completeness for the ethambutol case set against the whole database and against
the comparator anti-tuberculosis drugs, and reports how much of the optic-nerve
case set survives a minimum-detail restriction.

Implementation note
    Two earlier query shapes did not finish: one query per completeness field,
    and one representative-drug-line CTE built per study group (each requiring a
    fresh scan of the 99-million-row `drug` table).  The final version scans the
    large tables a fixed number of times: `drug` once, `reac` once, and the
    per-case aggregates once.

Outputs -> results/faers_report_adequacy.csv, results/faers_adequacy_summary.csv,
           tables/Table10_adequacy.csv
"""
from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
DB = DERIVED / "faers.sqlite"
CACHE = DERIVED / "adequacy_cache.csv"

DRUGS = {
    "ethambutol": ["ETHAMBUTOL"],
    "isoniazid": ["ISONIAZID"],
    "rifampicin": ["RIFAMPICIN", "RIFAMPIN"],
    "pyrazinamide": ["PYRAZINAMIDE"],
    "streptomycin": ["STREPTOMYCIN"],
    "linezolid": ["LINEZOLID"],
}

DEMO_FIELDS = {"age": "age", "sex": "sex", "weight": "wt",
               "reporter type": "rept_cod", "country": "reporter_country",
               "event date": "event_dt"}
DRUG_FIELDS = {"dose": "dose_amt", "dose unit": "dose_unit", "route": "route",
               "indication": "indication"}
THER_FIELDS = {"therapy start": "start_dt", "therapy duration": "dur"}


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=1800)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1200000")
    return con


def build_detail(con) -> pd.DataFrame:
    """
    One row per de-duplicated case with its completeness indicators.

    The representative drug line is the primary-suspect line where one exists,
    otherwise the secondary-suspect line, otherwise any line.  Drug name, dose,
    route, indication and therapy dates are attached from that line.
    """
    if CACHE.exists():
        print(f"[cache] reusing {CACHE.name}")
        return pd.read_csv(CACHE, encoding="utf-8-sig")
    t0 = time.time()
    print("[build] enumerating registered drug names (single pass) ...")
    # Only the rows whose name matches one of the tokens of interest are needed;
    # a registration table keeps the INNER join small.
    con.execute("DROP TABLE IF EXISTS temp.reg")
    con.execute("""CREATE TEMP TABLE reg (
                       caseid TEXT, primaryid TEXT, drug_seq TEXT, token TEXT,
                       role_cod TEXT, dose_amt TEXT, dose_unit TEXT, route TEXT,
                       indication TEXT)""")
    for drug, tokens in DRUGS.items():
        cond = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
                            "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?"] * len(tokens))
        params: list = []
        for tk in tokens:
            params += [f"%{tk.upper()}%", f"%{tk.upper()}%"]
        q = f"""INSERT INTO reg
                SELECT d.caseid, d.primaryid, d.drug_seq, '{drug}', d.role_cod,
                       d.dose_amt, d.dose_unit, d.route, d.indication
                FROM drug d
                JOIN drugname dn ON dn.primaryid = d.primaryid
                                AND dn.drug_seq = d.drug_seq
                WHERE ({cond})"""
        con.execute(q, params)
        n = con.execute("SELECT COUNT(*) FROM reg WHERE token=?",
                        (drug,)).fetchone()[0]
        print(f"    {drug:14s} {n:>9,} drug lines   ({time.time()-t0:.0f}s)")
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_reg ON reg(primaryid, drug_seq)")
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_reg_case ON reg(caseid)")

    print("[build] building the per-case detail table ...")
    con.execute("DROP TABLE IF EXISTS temp.case_detail")
    con.execute("""
        CREATE TEMP TABLE case_detail AS
        WITH ranked AS (
            SELECT r.caseid AS caseid, r.primaryid AS primaryid,
                   r.drug_seq AS drug_seq, r.token AS token,
                   r.dose_amt AS dose_amt, r.dose_unit AS dose_unit,
                   r.route AS route, r.indication AS indication,
                   ROW_NUMBER() OVER (
                       PARTITION BY r.caseid
                       ORDER BY CASE WHEN UPPER(COALESCE(r.role_cod,''))='PS' THEN 0
                                     WHEN UPPER(COALESCE(r.role_cod,''))='SS' THEN 1
                                     ELSE 2 END,
                                CASE WHEN UPPER(COALESCE(r.token,''))='ethambutol'
                                     THEN 0 ELSE 1 END) AS rn
            FROM reg r
            JOIN dedup_map m ON m.primaryid = r.primaryid
        )
        SELECT c.caseid, c.primaryid, c.drug_seq, c.token,
               c.dose_amt, c.dose_unit, c.route, c.indication,
               dm.age, dm.sex, dm.wt, dm.rept_cod, dm.reporter_country,
               dm.event_dt, t.start_dt, t.dur
        FROM ranked c
        JOIN demo dm ON dm.primaryid = c.primaryid
        LEFT JOIN drug_ther t ON t.primaryid = c.primaryid
                             AND t.drug_seq = c.drug_seq
        WHERE c.rn = 1
    """)
    n = con.execute("SELECT COUNT(*) FROM case_detail").fetchone()[0]
    print(f"    {n:,} cases profiled ({time.time()-t0:.0f}s)")

    df = pd.read_sql_query("SELECT * FROM case_detail", con)
    print(f"    token distribution: "
          f"{df.token.value_counts().to_dict()}")
    # per-case reaction and drug counts
    print("[build] per-case reaction and drug counts ...")
    nr = pd.read_sql_query(
        """SELECT r.caseid AS caseid, COUNT(DISTINCT r.pt) AS n_reac
           FROM reac r JOIN dedup_map m ON m.primaryid = r.primaryid
           WHERE r.caseid IN (SELECT caseid FROM case_detail)
           GROUP BY r.caseid""", con)
    df = df.merge(nr, on="caseid", how="left")
    df["n_reac"] = df["n_reac"].fillna(0)
    df.to_csv(CACHE, index=False, encoding="utf-8-sig")
    print(f"[build] done in {time.time()-t0:.0f}s -> {CACHE.name}")
    return df


def completeness(df: pd.DataFrame, label: str) -> dict:
    n = len(df)
    row: dict = {"group": label, "n_cases": n}
    for name, col in DEMO_FIELDS.items():
        v = int((df[col].astype(str).str.strip().replace("", pd.NA)
                 .notna()).sum()) if col in df.columns else 0
        row[f"{name}_n"] = v
        row[f"{name}_pct"] = round(100.0 * v / max(n, 1), 2)
    for name, col in DRUG_FIELDS.items():
        v = int((df[col].astype(str).str.strip().replace("", pd.NA)
                 .notna()).sum()) if col in df.columns else 0
        row[f"{name}_n"] = v
        row[f"{name}_pct"] = round(100.0 * v / max(n, 1), 2)
    for name, col in THER_FIELDS.items():
        v = int((df[col].astype(str).str.strip().replace("", pd.NA)
                 .notna()).sum()) if col in df.columns else 0
        row[f"{name}_n"] = v
        row[f"{name}_pct"] = round(100.0 * v / max(n, 1), 2)
    row["mean_reactions"] = round(float(df["n_reac"].mean()), 2)
    return row


def main() -> int:
    con = connect()
    n_all = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
    detail = build_detail(con)
    print(f"[base] all FAERS cases = {n_all:,}; profiled = {len(detail):,}")

    rows = []
    # "All FAERS" needs every case, which the registered-name table does not hold,
    # so it is profiled directly from the demographic and drug tables
    t0 = time.time()
    q = """SELECT COUNT(*) AS n,
                  SUM(CASE WHEN COALESCE(age,'')<>'' THEN 1 ELSE 0 END) AS age_n,
                  SUM(CASE WHEN COALESCE(sex,'')<>'' THEN 1 ELSE 0 END) AS sex_n,
                  SUM(CASE WHEN COALESCE(wt,'')<>'' THEN 1 ELSE 0 END) AS weight_n,
                  SUM(CASE WHEN COALESCE(rept_cod,'')<>'' THEN 1 ELSE 0 END) AS rep_n,
                  SUM(CASE WHEN COALESCE(reporter_country,'')<>'' THEN 1 ELSE 0 END) AS ctry_n,
                  SUM(CASE WHEN COALESCE(event_dt,'')<>'' THEN 1 ELSE 0 END) AS ev_n
           FROM demo dm
           JOIN dedup_map m ON m.primaryid = dm.primaryid"""
    n, age_n, sex_n, wt_n, rep_n, ctry_n, ev_n = con.execute(q).fetchone()
    allrow = {"group": "All FAERS", "n_cases": int(n),
              "age_pct": round(100 * age_n / n, 2),
              "sex_pct": round(100 * sex_n / n, 2),
              "weight_pct": round(100 * wt_n / n, 2),
              "reporter type_pct": round(100 * rep_n / n, 2),
              "country_pct": round(100 * ctry_n / n, 2),
              "event date_pct": round(100 * ev_n / n, 2)}
    rows.append(allrow)
    print(f"  All FAERS profiled ({time.time()-t0:.0f}s)")

    for drug in DRUGS:
        # token holds the curated drug label; drug names in FAERS are free text
        # ("ETHAMBUTOL HYDROCHLORIDE 400 mg tablet"), so a substring match is used
        sub = detail[detail.token.astype(str).str.contains(drug, case=False,
                                                           na=False)]
        rows.append(completeness(sub, drug))
        print(f"  {drug:14s} {len(sub):>8,}")

    # how often is ethambutol itself the suspect drug rather than a concomitant?
    tot_sql = """SELECT COUNT(DISTINCT d.caseid) FROM drug d
                 JOIN dedup_map m ON m.primaryid = d.primaryid
                 JOIN drugname dn ON dn.primaryid = d.primaryid
                                 AND dn.drug_seq = d.drug_seq
                 WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
                    OR UPPER(COALESCE(dn.prod_ai,'')) LIKE '%ETHAMBUTOL%'"""
    n_eth_all = con.execute(tot_sql).fetchone()[0]
    n_eth_suspect = con.execute(tot_sql +
                                " AND UPPER(COALESCE(d.role_cod,'')) IN ('PS','SS')"
                                ).fetchone()[0]
    print(f"\n[roles] ethambutol cases overall            : {n_eth_all:,}")
    print(f"[roles]   with ethambutol as suspect (PS/SS): {n_eth_suspect:,} "
          f"({100*n_eth_suspect/max(n_eth_all,1):.1f}%)")
    print(f"[roles]   with ethambutol as concomitant    : "
          f"{n_eth_all - n_eth_suspect:,}")

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "faers_report_adequacy.csv", index=False,
              encoding="utf-8-sig")
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / "Table10_adequacy.csv", index=False, encoding="utf-8-sig")

    show = [c for c in ["group", "n_cases", "age_pct", "sex_pct", "country_pct",
                        "event date_pct", "therapy start_pct",
                        "therapy duration_pct", "dose_pct", "route_pct",
                        "indication_pct", "mean_reactions"] if c in df.columns]
    print("\n=== report completeness (% of cases with the field populated) ===")
    print(df[show].to_string(index=False))

    # minimum-detail restriction within the ethambutol cases
    eth = detail[detail.token.astype(str).str.contains("ethambutol",
                                                       case=False, na=False)]
    optic_terms = {"OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
                   "OPTIC NERVE DISORDER", "PAPILLOEDEMA", "VISUAL ACUITY REDUCED",
                   "BLINDNESS", "VISUAL FIELD DEFECT", "DYSCHROMATOPSIA",
                   "SCOTOMA", "HEMIANOPIA", "CHROMATOPSIA", "OCULAR TOXICITY"}
    ev = pd.read_sql_query(
        """SELECT r.caseid AS caseid, UPPER(r.pt) AS pt FROM reac r
           JOIN dedup_map m ON m.primaryid = r.primaryid""", con)
    optic_ids = set(ev[ev.pt.isin(optic_terms)]["caseid"])
    oc = eth[eth.caseid.isin(optic_ids)].copy()

    def filled(s):
        return s.astype(str).str.strip().replace("", pd.NA).notna()

    n_oc = len(oc)
    n_demo = int((filled(oc.age) & filled(oc.sex)).sum())
    n_start = int(filled(oc.start_dt).sum())
    n_both = int((filled(oc.age) & filled(oc.sex) & filled(oc.start_dt)).sum())
    print("\n=== minimum-detail restriction on the ethambutol ocular cases ===")
    print(f"  ocular (optic-nerve spectrum) cases : {n_oc:,}")
    print(f"    age AND sex                       : {n_demo:,} "
          f"({100*n_demo/max(n_oc,1):.1f}%)")
    print(f"    therapy start date                : {n_start:,} "
          f"({100*n_start/max(n_oc,1):.1f}%)")
    print(f"    both (time-to-onset analysable)   : {n_both:,} "
          f"({100*n_both/max(n_oc,1):.1f}%)")
    summ = pd.DataFrame([{
        "n_ocular_spectrum_cases": n_oc, "with_age_and_sex": n_demo,
        "with_therapy_start": n_start, "with_both": n_both,
        "pct_age_and_sex": round(100 * n_demo / max(n_oc, 1), 1),
        "pct_therapy_start": round(100 * n_start / max(n_oc, 1), 1),
        "pct_both": round(100 * n_both / max(n_oc, 1), 1),
        "n_ethambutol_cases_overall": n_eth_all,
        "n_ethambutol_as_suspect": n_eth_suspect,
        "pct_ethambutol_as_suspect": round(100 * n_eth_suspect /
                                           max(n_eth_all, 1), 1)}])
    summ.to_csv(RESULTS / "faers_adequacy_summary.csv", index=False,
                encoding="utf-8-sig")
    print(f"\n-> {RESULTS / 'faers_report_adequacy.csv'}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
