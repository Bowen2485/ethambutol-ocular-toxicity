# -*- coding: utf-8 -*-
"""
Find why the WHO and FAERS keys do not join.

The merge returned zero matched cells on both sides having plenty of data: the WHO
incidence indicator gave 5,177 rows and the FAERS query gave 927 country-year cells
covering 13,244 reports.  A join that returns nothing while both inputs are populated
means the keys differ in form, and guessing which form would be the third time in this
project that an assumed interface wasted a run.

So this prints the actual values.  What the WHO and FAERS columns look like is a fact to
be read, not inferred.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"

print("=" * 96)
print("1. WHO incidence file, as written")
print("=" * 96)
p = DERIVED / "who_TB_incidence_per100k.csv"
who = pd.read_csv(p)
print(f"  columns: {list(who.columns)}")
print(f"  rows   : {len(who):,}")
print()
for c in who.columns:
    nun = who[c].nunique(dropna=True)
    sample = who[c].dropna().unique()[:8]
    print(f"  {c:20s} {nun:>7,} distinct   sample: {list(sample)}")

print()
print("=" * 96)
print("2. FAERS country-year cells")
print("=" * 96)
con = sqlite3.connect(f"file:{DERIVED/'faers.sqlite'}?mode=ro", uri=True)
MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")
pats = ["%ETHAMBUTOL%", "%MYAMBUTOL%", "%DEXAMBUTOL%", "%ETAMBUTOL%"]
cond = " OR ".join([MATCH] * len(pats))
params = [p for pat in pats for p in (pat, pat)]
q = f"""SELECT UPPER(TRIM(dm.reporter_country)) AS cc,
               substr(dm.fda_dt,1,4) AS yr,
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
print(f"  rows: {len(emb):,}")
print(f"  cc   distinct: {emb.cc.nunique()}   sample: {sorted(emb.cc.unique())[:12]}")
print(f"  yr   distinct: {emb.yr.nunique()}   range: {emb.yr.min()} - {emb.yr.max()}")
print(f"  yr   dtype   : {emb.yr.dtype}")

print()
print("=" * 96)
print("3. Overlap in each key")
print("=" * 96)
who_cc = set(who["SpatialDim"].dropna().astype(str))
who_yr = set(pd.to_numeric(who["TimeDim"], errors="coerce").dropna().astype(int))
fa_cc = set(emb.cc.astype(str))
fa_yr = set(pd.to_numeric(emb.yr, errors="coerce").dropna().astype(int))
print(f"  country codes: WHO {len(who_cc)},  FAERS {len(fa_cc)},  "
      f"intersection {len(who_cc & fa_cc)}")
print(f"      WHO sample  : {sorted(who_cc)[:12]}")
print(f"      FAERS sample: {sorted(fa_cc)[:12]}")
print(f"  years: WHO {min(who_yr) if who_yr else '-'}-{max(who_yr) if who_yr else '-'}"
      f"  FAERS {min(fa_yr) if fa_yr else '-'}-{max(fa_yr) if fa_yr else '-'},  "
      f"intersection {len(who_yr & fa_yr)}")

print()
print("=" * 96)
print("4. If the codes differ, is there a mapping column?")
print("=" * 96)
# WHO indicators sometimes carry the country name in a separate dimension
for extra in ("Dim1", "Dim2", "Value"):
    if extra in who.columns:
        n = who[extra].nunique(dropna=True)
        print(f"  {extra}: {n:,} distinct   sample {list(who[extra].dropna().unique()[:6])}")

# and what the raw indicator response contains for one country
import json
import ssl
import urllib.request
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
cell = who[who["SpatialDim"].astype(str).str.len() == 3].head(3)
print()
print("  three-character WHO codes present:")
print("   ", list(cell["SpatialDim"].astype(str)))
print("  four-or-more-character WHO codes present (if any):")
long_codes = who[who["SpatialDim"].astype(str).str.len() > 3]
print("   ", list(long_codes["SpatialDim"].astype(str).unique()[:10]),
      f"({len(long_codes)} rows)")
