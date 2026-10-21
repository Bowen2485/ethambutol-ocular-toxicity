# -*- coding: utf-8 -*-
"""Recompute every p value and q value with a test that is valid for sparse 2x2 tables.

The previous values came from Pearson's chi-square, whose asymptotic approximation is unreliable
when the expected count in a cell is small; this cohort is a small fraction of a 20-million-case
database, so several preferred terms have expected counts below one.  The rule now applied, and
stated in the Methods, is:

    two-sided Fisher exact test when the smallest expected cell count is below 5
    Pearson chi-square (no continuity correction) otherwise
    Benjamini-Hochberg within each of the two declared families (11 queries, 15 terms)

Both tests are two-sided.  The script also records which test produced each p, so the supplement
can show the raw p next to the q.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import chi2_contingency, fisher_exact

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
main = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
N = main["N"]


def cells(a: int, n_event: int, n_drug: int) -> list[list[int]]:
    b = n_drug - a
    c = n_event - a
    d = N - n_drug - n_event + a
    return [[a, b], [c, d]]


def p_value(table: list[list[int]]) -> tuple[float, str]:
    arr = np.asarray(table, float)
    expected = chi2_contingency(arr, correction=False)[3]
    if float(expected.min()) < 5:
        t0 = time.time()
        p = float(fisher_exact(table, alternative="two-sided")[1])
        return p, f"Fisher exact (min expected {expected.min():.3g}, {time.time()-t0:.2f}s)"
    p = float(chi2_contingency(arr, correction=False)[1])
    return p, f"Pearson chi-square (min expected {expected.min():.1f})"


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


def disp(v: float) -> str:
    if v == 0:
        return "<1e-300"
    return f"{v:.1e}" if v < 1e-4 else f"{v:.4g}"


for block in ("smq", "pt"):
    rows = main[block]
    ps, tests = [], []
    for r in rows:
        n_drug = int(r.get("n_drug", main["n_ethambutol"]))
        p, how = p_value(cells(int(r["a"]), int(r["n_event"]), n_drug))
        ps.append(p)
        tests.append(how)
    qs = bh(ps)
    for r, p, q, how in zip(rows, ps, qs, tests):
        r["p_pearson_old"] = r["p"]
        r["p"] = p
        r["q_bh_old"] = r["q_bh"]
        r["q_bh"] = q
        r["p_test"] = how
        r["p_display"] = disp(p)
        r["q_bh_display"] = disp(q)
    print(f"\n{block}: {len(rows)} tests")
    for r in sorted(rows, key=lambda x: x["q_bh"]):
        flag = "" if abs(r["q_bh"] - r["q_bh_old"]) < 1e-6 else \
               f"  (was {r['q_bh_old']:.2g})"
        print(f"  {str(r.get('smq') or r.get('term'))[:34]:34s} a={r['a']:>4} "
              f"p={r['p_display']:>9s} q={r['q_bh_display']:>9s}{flag}")

main["statistics"] = {
    "test_rule": ("two-sided Fisher exact when the smallest expected cell count < 5, "
                  "Pearson chi-square without continuity correction otherwise"),
    "multiplicity": "Benjamini-Hochberg within the 11 ocular queries and within the 15 preferred terms",
}
(RES / "main_results.json").write_text(json.dumps(main, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
print("\nmain_results.json updated with exact p values")
