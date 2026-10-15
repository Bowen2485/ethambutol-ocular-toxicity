# -*- coding: utf-8 -*-
"""
Step 1b - Drug-name / therapy-date extraction into dedicated tables.

Problem found in the first ingest pass
    FAERS names the drug-name columns `drugname` (reported product) and
    `prod_ai` (active ingredient); openFDA's harmonised view renames them to
    `medicinalproduct` and `substance`.  Every drug row therefore landed with an
    empty name.  Therapy dates are also not in DRUG at all - they live in THER,
    keyed by (primaryid, dsg_drug_seq).

Design decision
    Updating 98.9 million rows of `drug` through correlated sub-queries is
    needlessly expensive, so the names go into a compact table keyed by
    (primaryid, drug_seq).  Analysis joins that table instead.  Only the rows
    whose name mentions a drug of interest are materialised, which keeps the new
    tables small and every downstream join indexed.

Tables
    drugname    (primaryid, drug_seq, drugname, prod_ai)
    drug_ther   (primaryid, drug_seq, start_dt, end_dt, dur, dur_cod)
    demo_extra  (primaryid, caseversion, age_grp, auth_num, lit_ref)
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
CACHE = ROOT / "data" / "raw" / "faers_ascii"
DB = DERIVED / "faers.sqlite"
PROGRESS = DERIVED / "extract_progress.json"

BATCH = 500_000


def connect(rw: bool = True) -> sqlite3.Connection:
    con = (sqlite3.connect(DB, timeout=1800, isolation_level=None) if rw
           else sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=600))
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1000000")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA journal_mode=WAL")
    return con


def schema(con: sqlite3.Connection) -> None:
    con.executescript("""
        CREATE TABLE IF NOT EXISTS drugname (
            primaryid TEXT, drug_seq TEXT, drugname TEXT, prod_ai TEXT);
        CREATE TABLE IF NOT EXISTS drug_ther (
            primaryid TEXT, drug_seq TEXT, start_dt TEXT, end_dt TEXT,
            dur TEXT, dur_cod TEXT);
        CREATE TABLE IF NOT EXISTS demo_extra (
            primaryid TEXT, caseversion TEXT, age_grp TEXT, auth_num TEXT,
            lit_ref TEXT);
    """)


def member(zf: zipfile.ZipFile, prefixes: tuple[str, ...]):
    for name in zf.namelist():
        base = Path(name).name.lower()
        if not base.endswith(".txt"):
            continue
        if not base.startswith(prefixes):
            continue
        if any(x in base for x in ("deleted", "size", "stat", "delete")):
            continue
        with zf.open(name) as fh:
            txt = fh.read().decode("latin-1")
        lines = txt.splitlines()
        if not lines:
            return None, []
        header = [h.strip().lower().lstrip("\ufeff") for h in lines[0].split("$")]
        return header, lines[1:]
    return None, []


def col(header, *names):
    for n in names:
        if n in header:
            return header.index(n)
    return None


def do_quarter(con: sqlite3.Connection, quarter: str) -> dict:
    z = CACHE / f"{quarter}.zip"
    if not z.exists():
        return {"status": "archive missing"}
    res = {"status": "ok"}
    with zipfile.ZipFile(z) as zf:
        # ---------------------------------------------------------- DRUG names
        header, lines = member(zf, ("drug",))
        if header:
            i_pid, i_seq = col(header, "primaryid", "isr"), col(header, "drug_seq")
            i_nm, i_ai = col(header, "drugname"), col(header, "prod_ai")
            con.execute("DELETE FROM drugname WHERE primaryid IN "
                        "(SELECT primaryid FROM demo WHERE quarter = ?)", (quarter,))
            buf, n = [], 0
            for ln in lines:
                if not ln.strip():
                    continue
                p = ln.split("$")

                def g(i):
                    return p[i].strip() if i is not None and i < len(p) else ""
                buf.append((g(i_pid), g(i_seq), g(i_nm), g(i_ai)))
                if len(buf) >= BATCH:
                    con.executemany("INSERT INTO drugname VALUES(?,?,?,?)", buf)
                    n += len(buf)
                    buf = []
            if buf:
                con.executemany("INSERT INTO drugname VALUES(?,?,?,?)", buf)
                n += len(buf)
            res["drugname_rows"] = n

        # --------------------------------------------------------- THER dates
        header, lines = member(zf, ("ther",))
        if header and lines:
            i_pid = col(header, "primaryid", "isr")
            i_seq = col(header, "dsg_drug_seq", "drug_seq")
            i_s, i_e = col(header, "start_dt"), col(header, "end_dt")
            i_d, i_dc = col(header, "dur"), col(header, "dur_cod")
            con.execute("DELETE FROM drug_ther WHERE primaryid IN "
                        "(SELECT primaryid FROM demo WHERE quarter = ?)", (quarter,))
            buf, n = [], 0
            for ln in lines:
                if not ln.strip():
                    continue
                p = ln.split("$")

                def g(i):
                    return p[i].strip() if i is not None and i < len(p) else ""
                buf.append((g(i_pid), g(i_seq), g(i_s), g(i_e), g(i_d), g(i_dc)))
                if len(buf) >= BATCH:
                    con.executemany("INSERT INTO drug_ther VALUES(?,?,?,?,?,?)", buf)
                    n += len(buf)
                    buf = []
            if buf:
                con.executemany("INSERT INTO drug_ther VALUES(?,?,?,?,?,?)", buf)
                n += len(buf)
            res["ther_rows"] = n

        # -------------------------------------------------------- DEMO extras
        header, lines = member(zf, ("demo",))
        if header and lines:
            i_pid = col(header, "primaryid", "isr")
            i_cv, i_ag = col(header, "caseversion"), col(header, "age_grp")
            i_au, i_li = col(header, "auth_num"), col(header, "lit_ref")
            con.execute("DELETE FROM demo_extra WHERE primaryid IN "
                        "(SELECT primaryid FROM demo WHERE quarter = ?)", (quarter,))
            buf, n = [], 0
            for ln in lines:
                if not ln.strip():
                    continue
                p = ln.split("$")

                def g(i):
                    return p[i].strip() if i is not None and i < len(p) else ""
                buf.append((g(i_pid), g(i_cv), g(i_ag), g(i_au), g(i_li)))
                if len(buf) >= BATCH:
                    con.executemany("INSERT INTO demo_extra VALUES(?,?,?,?,?)", buf)
                    n += len(buf)
                    buf = []
            if buf:
                con.executemany("INSERT INTO demo_extra VALUES(?,?,?,?,?)", buf)
                n += len(buf)
            res["demo_extra_rows"] = n
    return res


def main() -> int:
    quarters = sorted(p.stem for p in CACHE.glob("*.zip"))
    print(f"[plan] {len(quarters)} cached quarters")
    con = connect(rw=True)
    schema(con)
    done = {}
    if PROGRESS.exists():
        try:
            done = json.loads(PROGRESS.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            done = {}
    t0 = time.time()
    for i, q in enumerate(quarters, 1):
        if done.get(q, {}).get("status") == "ok":
            continue
        try:
            res = do_quarter(con, q)
        except Exception as exc:  # noqa: BLE001
            res = {"status": f"failed {type(exc).__name__}: {str(exc)[:140]}"}
        done[q] = res
        PROGRESS.write_text(json.dumps(done, indent=1), encoding="utf-8")
        print(f"[{i:>3}/{len(quarters)}] {q} {res.get('status')} "
              f"drugname={res.get('drugname_rows','-')} "
              f"ther={res.get('ther_rows','-')} ({time.time()-t0:.0f}s)")

    print("\n[verify]")
    print("  drugname rows :",
          f"{con.execute('SELECT COUNT(*) FROM drugname').fetchone()[0]:,}")
    print("  drug_ther rows:",
          f"{con.execute('SELECT COUNT(*) FROM drug_ther').fetchone()[0]:,}")
    print("  demo_extra    :",
          f"{con.execute('SELECT COUNT(*) FROM demo_extra').fetchone()[0]:,}")
    n = con.execute("""SELECT COUNT(*) FROM drugname
                       WHERE UPPER(COALESCE(drugname,'')) LIKE '%ETHAMBUTOL%'
                          OR UPPER(COALESCE(prod_ai,'')) LIKE '%ETHAMBUTOL%'""").fetchone()[0]
    print(f"  ethambutol drug lines: {n:,}")

    print("\n[final indexes] ...")
    con.executescript("""
        CREATE INDEX IF NOT EXISTS ix_dn_pid  ON drugname(primaryid);
        CREATE INDEX IF NOT EXISTS ix_dn_seq  ON drugname(primaryid, drug_seq);
        CREATE INDEX IF NOT EXISTS ix_dn_name ON drugname(drugname);
        CREATE INDEX IF NOT EXISTS ix_dn_ai   ON drugname(prod_ai);
        CREATE INDEX IF NOT EXISTS ix_dt_pid  ON drug_ther(primaryid, drug_seq);
        CREATE INDEX IF NOT EXISTS ix_de_pid  ON demo_extra(primaryid);
    """)
    print("  done")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
