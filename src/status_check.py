# -*- coding: utf-8 -*-
"""Quick status check of the FAERS warehouse extraction."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"
PROG = ROOT / "data" / "derived" / "extract_progress.json"

if PROG.exists():
    j = json.loads(PROG.read_text(encoding="utf-8"))
    ok = sum(1 for v in j.values() if v.get("status") == "ok")
    bad = [(k, v.get("status")) for k, v in j.items() if v.get("status") != "ok"]
    print(f"extract quarters: ok={ok} failed={len(bad)}")
    for k, s in bad[:3]:
        print(f"   {k}: {s}")

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=120)
con.execute("PRAGMA query_only=1")
for t in ("demo", "drug", "reac"):
    try:
        print(f"{t:10s}: {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>12,}")
    except Exception as exc:  # noqa: BLE001
        print(f"{t:10s}: {exc}")
for t in ("drugname", "drug_ther", "demo_extra", "dedup_map", "drug_case",
          "ocular_case", "term_db"):
    try:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t:10s}: {n:>12,}")
    except Exception as exc:  # noqa: BLE001
        print(f"{t:10s}: (missing)")

for drug in ("ethambutol", "isoniazid", "rifampicin", "pyrazinamide",
             "streptomycin", "linezolid"):
    n = con.execute("""SELECT COUNT(DISTINCT dn.primaryid) FROM drugname dn
                       WHERE UPPER(COALESCE(dn.drugname,'')) LIKE ?
                          OR UPPER(COALESCE(dn.prod_ai,'')) LIKE ?""",
                    (f"%{drug.upper()}%", f"%{drug.upper()}%")).fetchone()[0]
    print(f"  drug lines mentioning {drug:14s}: {n:>10,}")
con.close()
