# -*- coding: utf-8 -*-
"""
Test whether the six FinnGen optic phenotypes share their variant set.

This decides the size of the job.  Producing the missing scans means querying one region
per (exposure, phenotype, window).  With seven exposures, six phenotypes and hundreds of
windows that is thousands of queries at 8 to 20 seconds each - many hours.

But FinnGen releases its endpoints as a common set of variants with different effect
estimates, so if the six optic phenotypes carry identical positions in a region, one
query can serve all six, cutting the work sixfold.  The two earlier cached runs are also
worth examining for the same reason: the earlier coverage file recorded identical
harmonised counts for every phenotype of a given exposure, which would be expected if
the phenotypes share variants and would be a coincidence otherwise.

The test is direct: query the same region in two phenotypes and compare the positions.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import bgzf_tabix as bt  # noqa: E402

GB = "https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release"
PHENOS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_NEUROPATHY",
          "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]

REGIONS = [("1", 1_000_000, 1_100_000), ("19", 45_000_000, 45_100_000)]

# the two phenotypes used in the existing cache, to check the inference from them
print("=" * 94)
print("1. Does a region return the same positions in different phenotypes?")
print("=" * 94)

for chrom, start, end in REGIONS:
    print(f"\n  region chr{chrom}:{start:,}-{end:,}")
    pos_by_pheno = {}
    for ph in PHENOS:
        data = f"{GB}/finngen_R12_{ph}.gz"
        index = data + ".tbi"
        t0 = time.time()
        try:
            tb = bt.Tabix(data, index)
            lines = tb.query(chrom, start, end)
        except Exception as exc:  # noqa: BLE001
            print(f"    {ph:28s} FAILED {type(exc).__name__}: {str(exc)[:70]}")
            continue
        pos = [ln.split("\t")[1] for ln in lines if ln.count("\t") >= 12]
        pos_by_pheno[ph] = set(pos)
        print(f"    {ph:28s} {len(lines):>6,} lines  {len(pos):>6,} positions  "
              f"({time.time()-t0:.1f}s)")

    if len(pos_by_pheno) > 1:
        keys = list(pos_by_pheno)
        base = pos_by_pheno[keys[0]]
        print(f"    overlap with {keys[0]}:")
        for k in keys[1:]:
            inter = len(base & pos_by_pheno[k])
            union = len(base | pos_by_pheno[k])
            jac = inter / union if union else 0
            print(f"      {k:28s} {inter:>6,}/{len(base):<6,} shared   "
                  f"Jaccard {jac:.3f}")

print()
print("=" * 94)
print("2. Are the phenotype names all present in the release?")
print("=" * 94)
import urllib.error  # noqa: E402
import urllib.request  # noqa: E402
for ph in PHENOS:
    url = f"{GB}/finngen_R12_{ph}.gz"
    try:
        req = urllib.request.Request(url, headers=bt.UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=45, context=bt.CTX) as r:
            size = r.headers.get("Content-Length")
            print(f"  {ph:28s} {r.status}  {int(size)/1e6 if size else 0:>7.1f} MB")
    except urllib.error.HTTPError as exc:
        print(f"  {ph:28s} HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {ph:28s} {type(exc).__name__}")

print()
print("=" * 94)
print("3. What the existing cache implies")
print("=" * 94)
RAW = ROOT / "data" / "raw" / "opengwas"
import pandas as pd  # noqa: E402
for gid, label in (("ebi-a-GCST90103634", "eGFR"), ("ebi-a-GCST90025945", "Cystatin C")):
    rows = []
    for ph in PHENOS[:4]:
        files = sorted(RAW.glob(f"mr_{gid}_{ph}_*.tsv"))
        if files:
            d = pd.read_csv(files[0], sep="\t")
            rows.append((ph, len(d), sorted(d["pos"])[:3] if "pos" in d else None))
    print(f"  {label}: first cached scan per phenotype")
    for ph, n, first in rows:
        print(f"      {ph:28s} {n:>6,} rows  first positions {first}")
