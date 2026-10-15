# -*- coding: utf-8 -*-
"""
Step 1 - Ingest the FAERS quarterly ASCII extracts into one SQLite warehouse.

Source   : FDA FAERS/AERS quarterly ASCII releases (fis.fda.gov), 2004Q1-2026Q2.
Why not openFDA: sustained bulk pagination on api.fda.gov is throttled (limit=100
requests hang after a few hundred calls), and the harmonised openFDA view drops
the raw CASEID / FDA_DT fields required for true case-version de-duplication.

De-duplication protocol (FDA's own recommendation)
    A case that is revised is re-submitted in a later quarter with the same
    CASEID and a newer FDA_DT.  For every CASEID keep the record with the
    highest FDA_DT, breaking ties on the highest PRIMARYID.

Tables
    demo   : case identity, dates, seriousness, demographics, reporter, country
    drug   : one row per drug line (name, role, dose, route, indication, dates)
    reac   : one row per reaction line (MedDRA PT + outcome)

Usage
    python faers_ascii_ingest.py --workers 4            # full ingest
    python faers_ascii_ingest.py --workers 4 --limit 3  # smoke test on 3 quarters
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sqlite3
import ssl
import sys
import threading
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
CACHE = RAW / "faers_ascii"
CACHE.mkdir(parents=True, exist_ok=True)
DERIVED.mkdir(parents=True, exist_ok=True)

DB = DERIVED / "faers.sqlite"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

PAGE = "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html"
BASE = "https://fis.fda.gov/content/Exports/"

# Field aliases: AERS-era and FAERS-era tables use different column names.
ALIAS = {
    "primaryid": ["primaryid", "isr"],
    "caseid": ["caseid", "case"],
    "fda_dt": ["fda_dt", "fda_dt"],
    "event_dt": ["event_dt", "event_dt"],
    "rept_cod": ["rept_cod", "rept_cod"],
    "mfr_dt": ["mfr_dt", "mfr_dt"],
    "init_fda_dt": ["init_fda_dt", "init_fda_dt"],
    "rept_dt": ["rept_dt", "rept_dt"],
    "auth_num": ["auth_num", "auth_num"],
    "mfr_num": ["mfr_num", "mfr_num"],
    "mfr_sndr": ["mfr_sndr", "mfr_sndr"],
    "lit_ref": ["lit_ref", "lit_ref"],
    "age": ["age", "age"],
    "age_cod": ["age_cod", "age_cod"],
    "age_grp": ["age_grp", "age_grp"],
    "sex": ["sex", "gndr_cod"],
    "wt": ["wt", "wt"],
    "wt_cod": ["wt_cod", "wt_cod"],
    "occp_cod": ["occp_cod", "occp_cod"],
    "reporter_country": ["reporter_country", "reporter_country"],
    "occr_country": ["occr_country", "occr_country"],
}

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=OFF;
CREATE TABLE IF NOT EXISTS demo (
    primaryid   TEXT, caseid TEXT, fda_dt TEXT, event_dt TEXT, rept_cod TEXT,
    age TEXT, age_cod TEXT, sex TEXT, wt TEXT,
    reporter_country TEXT, occr_country TEXT, quarter TEXT
);
CREATE TABLE IF NOT EXISTS drug (
    primaryid TEXT, caseid TEXT, fda_dt TEXT, drug_seq TEXT, role_cod TEXT,
    medicinalproduct TEXT, substance TEXT, indication TEXT,
    route TEXT, dose_vbm TEXT, dose_amt TEXT, dose_unit TEXT,
    start_dt TEXT, end_dt TEXT, dur TEXT, dur_cod TEXT, quarter TEXT
);
CREATE TABLE IF NOT EXISTS reac (
    primaryid TEXT, caseid TEXT, fda_dt TEXT, pt TEXT, outcome TEXT, quarter TEXT
);
CREATE TABLE IF NOT EXISTS done (
    quarter TEXT PRIMARY KEY, n_demo INTEGER, n_drug INTEGER, n_reac INTEGER,
    bytes INTEGER, finished TEXT
);
"""

INDEXES = """
CREATE INDEX IF NOT EXISTS ix_demo_case ON demo(caseid);
CREATE INDEX IF NOT EXISTS ix_demo_pid  ON demo(primaryid);
CREATE INDEX IF NOT EXISTS ix_drug_pid  ON drug(primaryid);
CREATE INDEX IF NOT EXISTS ix_drug_sub  ON drug(substance);
CREATE INDEX IF NOT EXISTS ix_reac_pid  ON reac(primaryid);
CREATE INDEX IF NOT EXISTS ix_reac_pt   ON reac(pt);
"""


# --------------------------------------------------------------------- helpers
def list_quarters() -> list[str]:
    req = urllib.request.Request(PAGE, headers=UA)
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        html = r.read().decode("utf-8", "replace")
    found = set()
    for m in re.finditer(r'href=["\']([^"\']*(?:faers|aers)_ascii_(\d{4})q(\d)\.zip)["\']',
                         html, flags=re.I):
        found.add(f"{m.group(2)}q{m.group(3)}")
    return sorted(found, key=lambda q: (int(q[:4]), int(q[-1])))


def schema_ok(header: list[str], table: str) -> bool:
    need = {"demo": ["primaryid", "caseid"], "drug": ["primaryid", "drug_seq"],
            "reac": ["primaryid", "pt"]}[table]
    hl = [h.lower() for h in header]
    if table == "demo":
        return any(x in hl for x in ("primaryid", "isr")) and \
               any(x in hl for x in ("caseid", "case"))
    return all(n in hl for n in need)


def read_table(zf: zipfile.ZipFile, target: str) -> tuple[list[str], list[list[str]]]:
    """Return (header, rows) for the requested table inside a quarterly archive."""
    wanted = {"demo": ("demo",), "drug": ("drug",), "reac": ("reac",)}
    for name in zf.namelist():
        low = name.lower()
        if not low.endswith(".txt"):
            continue
        base = Path(low).name
        if not any(base.startswith(w) for w in wanted[target]):
            continue
        if "sup" in base or "indi" in base or "ther" in base or "rpsr" in base:
            continue
        with zf.open(name) as fh:
            raw = fh.read()
        text = raw.decode("latin-1")
        lines = text.splitlines()
        if not lines:
            return [], []
        sep = "$"
        header = [h.strip().lower() for h in lines[0].split(sep)]
        if len(header) < 2:
            sep = ","
            header = [h.strip().strip('"').lower() for h in lines[0].split(sep)]
        out = []
        for line in lines[1:]:
            if not line.strip():
                continue
            out.append([c.strip().strip('"') for c in line.split(sep)])
        return header, out
    return [], []


def pick(header: list[str], key: str) -> int | None:
    for cand in ALIAS.get(key, [key]):
        if cand in header:
            return header.index(cand)
    return None


def cell(row: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    v = row[idx]
    return "" if v in ("", "NA", "N/A", "NULL", "None", ".") else v


def _head_size(url: str) -> int:
    req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        cr = r.headers.get("Content-Range", "")
        if "/" in cr:
            return int(cr.rsplit("/", 1)[1])
        return int(r.headers.get("Content-Length", 0))


def download_parallel(url: str, dest: Path, n_chunks: int = 12) -> int:
    """
    fda.gov throttles a single TCP stream to ~35 KB/s but allows concurrent
    ranged requests, so fetch the archive as N byte ranges in parallel and
    scatter-write them into the destination file.
    """
    size = _head_size(url)
    if size <= 0:
        raise RuntimeError(f"cannot determine size for {url}")
    tmp = dest.with_suffix(".zip.part")
    with tmp.open("wb") as fh:
        fh.truncate(size)

    step = max(1, -(-size // n_chunks))
    errors: list[str] = []
    lock = threading.Lock()

    def grab(idx: int, start: int, end: int) -> None:
        rng = f"bytes={start}-{end}"
        for attempt in range(6):
            try:
                req = urllib.request.Request(url, headers={**UA, "Range": rng})
                with urllib.request.urlopen(req, timeout=600, context=CTX) as r:
                    blob = r.read()
                if len(blob) != end - start + 1:
                    raise IOError(f"short read {len(blob)} != {end - start + 1}")
                with tmp.open("r+b") as fh:
                    fh.seek(start)
                    fh.write(blob)
                return
            except Exception as exc:  # noqa: BLE001
                if attempt == 5:
                    with lock:
                        errors.append(f"chunk {idx} ({rng}): {exc}")
                time.sleep(2 + attempt * 2)

    with ThreadPoolExecutor(max_workers=n_chunks) as pool:
        futs = []
        for i in range(n_chunks):
            s = i * step
            e = min(size - 1, s + step - 1)
            if s > e:
                break
            futs.append((i, s, e, pool.submit(grab, i, s, e)))
        for _, _, _, f in futs:
            f.result()
    if errors:
        raise RuntimeError("; ".join(errors[:3]))
    tmp.replace(dest)
    return size


def ingest_quarter(quarter: str, force: bool = False, chunks: int = 12) -> dict:
    con = sqlite3.connect(DB, timeout=180, isolation_level=None)
    try:
        row = con.execute("SELECT quarter FROM done WHERE quarter=?", (quarter,)).fetchone()
        if row and not force:
            return {"quarter": quarter, "skipped": True}
    finally:
        con.close()

    zip_path = CACHE / f"{quarter}.zip"
    if not zip_path.exists() or zip_path.stat().st_size == 0:
        names = [f"faers_ascii_{quarter}.zip", f"aers_ascii_{quarter}.zip"]
        last = None
        for n in names:
            try:
                download_parallel(BASE + n, zip_path, n_chunks=chunks)
                break
            except Exception as exc:  # noqa: BLE001
                last = exc
                if zip_path.with_suffix(".zip.part").exists():
                    try:
                        zip_path.with_suffix(".zip.part").unlink()
                    except Exception:  # noqa: BLE001
                        pass
        else:
            raise RuntimeError(f"{quarter}: download failed :: {last}")

    nbytes = zip_path.stat().st_size
    counts = {"demo": 0, "drug": 0, "reac": 0}
    payload: dict[str, tuple[list[str], list[list[str]]]] = {}
    with zipfile.ZipFile(zip_path) as zf:
        for table in ("demo", "drug", "reac"):
            header, rows = read_table(zf, table)
            if not header:
                raise RuntimeError(f"{quarter}: table '{table}' not found in archive "
                                   f"{zf.namelist()}")
            payload[table] = (header, rows)
            counts[table] = len(rows)

    con = sqlite3.connect(DB, timeout=180, isolation_level=None)
    try:
        # ---- demo
        header, rows = payload["demo"]
        i = {k: pick(header, k) for k in ALIAS}
        cols = ["primaryid", "caseid", "fda_dt", "event_dt", "rept_cod", "age",
                "age_cod", "sex", "wt", "reporter_country", "occr_country", "quarter"]
        data = [tuple(cell(r, i[k]) for k in
                      ("primaryid", "caseid", "fda_dt", "event_dt", "rept_cod", "age",
                       "age_cod", "sex", "wt", "reporter_country", "occr_country"))
                + (quarter,) for r in rows]
        for attempt in range(40):
            try:
                con.execute("BEGIN IMMEDIATE")
                con.executemany(
                    f"INSERT INTO demo({','.join(cols)}) VALUES({','.join('?' * len(cols))})",
                    data)
                con.execute("COMMIT")
                break
            except sqlite3.OperationalError:
                time.sleep(1.5 + attempt * 0.4)
        else:
            raise RuntimeError(f"{quarter}: demo insert kept failing")

        # ---- drug
        header, rows = payload["drug"]
        i = {k: pick(header, k) for k in
             ("primaryid", "caseid", "fda_dt", "drug_seq", "role_cod", "medicinalproduct",
              "substance", "indication", "route", "dose_vbm", "dose_amt", "dose_unit",
              "start_dt", "end_dt", "dur", "dur_cod")}
        cols = ["primaryid", "caseid", "fda_dt", "drug_seq", "role_cod",
                "medicinalproduct", "substance", "indication", "route", "dose_vbm",
                "dose_amt", "dose_unit", "start_dt", "end_dt", "dur", "dur_cod", "quarter"]
        data = [tuple(cell(r, i[k]) for k in
                      ("primaryid", "caseid", "fda_dt", "drug_seq", "role_cod",
                       "medicinalproduct", "substance", "indication", "route", "dose_vbm",
                       "dose_amt", "dose_unit", "start_dt", "end_dt", "dur", "dur_cod"))
                + (quarter,) for r in rows]
        for attempt in range(40):
            try:
                con.execute("BEGIN IMMEDIATE")
                con.executemany(
                    f"INSERT INTO drug({','.join(cols)}) VALUES({','.join('?' * len(cols))})",
                    data)
                con.execute("COMMIT")
                break
            except sqlite3.OperationalError:
                time.sleep(1.5 + attempt * 0.4)
        else:
            raise RuntimeError(f"{quarter}: drug insert kept failing")

        # ---- reac
        header, rows = payload["reac"]
        i = {k: pick(header, k) for k in ("primaryid", "caseid", "fda_dt", "pt", "outc_cod")}
        cols = ["primaryid", "caseid", "fda_dt", "pt", "outcome", "quarter"]
        data = [tuple(cell(r, i[k]) for k in
                      ("primaryid", "caseid", "fda_dt", "pt", "outc_cod")) + (quarter,)
                for r in rows]
        for attempt in range(40):
            try:
                con.execute("BEGIN IMMEDIATE")
                con.executemany(
                    f"INSERT INTO reac({','.join(cols)}) VALUES({','.join('?' * len(cols))})",
                    data)
                con.execute("COMMIT")
                break
            except sqlite3.OperationalError:
                time.sleep(1.5 + attempt * 0.4)
        else:
            raise RuntimeError(f"{quarter}: reac insert kept failing")

        con.execute("INSERT OR REPLACE INTO done VALUES(?,?,?,?,?,?)",
                    (quarter, counts["demo"], counts["drug"], counts["reac"], nbytes,
                     time.strftime("%Y-%m-%d %H:%M:%S")))
    finally:
        con.close()
    return {"quarter": quarter, **counts, "bytes": nbytes, "skipped": False}


def init_db() -> None:
    con = sqlite3.connect(DB, timeout=180, isolation_level=None)
    try:
        con.executescript(SCHEMA)
    finally:
        con.close()


def finalize() -> None:
    print("[finalize] building indexes (this can take a while) ...")
    con = sqlite3.connect(DB, timeout=600, isolation_level=None)
    try:
        con.executescript(INDEXES)
        n = con.execute("SELECT COUNT(*) FROM demo").fetchone()[0]
        print(f"[finalize] demo rows: {n:,}")
        for q in ("SELECT COUNT(*) FROM drug", "SELECT COUNT(*) FROM reac"):
            print(f"[finalize] {q}: {con.execute(q).fetchone()[0]:,}")
        con.execute("ANALYZE")
    finally:
        con.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--chunks", type=int, default=12,
                    help="parallel byte-range streams per archive")
    ap.add_argument("--limit", type=int, default=0, help="only the newest N quarters")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--from-quarter", default="")
    args = ap.parse_args()

    init_db()
    quarters = list_quarters()
    if args.from_quarter:
        quarters = [q for q in quarters if (int(q[:4]), int(q[-1])) >=
                    (int(args.from_quarter[:4]), int(args.from_quarter[-1]))]
    if args.limit:
        quarters = quarters[-args.limit:]
    print(f"[plan] {len(quarters)} quarters: {quarters[0]} .. {quarters[-1]}")

    ok, failed = [], []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(ingest_quarter, q, args.force, args.chunks): q
                for q in quarters}
        for k, fut in enumerate(as_completed(futs), 1):
            q = futs[fut]
            try:
                res = fut.result()
                ok.append(res)
                state = "cached" if res.get("skipped") else (
                    f"demo={res['demo']:,} drug={res['drug']:,} reac={res['reac']:,}")
                print(f"[{k:>3}/{len(quarters)}] {q}  {state}   "
                      f"({time.time() - t0:.0f}s)")
            except Exception as exc:  # noqa: BLE001
                failed.append((q, str(exc)[:200]))
                print(f"[{k:>3}/{len(quarters)}] {q}  FAILED: {str(exc)[:160]}")

    finalize()
    report = {"quarters_ok": len(ok), "quarters_failed": failed,
              "total_bytes": sum(r.get("bytes", 0) for r in ok)}
    (DERIVED / "faers_ingest_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[done] ok={len(ok)} failed={len(failed)} "
          f"bytes={report['total_bytes'] / 1e9:.2f} GB")
    if failed:
        print("failed quarters:", failed)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
