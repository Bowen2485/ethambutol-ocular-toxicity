# -*- coding: utf-8 -*-
"""
Attach a tuberculosis burden denominator to the FAERS country counts.

Why this matters
    Every figure in the paper is a proportion of reports, never a rate, because FAERS
    has no denominator: nobody knows how many people took ethambutol.  That is the
    single most serious limitation a reviewer will raise.

    A denominator can be approximated.  Ethambutol is a standard component of first-line
    antitubercular therapy, so the number of people treated with it scales with the
    number treated for tuberculosis, which WHO publishes annually for every country.
    Dividing reports by that estimate gives reports per 100,000 estimated treated
    patients - a report rate rather than a report proportion.

What the country data already show
    The country field is 98.2% populated overall and 100% for the ethambutol cases, and
    the reports span 175 countries.  Crude optic-neuropathy percentages within country
    range from 0% (Italy, South Africa, Switzerland, Brazil, Indonesia) to 6.06%
    (Taiwan).  Two explanations compete: countries differ in the true incidence, or they
    differ in how intensively they report.  A burden denominator separates them, because
    if reporting intensity dominates then the rate per treated patient will be inversely
    related to burden - a country with many patients and few reports.

Method and its assumptions
    Treated patients  ~  notified incidence (per 100k) x population / 100,000
    Ethambutol-exposed  ~  a fixed fraction of those, assumed equal across countries
    Reports per 100k treated  =  observed ethambutol reports / estimated exposed x 100,000
    The fraction cancels in comparisons across countries, which is the only use made of
    it here.  This is stated as an approximation, not as an incidence.
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}
GHO = "https://ghoapi.azureedge.net/api"

#: WHO indicators: incidence is what scales with treated patients
INDICATORS = {
    "TB_incidence_per100k": "MDG_0000000020",
    "TB_treatment_coverage": "TB_1",
    "TB_new_and_relapse": "TB_tot_newrel",
}

#: three-letter codes present in the FAERS country column that are actually countries
#: (EU is an aggregate; "COUNTRY NOT SPECIFIED" is a placeholder)
NOT_A_COUNTRY = {"EU", "COUNTRY NOT SPECIFIED", "NOT SPECIFIED", "UNKNOWN", "XX"}


def fetch_indicator(code: str) -> pd.DataFrame:
    """All values for one indicator, following OData paging."""
    rows, url = [], f"{GHO}/{code}"
    while url:
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
                    j = json.loads(r.read())
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    print(f"    {code}: failed {type(exc).__name__}")
                    return pd.DataFrame()
                time.sleep(2)
        rows.extend(j.get("value", []))
        url = j.get("@odata.nextLink")
    df = pd.DataFrame(rows)
    print(f"    {code}: {len(df):,} rows")
    return df


print("=" * 96)
print("1. WHO Global Health Observatory")
print("=" * 96)
frames = {}
for label, code in INDICATORS.items():
    print(f"  fetching {label}")
    d = fetch_indicator(code)
    if d.empty:
        continue
    keep = [c for c in ("SpatialDim", "TimeDim", "NumericValue", "Dim1", "Value")
            if c in d.columns]
    d = d[keep].copy()
    frames[label] = d
    DERIVED.joinpath(f"who_{label}.csv").write_text(
        d.to_csv(index=False), encoding="utf-8")
    print(f"      -> data/derived/who_{label}.csv  ({len(d):,} rows)")

print()
print("=" * 96)
print("2. FAERS ethambutol reports by country and year")
print("=" * 96)
import sqlite3
con = sqlite3.connect(f"file:{ROOT/'data/derived/faers.sqlite'}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-2000000")
MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")
pats = ["%ETHAMBUTOL%", "%MYAMBUTOL%", "%DEXAMBUTOL%", "%ETAMBUTOL%"]
cond = " OR ".join([MATCH] * len(pats))
params = [p for pat in pats for p in (pat, pat)]
import re
q = f"""SELECT UPPER(TRIM(dm.reporter_country)) AS cc,
               CAST(substr(dm.fda_dt,1,4) AS INTEGER) AS yr,
               COUNT(DISTINCT d.caseid) AS n
        FROM drug d
        JOIN dedup_map m ON d.primaryid = m.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        JOIN demo dm ON dm.primaryid = m.primaryid
        WHERE {cond}
          AND dm.reporter_country IS NOT NULL AND TRIM(dm.reporter_country) <> ''
          AND dm.fda_dt IS NOT NULL AND length(dm.fda_dt) >= 4
        GROUP BY cc, yr"""
emb = pd.DataFrame(con.execute(q, params).fetchall(),
                   columns=["cc", "yr", "n_reports"])
con.close()
emb = emb[~emb.cc.isin(NOT_A_COUNTRY)]
emb = emb[(emb.yr >= 2004) & (emb.yr <= 2025)]
print(f"  {len(emb):,} country-year cells, {emb.cc.nunique()} countries, "
      f"{emb.n_reports.sum():,} reports")

print()
print("=" * 96)
print("3. Merge the burden data")
print("=" * 96)
if "TB_incidence_per100k" in frames:
    inc = frames["TB_incidence_per100k"]
    inc = inc.rename(columns={"SpatialDim": "cc", "TimeDim": "yr",
                              "NumericValue": "tb_inc_per100k"})
    inc = inc[["cc", "yr", "tb_inc_per100k"]].dropna()
    inc["yr"] = pd.to_numeric(inc["yr"], errors="coerce")
    inc = inc.dropna(subset=["yr"])
    inc["yr"] = inc["yr"].astype(int)
    merged = emb.merge(inc, on=["cc", "yr"], how="inner")
    print(f"  reports matched to a WHO incidence figure: {len(merged):,} cells")
    print(f"  reports covered: {merged.n_reports.sum():,} of "
          f"{emb.n_reports.sum():,} "
          f"({100*merged.n_reports.sum()/max(emb.n_reports.sum(),1):.1f}%)")

    # reports per unit of burden: high values mean many reports for few patients
    merged["reports_per_100k_inc"] = (
        merged.n_reports / merged.tb_inc_per100k.replace(0, pd.NA) * 100)
    agg = (merged.groupby("cc")
           .agg(reports=("n_reports", "sum"),
                mean_inc=("tb_inc_per100k", "mean"),
                years=("yr", "count"))
           .reset_index())
    agg = agg[agg.reports >= 50].sort_values("mean_inc", ascending=False)
    print()
    print("  Countries with at least 50 ethambutol reports, by mean TB incidence")
    print(f"  {'cc':6s} {'reports':>8s} {'mean TB inc/100k':>18s} "
          f"{'reports per 100 inc units':>26s}")
    for _, r in agg.iterrows():
        ratio = r.reports / max(r.mean_inc, 1e-9) * 100
        print(f"  {r.cc:6s} {int(r.reports):>8,} {r.mean_inc:>18.1f} {ratio:>26.1f}")

    DERIVED.joinpath("faers_tb_denominator.csv").write_text(
        agg.to_csv(index=False), encoding="utf-8")
    print()
    print("  -> data/derived/faers_tb_denominator.csv")
    if len(agg) >= 4:
        rho = agg["mean_inc"].corr(agg["reports"], method="spearman")
        print()
        print(f"  Spearman rho between a country's mean TB incidence and its "
              f"ethambutol report count: {rho:+.3f}")
        print("  A negative value means countries with more tuberculosis patients "
              "generate fewer reports each,")
        print("  which would point to reporting intensity rather than disease burden "
              "driving the counts.")
else:
    print("  incidence indicator unavailable; the denominator cannot be built")
