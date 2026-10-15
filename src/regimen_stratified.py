# -*- coding: utf-8 -*-
"""
Correct the within-class comparison for co-administration.

The problem being corrected
    The drugs in a tuberculosis regimen are reported together.  Among ethambutol cases,
    71.1% also name rifampicin, 54.9% isoniazid and 48.8% pyrazinamide; and the
    asymmetry runs both ways, since 73.3% of pyrazinamide cases name ethambutol while
    only 48.8% of ethambutol cases name pyrazinamide.  So the apparent contrast
    "pyrazinamide 0.67% versus ethambutol 1.25% optic neuropathy" contrasts two
    differently-sized subsets of largely the same patients, not two exposures.  A drug
    cannot be compared with another drug when most reports contain both.

Three analyses that do hold the regimen fixed
    1. Regimen strata.  Partition every antitubercular case by which first-line drugs it
       names and compare the optic-nerve rate between strata that differ only by the
       presence of ethambutol.  Within a stratum the background is held constant by
       construction.
    2. Fixed-regimen proportions.  Restrict to reports naming rifampicin, isoniazid and
       pyrazinamide and compare those that also name ethambutol with those that do not.
    3. Isoniazid without ethambutol.  Isoniazid is also given alone for latent
       tuberculosis, an exposure that shares the tuberculosis indication and the health
       system but contains no ethambutol.

What this cannot do
    None of it removes confounding by indication, because the regimen a patient receives
    reflects how sick they are and how long they have been treated.  Analysis 1 removes
    confounding *within* a stratum; analysis 3 removes the disease entirely but replaces
    it with a different disease state, since latent infection is not active tuberculosis.
    Both limits are reported.
"""
from __future__ import annotations

import collections
import csv
import itertools
import math
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
RESULTS = ROOT / "results"

DRUGS = {
    "ethambutol": ["%ETHAMBUTOL%", "%DEXAMBUTOL%", "%MYAMBUTOL%", "%ETAMBUTOL%"],
    "isoniazid": ["%ISONIAZID%", "%ISONICOTINYLHYDRAZINE%", "%INH%"],
    "rifampicin": ["%RIFAMPICIN%", "%RIFAMPIN%", "%RIFADIN%", "%RIFAMYCIN%"],
    "pyrazinamide": ["%PYRAZINAMIDE%"],
}
FIRST_LINE = ["rifampicin", "isoniazid", "pyrazinamide"]
#: optic-nerve terms as used throughout the paper
OPTIC = ["OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
         "TOXIC OPTIC NEUROPATHY"]
#: terms expected to be null, for the same internal contrast
CONTROLS = ["CATARACT", "DRY EYE", "EYE PAIN", "GLAUCOMA"]

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-2000000")
MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")


def cases_for(pats: list[str]) -> set[str]:
    cond = " OR ".join([MATCH] * len(pats))
    params = [p for pat in pats for p in (pat, pat)]
    q = f"""SELECT DISTINCT d.caseid FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE {cond}"""
    return {r[0] for r in con.execute(q, params)}


def cases_with_terms(terms: list[str]) -> set[str]:
    lst = ",".join(f"'{t}'" for t in terms)
    q = f"""SELECT DISTINCT r.caseid FROM reac r
            JOIN dedup_map m ON r.primaryid = m.primaryid
            WHERE UPPER(r.pt) IN ({lst})"""
    return {r[0] for r in con.execute(q)}


print("[collecting case sets]")
sets = {k: cases_for(v) for k, v in DRUGS.items()}
for k, v in sets.items():
    print(f"    {k:14s} {len(v):>9,}")
optic = cases_with_terms(OPTIC)
controls = {c: cases_with_terms([c]) for c in CONTROLS}
for c, v in controls.items():
    print(f"    {c:14s} {len(v):>9,}  (control term)")
print(f"    {'optic (any)':14s} {len(optic):>9,}  (optic-nerve composite)")
con.close()

# every case in any of the four drugs is a tuberculosis-treatment case
att = set().union(*sets.values())
print(f"\n  cases naming at least one first-line drug: {len(att):,}")
print(f"  of which with an optic-nerve term:         {len(att & optic):,} "
      f"({100*len(att & optic)/max(len(att),1):.2f}%)")

rows = []

# ---------------------------------------------------------------- analysis 1
print()
print("=" * 100)
print("1. Regimen strata: the optic-nerve rate with and without ethambutol")
print("=" * 100)
print("  Within a stratum every case names the same first-line drugs, so the")
print("  background regimen is held constant by construction.\n")
print(f"  {'stratum (first-line drugs named)':46s} {'n':>8s} "
      f"{'optic':>7s} {'rate %':>7s}   {'controls':>9s}")
strata = {}
for r in range(0, len(FIRST_LINE) + 1):
    for combo in itertools.combinations(FIRST_LINE, r):
        members = {c for c in att
                   if all(c in sets[d] for d in combo)
                   and not any(c in sets[d] for d in FIRST_LINE
                               if d not in combo)}
        if len(members) < 50:
            continue
        with_emb = {c for c in members if c in sets["ethambutol"]}
        without = members - with_emb
        ctrl_hits = sum(1 for c in members if any(c in v for v in controls.values()))
        label = " + ".join(combo) if combo else "(no first-line drug named)"
        strata[tuple(combo)] = (len(members), with_emb, without)
        rate = 100 * len(members & optic) / len(members)
        print(f"  {label:46s} {len(members):>8,} {len(members & optic):>7,} "
              f"{rate:>7.2f}   {ctrl_hits:>9,}")

print()
print("  Strata that contain some cases with ethambutol and some without, which is")
print("  where a like-for-like comparison is possible:")
print(f"  {'stratum':46s} {'with EMB':>17s} {'without EMB':>17s} {'ratio':>8s}")
for combo in sorted(strata, key=lambda k: -strata[k][0]):
    n, with_emb, without = strata[combo]
    if len(with_emb) < 100 or len(without) < 100:
        continue
    a = len(with_emb & optic)
    b = len(without & optic)
    ra = 100 * a / len(with_emb)
    rb = 100 * b / len(without)
    ratio = ra / rb if rb > 0 else float("nan")
    label = " + ".join(combo) if combo else "(none)"
    print(f"  {label:46s} {a:>6}/{len(with_emb):<10,} {b:>6}/{len(without):<10,} "
          f"{ratio:>8.2f}")
    # Woolf interval on the rate ratio
    if a and b and len(with_emb) > a and len(without) > b:
        se = math.sqrt(1/a - 1/len(with_emb) + 1/b - 1/len(without))
        lo, hi = ratio * math.exp(-1.96*se), ratio * math.exp(1.96*se)
        print(f"  {'':46s} {'':>17s} {'':>17s} "
              f"95% CI {lo:.2f}-{hi:.2f}")
    rows.append({"analysis": "regimen stratum", "stratum": label,
                 "n_with_ethambutol": len(with_emb), "optic_with": a,
                 "n_without_ethambutol": len(without), "optic_without": b,
                 "rate_ratio": round(ratio, 3) if math.isfinite(ratio) else "",
                 "rate_with_pct": round(ra, 3), "rate_without_pct": round(rb, 3)})

# ---------------------------------------------------------------- analysis 2
print()
print("=" * 100)
print("2. Fixed-regimen comparison: RIPE-style reports with and without ethambutol")
print("=" * 100)
core = {c for c in att
        if all(c in sets[d] for d in FIRST_LINE)}
core_with = {c for c in core if c in sets["ethambutol"]}
core_without = core - core_with
print(f"  reports naming rifampicin + isoniazid + pyrazinamide : {len(core):,}")
print(f"      of which also naming ethambutol                   : {len(core_with):,}")
print(f"      of which not naming ethambutol                    : {len(core_without):,}")
for name, group in (("with ethambutol", core_with), ("without ethambutol", core_without)):
    n = len(group)
    o = len(group & optic)
    print(f"  {name:22s} optic {o:>5} / {n:>7,}  = {100*o/max(n,1):.2f}%")
    for c in CONTROLS:
        k = len(group & controls[c])
        print(f"      {c:12s} {k:>5} / {n:>7,}  = {100*k/max(n,1):.2f}%")
a = len(core_with & optic)
b = len(core_without & optic)
if a and b:
    ra, rb = a/len(core_with), b/len(core_without)
    ratio = ra / rb if rb else float("nan")
    se = math.sqrt(1/a - 1/len(core_with) + 1/b - 1/len(core_without))
    lo, hi = ratio*math.exp(-1.96*se), ratio*math.exp(1.96*se)
    print()
    print(f"  rate ratio (with vs without ethambutol): {ratio:.2f} "
          f"(95% CI {lo:.2f}-{hi:.2f})")
    rows.append({"analysis": "fixed regimen (RIP +/- E)", "stratum": "RIP base",
                 "n_with_ethambutol": len(core_with), "optic_with": a,
                 "n_without_ethambutol": len(core_without), "optic_without": b,
                 "rate_ratio": round(ratio, 3), "rate_with_pct": round(100*ra, 3),
                 "rate_without_pct": round(100*rb, 3)})

# ---------------------------------------------------------------- analysis 3
print()
print("=" * 100)
print("3. Isoniazid without ethambutol, as an active comparator")
print("=" * 100)
inh_only = {c for c in sets["isoniazid"]
            if c not in sets["ethambutol"] and c not in sets["rifampicin"]}
inh_emb = sets["isoniazid"] & sets["ethambutol"]
print(f"  isoniazid named, ethambutol and rifampicin not : {len(inh_only):,}")
print(f"  isoniazid and ethambutol both named            : {len(inh_emb):,}")
for name, group in (("isoniazid alone", inh_only),
                    ("isoniazid + ethambutol", inh_emb)):
    n = len(group)
    o = len(group & optic)
    print(f"  {name:26s} optic {o:>5} / {n:>7,}  = {100*o/max(n,1):.2f}%")
    for c in CONTROLS:
        k = len(group & controls[c])
        print(f"      {c:12s} {k:>5} / {n:>7,}  = {100*k/max(n,1):.2f}%")
a = len(inh_emb & optic)
b = len(inh_only & optic)
if a and b:
    ra, rb = a/len(inh_emb), b/len(inh_only)
    ratio = ra/rb if rb else float("nan")
    se = math.sqrt(1/a - 1/len(inh_emb) + 1/b - 1/len(inh_only))
    lo, hi = ratio*math.exp(-1.96*se), ratio*math.exp(1.96*se)
    print()
    print(f"  rate ratio (+ethambutol vs isoniazid alone): {ratio:.2f} "
          f"(95% CI {lo:.2f}-{hi:.2f})")
    rows.append({"analysis": "isoniazid +/- ethambutol", "stratum": "INH base",
                 "n_with_ethambutol": len(inh_emb), "optic_with": a,
                 "n_without_ethambutol": len(inh_only), "optic_without": b,
                 "rate_ratio": round(ratio, 3), "rate_with_pct": round(100*ra, 3),
                 "rate_without_pct": round(100*rb, 3)})

out = RESULTS / "faers_regimen_strata.csv"
if rows:
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n-> {out}")
print()
print("=" * 100)
print("Reading")
print("=" * 100)
print("""  A rate ratio above 1 within a fixed-regimen stratum is the corrected statement of
  what the naive within-class table suggested: reports naming ethambutol carry
  optic-nerve terms more often than reports naming the same other drugs without it.
  The isoniazid-alone comparison is the closest thing to an active control available,
  with the caveat that latent infection is not active tuberculosis.""")
