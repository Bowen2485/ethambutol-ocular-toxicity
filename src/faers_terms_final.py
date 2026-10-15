# -*- coding: utf-8 -*-
"""
Step 2a - Final ocular adverse-event term list.

Two complementary sources, both resolved against the local FAERS warehouse:
  (A) data-driven : every MedDRA PT occurring in ethambutol cases that matches a
                    broad ocular lexicon;
  (B) curated     : the recognised ethambutol ocular toxicity spectrum, already
                    verified against FAERS by exact counts in faers_terms.py.
Terms absent from the database are dropped, so no non-existent PT can enter the
analysis.

Output: data/derived/ocular_terms.json (term, group, source, n_index, in_faers)
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DB = DERIVED / "faers.sqlite"

OCULAR_PATTERNS = [
    r"\bEYE", r"\bEYES", r"\bOCUL", r"\bOPHTHALM", r"\bVISUAL", r"\bVISION",
    r"\bSIGHT", r"\bBLIND", r"\bOPTIC", r"\bRETIN", r"\bMACUL", r"\bVITREOUS",
    r"\bCHOROID", r"\bCONJUNCTIV", r"\bCORNE", r"\bIRIS\b", r"\bIRID",
    r"\bUVE", r"\bSCLER", r"\bLACRIMAL", r"\bLACRIMATION", r"\bTEAR",
    r"\bPUPIL", r"\bPTOSIS", r"\bDIPLOPIA", r"\bNYSTAGMUS", r"\bPHOTOPHOBIA",
    r"\bSCOTOMA", r"\bAMBLYOPIA", r"\bCATARACT", r"\bGLAUCOMA",
    r"\bPAPILLOEDEMA", r"\bPAPILLEDEMA", r"\bPAPILLITIS", r"\bCHALAZION",
    r"\bBLEPHAR", r"\bEYELID", r"\bPERIORBITAL", r"\bORBITAL",
    r"\bDYSCHROMATOPSIA", r"\bCHROMATOPSIA", r"\bHEMIANOPIA", r"\bQUADRANTANOPIA",
    r"\bFUNDUS", r"\bRETROBULBAR", r"\bVISUAL FIELD", r"\bVISUAL ACUITY",
    r"\bVISUAL IMPAIRMENT", r"\bEYEBALL", r"\bEYE PAIN", r"\bEYE IRRITATION",
    r"\bDRY EYE", r"\bEYE DISORDER", r"\bOPTIC NERVE", r"\bOPTIC DISC",
    r"\bOCULAR", r"\bEYE HAEMORRHAGE", r"\bEYE OEDEMA",
]
RX = re.compile("|".join(OCULAR_PATTERNS))

GROUP_RULES: list[tuple[str, str]] = [
    ("Optic nerve", r"OPTIC|PAPILLO|RETROBULBAR|PAPILLARY"),
    ("Retina / macula", r"RETIN|MACUL|CHOROID|VITREOUS|VITR"),
    ("Ocular surface / adnexa",
     r"CONJUNCTIV|CORNE|EYELID|BLEPHAR|LACRIMAL|LACRIM|DRY EYE|EYE PAIN|"
     r"EYE IRRITATION|EYE PRURITUS|EYE SWELLING|OCULAR DISCOMFORT|PTOSIS|"
     r"PERIORBITAL|CHALAZION|HORDEOLUM|ECTROPION|ENTROPION|XANTHELASMA"),
    ("Visual function",
     r"VISUAL|VISION|BLIND|SCOTOMA|HEMIANOPIA|DIPLOPIA|PHOTOPHOBIA|"
     r"CHROMATOPSIA|NYSTAGMUS|AMBLYOPIA|PHOTOPSIA|METAMORPHOPSIA|SIGHT"),
]


def classify(term: str) -> str:
    for group, pat in GROUP_RULES:
        if re.search(pat, term):
            return group
    return "Other ocular"


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"{DB} not found")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=600)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-800000")

    have = con.execute("SELECT name FROM sqlite_master WHERE type='table' "
                       "AND name='dedup_map'").fetchone()
    if not have:
        raise SystemExit("dedup_map missing - run faers_signal_analysis.py first")

    print("[A] MedDRA PTs occurring in ethambutol cases ...")
    # identity is the de-duplicated representative PRIMARYID; the reac and drug
    # tables are joined on primaryid, not on caseid (an earlier version joined on
    # caseid, which the reac table does not carry, and returned nothing)
    con.execute("DROP TABLE IF EXISTS temp.ethpid")
    con.execute("""
        CREATE TEMP TABLE ethpid AS
        SELECT DISTINCT d.primaryid AS primaryid
        FROM drug d
        JOIN dedup_map m ON m.primaryid = d.primaryid
        JOIN drugname dn ON dn.primaryid = d.primaryid
                        AND dn.drug_seq = d.drug_seq
        WHERE UPPER(COALESCE(dn.drugname,'')) LIKE '%ETHAMBUTOL%'
           OR UPPER(COALESCE(dn.prod_ai,''))  LIKE '%ETHAMBUTOL%'
    """)
    con.execute("CREATE INDEX IF NOT EXISTS temp.ix_ethpid ON ethpid(primaryid)")
    n_eth_pid = con.execute("SELECT COUNT(*) FROM ethpid").fetchone()[0]
    print(f"    {n_eth_pid:,} ethambutol report lines (representative primaryids)")

    rows = con.execute("""
        SELECT UPPER(r.pt) AS pt, COUNT(DISTINCT r.primaryid) AS n
        FROM reac r
        JOIN ethpid e ON e.primaryid = r.primaryid
        WHERE r.pt IS NOT NULL AND r.pt <> ''
        GROUP BY UPPER(r.pt)
    """).fetchall()
    print(f"    {len(rows)} distinct PTs across ethambutol cases")

    print("[B] whole-database PT counts for the ocular candidates ...")
    ocular_in_index = [(pt, n) for pt, n in rows if RX.search(pt)]
    print(f"    ocular-looking PTs in ethambutol cases: {len(ocular_in_index)}")

    # whole-database counts restricted to the terms of interest
    terms = sorted({pt for pt, _ in ocular_in_index})
    db_counts = {}
    for i in range(0, len(terms), 400):
        chunk = terms[i:i + 400]
        ph = ",".join("?" * len(chunk))
        q = f"""SELECT UPPER(r.pt) AS pt, COUNT(DISTINCT r.primaryid) AS n
                FROM reac r JOIN dedup_map m ON r.primaryid = m.primaryid
                WHERE UPPER(r.pt) IN ({ph}) GROUP BY UPPER(r.pt)"""
        db_counts.update({p: n for p, n in con.execute(q, chunk)})
    print(f"    database counts retrieved for {len(db_counts)} terms")

    records = []
    for pt, n in sorted(ocular_in_index, key=lambda kv: -kv[1]):
        records.append({"term": pt, "group": classify(pt),
                        "source": "Data-driven (in ethambutol cases)",
                        "n_index": n, "in_faers": db_counts.get(pt, 0)})
    seen = {r["term"] for r in records}

    # merge the curated panel already validated against openFDA
    curated_path = DERIVED / "ocular_terms.json"
    n_curated = 0
    if curated_path.exists():
        for rec in json.loads(curated_path.read_text(encoding="utf-8")):
            if rec["term"] in seen:
                continue
            seen.add(rec["term"])
            rec = dict(rec)
            rec["source"] = "Curated panel"
            records.append(rec)
            n_curated += 1
        print(f"[C] merged {n_curated} additional curated terms")

    df = pd.DataFrame(records)
    df = df[df.in_faers > 0]
    df = df.sort_values(["source", "n_index"], ascending=[True, False])
    df.to_csv(DERIVED / "ocular_terms.csv", index=False, encoding="utf-8-sig")
    DERIVED.joinpath("ocular_terms.json").write_text(
        json.dumps(df.to_dict("records"), indent=2, ensure_ascii=False),
        encoding="utf-8")

    print(f"\n[D] final panel: {len(df)} ocular MedDRA PTs")
    print(df.groupby(["source", "group"]).size().to_string())
    print(f"\n   terms with >=1 ethambutol case: {int((df.n_index > 0).sum())}")
    print(f"-> {DERIVED / 'ocular_terms.json'}")
    con.close()


if __name__ == "__main__":
    main()
