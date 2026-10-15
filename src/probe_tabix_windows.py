# -*- coding: utf-8 -*-
"""
Confirm the project's own tabix reader works from Windows against the FinnGen bucket.

The pipeline already contains a minimal BGZF reader that fetches only the byte ranges a
query needs, and it is known to work under WSL.  If it also works here, the missing
outcome scans can be produced on this side and copied into the project, which avoids
WSL entirely - and WSL is where the Mendelian randomisation has failed twice, once on a
proxy that was not mirrored and once when the run was interrupted.

Testing before building matters here: this project has repeatedly lost time to code
written against an assumed interface, and the reader is the one component whose
behaviour under Windows is unknown.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

GB = "https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release"
PHENO = "H7_OPTNEURITIS"
DATA = f"{GB}/finngen_R12_{PHENO}.gz"
INDEX = f"{GB}/finngen_R12_{PHENO}.gz.tbi"

try:
    import bgzf_tabix as bt
except ImportError as exc:
    raise SystemExit(f"cannot import bgzf_tabix: {exc}")

print("=" * 90)
print("1. What the module exposes")
print("=" * 90)
names = [n for n in dir(bt) if not n.startswith("_")]
print(f"  {names}")
for n in ("Tabix", "HttpFile", "read_from_voffset", "read_bgzf_block"):
    print(f"    {n}: {hasattr(bt, n)}")

print()
print("=" * 90)
print("2. Open the tabix index over HTTP and query a small region")
print("=" * 90)
t0 = time.time()
try:
    tb = bt.Tabix(DATA, INDEX)
    print(f"  index opened in {time.time()-t0:.1f}s")
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED {type(exc).__name__}: {str(exc)[:200]}")
    raise SystemExit(1)

# a region on chromosome 1, wide enough to return rows but small enough to be quick
for chrom, start, end in (("1", 1_000_000, 1_200_000), ("6", 30_000_000, 30_200_000)):
    t0 = time.time()
    try:
        lines = tb.query(chrom, start, end)
        dt = time.time() - t0
        print(f"  chr{chrom}:{start:,}-{end:,}  ->  {len(lines):,} lines  "
              f"({dt:.1f}s)")
        if lines:
            print(f"      first: {lines[0][:150]}")
            print(f"      columns: {len(lines[0].split(chr(9)))}")
    except Exception as exc:  # noqa: BLE001
        print(f"  chr{chrom} query FAILED {type(exc).__name__}: {str(exc)[:160]}")

print()
print("=" * 90)
print("3. Reading a single variant by position")
print("=" * 90)
try:
    lines = tb.query("1", 1_000_000, 1_500_000)
    print(f"  returned {len(lines)} lines for a 500 kb window")
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED {type(exc).__name__}: {str(exc)[:160]}")

print()
print("=" * 90)
print("Reading")
print("=" * 90)
print("""  If the queries returned lines, the reader works from Windows and the missing scans
  can be generated here.  If they did not, the panel stays as it is and the manuscript's
  statement of scope is unchanged.""")
