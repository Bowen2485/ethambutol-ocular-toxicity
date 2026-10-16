# -*- coding: utf-8 -*-
"""
Check the DisGeNET result for false positives before it is reported.

The counts are 20 of 33 hub genes with an eye association against 4 of 33 control genes, and
the Fisher test prints as 0.0000 because the format rounds it.  Both need attention before
the number goes anywhere near the manuscript.

First, the exact p value, computed rather than displayed.

Second, the keyword match.  Scanning disease names for "kerat", "cataract" and the like will
catch conditions that are not eye diseases: keratosis is a skin condition whose name contains
"kerat", and "cataract and cardiomyopathy" is a syndrome named after its eye feature but
classified under its cardiac one.  A match that is an artefact of the string inflates the hub
side and would be a real weakness if a reviewer noticed it.  So every match is listed and the
questionable ones are separated out, and the test is recomputed without them.

This is a check on my own method, and the expected outcome is that the result gets weaker,
not that it survives untouched.
"""
from __future__ import annotations

import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "results" / "disgenet_hub_annotation.json"
d = json.loads(P.read_text(encoding="utf-8"))

hub, ctrl = d["hubs"], d["controls"]

print("=" * 100)
print("1. The exact p value, not the rounded display")
print("=" * 100)


def fisher_all(a: int, b: int, c: int, d_: int) -> float:
    """Two-sided Fisher exact, summing every table at least as extreme."""
    from fractions import Fraction
    n = a + b + c + d_
    r1, r2, c1, c2 = a + b, c + d_, a + c, b + d_

    def prob(x):
        # x = top-left cell
        if x < max(0, r1 - c2) or x > min(r1, c1):
            return Fraction(0)
        return (Fraction(comb(c1, x) * comb(c2, r1 - x), comb(n, r1)))

    p_obs = prob(a)
    total = Fraction(1)
    p = sum(prob(x) for x in range(max(0, r1 - c2), min(r1, c1) + 1)
            if prob(x) <= p_obs * (1 + 1e-12) * total / total)
    return float(p)


a, b = d["n_hub_eye"], 33 - d["n_hub_eye"]
c, dd = d["n_ctrl_eye"], 33 - d["n_ctrl_eye"]
p_one = sum(comb(a + c, k) * comb((33 - a) + (33 - c), (a + b) - k)
            / comb(66, a + b) for k in range(a, min(a + b, a + c) + 1))
print(f"  table: hubs {a}/{a+b}   controls {c}/{c+dd}")
print(f"  one-sided hypergeometric p = {p_one:.3e}")
print(f"  odds ratio                 = "
      f"{((a+0.5)*(dd+0.5))/((b+0.5)*(c+0.5)):.2f}  (Haldane-Anscombe)")
print()
print(f"  for comparison, the earlier narrow-source result: 10/33 vs 8/33, p = 0.39")

print()
print("=" * 100)
print("2. Every match, so the questionable ones can be judged")
print("=" * 100)
SUSPECT = ("keratosis", "cataract and cardiomyopathy", "cardiomyopathy")
print(f"  {'gene':10s} {'disease':74s} verdict")
flagged_hub: set[str] = set()
for g, v in hub.items():
    for name in v.get("eye_diseases", []):
        low = name.lower()
        susp = any(s in low for s in SUSPECT)
        if susp:
            flagged_hub.add(g)
        print(f"  {g:10s} {name[:74]:74s} "
              f"{'QUESTIONABLE' if susp else 'eye disease'}")

print()
if flagged_hub:
    print(f"  genes whose only eye matches are questionable: {sorted(flagged_hub)}")
else:
    print("  no questionable match was the only one for a gene")

print()
print("=" * 100)
print("3. The test recomputed with the questionable matches removed")
print("=" * 100)
#: a match counts as an eye association only if at least one of its names is not suspect
hub_strict = {}
for g, v in hub.items():
    good = [n for n in v.get("eye_diseases", [])
            if not any(s in n.lower() for s in SUSPECT)]
    hub_strict[g] = good
ctrl_strict = {}
for g, v in ctrl.items():
    good = [n for n in v.get("eye_diseases", [])
            if not any(s in n.lower() for s in SUSPECT)]
    ctrl_strict[g] = good

a2 = sum(1 for v in hub_strict.values() if v)
c2 = sum(1 for v in ctrl_strict.values() if v)
b2, d2 = 33 - a2, 33 - c2
p2 = sum(comb(a2 + c2, k) * comb(b2 + d2, (a2 + b2) - k) / comb(66, a2 + b2)
         for k in range(a2, min(a2 + b2, a2 + c2) + 1))
print(f"  hubs with a non-questionable eye association     : {a2}/33")
print(f"  controls with a non-questionable eye association : {c2}/33")
print(f"  one-sided p = {p2:.3e}")
print(f"  odds ratio  = {((a2+0.5)*(d2+0.5))/((b2+0.5)*(c2+0.5)):.2f}")

print()
print("=" * 100)
print("4. The specific genes that matter for this manuscript")
print("=" * 100)
FOCUS = ["OPA1", "DNM1L", "MFN2", "HMOX1", "SDHB", "NFE2L2", "GPX4", "SLC7A11",
         "ACSL4", "TNF", "TP53", "SLC25A4"]
print("  OPA1, DNM1L and SLC25A4 are mitochondrial and are annotated for optic atrophy or")
print("  cataract and cardiomyopathy, so their appearance is the expected positive control")
print("  for this method: a genuine optic-nerve gene must be detected.")
print()
for g in FOCUS:
    v = hub.get(g)
    if not v:
        continue
    eyes = v.get("eye_diseases", [])
    print(f"  {g:10s} {v['n_diseases']:>4d} diseases, {v['n_eye']:>2d} eye   "
          f"max score {v['max_score']}")
    for n in eyes[:3]:
        print(f"      - {n}")

out = {
    "hub_with_eye": a, "control_with_eye": c,
    "p_one_sided": p_one, "p_one_sided_strict": p2,
    "hub_with_eye_strict": a2, "control_with_eye_strict": c2,
    "questionable_terms": list(SUSPECT),
    "genes_only_questionable": sorted(flagged_hub),
    "odds_ratio_strict": round(((a2 + 0.5) * (d2 + 0.5)) / ((b2 + 0.5) * (c2 + 0.5)), 2),
}
(ROOT / "results" / "disgenet_false_positive_check.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  -> results/disgenet_false_positive_check.json")
