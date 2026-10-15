# -*- coding: utf-8 -*-
"""
Check whether the restarted refetch is actually writing files.

The counter the fetch script prints includes skipped files, so it cannot distinguish
progress from a resumed no-op.  The file count on disk is the reliable signal, and more
specifically the modification times: if nothing new has appeared in the last few minutes
the run is either still forming its first connection or has failed, and the two need to be
told apart before the job is left running for hours.
"""
from __future__ import annotations

import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"

files = list(RAW.glob("mr_*.tsv"))
now = time.time()
print(f"  cache directory      : {RAW}")
print(f"  mr_*.tsv files       : {len(files):,}")

if not files:
    raise SystemExit("  no cached scans yet")

ages = sorted(now - f.stat().st_mtime for f in files)
newest = min(files, key=lambda p: -p.stat().st_mtime)

print(f"  newest file          : {newest.name}")
print(f"  newest written at    : {time.strftime('%H:%M:%S', time.localtime(newest.stat().st_mtime))}")
print(f"  seconds since newest : {ages[0]:.0f}")
print(f"  newest size          : {newest.stat().st_size:,} bytes")
print()

for window, label in ((60, "1 minute"), (180, "3 minutes"), (600, "10 minutes"),
                      (3600, "1 hour")):
    n = sum(1 for a in ages if a < window)
    print(f"  written within {label:11s}: {n}")

print()
if ages[0] < 120:
    print("  RUNNING - files are appearing")
elif ages[0] < 900:
    print("  SLOW - nothing in the last few minutes; a single Tabix query can take a")
    print("  while, but if this persists the job may be stalled on the network")
else:
    print("  STALLED - no new file for over 15 minutes; check the job output")
