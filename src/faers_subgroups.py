# -*- coding: utf-8 -*-
"""
Subgroup analysis of the ethambutol optic-nerve signal by sex, age, region and era.

Why
    Three of the four peer papers in this genre report subgroup analyses, and reviewers
    routinely ask whether a signal holds across the groups where it would be expected to
    differ.  The manuscript currently stratifies only by treatment regimen and by reporting
    era, which answers the confounding question but not the consistency question.

What is computed
    Within each subgroup the ethambutol optic-nerve odds ratio is recomputed against the
    whole de-duplicated database, using the same 2x2 construction, ROR and Woolf interval as
    the main analysis so the numbers are directly comparable with it.

    The subgroups are then compared with each other by the ratio of their odds ratios rather
    than by eye.  Two strata can both be significant, or both be null, and still differ from
    each other, so reporting the ratio with an interval is what turns a table into a test.
    This is the point of the analysis: not to show that the signal is present everywhere -
    which would be expected of a real effect - but to show that no subgroup behaves
    differently enough to explain it.

Missing data
    Sex is unrecorded in 12% of reports and age in 39%, so an explicit "unknown" stratum is
    carried rather than dropping those reports, because dropping them would change the
    denominator.  Age is restricted to reports recorded in years, which is 60% of the total.
"""
from __future__ import annotations

import csv
import math
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
RES = ROOT / "results"
RES.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-4000000")

MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")

# ---------------------------------------------------------------- base sets
print("collecting ethambutol cases ...")
eth = {r[0] for r in con.execute(
    f"""SELECT DISTINCT d.caseid FROM drug d
        JOIN dedup_map m ON d.primaryid = m.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid AND dn.drug_seq = d.drug_seq
        WHERE {MATCH}""", ("%ETHAMBUTOL%", "%ETHAMBUTOL%"))}
n_total = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
print(f"  ethambutol cases : {len(eth):,}")
print(f"  whole database   : {n_total:,}")

OPTIC = ("OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
         "TOXIC OPTIC NEUROPATHY")
lst = ",".join(f"'{t}'" for t in OPTIC)
optic = {r[0] for r in con.execute(
    f"""SELECT DISTINCT o.caseid FROM ocular_case o
        WHERE UPPER(o.term) IN ({lst})""")}
print(f"  optic-nerve cases: {len(optic):,}")

# ---------------------------------------------------------------- patient attributes
print("reading patient attributes ...")
attr: dict[str, dict] = {}
for caseid, sex, age, age_cod, country, fda_dt, quarter in con.execute(
        """SELECT m.caseid, d.sex, d.age, d.age_cod, d.reporter_country, d.fda_dt, d.quarter
           FROM demo d JOIN dedup_map m ON d.primaryid = m.primaryid"""):
    s = (sex or "").strip().upper()
    sex_g = "Female" if s == "F" else "Male" if s == "M" else "Unknown"
    try:
        a = float(age)
    except (TypeError, ValueError):
        a = None
    if (age_cod or "").strip().upper() == "YR" and a is not None:
        band = ("0-17" if a < 18 else "18-44" if a < 45 else "45-64"
                if a < 65 else "65+")
    else:
        band = "Unknown"
    c = (country or "").strip().upper()
    if c in ("US", "USA", "PUERTO RICO"):
        region = "Americas"
    elif c in ("JP", "JAPAN", "CN", "CHINA", "KR", "KOREA, REPUBLIC OF",
               "SOUTH KOREA", "TW", "TAIWAN", "IN", "INDIA", "TH", "THAILAND",
               "PH", "PHILIPPINES", "MY", "MALAYSIA", "SG", "SINGAPORE",
               "ID", "INDONESIA", "VN", "VIET NAM", "HK", "HONG KONG"):
        region = "Asia"
    elif c in ("GB", "UNITED KINGDOM", "DE", "GERMANY", "FR", "FRANCE", "IT",
               "ITALY", "ES", "SPAIN", "NL", "NETHERLANDS", "BE", "BELGIUM",
               "SE", "SWEDEN", "CH", "SWITZERLAND", "AT", "AUSTRIA", "PL",
               "POLAND", "PT", "PORTUGAL", "DK", "DENMARK", "NO", "NORWAY",
               "FI", "FINLAND", "IE", "IRELAND", "CZ", "CZECHIA", "GR", "GREECE"):
        region = "Europe"
    elif c in ("BR", "BRAZIL", "ZA", "SOUTH AFRICA", "MX", "MEXICO", "AR",
               "ARGENTINA", "CO", "COLOMBIA", "PE", "PERU", "CL", "CHILE",
               "NG", "NIGERIA", "KE", "KENYA", "EG", "EGYPT", "ET", "ETHIOPIA",
               "TR", "TURKEY", "RU", "RUSSIAN FEDERATION", "UA", "UKRAINE"):
        region = "Other regions"
    else:
        region = "Other / unknown"
    y = None
    for tok in str(fda_dt or "").replace("-", " ").split():
        if len(tok) == 4 and tok.isdigit():
            y = int(tok)
            break
    if y is None:
        q = str(quarter or "")
        if len(q) >= 4 and q[:4].isdigit():
            y = int(q[:4])
    era = ("Unknown" if y is None else "2004-2016" if y <= 2016 else "2017-2026")
    attr[caseid] = {"sex": sex_g, "age_band": band, "region": region,
                    "era": era, "age": a}


def ror(a, b, c, d):
    if min(a, b, c, d) <= 0:
        return None
    or_ = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return or_, or_ * math.exp(-1.96 * se), or_ * math.exp(1.96 * se)


def ror_ci_from_counts(a, n_drug, n_event, n_all):
    b = n_drug - a
    c = n_event - a
    d = n_all - n_drug - c
    return ror(a, b, c, d)


rows = []
DIMENSIONS = [("sex", ["Female", "Male", "Unknown"]),
              ("age_band", ["0-17", "18-44", "45-64", "65+", "Unknown"]),
              ("region", ["Americas", "Asia", "Europe", "Other regions",
                          "Other / unknown"]),
              ("era", ["2004-2016", "2017-2026", "Unknown"])]

for dim, levels in DIMENSIONS:
    for lv in levels:
        sub = {k for k, v in attr.items() if v[dim] == lv}
        if not sub:
            continue
        drug_sub = eth & sub
        event_sub = optic & sub
        n_drug = len(drug_sub)
        n_event = len(event_sub)
        n_all = len(sub)
        a = len(drug_sub & event_sub)
        r = ror_ci_from_counts(a, n_drug, n_event, n_all)
        if r is None:
            rows.append({"dimension": dim, "level": lv, "cases": n_drug,
                         "optic_cases": a, "n_event_total": n_event, "n_stratum": n_all,
                         "ror": "", "ror_lcl": "", "ror_ucl": "", "note": "not estimable"})
            continue
        or_, lo, hi = r
        rows.append({"dimension": dim, "level": lv, "cases": n_drug,
                     "optic_cases": a, "n_event_total": n_event, "n_stratum": n_all,
                     "ror": round(or_, 2), "ror_lcl": round(lo, 2),
                     "ror_ucl": round(hi, 2), "note": ""})

print()
print("=" * 108)
print("Optic-nerve odds ratio within each subgroup")
print("=" * 108)
print(f"  {'dimension':10s} {'level':16s} {'cases':>7s} {'optic':>6s} "
      f"{'ROR':>9s} {'95% CI':>18s}")
for r in rows:
    ci = (f"{r['ror_lcl']}-{r['ror_ucl']}" if r["ror"] != "" else r["note"])
    print(f"  {r['dimension']:10s} {r['level']:16s} {r['cases']:>7,} {r['optic_cases']:>6,} "
          f"{str(r['ror']):>9s} {ci:>18s}")

# ---------------------------------------------------------------- ratio of odds ratios
print()
print("=" * 108)
print("Ratio of odds ratios, comparing each level with the reference level")
print("=" * 108)
print("""  Two strata can both be significant, or both null, and still differ.  The ratio of
  their odds ratios with an interval is what tests that, so it is reported rather than
  left to inspection.""")
comparisons = []
for dim, levels in DIMENSIONS:
    usable = [r for r in rows if r["dimension"] == dim and r["ror"] != ""]
    if len(usable) < 2:
        continue
    ref = usable[0]
    print(f"\n  {dim}  (reference: {ref['level']}, ROR {ref['ror']})")
    for r in usable[1:]:
        # ratio of odds ratios, with the variance of the log ROR summed
        lr = math.log(r["ror"]) - math.log(ref["ror"])
        se = math.sqrt(
            (math.log(r["ror_ucl"]) - math.log(r["ror"])) ** 2 / 1.96 ** 2 +
            (math.log(ref["ror_ucl"]) - math.log(ref["ror"])) ** 2 / 1.96 ** 2)
        lo, hi = math.exp(lr - 1.96 * se), math.exp(lr + 1.96 * se)
        flag = "" if lo <= 1 <= hi else "   <- differs"
        print(f"      {r['level']:16s} ROR ratio {math.exp(lr):.2f} "
              f"({lo:.2f}-{hi:.2f}){flag}")
        comparisons.append({"dimension": dim, "reference": ref["level"],
                            "level": r["level"], "ratio": round(math.exp(lr), 2),
                            "ratio_lcl": round(lo, 2), "ratio_ucl": round(hi, 2),
                            "differs": "" if lo <= 1 <= hi else "yes"})

with open(RES / "faers_subgroups.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
with open(RES / "faers_subgroup_contrasts.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=["dimension", "reference", "level", "ratio",
                                       "ratio_lcl", "ratio_ucl", "differs"])
    w.writeheader()
    w.writerows(comparisons)

print()
print(f"  -> {RES / 'faers_subgroups.csv'}")
print(f"  -> {RES / 'faers_subgroup_contrasts.csv'}")
differ = [c for c in comparisons if c["differs"] == "yes"]
print()
print(f"  contrasts whose interval excludes 1: {len(differ)} of {len(comparisons)}")
for c in differ:
    print(f"      {c['dimension']} {c['level']} vs {c['reference']}: "
          f"{c['ratio']} ({c['ratio_lcl']}-{c['ratio_ucl']})")
con.close()
