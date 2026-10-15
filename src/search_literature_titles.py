# -*- coding: utf-8 -*-
"""
Answer "has this paper been written already" with a title-restricted search.

The first attempt sorted by citation count, which surfaced highly cited reviews that
merely mentioned ethambutol among other drugs - 1,158 hits for the epidemiology angle,
almost none of them relevant.  Sorting by citations answers "what is influential",
which is not the question; the question is "what is on this exact subject".

Requiring ethambutol in the title is the filter that works, because a paper about
ethambutol ocular toxicity will name the drug in its title, while a review that
mentions it in passing will not.  Two further angles - pharmacovigilance signal work on
antitubercular drugs generally, and the ferroptosis mechanism - are searched separately
because their titles may not name ethambutol even when the content bears on it.

Recent years are listed in full rather than sampled, since a competing paper is most
likely to be recent.
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

#: (label, query, sort) - sort by date where recency matters, citations otherwise
SEARCHES = [
    ("ethambutol in the title, any subject",
     'TITLE:"ethambutol"', "P_PDATE_D desc"),
    ("ethambutol + eye/optic in title",
     '(TITLE:"ethambutol") AND (TITLE:"optic" OR TITLE:"ocular" OR TITLE:"eye" OR '
     'TITLE:"ophthalmic" OR TITLE:"retina" OR TITLE:"vision")', "P_PDATE_D desc"),
    ("ethambutol + pharmacovigilance/FAERS anywhere",
     '(TITLE:"ethambutol") AND (FAERS OR "adverse event reporting system" OR '
     'pharmacovigilance OR "reporting odds ratio" OR disproportionality)',
     "P_PDATE_D desc"),
    ("ethambutol + mechanism/network anywhere",
     '(TITLE:"ethambutol") AND (ferroptosis OR "network pharmacology" OR '
     '"network toxicology" OR docking OR "molecular dynamics" OR transcriptom*)',
     "P_PDATE_D desc"),
    ("antitubercular FAERS signal mining (ethambutol may not be in title)",
     '(TITLE:"tuberculosis" OR TITLE:"antitubercul*" OR TITLE:"anti-tubercul*") AND '
     '(FAERS OR "reporting odds ratio" OR disproportionality)',
     "P_PDATE_D desc"),
    ("ethambutol retinal ganglion / ferroptosis mechanism",
     '(ethambutol) AND ("retinal ganglion" OR retina) AND (ferroptosis OR '
     '"cell death" OR mitochondrial) AND (PUB_YEAR:[2022 TO 2027])',
     "P_PDATE_D desc"),
]

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "literature_ethambutol_titles.json"


def search(query: str, sort: str, page_size: int = 100) -> tuple[int, list]:
    params = urllib.parse.urlencode({
        "query": query, "format": "json", "pageSize": page_size,
        "resultType": "core", "sort": sort,
    })
    req = urllib.request.Request(f"{BASE}?{params}", headers=UA)
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        j = json.loads(r.read())
    return j.get("hitCount", 0), j.get("resultList", {}).get("result", [])


store = {}
for label, q, sort in SEARCHES:
    print("=" * 108)
    print(f"{label}")
    print(f"  query: {q}")
    print("=" * 108)
    try:
        n, res = search(q, sort)
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED {type(exc).__name__}: {str(exc)[:90]}")
        continue
    store[label] = [{k: r.get(k) for k in ("title", "pubYear", "pmid", "doi",
                                           "journalInfo", "authorString")}
                    for r in res]
    print(f"  {n:,} hits, showing {len(res)} most recent\n")
    for r in res:
        year = r.get("pubYear", "?")
        title = (r.get("title") or "").rstrip(".")
        jt = ((r.get("journalInfo") or {}).get("journal") or {}).get("title", "") or ""
        pm = r.get("pmid", "")
        print(f"  {year}  {title[:100]}")
        if jt:
            print(f"        {jt[:80]}{'  PMID:' + pm if pm else ''}")
    time.sleep(0.6)
    print()

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(store, indent=1, ensure_ascii=False)[:4_000_000],
               encoding="utf-8")
print(f"-> {OUT}")

print()
print("=" * 108)
print("Assessment")
print("=" * 108)
print("""  A paper that pre-empts this manuscript would have to combine: ethambutol, a
  spontaneous-reporting database, an ocular or optic-nerve focus, and preferably a
  mechanistic arm.  The lists above are read for that combination, and anything found
  is reported in the answer rather than buried here.""")
