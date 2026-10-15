# -*- coding: utf-8 -*-
"""Fetch journalTitle / authorString for a PMID list via Europe PMC (resultType=lite)."""
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

CTX = ssl._create_unverified_context()
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
HEADERS = {"User-Agent": "Mozilla/5.0"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(query):
    params = {"query": query, "format": "json", "pageSize": "100",
              "resultType": "lite"}
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            time.sleep(2 * (attempt + 1))
    return {}


def main():
    pms = [p.strip() for p in re.split(r"[,\s]+", open(sys.argv[1], encoding="utf-8").read())
           if p.strip().isdigit()]
    pms = sorted(set(pms))
    out = {}
    for i in range(0, len(pms), 25):
        chunk = pms[i:i + 25]
        q = " OR ".join(f"EXT_ID:{p}" for p in chunk)
        d = fetch(q)
        for r in d.get("resultList", {}).get("result", []):
            out[str(r.get("pmid"))] = {
                "journal": r.get("journalTitle"),
                "authors": r.get("authorString"),
                "year": r.get("pubYear"),
                "title": r.get("title"),
                "doi": r.get("doi"),
            }
        print(f"  batch {i//25+1}: got {len(out)} total")
        time.sleep(0.4)
    missing = [p for p in pms if p not in out]
    path = os.path.join(ROOT, "data", "derived", "journal_map.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"requested={len(pms)} resolved={len(out)} missing={missing}")
    print("written", path)


if __name__ == "__main__":
    main()
