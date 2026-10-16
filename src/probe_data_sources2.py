# -*- coding: utf-8 -*-
"""
Probe the data sources properly, judging them on the data returned rather than the status.

The first probe was misleading in both directions.  Open Targets returned 400 because a
GraphQL endpoint was queried with GET instead of a POST carrying a query, which is a fault
of the probe.  DisGeNET returned 200 but the payload was an HTML document, which is a fault
of the source as an API.  A status code alone therefore says nothing, so each candidate is
now asked for something specific and the reply is inspected.

The question being answered is narrow: can this source supply a gene-to-disease or
gene-to-expression mapping for the manuscript's hub genes, using a documented interface
without a licence key?  Anything else is out of scope.
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

UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
      "Accept": "application/json, text/plain, */*"}


def post_json(url: str, payload: dict, timeout: int = 40) -> tuple[bool, str, int]:
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data, headers={**UA, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            body = fh.read(500_000).decode("utf-8", "replace")
        return True, body, len(body)
    except urllib.error.HTTPError as e:
        return False, f"HTTPError {e.code} {e.reason}", 0
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:110]}", 0


def get(url: str, timeout: int = 40, accept: str = "") -> tuple[bool, str, int]:
    h = dict(UA)
    if accept:
        h["Accept"] = accept
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h),
                                    timeout=timeout) as fh:
            body = fh.read(500_000).decode("utf-8", "replace")
            ctype = fh.headers.get("Content-Type", "")
        return True, body, len(body)
    except urllib.error.HTTPError as e:
        return False, f"HTTPError {e.code} {e.reason}", 0
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:110]}", 0


def looks_like_data(body: str, expect) -> bool:
    if not body:
        return False
    if "<!doctype html" in body[:200].lower() or "<html" in body[:200].lower():
        return False
    if expect == "json":
        try:
            json.loads(body)
            return True
        except Exception:
            return False
    if expect == "tsv":
        lines = [l for l in body.splitlines() if l.strip()]
        return len(lines) >= 2 and "\t" in lines[0]
    return len(body) > 50


print("=" * 104)
print("1. Open Targets GraphQL, asked properly with a POST")
print("=" * 104)
OT = "https://api.platform.opentargets.org/api/v4/graphql"
q = {"query": '{ target(ensemblId: "ENSG00000134184") { approvedSymbol '
              'associatedDiseases(page: {index: 0, size: 3}) { rows { disease { name } '
              'score } } } }'}
ok, body, size = post_json(OT, q)
good = ok and looks_like_data(body, "json")
print(f"  status: {'data' if good else 'no data'}   {size:,} bytes")
print(f"  {body[:400]}")
print(f"  -> usable: {good}")

print()
print("=" * 104)
print("2. STRING, with the caller identity it requires")
print("=" * 104)
s_url = ("https://string-db.org/api/json/interactionPartners"
         "?identifiers=TP53%0dNFE2L2&species=9606&limit=3"
         "&caller_identity=ethambutol_manuscript")
ok, body, size = get(s_url)
good = ok and looks_like_data(body, "json")
print(f"  status: {'data' if good else 'no data'}   {size:,} bytes")
print(f"  {body[:300]}")
print(f"  -> usable: {good}")

print()
print("=" * 104)
print("3. CTD, following where it redirects")
print("=" * 104)
c_url = ("https://ctdbase.org/tools/batchQuery.go?inputType=gene&inputTerms=TP53"
         "&report=diseases_curated&format=tsv")
ok, body, size = get(c_url)
good = ok and looks_like_data(body, "tsv")
print(f"  status: {'data' if good else 'no data'}   {size:,} bytes")
print(f"  {body[:300]}")
print(f"  -> usable: {good}")

print()
print("=" * 104)
print("4. DisGeNET, checking whether the payload is data or a page")
print("=" * 104)
ok, body, size = get("https://www.disgenet.org/api/gda/summary/TP53",
                     accept="application/json")
good = ok and looks_like_data(body, "json")
print(f"  status: {'data' if good else 'no data'}   {size:,} bytes")
print(f"  first 200 characters: {body[:200]!r}")
print(f"  -> usable: {good}")

print()
print("=" * 104)
print("5. NCBI GEO through eutils, which answered before")
print("=" * 104)
e_url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
         "db=gds&term=%28retina%5BAll+Fields%5D+OR+optic+nerve%5BAll+Fields%5D%29"
         "+AND+%22Homo+sapiens%22%5BOrganism%5D+AND+gse%5BEntry+Type%5D"
         "&retmax=10&retmode=json")
ok, body, size = get(e_url)
good = ok and looks_like_data(body, "json")
print(f"  status: {'data' if good else 'no data'}   {size:,} bytes")
print(f"  {body[:400]}")
print(f"  -> usable: {good}")

print()
print("=" * 104)
print("Verdict")
print("=" * 104)
verdict = {
    "open_targets_graphql": good if False else None,
}
for label, (ok_, body_, size_) in {
    "open_targets": (ok, "", 0),  # recomputed below
}.items():
    pass
print("""  Sources confirmed usable are used as they are.  A source that cannot be reached
  without a licence key is reported as unavailable and is not replaced by a different
  database, because substituting one silently would change what the analysis means.""")
