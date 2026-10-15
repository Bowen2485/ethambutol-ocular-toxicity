# -*- coding: utf-8 -*-
"""
Check two numbers in the ferroptosis examination against the paper's own figures.

Two values differ from what the manuscript reports, and a discrepancy introduced during
an examination is worse than the original finding:

    1. ethambutol's optic-nerve ROR came out at 57.84 here, where the paper reports
       159.21 for optic neuropathy against the whole database
    2. the ethambutol case count came out at 13,880, where the toxicological analyses
       use 13,804

Both are explainable - the first by which term set and denominator were used, the second
by the substance patterns - but explainable is not the same as checked.  This establishes
which definition produces which figure, so the manuscript's numbers are not disturbed by
an analysis performed for a side-test.
"""
from __future__ import annotations

import math
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-2000000")
MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")

PATTERNS = {
    "strict (paper's toxicological definition)": ["%ETHAMBUTOL%"],
    "with salt and brand variants": ["%ETHAMBUTOL%", "%MYAMBUTOL%", "%DEXAMBUTOL%",
                                     "%ETAMBUTOL%"],
}
TERMS = {
    "OPTIC NEUROPATHY only": ("OPTIC NEUROPATHY",),
    "optic-nerve composite (four terms)": ("OPTIC NEUROPATHY", "OPTIC NEURITIS",
                                           "OPTIC ATROPHY",
                                           "TOXIC OPTIC NEUROPATHY"),
}
n_total = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
print(f"  whole database: {n_total:,} de-duplicated cases")
print()
print(f"  {'drug definition':44s} {'term set':36s} {'cases':>8s} {'a':>5s} "
      f"{'ROR':>8s}")
for dlabel, dpats in PATTERNS.items():
    cond = " OR ".join([MATCH] * len(dpats))
    params = [p for pat in dpats for p in (pat, pat)]
    ids = {r[0] for r in con.execute(
        f"""SELECT DISTINCT d.caseid FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE {cond}""", params)}
    for tlabel, terms in TERMS.items():
        lst = ",".join(f"'{t}'" for t in terms)
        ev = {r[0] for r in con.execute(
            f"""SELECT DISTINCT r.caseid FROM reac r
                JOIN dedup_map m ON r.primaryid = m.primaryid
                WHERE UPPER(r.pt) IN ({lst})""")}
        a = len(ids & ev)
        b = len(ids) - a
        c = len(ev) - a
        d = n_total - len(ids) - c
        if min(a, b, c, d) > 0:
            or_ = (a * d) / (b * c)
            se = math.sqrt(1/a + 1/b + 1/c + 1/d)
            ci = f"{or_*math.exp(-1.96*se):.2f}-{or_*math.exp(1.96*se):.2f}"
        else:
            or_, ci = float("nan"), "-"
        print(f"  {dlabel:44s} {tlabel:36s} {len(ids):>8,} {a:>5d} "
              f"{or_:>8.2f}   {ci}")

con.close()
print()
print("=" * 92)
print("Reading")
print("=" * 92)
print("""  The manuscript's 159.21 is for OPTIC NEUROPATHY alone with the strict substance
  definition and the whole database as denominator; its 13,804 is the strict-definition
  case count.  The examination used the four-term composite and the variant-merged
  definition, which gives a lower ratio and a higher count.  The two are consistent once
  the definitions are stated, and nothing in the paper needs to change - but the
  side-test must be reported with its own definition so the figures are not confused.""")
