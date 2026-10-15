# -*- coding: utf-8 -*-
"""Verify ligand PDBQT content and debug the RCSB metadata join."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

print("### ethambutol PDBQT content")
p = ROOT / "docking" / "ligands" / "ethambutol.pdbqt"
if p.exists():
    txt = p.read_text(errors="replace")
    print(f"file: {p.name}  bytes={p.stat().st_size}  lines={len(txt.splitlines())}")
    print("--- first 40 lines ---")
    print("\n".join(txt.splitlines()[:40]))
    print("--- counts ---")
    for k in ("ATOM", "HETATM", "BRANCH", "TORSDOF", "ROOT", "ENDROOT"):
        print(f"  {k}: {sum(1 for ln in txt.splitlines() if ln.startswith(k))}")
else:
    print("ethambutol.pdbqt missing")

print("\n### RCSB search + graphql join")
q = {"query": {"type": "terminal", "service": "full_text",
               "parameters": {"value": "AKT1"}},
     "return_type": "entry",
     "request_options": {"paginate": {"start": 0, "rows": 20}}}
url = "https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(q))
req = urllib.request.Request(url, headers=UA)
with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
    d = json.loads(r.read().decode())
ids = [x["identifier"] for x in d.get("result_set", [])]
print("search hits:", ids)

gq = """
query($ids:[String!]!) {
  entries(entry_ids:$ids) {
    rcsb_id
    struct { title }
    rcsb_entry_info { resolution_combined experimental_method nonpolymer_bound_components }
    polymer_entities {
      rcsb_polymer_entity { pdbx_description }
      rcsb_entity_source_organism { ncbi_gene_name scientific_name }
    }
  }
}"""
body = json.dumps({"query": gq, "variables": {"ids": ids[:5]}}).encode()
req = urllib.request.Request("https://data.rcsb.org/graphql", data=body,
                             headers={**UA, "Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
        payload = json.loads(r.read().decode())
    print(json.dumps(payload, indent=1)[:3000])
except urllib.error.HTTPError as e:
    print("graphql HTTP", e.code, e.read()[:600])
