# -*- coding: utf-8 -*-
"""Cotherapy overlap among the ethambutol and comparator cohorts, from the warehouse.

Section 3.2b's argument depends on how often the first-line drugs appear in the same reports
(71.1% rifampicin, 54.9% isoniazid, 48.8% pyrazinamide, and the asymmetric 73.3% overlap of
pyrazinamide cases with ethambutol).  These are checked here so the text can cite the
90-quarter values rather than the ones typed from the earlier run.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect((ROOT / "data" / "derived" / "faers.sqlite").as_uri() + "?mode=ro",
                      uri=True)

drugs = ["ethambutol", "isoniazid", "rifampicin", "pyrazinamide"]
cases: dict[str, set[int]] = {}
for d in drugs:
    cases[d] = {r[0] for r in con.execute(
        "SELECT DISTINCT caseid FROM drug_case WHERE drug = ?", (d,))}

eth = cases["ethambutol"]
out: dict[str, float] = {}
print(f"ethambutol cases: {len(eth):,}")
for d in ("rifampicin", "isoniazid", "pyrazinamide"):
    n = len(eth & cases[d])
    out[f"eth_with_{d}"] = round(100 * n / len(eth), 1)
    print(f"  also naming {d:13s}: {n:>6,}  ({100*n/len(eth):.1f}%)")

pza = cases["pyrazinamide"]
n = len(pza & eth)
out["pza_with_eth"] = round(100 * n / len(pza), 1)
print(f"  pyrazinamide cases naming ethambutol: {n:,} of {len(pza):,} ({100*n/len(pza):.1f}%)")

(ROOT / "results" / "faers_cotherapy_overlap.json").write_text(
    json.dumps({"source": "data/derived/faers.sqlite: distinct caseid per drug",
                "percent": out}, indent=2), encoding="utf-8")
print("\nwritten results/faers_cotherapy_overlap.json")
