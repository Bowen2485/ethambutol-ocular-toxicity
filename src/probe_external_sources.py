# -*- coding: utf-8 -*-
"""
Determine which external pharmacovigilance sources are actually reachable from here.

The paper's single-source weakness can only be answered with a second database, and the
manuscript currently states that external replication "has not been performed".  Before
promising anything, the sources have to be checked rather than assumed - each has a
different access model, and several require registration that cannot be completed from
this environment.

Sources and their access conditions, as understood before testing:
    JADER (Japan, PMDA)          free download of quarterly CSVs, no registration
    FAERS itself                 already held locally, so it is not external
    EudraVigilance (EU)          requires an EMA account and a data-use agreement
    VigiBase (WHO/UMC)           requires UMC membership; not obtainable here
    VigiAccess (WHO/UMC)         public but aggregated to counts only, no case detail
    Canada CVARD / Australia DAEN  web query forms, no bulk API
    Korea KAERS                  Korean-language portal, no bulk API

This script tests reachability and, where a listing is exposed, reports what files are
available and how large they are.  Nothing is downloaded.
"""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research; contact via institution)"}

TARGETS = [
    ("JADER index (PMDA)",
     "https://www.pmda.go.jp/english/reports-services/psr-hp/0011.html"),
    ("JADER files listing",
     "https://www.pmda.go.jp/safety/info-services/drugs/adr-info/suspected-adr/0003.html"),
    ("EudraVigilance data access",
     "https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/"
     "pharmacovigilance-post-authorisation/eudravigilance-medicines"),
    ("VigiAccess",
     "https://www.vigiaccess.org/"),
    ("WHO UMC (VigiBase)",
     "https://www.who-umc.org/"),
    ("Canada CVARD",
     "https://www.canada.ca/en/health-canada/services/drugs-health-products/"
     "medeffect-canada/adverse-reaction-database.html"),
    ("Australia DAEN",
     "https://www.tga.gov.au/resources/database/daen"),
    ("openFDA API",
     "https://api.fda.gov/drug/event.json?limit=1"),
]


def probe(label: str, url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    out = {"label": label, "url": url}
    try:
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            body = r.read(400_000)
            out["status"] = r.status
            out["length"] = len(body)
            out["ctype"] = r.headers.get("Content-Type", "")
            # count links that look like downloadable data
            text = body.decode("utf-8", "replace")
            low = text.lower()
            for ext in (".zip", ".csv", ".txt", ".xlsx", ".gz"):
                out[f"links_{ext}"] = low.count(ext)
    except urllib.error.HTTPError as exc:
        out["status"] = f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        out["status"] = f"{type(exc).__name__}"
    return out


print("=" * 92)
print("Reachability of external pharmacovigilance sources")
print("=" * 92)
results = []
for label, url in TARGETS:
    r = probe(label, url)
    results.append(r)
    dl = " ".join(f"{k.split('_')[1]}={v}" for k, v in r.items()
                  if k.startswith("links_") and v)
    print(f"  {label:28s} {str(r.get('status')):>12s}  "
          f"{(str(r.get('length', '')) + ' bytes') if r.get('length') else '':>14s}  {dl}")

print()
print("=" * 92)
print("openFDA: does it give case-level detail that could serve as a second source?")
print("=" * 92)
try:
    req = urllib.request.Request(
        "https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:"
        "%22ETHAMBUTOL%22&limit=1", headers=UA)
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        j = json.loads(r.read())
    meta = j.get("meta", {}).get("results", {})
    print(f"  total reports matching ethambutol: {meta.get('total', '?')}")
    res = j.get("results", [])
    if res:
        rec = res[0]
        keys = sorted(rec.keys())
        print(f"  top-level fields: {keys}")
        di = rec.get("drug", [{}])
        print(f"  drug entry fields: {sorted(di[0].keys()) if di else '-'}")
        rx = rec.get("reaction", [])
        print(f"  reactions in this report: {len(rx)}")
        pt = rec.get("patient", {}).get("reaction", [])
        print(f"  patient.reaction entries: {len(pt)}")
        if pt:
            print(f"    first: {pt[0]}")
except Exception as exc:  # noqa: BLE001
    print(f"  openFDA query failed: {type(exc).__name__}: {str(exc)[:120]}")

print()
print("=" * 92)
print("Assessment")
print("=" * 92)
reachable = [r for r in results if isinstance(r.get("status"), int)]
print(f"  sources that responded: {len(reachable)} of {len(TARGETS)}")
for r in reachable:
    print(f"      {r['label']}")
print()
print("""  Responding to a web page is not the same as offering downloadable case-level data.
  The decisive question for replication is whether a source exposes individual reports
  with a drug field and a reaction field, because the whole analysis is a 2x2 count of
  exposed/unexposed by event/no-event.  Aggregated counts, as in VigiAccess, cannot
  support that.""")
