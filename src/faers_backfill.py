# -*- coding: utf-8 -*-
"""
Step 1b - Backfill the drug names and therapy dates.

The first ingest pass missed the drug-name columns because FAERS names them
`drugname` / `prod_ai` (openFDA's harmonised view calls them `medicinalproduct`
and `substance`).  Therapy dates live in a separate THER table keyed by
(primaryid, drug_seq), so they are stored in their own table rather than being
denormalised onto 98.9 million drug rows.

Re-reading the cached quarterly archives is far cheaper than re-downloading, and
the work is idempotent: a quarter already processed is skipped.

    drug.drugname_raw  <- DRUG.drugname
    drug.prod_ai       <- DRUG.prod_ai
    drug.medicinalproduct <- upper(drugname)   (normalised lookup key)
    drug.substance        <- upper(prod_ai)    (normalised lookup key)
    drug_ther          <- THER.start_dt/end_dt/dur/dur_cod
    demo_extra         <- DEMO.age_grp / auth_num / lit_ref / caseversion
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
PROGRESS = DERIVED / "backfill_progress.json"

BATCH = 400_000


def connect(rw: bool = True) -> sqlite3.Connection:
    con = (sqlite3.connect(DB, timeout=1200, isolation_level=None) if rw
           else sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=600))
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-800000")
    con.execute("PRAGMA synchronous=OFF")
    return con


def ensure_columns(con: sqlite3.Connection) -> None:
    have = {r[1] for r in con.execute("PRAGMA table_info(drug)")}
    for col in ("drugname_raw", "prod_ai"):
        if col not in have:
            con.execute(f"ALTER TABLE drug ADD COLUMN {col} TEXT")
            print(f"  added drug.{col}")
    have = {r[1] for r in con.execute("PRAGMA table_info(demo)")}
    for col in ("age_grp", "auth_num", "lit_ref", "caseversion"):
        if col not in have:
            con.execute(f"ALTER TABLE demo ADD COLUMN {col} TEXT")
            print(f"  added demo.{col}")
    con.execute("""CREATE TABLE IF NOT EXISTS drug_ther (
                       primaryid TEXT, caseid TEXT, drug_seq TEXT,
                       start_dt TEXT, end_dt TEXT, dur TEXT, dur_cod TEXT)""")


def read_member(zf: zipfile.ZipFile, prefixes: tuple[str, ...]) -> list[str]:
    for name in zf.namelist():
        base = Path(name).name.lower()
        if not base.endswith(".txt"):
            continue
        if any(base.startswith(p) for p in prefixes):
            if any(x in base for x in ("deleted", "size", "stat")):
                continue
            with zf.open(name) as fh:
                txt = fh.read().decode("latin-1")
            lines = txt.splitlines()
            if not lines:
                return []
            header = [h.strip().lower().lstrip("\ufeff") for h in lines[0].split("$")]
            return header, lines[1:]
    return None, []


def idx(header: list[str], *names, default=None):
    for n in names:
        if n in header:
            return header.index(n)
    return default


def backfill_quarter(con: sqlite3.Connection, quarter: str) -> dict:
    z = CACHE / f"{quarter}.zip"
    if not z.exists():
        return {"quarter": quarter, "status": "archive missing"}
    out = {"quarter": quarter}
    with zipfile.ZipFile(z) as zf:
        # ---------------- DRUG names
        header, lines = read_member(zf, ("drug",))
        if header:
            i_pid = idx(header, "primaryid", "isr")
            i_seq = idx(header, "drug_seq")
            i_name = idx(header, "drugname")
            i_ai = idx(header, "prod_ai")
            i_ther_seq = i_seq
            con.execute("BEGIN IMMEDIATE")
            con.execute("CREATE TEMP TABLE IF NOT EXISTS bf_drug ("
                        "primaryid TEXT, drug_seq TEXT, drugname_raw TEXT, prod_ai TEXT)")
            con.execute("DELETE FROM bf_drug")
            n = 0
            buf = []
            for ln in lines:
                if not ln.strip():
                    continue
                p = ln.split("$")
                buf.append((
                    p[i_pid].strip() if i_pid is not None and i_pid < len(p) else "",
                    p[i_seq].strip() if i_seq is not None and i_seq < len(p) else "",
                    p[i_name].strip() if i_name is not None and i_name < len(p) else "",
                    p[i_ai].strip() if i_ai is not None and i_ai < len(p) else "",
                ))
                if len(buf) >= BATCH:
                    con.executemany("INSERT INTO bf_drug VALUES(?,?,?,?)", buf)
                    n += len(buf)
                    buf = []
            if buf:
                con.executemany("INSERT INTO bf_drug VALUES(?,?,?,?)", buf)
                n += len(buf)
            con.execute("""UPDATE drug SET
                             drugname_raw = (SELECT b.drugname_raw FROM bf_drug b
                                             WHERE b.primaryid = drug.primaryid
                                               AND b.drug_seq = drug.drug_seq),
                             prod_ai = (SELECT b.prod_ai FROM bf_drug b
                                        WHERE b.primaryid = drug.primaryid
                                          AND b.drug_seq = drug.drug_seq),
                             medicinalproduct = UPPER(COALESCE((SELECT b.drugname_raw
                                        FROM bf_drug b WHERE b.primaryid = drug.primaryid
                                          AND b.drug_seq = drug.drug_seq),'')),
                             substance = UPPER(COALESCE((SELECT b.prod_ai
                                        FROM bf_drug b WHERE b.primaryid = drug.primaryid
                                          AND b.drug_seq = drug.drug_seq),''))
                           WHERE primaryid IN (SELECT primaryid FROM bf_drug)
                             AND quarter = ?""", (quarter,))
            con.execute("COMMIT")
            out["drug_rows_read"] = n
        else:
            out["drug_rows_read"] = 0

        # ---------------- THER dates
        header, lines = read_member(zf, ("ther",))
        if header and lines:
            i_pid = idx(header, "primaryid", "isr")
            i_case = idx(header, "caseid", "case")
            i_seq = idx(header, "dsg_drug_seq", "drug_seq")
            i_s = idx(header, "start_dt")
            i_e = idx(header, "end_dt")
            i_d = idx(header, "dur")
            i_dc = idx(header, "dur_cod")
            con.execute("BEGIN IMMEDIATE")
            con.execute("DELETE FROM drug_ther WHERE primaryid IN "
                        "(SELECT primaryid FROM drug WHERE quarter = ?)", (quarter,))
            buf = []
            n = 0
            for ln in lines:
                if not ln.strip():
                    continue
                p = ln.split("$")

                def g(i):
                    return p[i].strip() if i is not None and i < len(p) else ""
                buf.append((g(i_pid), g(i_case), g(i_seq), g(i_s), g(i_e), g(i_d), g(i_dc)))
                if len(buf) >= BATCH:
                    con.executemany("INSERT INTO drug_ther VALUES(?,?,?,?,?,?,?)", buf)
                    n += len(buf)
                    buf = []
            if buf:
                con.executemany("INSERT INTO drug_ther VALUES(?,?,?,?,?,?,?)", buf)
                n += len(buf)
            con.execute("COMMIT")
            out["ther_rows"] = n

        # ---------------- DEMO extras
        header, lines = read_member(zf, ("demo",))
        if header and lines:
            i_pid = idx(header, "primaryid", "isr")
            i_ag = idx(header, "age_grp")
            i_auth = idx(header, "auth_num")
            i_lit = idx(header, "lit_ref")
            i_cv = idx(header, "caseversion")
            if any(x is not None for x in (i_ag, i_auth, i_lit, i_cv)):
                con.execute("BEGIN IMMEDIATE")
                con.execute("CREATE TEMP TABLE IF NOT EXISTS bf_demo ("
                            "primaryid TEXT, age_grp TEXT, auth_num TEXT, "
                            "lit_ref TEXT, caseversion TEXT)")
                con.execute("DELETE FROM bf_demo")
                buf = []
                n = 0
                for ln in lines:
                    if not ln.strip():
                        continue
                    p = ln.split("$")

                    def g(i):
                        return p[i].strip() if i is not None and i < len(p) else ""
                    buf.append((g(i_pid), g(i_ag), g(i_auth), g(i_lit), g(i_cv)))
                    if len(buf) >= BATCH:
                        con.executemany("INSERT INTO bf_demo VALUES(?,?,?,?,?)", buf)
                        n += len(buf)
                        buf = []
                if buf:
                    con.executemany("INSERT INTO bf_demo VALUES(?,?,?,?,?)", buf)
                    n += len(buf)
                for col in ("age_grp", "auth_num", "lit_ref", "caseversion"):
                    con.execute(f"""UPDATE demo SET {col} = (SELECT b.{col}
                                    FROM bf_demo b WHERE b.primaryid = demo.primaryid)
                                    WHERE primaryid IN (SELECT primaryid FROM bf_demo)""")
                con.execute("COMMIT")
                out["demo_rows"] = n
    out["status"] = "ok"
    return out


def main() -> int:
    quarters = sorted(p.stem for p in CACHE.glob("*.zip"))
    print(f"[plan] {len(quarters)} cached quarters")
    done = {}
    if PROGRESS.exists():
        try:
            done = json.loads(PROGRESS.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            done = {}
    con = connect(rw=True)
    ensure_columns(con)
    t0 = time.time()
    for i, q in enumerate(quarters, 1):
        if done.get(q, {}).get("status") == "ok":
            continue
        try:
            res = backfill_quarter(con, q)
        except Exception as exc:  # noqa: BLE001
            res = {"quarter": q, "status": f"failed {type(exc).__name__}: {str(exc)[:120]}"}
        done[q] = res
        PROGRESS.write_text(json.dumps(done, indent=1), encoding="utf-8")
        print(f"[{i:>3}/{len(quarters)}] {q}  {res.get('status')}  "
              f"drug={res.get('drug_rows_read','-')} ther={res.get('ther_rows','-')}  "
              f"({time.time()-t0:.0f}s)")

    print("\n[verify] ...")
    print("  drug rows with a name :",
          con.execute("SELECT COUNT(*) FROM drug WHERE COALESCE(medicinalproduct,'')<>''")
          .fetchone()[0])
    print("  drug_ther rows        :",
          con.execute("SELECT COUNT(*) FROM drug_ther").fetchone()[0])
    n_eth = con.execute("""SELECT COUNT(*) FROM drug
                           WHERE medicinalproduct LIKE '%ETHAMBUTOL%'
                              OR substance LIKE '%ETHAMBUTOL%'""").fetchone()[0]
    print("  drug rows w/ ethambutol:", f"{n_eth:,}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
