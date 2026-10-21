# -*- coding: utf-8 -*-
"""Merge the corrected period estimates into main_results.json.

The period block written by src/build_main_results.py used the whole-database N in the d cell,
which inflates a period-specific odds ratio by roughly the ratio of the database to the period.
src/audit_period_and_strict.py recomputed each period with that period's own de-duplicated case
count; this script replaces the block with those values and records where they came from, so
that the tables and figures, which read main_results.json, all move together.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
main = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
extra = json.loads((RES / "audit_period_strict.json").read_text(encoding="utf-8"))

for label, p in extra["periods"].items():
    old = main["temporal"][label]
    print(f"{label}: {old['ror']:.2f} -> {p['ror']:.2f}  "
          f"(N_period {p['N_period']:,}, d {p['d']:,})")
    main["temporal"][label] = {
        "n_drug": p["n_drug"], "n_event": p["n_event"], "a": p["a"],
        "N_period": p["N_period"], "b": p["b"], "c": p["c"], "d": p["d"],
        "ror": p["ror"], "ror_lcl": p["ror_lcl"], "ror_ucl": p["ror_ucl"],
        "pct_eth": p["pct_eth"], "pct_other": p["pct_other"],
    }
main["temporal"]["note"] = ("recomputed with the period's own de-duplicated case count as d; "
                            "the first version used the whole-database N and overstated both "
                            "periods")
main["strict_token"] = {
    "status": "not a separate analysis",
    "why": ("the cohort is identified by a case-insensitive substring match on the drug-name "
            "fields with the single name token ETHAMBUTOL, so a 'whole-token' variant does not "
            "define a different cohort; the earlier Methods text described the exposure "
            "incorrectly and the sensitivity has been withdrawn rather than reported"),
}
(RES / "main_results.json").write_text(json.dumps(main, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
print("\nmain_results.json updated")
