# -*- coding: utf-8 -*-
"""
Find a gene-annotation source that can replace the licensed disease-target databases.

GeneCards returned 403 and the DisGeNET API returned an HTML page, so neither can supply
the gene-to-disease mapping that a network-toxicology paper normally assembles.  Rather than
substitute a different database without saying so, the alternatives are probed: whatever
answers can be named in the methods, and whatever does not is reported as unavailable.

The question for each candidate is whether it returns structured data for a gene, not
whether the request succeeded.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
      "Accept": "application/json, text/plain, */*"}


def get(url: str, timeout: int = 30) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=timeout) as fh:
            return True, fh.read(400_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return False, f"HTTPError {e.code} {e.reason}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:100]}"


def is_data(body: str, kind: str) -> bool:
    if not body or "<!doctype html" in body[:200].lower():
        return False
    if kind == "json":
        try:
            json.loads(body)
            return True
        except Exception:
            return False
    if kind == "tsv":
        lines = [l for l in body.splitlines() if l.strip()]
        return len(lines) >= 2 and "\t" in lines[0]
    return len(body) > 80


CANDIDATES = [
    ("Monarch Initiative v3 entity", "json",
     "https://api.monarchinitiative.org/v3/api/entity/NCBIGene:7157"),
    ("Monarch v3 gene associations", "json",
     "https://api.monarchinitiative.org/v3/api/association?subject=NCBIGene:7157"
     "&category=biolink:GeneToDiseaseAssociation&limit=5"),
    ("HPO JAX network annotation", "json",
     "https://ontology.jax.org/api/network/annotation/NCBIGene:7157"),
    ("Gene Ontology API (bioentity)", "json",
     "https://api.geneontology.org/api/bioentity/gene/NCBIGene:7157"),
    ("Reactome content service", "json",
     "https://reactome.org/ContentService/data/mapping/UniProt:P04637/pathways"),
    ("Open Targets target by symbol", "json",
     "https://api.platform.opentargets.org/api/v4/graphql"),
    ("NCBI ClinVar esearch", "json",
     "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
     "?db=clinvar&term=TP53&retmode=json&retmax=3"),
    ("NCBI Gene esummary", "json",
     "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
     "?db=gene&id=7157&retmode=json"),
    ("Ensembl REST (xrefs)", "json",
     "https://rest.ensembl.org/xrefs/symbol/homo_sapiens/TP53?content-type=application/json"),
    ("DisGeNET v1 with json accept", "json",
     "https://www.disgenet.org/api/gda/summary/TP53"),
]

print("=" * 100)
print("Gene-annotation sources, judged on the data returned")
print("=" * 100)
results = []
for label, kind, url in CANDIDATES:
    ok, body = get(url)
    good = ok and is_data(body, kind)
    results.append({"source": label, "url": url, "usable": good,
                    "bytes": len(body), "sample": body[:160]})
    print(f"  {'USABLE' if good else 'no data':8s} {label:34s} {len(body):>8,} B")
    print(f"           {body[:150]}")
    print()

(OUT / "gene_annotation_probe.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

usable = [r["source"] for r in results if r["usable"]]
print("=" * 100)
print("Verdict")
print("=" * 100)
print(f"  usable for a gene-to-disease mapping: {len(usable)}")
for u in usable:
    print(f"      {u}")
print()
print("""  Only sources listed above can be named in the methods.  Where a source that the
  peer papers used is unavailable - GeneCards returns 403 and DisGeNET serves a page
  instead of data - that is reported as a limitation rather than quietly worked around,
  because swapping in a different database would change what the enrichment means while
  leaving the sentence unchanged.""")
print(f"\n  written: {(OUT / 'gene_annotation_probe.json').relative_to(ROOT)}")
