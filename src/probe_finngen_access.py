# -*- coding: utf-8 -*-
"""
Test whether the FinnGen outcome data can be reached from this machine.

The Mendelian randomisation panel is missing seven exposures because their FinnGen
outcome scans were never cached.  Those scans read the R12 summary statistics through
HTTP range requests against a Google Cloud Storage bucket, and earlier attempts to
finish the panel failed on network access.  The WSL side reported that a Windows
localhost proxy was not mirrored into it, so before planning any work the question is
whether this side can reach the bucket at all.

Three things are tested separately, because they fail for different reasons:
    1. the bucket host resolves and answers
    2. a real tabix index can be fetched, which is a few MB from the same bucket
    3. a small range request against the data file returns bytes

If range requests work, the remaining scans can be produced here in Python and copied
into the project, without involving WSL at all.
"""
from __future__ import annotations

import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}

GB = "https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release"
PHENO = "H7_OPTNEURITIS"
DATA = f"{GB}/finngen_R12_{PHENO}.gz"
INDEX = f"{GB}/finngen_R12_{PHENO}.gz.tbi"

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "finngen"
RAW.mkdir(parents=True, exist_ok=True)


def head(url: str, timeout: int = 60):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return (time.time() - t0, r.status,
                    r.headers.get("Content-Length"), r.headers.get("Accept-Ranges"))
    except urllib.error.HTTPError as exc:
        return (time.time() - t0, f"HTTP {exc.code}", None, None)
    except Exception as exc:  # noqa: BLE001
        return (time.time() - t0, type(exc).__name__, None, None)


print("=" * 92)
print("1. Does the bucket answer?")
print("=" * 92)
for url in (DATA, INDEX):
    dt, status, size, accept = head(url)
    name = url.rsplit("/", 1)[-1]
    print(f"  {name:46s} {dt:6.2f}s  {str(status):>12s}  "
          f"size={size}  ranges={accept}")

print()
print("=" * 92)
print("2. Fetch the tabix index and keep it")
print("=" * 92)
idx_out = RAW / f"{PHENO}.gz.tbi"
try:
    t0 = time.time()
    req = urllib.request.Request(INDEX, headers=UA)
    with urllib.request.urlopen(req, timeout=300, context=CTX) as r:
        blob = r.read()
    idx_out.write_bytes(blob)
    print(f"  downloaded {len(blob):,} bytes in {time.time()-t0:.1f}s -> {idx_out.name}")
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED {type(exc).__name__}: {str(exc)[:120]}")

print()
print("=" * 92)
print("3. A small range request against the data file")
print("=" * 92)
try:
    t0 = time.time()
    req = urllib.request.Request(DATA, headers={**UA, "Range": "bytes=0-65535"})
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        block = r.read()
    print(f"  {len(block):,} bytes in {time.time()-t0:.1f}s, HTTP {r.status}")
    # a BGZF file starts with the gzip magic and carries an FEXTRA block
    print(f"  first bytes: {block[:18]!r}")
    ok = block[:2] == b"\x1f\x8b"
    print(f"  gzip magic present: {ok}")
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED {type(exc).__name__}: {str(exc)[:120]}")

print()
print("=" * 92)
print("Reading")
print("=" * 92)
print("""  If the range request returned gzip bytes, the bucket is reachable from here and the
  missing scans can be produced on this side, bypassing WSL entirely.  If it did not,
  the panel cannot be completed by this route and the manuscript's current statement of
  scope stands.""")
