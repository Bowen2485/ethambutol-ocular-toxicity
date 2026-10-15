# -*- coding: utf-8 -*-
"""Probe the FinnGen pheweb JSON API as a faster path to regional association data."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.status, r.read().decode("utf-8", "replace")


CANDS = [
    ("region", "https://r12.finngen.fi/api/region?chrom=3&start=193593000&end=193700000&pheno=H7_OPTNEURITIS"),
    ("region2", "https://r12.finngen.fi/api/region?chrom=3&start=193593000&end=193700000&phenocode=H7_OPTNEURITIS"),
    ("variant", "https://r12.finngen.fi/api/variant?chrom=3&pos=193593592&pheno=H7_OPTNEURITIS"),
    ("pheno", "https://r12.finngen.fi/api/pheno/H7_OPTNEURITIS"),
    ("top_hits", "https://r12.finngen.fi/api/top_hits?pheno=H7_OPTNEURITIS"),
    ("manhattan", "https://r12.finngen.fi/api/manhattan?pheno=H7_OPTNEURITIS"),
    ("phenos", "https://r12.finngen.fi/api/phenos"),
    ("variant_list", "https://r12.finngen.fi/api/variant_list?pheno=H7_OPTNEURITIS"),
    ("pheweb_root", "https://r12.finngen.fi/api/"),
]
for name, url in CANDS:
    try:
        st, body = get(url, timeout=90)
        kind = "JSON" if body.lstrip()[:1] in "[{" else "HTML/other"
        print(f"[{st}] {name:12s} {kind:10s} len={len(body):>8} :: {body[:180]!r}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {name:12s} {e.read()[:140]!r}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name:12s} {type(e).__name__} {str(e)[:90]}")
