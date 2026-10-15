# -*- coding: utf-8 -*-
"""
Repair the eQTLGen download.

The molgenis file server truncates every stream at ~307.8 MB of the 322.8 MB
object (a repeatable server-side cap, reproducible with 1, 16 and 40 concurrent
ranged requests).  The missing tail is fetched in small tolerant ranges and
written into the pre-allocated file, then the whole gzip is verified by full
decompression.
"""
from __future__ import annotations

import ssl
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

TARGET = ROOT / "data" / "raw" / "eqtlgen" / "cis-eQTLsFDR0.05-ProbeLevel.txt.gz"
PART = TARGET.with_suffix(TARGET.suffix + ".part")
SIZE = 322_775_879


def fetch(start: int, end: int, tries: int = 6) -> bytes | None:
    for a in range(tries):
        try:
            req = urllib.request.Request(URL, headers={**UA, "Range": f"bytes={start}-{end}"})
            with urllib.request.urlopen(req, timeout=300, context=CTX) as r:
                blob = r.read()
            if blob:
                return blob
        except Exception as exc:  # noqa: BLE001
            print(f"    retry {a+1} {start}-{end}: {type(exc).__name__}")
            time.sleep(2 * (a + 1))
    return None


def main() -> int:
    src = PART if PART.exists() else TARGET
    if not src.exists():
        print("no local file to repair")
        return 1
    print(f"source: {src.name} size={src.stat().st_size:,} (target {SIZE:,})")

    # where does the real data end?
    with src.open("rb") as fh:
        fh.seek(0)
        first = fh.read(4)
    print(f"header: {first.hex(' ')} ({'gzip' if first[:2] == b'\\x1f\\x8b' else 'NOT gzip'})")

    # find the first fully-zero 4 KB block
    data_end = None
    step = 4096
    with src.open("rb") as fh:
        off = 0
        while off < SIZE:
            fh.seek(off)
            b = fh.read(min(step, SIZE - off))
            if not b:
                break
            if b.count(0) == len(b):
                data_end = off
                break
            off += len(b)
    print(f"real data ends at: {data_end:,}" if data_end else "no zero block found")

    start_repair = data_end if data_end is not None else max(0, SIZE - 20 << 20)
    print(f"\nfetching bytes {start_repair:,} .. {SIZE-1:,} "
          f"({(SIZE-start_repair)/1e6:.1f} MB) in 1 MB ranges ...")
    t0 = time.time()
    out = PART if PART.exists() else TARGET
    with out.open("r+b") as fh:
        fh.seek(start_repair)
        pos = start_repair
        while pos < SIZE:
            end = min(SIZE - 1, pos + (1 << 20) - 1)
            blob = fetch(pos, end)
            if blob is None:
                print(f"  FAILED at {pos:,}")
                return 1
            fh.write(blob)
            pos += len(blob)
            if (pos - start_repair) % (5 << 20) < (1 << 20):
                print(f"  {pos/1e6:8.1f} MB  ({time.time()-t0:.0f}s)")
    print(f"repair done in {time.time()-t0:.0f}s")

    # verify
    print("\nverifying full decompression ...")
    try:
        d = zlib.decompressobj(31)
        n_out = 0
        with out.open("rb") as fh:
            while True:
                b = fh.read(1 << 22)
                if not b:
                    break
                n_out += len(d.decompress(b))
        n_out += len(d.flush())
        print(f"  decompressed {n_out:,} bytes; eof={d.eof}; "
              f"size={out.stat().st_size:,}")
        if out.stat().st_size == SIZE and d.eof:
            if out != TARGET:
                out.replace(TARGET)
            print(f"  -> {TARGET.name} OK")
            return 0
    except Exception as exc:  # noqa: BLE001
        print(f"  decompress failed: {type(exc).__name__} {str(exc)[:140]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
