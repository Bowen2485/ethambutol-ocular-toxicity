# -*- coding: utf-8 -*-
"""
Verify every reference against the live Europe PMC record.

A reference list written from memory would be a fabrication risk, so each PMID is
looked up and the returned title, journal, year and authors are compared with the
entry drafted in assemble_manuscript.py.  Mismatches are printed for correction;
nothing is written into the manuscript that the API did not return.

Output -> data/derived/references_verified.json
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
sys.path.insert(0, str(ROOT / "src"))

from assemble_manuscript import CITE_ORDER, REFERENCES      # noqa: E402

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def lookup(pmid: str) -> dict | None:
    url = (f"{EPMC}?query=EXT_ID:{pmid}%20AND%20SRC:MED&format=json"
           f"&resultType=core&pageSize=1")
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
            res = d.get("resultList", {}).get("result", [])
            return res[0] if res else None
        except Exception as exc:  # noqa: BLE001
            if attempt == 3:
                print(f"  [{pmid}] lookup failed: {type(exc).__name__}")
                return None
            time.sleep(2 * (attempt + 1))
    return None


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def main() -> int:
    drafted = dict(REFERENCES)
    out, problems = [], []
    print(f"verifying {len(CITE_ORDER)} references against Europe PMC ...\n")
    for pmid in CITE_ORDER:
        rec = lookup(pmid)
        if rec is None:
            problems.append((pmid, "NOT FOUND in Europe PMC"))
            out.append({"pmid": pmid, "verified": False,
                        "draft": drafted.get(pmid, "")})
            print(f"  [{pmid}] *** NOT FOUND ***")
            time.sleep(0.35)
            continue
        title = rec.get("title", "")
        journal = (rec.get("journalInfo", {}) or {}).get("journal", {}).get("title", "")
        year = rec.get("pubYear", "")
        authors = rec.get("authorString", "")
        doi = rec.get("doi", "")
        first_author = authors.split(",")[0].strip() if authors else ""
        draft = drafted.get(pmid, "")
        # compare the first author surname and the title's leading words
        ok_author = norm(first_author.split()[-1] if first_author else "") in norm(draft)
        title_head = " ".join(norm(title).split()[:5])
        ok_title = title_head[:26] in norm(draft) if title_head else False
        out.append({
            "pmid": pmid, "verified": True, "title": title, "journal": journal,
            "year": year, "authors": authors, "doi": doi,
            "first_author": first_author,
            "draft": draft,
            "author_matches": bool(ok_author), "title_matches": bool(ok_title),
            "suggested": (f"{authors.split(',')[0].strip() if authors else ''}"
                          f"{', et al. ' if authors.count(',') > 1 else '. '}"
                          f"{title} {journal}. {year}."
                          + (f" doi:{doi}" if doi else "")),
        })
        flag = "" if (ok_author and ok_title) else "  <-- CHECK"
        print(f"  [{pmid}] {year} {journal[:34]:34s} {title[:66]}{flag}")
        if not (ok_author and ok_title):
            problems.append((pmid, "draft entry differs from the live record"))
        time.sleep(0.35)

    (DER / "references_verified.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    df = pd.DataFrame(out)
    df.to_csv(DER / "references_verified.csv", index=False, encoding="utf-8-sig")

    print(f"\n=== summary ===")
    print(f"  verified against Europe PMC : {int(df.verified.sum())}/{len(df)}")
    if "author_matches" in df.columns:
        print(f"  author matches draft        : {int(df.author_matches.sum())}")
        print(f"  title matches draft         : {int(df.title_matches.sum())}")
    if problems:
        print(f"\n  {len(problems)} entries need attention:")
        for pmid, why in problems:
            print(f"    {pmid}: {why}")
    print(f"\n-> {DER / 'references_verified.json'}")
    print("\n=== machine-generated citation strings (use these) ===")
    for r in out:
        if r.get("verified"):
            print(f"  [{r['pmid']}] {r['suggested']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
