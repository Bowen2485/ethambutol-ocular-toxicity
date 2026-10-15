# -*- coding: utf-8 -*-
"""
Step 5 - Case-level analysis of the ethambutol reports: time to ocular onset and
multivariable predictors.

Two questions the disproportionality analysis cannot answer:
  1. When do ocular events occur after starting ethambutol?  (time-to-onset, TTO)
  2. Which report-level characteristics accompany an ocular event?  (logistic
     regression on the de-duplicated ethambutol case set)

TTO is computed as (EVENT_DT - therapy start) in days, restricted to reports with
both dates present, a non-negative interval and a plausible upper bound
(<= 3650 days).  The regression uses the same case set as the signal analysis,
with the ocular composite as the dependent variable; results are reported as
adjusted odds ratios with 95% confidence intervals and a complete-case account.

Outputs -> results/faers_tto.csv, results/faers_logistic.csv, results/faers_cases_profile.csv
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
DB = DERIVED / "faers.sqlite"

OCULAR_TERMS = [
    "OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY", "OPTIC NERVE DISORDER",
    "BLINDNESS", "VISUAL IMPAIRMENT", "VISUAL ACUITY REDUCED", "VISION BLURRED",
    "VISUAL FIELD DEFECT", "SCOTOMA", "COLOUR VISION DEFECT", "DYSCHROMATOPSIA",
    "CHROMATOPSIA", "DIPLOPIA", "PHOTOPHOBIA", "NYSTAGMUS", "BLINDNESS UNILATERAL",
    "BLINDNESS BILATERAL", "RETINOPATHY", "MACULOPATHY", "RETINAL DISORDER",
    "OPTIC DISC DISORDER", "PAPILLOEDEMA", "VISUAL DISTURBANCE",
    "SUDDEN VISUAL LOSS", "RETINAL NERVE FIBRE LAYER THINNING", "DRY EYE",
    "EYE PAIN", "OCULAR HYPERAEMIA", "LACRIMATION INCREASED", "CATARACT",
    "GLAUCOMA", "UVEITIS", "VISUAL EVOKED POTENTIAL ABNORMAL",
]
OPTIC_TERMS = ["OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
               "OPTIC NERVE DISORDER", "OPTIC DISC DISORDER", "PAPILLOEDEMA",
               "BLINDNESS", "BLINDNESS UNILATERAL", "BLINDNESS BILATERAL",
               "SUDDEN VISUAL LOSS", "VISUAL FIELD DEFECT", "SCOTOMA",
               "COLOUR VISION DEFECT", "DYSCHROMATOPSIA"]


def connect() -> sqlite3.Connection:
    if not DB.exists():
        raise SystemExit(f"{DB} not found")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=600)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-600000")
    return con


def ensure_dedup(con) -> None:
    have = con.execute("SELECT name FROM sqlite_master WHERE type='table' "
                       "AND name='dedup_map'").fetchone()
    if have:
        return
    print("[dedup] reconstructing dedup_map ...")
    con.executescript("""
        CREATE TABLE dedup_map AS
        SELECT caseid, primaryid FROM (
            SELECT caseid, primaryid,
                   ROW_NUMBER() OVER (PARTITION BY caseid
                       ORDER BY COALESCE(fda_dt,'') DESC,
                                COALESCE(primaryid,'') DESC) AS rn
            FROM demo WHERE caseid IS NOT NULL AND caseid <> ''
        ) WHERE rn = 1;
        CREATE INDEX IF NOT EXISTS ix_dm_case ON dedup_map(caseid);
        CREATE INDEX IF NOT EXISTS ix_dm_pid  ON dedup_map(primaryid);
    """)


def load_cases(con) -> pd.DataFrame:
    q = """
    SELECT d.caseid AS caseid, d.primaryid AS primaryid, d.fda_dt AS fda_dt,
           dm.age AS age, dm.age_cod AS age_cod, dm.sex AS sex, dm.wt AS wt,
           dm.rept_cod AS reporter, dm.reporter_country AS reporter_country,
           dm.occr_country AS occr_country, dm.event_dt AS event_dt,
           d.role_cod AS role_cod, d.start_dt AS start_dt, d.end_dt AS end_dt,
           d.dur AS dur, d.dur_cod AS dur_cod, d.route AS route,
           d.dose_amt AS dose_amt, d.dose_unit AS dose_unit,
           d.dose_vbm AS dose_vbm, d.indication AS indication
    FROM drug d
    JOIN dedup_map m ON d.primaryid = m.primaryid
    LEFT JOIN demo dm ON dm.primaryid = d.primaryid
    WHERE UPPER(COALESCE(d.substance,'')) LIKE '%ETHAMBUTOL%'
       OR UPPER(COALESCE(d.medicinalproduct,'')) LIKE '%ETHAMBUTOL%'
    """
    df = pd.read_sql_query(q, con)
    print(f"[cases] {len(df)} drug lines for ethambutol")
    # one row per case: prefer the primary-suspect line
    rank = {"PS": 0, "SS": 1, "C": 2, "I": 3}
    df["role_rank"] = df.role_cod.fillna("").str.upper().map(rank).fillna(4)
    df = (df.sort_values(["caseid", "role_rank"])
            .drop_duplicates("caseid", keep="first"))
    print(f"[cases] {len(df)} de-duplicated cases")
    return df


def attach_events(con, cases: pd.DataFrame) -> pd.DataFrame:
    q = """SELECT r.caseid AS caseid, UPPER(r.pt) AS pt, r.outcome AS outcome
           FROM reac r JOIN dedup_map m ON r.primaryid = m.primaryid
           WHERE r.pt IS NOT NULL AND r.pt <> ''"""
    ev = pd.read_sql_query(q, con)
    ocular = set(OCULAR_TERMS)
    optic = set(OPTIC_TERMS)
    ev["is_ocular"] = ev.pt.isin(ocular)
    ev["is_optic"] = ev.pt.isin(optic)
    agg = ev.groupby("caseid").agg(
        n_reactions=("pt", "size"),
        n_ocular=("is_ocular", "sum"),
        n_optic=("is_optic", "sum"),
        reactions=("pt", lambda s: "; ".join(sorted(set(s))[:14]))).reset_index()
    out = cases.merge(agg, on="caseid", how="left")
    out["n_reactions"] = out.n_reactions.fillna(0).astype(int)
    out["n_ocular"] = out.n_ocular.fillna(0).astype(int)
    out["n_optic"] = out.n_optic.fillna(0).astype(int)
    out["any_ocular"] = (out.n_ocular > 0).astype(int)
    out["any_optic"] = (out.n_optic > 0).astype(int)
    print(f"[events] {out.any_ocular.sum()} cases with an ocular term; "
          f"{out.any_optic.sum()} with an optic-nerve term")
    return out


def parse_date(s: pd.Series) -> pd.Series:
    d = pd.to_datetime(s.astype(str).str.strip(), format="%Y%m%d", errors="coerce")
    return d


def tto_table(cases: pd.DataFrame) -> pd.DataFrame:
    df = cases.copy()
    df["start"] = parse_date(df.start_dt)
    df["event"] = parse_date(df.event_dt)
    df["tto_days"] = (df.event - df.start).dt.days
    d = df[(df.tto_days.notna()) & (df.tto_days >= 0) & (df.tto_days <= 3650)]
    print(f"[tto] {len(d)} cases with a computable time to onset "
          f"({len(df)} ethambutol cases total)")
    rows = []
    for label, mask in [("All ethambutol reports", d.tto_days.notna()),
                        ("Ocular event", d.any_ocular == 1),
                        ("Optic-nerve event", d.any_optic == 1),
                        ("No ocular event", d.any_ocular == 0)]:
        sub = d[mask]
        if sub.empty:
            continue
        q = sub.tto_days.quantile([0.25, 0.5, 0.75, 0.9]).to_dict()
        rows.append({
            "group": label, "n": int(len(sub)),
            "median_days": float(sub.tto_days.median()),
            "q25_days": float(q.get(0.25, np.nan)),
            "q75_days": float(q.get(0.75, np.nan)),
            "p90_days": float(q.get(0.9, np.nan)),
            "mean_days": float(sub.tto_days.mean()),
            "min_days": int(sub.tto_days.min()), "max_days": int(sub.tto_days.max()),
        })
    return pd.DataFrame(rows), d


def logistic(cases: pd.DataFrame) -> pd.DataFrame:
    import statsmodels.api as sm
    df = cases.copy()
    df["age_y"] = pd.to_numeric(df.age, errors="coerce")
    # FAERS age codes: DEC=decade, YR=years, MONTHS, WKS, DAYS
    cod = df.age_cod.fillna("").str.upper()
    df.loc[cod.str.startswith("DEC"), "age_y"] *= 10
    df.loc[cod.str.startswith(("MONTH", "MON")), "age_y"] /= 12.0
    df.loc[cod.str.startswith(("WK", "WEEK")), "age_y"] /= 52.0
    df.loc[cod.str.startswith(("D", "DAY")), "age_y"] /= 365.0
    df.loc[(df.age_y < 0) | (df.age_y > 110), "age_y"] = np.nan
    df["female"] = (df.sex.astype(str).str.upper().str[0] == "F").astype(int)
    df.loc[~df.sex.astype(str).str.upper().str[0].isin(["F", "M"]), "female"] = np.nan
    df["year"] = pd.to_numeric(df.fda_dt.astype(str).str[:4], errors="coerce")
    df["region_asia"] = df.reporter_country.fillna("").str.upper().isin(
        ["IN", "JP", "KR", "CN", "TW", "TH", "ID", "PH", "MY", "VN", "SG", "PK",
         "BD", "NP", "LK"]).astype(int)
    df["region_eur"] = df.reporter_country.fillna("").str.upper().isin(
        ["FR", "DE", "IT", "ES", "GB", "NL", "BE", "SE", "CH", "AT", "DK", "NO",
         "FI", "IE", "PT", "PL", "GR", "CZ", "HU", "RO"]).astype(int)
    df["region_us"] = df.reporter_country.fillna("").str.upper().isin(
        ["US", "CA", "MX"]).astype(int)
    df["n_reactions_log"] = np.log1p(df.n_reactions)
    df["age_missing"] = df.age_y.isna().astype(int)
    df["age_y"] = df.age_y.fillna(df.age_y.median())
    df["female"] = df.female.fillna(df.female.mode().iloc[0] if len(df.female.mode()) else 0)
    df["year"] = df.year.fillna(df.year.median())

    y = df["any_ocular"].astype(int).values
    cols = ["age_y", "female", "year", "n_reactions_log", "region_asia",
            "region_eur"]
    X = sm.add_constant(df[cols].astype(float).fillna(0.0))
    try:
        model = sm.Logit(y, X).fit(disp=False, maxiter=200)
    except Exception as exc:  # noqa: BLE001
        print(f"[logit] fitting failed: {exc}")
        return pd.DataFrame()
    params, conf = model.params, model.conf_int()
    rows = []
    for name in X.columns:
        if name == "const":
            continue
        b = float(params[name])
        lo, hi = float(conf.loc[name, 0]), float(conf.loc[name, 1])
        rows.append({
            "predictor": name, "beta": b, "se": float(model.bse[name]),
            "p": float(model.pvalues[name]),
            "or": math.exp(b), "or_lcl": math.exp(lo), "or_ucl": math.exp(hi),
        })
    res = pd.DataFrame(rows)
    res.attrs["n"] = int(len(df))
    res.attrs["pseudo_r2"] = float(getattr(model, "prsquared", np.nan))
    print(f"[logit] n={len(df)} pseudo-R2={res.attrs['pseudo_r2']:.4f}")
    return res


def exposure_summary(cases: pd.DataFrame) -> pd.DataFrame:
    rows = []

    def _dur_days(v, cod):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return np.nan
        c = str(cod or "").upper()
        if c.startswith(("D", "DAY")):
            return v
        if c.startswith(("WK", "WEEK")):
            return v * 7
        if c.startswith(("MON", "MONTH")):
            return v * 30.44
        if c.startswith(("YR", "YEAR")):
            return v * 365.25
        return np.nan

    d = cases[(cases.any_ocular == 1) | (cases.any_optic == 1)].copy()
    d["dur_days"] = [_dur_days(v, c) for v, c in zip(d.dur, d.dur_cod)]
    ok = d.dur_days.dropna()
    if len(ok):
        rows.append({"metric": "therapy duration (days), ocular cases", "n": int(len(ok)),
                     "median": float(ok.median()), "q25": float(ok.quantile(0.25)),
                     "q75": float(ok.quantile(0.75))})
    dose = pd.to_numeric(cases.dose_amt, errors="coerce")
    ok2 = dose[dose.notna() & (dose > 0)]
    if len(ok2):
        rows.append({"metric": "reported daily dose (mg)", "n": int(len(ok2)),
                     "median": float(ok2.median()), "q25": float(ok2.quantile(0.25)),
                     "q75": float(ok2.quantile(0.75))})
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases-csv", default="")
    args = ap.parse_args()

    con = connect()
    ensure_dedup(con)
    if args.cases_csv and Path(args.cases_csv).exists():
        cases = pd.read_csv(args.cases_csv, encoding="utf-8-sig")
        cases = attach_events(con, cases)
    else:
        cases = attach_events(con, load_cases(con))

    cases.to_csv(RESULTS / "faers_cases_profile.csv", index=False,
                 encoding="utf-8-sig")

    tto, tto_cases = tto_table(cases)
    if not tto.empty:
        tto.to_csv(RESULTS / "faers_tto.csv", index=False, encoding="utf-8-sig")
        print("\n=== time to ocular onset ===")
        print(tto.to_string(index=False))
        # expose the per-case TTO for the figure
        keep = ["caseid", "any_ocular", "any_optic", "tto_days", "age_y"
                if "age_y" in tto_cases.columns else "age"]
        tto_cases[["caseid", "any_ocular", "any_optic", "tto_days", "age",
                   "sex", "reporter_country"]].to_csv(
            DERIVED / "faers_tto_cases.csv", index=False, encoding="utf-8-sig")

    prof = exposure_summary(cases)
    if not prof.empty:
        print("\n=== exposure characteristics ===")
        print(prof.to_string(index=False))
        prof.to_csv(RESULTS / "faers_exposure_summary.csv", index=False,
                    encoding="utf-8-sig")

    log = logistic(cases)
    if not log.empty:
        log.to_csv(RESULTS / "faers_logistic.csv", index=False, encoding="utf-8-sig")
        print("\n=== multivariable logistic regression (outcome: any ocular AE) ===")
        print(f"    n = {log.attrs.get('n')}, "
              f"pseudo-R2 = {log.attrs.get('pseudo_r2', float('nan')):.4f}")
        print(log.to_string(index=False))

    print("\n=== case profile ===")
    n = len(cases)
    print(f"  ethambutol cases                 : {n:,}")
    print(f"  with >=1 ocular term             : {int(cases.any_ocular.sum()):,} "
          f"({100 * cases.any_ocular.mean():.2f}%)")
    print(f"  with >=1 optic-nerve term        : {int(cases.any_optic.sum()):,} "
          f"({100 * cases.any_optic.mean():.2f}%)")
    for lab, col in [("median age (y)", "age"), ("female %", "sex")]:
        pass
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
