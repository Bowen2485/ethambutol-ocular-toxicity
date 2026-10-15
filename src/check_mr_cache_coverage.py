# -*- coding: utf-8 -*-
"""
Work out whether the MR panel can finish from the cache alone, with no network access.

The WSL side reports that a Windows localhost proxy is not mirrored into WSL, so any
HTTP call from inside WSL will fail.  mr_final.py talks to api.opengwas.io for
instruments and reads FinnGen over HTTP range requests for outcomes.  If the cache
already holds everything the remaining exposures need, the run is fully offline and
the proxy question is irrelevant.

This counts the cached files per exposure and outcome and reports the gap.
"""
from __future__ import annotations

import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

# exposure and outcome identifiers, in the order mr_final.py uses them
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

print("=" * 84)
print("1. Instruments (tophits) - needed once per exposure")
print("=" * 84)
have_inst, missing_inst = [], []
for gid, label in EXPOSURES.items():
    p = RAW / f"tophits_{gid}_5e-08.tsv"
    if p.exists() and p.stat().st_size > 1:
        try:
            n = max(p.read_text(encoding="utf-8", errors="replace").count("\n") - 1, 0)
        except Exception:  # noqa: BLE001
            n = -1
        have_inst.append(label)
        print(f"  cached   {label:26s} {n:>5} instruments")
    else:
        missing_inst.append(label)
        print(f"  MISSING  {label:26s} would need a network call")
print(f"\n  cached: {len(have_inst)}/{len(EXPOSURES)}")

print()
print("=" * 84)
print("2. Outcome scans - the (exposure, outcome, chromosome, window) cache")
print("=" * 84)
scans = list(RAW.glob("mr_*.tsv"))
by_exp = collections.Counter()
for p in scans:
    # filename is mr_<gwasid>_<phenotype>_<chrom>_<window>.tsv, and the phenotype
    # itself contains underscores, so match against the known identifiers
    stem = p.stem
    for gid in EXPOSURES:
        if stem.startswith(f"mr_{gid}_"):
            by_exp[gid] += 1
            break
print(f"  total scan files: {len(scans):,}")
for gid, label in EXPOSURES.items():
    n = by_exp.get(gid, 0)
    state = "cached" if n else "NOT SCANNED"
    print(f"  {label:26s} {n:>6,} scans   {state}")

print()
print("=" * 84)
print("3. Verdict")
print("=" * 84)
no_scans = [EXPOSURES[g] for g in EXPOSURES if by_exp.get(g, 0) == 0]
print(f"  exposures with instruments cached : {len(have_inst)}")
print(f"  exposures with no outcome scans   : {len(no_scans)}")
if no_scans:
    print(f"    {no_scans}")
print()
if not missing_inst and not no_scans:
    print("  The whole panel is satisfiable from the cache: the MR run needs no network.")
elif missing_inst:
    print("  Some instruments are not cached, so those exposures would need a network")
    print("  call.  Either fix the proxy, or run the MR on the Windows side where the")
    print("  cache and network both already work.")
else:
    print("  Instruments are cached but outcome scans are missing for some exposures.")
    print("  Those scans require HTTP range requests against the FinnGen bucket.")
    print("  Fix the proxy, or run the MR on the Windows side.")
print()
print("  Note: the manuscript does not depend on completing the panel.  Three renal")
print("  exposures are already finished and the null result is unchanged; if the panel")
print("  cannot be completed, the Methods section should simply describe those three.")
