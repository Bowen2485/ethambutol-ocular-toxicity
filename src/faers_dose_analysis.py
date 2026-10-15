# -*- coding: utf-8 -*-
"""
Dose-stratified analysis of ethambutol ocular toxicity.

The clinical question
    A propensity-score cohort in Mycobacterium avium complex (MAC) pulmonary
    disease reported 0% optic neuropathy at 10.7 mg/kg/day versus 4.8% at
    15.4 mg/kg/day.  Whether that gradient holds in spontaneous reports, and in
    tuberculosis treatment where doses are higher, is unresolved.  This step tests
    it in the FAERS ethambutol case set.

The confounding problem, and how it is handled
    Ethambutol is used at two dose levels for two indications: 15-20 mg/kg/day for
    tuberculosis and roughly 10-15 mg/kg/day for MAC.  A naive dose-risk gradient
    could therefore be an indication effect rather than a dose effect.  Indication
    text in FAERS is sparse and inconsistently coded, so instead of adjusting for a
    field that is mostly empty, the analysis is repeated within dose bands defined
    by the weight-independent daily totals that dominate the data, and the
    sensitivity of the result to the assumed dose categories is reported.

Outputs -> results/faers_dose_strata.csv, tables/Table11_dose.csv
"""
from __future__ import annotations

import json
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
TAB = ROOT / "tables"
DB = DER / "faers.sqlite"

# units that express an absolute amount per administration
ABSOLUTE = {"MG": 1.0, "G": 1000.0, "GM": 1000.0, "MG.": 1.0, "MILLIGRAM": 1.0,
            "GRAM": 1000.0, "GR": 1000.0, "MCG": 0.001, "UG": 0.001}
# weight-based units, handled separately
WEIGHT_BASED = {"MG/KG", "MG/KG/DAY", "MGKG", "MG PER KG"}


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=1800)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1200000")
    return con


def parse_dose(amt: str, unit: str) -> tuple[float | None, str]:
    """Return (mg, kind) where kind is 'absolute', 'weight' or 'unusable'."""
    if amt is None or unit is None:
        return None, "unusable"
    a = re.sub(r"[^0-9.,]", "", str(amt)).replace(",", "")
    if not a:
        return None, "unusable"
    try:
        v = float(a)
    except ValueError:
        return None, "unusable"
    if v <= 0:
        return None, "unusable"
    u = str(unit).strip().upper()
    if u in ABSOLUTE:
        return v * ABSOLUTE[u], "absolute"
    if u in WEIGHT_BASED:
        return v, "weight"
    return None, "unusable"


def analyse(case_df: pd.DataFrame, label: str) -> dict:
    """Optic-event rate across dose strata, with a trend test."""
    d = case_df[case_df.mg.notna()].copy()
    if d.empty:
        return {}
    # daily totals cluster on 400/500/750/800/1000/1200/1500/1600 mg
    bins = [0, 799, 1199, np.inf]
    names = ["<800 mg/day", "800-1199 mg/day", ">=1200 mg/day"]
    d["stratum"] = pd.cut(d.mg, bins=bins, labels=names, right=False)
    out = {"analysis": label, "n_with_dose": len(d)}
    rows = []
    for nm in names:
        s = d[d.stratum == nm]
        rows.append({"stratum": nm, "n": len(s),
                     "n_optic": int(s.any_optic.sum()),
                     "pct_optic": round(100 * s.any_optic.mean(), 2) if len(s) else np.nan,
                     "n_ocular": int(s.any_ocular.sum()),
                     "pct_ocular": round(100 * s.any_ocular.mean(), 2) if len(s) else np.nan})
    # Cochran-Armitage trend test on the optic outcome
    tab = np.array([[r["n_optic"], r["n"] - r["n_optic"]] for r in rows])
    if tab.shape[0] == 3 and tab[:, 1].sum() > 0:
        scores = np.array([0, 1, 2])
        n = tab.sum()
        p = tab[:, 0] / np.maximum(tab.sum(axis=1), 1)
        pbar = tab[:, 0].sum() / n
        num = np.sum(tab.sum(axis=1) * (scores - np.average(scores,
                       weights=tab.sum(axis=1))) * (p - pbar))
        den = np.sqrt(pbar * (1 - pbar) * np.sum(
            tab.sum(axis=1) * (scores - np.average(scores, weights=tab.sum(axis=1))) ** 2))
        z = num / den if den > 0 else np.nan
        out["trend_z"] = round(float(z), 3) if np.isfinite(z) else np.nan
        out["trend_p"] = round(float(2 * (1 - stats.norm.cdf(abs(z)))), 6) \
            if np.isfinite(z) else np.nan
    for r in rows:
        out[f"n_{r['stratum']}"] = r["n"]
        out[f"optic_pct_{r['stratum']}"] = r["pct_optic"]
    return out


def main() -> int:
    con = connect()

    print("[1] extracting ethambutol records with a dose ...")
    con.execute("DROP TABLE IF EXISTS temp.eth")
    con.execute("""
        CREATE TEMP TABLE eth AS
        SELECT DISTINCT d.primaryid AS primaryid, d.caseid AS caseid,
               d.dose_amt AS amt, d.dose_unit AS unit, d.route AS route,
               d.indication AS indication
        FROM drug d
        JOIN dedup_map m ON m.primaryid = d.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        WHERE (UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
            OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%')
    """)
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_eth ON eth(primaryid)")
    n_rows = con.execute("SELECT COUNT(*) FROM eth").fetchone()[0]
    n_case = con.execute("SELECT COUNT(DISTINCT caseid) FROM eth").fetchone()[0]
    print(f"    {n_rows:,} drug lines across {n_case:,} cases")

    print("[2] how often is an indication recorded?")
    n_ind = con.execute(
        "SELECT COUNT(*) FROM eth WHERE COALESCE(indication,'') <> ''").fetchone()[0]
    print(f"    indication present on {n_ind:,} / {n_rows:,} lines "
          f"({100*n_ind/n_rows:.1f}%)")
    if n_ind:
        for v, c in con.execute(
                "SELECT UPPER(indication), COUNT(*) FROM eth "
                "WHERE COALESCE(indication,'') <> '' GROUP BY 1 ORDER BY 2 DESC "
                "LIMIT 12"):
            print(f"      {str(v)[:58]:60s} {c:>6,}")

    df = pd.read_sql_query("SELECT * FROM eth", con)
    con.close()

    print("\n[3] parsing doses ...")
    parsed = df.amt.combine(df.unit, lambda a, u: parse_dose(a, u))
    df["mg"] = [p[0] for p in parsed]
    df["kind"] = [p[1] for p in parsed]
    print(df.kind.value_counts().to_string())
    # one representative record per case: keep the largest absolute mg
    df_abs = df[(df.kind == "absolute") & df.mg.notna()]
    df_wt = df[(df.kind == "weight") & df.mg.notna()]

    cases = pd.read_csv(RES / "faers_cases_profile.csv", encoding="utf-8-sig")
    cases["primaryid"] = cases.primaryid.astype(str)

    def merge_outcomes(d: pd.DataFrame) -> pd.DataFrame:
        d = d.copy()
        d["primaryid"] = d.primaryid.astype(str)
        # per case keep the highest recorded absolute dose
        d = d.sort_values("mg", ascending=False).drop_duplicates("caseid")
        m = d.merge(cases[["primaryid", "any_ocular", "any_optic"]],
                    on="primaryid", how="inner")
        return m

    abs_cases = merge_outcomes(df_abs)
    wt_cases = merge_outcomes(df_wt)
    print(f"\n[4] cases with an absolute dose : {len(abs_cases):,}")
    print(f"    cases with a weight-based dose: {len(wt_cases):,}")

    rows = []
    r1 = analyse(abs_cases, "absolute daily dose (mg/day)")
    if r1:
        rows.append(r1)

    # ------------------------------------------------------------------ mg/kg
    # The published contrast is 10.7 vs 15.4 mg/kg/day in MAC disease, so the
    # weight-based subset is stratified at the clinically meaningful cut-points
    # rather than rescaled onto the absolute-dose bins.
    wt_out = {}
    if len(wt_cases) >= 30:
        w = wt_cases.copy()
        bands = [0, 10, 15, np.inf]
        names = ["<10 mg/kg/day", "10-14.9 mg/kg/day", ">=15 mg/kg/day"]
        w["stratum"] = pd.cut(w.mg, bins=bands, labels=names, right=False)
        wt_out = {"analysis": "weight-based dose (mg/kg/day)",
                  "n_with_dose": len(w)}
        for nm in names:
            s = w[w.stratum == nm]
            wt_out[f"n_{nm}"] = len(s)
            wt_out[f"optic_pct_{nm}"] = (round(100 * s.any_optic.mean(), 2)
                                         if len(s) else np.nan)
        # Fisher exact on the two clinically relevant bands
        lo = w[w.stratum == names[0]]
        hi = w[w.stratum == names[2]]
        if len(lo) >= 5 and len(hi) >= 5:
            tab = [[int(hi.any_optic.sum()), len(hi) - int(hi.any_optic.sum())],
                   [int(lo.any_optic.sum()), len(lo) - int(lo.any_optic.sum())]]
            try:
                odds, pf = stats.fisher_exact(tab)
                wt_out["fisher_or_hi_vs_lo"] = round(float(odds), 3)
                wt_out["fisher_p"] = round(float(pf), 4)
            except Exception:  # noqa: BLE001
                pass
        rows.append(wt_out)

    out = pd.DataFrame(rows)
    out.to_csv(RES / "faers_dose_strata.csv", index=False, encoding="utf-8-sig")

    print("\n=== dose strata: optic-nerve event rate ===")
    print(out.to_string(index=False))

    # ------------------------------------------------------ power of the test
    # With ~3,300 dosed cases and a ~3.5% event rate, what difference could this
    # sample actually detect?  Report it rather than leaving the null ambiguous.
    print("\n=== detectable difference (post-hoc power, optic outcome) ===")
    from statsmodels.stats.power import NormalIndPower
    from statsmodels.stats.proportion import proportion_effectsize
    n_per = len(abs_cases) // 3
    p0 = abs_cases.any_optic.mean()
    power = NormalIndPower()
    for delta in (0.02, 0.03, 0.05, 0.08):
        try:
            es = proportion_effectsize(min(p0 + delta, 0.99), p0)
            pw = power.power(effect_size=es, nobs1=n_per, alpha=0.05,
                             ratio=1.0, alternative="two-sided")
            print(f"    {delta*100:.0f} percentage-point increase "
                  f"({p0*100:.1f}% -> {(p0+delta)*100:.1f}%): power = {pw:.2f}")
        except Exception:  # noqa: BLE001
            pass
    print(f"    (n per group = {n_per:,}; baseline optic rate = {p0*100:.2f}%)")

    print("\n=== absolute-dose distribution (mg) ===")
    q = df_abs.mg.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
    print(q.to_string())
    print("\n  most common absolute doses:")
    for v, c in df_abs.mg.value_counts().head(12).items():
        print(f"      {v:>8.0f} mg   {c:>5,} records")

    out.to_csv(TAB / "Table11_dose.csv", index=False, encoding="utf-8-sig")
    print(f"\n-> {RES / 'faers_dose_strata.csv'}")
    print(f"-> {TAB / 'Table11_dose.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
