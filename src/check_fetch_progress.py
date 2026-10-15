# -*- coding: utf-8 -*-
"""Report progress of the FinnGen scan fetch, by counting files per exposure."""
from __future__ import annotations

import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

#: exposure -> (label, number of windows the instruments require)
TARGETS = {
    "ukb-b-13891": ("Zinc supplement use", 3),
    "ieu-b-25": ("Cigarettes per day", 21),
    "ieu-b-73": ("Alcoholic drinks per week", 30),
    "ieu-b-4877": ("Smoking initiation", 87),
    "ebi-a-GCST006867": ("Type 2 diabetes", 109),
    "ebi-a-GCST90014006": ("HbA1c", 260),
    "ieu-b-40": ("Body mass index", 331),
}
PHENOS = 6

counts = collections.Counter()
for p in RAW.glob("mr_*.tsv"):
    for gid in TARGETS:
        if f"mr_{gid}_" in p.name:
            counts[gid] += 1
            break

print("=" * 74)
print("FinnGen scan fetch progress")
print("=" * 74)
print(f"  {'exposure':26s} {'windows':>9s} {'target':>8s}")
total_done = total_goal = 0
for gid, (label, goal) in TARGETS.items():
    done = counts.get(gid, 0) // PHENOS      # six phenotype files per window
    total_done += min(done, goal)
    total_goal += goal
    mark = "   complete" if done >= goal else ""
    print(f"  {label:26s} {done:>9d} {goal:>8d}{mark}")
pct = 100 * total_done / max(total_goal, 1)
print(f"  {'TOTAL':26s} {total_done:>9d} {total_goal:>8d}   {pct:.0f}%")

raw_files = sum(counts.values())
print()
print(f"  raw scan files written for these exposures: {raw_files:,}")
print(f"  each window produces {PHENOS} files, one per phenotype")
