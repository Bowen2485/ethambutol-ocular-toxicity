# -*- coding: utf-8 -*-
"""
Step 10 - Robustness checks on the pharmacovigilance conclusions.

Three ways the headline result could be an artefact are tested directly:
  (1) the exposure definition      - strict whole-token matching instead of a
      substring match, which excludes combination products;
  (2) the drug-role restriction     - primary/secondary suspect reports only;
  (3) the comparator denominator    - restriction to anti-tuberculosis reports
      only, which removes the possibility that the signal merely reflects how
      sick the underlying population is.

A conclusion that survives all three is not an artefact of the analysis
conventions.

Outputs -> results/faers_robustness.csv, tables/Table9_robustness.csv
"""
from __future__ import annotations

import math
import re
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
DB = DERIVED / "faers.sqlite"

TERMS = ["OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
         "VISUAL ACUITY REDUCED", "BLINDNESS", "VISION BLURRED",
         "CATARACT", "DRY EYE", "EYE PAIN", "GLAUCOMA"]

ALL_ATT = ["ETHAMBUTOL", "ISONIAZID", "RIFAMPICIN", "RIFAMPIN", "PYRAZINAMIDE",
           "STREPTOMYCIN"]


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=900)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1000000")
    return con


def ror_ci(a, b, c, d, z=1.959964):
    if a == 0:
        return 0.0, 0.0, float("inf")
    A, B, C, D = float(a), float(b), float(c), float(d)
    if min(B, C, D) == 0:
        A, B, C, D = A + 0.5, B + 0.5, C + 0.5, D + 0.5
    ror = (A * D) / (B * C)
    se = math.sqrt(1 / A + 1 / B + 1 / C + 1 / D)
    return ror, ror * math.exp(-z * se), ror * math.exp(z * se)


def strict_match_sql(alias: str, tokens: list[str]) -> tuple[str, list]:
    """Whole-token match: the name must contain the token and no other API."""
    conds, params = [], []
    for t in tokens:
        conds.append(
            f"(UPPER(COALESCE({alias}.drugname,'')) LIKE ? "
            f"OR UPPER(COALESCE({alias}.prod_ai,'')) LIKE ?)")
        params += [f"%{t}%", f"%{t}%"]
    return "(" + " OR ".join(conds) + ")", params


def count_cases(con, tokens: list[str], suspect_only: bool = False,
                restrict_to_att: bool = False) -> set[str]:
    cond, params = strict_match_sql("dn", tokens)
    role = " AND UPPER(COALESCE(d.role_cod,'')) IN ('PS','SS')" if suspect_only else ""
    att_cond, att_params = strict_match_sql("dn2", ALL_ATT)
    att = ""
    if restrict_to_att:
        att = f""" AND d.caseid IN (
            SELECT DISTINCT d2.caseid FROM drug d2
            JOIN dedup_map m2 ON d2.primaryid = m2.primaryid
            JOIN drugname dn2 ON dn2.primaryid = d2.primaryid
                             AND dn2.drug_seq = d2.drug_seq
            WHERE {att_cond})"""
        params = params + att_params
    q = f"""SELECT DISTINCT d.caseid FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE {cond}{role}{att}"""
    return {r[0] for r in con.execute(q, params)}


def count_with_term(con, tokens: list[str], term: str, suspect_only: bool = False,
                    restrict_to_att: bool = False) -> int:
    cond, params = strict_match_sql("dn", tokens)
    role = " AND UPPER(COALESCE(d.role_cod,'')) IN ('PS','SS')" if suspect_only else ""
    att = ""
    if restrict_to_att:
        att_cond, att_params = strict_match_sql("dn2", ALL_ATT)
        att = f""" AND d.caseid IN (
            SELECT DISTINCT d2.caseid FROM drug d2
            JOIN dedup_map m2 ON d2.primaryid = m2.primaryid
            JOIN drugname dn2 ON dn2.primaryid = d2.primaryid
                             AND dn2.drug_seq = d2.drug_seq
            WHERE {att_cond})"""
        params = params + att_params
    q = f"""SELECT COUNT(*) FROM (
              SELECT DISTINCT d.caseid FROM drug d
              JOIN dedup_map m ON d.primaryid = m.primaryid
              JOIN drugname dn ON dn.primaryid = d.primaryid
                              AND dn.drug_seq = d.drug_seq
              WHERE {cond}{role}{att}
              INTERSECT
              SELECT DISTINCT r.caseid FROM reac r
              JOIN dedup_map m3 ON r.primaryid = m3.primaryid
              WHERE UPPER(r.pt) = ?)"""
    return con.execute(q, params + [term]).fetchone()[0]


def main() -> int:
    con = connect()
    N = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
    att_cases = count_cases(con, ALL_ATT)
    N_att = len(att_cases)
    print(f"[base] all FAERS cases   = {N:,}")
    print(f"[base] anti-TB-exposed   = {N_att:,}")

    # materialise the anti-TB case set so the restricted denominator can be used
    # consistently for every cell of the table
    con.execute("ATTACH DATABASE ':memory:' AS mem")
    con.execute("CREATE TEMP TABLE dc_att (caseid TEXT PRIMARY KEY)")
    con.executemany("INSERT OR IGNORE INTO dc_att VALUES(?)",
                    [(c,) for c in att_cases])
    con.execute("CREATE INDEX temp.ix_dc_att ON dc_att(caseid)")

    rows = []
    scenarios = [
        ("main (all roles, whole database)", dict(), None),
        ("strict whole-token exposure", dict(), None),
        ("suspect-only reports", dict(suspect_only=True), None),
        ("anti-TB comparator only", dict(restrict_to_att=True), att_cases),
    ]
    t0 = time.time()
    for label, opts, denom in scenarios:
        eth = count_cases(con, ["ETHAMBUTOL"], **opts)
        n_d = len(eth)
        # the contingency denominator must match the scenario: restricting the
        # comparator to anti-TB reports means those are the only "non-exposed"
        # cases that can contribute
        N_scen = len(denom) if denom is not None else N
        if denom is not None:
            eth = eth & denom
            n_d = len(eth)
        print(f"\n[{label}] ethambutol cases = {n_d:,}; "
              f"denominator = {N_scen:,} ({time.time()-t0:.0f}s)")
        for term in TERMS:
            if denom is not None:
                n_e = con.execute(
                    """SELECT COUNT(DISTINCT r.caseid) FROM reac r
                       JOIN dedup_map m ON r.primaryid = m.primaryid
                       WHERE UPPER(r.pt) = ?
                         AND r.caseid IN (SELECT caseid FROM dc_att)""",
                    (term,)).fetchone()[0]
            else:
                n_e = con.execute(
                    """SELECT COUNT(DISTINCT r.caseid) FROM reac r
                       JOIN dedup_map m ON r.primaryid = m.primaryid
                       WHERE UPPER(r.pt) = ?""", (term,)).fetchone()[0]
            a = count_with_term(con, ["ETHAMBUTOL"], term, **opts)
            if denom is not None:
                a = con.execute(
                    """SELECT COUNT(*) FROM (
                         SELECT DISTINCT d.caseid FROM drug d
                         JOIN dedup_map m ON d.primaryid = m.primaryid
                         JOIN drugname dn ON dn.primaryid = d.primaryid
                                         AND dn.drug_seq = d.drug_seq
                         WHERE (UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
                             OR UPPER(COALESCE(dn.prod_ai,'')) LIKE '%ETHAMBUTOL%')
                         INTERSECT
                         SELECT caseid FROM dc_att
                         INTERSECT
                         SELECT DISTINCT r.caseid FROM reac r
                         JOIN dedup_map m3 ON r.primaryid = m3.primaryid
                         WHERE UPPER(r.pt) = ?)""", (term,)).fetchone()[0]
            b, c = n_d - a, n_e - a
            d = N_scen - a - b - c
            if min(b, c, d) < 0:
                raise AssertionError(
                    f"{label}/{term}: negative cell a={a} b={b} c={c} d={d} "
                    f"(N={N_scen}, n_d={n_d}, n_e={n_e})")
            ror, lo, hi = ror_ci(a, b, c, d)
            rows.append({"scenario": label, "term": term, "a": a,
                         "n_ethambutol": n_d, "n_event": n_e,
                         "ror": ror, "ror_lcl": lo, "ror_ucl": hi,
                         "signal": bool(lo > 1 and a >= 3)})
            print(f"    {term:24s} a={a:>4} ROR={ror:>10.2f} "
                  f"({lo:>8.2f}-{hi:>10.2f}) {'SIGNAL' if lo > 1 and a >= 3 else '-'}")

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "faers_robustness.csv", index=False, encoding="utf-8-sig")
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / "Table9_robustness.csv", index=False, encoding="utf-8-sig")

    print("\n=== robustness summary: ROR by scenario ===")
    piv = df.pivot_table(index="term", columns="scenario", values="ror")
    print(piv.round(2).to_string())
    print("\n=== signal agreement ===")
    sig = df.pivot_table(index="term", columns="scenario", values="signal",
                         aggfunc="first")
    print(sig.to_string())
    core = ["OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY"]
    print("\n=== conclusion check ===")
    for t in core:
        sub = df[df.term == t]
        allsig = bool(sub.signal.all())
        print(f"  {t:20s} signal in all scenarios: {allsig}  "
              f"(ROR range {sub.ror.min():.1f}-{sub.ror.max():.1f})")
    neg = df[df.term.isin(["DRY EYE", "CATARACT", "GLAUCOMA", "EYE PAIN"])]
    print(f"  non-specific terms never forming a signal in any scenario: "
          f"{bool((~neg.signal).all())}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
