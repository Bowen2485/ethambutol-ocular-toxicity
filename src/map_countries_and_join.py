# -*- coding: utf-8 -*-
"""
Map the FAERS country values onto ISO alpha-3, then attach the WHO tuberculosis burden.

The problem
    FAERS stores the reporting country as a mixture of forms - two-letter codes, full
    names in capitals, and a few placeholders - while the WHO Global Health Observatory
    keys on ISO alpha-3.  A merge on the raw values returned zero matched cells even
    though both sides were fully populated.

    No mapping library is installed and none is being installed for this, so the table
    below is written out explicitly.  It is checked rather than trusted: the script
    reports what fraction of reports it maps, and lists anything it could not place, so
    an incomplete table shows up as a number instead of silently dropping countries.

After mapping
    WHO incidence (per 100,000 per year) x population is not available directly, but the
    ratio used here does not need it: what matters is how many reports a country
    generates relative to its tuberculosis burden, and burden per 100,000 serves as the
    relative measure.  Reports are matched to the WHO year, and the report volume per
    unit of burden is compared across countries.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"

#: FAERS value -> ISO alpha-3.  Includes two-letter codes, full names, and the common
#: variants that appear in FAERS; anything absent is reported rather than dropped.
A2 = {
    "AE": "ARE", "AF": "AFG", "AL": "ALB", "AM": "ARM", "AO": "AGO", "AR": "ARG",
    "AT": "AUT", "AU": "AUS", "AZ": "AZE", "BA": "BIH", "BD": "BGD", "BE": "BEL",
    "BF": "BFA", "BG": "BGR", "BH": "BHR", "BJ": "BEN", "BO": "BOL", "BR": "BRA",
    "BY": "BLR", "CA": "CAN", "CH": "CHE", "CI": "CIV", "CL": "CHL", "CM": "CMR",
    "CN": "CHN", "CO": "COL", "CR": "CRI", "CU": "CUB", "CY": "CYP", "CZ": "CZE",
    "DE": "DEU", "DK": "DNK", "DO": "DOM", "DZ": "DZA", "EC": "ECU", "EE": "EST",
    "EG": "EGY", "ES": "ESP", "ET": "ETH", "FI": "FIN", "FR": "FRA", "GB": "GBR",
    "GE": "GEO", "GH": "GHA", "GR": "GRC", "GT": "GTM", "HK": "HKG", "HR": "HRV",
    "HU": "HUN", "ID": "IDN", "IE": "IRL", "IL": "ISR", "IN": "IND", "IQ": "IRQ",
    "IR": "IRN", "IS": "ISL", "IT": "ITA", "JM": "JAM", "JO": "JOR", "JP": "JPN",
    "KE": "KEN", "KG": "KGZ", "KH": "KHM", "KR": "KOR", "KW": "KWT", "KZ": "KAZ",
    "LB": "LBN", "LK": "LKA", "LT": "LTU", "LU": "LUX", "LV": "LVA", "LY": "LBY",
    "MA": "MAR", "MD": "MDA", "ME": "MNE", "MK": "MKD", "MM": "MMR", "MN": "MNG",
    "MT": "MLT", "MU": "MUS", "MV": "MDV", "MX": "MEX", "MY": "MYS", "MZ": "MOZ",
    "NG": "NGA", "NL": "NLD", "NO": "NOR", "NP": "NPL", "NZ": "NZL", "OM": "OMN",
    "PA": "PAN", "PE": "PER", "PH": "PHL", "PK": "PAK", "PL": "POL", "PT": "PRT",
    "PY": "PRY", "QA": "QAT", "RO": "ROU", "RS": "SRB", "RU": "RUS", "SA": "SAU",
    "SE": "SWE", "SG": "SGP", "SI": "SVN", "SK": "SVK", "SN": "SEN", "SV": "SLV",
    "SY": "SYR", "TH": "THA", "TN": "TUN", "TR": "TUR", "TT": "TTO", "TW": "TWN",
    "TZ": "TZA", "UA": "UKR", "UG": "UGA", "US": "USA", "UY": "URY", "UZ": "UZB",
    "VE": "VEN", "VN": "VNM", "YE": "YEM", "ZA": "ZAF", "ZM": "ZMB", "ZW": "ZWE",
}
NAME = {
    "ARGENTINA": "ARG", "AUSTRALIA": "AUS", "AUSTRIA": "AUT", "BELGIUM": "BEL",
    "BRAZIL": "BRA", "BULGARIA": "BGR", "CANADA": "CAN", "CHILE": "CHL",
    "CHINA": "CHN", "COLOMBIA": "COL", "CROATIA": "HRV", "CUBA": "CUB",
    "CZECH REPUBLIC": "CZE", "DENMARK": "DNK", "EGYPT": "EGY", "ESTONIA": "EST",
    "FINLAND": "FIN", "FRANCE": "FRA", "GERMANY": "DEU", "GREECE": "GRC",
    "HONG KONG": "HKG", "HUNGARY": "HUN", "ICELAND": "ISL", "INDIA": "IND",
    "INDONESIA": "IDN", "IRAN": "IRN", "IRELAND": "IRL", "ISRAEL": "ISR",
    "ITALY": "ITA", "JAPAN": "JPN", "JORDAN": "JOR", "KENYA": "KEN",
    "KOREA": "KOR", "SOUTH KOREA": "KOR", "REPUBLIC OF KOREA": "KOR",
    "KUWAIT": "KWT", "LATVIA": "LVA", "LEBANON": "LBN", "LITHUANIA": "LTU",
    "MALAYSIA": "MYS", "MEXICO": "MEX", "MOROCCO": "MAR", "NEPAL": "NPL",
    "NETHERLANDS": "NLD", "NEW ZEALAND": "NZL", "NIGERIA": "NGA", "NORWAY": "NOR",
    "PAKISTAN": "PAK", "PERU": "PER", "PHILIPPINES": "PHL", "POLAND": "POL",
    "PORTUGAL": "PRT", "ROMANIA": "ROU", "RUSSIA": "RUS", "SAUDI ARABIA": "SAU",
    "SERBIA": "SRB", "SINGAPORE": "SGP", "SLOVAKIA": "SVK", "SLOVENIA": "SVN",
    "SOUTH AFRICA": "ZAF", "SPAIN": "ESP", "SWEDEN": "SWE", "SWITZERLAND": "CHE",
    "TAIWAN": "TWN", "THAILAND": "THA", "TURKEY": "TUR", "TURKIYE": "TUR",
    "UKRAINE": "UKR", "UNITED KINGDOM": "GBR", "UNITED STATES": "USA",
    "USA": "USA", "UK": "GBR", "VENEZUELA": "VEN", "VIETNAM": "VNM",
    "VIET NAM": "VNM", "ZAMBIA": "ZMB", "ZIMBABWE": "ZWE", "GEORGIA": "GEO",
    "KAZAKHSTAN": "KAZ", "SRI LANKA": "LKA", "BANGLADESH": "BGD",
    "ETHIOPIA": "ETH", "GHANA": "GHA", "TANZANIA": "TZA", "UGANDA": "UGA",
    "CAMEROON": "CMR", "SENEGAL": "SEN", "MOZAMBIQUE": "MOZ",
}
#: values that are not countries and must not be mapped
SKIP = {"", "COUNTRY NOT SPECIFIED", "NOT SPECIFIED", "UNKNOWN", "EU", "EUROPE",
        "AFRICA", "ASIA", "WORLDWIDE", "N/A", "NA"}


def to_iso3(v: str) -> str | None:
    s = (v or "").strip().upper()
    if s in SKIP:
        return None
    if s in NAME:
        return NAME[s]
    if len(s) == 2 and s in A2:
        return A2[s]
    if len(s) == 3 and s.isalpha():
        return s          # already ISO3
    return None


print("=" * 96)
print("1. Map the FAERS country values")
print("=" * 96)
# The distinct values are read straight from the database rather than from an
# intermediate file: an earlier version expected results/faers_country_values.csv,
# which a failed shell command had never produced, and the script died on the missing
# file instead of doing the work.  Reading the source removes the dependency.
_con = sqlite3.connect(f"file:{DERIVED/'faers.sqlite'}?mode=ro", uri=True)
_q = """SELECT UPPER(TRIM(reporter_country)) AS raw_value, COUNT(*) AS n_cases
        FROM demo d JOIN dedup_map m ON d.primaryid = m.primaryid
        WHERE reporter_country IS NOT NULL AND TRIM(reporter_country) <> ''
        GROUP BY raw_value ORDER BY n_cases DESC"""
raw = pd.DataFrame(_con.execute(_q).fetchall(), columns=["raw_value", "n_cases"])
_con.close()
raw["raw_value"] = raw["raw_value"].fillna("").astype(str)
print(f"  distinct FAERS country values read from the database: {len(raw)}")
raw["iso3"] = raw["raw_value"].map(to_iso3)
mapped = raw[raw.iso3.notna()]
unmapped = raw[raw.iso3.isna() & ~raw.raw_value.str.upper().isin(SKIP)]
total = raw.n_cases.sum()
print(f"  distinct FAERS values : {len(raw)}")
print(f"  mapped to ISO3        : {mapped.raw_value.nunique()} values, "
      f"{mapped.n_cases.sum():,} reports "
      f"({100*mapped.n_cases.sum()/total:.1f}%)")
print(f"  skipped as non-country: {raw[raw.raw_value.str.upper().isin(SKIP)].n_cases.sum():,} "
      f"reports")
print(f"  UNMAPPED              : {unmapped.n_cases.sum():,} reports "
      f"in {len(unmapped)} values")
if len(unmapped):
    print("      (these are listed rather than dropped silently)")
    for _, r in unmapped.sort_values("n_cases", ascending=False).head(30).iterrows():
        print(f"        {r.n_cases:>7,}  {r.raw_value!r}")

print()
print("=" * 96)
print("2. FAERS ethambutol reports by ISO3 and year")
print("=" * 96)
con = sqlite3.connect(f"file:{DERIVED/'faers.sqlite'}?mode=ro", uri=True)
MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")
pats = ["%ETHAMBUTOL%", "%MYAMBUTOL%", "%DEXAMBUTOL%", "%ETAMBUTOL%"]
cond = " OR ".join([MATCH] * len(pats))
params = [p for pat in pats for p in (pat, pat)]
q = f"""SELECT UPPER(TRIM(dm.reporter_country)) AS cc,
               CAST(substr(dm.fda_dt,1,4) AS INTEGER) AS yr,
               COUNT(DISTINCT d.caseid) AS n_reports
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
                   columns=["raw_value", "yr", "n_reports"])
con.close()
emb["iso3"] = emb.raw_value.map(to_iso3)
emb = emb[emb.iso3.notna() & emb.yr.between(2004, 2024)]
print(f"  {emb.n_reports.sum():,} reports across {emb.iso3.nunique()} countries")

print()
print("=" * 96)
print("3. Join to the WHO incidence indicator")
print("=" * 96)
who = pd.read_csv(DERIVED / "who_TB_incidence_per100k.csv")
who = who.rename(columns={"SpatialDim": "iso3", "TimeDim": "yr",
                          "NumericValue": "tb_inc_per100k"})
who = who[["iso3", "yr", "tb_inc_per100k"]].dropna()
who["yr"] = pd.to_numeric(who["yr"], errors="coerce").astype("Int64")
who = who.dropna(subset=["yr"])
who["yr"] = who["yr"].astype(int)
# WHO aggregates are not countries
AGG = {"GLOBAL", "WB_HI", "WB_LMI", "WB_UMI", "WB_LI", "AFR", "AMR", "SEAR",
       "EUR", "EMR", "WPR"}
who = who[~who.iso3.isin(AGG)]
merged = emb.merge(who, on=["iso3", "yr"], how="inner")
print(f"  matched cells        : {len(merged):,}")
print(f"  reports covered      : {merged.n_reports.sum():,} of "
      f"{emb.n_reports.sum():,} "
      f"({100*merged.n_reports.sum()/max(emb.n_reports.sum(),1):.1f}%)")
print(f"  countries matched    : {merged.iso3.nunique()}")

agg = (merged.groupby(["iso3", "cc" if "cc" in merged else "iso3"])
       .agg(reports=("n_reports", "sum"),
            mean_inc=("tb_inc_per100k", "mean"),
            years=("yr", "nunique"))
       .reset_index(drop=True))
agg = merged.groupby("iso3").agg(reports=("n_reports", "sum"),
                                 mean_inc=("tb_inc_per100k", "mean"),
                                 years=("yr", "nunique")).reset_index()
agg = agg[agg.reports >= 50].copy()
agg["reports_per_inc"] = agg.reports / agg.mean_inc.clip(lower=0.01)
agg = agg.sort_values("mean_inc", ascending=False)
print()
print(f"  {'iso3':6s} {'reports':>8s} {'mean TB inc/100k':>18s} {'years':>6s} "
      f"{'reports per inc unit':>22s}")
for _, r in agg.iterrows():
    print(f"  {r.iso3:6s} {int(r.reports):>8,} {r.mean_inc:>18.1f} "
          f"{int(r.years):>6d} {r.reports_per_inc:>22.1f}")

DERIVED.joinpath("faers_tb_denominator.csv").write_text(
    agg.to_csv(index=False), encoding="utf-8")
DERIVED.joinpath("faers_who_merged.csv").write_text(
    merged.to_csv(index=False), encoding="utf-8")

if len(agg) >= 5:
    rho = agg["mean_inc"].corr(agg["reports"], method="spearman")
    print()
    print(f"  Spearman rho (mean TB incidence vs report count): {rho:+.3f}  "
          f"across {len(agg)} countries")
    print("  Negative would mean high-burden countries generate fewer reports each,")
    print("  pointing to reporting intensity rather than patient numbers.")
print()
print(f"  -> data/derived/faers_tb_denominator.csv")
print(f"  -> data/derived/faers_who_merged.csv")
