# -*- coding: utf-8 -*-
"""Repair a FAERS quarterly archive that was downloaded truncated, then ingest it.

Why this exists
    faers_ascii_ingest.py re-downloads an archive only when it is *missing* or
    *zero bytes*:

        if not zip_path.exists() or zip_path.stat().st_size == 0:

    A download that stopped part-way leaves a plausible-looking file, so the
    condition is never met, the truncated zip is opened, zipfile raises, and the
    quarter is dropped - with no retry and no message saying the file itself is
    the problem.  2026Q2 sat in exactly that state: 37,748,736 bytes locally
    against 63,223,614 bytes at the source (exactly 36 MiB, the tell-tale of an
    interrupted transfer), which is why the analysis interval had been stuck at
    89 of 90 quarters.

    This script makes the retry possible: it compares the cached archive against
    the source, deletes it when they disagree, clears any partial rows for that
    quarter, and re-ingests.  Deleting first is the whole point - the ingest
    function cannot repair a file it considers present.

Usage
    python src/repair_truncated_faers_archive.py --check                 # report only
    python src/repair_truncated_faers_archive.py --quarter 2026q2        # repair + ingest
    python src/repair_truncated_faers_archive.py --quarter 2026q2 --force-ingest

--check touches nothing and is safe to run at any time.
"""
from __future__ import annotations

import argparse
import sqlite3
import ssl
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import faers_ascii_ingest as ing  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def source_size(quarter: str) -> int | None:
    """Total byte length of the quarter's archive at the source, or None."""
    for name in (f"faers_ascii_{quarter}.zip", f"aers_ascii_{quarter}.zip"):
        try:
            req = urllib.request.Request(ing.BASE + name,
                                         headers={**UA, "Range": "bytes=0-0"})
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                cr = r.headers.get("Content-Range", "")
                if "/" in cr:
                    return int(cr.split("/")[-1])
                return int(r.headers.get("Content-Length", 0)) or None
        except Exception:  # noqa: BLE001
            continue
    return None


def report() -> int:
    """Print the warehouse state and every cached archive that cannot be opened.

    Size is deliberately NOT used to guess: the earliest FAERS quarters are a
    few megabytes while recent ones are 60-77 MB, so any size threshold flags
    years of legitimate releases.  A truncated download has lost the central
    directory that lives at the end of the file, so asking zipfile to open it is
    both decisive and cheap - it reads only the tail.
    """
    con = sqlite3.connect(f"file:{ing.DB}?mode=ro", uri=True, timeout=120)
    done = [r[0] for r in con.execute("SELECT quarter FROM done ORDER BY quarter")]
    print(f"warehouse : {ing.DB}")
    print(f"  quarters ingested : {len(done)}  ({done[0]} .. {done[-1]})")
    for table in ("demo", "drug", "reac"):
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:5s} rows       : {n:,}")
    con.close()

    zips = sorted(ing.CACHE.glob("*.zip"))
    print(f"\ncached archives in {ing.CACHE}: {len(zips)}")
    if not zips:
        return 0

    bad: list[tuple[Path, str]] = []
    for p in zips:
        try:
            with zipfile.ZipFile(p) as zf:
                if not zf.namelist():
                    bad.append((p, "empty central directory"))
        except Exception as exc:  # noqa: BLE001
            bad.append((p, f"{type(exc).__name__}: {exc}"))

    if not bad:
        print("  every cached archive opens cleanly")
        return 0

    print(f"  UNREADABLE (truncated or otherwise corrupt): {len(bad)}")
    for p, why in bad:
        n = p.stat().st_size
        rr = source_size(p.stem)
        line = f"    {p.name:16s} {n:>13,} bytes  {why}"
        print(line)
        if rr:
            print(f"      source has {rr:,} bytes"
                  + (f"  -> short by {rr - n:,}; repair with --quarter {p.stem}"
                     if rr > n else "  (local is not smaller than source)"))
        else:
            print("      source size unavailable")
    return 0



def repair(quarter: str, force_ingest: bool, chunks: int) -> int:
    zip_path = ing.CACHE / f"{quarter}.zip"
    remote = source_size(quarter)
    local = zip_path.stat().st_size if zip_path.exists() else 0
    print(f"{quarter}: local {local:,} bytes, source "
          + (f"{remote:,} bytes" if remote else "unavailable"))

    if zip_path.exists() and (remote is None or local >= remote):
        print(f"  cached archive looks complete; ingesting as-is")
    elif zip_path.exists():
        print(f"  TRUNCATED by {remote - local:,} bytes - deleting so the ingest will re-fetch")
        zip_path.unlink()
    else:
        print("  no cached archive; the ingest will download it")

    part = zip_path.with_suffix(".zip.part")
    if part.exists():
        part.unlink()
        print("  removed a stale .part file")

    # Clear partial rows so a half-finished earlier attempt cannot double-count.
    con = sqlite3.connect(ing.DB, timeout=180, isolation_level=None)
    try:
        for table in ("demo", "drug", "reac"):
            n = con.execute(f"SELECT COUNT(*) FROM {table} WHERE quarter=?",
                            (quarter,)).fetchone()[0]
            if n:
                print(f"  clearing {n:,} partial {table} rows for {quarter}")
                con.execute(f"DELETE FROM {table} WHERE quarter=?", (quarter,))
        if con.execute("SELECT COUNT(*) FROM done WHERE quarter=?",
                       (quarter,)).fetchone()[0]:
            con.execute("DELETE FROM done WHERE quarter=?", (quarter,))
            print("  cleared a stale `done` row")
    finally:
        con.close()

    t0 = time.time()
    print(f"  downloading and ingesting {quarter} ...")
    res = ing.ingest_quarter(quarter, force=True, chunks=chunks)
    print(f"  result : {res}")
    print(f"  elapsed: {time.time() - t0:.0f} s")

    ing.finalize()

    con = sqlite3.connect(f"file:{ing.DB}?mode=ro", uri=True)
    done = [r[0] for r in con.execute("SELECT quarter FROM done ORDER BY quarter")]
    print(f"\nquarters ingested now: {len(done)}  ({done[0]} .. {done[-1]})")
    for table in ("demo", "drug", "reac"):
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:5s} rows: {n:,}")
    con.close()
    print(f"  archive now: {zip_path.stat().st_size:,} bytes")

    print("\nNOTE: the signal analysis is NOT rerun by this script.  The new quarter "
          "only enters\nthe results once faers_analysis.py is run, and it caches its "
          "de-duplication:\ndelete data/derived/dedup_map.flag first, or the new "
          "quarter is silently ignored.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quarter", help="e.g. 2026q2")
    ap.add_argument("--check", action="store_true", help="report only; changes nothing")
    ap.add_argument("--force-ingest", action="store_true",
                    help="ingest even when the cached archive looks complete")
    ap.add_argument("--chunks", type=int, default=12, help="parallel byte-range streams")
    args = ap.parse_args()

    if args.check or not args.quarter:
        return report()
    return repair(args.quarter, args.force_ingest, args.chunks)


if __name__ == "__main__":
    sys.exit(main())
