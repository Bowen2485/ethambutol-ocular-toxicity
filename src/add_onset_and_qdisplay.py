# -*- coding: utf-8 -*-
"""Add the onset block and a display form for underflowed q values to main_results.json.

The review asked that a q of 0.0 not be left to stand as a literal zero.  The value is a
floating-point underflow; the file keeps the number but adds a display string, which the
supplementary workbook now uses.  The onset block records the group sizes the Results section
quotes, so those numbers are traceable to the same file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
main = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))

tto = pd.read_csv(RES / "faers_tto.csv", encoding="utf-8-sig")
prof = pd.read_csv(RES / "faers_cases_profile.csv", encoding="utf-8-sig", low_memory=False)


def q_display(q: float) -> str:
    if q == 0:
        return "<1e-300"
    return f"{q:.1e}" if q < 1e-4 else f"{q:.4g}"


for block in ("smq", "pt"):
    for r in main[block]:
        r["q_bh_display"] = q_display(r["q_bh"])

main["onset"] = {
    "n_cases": len(prof),
    "n_with_interval": int(tto.iloc[0].n),
    "n_missing_or_unusable": len(prof) - int(tto.iloc[0].n),
    "n_optic_nerve": int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0]),
    "median_optic_nerve_days": float(tto[tto.group.str.startswith("Optic-nerve")].median_days.iloc[0]),
    "n_ocular": int(tto[tto.group.str.startswith("Ocular event")].n.iloc[0]),
    "n_non_ocular": int(tto[tto.group.str.startswith("No ocular")].n.iloc[0]),
    "median_non_ocular_days": float(tto[tto.group.str.startswith("No ocular")].median_days.iloc[0]),
    "n_cases_with_any_of_17_terms": int(prof.any_optic.sum()),
    "term_set": "17 preferred terms in src/faers_case_deep.py OPTIC_TERMS; wider than the 45-term query",
}
(RES / "main_results.json").write_text(json.dumps(main, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
print("main_results.json: onset block added, q_display added")
print(main["onset"])
