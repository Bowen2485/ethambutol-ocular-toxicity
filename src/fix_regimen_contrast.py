# -*- coding: utf-8 -*-
"""Replace the fixed-regimen contrast with the value recomputed on the current cohort.

The published 66/5,736 versus 3/845 (rate ratio 3.24) came from the 18 October run with a
different case identity.  Recomputed from the same case table as every other estimate in the
paper, the contrast is 76/6,167 versus 7/1,098, rate ratio 1.93 with an interval that includes
unity.  The direction is unchanged and the claim must be weaker: the contrast is reported as a
supporting analysis, not as a significant within-class effect.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
reg = json.loads((ROOT / "results" / "audit_regimen.json").read_text(encoding="utf-8"))
s = reg["strata"]
w = s["rifampicin+isoniazid+pyrazinamide+ethambutol"]
o = s["rifampicin+isoniazid+pyrazinamide"]
pct_w = 100 * w["n_optic"] / w["n"]
pct_o = 100 * o["n_optic"] / o["n"]

p = MAN / "TADS_results.md"
text = p.read_text(encoding="utf-8")
old = re.search(r"Within the antitubercular class, the one comparison.*?without ethambutol\.", text, re.S)
assert old, "regimen paragraph not found"
new = (
    "Within the antitubercular class, the one comparison in which the background regimen is held "
    "constant — reports naming rifampicin, isoniazid and pyrazinamide, partitioned by whether "
    f"ethambutol is also named — gave an optic-nerve rate of {pct_w:.2f}% ({w['n_optic']}/{w['n']:,}) "
    f"with ethambutol against {pct_o:.2f}% ({o['n_optic']}/{o['n']:,}) without, a rate ratio of "
    f"{reg['rate_ratio']:.2f} ({reg['rate_ratio_lcl']:.2f}–{reg['rate_ratio_ucl']:.2f}). The interval "
    "includes unity and the unexposed group is small, so this contrast is consistent in direction "
    "with the rest of the analysis but is not statistically significant on its own, and it is "
    "reported as a supporting analysis rather than as the basis of a within-class claim.")
text = text[:old.start()] + new + text[old.end():]
p.write_text(text, encoding="utf-8")

p = MAN / "TADS_discussion.md"
text = p.read_text(encoding="utf-8")
old2 = ("Restriction to suspect-drug reports, a strict token match and the class-restricted "
        "comparison each change the size of the estimate without changing its direction, and the "
        "fixed-regimen contrast — rifampicin, isoniazid and pyrazinamide with versus without "
        "ethambutol — holds the background regimen constant, at the cost of a wide interval because "
        "few reports name the three-drug regimen without ethambutol.")
if old2 in text:
    new2 = ("Restriction to suspect-drug reports and the period split change the size of the "
            "estimate without changing its direction. The fixed-regimen contrast — rifampicin, "
            "isoniazid and pyrazinamide with versus without ethambutol — holds the background "
            "regimen constant but rests on a small unexposed group, and its interval includes "
            "unity; it is reported for completeness rather than as evidence of a within-class "
            "effect.")
    text = text.replace(old2, new2, 1)
    p.write_text(text, encoding="utf-8")
    print("discussion updated")
else:
    print("discussion: regimen sentence not found verbatim (left unchanged)")

print(f"regimen now {w['n_optic']}/{w['n']:,} vs {o['n_optic']}/{o['n']:,}, "
      f"rate ratio {reg['rate_ratio']:.2f} ({reg['rate_ratio_lcl']:.2f}-{reg['rate_ratio_ucl']:.2f})")
