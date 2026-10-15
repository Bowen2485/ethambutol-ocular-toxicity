# -*- coding: utf-8 -*-
"""
Step 5 - Case-level analysis of the ethambutol reports: time to ocular onset,
multivariable predictors and reporting trends.

Complements the disproportionality analysis by answering three questions it
cannot:
  1. When after starting ethambutol do ocular events occur?          (time to onset)
  2. Which report-level characteristics accompany an ocular event?   (logistic model)
  3. How has ocular reporting for ethambutol changed over time?       (annual trends)

Sources inside data/derived/faers.sqlite
    drugname   (primaryid, drug_seq, drugname, prod_ai)   <- FAERS DRUG table
    drug_ther  (primaryid, drug_seq, start_dt, end_dt, dur, dur_cod) <- FAERS THER
    demo       case identity, dates, demographics, country
    reac       MedDRA PT + outcome
    dedup_map  de-duplicated case -> representative primaryid

Outputs -> results/faers_tto.csv, faers_logistic.csv, faers_trend.csv,
           faers_exposure_summary.csv, data/derived/faers_tto_cases.csv
"""
from __future__ import annotations

import argparse
import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)
DB = DERIVED / "faers.sqlite"

OCULAR_TERMS = [
    "OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY", "OPTIC NERVE DISORDER",
    "OPTIC DISC DISORDER", "PAPILLOEDEMA", "BLINDNESS", "BLINDNESS UNILATERAL",
    "VISUAL IMPAIRMENT", "VISUAL ACUITY REDUCED", "VISION BLURRED",
    "VISUAL FIELD DEFECT", "SCOTOMA", "HEMIANOPIA", "DIPLOPIA", "PHOTOPHOBIA",
    "COLOUR VISION DEFECT", "DYSCHROMATOPSIA", "CHROMATOPSIA", "NYSTAGMUS",
    "AMBLYOPIA", "SUDDEN VISUAL LOSS", "OCULAR TOXICITY", "RETINOPATHY",
    "MACULOPATHY", "RETINAL DISORDER", "RETINAL HAEMORRHAGE", "RETINAL OEDEMA",
    "CYSTOID MACULAR OEDEMA", "MACULAR DEGENERATION", "RETINAL DETACHMENT",
    "UVEITIS", "IRIDOCYCLITIS", "VITRITIS", "VITREOUS FLOATERS", "PTOSIS",
    "DIPLOPIA", "OCULOGYRIC CRISIS", "PUPILLARY REFLEX IMPAIRED",
    "VISUAL DISTURBANCE", "EYE PAIN", "EYE IRRITATION", "DRY EYE",
    "OCULAR HYPERAEMIA", "LACRIMATION INCREASED", "CONJUNCTIVITIS",
    "CATARACT", "GLAUCOMA", "EYELID OEDEMA", "PERIORBITAL OEDEMA",
    "KERATITIS", "CORNEAL DISORDER", "BLINDNESS TRANSIENT", "PHOTOPSIA",
    "METAMORPHOPSIA", "EYE HAEMORRHAGE", "EYE PRURITUS", "EYE SWELLING",
    "OCULAR DISCOMFORT", "EYE MOVEMENT DISORDER", "PAPILLARY OEDEMA",
]

# the optic-nerve / ganglion-cell axonopathy core of the phenotype
OPTIC_TERMS = [
    "OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY", "OPTIC NERVE DISORDER",
    "OPTIC NERVE INJURY", "OPTIC DISC DISORDER", "PAPILLOEDEMA", "BLINDNESS",
    "BLINDNESS UNILATERAL", "BLINDNESS BILATERAL", "SUDDEN VISUAL LOSS",
    "VISUAL FIELD DEFECT", "SCOTOMA", "DYSCHROMATOPSIA", "CHROMATOPSIA",
    "HEMIANOPIA", "OCULAR TOXICITY",
]


def connect() -> sqlite3.Connection:
    if not DB.exists():
        raise SystemExit(f"{DB} not found")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=900)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1000000")
    return con


def load_cases(con: sqlite3.Connection) -> pd.DataFrame:
    """One row per de-duplicated ethambutol case."""
    q = """
    WITH eth AS (
        SELECT DISTINCT d.caseid, d.primaryid, d.drug_seq, d.role_cod
        FROM drug d
        JOIN drugname dn ON dn.primaryid = d.primaryid AND dn.drug_seq = d.drug_seq
        WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
           OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%'
    )
    SELECT e.caseid AS caseid, e.primaryid AS primaryid, e.drug_seq AS drug_seq,
           e.role_cod AS role_cod,
           dm.fda_dt AS fda_dt, dm.event_dt AS event_dt, dm.rept_cod AS reporter,
           dm.reporter_country AS reporter_country,
           dm.occr_country AS occr_country, dm.age AS age, dm.age_cod AS age_cod,
           dm.sex AS sex, dm.wt AS wt,
           dn.drugname AS drugname, dn.prod_ai AS prod_ai,
           dt.start_dt AS start_dt, dt.end_dt AS end_dt,
           dt.dur AS dur, dt.dur_cod AS dur_cod,
           d.route AS route, d.dose_amt AS dose_amt, d.dose_unit AS dose_unit,
           d.dose_vbm AS dose_vbm
    FROM eth e
    JOIN dedup_map m ON e.primaryid = m.primaryid
    JOIN demo dm ON dm.primaryid = e.primaryid
    LEFT JOIN drug d ON d.primaryid = e.primaryid AND d.drug_seq = e.drug_seq
    LEFT JOIN drugname dn ON dn.primaryid = e.primaryid AND dn.drug_seq = e.drug_seq
    LEFT JOIN drug_ther dt ON dt.primaryid = e.primaryid AND dt.drug_seq = e.drug_seq
    """
    df = pd.read_sql_query(q, con)
    print(f"[cases] {len(df)} drug lines across ethambutol cases")
    rank = {"PS": 0, "SS": 1, "C": 2, "I": 3}
    df["role_rank"] = df.role_cod.fillna("").str.upper().map(rank).fillna(4)
    # prefer the line that has therapy dates, then the suspect line
    df["has_dates"] = df.start_dt.notna() & df.event_dt.notna()
    df = (df.sort_values(["caseid", "has_dates", "role_rank"],
                         ascending=[True, False, True])
            .drop_duplicates("caseid", keep="first"))
    print(f"[cases] {len(df)} de-duplicated ethambutol cases")
    return df


def attach_events(con: sqlite3.Connection, cases: pd.DataFrame) -> pd.DataFrame:
    q = """SELECT r.caseid AS caseid, UPPER(r.pt) AS pt, r.outcome AS outcome
           FROM reac r JOIN dedup_map m ON r.primaryid = m.primaryid
           WHERE r.pt IS NOT NULL AND r.pt <> ''"""
    ev = pd.read_sql_query(q, con)
    ev["is_ocular"] = ev.pt.isin(set(OCULAR_TERMS))
    ev["is_optic"] = ev.pt.isin(set(OPTIC_TERMS))
    agg = ev.groupby("caseid").agg(
        n_reactions=("pt", "size"),
        n_ocular=("is_ocular", "sum"),
        n_optic=("is_optic", "sum"),
        reactions=("pt", lambda s: "; ".join(sorted(set(s))[:12]))).reset_index()
    out = cases.merge(agg, on="caseid", how="left")
    for c in ("n_reactions", "n_ocular", "n_optic"):
        out[c] = out[c].fillna(0).astype(int)
    out["any_ocular"] = (out.n_ocular > 0).astype(int)
    out["any_optic"] = (out.n_optic > 0).astype(int)
    print(f"[events] ocular={int(out.any_ocular.sum())} "
          f"optic-nerve={int(out.any_optic.sum())} of {len(out)} cases")
    return out


def to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s.astype(str).str.strip(), format="%Y%m%d", errors="coerce")


def duration_days(v, cod) -> float:
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


def tto_table(cases: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = cases.copy()
    df["start"] = to_dt(df.start_dt)
    df["event"] = to_dt(df.event_dt)
    df["tto_days"] = (df.event - df.start).dt.days
    valid = df[(df.tto_days.notna()) & (df.tto_days >= 0) & (df.tto_days <= 3650)].copy()
    print(f"[tto] {len(valid)} cases with a computable time to onset "
          f"(of {len(df)} ethambutol cases)")
    rows = []
    for label, mask in [("All ethambutol reports", valid.tto_days.notna()),
                        ("Ocular event", valid.any_ocular == 1),
                        ("Optic-nerve event", valid.any_optic == 1),
                        ("No ocular event", valid.any_ocular == 0)]:
        sub = valid[mask]
        if sub.empty:
            continue
        q = sub.tto_days.quantile([0.25, 0.5, 0.75, 0.9])
        rows.append({
            "group": label, "n": int(len(sub)),
            "median_days": float(sub.tto_days.median()),
            "q25_days": float(q.loc[0.25]), "q75_days": float(q.loc[0.75]),
            "p90_days": float(q.loc[0.9]), "mean_days": float(sub.tto_days.mean()),
            "min_days": int(sub.tto_days.min()), "max_days": int(sub.tto_days.max()),
        })
    return pd.DataFrame(rows), valid


def logistic(cases: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    import statsmodels.api as sm
    df = cases.copy()
    df["age_y"] = pd.to_numeric(df.age, errors="coerce")
    cod = df.age_cod.fillna("").str.upper()
    df.loc[cod.str.startswith("DEC"), "age_y"] *= 10
    df.loc[cod.str.startswith(("MONTH", "MON")), "age_y"] /= 12.0
    df.loc[cod.str.startswith(("WK", "WEEK")), "age_y"] /= 52.0
    df.loc[cod.str.startswith(("D", "DAY")), "age_y"] /= 365.0
    df.loc[(df.age_y < 0) | (df.age_y > 110), "age_y"] = np.nan
    df["age_missing"] = df.age_y.isna().astype(int)
    df["age_y"] = df.age_y.fillna(df.age_y.median())

    g = df.sex.astype(str).str.upper().str[0]
    df["female"] = np.where(g == "F", 1.0, np.where(g == "M", 0.0, np.nan))
    df["female"] = df.female.fillna(0.5)

    df["year"] = pd.to_numeric(df.fda_dt.astype(str).str[:4], errors="coerce")
    df["year"] = df.year.fillna(df.year.median())

    ctry = df.reporter_country.fillna("").str.upper()
    asia = {"IN", "JP", "KR", "CN", "TW", "TH", "ID", "PH", "MY", "VN", "SG", "PK",
            "BD", "NP", "LK", "HK"}
    eur = {"FR", "DE", "IT", "ES", "GB", "NL", "BE", "SE", "CH", "AT", "DK", "NO",
           "FI", "IE", "PT", "PL", "GR", "CZ", "HU", "RO", "TR", "IL"}
    amer = {"US", "CA", "MX", "BR", "AR", "CO", "CL", "PE"}
    df["region_asia"] = ctry.isin(asia).astype(int)
    df["region_eur"] = ctry.isin(eur).astype(int)
    df["region_amer"] = ctry.isin(amer).astype(int)
    df["region_other"] = ((df.region_asia + df.region_eur + df.region_amer) == 0).astype(int)

    df["n_reactions_log"] = np.log1p(df.n_reactions)
    df["multi_drug"] = (df.role_rank >= 0).astype(int)

    y = df["any_ocular"].astype(int).values
    cols = ["age_y", "female", "year", "n_reactions_log",
            "region_asia", "region_eur", "region_other"]
    X = sm.add_constant(df[cols].astype(float).fillna(0.0))
    res = {}
    try:
        model = sm.Logit(y, X).fit(disp=False, maxiter=300)
    except Exception as exc:  # noqa: BLE001
        print(f"[logit] fit failed: {exc}")
        return pd.DataFrame(), res
    params, conf = model.params, model.conf_int()
    rows = []
    pretty = {"age_y": "Age (per year)", "female": "Female sex",
              "year": "Report year (per year)",
              "n_reactions_log": "Number of reactions (log)",
              "region_asia": "Reporter region: Asia",
              "region_eur": "Reporter region: Europe",
              "region_other": "Reporter region: other"}
    for name in cols:
        b = float(params[name])
        lo, hi = float(conf.loc[name, 0]), float(conf.loc[name, 1])
        rows.append({"predictor": pretty.get(name, name), "beta": b,
                     "se": float(model.bse[name]), "p": float(model.pvalues[name]),
                     "or": math.exp(b), "or_lcl": math.exp(lo), "or_ucl": math.exp(hi)})
    res["n"] = int(len(df))
    res["n_events"] = int(y.sum())
    res["pseudo_r2"] = float(getattr(model, "prsquared", np.nan))
    res["llr_p"] = float(getattr(model, "llr_pvalue", np.nan))
    print(f"[logit] n={len(df)} events={int(y.sum())} "
          f"pseudo-R2={res['pseudo_r2']:.4f} LLR p={res['llr_p']:.3g}")
    return pd.DataFrame(rows), res


def trend_table(cases: pd.DataFrame, grand: int) -> pd.DataFrame:
    df = cases.copy()
    df["year"] = pd.to_numeric(df.fda_dt.astype(str).str[:4], errors="coerce")
    d = df[df.year.between(2004, 2026)]
    rows = []
    for y, g in d.groupby("year"):
        rows.append({
            "year": int(y), "n_reports": int(len(g)),
            "n_ocular": int(g.any_ocular.sum()),
            "n_optic": int(g.any_optic.sum()),
            "pct_ocular": 100 * float(g.any_ocular.mean()),
            "pct_optic": 100 * float(g.any_optic.mean()),
        })
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-trend", action="store_true")
    args = ap.parse_args()

    con = connect()
    cases = attach_events(con, load_cases(con))
    grand = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
    cases.to_csv(RESULTS / "faers_cases_profile.csv", index=False,
                 encoding="utf-8-sig")
    print(f"[base] FAERS de-duplicated total = {grand:,}")

    # --------------------------------------------------------------- 1. TTO
    tto, valid = tto_table(cases)
    if not tto.empty:
        tto.to_csv(RESULTS / "faers_tto.csv", index=False, encoding="utf-8-sig")
        print("\n=== time from ethambutol start to event (days) ===")
        print(tto.to_string(index=False))
        keep = ["caseid", "any_ocular", "any_optic", "tto_days", "age", "age_cod",
                "sex", "reporter_country", "fda_dt", "role_cod", "dur", "dur_cod"]
        valid[[c for c in keep if c in valid.columns]].to_csv(
            DERIVED / "faers_tto_cases.csv", index=False, encoding="utf-8-sig")

    # -------------------------------------------------- 2. exposure summary
    d = cases.copy()
    d["dur_days"] = [duration_days(v, c) for v, c in zip(d.dur, d.dur_cod)]
    rows = []
    for label, sub in [("all ethambutol cases", d),
                       ("ocular cases", d[d.any_ocular == 1]),
                       ("optic-nerve cases", d[d.any_optic == 1])]:
        ok = sub.dur_days.dropna()
        if len(ok):
            rows.append({"group": label, "metric": "recorded therapy duration (days)",
                         "n": int(len(ok)), "median": float(ok.median()),
                         "q25": float(ok.quantile(0.25)),
                         "q75": float(ok.quantile(0.75))})
        dose = pd.to_numeric(sub.dose_amt, errors="coerce")
        dose = dose[dose > 0]
        if len(dose):
            rows.append({"group": label, "metric": "recorded dose amount",
                         "n": int(len(dose)), "median": float(dose.median()),
                         "q25": float(dose.quantile(0.25)),
                         "q75": float(dose.quantile(0.75))})
    ex = pd.DataFrame(rows)
    if not ex.empty:
        ex.to_csv(RESULTS / "faers_exposure_summary.csv", index=False,
                  encoding="utf-8-sig")
        print("\n=== recorded exposure characteristics ===")
        print(ex.to_string(index=False))

    # --------------------------------------------------- 3. logistic model
    log, meta = logistic(cases)
    if not log.empty:
        log.to_csv(RESULTS / "faers_logistic.csv", index=False, encoding="utf-8-sig")
        print(f"\n=== multivariable logistic regression "
              f"(outcome: any ocular AE; n={meta.get('n')}, "
              f"events={meta.get('n_events')}, "
              f"pseudo-R2={meta.get('pseudo_r2', float('nan')):.4f}) ===")
        print(log.to_string(index=False))

    # ------------------------------------------------------- 4. time trend
    if not args.no_trend:
        tr = trend_table(cases, grand)
        tr.to_csv(RESULTS / "faers_trend.csv", index=False, encoding="utf-8-sig")
        print("\n=== ethambutol reports and ocular share by year ===")
        print(tr.to_string(index=False))

    # ---------------------------------------------------------- case profile
    print("\n=== case profile ===")
    print(f"  ethambutol cases              : {len(cases):,}")
    print(f"  with >=1 ocular term          : {int(cases.any_ocular.sum()):,} "
          f"({100*cases.any_ocular.mean():.2f}%)")
    print(f"  with >=1 optic-nerve term     : {int(cases.any_optic.sum()):,} "
          f"({100*cases.any_optic.mean():.2f}%)")
    for label, col in [("age", "age"), ("sex", "sex")]:
        pass
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
