# -*- coding: utf-8 -*-
"""
Report progress of the corrected refetch.

The corrected fetch queries each phenotype separately, so each window produces six files
and the number of completed windows is the file count divided by six.  A useful extra
check is whether the phenotypes are genuinely different: if any window's six files share
a hash, the fault has recurred and the run should be stopped rather than left to
complete.
"""
from __future__ import annotations

import collections
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

TARGETS = {
    "ukb-b-13891": ("Zinc supplement use", 3),
    "ieu-b-25": ("Cigarettes per day", 21),
    "ieu-b-73": ("Alcoholic drinks per week", 30),
    "ieu-b-4877": ("Smoking initiation", 87),
    "ebi-a-GCST006867": ("Type 2 diabetes", 109),
    "ebi-a-GCST90014006": ("HbA1c", 260),
    "ieu-b-40": ("Body mass index", 331),
}
PHENOS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
          "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]
N_PHENO = len(PHENOS)

counts = collections.Counter()
for p in RAW.glob("mr_*.tsv"):
    for gid in TARGETS:
        if f"mr_{gid}_" in p.name:
            counts[gid] += 1
            break

print("=" * 78)
print("Corrected refetch progress")
print("=" * 78)
print(f"  {'exposure':26s} {'windows':>9s} {'target':>8s}")
done = goal = 0
for gid, (label, tgt) in TARGETS.items():
    d = counts.get(gid, 0) // N_PHENO
    done += min(d, tgt)
    goal += tgt
    mark = "   complete" if d >= tgt else ""
    print(f"  {label:26s} {d:>9d} {tgt:>8d}{mark}")
print(f"  {'TOTAL':26s} {done:>9d} {goal:>8d}   "
      f"{100*done/max(goal,1):.0f}%")
print()
total_files = sum(counts.values())
print(f"  scan files written for these exposures : {total_files:,}")
print(f"  expected when complete                 : {goal*N_PHENO:,}")

print()
print("=" * 78)
print("Integrity spot-check: are the phenotypes different?")
print("=" * 78)
bad = []
checked = 0
for gid, (label, tgt) in TARGETS.items():
    # find any window that has all six phenotypes written
    by_window: dict[str, list[Path]] = collections.defaultdict(list)
    for p in RAW.glob(f"mr_{gid}_*.tsv"):
        m = re.match(rf"mr_{re.escape(gid)}_(H7_[A-Z]+)_(.+)\.tsv$", p.name)
        if m:
            by_window[m.group(2)].append(p)
    full = {w: ps for w, ps in by_window.items() if len(ps) == N_PHENO}
    if not full:
        print(f"  {label:26s} no complete window yet")
        continue
    w, ps = sorted(full.items())[0]
    hashes = {hashlib.md5(p.read_bytes()).hexdigest()[:8] for p in ps}
    ok = len(hashes) == N_PHENO
    checked += 1
    if not ok:
        bad.append(label)
    print(f"  {label:26s} window {w:>8s}: {len(hashes)}/{N_PHENO} distinct "
          f"hash(es)   {'OK' if ok else '*** IDENTICAL ***'}")

print()
if bad:
    print(f"  {len(bad)} exposure(s) show copied data: {bad}")
    print("  stop the fetch and investigate before continuing")
else:
    print(f"  {checked} exposure(s) checked; all hold phenotype-specific data")
