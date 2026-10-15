# -*- coding: utf-8 -*-
"""
Establish exactly what is missing before fetching anything.

Two things are needed for each exposure-outcome pair:
    * the instrument file, tophits_<gwas_id>_5e-08.tsv, which gives the variants and
      their effect sizes
    * the FinnGen outcome scan for each instrument window, which is what has to be
      downloaded

The earlier coverage audit found the instrument files cached for all ten exposures and
the outcome scans missing for seven of them, but that audit ran before serum creatinine
was recovered and before any new scans were produced, so it is re-checked here rather
than trusted.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

EXPOSURES = {
    "ebi-a-GCST90103634": "eGFR (creatinine)",
    "ebi-a-GCST90025945": "Cystatin C",
    "ebi-a-GCST90025946": "Serum creatinine",
    "ebi-a-GCST006867": "Type 2 diabetes",
    "ebi-a-GCST90014006": "HbA1c",
    "ieu-b-4877": "Smoking initiation",
    "ieu-b-25": "Cigarettes per day",
    "ieu-b-73": "Alcoholic drinks per week",
    "ukb-b-13891": "Zinc supplement use",
    "ieu-b-40": "Body mass index",
}
OUTCOMES = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
            "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]

print("=" * 96)
print("Instrument files")
print("=" * 96)
inst = {}
for gid, label in EXPOSURES.items():
    p = RAW / f"tophits_{gid}_5e-08.tsv"
    if p.exists() and p.stat().st_size > 1:
        try:
            n = len(pd.read_csv(p, sep="\t"))
        except Exception:  # noqa: BLE001
            n = -1
        inst[gid] = n
        print(f"  {label:26s} {n:>5} instruments   cached")
    else:
        print(f"  {label:26s} MISSING - has to come from the OpenGWAS API")

print()
print("=" * 96)
print("Cached outcome scans, by exposure and outcome")
print("=" * 96)
have = {}
for gid in EXPOSURES:
    row = []
    for ph in OUTCOMES:
        n = len(list(RAW.glob(f"mr_{gid}_{ph}_*.tsv")))
        row.append(n)
        have[(gid, ph)] = n
    label = EXPOSURES[gid]
    print(f"  {label:26s} " + " ".join(f"{v:>5}" for v in row)
          + f"   total {sum(row):>6}")

print()
print("  columns: " + " ".join(f"{o[3:9]:>5}" for o in OUTCOMES))

print()
print("=" * 96)
print("What still has to be fetched")
print("=" * 96)
todo = []
for gid, label in EXPOSURES.items():
    if gid not in inst:
        todo.append((label, "instruments", None))
        continue
    for ph in OUTCOMES:
        if have[(gid, ph)] == 0:
            todo.append((label, ph, inst[gid]))
if not todo:
    print("  nothing; the panel is complete")
else:
    by_exp = {}
    for label, what, n in todo:
        by_exp.setdefault(label, []).append((what, n))
    for label, items in by_exp.items():
        if items and items[0][0] == "instruments":
            print(f"  {label:26s} instruments missing entirely")
        else:
            print(f"  {label:26s} {len(items)} outcome(s) unscanned, "
                  f"{items[0][1]} instruments each")
    print()
    print(f"  total outstanding entries: {len(todo)}")
