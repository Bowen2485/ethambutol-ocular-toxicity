# -*- coding: utf-8 -*-
"""
Assemble the citation details for the Mao & Ou 2026 paper and check its indexing.

The paper has to be cited, so the reference needs to be accurate.  Two things are
needed: the bibliographic details, and whether it carries a PubMed identifier.  Europe
PMC indexing matters here beyond form - if the journal is not indexed in PubMed or
MEDLINE, the reference can still be cited but the reader cannot look it up through the
usual route, which is worth knowing before it goes into a manuscript.
"""
from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}
ROOT = Path(__file__).resolve().parents[1]

print("=" * 90)
print("1. What the earlier search stored")
print("=" * 90)
p = ROOT / "docs" / "literature_ethambutol_titles.json"
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    found = False
    for angle, items in d.items():
        for r in items:
            ti = r.get("title") or ""
            if "anti-tuberculosis drugs" in ti.lower() or \
               "antituberculosis drugs" in ti.lower():
                found = True
                ji = r.get("journalInfo") or {}
                j = ji.get("journal") or {}
                print(f"  angle      : {angle}")
                print(f"  title      : {ti}")
                print(f"  authors    : {r.get('authorString')}")
                print(f"  journal    : {j.get('title')}")
                print(f"  year/vol/is: {r.get('pubYear')} / {ji.get('volume')} / "
                      f"{ji.get('issue')}")
                print(f"  pages      : {r.get('pageInfo')}")
                print(f"  pmid       : {r.get('pmid')!r}")
                print(f"  doi        : {r.get('doi')!r}")
                print(f"  pmcid      : {r.get('pmcid')!r}")
                print()
    if not found:
        print("  the paper is not in the stored results; it was found via web search")
else:
    print("  archive not found")

print("=" * 90)
print("2. Is it indexed in Europe PMC / PubMed?")
print("=" * 90)
query = 'TITLE:"Mining of Adverse Reaction Signals and Medication Insights"'
params = urllib.parse.urlencode({"query": query, "format": "json", "pageSize": 5,
                                 "resultType": "core"})
try:
    req = urllib.request.Request(
        f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}",
        headers=UA)
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        j = json.loads(r.read())
    print(f"  hit count: {j.get('hitCount')}")
    for x in j.get("resultList", {}).get("result", []):
        ji = x.get("journalInfo") or {}
        print(f"    {x.get('pubYear')}  {(x.get('title') or '')[:88]}")
        print(f"      PMID={x.get('pmid')!r}  DOI={x.get('doi')!r}  "
              f"PMCID={x.get('pmcid')!r}")
        print(f"      journal={(ji.get('journal') or {}).get('title')!r}")
except Exception as exc:  # noqa: BLE001
    print(f"  query failed: {type(exc).__name__}: {str(exc)[:120]}")

print()
print("=" * 90)
print("3. Also check the other two, so the numbering is planned once")
print("=" * 90)
for label, q in (("Suresh 2026 VigiBase", 'EXT_ID:42240730'),
                 ("Gupta 2026 meta-analysis", 'EXT_ID:41905405'),
                 ("Li 2026 ferroptosis", 'EXT_ID:41563626')):
    params = urllib.parse.urlencode({"query": q, "format": "json", "pageSize": 1,
                                     "resultType": "core"})
    try:
        req = urllib.request.Request(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}",
            headers=UA)
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            j = json.loads(r.read())
        res = j.get("resultList", {}).get("result", [])
        if res:
            x = res[0]
            ji = x.get("journalInfo") or {}
            print(f"  {label}")
            print(f"      {x.get('authorString')}")
            print(f"      {(x.get('title') or '')[:100]}")
            print(f"      {(ji.get('journal') or {}).get('title')} "
                  f"{x.get('pubYear')};{ji.get('volume')}({ji.get('issue')})"
                  f":{x.get('pageInfo')}")
            print(f"      PMID={x.get('pmid')} DOI={x.get('doi')}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label}: {type(exc).__name__}")
    print()
