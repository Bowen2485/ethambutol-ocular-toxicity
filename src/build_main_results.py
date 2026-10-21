# -*- coding: utf-8 -*-
"""Rebuild every number the restructured paper needs, from the warehouse, in one place.

Why this script exists
    The audit found that several derived tables were built with a case-sensitive term match.
    The PT "Optic neuropathy" exists in reac in two spellings - 1,626 cases as "Optic
    neuropathy" and 446 as "OPTIC NEUROPATHY" - so a matcher that looked for one spelling
    counted a=151 instead of a=165 and reported ROR 105.81 instead of 116.58.  Other tables
    (temporal split, drug controls) were also built before the 2026Q2 archive was ingested and
    still cumulate to the old 13,836-case cohort.

    Rather than patch each stale file, this script recomputes the whole evidence base against
    the current warehouse, matching every MedDRA term in both spellings, and writes a single
    results/main_results.json.  The manuscript, the tables and the figures all read that file.

What it computes
    case flow                      submitted -> de-duplicated -> ethambutol -> suspect -> dated
    11 ocular SMQs                 n_event, a, ROR and CI, BH across the eleven
    optic-nerve PTs and controls   the PT-level detail and the pre-specified non-specific terms
    sensitivity                    all roles vs primary/secondary suspect, whole database
    temporal split                 receipt year <= 2016 vs >= 2017, from demo.fda_dt
    fixed-regimen contrast         re-uses results/faers_regimen_strata.csv (unchanged source)
"""
from __future__ import annotations

import json
import math
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
RES = ROOT / "results"

con = sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True, timeout=30)

#: dedup_map carries no index in this warehouse, and joining it repeatedly turned each 2x2 into
#: a full scan of 20.7 million rows.  A temporary indexed copy makes every query below an index
#: seek; the copy costs one pass and is reused by all of them.
con.execute("CREATE TEMP TABLE dm AS SELECT caseid, primaryid FROM dedup_map")
con.execute("CREATE INDEX temp.ix_dm_pid ON dm(primaryid)")
con.execute("CREATE INDEX temp.ix_dm_cid ON dm(caseid)")

#: exposure cohort: every de-duplicated case naming ethambutol anywhere in its drug records
con.execute("CREATE TEMP TABLE eth AS SELECT DISTINCT caseid FROM drug_case WHERE drug = 'ethambutol'")
con.execute("CREATE INDEX temp.ix_eth ON eth(caseid)")
con.execute("CREATE TEMP TABLE eth_ps AS SELECT DISTINCT caseid FROM drug_case "
            "WHERE drug = 'ethambutol' AND role_cod IN ('PS','SS')")
con.execute("CREATE INDEX temp.ix_eth_ps ON eth_ps(caseid)")

N = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
n_eth = con.execute("SELECT COUNT(*) FROM eth").fetchone()[0]
n_eth_ps = con.execute("SELECT COUNT(*) FROM eth_ps").fetchone()[0]
print(f"N={N:,}  ethambutol(all roles)={n_eth:,}  suspect={n_eth_ps:,}")


def variants(term: str) -> list[str]:
    """Every spelling the warehouse actually uses for a PT: canonical and all-uppercase."""
    t = term.strip()
    return sorted({t, t.upper()})


def ror_ci(a: float, b: float, c: float, d: float, z: float = 1.959964):
    if min(a, b, c, d) <= 0:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    est = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return est, math.exp(math.log(est) - z * se), math.exp(math.log(est) + z * se)


def counts(terms: list[str], cohort: str = "eth", roles: str = "all") -> tuple[int, int]:
    """(n_event in the whole database, a in the exposure cohort) for a set of PTs.

    The hits are materialised first.  Written as one joined statement, SQLite chose to scan the
    20.7-million-row de-duplication table and probe the reaction table for each row, which ran
    for half an hour without finishing; materialising the (small) set of matching report ids and
    joining that against the indexed map takes seconds.
    """
    inlist: list[str] = []
    for t in terms:
        inlist.extend(variants(t))
    ph = ",".join("?" * len(inlist))
    con.execute("DROP TABLE IF EXISTS temp.hits")
    con.execute(f"CREATE TEMP TABLE hits AS SELECT DISTINCT primaryid FROM reac "
                f"WHERE pt IN ({ph})", inlist)
    con.execute("CREATE INDEX temp.ix_hits ON hits(primaryid)")
    n_event = con.execute(
        "SELECT COUNT(DISTINCT m.caseid) FROM hits h JOIN dm m ON m.primaryid = h.primaryid"
    ).fetchone()[0]
    table = "eth" if roles == "all" else "eth_ps"
    a = con.execute(
        f"SELECT COUNT(DISTINCT m.caseid) FROM hits h JOIN dm m ON m.primaryid = h.primaryid "
        f"JOIN {table} e ON e.caseid = m.caseid").fetchone()[0]
    return int(n_event), int(a)


def bh(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    q = np.empty_like(p)
    m = len(p)
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = order[rank]
        prev = min(prev, p[i] * m / (rank + 1))
        q[i] = prev
    return q.tolist()


# ------------------------------------------------------------------ SMQ level
smq = json.loads((RES / "faers_smq_ocular.json").read_text(encoding="utf-8"))
smq_rows = []
for r in smq["results"]:
    n_event, a = counts(r["terms"])
    print(f"  [smq] {r['smq']:<32} a={a:>4} n={n_event:>7,}", flush=True)
    b, c, d = n_eth - a, n_event - a, N - n_eth - n_event + a
    est, lo, hi = ror_ci(a, b, c, d)
    #: two-sided p for the 2x2, via the chi-square statistic without correction
    stat = (a * d - b * c) ** 2 * (a + b + c + d) / ((a + b) * (c + d) * (a + c) * (b + d))
    p = float(chi2.sf(stat, 1))
    _, a_ps = counts(r["terms"], roles="suspect")
    smq_rows.append({"smq": r["smq"], "narrow_terms": r["narrow_terms"], "a": a,
                     "n_event": n_event, "n_drug": n_eth, "ror": est, "ror_lcl": lo, "ror_ucl": hi,
                     "p": p, "a_suspect": a_ps,
                     "ror_suspect": ror_ci(a_ps, n_eth_ps - a_ps, n_event - a_ps,
                                           N - n_eth_ps - n_event + a_ps)[0]})
q = bh([r["p"] for r in smq_rows])
for r, qv in zip(smq_rows, q):
    r["q_bh"] = qv

smq_df = pd.DataFrame(smq_rows).sort_values("ror", ascending=False)
smq_df.to_csv(RES / "main_smq.csv", index=False, encoding="utf-8-sig")
print("\nSMQ level:")
for r in smq_rows:
    print(f"  {r['smq']:32s} a={r['a']:>4} n={r['n_event']:>7,} "
          f"ROR={r['ror']:7.2f} ({r['ror_lcl']:.2f}-{r['ror_ucl']:.2f}) q={r['q_bh']:.2g}")

# ------------------------------------------------------------ PT-level detail
OPTIC = ["Optic neuropathy", "Optic neuritis", "Toxic optic neuropathy", "Optic atrophy",
         "Papilloedema", "Optic nerve disorder", "Optic nerve injury",
         "Visual evoked potentials abnormal", "Optic disc hyperaemia"]
CONTROLS = ["Cataract", "Dry eye", "Eye pain", "Glaucoma", "Conjunctivitis", "Vision blurred"]

pt_rows = []
for term in OPTIC + CONTROLS:
    n_event, a = counts([term])
    b, c, d = n_eth - a, n_event - a, N - n_eth - n_event + a
    est, lo, hi = ror_ci(a, b, c, d)
    _, a_ps = counts([term], roles="suspect")
    pt_rows.append({"term": term, "group": "optic nerve" if term in OPTIC else "control",
                    "a": a, "n_event": n_event, "ror": est, "ror_lcl": lo, "ror_ucl": hi,
                    "a_suspect": a_ps,
                    "ror_suspect": ror_ci(a_ps, n_eth_ps - a_ps, n_event - a_ps,
                                          N - n_eth_ps - n_event + a_ps)[0]})
#: BH across the tested panel uses the two-sided chi-square p of each 2x2
pv = []
for r in pt_rows:
    a, n_event = r["a"], r["n_event"]
    b, c, d = n_eth - a, n_event - a, N - n_eth - n_event + a
    stat = (a * d - b * c) ** 2 * (a + b + c + d) / ((a + b) * (c + d) * (a + c) * (b + d))
    pv.append(float(chi2.sf(stat, 1)))
for r, qv, pval in zip(pt_rows, bh(pv), pv):
    r["p"] = pval
    r["q_bh"] = qv
pt_df = pd.DataFrame(pt_rows)
pt_df.to_csv(RES / "main_pt.csv", index=False, encoding="utf-8-sig")
print("\nPT level:")
for r in pt_df.itertuples():
    print(f"  {r.term:34s} a={r.a:>4} n={r.n_event:>7,} ROR={r.ror:8.2f} "
          f"({r.ror_lcl:.2f}-{r.ror_ucl:.2f}) q={r.q_bh:.2g}")

# ------------------------------------------------------------------ temporal
def period_counts(lo: int, hi: int) -> dict:
    cond = f"substr(de.fda_dt,1,4) BETWEEN '{lo}' AND '{hi}'"
    con.execute("DROP TABLE IF EXISTS temp.hits2")
    con.execute("CREATE TEMP TABLE hits2 AS SELECT DISTINCT primaryid FROM reac "
                "WHERE pt IN (?,?)", variants("Optic neuropathy"))
    con.execute("CREATE INDEX temp.ix_hits2 ON hits2(primaryid)")
    n_eth_p = con.execute(
        f"SELECT COUNT(DISTINCT e.caseid) FROM eth e JOIN dm m ON m.caseid = e.caseid "
        f"JOIN demo de ON de.primaryid = m.primaryid WHERE {cond}").fetchone()[0]
    n_ev = con.execute(
        f"SELECT COUNT(DISTINCT m.caseid) FROM hits2 h JOIN dm m ON m.primaryid = h.primaryid "
        f"JOIN demo de ON de.primaryid = m.primaryid WHERE {cond}").fetchone()[0]
    a = con.execute(
        f"SELECT COUNT(DISTINCT m.caseid) FROM hits2 h JOIN dm m ON m.primaryid = h.primaryid "
        f"JOIN eth e ON e.caseid = m.caseid JOIN demo de ON de.primaryid = m.primaryid "
        f"WHERE {cond}").fetchone()[0]
    return {"n_drug": int(n_eth_p), "n_event": int(n_ev), "a": int(a)}


periods = {"2004-2016": period_counts(2004, 2016), "2017-2026": period_counts(2017, 2026)}
for name, p in periods.items():
    b, c, d = p["n_drug"] - p["a"], p["n_event"] - p["a"], N - p["n_drug"] - p["n_event"] + p["a"]
    p["ror"], p["ror_lcl"], p["ror_ucl"] = ror_ci(p["a"], b, c, d)
    print(f"\ntemporal {name}: cases={p['n_drug']:,} a={p['a']} n_event={p['n_event']:,} "
          f"ROR={p['ror']:.2f} ({p['ror_lcl']:.2f}-{p['ror_ucl']:.2f})")

# ---------------------------------------------------------------- case flow
flow = {
    "submitted_reports": con.execute("SELECT COUNT(*) FROM demo").fetchone()[0],
    "de_duplicated_cases": N,
    "ethambutol_any_role": n_eth,
    "ethambutol_suspect_ps_ss": n_eth_ps,
    "ethambutol_primary_suspect": con.execute(
        "SELECT COUNT(DISTINCT caseid) FROM drug_case WHERE drug='ethambutol' "
        "AND role_cod='PS'").fetchone()[0],
    "ethambutol_concomitant_only": n_eth - n_eth_ps,
}

payload = {
    "generated_by": "src/build_main_results.py",
    "main_specification": {
        "exposure": "ethambutol anywhere in the drug records of the surviving case version, any role",
        "outcome": "MedDRA 29.0 narrow SMQ or preferred term, matched in canonical and upper-case spelling",
        "denominator": "all de-duplicated FAERS cases, 2004Q1-2026Q2",
        "metric": "ROR with Woolf 95% CI; BH across the eleven ocular SMQs and across the tested PT panel",
    },
    "N": N, "n_ethambutol": n_eth, "n_ethambutol_suspect": n_eth_ps,
    "case_flow": flow,
    "smq": smq_rows,
    "pt": pt_rows,
    "temporal": periods,
}

out = RES / "main_results.json"
out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
pd.DataFrame([flow]).T.rename(columns={0: "n"}).to_csv(RES / "case_flow.csv", encoding="utf-8-sig")
print(f"\nwritten {out.relative_to(ROOT)}")
con.close()
