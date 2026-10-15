# -*- coding: utf-8 -*-
"""Debug the openFDA 403 on the whole-database count query."""
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FAERS-research/1.0"}
API = "https://api.fda.gov/drug/event.json"

CANDIDATES = [
    ('search=_exists_:receivedate&count=patient.reaction.reactionmeddrapt.exact&limit=1000', None),
    ('search=receivedate:[19000101+TO+29991231]&count=patient.reaction.reactionmeddrapt.exact&limit=1000', None),
    ('search=receivedate:[19000101+TO+29991231]&count=patient.reaction.reactionmeddrapt.exact&limit=100', None),
    ('search=patient.reaction.reactionmeddrapt:*&count=patient.reaction.reactionmeddrapt.exact&limit=1000', None),
    ('search=patient.drug.medicinalproduct:"ETHAMBUTOL"&count=patient.reaction.reactionmeddrapt.exact&limit=1000', None),
    ('search=receivedate:[19000101+TO+29991231]&count=receivedate&limit=1', None),
    ('search=receivedate:[19000101+TO+29991231]&count=patient.reaction.reactionmeddrapt.exact&limit=1000',
     {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}),
]


def try_url(qs, hdr):
    url = f"{API}?{qs}"
    h = dict(UA)
    if hdr:
        h.update(hdr)
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            body = r.read()
        d = json.loads(body.decode("utf-8", "replace"))
        n = len(d.get("results", []))
        print(f"[OK  ] {qs[:88]:90s} -> {len(body):>9,} bytes, {n} rows")
        if n:
            print("        first:", d["results"][0], " total_reports:", d.get("meta", {}).get("results", {}).get("total"))
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {qs[:88]:90s} -> {e.read()[:180]!r}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {qs[:88]:90s} -> {type(e).__name__} {str(e)[:90]}")
    time.sleep(0.6)


for qs, hdr in CANDIDATES:
    try_url(qs, hdr)
