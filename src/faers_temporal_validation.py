# -*- coding: utf-8 -*-
"""
Temporal validation of the optic-nerve signal inside FAERS.

The weakness this addresses
    Every finding in the paper comes from one database.  FAERS is subject to stimulated
    reporting, duplicate submissions and drifting reporting habits, so a pooled analysis
    cannot separate a property of the drug from a property of the era in which it was
    reported.  Splitting the de-duplicated database by receipt date and testing the same
    hypothesis independently in each period is the strongest validation available
    without a second data source, and needs no new data.

Exposure and event definitions
    These are copied from faers_robustness.py rather than written afresh, because a
    different definition would not be comparable with the published numbers.  The first
    attempt of this script matched drug names with a plain LIKE on drugname alone and
    found 18,690 ethambutol cases against the paper's 13,804 - a 35% overcount.  The
    difference is real: the pipeline joins drug to drugname on drug_seq so that a name
    is attributed to the correct drug record, and requires the three-table join
    drug -> dedup_map -> drugname.  That chain is reproduced here exactly.

    The paper's optic-neuropathy analysis uses the single preferred term
    OPTIC NEUROPATHY (a = 153 in the pooled database), so the same single term is used
    here.  A composite of several optic terms would give a much larger a and would not
    be comparable with the reported estimate.

Usage
    python src/faers_temporal_validation.py
"""
from __future__ import annotations

import csv
import math
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
RESULTS = ROOT / "results"

# exactly as in faers_robustness.py
TOKENS = ["ETHAMBUTOL", "MYAMBUTOL"]
TERMS = ["OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
         "TOXIC OPTIC NEUROPATHY"]
# negative controls, expected null in both periods
CONTROLS = ["CATARACT", "DRY EYE", "EYE PAIN", "GLAUCOMA"]


def match_sql(alias: str, tokens: list[str]) -> tuple[str, list]:
    """Whole-substance match, identical to faers_robustness.strict_match_sql."""
    conds, params = [], []
    for t in tokens:
        conds.append(f"(UPPER(COALESCE({alias}.drugname,'')) LIKE ? "
                     f"OR UPPER(COALESCE({alias}.prod_ai,'')) LIKE ?)")
        params += [f"%{t}%", f"%{t}%"]
    return "(" + " OR ".join(conds) + ")", params


def year_filter(where_period: str) -> str:
    return f" AND d.fda_dt IS NOT NULL AND length(d.fda_dt) >= 4 {where_period}"


def ethambutol_cases(con, period: str | None) -> set[str]:
    """
    Case IDs exposed to ethambutol, optionally restricted to a receipt period.

    The receipt year is taken from demo, not from drug.  drug.fda_dt exists as a column
    but is empty in every one of its 98,884,686 rows, so filtering on it removed all
    cases and the first run reported zero ethambutol exposure against the paper's
    13,804.  demo.fda_dt is populated, and joining it on primaryid through dedup_map
    keeps the de-duplicated case set intact.
    """
    cond, params = match_sql("dn", TOKENS)
    date = ""
    if period:
        date = f" AND substr(dm.fda_dt,1,4) {period}"
    q = f"""SELECT DISTINCT d.caseid FROM drug d
            JOIN dedup_map m  ON d.primaryid = m.primaryid
            JOIN drugname dn  ON dn.primaryid = d.primaryid
                             AND dn.drug_seq = d.drug_seq
            JOIN demo dm      ON dm.primaryid = m.primaryid
            WHERE {cond}
              AND dm.fda_dt IS NOT NULL AND length(dm.fda_dt) >= 4{date}"""
    return {r[0] for r in con.execute(q, params)}


def cases_with_term(con, term: str, period: str | None) -> set[str]:
    """Case IDs reporting the preferred term, in the same periods.

    reac.fda_dt is used only as a non-empty check; the period comes from demo, for the
    same reason as above.
    """
    date = ""
    if period:
        date = f" AND substr(dm.fda_dt,1,4) {period}"
    q = f"""SELECT DISTINCT r.caseid FROM reac r
            JOIN dedup_map m ON r.primaryid = m.primaryid
            JOIN demo dm     ON dm.primaryid = m.primaryid
            WHERE UPPER(r.pt) = '{term}'
              AND dm.fda_dt IS NOT NULL AND length(dm.fda_dt) >= 4{date}"""
    return {r[0] for r in con.execute(q)}


def total_cases(con, period: str | None) -> int:
    date = ""
    if period:
        date = f" AND substr(d.fda_dt,1,4) {period}"
    q = f"""SELECT COUNT(DISTINCT d.caseid) FROM demo d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            WHERE d.fda_dt IS NOT NULL AND length(d.fda_dt) >= 4{date}"""
    return con.execute(q).fetchone()[0]


def ror_ci(a, b, c, d, z=1.959964):
    if a == 0 or b == 0 or c == 0 or d == 0:
        return float("nan"), float("nan"), float("nan")
    ror = (a * d) / (b * c)
    se = math.sqrt(1/a + 1/b + 1/c + 1/d)
    return ror, ror * math.exp(-z * se), ror * math.exp(z * se)


def main() -> int:
    if not DB.exists():
        raise SystemExit(f"{DB} not found")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.execute("PRAGMA cache_size=-2000000")

    print("[1] the exposure definition, checked against the published figure")
    eth_all = ethambutol_cases(con, None)
    N_all = total_cases(con, None)
    print(f"    total de-duplicated cases : {N_all:,}")
    print(f"    ethambutol cases          : {len(eth_all):,}   "
          f"(the paper reports 13,804 strict-match cases; 15,573 with name variants)")
    if not (12_000 <= len(eth_all) <= 17_000):
        print("    WARNING the count is outside the expected range; the definition "
              "may not match the pipeline's")

    print()
    print("[2] receipt-year distribution of the ethambutol cases")
    # the year comes from demo: drug.fda_dt is empty in all 98,884,686 of its rows
    q = f"""SELECT substr(dm.fda_dt,1,4) AS y, COUNT(DISTINCT d.caseid)
            FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            JOIN demo dm ON dm.primaryid = m.primaryid
            WHERE {match_sql('dn', TOKENS)[0]}
              AND dm.fda_dt IS NOT NULL AND length(dm.fda_dt) >= 4
            GROUP BY y ORDER BY y"""
    yearly = con.execute(q, match_sql("dn", TOKENS)[1]).fetchall()
    for y, n in yearly:
        if y and y.isdigit() and int(y) >= 2000:
            print(f"    {y}  {n:>7,}")

    print()
    print("[3] choosing the split so both periods carry enough events")
    opt_all = cases_with_term(con, "OPTIC NEUROPATHY", None)
    solved = False
    for cut in range(2012, 2026):
        e1 = ethambutol_cases(con, f"<= '{cut}'")
        e2 = ethambutol_cases(con, f"> '{cut}'")
        o1 = opt_all & e1
        o2 = opt_all & e2
        if len(o1) >= 40 and len(o2) >= 40:
            print(f"    split at {cut}: early {len(e1):,} ethambutol cases with "
                  f"{len(o1)} optic-neuropathy events; late {len(e2):,} with {len(o2)}")
            split = cut
            solved = True
            break
    if not solved:
        split = 2018
        print(f"    no split gave 40 events in both periods; using {split}")

    periods = [("discovery", f"<= '{split}'"),
               ("validation", f"> '{split}'")]
    print(f"    discovery: 2004-{split}    validation: {split+1}-2026")

    print()
    print("[4] disproportionality in each period, by term")
    rows = []
    for term in TERMS:
        term_cases = cases_with_term(con, term, None)
        rec = {"term": term}
        for pname, pcond in periods:
            eth = ethambutol_cases(con, pcond)
            N = total_cases(con, pcond)
            a = len(eth & term_cases)
            b = len(eth) - a
            c = len(term_cases) - a
            d = N - a - b - c
            ror, lo, hi = ror_ci(a, b, c, d)
            rec.update({f"{pname}_a": a, f"{pname}_n_emb": len(eth),
                        f"{pname}_ror": ror, f"{pname}_lcl": lo,
                        f"{pname}_ucl": hi})
            print(f"    {term:22s} {pname:11s} n_emb={len(eth):>6,} a={a:>4} "
                  f"ROR={ror:>8.2f} ({lo:.2f}-{hi:.2f})")
        # is the signal present in both periods?
        r1, r2 = rec["discovery_ror"], rec["validation_ror"]
        rec["both_periods_signal"] = bool(
            r1 > 1 and r2 > 1
            and rec["discovery_lcl"] > 1 and rec["validation_lcl"] > 1)
        rows.append(rec)
        print(f"    {'':22s} -> replicated in both periods: "
              f"{rec['both_periods_signal']}")

    print()
    print("[5] negative controls, which should stay null in both periods")
    ctrl_rows = []
    for term in CONTROLS:
        term_cases = cases_with_term(con, term, None)
        rec = {"term": term}
        for pname, pcond in periods:
            eth = ethambutol_cases(con, pcond)
            N = total_cases(con, pcond)
            a = len(eth & term_cases)
            b = len(eth) - a
            c = len(term_cases) - a
            d = N - a - b - c
            ror, lo, hi = ror_ci(a, b, c, d)
            rec.update({f"{pname}_a": a, f"{pname}_ror": ror,
                        f"{pname}_lcl": lo, f"{pname}_ucl": hi})
        ctrl_rows.append(rec)
        print(f"    {term:14s} discovery ROR {rec['discovery_ror']:>6.2f} "
              f"({rec['discovery_lcl']:.2f}-{rec['discovery_ucl']:.2f})   "
              f"validation ROR {rec['validation_ror']:>6.2f} "
              f"({rec['validation_lcl']:.2f}-{rec['validation_ucl']:.2f})")

    con.close()

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "faers_temporal_validation.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v)
                        for k, v in r.items()})
    print(f"\n-> {out}")
    ctrl = RESULTS / "faers_temporal_controls.csv"
    with open(ctrl, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ctrl_rows[0].keys()))
        w.writeheader()
        for r in ctrl_rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v)
                        for k, v in r.items()})
    print(f"-> {ctrl}")

    print()
    print("=" * 84)
    print("How to read this")
    print("=" * 84)
    print("""  The optic-nerve signal should be present, and of similar magnitude, in both
  periods, with lower confidence limits above 1 in each.  Two independent reporting
  eras agreeing is evidence that the association belongs to the drug rather than to
  when it was reported.  The negative controls should stay null in both; a control
  that becomes a signal in one period only would point to a period effect.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
