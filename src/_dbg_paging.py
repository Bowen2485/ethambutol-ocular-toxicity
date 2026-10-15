# -*- coding: utf-8 -*-
"""Diagnose the stalled openFDA pagination: how long does one page take?"""
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

TERM = "ETHAMBUTOL"


def timed(qs: str, timeout: int):
    url = f"{API}?{qs}"
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            body = r.read()
        dt = time.time() - t0
        d = json.loads(body.decode("utf-8", "replace"))
        n = len(d.get("results", []))
        tot = d.get("meta", {}).get("results", {}).get("total")
        print(f"[OK {dt:6.1f}s] {qs[:70]:72s} bytes={len(body):>9,} rows={n} total={tot}")
        return dt
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL {time.time()-t0:6.1f}s] {qs[:70]:72s} {type(e).__name__} {str(e)[:80]}")
        return None


S = urllib.parse.quote(f'patient.drug.medicinalproduct:"{TERM}"')
print("--- single page, generous timeout ---")
timed(f"search={S}&limit=100&skip=0", 180)
timed(f"search={S}&limit=100&skip=100", 180)
print("--- smaller page size (is 100 the problem?) ---")
timed(f"search={S}&limit=50&skip=0", 180)
timed(f"search={S}&limit=10&skip=0", 180)
print("--- with explicit sort, no skip ---")
timed(f"search={S}&limit=100", 180)
print("--- total only ---")
timed(f"search={S}&limit=1", 180)
