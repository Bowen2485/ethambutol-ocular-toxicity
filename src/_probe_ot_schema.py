# -*- coding: utf-8 -*-
"""Introspect the Open Targets GraphQL schema and dump the ethambutol drug record."""
from __future__ import annotations

import json
import ssl
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
OT = "https://api.platform.opentargets.org/api/v4/graphql"


def q(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    req = urllib.request.Request(
        OT, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


for type_name in ["Drug", "Disease", "Target", "AssociatedTargets", "AssociatedTargetsRow",
                  "MechanismsOfAction", "MechanismOfActionRow", "DrugTargetRow"]:
    try:
        r = q('{ __type(name:"%s"){ kind fields { name type { name kind ofType { name } } } } }'
              % type_name)
        t = r.get("data", {}).get("__type")
        if not t:
            print(f"{type_name}: NOT FOUND")
            continue
        names = [f["name"] for f in t["fields"]]
        print(f"{type_name} ({t['kind']}): {names}")
    except Exception as e:  # noqa: BLE001
        print(f"{type_name}: FAIL {type(e).__name__} {str(e)[:120]}")
    print()

print("=" * 70)
r = q('{ search(queryString:"ethambutol", entityNames:["drug"]) { hits { id name } } }')
print("search:", json.dumps(r)[:300])
cid = r["data"]["search"]["hits"][0]["id"]

probe = """
query($id:String!) {
  drug(chemblId:$id) {
    id name drugType isApproved yearOfFirstApproval
    mechanismsOfAction {
      uniqueActionTypes uniqueTargetTypes
      rows { actionType mechanismOfAction targetName
             targets { id approvedSymbol approvedName } }
    }
    linkedTargets { count rows { id approvedSymbol approvedName } }
  }
}"""
try:
    r = q(probe, {"id": cid})
    print("PROBE OK")
    print(json.dumps(r, indent=1, ensure_ascii=False)[:4000])
except urllib.error.HTTPError as e:
    print("PROBE HTTP", e.code, e.read().decode()[:1500])
