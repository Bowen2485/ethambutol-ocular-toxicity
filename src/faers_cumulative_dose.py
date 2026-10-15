# -*- coding: utf-8 -*-
"""
Cumulative-dose analysis of ethambutol optic neuropathy.

The hypothesis being tested
    The time-to-onset result (median 125 days for optic-nerve events versus 30 days
    for non-ocular events in the same reports) points to a cumulative toxic
    axonopathy rather than an acute reaction.  A cumulative mechanism makes a
    specific prediction: the risk should track the total amount of drug the patient
    has received - daily dose x days of exposure - rather than the daily dose alone.
    The daily-dose analysis already found no gradient, so this step tests the
    alternative directly.

Definitions
    interval_days  = event_dt - therapy start_dt, the observed exposure window
    daily_dose_mg  = the reported absolute dose, converted to mg
    cum_dose_g     = daily_dose_mg x interval_days / 1000

Handling of unusable records, all reported rather than silently dropped
    * partial dates (YYYYMM, YYYY) are completed with the first day of the period
      and the record is flagged, because the resulting interval is uncertain by up
      to a month or a year
    * records where event_dt < start_dt are dropped as internal inconsistencies
    * intervals longer than MAX_INTERVAL_DAYS are capped, and the number capped is
      reported, because values of decades are data errors rather than exposures

Outputs -> results/faers_cumulative_dose.csv, tables/Table13_cumulative_dose.csv
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
RES = ROOT / "results"
TAB = ROOT / "tables"
DB = DER / "faers.sqlite"

MAX_INTERVAL_DAYS = 1825     # 5 years; longer values are treated as data errors
ABSOLUTE = {"MG": 1.0, "G": 1000.0, "GM": 1000.0, "MG.": 1.0, "MILLIGRAM": 1.0,
            "GRAM": 1000.0, "GR": 1000.0, "MCG": 0.001, "UG": 0.001}


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=1800)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1200000")
    return con


def to_mg(amt, unit) -> float | None:
    if amt is None or unit is None:
        return None
    a = re.sub(r"[^0-9.]", "", str(amt))
    if not a:
        return None
    try:
        v = float(a)
    except ValueError:
        return None
    u = str(unit).strip().upper()
    if v <= 0 or u not in ABSOLUTE:
        return None
    return v * ABSOLUTE[u]


def parse_date(s) -> tuple[pd.Timestamp | None, bool]:
    """Return (timestamp, is_partial). Partial dates take the first day."""
    if s is None:
        return None, False
    d = re.sub(r"\D", "", str(s))
    if len(d) == 8:
        try:
            return pd.Timestamp(int(d[:4]), int(d[4:6]), int(d[6:8])), False
        except ValueError:
            return None, False
    if len(d) == 6:
        try:
            return pd.Timestamp(int(d[:4]), int(d[4:6]), 1), True
        except ValueError:
            return None, False
    if len(d) == 4:
        try:
            return pd.Timestamp(int(d), 1, 1), True
        except ValueError:
            return None, False
    return None, False


def main() -> int:
    con = connect()
    print("[1] pulling ethambutol records with dose and therapy dates ...")
    con.execute("DROP TABLE IF EXISTS temp.eth")
    con.execute("""
        CREATE TEMP TABLE eth AS
        SELECT DISTINCT d.primaryid AS primaryid, d.caseid AS caseid,
               d.drug_seq AS drug_seq, d.dose_amt AS amt, d.dose_unit AS unit
        FROM drug d
        JOIN dedup_map m ON m.primaryid = d.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid AND dn.drug_seq = d.drug_seq
        WHERE (UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
            OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%')
    """)
    q = """
        SELECT e.caseid AS caseid, e.primaryid AS primaryid,
               e.amt AS amt, e.unit AS unit,
               t.start_dt AS start_dt, t.end_dt AS end_dt,
               x.event_dt AS event_dt
        FROM eth e
        JOIN drug_ther t ON t.primaryid = e.primaryid
                        AND t.drug_seq = e.drug_seq
        JOIN demo x ON x.primaryid = e.primaryid
        WHERE COALESCE(e.amt,'') <> ''
          AND LENGTH(COALESCE(e.unit,'')) >= 1
          AND LENGTH(COALESCE(t.start_dt,'')) >= 6
          AND LENGTH(COALESCE(x.event_dt,'')) >= 6
    """
    df = pd.read_sql_query(q, con)
    con.close()
    print(f"    {len(df):,} drug lines with all three fields")

    print("[2] parsing doses and dates ...")
    df["mg"] = [to_mg(a, u) for a, u in zip(df.amt, df.unit)]
    parsed_start = [parse_date(s) for s in df.start_dt]
    parsed_event = [parse_date(s) for s in df.event_dt]
    df["start"] = [p[0] for p in parsed_start]
    df["start_partial"] = [p[1] for p in parsed_start]
    df["event"] = [p[0] for p in parsed_event]
    df["event_partial"] = [p[1] for p in parsed_event]
    df = df[df.mg.notna() & df.start.notna() & df.event.notna()].copy()
    print(f"    {len(df):,} usable records after parsing")

    df["interval_days"] = (df.event - df.start).dt.days
    n_neg = int((df.interval_days < 0).sum())
    df = df[df.interval_days >= 0].copy()
    print(f"    dropped {n_neg:,} records with event date before therapy start "
          f"({100*n_neg/max(len(df)+n_neg,1):.1f}%)")

    n_cap = int((df.interval_days > MAX_INTERVAL_DAYS).sum())
    df["interval_capped"] = df.interval_days.clip(upper=MAX_INTERVAL_DAYS)
    print(f"    capped {n_cap:,} intervals longer than {MAX_INTERVAL_DAYS} days")

    df["cum_dose_g"] = df.mg * df.interval_capped / 1000.0
    # one representative line per case: the highest cumulative exposure recorded
    df = df.sort_values("cum_dose_g", ascending=False).drop_duplicates("caseid")

    cases = pd.read_csv(RES / "faers_cases_profile.csv", encoding="utf-8-sig")
    cases["primaryid"] = cases.primaryid.astype(str)
    d = df.merge(cases[["primaryid", "any_ocular", "any_optic",
                        "age", "sex", "reporter_country"]],
                 on="primaryid", how="inner")
    print(f"\n[3] analysable cases: {len(d):,}")
    print(f"    with an optic-nerve event : {int(d.any_optic.sum()):,} "
          f"({100*d.any_optic.mean():.2f}%)")
    print(f"    with any ocular event     : {int(d.any_ocular.sum()):,} "
          f"({100*d.any_ocular.mean():.2f}%)")
    print(f"    based on a partial date   : "
          f"{int((d.start_partial | d.event_partial).sum()):,}")

    # ------------------------------------------------------ exposure summary
    print("\n[4] exposure distribution among these cases")
    for col, unit in (("mg", "mg/day"), ("interval_capped", "days"),
                      ("cum_dose_g", "g")):
        s = d[col]
        print(f"    {col:18s} median {s.median():>9.1f} {unit:8s} "
              f"IQR {s.quantile(.25):>9.1f} - {s.quantile(.75):>9.1f}")

    # ----------------------------------------------------------- dose strata
    print("\n[5] optic-event rate by cumulative-dose tertile")
    d["cum_tertile"] = pd.qcut(d.cum_dose_g, 3,
                               labels=["low", "middle", "high"])
    rows = []
    for lab in ["low", "middle", "high"]:
        s = d[d.cum_tertile == lab]
        rows.append({
            "stratum": lab, "n": len(s),
            "cum_dose_median_g": round(float(s.cum_dose_g.median()), 1),
            "cum_dose_range_g": f"{s.cum_dose_g.min():.0f}-{s.cum_dose_g.max():.0f}",
            "median_interval_d": int(s.interval_capped.median()),
            "median_daily_mg": int(s.mg.median()),
            "n_optic": int(s.any_optic.sum()),
            "pct_optic": round(100 * s.any_optic.mean(), 2),
            "n_ocular": int(s.any_ocular.sum()),
            "pct_ocular": round(100 * s.any_ocular.mean(), 2)})
    tab = pd.DataFrame(rows)
    print(tab.to_string(index=False))

    # Cochran-Armitage trend on cumulative dose
    counts = tab.n_optic.values.astype(float)
    totals = tab.n.values.astype(float)
    scores = np.array([0.0, 1.0, 2.0])
    n = totals.sum()
    p = counts / totals
    pbar = counts.sum() / n
    w = totals
    num = np.sum(w * (scores - np.average(scores, weights=w)) * (p - pbar))
    den = np.sqrt(pbar * (1 - pbar) *
                  np.sum(w * (scores - np.average(scores, weights=w)) ** 2))
    z_cum = num / den if den > 0 else np.nan
    p_cum = 2 * (1 - stats.norm.cdf(abs(z_cum))) if np.isfinite(z_cum) else np.nan
    print(f"\n    Cochran-Armitage trend (cumulative dose): "
          f"z={z_cum:.3f}, P={p_cum:.4f}")

    # same test on interval alone, for comparison
    d["int_tertile"] = pd.qcut(d.interval_capped, 3,
                               labels=["short", "medium", "long"], duplicates="drop")
    ic = d.groupby("int_tertile", observed=True).agg(
        n=("any_optic", "size"), n_optic=("any_optic", "sum"))
    ic["pct"] = 100 * ic.n_optic / ic.n
    print("\n    for comparison, optic-event rate by exposure-interval tertile:")
    print(ic.to_string())

    # ------------------------------------------- which predictor carries risk?
    print("\n[6] does cumulative dose add information beyond exposure duration?")
    m = d.copy()
    m["log_daily"] = np.log(m.mg.clip(lower=1))
    m["log_days"] = np.log(m.interval_capped.clip(lower=1))
    m["log_cum"] = np.log(m.cum_dose_g.clip(lower=0.001))
    m["optic"] = m.any_optic.astype(int)

    def fit(cols):
        X = sm.add_constant(m[cols].astype(float))
        return sm.Logit(m.optic, X).fit(disp=0)

    fits = {}
    for name, cols in (("duration only", ["log_days"]),
                       ("daily dose only", ["log_daily"]),
                       ("cumulative dose only", ["log_cum"]),
                       ("duration + daily dose", ["log_days", "log_daily"])):
        try:
            r = fit(cols)
            fits[name] = r
            ors = ", ".join(
                f"{c}: OR {np.exp(r.params[c]):.3f} (P={r.pvalues[c]:.4f})"
                for c in cols)
            print(f"    {name:22s} pseudo-R2={r.prsquared:.4f}  {ors}")
        except Exception as exc:  # noqa: BLE001
            print(f"    {name:22s} failed: {type(exc).__name__} {exc}")

    if "duration only" in fits and "duration + daily dose" in fits:
        lr = 2 * (fits["duration + daily dose"].llf - fits["duration only"].llf)
        p_lr = 1 - stats.chi2.cdf(lr, df=1)
        print(f"\n    likelihood-ratio test, adding daily dose to duration: "
              f"chi2={lr:.3f}, P={p_lr:.4f}")
        print(f"    -> daily dose "
              f"{'adds' if p_lr < 0.05 else 'does not add'} information "
              f"beyond how long the patient was treated")

    tab.to_csv(RES / "faers_cumulative_dose.csv", index=False,
               encoding="utf-8-sig")
    tab.to_csv(TAB / "Table13_cumulative_dose.csv", index=False,
               encoding="utf-8-sig")
    d[["caseid", "primaryid", "mg", "interval_capped", "cum_dose_g",
       "any_optic", "any_ocular"]].to_csv(RES / "faers_cumulative_cases.csv",
                                          index=False, encoding="utf-8-sig")
    print(f"\n-> {RES / 'faers_cumulative_dose.csv'}")
    print(f"-> {TAB / 'Table13_cumulative_dose.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
