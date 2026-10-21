# -*- coding: utf-8 -*-
"""Correct the exposure description recorded inside main_results.json.

The review caught that the Methods described the exposure as a substring match on `substance` or
`medicinalproduct`, while the cohort is actually built from the drug-name fields (`drugname`,
`prod_ai`) with the single name token ETHAMBUTOL.  The JSON carries the same sentence, and the
repository now publishes it, so it is corrected here and the file is re-synced.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "results" / "main_results.json"
d = json.loads(P.read_text(encoding="utf-8"))
d["main_specification"]["exposure"] = (
    "ethambutol in the drug-name fields (drugname, prod_ai) of the surviving case version, "
    "case-insensitive substring match on the single name token ETHAMBUTOL, any drug role "
    "unless stated otherwise")
d["main_specification"]["sensitivity"] = [
    "suspect drug only (primary or secondary)",
    "receipt year split at 2016, each period with its own denominator",
    "fixed regimen (rifampicin + isoniazid + pyrazinamide with vs without ethambutol)",
]
P.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print("main_results.json exposure description corrected")
