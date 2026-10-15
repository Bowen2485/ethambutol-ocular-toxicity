# -*- coding: utf-8 -*-
"""Verify that the comparator correction landed in both assembled manuscripts."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
en = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
cn = (ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")

checks = [
    ("EN dropped 'order of magnitude above the next antitubercular'",
     "order of magnitude above the next antitubercular" not in en),
    ("EN states the within-class rank",
     bool(re.search(r"(6th of 18|sixth of eighteen|6 of 18)", en))),
    ("EN quotes the within-class optic-neuropathy ROR 6.47", "6.47" in en),
    ("EN names the first-line comparators' ratios",
     all(x in en for x in ["1.47", "2.20", "2.87"])),
    ("EN makes dyschromatopsia the distinguishing feature",
     "dyschromatopsia" in en.lower() and "hallmark" in en.lower()),
    ("EN explains what the whole-database ratio means", "159.21" in en),
    ("EN has a results subsection on the comparison",
     "Within the antitubercular class" in en or "3.2b" in en),
    ("EN limitation covers indication-severity confounding",
     "indication" in en.lower() and "second-line" in en.lower()),
    ("EN limitation says the claim is limited to same-regimen drugs",
     "same regimen" in en.lower() or "co-administered" in en.lower()),
    ("EN negative controls still reported as null",
     all(x in en for x in ["0.35", "0.32", "0.18"])),
    ("CN states the within-class comparison", "同类内部" in cn),
    ("CN reports the rank", bool(re.search(r"第\s*6\s*位", cn))),
    ("CN reports the within-class ROR", "6.47" in cn),
    ("CN highlights dyschromatopsia", "色觉障碍" in cn),
    ("CN dropped the TCM framing", not re.search(r"清阳|浊阴|中医", cn)),
    ("CN conclusion matches the corrected claim", "同类" in cn),
]
bad = 0
for name, ok in checks:
    print(f"  {'OK  ' if ok else 'FAIL'} {name}")
    bad += 0 if ok else 1
print(f"\n{len(checks)-bad}/{len(checks)} checks passed")
raise SystemExit(1 if bad else 0)
