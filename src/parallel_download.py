# -*- coding: utf-8 -*-
"""
Utility - parallel ranged HTTP downloader.

Single-stream throughput to research file servers is often throttled to a few
tens of KB/s while concurrent ranged requests are served at full speed (measured
on fis.fda.gov: ~35 KB/s per stream, ~150 KB/s with 12 streams).  This module
downloads a URL as N byte ranges in parallel and scatter-writes them.

Usage
    python parallel_download.py <url> <destination> [--chunks 16]
"""
from __future__ import annotations

import argparse
import os
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}


def head_size(url: str, timeout: int = 120) -> int:
    req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        cr = r.headers.get("Content-Range", "")
        if "/" in cr:
            return int(cr.rsplit("/", 1)[1])
        return int(r.headers.get("Content-Length", 0))


def download(url: str, dest: Path, chunks: int = 16, timeout: int = 900,
             progress: bool = True) -> bool:
    size = head_size(url)
    if size <= 0:
        print(f"cannot determine size for {url}")
        return False
    part = dest.with_suffix(dest.suffix + ".part")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with part.open("wb") as fh:
        fh.truncate(size)

    step = max(1, -(-size // chunks))
    state = {"done": 0}
    lock = threading.Lock()
    errors: list[str] = []
    t0 = time.time()

    def grab(idx: int, start: int, end: int) -> None:
        rng = f"bytes={start}-{end}"
        for attempt in range(8):
            try:
                req = urllib.request.Request(url, headers={**UA, "Range": rng})
                with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                    blob = r.read()
                if len(blob) != end - start + 1:
                    raise IOError(f"short read {len(blob)} != {end - start + 1}")
                with part.open("r+b") as fh:
                    fh.seek(start)
                    fh.write(blob)
                with lock:
                    state["done"] += len(blob)
                    if progress and state["done"] % (32 << 20) < len(blob):
                        el = time.time() - t0
                        pct = 100 * state["done"] / size
                        print(f"    {state['done']/1e6:8.1f}/{size/1e6:.1f} MB "
                              f"({pct:5.1f}%)  {state['done']/1e6/max(el,1e-9):6.1f} MB/s")
                return
            except Exception as exc:  # noqa: BLE001
                if attempt == 7:
                    with lock:
                        errors.append(f"chunk {idx} ({rng}): {exc}")
                time.sleep(2 + attempt * 3)

    threads = []
    for i in range(chunks):
        s = i * step
        e = min(size - 1, s + step - 1)
        if s > e:
            break
        t = threading.Thread(target=grab, args=(i, s, e), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    if errors:
        print(f"[fail] {len(errors)} chunks failed: {errors[:2]}")
        return False
    # integrity: the server must serve the expected total
    if part.stat().st_size != size:
        print(f"[fail] size mismatch {part.stat().st_size} != {size}")
        return False
    part.replace(dest)
    el = time.time() - t0
    print(f"[ok] {dest.name}: {size/1e6:.1f} MB in {el:.0f}s "
          f"({size/1e6/max(el,1e-9):.1f} MB/s)")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("dest")
    ap.add_argument("--chunks", type=int, default=16)
    args = ap.parse_args()
    ok = download(args.url, Path(args.dest), chunks=args.chunks)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
