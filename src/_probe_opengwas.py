# -*- coding: utf-8 -*-
"""Validate the OpenGWAS API token and probe the endpoints the MR script uses."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
ROOT = Path(__file__).resolve().parents[1]
(ROOT / "data" / "raw" / "opengwas").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "raw" / "opengwas" / "token.txt").write_text(TOKEN, encoding="utf-8")

BASE = "https://api.opengwas.io/api"
H = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 eon-mr/1.0",
     "Content-Type": "application/json"}


def get(url, timeout=120):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def post(url, payload, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=H)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


print("### 1. token status")
for path in ("/user", "/status", "/gwasinfo/ieu-a-2"):
    try:
        st, body = get(BASE + path)
        print(f"[{st}] {path}: {body[:220]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {path}: {e.read().decode()[:220]}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {path}: {type(e).__name__} {str(e)[:90]}")
    time.sleep(0.5)

print("\n### 2. trait search")
for term in ("creatinine", "zinc", "type 2 diabetes", "smoking", "vitamin B12"):
    try:
        st, body = get(f"{BASE}/gwasinfo?trait={urllib.parse.quote(term)}&limit=5"
                       if False else
                       f"{BASE}/gwasinfo?trait={term.replace(' ', '%20')}&limit=5")
        d = json.loads(body)
        rows = [{"id": k, **v} for k, v in d.items()] if isinstance(d, dict) else d
        print(f"[{st}] '{term}': {len(rows)} datasets")
        for r in rows[:3]:
            print(f"      {r.get('id'):18s} n={r.get('sample_size')} "
                  f"pop={r.get('population')} {str(r.get('trait'))[:52]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] '{term}': {e.read().decode()[:160]}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] '{term}': {type(e).__name__} {str(e)[:80]}")
    time.sleep(0.6)

print("\n### 3. tophits endpoint")
for gid in ("ieu-a-2", "ieu-b-40", "ebi-a-GCST006867"):
    try:
        st, body = post(f"{BASE}/tophits",
                        {"id": [gid], "pval": 5e-8, "preclump": True,
                         "clump": True, "r2": 0.001, "kb": 10000})
        d = json.loads(body)
        rows = d if isinstance(d, list) else d.get("data", d.get("results", []))
        print(f"[{st}] tophits {gid}: {len(rows)} rows")
        if rows:
            print(f"      keys: {list(rows[0].keys())[:18]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] tophits {gid}: {e.read().decode()[:200]}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] tophits {gid}: {type(e).__name__} {str(e)[:90]}")
    time.sleep(0.6)

import urllib.parse  # noqa: E402  (imported late to keep the probe readable)
