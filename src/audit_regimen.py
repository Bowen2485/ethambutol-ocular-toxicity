# -*- coding: utf-8 -*-
"""Re-verify the fixed-regimen contrast against the current cohort.

The rifampicin + isoniazid + pyrazinamide strata were computed on 2026-10-18; the review's point
about every number coming from one run applies to them too.  This recomputes the four strata and
the optic-nerve rate with versus without ethambutol, using the same case table as the main
analysis and both spellings of each optic-nerve term.
"""
from __future__ import annotations

import json
import math
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
con = sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True, timeout=30)

cases = {}
for drug in ("ethambutol", "isoniazid", "rifampicin", "pyrazinamide"):
    cases[drug] = {r[0] for r in con.execute(
        "SELECT DISTINCT caseid FROM drug_case WHERE drug = ?", (drug,))}
print({k: len(v) for k, v in cases.items()})

OPTIC_TERMS = ["Optic neuropathy", "Optic neuritis", "Optic atrophy", "Toxic optic neuropathy"]
variants = []
for t in OPTIC_TERMS:
    variants += [t, t.upper()]
ph = ",".join("?" * len(variants))
con.execute(f"CREATE TEMP TABLE opt AS SELECT DISTINCT r.primaryid FROM reac r "
            f"WHERE r.pt IN ({ph})", variants)
con.execute("CREATE INDEX temp.ix_opt ON opt(primaryid)")
optic_cases = {r[0] for r in con.execute(
    "SELECT DISTINCT m.caseid FROM opt o JOIN dedup_map m ON m.primaryid = o.primaryid")}
print(f"cases with any optic-nerve term: {len(optic_cases):,}")


def rate(case_set: set[str]) -> tuple[int, int]:
    n = len(case_set & optic_cases)
    return n, len(case_set)


def ratio(n1: int, d1: int, n0: int, d0: int):
    r1, r0 = n1 / d1, n0 / d0
    se = math.sqrt(1 / n1 - 1 / d1 + 1 / n0 - 1 / d0)
    rr = r1 / r0
    return rr, math.exp(math.log(rr) - 1.959964 * se), math.exp(math.log(rr) + 1.959964 * se)


triple = cases["rifampicin"] & cases["isoniazid"] & cases["pyrazinamide"]
with_emb = triple & cases["ethambutol"]
without_emb = triple - cases["ethambutol"]
n1, d1 = rate(with_emb)
n0, d0 = rate(without_emb)
rr, lo, hi = ratio(n1, d1, n0, d0)
print(f"RIF+INH+PZA with ethambutol: {n1}/{d1} ({100*n1/d1:.2f}%)")
print(f"RIF+INH+PZA without       : {n0}/{d0} ({100*n0/d0:.2f}%)")
print(f"rate ratio {rr:.2f} ({lo:.2f}-{hi:.2f})")

payload = {"strata": {"rifampicin+isoniazid+pyrazinamide+ethambutol": {"n_optic": n1, "n": d1},
                      "rifampicin+isoniazid+pyrazinamide": {"n_optic": n0, "n": d0}},
           "rate_ratio": rr, "rate_ratio_lcl": lo, "rate_ratio_ucl": hi,
           "optic_terms": OPTIC_TERMS}
(ROOT / "results" / "audit_regimen.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
con.close()
