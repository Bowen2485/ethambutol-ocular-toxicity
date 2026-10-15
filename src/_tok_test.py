# -*- coding: utf-8 -*-
"""Focused, time-boxed OpenGWAS token test."""
from __future__ import annotations

import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request

TOKEN = (sys.argv[1] if len(sys.argv) > 1
         else open("data/raw/opengwas/token.txt", encoding="utf-8").read().strip())
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def call(url, headers, data=None, timeout=45):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            body = r.read().decode("utf-8", "replace")
        return f"[{r.status}] {time.time()-t0:5.1f}s {body[:300]}"
    except urllib.error.HTTPError as e:
        try:
            b = e.read().decode()[:300]
        except Exception:  # noqa: BLE001
            b = ""
        return f"[HTTP{e.code}] {time.time()-t0:5.1f}s {b}"
    except socket.timeout:
        return f"[TIMEOUT] {time.time()-t0:5.1f}s"
    except Exception as e:  # noqa: BLE001
        return f"[{type(e).__name__}] {time.time()-t0:5.1f}s {str(e)[:140]}"


print("token length:", len(TOKEN))
print("token head  :", TOKEN[:40])
print()

tests = [
    ("no auth, public gwasinfo",
     "https://api.opengwas.io/api/gwasinfo/ieu-a-2",
     {"User-Agent": "Mozilla/5.0"}),
    ("bearer auth, public gwasinfo",
     "https://api.opengwas.io/api/gwasinfo/ieu-a-2",
     {"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {TOKEN}"}),
    ("bearer auth, /user",
     "https://api.opengwas.io/api/user",
     {"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {TOKEN}"}),
    ("bearer auth, gwasinfo list",
     "https://api.opengwas.io/api/gwasinfo?limit=3",
     {"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {TOKEN}"}),
    ("legacy host with bearer",
     "https://gwas-api.mrcieu.ac.uk/gwasinfo/ieu-a-2",
     {"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {TOKEN}"}),
]
for name, url, hdr in tests:
    print(f"{name:34s} {call(url, hdr)}")

print()
print("POST tophits (bearer):")
body = json.dumps({"id": ["ieu-a-2"], "pval": 5e-8, "preclump": True,
                   "clump": True, "r2": 0.001, "kb": 10000}).encode()
print("  ", call("https://api.opengwas.io/api/tophits",
                  {"User-Agent": "Mozilla/5.0",
                   "Authorization": f"Bearer {TOKEN}",
                   "Content-Type": "application/json"}, data=body, timeout=90)[:400])
