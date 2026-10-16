# -*- coding: utf-8 -*-
"""
Probe which disease-target and transcriptomic sources are actually reachable.

Before promising an enrichment against GeneCards or DisGeNET it is worth checking that the
endpoint answers, because both have restricted access at various points: DisGeNET moved its
API behind a registration, and GeneCards licenses its data and rate-limits automated
queries.  Recommending an analysis that cannot be run would waste the effort twice.

The probe reports, for each candidate source, whether it answered, how quickly, and what it
returned, so the choice of sources is made on evidence.

A note on trust: responses are external content and are inspected as data, never executed.
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

UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)"}


def probe(label: str, url: str, timeout: int = 30) -> dict:
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            body = fh.read(400_000)
            code = fh.status
        txt = body.decode("utf-8", "replace")
        return {"label": label, "url": url, "status": code,
                "seconds": round(time.time() - t0, 2),
                "bytes": len(body), "ok": True,
                "sample": txt[:200].replace("\n", " ")}
    except urllib.error.HTTPError as e:
        return {"label": label, "url": url, "status": e.code,
                "seconds": round(time.time() - t0, 2), "bytes": 0, "ok": False,
                "sample": f"HTTPError {e.code} {e.reason}"}
    except Exception as e:  # noqa: BLE001
        return {"label": label, "url": url, "status": None,
                "seconds": round(time.time() - t0, 2), "bytes": 0, "ok": False,
                "sample": f"{type(e).__name__}: {str(e)[:120]}"}


PROBES = [
    ("Open Targets GraphQL (known working)",
     "https://api.platform.opentargets.org/api/v4/graphql"),
    ("CTD disease-gene associations (batch query)",
     "https://ctdbase.org/tools/batchQuery.go?inputType=gene&inputTerms=CASP3"
     "&report=curated&format=tsv"),
    ("DisGeNET public API v1",
     "https://www.disgenet.org/api/gda/summary/CASP3"),
    ("GeneCards search page",
     "https://www.genecards.org/cgi-bin/carddisp.pl?gene=CASP3"),
    ("NCBI eutils esearch (GEO)",
     "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
     "db=gds&term=retina+AND+human%5Borgn%5D&retmax=5&retmode=json"),
    ("Europe PMC search",
     "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
     "query=retina%20AND%20expression&format=json&pageSize=2"),
    ("MONARCH / HPO gene-disease",
     "https://api.monarchinitiative.org/api/bioentity/gene/NCBIGene:1432/diseases"),
    ("STRING API",
     "https://string-db.org/api/tsv/interactionPartners?identifiers=TP53&limit=5"),
]

print("=" * 100)
print("Reachability of the candidate data sources")
print("=" * 100)
results = []
for label, url in PROBES:
    r = probe(label, url)
    results.append(r)
    mark = "OK  " if r["ok"] else "FAIL"
    print(f"  {mark} {label:44s} {r['seconds']:>6.2f}s  "
          f"{r['status'] if r['status'] else '-':>5}  {r['bytes']:>8,} B")
    print(f"       {r['sample'][:140]}")
    print()

(OUT / "data_source_probe.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

print("=" * 100)
print("Reading")
print("=" * 100)
ok = [r["label"] for r in results if r["ok"]]
bad = [r["label"] for r in results if not r["ok"]]
print(f"  reachable : {len(ok)}")
for x in ok:
    print(f"      {x}")
print(f"  not reachable: {len(bad)}")
for x in bad:
    print(f"      {x}")
print()
print("""  Sources that answered can be used directly.  Any that did not is reported as
  unavailable rather than worked around, because substituting a different database silently
  would change what the enrichment means.""")
print(f"\n  written: {(OUT / 'data_source_probe.json').relative_to(ROOT)}")
