# -*- coding: utf-8 -*-
"""Probe Europe PMC REST API connectivity and result counts."""
import json
import ssl
import urllib.parse
import urllib.request

CTX = ssl._create_unverified_context()
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def epmc(query, page_size=25, sort="CITED desc", result_type="core"):
    params = {
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": result_type,
    }
    if sort:
        params["sort"] = sort
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60, context=CTX) as resp:
        return json.loads(resp.read().decode("utf-8"))


PROBES = [
    'ethambutol AND "optic neuropathy"',
    'ethambutol AND (visual evoked potential OR optical coherence tomography OR retinal nerve fibre layer)',
    'ethambutol AND (pharmacovigilance OR FAERS OR disproportionality OR spontaneous reporting)',
    'ethambutol AND (mitochondrial OR oxidative stress OR zinc OR copper OR lysosome OR autophagy)',
    'ethambutol AND (dose OR risk factor OR incidence OR screening)',
    '(isoniazid OR rifampicin OR pyrazinamide) AND (optic neuropathy OR ocular toxicity)',
]

if __name__ == "__main__":
    for q in PROBES:
        try:
            d = epmc(q, page_size=1)
            print(f"{d.get('hitCount')}\t{q}")
        except Exception as e:
            print(f"ERROR\t{q}\t{e!r}")
