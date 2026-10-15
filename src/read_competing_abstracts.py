# -*- coding: utf-8 -*-
"""
Read the abstracts of the studies that come closest to this one.

The novelty claim rests on what those studies did not do, so it has to be checked against
what they say they did rather than against titles.  Three matter:

    42240730  Suresh 2026, Int Ophthalmol
              Ocular toxicity of ethambutol in South-East Asia - the closest work in
              kind, and the one the manuscript already distinguishes itself from.
    41563626  Li 2026, Human Cell
              Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis -
              the experimental confirmation of the mechanism this work predicts.
    41905405  the 2026 systematic review and meta-analysis of EON risk factors -
              establishes how saturated the clinical literature is.

Europe PMC is used because PubMed returns a bot block.
"""
from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

IDS = {
    "42240730": "Suresh 2026 - ocular toxicity of ethambutol, South-East Asia",
    "41563626": "Li 2026 - SDHB-mediated ferroptosis in retinal ganglion cells",
    "41905405": "2026 - risk factors for EON, systematic review and meta-analysis",
    "39195651": "2024 - risk factors of optic neuropathy in ethambutol users",
    "39474613": "Kim 2024 - nationwide usage and screening practices",
    "35301670": "2022 - proteomics-informed mechanism of ethambutol ocular toxicity",
    "41184893": "2025 - Müller glia protection of retinal ganglion cells",
}

for pmid, label in IDS.items():
    q = f"EXT_ID:{pmid}"
    params = urllib.parse.urlencode({"query": q, "format": "json", "pageSize": 1,
                                     "resultType": "core"})
    print("=" * 100)
    print(f"{label}")
    print("=" * 100)
    try:
        req = urllib.request.Request(f"{BASE}?{params}", headers=UA)
        with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
            j = json.loads(r.read())
        res = j.get("resultList", {}).get("result", [])
        if not res:
            print("  not found in Europe PMC")
            print()
            continue
        rec = res[0]
        print(f"  title  : {(rec.get('title') or '').strip()}")
        jt = ((rec.get("journalInfo") or {}).get("journal") or {}).get("title", "")
        print(f"  journal: {jt}  ({rec.get('pubYear')})")
        print(f"  authors: {(rec.get('authorString') or '')[:150]}")
        abstract = (rec.get("abstractText") or "").replace("<h4>", "\n  ")
        abstract = abstract.replace("</h4>", ": ").replace("<p>", " ").replace("</p>", " ")
        print("  abstract:")
        for chunk in [abstract[i:i + 104] for i in range(0, min(len(abstract), 2600), 104)]:
            print(f"    {chunk}")
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED {type(exc).__name__}: {str(exc)[:100]}")
    print()
