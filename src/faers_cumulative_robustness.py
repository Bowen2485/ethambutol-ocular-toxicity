# -*- coding: utf-8 -*-
"""
Robustness checks for the cumulative-dose finding.

The headline result is that the optic-event rate rises steeply with cumulative dose
(0.95% -> 3.55% -> 10.90% across tertiles, trend P < 1e-4) while daily dose carries
no information once exposure duration is accounted for (likelihood-ratio P = 0.55).
Because cumulative dose is the product of daily dose and duration, and the daily
dose gradient is flat, cumulative dose is numerically close to a restatement of
duration.  Three checks are needed before that interpretation is safe.

  1. collinearity between the three exposure variables
  2. whether the duration effect is an artefact of the interval definition itself -
     cases with a longer interval have more opportunity to be reported with an
     optic event, but they also differ in daily dose; check both directions
  3. whether the result survives adjustment for age and sex (longer treatment may
     simply mark a different patient mix)
  4. a negative control: the same model on non-specific ocular events, which should
     not show the same duration dependence if the finding is specific

Outputs -> results/faers_cumulative_robustness.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"



def main() -> int:
    cases = pd.read_csv(RES / "faers_cumulative_cases.csv", encoding="utf-8-sig")
    profile = pd.read_csv(RES / "faers_cases_profile.csv", encoding="utf-8-sig")
    # the id columns are read as different dtypes depending on the file, so both
    # sides are normalised to string before merging
    cases["primaryid"] = cases.primaryid.astype(str)
    profile["primaryid"] = profile.primaryid.astype(str)
    d = cases.merge(profile[["primaryid", "age", "age_cod", "sex"]],
                    on="primaryid", how="left")

    d["log_days"] = np.log(d.interval_capped.clip(lower=1))
    d["log_daily"] = np.log(d.mg.clip(lower=1))
    d["log_cum"] = np.log(d.cum_dose_g.clip(lower=0.001))
    d["optic"] = d.any_optic.astype(int)
    d["ocular"] = d.any_ocular.astype(int)
    # normalise age for the decade unit and drop implausible values
    age = pd.to_numeric(d.age, errors="coerce")
    dec = d.age_cod.astype(str).str.upper().str.startswith("DEC")
    age[dec] = age[dec] * 10
    age[(age < 0) | (age > 110)] = np.nan
    d["age_y"] = age
    d["female"] = d.sex.astype(str).str.upper().str[0].eq("F").astype(float)
    d.loc[d.sex.isna(), "female"] = np.nan

    rows = []

    def note(**kw):
        rows.append(kw)

    print("=" * 74)
    print("1. Collinearity among the exposure variables")
    print("=" * 74)
    cm = d[["log_days", "log_daily", "log_cum"]].corr(method="spearman")
    print(cm.round(3).to_string())
    r_dc = cm.loc["log_days", "log_cum"]
    r_dd = cm.loc["log_days", "log_daily"]
    print(f"\n  Spearman(duration, cumulative dose) = {r_dc:.3f}")
    print(f"  Spearman(duration, daily dose)      = {r_dd:.3f}")
    print("  -> cumulative dose is numerically dominated by duration, which is")
    print("     exactly what a flat daily-dose gradient implies")
    note(check="collinearity", spearman_duration_cum=round(float(r_dc), 3),
         spearman_duration_daily=round(float(r_dd), 3))

    print()
    print("=" * 74)
    print("2. Duration effect with and without adjustment")
    print("=" * 74)

    def fit(df, outcome: str, cols: list[str]):
        sub = df.dropna(subset=cols + [outcome])
        X = sm.add_constant(sub[cols].astype(float))
        return sm.Logit(sub[outcome].astype(int), X).fit(disp=0), len(sub)

    specs = [
        ("optic", ["log_days"], "duration only"),
        ("optic", ["log_days", "log_daily"], "+ daily dose"),
        ("optic", ["log_days", "log_daily", "age_y"], "+ age"),
        ("optic", ["log_days", "log_daily", "age_y", "female"], "+ age + sex"),
        ("ocular", ["log_days", "log_daily", "age_y", "female"],
         "non-specific ocular outcome (negative control)"),
    ]
    for outcome, cols, label in specs:
        try:
            r, n = fit(d, outcome, cols)
            or_days = np.exp(r.params["log_days"])
            p_days = r.pvalues["log_days"]
            extra = ""
            if "log_daily" in cols:
                extra = (f" | daily-dose OR {np.exp(r.params['log_daily']):.3f} "
                         f"(P={r.pvalues['log_daily']:.3f})")
            print(f"  {label:52s} n={n:>5,}  "
                  f"duration OR/unit log = {or_days:.3f} (P={p_days:.2e}){extra}")
            note(check=f"model: {label}", n=n,
                 duration_or=round(float(or_days), 3),
                 duration_p=float(f"{p_days:.3e}"),
                 daily_or=(round(float(np.exp(r.params["log_daily"])), 3)
                           if "log_daily" in cols else None),
                 daily_p=(float(f"{r.pvalues['log_daily']:.3e}")
                          if "log_daily" in cols else None))
        except Exception as exc:  # noqa: BLE001
            print(f"  {label:52s} failed: {type(exc).__name__}")

    print()
    print("=" * 74)
    print("3. Restricting to long intervals only (removes short-interval cases)")
    print("=" * 74)
    for lo in (0, 30, 90, 180):
        s = d[d.interval_capped >= lo]
        if s.optic.sum() < 5:
            print(f"  interval >= {lo:>3} d: too few events ({int(s.optic.sum())})")
            continue
        s = s.copy()
        s["tert"] = pd.qcut(s.cum_dose_g, 3, labels=["low", "mid", "high"],
                            duplicates="drop")
        g = s.groupby("tert", observed=True).agg(n=("optic", "size"),
                                                 ev=("optic", "sum"))
        g["pct"] = 100 * g.ev / g.n
        print(f"  interval >= {lo:>3} d  (n={len(s):,}, events={int(s.optic.sum())}): "
              + "  ".join(f"{i}={r.pct:.2f}%" for i, r in g.iterrows()))
        note(check=f"cumulative-dose gradient, interval >= {lo} d", n=len(s),
             events=int(s.optic.sum()),
             pct_by_tertile=[round(float(v), 2) for v in g.pct.values])

    print()
    print("=" * 74)
    print("4. Power: what duration difference could this sample detect?")
    print("=" * 74)
    from statsmodels.stats.power import NormalIndPower
    from statsmodels.stats.proportion import proportion_effectsize
    n_per = len(d) // 3
    p0 = d.optic.mean()
    pw = NormalIndPower()
    for delta in (0.02, 0.04, 0.06):
        es = proportion_effectsize(min(p0 + delta, 0.99), p0)
        power = pw.power(effect_size=es, nobs1=n_per, alpha=0.05, ratio=1.0,
                         alternative="two-sided")
        print(f"  detecting a {delta*100:.0f} pp rise from {p0*100:.2f}%: "
              f"power = {power:.2f}")
        note(check=f"power for +{delta*100:.0f}pp", n_per_group=int(n_per),
             power=round(float(power), 3))

    out = pd.DataFrame(rows)
    out.to_csv(RES / "faers_cumulative_robustness.csv", index=False,
               encoding="utf-8-sig")
    print(f"\n-> {RES / 'faers_cumulative_robustness.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
