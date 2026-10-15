# -*- coding: utf-8 -*-
"""
Establish what has already been published on this topic, with a systematic search.

The question the authors asked - has this been done - has to be answered from the
literature rather than from impression, because it decides what the paper can claim as
its contribution and which competing work the Discussion must address. Two studies are
already known to overlap:

    Mao & Ou 2026, Asia-Pacific Medical Frontiers
        FAERS signal mining of the four first-line antitubercular drugs, 2021Q1-2025Q3,
        using ROR, PRR, MHRA, BCPNN and MGPS.  Ethambutol gave the most eye-disorder
        signals of the four drugs (9 signals, 11.04% of its reports).  Overlap: same
        database, same drug, same organ class, same conclusion at that level.

    Suresh 2026, Int Ophthalmol
        VigiBase analysis of ethambutol ocular toxicity in South-East Asia.

    Kim 2024, Front Pharmacol
        Nationwide ethambutol usage with optic neuropathy incidence and screening.

And one experimental paper bears directly on the mechanism claimed here:
    ethambutol inducing ferroptosis in retinal ganglion cells via Smad4/SDHB.

This queries Europe PMC across several angles and reports every hit with its identifiers,
so overlap can be judged from titles and abstracts rather than assumed. It is a
screening exercise, not a systematic review: the aim is to find anything that would
pre-empt the manuscript's claims.
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

QUERIES = {
    "FAERS + ethambutol":
        '(ethambutol) AND (FAERS OR "adverse event reporting system" OR '
        '"spontaneous reporting")',
    "disproportionality + ethambutol":
        '(ethambutol) AND (disproportionality OR "reporting odds ratio" OR ROR OR '
        'pharmacovigilance)',
    "ethambutol ocular signal":
        '(ethambutol) AND (ocular OR ophthalmic OR eye) AND (signal OR '
        '"data mining")',
    "ethambutol optic neuropathy epidemiology":
        '(ethambutol) AND ("optic neuropathy" OR "optic neuritis") AND '
        '(incidence OR risk factor OR cohort)',
    "ethambutol mechanism network":
        '(ethambutol) AND (ferroptosis OR "network toxicology" OR "network '
        'pharmacology" OR "molecular docking")',
    "ethambutol retinal ganglion ferroptosis":
        '(ethambutol) AND ("retinal ganglion" OR retina) AND (ferroptosis OR '
        'mitochondrial)',
    "ethambutol mendelian randomisation":
        '(ethambutol) AND ("mendelian randomization" OR "mendelian randomisation")',
    "ethambutol molecular dynamics":
        '(ethambutol) AND ("molecular dynamics" OR "all-atom")',
}

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "literature_overlap_check.json"


def search(query: str, page_size: int = 60) -> tuple[int, list]:
    params = urllib.parse.urlencode({
        "query": query, "format": "json", "pageSize": page_size,
        "resultType": "core", "sort": "CITED desc",
    })
    url = f"{BASE}?{params}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        j = json.loads(r.read())
    return j.get("hitCount", 0), j.get("resultList", {}).get("result", [])


all_hits = {}
print("=" * 104)
for label, q in QUERIES.items():
    try:
        n, res = search(q)
    except Exception as exc:  # noqa: BLE001
        print(f"\n{label}: FAILED {type(exc).__name__}: {str(exc)[:80]}")
        continue
    all_hits[label] = res
    print(f"\n{label}   ({n:,} hits, showing top {len(res)})")
    print("-" * 104)
    for r in res[:12]:
        year = r.get("pubYear", "?")
        journal = (r.get("journalInfo", {}) or {}).get("journal", {}).get(
            "title", "") or r.get("bookOrReportDetails", {}).get("publisher", "")
        title = (r.get("title") or "").rstrip(".")
        pmid = r.get("pmid", "")
        doi = r.get("doi", "")
        ids = " ".join(x for x in (f"PMID:{pmid}" if pmid else "",
                                   f"doi:{doi}" if doi else "") if x)
        print(f"  {year}  {title[:96]}")
        if journal:
            print(f"        {journal[:78]}")
        if ids:
            print(f"        {ids}")
    time.sleep(0.6)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(all_hits, indent=1)[:3_000_000], encoding="utf-8")
print()
print("=" * 104)
print(f"raw results written to {OUT}")
print("=" * 104)

# the decisive question: has anyone combined the same four angles?
print()
print("Papers appearing under more than one angle (candidate overlaps):")
seen: dict[str, set] = {}
for label, res in all_hits.items():
    for r in res:
        key = r.get("pmid") or r.get("doi") or (r.get("title") or "")[:60]
        if key:
            seen.setdefault(key, set()).add(label)
multi = {k: v for k, v in seen.items() if len(v) > 1}
for k, v in sorted(multi.items(), key=lambda x: -len(x[1]))[:20]:
    title = next((r.get("title") for res in all_hits.values() for r in res
                  if (r.get("pmid") or r.get("doi") or (r.get("title") or "")[:60]) == k),
                 "")
    print(f"  [{len(v)}] {k}")
    print(f"      {(title or '')[:100]}")
    print(f"      angles: {sorted(v)}")
