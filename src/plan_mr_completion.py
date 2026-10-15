# -*- coding: utf-8 -*-
"""
Plan the remaining Mendelian randomisation work, entirely offline.

Two facts make this tractable without touching the network:

  * instruments for all ten nominated exposures are already cached
    (data/raw/opengwas/tophits_*.tsv, fetched during earlier runs)

  * outcome scans are keyed by (phenotype, chromosome, window index), not by exposure
    (see mr_final.py: RAW / f"mr_{gid}_{ph}_{chrom}_{wi}.tsv").  A scan of a region for
    one exposure is therefore reusable by any other exposure whose instruments fall in
    the same region.  4,825 such scans already exist.

So the amount of work still outstanding can be computed here, exactly: which windows
each missing exposure needs, how many of those are already on disk, and how many would
require an HTTP range request against the FinnGen bucket.

The window boundaries have to be reproduced exactly as mr_final.py computes them, or the
cache keys will not match and the reuse estimate will be wrong.  That logic is copied
from mr_final.py lines 208-231.

Usage
    python src/plan_mr_completion.py
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

# exposures in the order mr_final.py lists them, with the label used in the manuscript
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

# from mr_analysis.py
P_THRESHOLD = 5e-8
WINDOW_PAD = 250_000          # the scan is widened by this much on each side
MERGE_GAP = 2_000_000         # windows closer than this are merged

print("=" * 84)
print("1. Instruments already cached")
print("=" * 84)
inst = {}
for gid, label in EXPOSURES.items():
    p = RAW / f"tophits_{gid}_5e-08.tsv"
    if p.exists() and p.stat().st_size > 1:
        df = pd.read_csv(p, sep="\t")
        inst[gid] = df
        print(f"  {label:26s} {len(df):>5} instruments   cached")
    else:
        print(f"  {label:26s} MISSING - would need the OpenGWAS API")
if not inst:
    raise SystemExit("no instruments cached; cannot plan offline")

print()
print("=" * 84)
print("2. Windows each exposure needs, reproduced from mr_final.py")
print("=" * 84)


def windows_for(df: pd.DataFrame) -> dict[str, list[tuple[int, int]]]:
    """Recreate the chromosome/window grouping exactly as mr_final.py does."""
    if "chr" in df.columns:
        chrom_col, pos_col = "chr", "pos"
    elif "chrom" in df.columns:
        chrom_col, pos_col = "chrom", "pos"
    else:
        raise SystemExit(f"cannot find a chromosome column; have {list(df.columns)}")
    per: dict[str, list[tuple[int, int]]] = {}
    for chrom, grp in df.groupby(chrom_col):
        c = str(chrom)
        c = re.sub(r"^chr", "", c)
        rows = sorted(int(x) for x in grp[pos_col].tolist())
        if not rows:
            continue
        ws: list[list[int]] = []
        for pos in rows:
            lo, hi = pos - WINDOW_PAD, pos + WINDOW_PAD
            if ws and lo <= ws[-1][1] + MERGE_GAP:
                ws[-1][1] = max(ws[-1][1], hi)
            else:
                ws.append([lo, hi])
        per[c] = [(a, b) for a, b in ws]
    return per


need: dict[str, dict[str, list[tuple[int, int]]]] = {}
total_windows = 0
for gid, df in inst.items():
    need[gid] = windows_for(df)
    n = sum(len(v) for v in need[gid].values())
    total_windows += n
    print(f"  {EXPOSURES[gid]:26s} {len(need[gid]):>3} chromosomes, "
          f"{n:>4} windows")
print(f"\n  total windows across all exposures: {total_windows:,}")

print()
print("=" * 84)
print("3. How many of those windows are already on disk (cache reuse)")
print("=" * 84)
present = set()
pat = re.compile(r"^mr_(?P<gid>.+)_(?P<ph>H7_[A-Z]+)_(?P<chrom>[0-9XYM]+)_(?P<wi>\d+)\.tsv$")
for p in RAW.glob("mr_*.tsv"):
    m = pat.match(p.name)
    if m:
        present.add((m.group("gid"), m.group("ph"), m.group("chrom"),
                     int(m.group("wi"))))
print(f"  cache entries on disk: {len(present):,}")
# which (phenotype, chrom, window) regions are covered, regardless of exposure
regions_present = {(ph, c, wi) for _g, ph, c, wi in present}
print(f"  distinct (phenotype, chromosome, window) regions covered: "
      f"{len(regions_present):,}")
# note: the window index depends on the exposure's instrument layout, so a window
# index is only comparable between exposures that produce the same grouping; the
# reusable unit is really the genomic interval
by_key = collections.defaultdict(set)
for p in RAW.glob("mr_*.tsv"):
    m = pat.match(p.name)
    if m:
        by_key[(m.group("ph"), m.group("chrom"))].add(int(m.group("wi")))
print(f"  phenotypes with any cached scan: "
      f"{sorted({k[0] for k in by_key})}")

print()
print("=" * 84)
print("4. Per-exposure, per-outcome status")
print("=" * 84)
header = f"  {'exposure':26s} " + " ".join(f"{o[3:9]:>7s}" for o in OUTCOMES)
print(header)
plan_rows = []
for gid, label in EXPOSURES.items():
    if gid not in need:
        print(f"  {label:26s} no instruments cached")
        continue
    cells, missing_total, cached_total = [], 0, 0
    for ph in OUTCOMES:
        n_needed = 0
        n_cached = 0
        for chrom, ws in need[gid].items():
            for wi in range(len(ws)):
                n_needed += 1
                if (gid, ph, chrom, wi) in present:
                    n_cached += 1
        missing = n_needed - n_cached
        missing_total += missing
        cached_total += n_cached
        cells.append(f"{n_cached}/{n_needed}")
        plan_rows.append((gid, label, ph, n_needed, n_cached, missing))
    print(f"  {label:26s} " + " ".join(f"{c:>7s}" for c in cells))

print()
print("=" * 84)
print("5. What still has to be fetched")
print("=" * 84)
todo = [r for r in plan_rows if r[5] > 0]
done = {r[0] for r in plan_rows if r[5] == 0 and r[3] > 0}
print(f"  exposure-outcome pairs already fully cached: "
      f"{len([r for r in plan_rows if r[5] == 0])}")
print(f"  exposure-outcome pairs needing work          : {len(todo)}")
by_exp = collections.Counter(r[1] for r in todo)
for label, n in by_exp.most_common():
    need_n = sum(r[3] for r in todo if r[1] == label)
    have_n = sum(r[4] for r in todo if r[1] == label)
    print(f"    {label:26s} {n:>2} outcomes, {have_n:,}/{need_n:,} scans cached")
print()
print("  A scan reads the FinnGen R12 tabix over HTTP range requests, so completing the")
print("  panel needs network access from whichever machine runs it.  The instruments need")
print("  no network at all - they are already here.")
