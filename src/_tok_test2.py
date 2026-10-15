# -*- coding: utf-8 -*-
"""Low-level OpenGWAS HTTP test with explicit Connection: close and hard limits."""
from __future__ import annotations

import http.client
import json
import socket
import ssl
import sys
import time

TOKEN = (sys.argv[1] if len(sys.argv) > 1
         else open("data/raw/opengwas/token.txt", encoding="utf-8").read().strip())
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def req(host, path, headers=None, method="GET", body=None, timeout=40, limit=1500):
    t0 = time.time()
    conn = None
    try:
        conn = http.client.HTTPSConnection(host, 443, timeout=timeout, context=CTX)
        h = {"User-Agent": "Mozilla/5.0", "Connection": "close",
             "Accept": "application/json"}
        if headers:
            h.update(headers)
        conn.request(method, path, body=body, headers=h)
        r = conn.getresponse()
        data = r.read(limit)
        return (f"[{r.status}] {time.time()-t0:5.1f}s len≈{r.getheader('Content-Length')} "
                f"{data[:400].decode('utf-8','replace')}")
    except socket.timeout:
        return f"[TIMEOUT] {time.time()-t0:5.1f}s"
    except Exception as e:  # noqa: BLE001
        return f"[{type(e).__name__}] {time.time()-t0:5.1f}s {str(e)[:140]}"
    finally:
        if conn:
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass


AUTH = {"Authorization": f"Bearer {TOKEN}"}
print("token len:", len(TOKEN))
print()
print("A no-auth  /gwasinfo/ieu-a-2      ", req("api.opengwas.io", "/api/gwasinfo/ieu-a-2"))
print("B auth     /gwasinfo/ieu-a-2      ", req("api.opengwas.io", "/api/gwasinfo/ieu-a-2", AUTH))
print("C auth     /user                  ", req("api.opengwas.io", "/api/user", AUTH))
print("D auth     /gwasinfo?limit=2      ", req("api.opengwas.io", "/api/gwasinfo?limit=2", AUTH))
print("E auth     /tophits (POST)        ",
      req("api.opengwas.io", "/api/tophits",
          {**AUTH, "Content-Type": "application/json"}, "POST",
          json.dumps({"id": ["ieu-a-2"], "pval": 5e-8, "preclump": True,
                      "clump": True, "r2": 0.001, "kb": 10000}).encode(), timeout=90))
print("F auth     /gwasinfo?trait=zinc   ",
      req("api.opengwas.io", "/api/gwasinfo?trait=zinc&limit=3", AUTH))
