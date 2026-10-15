# -*- coding: utf-8 -*-
"""Introspect the RCSB GraphQL schema for gene-name metadata."""
import json
import ssl
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}


def gq(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    req = urllib.request.Request("https://data.rcsb.org/graphql",
                                data=json.dumps(body).encode(), headers=UA)
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        return json.loads(r.read().decode())


for t in ["RcsbEntitySourceOrganism", "PolymerEntity", "RcsbPolymerEntity",
          "RcsbPolymerEntityAlign", "RcsbEntityPolymerEntityInstance"]:
    try:
        r = gq('{ __type(name: "%s") { fields { name } } }' % t)
        tt = r.get("data", {}).get("__type")
        print(f"{t}: {[f['name'] for f in tt['fields']] if tt else 'NOT FOUND'}")
    except Exception as e:  # noqa: BLE001
        print(f"{t}: FAIL {type(e).__name__} {str(e)[:120]}")
    print()

# pragmatic: which fields on PolymerEntity mention gene?
r = gq('{ __type(name: "PolymerEntity") { fields { name } } }')
names = [f["name"] for f in r["data"]["__type"]["fields"]]
for n in names:
    if any(k in n.lower() for k in ("source", "ident", "align", "entity", "name")):
        print("candidate field:", n)
