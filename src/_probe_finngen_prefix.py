# -*- coding: utf-8 -*-
"""Locate the FinnGen R12 summary-statistics object prefix inside the public bucket."""
from __future__ import annotations

import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}
GB = "https://storage.googleapis.com/finngen-public-data-r12"


def list_keys(prefix: str = "", delimiter: str = "", max_keys: int = 50):
    url = f"{GB}?list-type=2&max-keys={max_keys}"
    if prefix:
        url += f"&prefix={urllib.parse.quote(prefix)}"
    if delimiter:
        url += f"&delimiter={urllib.parse.quote(delimiter)}"
    for a in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            time.sleep(1.5 * (a + 1))
    return ""


print("### top-level prefixes (delimiter=/)")
body = list_keys("", "/", 200)
prefixes = re.findall(r"<Prefix>([^<]+)</Prefix>", body)
print("\n".join(prefixes[:60]))

for pfx in ["summary_stats/", "pheweb/", "summary_stats/release/",
            "summary_stats/R12/", "pheweb/pheno_gz/"]:
    body = list_keys(pfx, "/", 30)
    pre = re.findall(r"<Prefix>([^<]+)</Prefix>", body)
    keys = re.findall(r"<Key>([^<]+)</Key>", body)
    print(f"\n### prefix '{pfx}': {len(pre)} sub-prefixes, {len(keys)} keys")
    for x in pre[:12]:
        print("   P", x)
    for x in keys[:8]:
        print("   K", x)

print("\n### direct probe of likely URLs")
cands = [
    ("summary_stats/release/finngen_R12_H7_OPTNEURITIS.gz"),
    ("summary_stats/finngen_R12_H7_OPTNEURITIS.gz"),
    ("pheweb/pheno_gz/H7_OPTNEURITIS.gz"),
    ("summary_stats/release/finngen_R12_H7_OPTNEURITIS.gz.tbi"),
]
for c in cands:
    url = f"{GB}/{c}"
    try:
        req = urllib.request.Request(url, headers={**UA}, method="HEAD")
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            print(f"[{r.status}] {c}  len={r.headers.get('Content-Length')}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {c}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {c}: {type(e).__name__}")
    time.sleep(0.3)
