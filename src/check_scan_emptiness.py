# -*- coding: utf-8 -*-
"""
Check whether the cached FinnGen scans actually contain variants, or are empty.

The puzzle
    Serum creatinine harmonised 0 of 370 instruments while eGFR harmonised 150 of 342,
    even though 56% of serum creatinine's rsIDs appear somewhere in the cached scans
    and only 53% of eGFR's do.  The exposure metadata is identical in form (both carry
    rsid, chr, pos, ea, nea, eaf, beta, sebeta), and mr_final.py renames rsid to rsids
    before calling harmonise, so the matching key is supplied for both.

    A zero that does not follow from the data has to come from the pipeline, and the
    most likely place is the scan itself: region_scan caches whatever the tabix query
    returns, and if a query returns nothing the empty result is cached and then reused
    forever.  This counts rows per scan file to see whether that happened.

Usage
    python src/check_scan_emptiness.py
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"
PAT = re.compile(r"^mr_(?P<gid>.+)_(?P<ph>H7_[A-Z]+)_(?P<chrom>[0-9XYM]+)_(?P<wi>\d+)\.tsv$")

EXPOSURES = {
    "ebi-a-GCST90103634": "eGFR (creatinine)   OK",
    "ebi-a-GCST90025945": "Cystatin C          OK",
    "ebi-a-GCST90025946": "Serum creatinine    FAILED",
    "ebi-a-GCST90014006": "HbA1c               FAILED",
    "ukb-b-13891": "Zinc supplement use FAILED",
}

print("=" * 84)
print("1. Rows per scan file, by exposure")
print("=" * 84)
stats: dict[str, list[int]] = collections.defaultdict(list)
empty: dict[str, int] = collections.Counter()
for p in RAW.glob("mr_*.tsv"):
    m = PAT.match(p.name)
    if not m:
        continue
    gid = m.group("gid")
    if gid not in EXPOSURES:
        continue
    try:
        n = max(sum(1 for _ in p.open(encoding="utf-8", errors="replace")) - 1, 0)
    except Exception:  # noqa: BLE001
        n = -1
    stats[gid].append(n)
    if n <= 0:
        empty[gid] += 1

for gid, label in EXPOSURES.items():
    v = stats.get(gid, [])
    if not v:
        print(f"  {label:26s} no scan files")
        continue
    v_sorted = sorted(v)
    med = v_sorted[len(v_sorted) // 2]
    print(f"  {label:26s} {len(v):>5} files   rows min={min(v):>6} "
          f"median={med:>6} max={max(v):>6}   empty files={empty[gid]}")

print()
print("=" * 84)
print("2. Is the emptiness structural?")
print("=" * 84)
print("""  A tabix query over a 500 kb window in a 20-million-variant release should return
  thousands of rows.  A file holding zero rows means the query returned nothing, and
  because region_scan caches whatever it gets, that empty frame is then served from
  cache on every later run.  If serum creatinine's scans are empty while eGFR's are
  not, the zero harmonisation is explained and it is an artefact of a failed retrieval
  that has been frozen into the cache.""")

print()
print("=" * 84)
print("3. Direct check: do the failing exposures' scans contain the instruments?")
print("=" * 84)
for gid, label in [("ebi-a-GCST90103634", "eGFR (creatinine)"),
                   ("ebi-a-GCST90025946", "Serum creatinine")]:
    ip = RAW / f"tophits_{gid}_5e-08.tsv"
    if not ip.exists():
        print(f"  {label}: no instrument file")
        continue
    ins = pd.read_csv(ip, sep="\t")
    want = set(ins["rsid"].dropna().astype(str))
    found_rs, scanned_rows = set(), 0
    # the scans this exposure's own run produced
    for p in RAW.glob(f"mr_{gid}_*.tsv"):
        try:
            d = pd.read_csv(p, sep="\t")
        except Exception:  # noqa: BLE001
            continue
        scanned_rows += len(d)
        if "rsids" in d.columns:
            for v in d["rsids"].dropna().astype(str):
                for piece in v.split(";"):
                    found_rs.add(piece.strip())
    inter = want & found_rs
    print(f"  {label:22s} scans hold {scanned_rows:>9,} variant rows; "
          f"{len(inter)}/{len(want)} instruments matched "
          f"({len(inter)/max(len(want),1)*100:.1f}%)")
