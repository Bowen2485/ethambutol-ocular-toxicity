# -*- coding: utf-8 -*-
"""Probe HERB (herb.ac.cn) and related TCM target databases for a usable API."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0",
      "Accept": "application/json, text/html, */*"}


def get(url, timeout=45, hdr=None):
    h = dict(UA)
    if hdr:
        h.update(hdr)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def probe(name, url, hdr=None, maxlen=260):
    try:
        st, ct, body = get(url, hdr=hdr)
        txt = body.decode("utf-8", "replace")
        looks_json = txt.lstrip().startswith(("{", "["))
        print(f"[{st}] {name:38s} ct={ct[:34]:36s} len={len(body):>7} "
              f"{'JSON' if looks_json else 'HTML/other'} :: {txt[:maxlen]!r}")
        return txt
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {name:38s} {e.read()[:150]!r}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name:38s} {type(e).__name__} {str(e)[:90]}")
    return None


CANDS = [
    ("herb_root", "http://herb.ac.cn/"),
    ("herb_api", "http://herb.ac.cn/api/"),
    ("herb_herb_list", "http://herb.ac.cn/api/herb/list"),
    ("herb_target_list", "http://herb.ac.cn/api/target/list"),
    ("herb_search", "http://herb.ac.cn/api/search?keyword=Gouqizi"),
    ("herb_v1_search", "http://herb.ac.cn/api/v1/search?q=Gouqizi"),
    ("herb_detail", "http://herb.ac.cn/HerbDetail?id=1"),
    ("herb_json_root", "http://herb.ac.cn/static/data/herb.json"),
    ("batman_home", "http://bionet.ncpsb.org.cn/batman-tcm/"),
    ("batman_api", "http://bionet.ncpsb.org.cn/batman-tcm/api/"),
    ("symmap_home", "http://www.symmap.org/"),
    ("symmap_api", "http://www.symmap.org/api/"),
    ("etcm2_home", "http://www.tcmip.cn/ETCM2/"),
    ("tcmbank_home", "https://www.bidd.group/TCMBank/"),
    ("tcmsp_home", "https://old.tcmsp-e.com/tcmsp.php"),
    ("tcmsp_json", "https://old.tcmsp-e.com/tcmspsearch.php?qr=Gouqizi&qsr=herb_all_name"),
    ("ctdbase_chem", "https://ctdbase.org/tools/batchQuery.go?inputType=chem&inputTerms=MESH:D004475&report=genes&format=tsv"),
    ("stitch_unavailable", "http://stitch.embl.de/api/tsv/interactors?identifiers=quercetin&species=9606"),
    ("swisstarget_home", "http://www.swisstargetprediction.ch/"),
    ("pubchem_herb", "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/quercetin/synonyms/JSON"),
    ("tcmid", "http://www.megabionet.org/tcmid/"),
    ("hitat", "http://www.bioinformatics.org/hitat/"),
    ("tcmio", "http://tcmio.xielab.net/"),
]

for name, url in CANDS:
    probe(name, url)

print("\n--- try HERB postgREST-style endpoints ---")
for suffix in ["/api/v1/herb", "/api/v1/target", "/api/v1/component",
               "/api/herb?page=1", "/api/v1/herb/1", "/api/v1/component/1"]:
    probe("herb" + suffix, "http://herb.ac.cn" + suffix)
