# -*- coding: utf-8 -*-
"""
Diagnose the molgenis download: is the tail zero-padding (server behaviour) and
does the real payload decompress cleanly?
"""
from __future__ import annotations

import ssl
import sys
import time
import urllib.request
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}
URL = ("https://molgenis26.gcc.rug.nl/downloads/eqtlgen/cis-eqtl/"
       "2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz")
PART = ROOT / "data" / "raw" / "eqtlgen" / "cis-eQTLsFDR0.05-ProbeLevel.txt.gz.part"

print("### server behaviour on several ranges")
for s, e in [(0, 31), (322_775_879 - 64, 322_775_879 - 1), (307_000_000, 307_000_063),
             (320_000_000, 320_000_063), (322_700_000, 322_700_063)]:
    try:
        req = urllib.request.Request(URL, headers={**UA, "Range": f"bytes={s}-{e}"})
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            blob = r.read()
        print(f"  {s:>12}-{e:<12} status={r.status} len={len(blob)} "
              f"head={blob[:16].hex(' ')} zeros={blob.count(0)}/{len(blob)}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {s:>12}-{e:<12} FAIL {type(exc).__name__} {str(exc)[:70]}")
    time.sleep(0.4)

print(f"\n### current .part file: exists={PART.exists()}")
if PART.exists():
    size = PART.stat().st_size
    print(f"  size = {size:,}")
    # find the last non-zero byte
    last_nz = -1
    with PART.open("rb") as fh:
        off = size
        step = 1 << 20
        while off > 0:
            off = max(0, off - step)
            fh.seek(off)
            b = fh.read(min(step, size - off))
            idx = len(b) - len(b.rstrip(b"\x00"))
            if idx != len(b):
                last_nz = off + len(b.rstrip(b"\x00")) - 1
                break
    print(f"  last non-zero byte = {last_nz:,} (tail zeros = {size - 1 - last_nz:,})")

    print("\n  attempt to decompress the non-zero prefix ...")
    try:
        d = zlib.decompressobj(31)
        n_out = 0
        consumed = 0
        with PART.open("rb") as fh:
            while True:
                b = fh.read(1 << 22)
                if not b:
                    break
                consumed += len(b)
                n_out += len(d.decompress(b))
        n_out += len(d.flush())
        print(f"  decompressed {n_out:,} bytes from {consumed:,}; eof={d.eof}")
    except Exception as exc:  # noqa: BLE001
        print(f"  decompress failed after {n_out:,} bytes: "
              f"{type(exc).__name__} {str(exc)[:120]}")
    # first bytes
    with PART.open("rb") as fh:
        head = fh.read(32)
    print(f"  first 32 bytes: {head.hex(' ')}")
