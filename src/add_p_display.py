# -*- coding: utf-8 -*-
"""Add p_display to the results file and the other-ocular row to the onset sheet.

A p or q of 0.0 is a floating-point underflow; the file keeps the number and carries a display
string so that no table prints a literal zero probability.  The onset sheet gains the 74
other-ocular events so that the three groups described in the Methods all appear.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
main = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))


def disp(v: float) -> str:
    if v == 0:
        return "<1e-300"
    return f"{v:.1e}" if v < 1e-4 else f"{v:.4g}"


for block in ("smq", "pt"):
    for r in main[block]:
        r["p_display"] = disp(r["p"])
        r["q_bh_display"] = disp(r["q_bh"])

main["onset"]["n_other_ocular"] = main["onset"]["n_ocular"] - main["onset"]["n_optic_nerve"]
main["onset"]["note_groups"] = ("the Methods describe three groups; the primary comparison is "
                                "optic-nerve versus non-ocular, and the other-ocular group is "
                                "reported with the ocular totals")
(RES / "main_results.json").write_text(json.dumps(main, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
print("p_display added; onset groups:", main["onset"]["n_optic_nerve"],
      main["onset"]["n_other_ocular"], main["onset"]["n_non_ocular"])
