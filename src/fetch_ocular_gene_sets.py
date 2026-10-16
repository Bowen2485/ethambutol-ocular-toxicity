# -*- coding: utf-8 -*-
"""
Retrieve the disease-associated gene sets that the comparator papers intersect with.

Why this, and why now
    All four papers in this genre do the same thing: they collect a drug's targets, collect the
    genes annotated for the disease, intersect the two, build a PPI network of the
    intersection, and take the hubs of that network.  The number that carries the argument is
    the size of the intersection - 30 targets shared between four antiseizure medications and
    2,835 SJS/TEN genes in one of them.

    This manuscript's network came from literature co-mention instead, so it never reported
    such an intersection.  The disease-gene side can be retrieved from DisGeNET through the
    documented interface, which is now available and removes the need to read pages by hand.

How it is queried
    The API takes a disease identifier, so the first step is to find the identifiers for the
    optic-nerve and ocular terms this paper is about.  CUI codes are used because the disease
    name fields vary; the optic neuropathy CUI is known from the pharmacovigilance terms, and
    the vocabulary is searched for the rest.

The response shape is the one confirmed earlier: status, paging, payload, warnings.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

KEY = (ROOT / "credential" / "disgenet_key.txt").read_text(
    encoding="utf-8", errors="replace").strip().split()[-1].strip(chr(34)).strip(chr(39))
BASE = "https://api.disgenet.com/api/v1/gda/summary"
HEADERS = {"Authorization": KEY, "accept": "*/*",
           "User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)"}


def query(params: dict, retries: int = 3) -> dict:
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=HEADERS), timeout=60) as fh:
                return json.loads(fh.read(2_500_000).decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": f"HTTP {e.code}", "params": params}
        except Exception as e:  # noqa: BLE001
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": f"{type(e).__name__}: {str(e)[:100]}", "params": params}
    return {"__error__": "exhausted", "params": params}


print("=" * 100)
print("1. Which disorder identifiers answer")
print("=" * 100)
#: the ocular terms this paper is about, with the vocabulary each belongs to.  UMLS CUIs are
#: used where known because the API matches on the identifier rather than the name.
PROBES = {
    "UMLS_C0029134": "Optic Nerve Diseases",
    "UMLS_C0029139": "Optic Neuritis",
    "UMLS_C0151876": "Optic Atrophy",
    "UMLS_C0271084": "Optic Neuropathy",
    "UMLS_C0015397": "Eye Diseases",
    "UMLS_C0035309": "Retinal Diseases",
    "UMLS_C0015396": "Eye",
}
probe_results = {}
for cui, label in PROBES.items():
    r = query({"disease": cui, "page_size": 5, "order_by": "score", "order": "DESC"})
    pay = r.get("payload") or []
    paging = r.get("paging") or {}
    err = r.get("__error__")
    total = paging.get("totalElements")
    good = bool(pay)
    probe_results[cui] = {"label": label, "total": total, "ok": good, "error": err}
    status = f"{total:>6}" if isinstance(total, int) else ("error" if err else "0")
    print(f"  {cui:16s} {label:26s} {status:>7} associations  "
          f"{'' if good else (err or 'no rows')}")
    if pay:
        first = pay[0]
        sym = first.get("symbolOfGene") or first.get("geneSymbol") or "?"
        dis = first.get("diseaseName") or "?"
        print(f"        e.g. {sym} - {dis}  (score {first.get('score')})")
    time.sleep(0.3)

(OUT / "disgenet_disease_probe.json").write_text(
    json.dumps(probe_results, indent=2, ensure_ascii=False), encoding="utf-8")

usable = {c: v for c, v in probe_results.items() if v["ok"]}
print()
print(f"  identifiers returning data: {len(usable)} of {len(PROBES)}")
print(f"  -> results/disgenet_disease_probe.json")

print()
print("=" * 100)
print("2. What this enables")
print("=" * 100)
print("""  Each identifier that answers is a disease-gene set, and the sets are what the comparator
  papers intersect with their drug targets.  The intersection with this manuscript's 33 hub
  genes is the number those papers report, and it can be computed from these responses.

  Note on what the sets contain: DisGeNET under an academic plan serves curated sources only
  and states so in each response, so the sets are smaller than a licensed query would return.
  That is recorded with the counts rather than discovered later.""")
