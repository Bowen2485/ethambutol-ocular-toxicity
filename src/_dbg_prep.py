# -*- coding: utf-8 -*-
"""Pin down the exact failures in the PubChem and RCSB calls."""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}


def get(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.status, r.read()


print("### PubChem property variants")
for props in ["CanonicalSMILES,IsomericSMILES,MolecularFormula,MolecularWeight,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,RotatableBondCount",
              "CanonicalSMILES,MolecularFormula,MolecularWeight,XLogP,TPSA",
              "CanonicalSMILES,MolecularWeight"]:
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/ethambutol/property/{props}/JSON"
    try:
        st, body = get(url)
        print(f"[{st}] n_props={len(props.split(','))} -> {body[:150]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] n_props={len(props.split(','))} -> {e.read()[:200]}")
    except Exception as e:
        print(f"[FAIL] {type(e).__name__} {str(e)[:90]}")
    time.sleep(0.4)

print("\n### PubChem 3D SDF")
for rec in ["3d", "2d"]:
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/ethambutol/SDF?record_type={rec}"
    try:
        st, body = get(url)
        txt = body.decode("latin-1", "replace")
        print(f"[{st}] {rec}: {len(body)} bytes, has_V2000={'V2000' in txt}, "
              f"3d_coords={'3D' in txt[:200]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {rec} -> {e.read()[:150]}")
    time.sleep(0.4)

print("\n### RCSB search variants")
q1 = {"query": {"type": "terminal", "service": "text",
                "parameters": {"attribute": "rcsb_gene_name.value",
                               "operator": "exact_match", "value": "AKT1"}},
      "return_type": "entry",
      "request_options": {"paginate": {"start": 0, "rows": 5},
                          "results_verbosity": "compact"}}
for label, q, method in [
    ("GET compact", q1, "GET"),
]:
    url = "https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(q))
    try:
        st, body = get(url)
        d = json.loads(body)
        print(f"[{st}] {label}: {len(d.get('result_set', []))} hits "
              f"{[r['identifier'] for r in d.get('result_set', [])]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {label} -> {e.read()[:300]}")
    except Exception as e:
        print(f"[FAIL] {label}: {type(e).__name__} {str(e)[:90]}")
    time.sleep(0.4)

q2 = {"query": {"type": "terminal", "service": "full_text", "parameters": {"value": "AKT1"}},
      "return_type": "entry", "request_options": {"paginate": {"start": 0, "rows": 5}}}
try:
    req = urllib.request.Request(
        "https://search.rcsb.org/rcsbsearch/v2/query",
        data=json.dumps(q2).encode(),
        headers={**UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        d = json.loads(r.read().decode())
    print("[OK] POST full_text:", len(d.get("result_set", [])), "hits",
          [x["identifier"] for x in d.get("result_set", [])])
except urllib.error.HTTPError as e:
    print(f"[HTTP{e.code}] POST -> {e.read()[:300]}")
except Exception as e:
    print(f"[FAIL] POST: {type(e).__name__} {str(e)[:90]}")

print("\n### RCSB GraphQL data API (alternative)")
gq = {"query": '{ entry(entry_id:"1UNQ") { rcsb_id struct { title } rcsb_entry_info { resolution_combined experimental_method } } }'}
try:
    req = urllib.request.Request("https://data.rcsb.org/graphql",
                                 data=json.dumps(gq).encode(),
                                 headers={**UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        print("[OK] graphql:", r.read().decode()[:400])
except Exception as e:
    print(f"[FAIL] graphql: {type(e).__name__} {str(e)[:120]}")
