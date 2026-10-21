# -*- coding: utf-8 -*-
"""Fix the two numerical problems the review raised, from the warehouse.

1. The period-specific ROR used the whole-database N in the d cell.  Within a single period the
   correct reference population is that period's de-duplicated cases, not all 20.7 million, so
   the published 379.28 and 171.17 are inflated by roughly the ratio of the database to the
   period.  This script recomputes each period's 2x2 with the period's own denominator.

2. Methods promised a strict whole-token exposure match and Results never reported it.  The
   cohort and the optic-neuropathy estimate are computed here so that the promise can be kept
   with a real number, or dropped if the definition does not change the cohort.

Writes results/audit_period_strict.json.
"""
from __future__ import annotations

import json
import math
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
con = sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True, timeout=30)

con.execute("CREATE TEMP TABLE dm AS SELECT caseid, primaryid FROM dedup_map")
con.execute("CREATE INDEX temp.ix_dm_pid ON dm(primaryid)")
con.execute("CREATE INDEX temp.ix_dm_cid ON dm(caseid)")
con.execute("CREATE TEMP TABLE eth AS SELECT DISTINCT caseid FROM drug_case WHERE drug='ethambutol'")
con.execute("CREATE INDEX temp.ix_eth ON eth(caseid)")

N = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
n_eth = con.execute("SELECT COUNT(*) FROM eth").fetchone()[0]
SPELL = ("Optic neuropathy", "OPTIC NEUROPATHY")


def ror(a, b, c, d):
    if min(a, b, c, d) <= 0:
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    est = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return est, math.exp(math.log(est) - 1.959964 * se), math.exp(math.log(est) + 1.959964 * se)


print(f"N={N:,}  ethambutol={n_eth:,}")

#: whole-database optic-neuropathy cases per period (the c cell)
con.execute("CREATE TEMP TABLE hits AS SELECT DISTINCT primaryid FROM reac WHERE pt IN (?,?)", SPELL)
con.execute("CREATE INDEX temp.ix_hits ON hits(primaryid)")

out = {"periods": {}, "strict": {}}
for label, (lo, hi) in {"2004-2016": ("2004", "2016"), "2017-2026": ("2017", "2026")}.items():
    cond = f"substr(de.fda_dt,1,4) BETWEEN '{lo}' AND '{hi}'"
    n_period = con.execute(
        f"SELECT COUNT(DISTINCT m.caseid) FROM dm m JOIN demo de ON de.primaryid = m.primaryid "
        f"WHERE {cond}").fetchone()[0]
    n_drug = con.execute(
        f"SELECT COUNT(DISTINCT e.caseid) FROM eth e JOIN dm m ON m.caseid = e.caseid "
        f"JOIN demo de ON de.primaryid = m.primaryid WHERE {cond}").fetchone()[0]
    n_event = con.execute(
        f"SELECT COUNT(DISTINCT m.caseid) FROM hits h JOIN dm m ON m.primaryid = h.primaryid "
        f"JOIN demo de ON de.primaryid = m.primaryid WHERE {cond}").fetchone()[0]
    a = con.execute(
        f"SELECT COUNT(DISTINCT m.caseid) FROM hits h JOIN dm m ON m.primaryid = h.primaryid "
        f"JOIN eth e ON e.caseid = m.caseid JOIN demo de ON de.primaryid = m.primaryid "
        f"WHERE {cond}").fetchone()[0]
    b, c, dd = n_drug - a, n_event - a, n_period - n_drug - n_event + a
    est, lo_ci, hi_ci = ror(a, b, c, dd)
    out["periods"][label] = {"N_period": n_period, "n_drug": n_drug, "n_event": n_event,
                             "a": a, "b": b, "c": c, "d": dd, "ror": est, "ror_lcl": lo_ci,
                             "ror_ucl": hi_ci,
                             "pct_eth": 100 * a / n_drug,
                             "pct_other": 100 * c / (n_period - n_drug)}
    print(f"{label}: N_period={n_period:,} cases={n_drug:,} a={a} c={c} d={dd:,} "
          f"ROR={est:.2f} ({lo_ci:.2f}-{hi_ci:.2f})  "
          f"pct_eth={100*a/n_drug:.2f}%  pct_other={100*c/(n_period-n_drug):.4f}%")

#: strict whole-token match, tried in the two spellings the drug table uses
for spelling in ("ETHAMBUTOL", "Ethambutol"):
    n_strict = con.execute(
        "SELECT COUNT(DISTINCT m.caseid) FROM drug d JOIN dm m ON d.primaryid = m.primaryid "
        "WHERE d.substance = ?", (spelling,)).fetchone()[0]
    print(f"strict substance {spelling!r}: {n_strict:,} cases")

n_strict = con.execute(
    "SELECT COUNT(DISTINCT m.caseid) FROM drug d JOIN dm m ON d.primaryid = m.primaryid "
    "WHERE d.substance IN ('ETHAMBUTOL','Ethambutol')").fetchone()[0]
a_strict = con.execute(
    "SELECT COUNT(DISTINCT m.caseid) FROM reac r JOIN dm m ON m.primaryid = r.primaryid "
    "JOIN drug d ON d.primaryid = r.primaryid "
    "WHERE r.pt IN (?,?) AND d.substance IN ('ETHAMBUTOL','Ethambutol')", SPELL).fetchone()[0]
b, c, dd = n_strict - a_strict, 2072 - a_strict, N - n_strict - 2072 + a_strict
est, lo_ci, hi_ci = ror(a_strict, b, c, dd)
out["strict"] = {"n_drug": n_strict, "a": a_strict, "n_event": 2072,
                 "ror": est, "ror_lcl": lo_ci, "ror_ucl": hi_ci}
print(f"strict whole-token: cases={n_strict:,} a={a_strict} ROR={est:.2f} ({lo_ci:.2f}-{hi_ci:.2f})")

out["N"] = N
out["n_ethambutol"] = n_eth
(ROOT / "results" / "audit_period_strict.json").write_text(json.dumps(out, indent=2),
                                                          encoding="utf-8")
print("\nwritten results/audit_period_strict.json")
con.close()
