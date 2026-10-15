# -*- coding: utf-8 -*-
"""
Step 6a - Find suitable OpenGWAS exposure datasets for the MR.

A trial OpenGWAS account allows ~100 queries per day, so this script runs one
paginated listing of the full public catalogue and filters it locally instead of
issuing one search request per trait.

Output: data/derived/opengwas_catalogue.csv  and a shortlist per exposure family.
"""
from __future__ import annotations

import http.client
import json
import ssl
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RAW = ROOT / "data" / "raw" / "opengwas"
RAW.mkdir(parents=True, exist_ok=True)

TOKEN = (RAW / "token.txt").read_text(encoding="utf-8").strip()
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HOST = "api.opengwas.io"


def api(path: str, method: str = "GET", body=None, timeout: int = 300,
        limit_bytes: int | None = None) -> bytes:
    for attempt in range(4):
        conn = None
        try:
            conn = http.client.HTTPSConnection(HOST, 443, timeout=timeout, context=CTX)
            h = {"User-Agent": "Mozilla/5.0", "Connection": "close",
                 "Accept": "application/json",
                 "Authorization": f"Bearer {TOKEN}"}
            if body is not None:
                h["Content-Type"] = "application/json"
            conn.request(method, path, body=body, headers=h)
            r = conn.getresponse()
            if r.status == 429:
                wait = int(r.getheader("Retry-After") or 30)
                print(f"    throttled, waiting {wait}s")
                time.sleep(wait)
                continue
            data = r.read() if limit_bytes is None else r.read(limit_bytes)
            if r.status != 200:
                raise RuntimeError(f"HTTP {r.status}: {data[:300]!r}")
            return data
        except Exception as exc:  # noqa: BLE001
            if attempt == 3:
                raise
            print(f"    retry {attempt+1}: {type(exc).__name__} {str(exc)[:90]}")
            time.sleep(3 * (attempt + 1))
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:  # noqa: BLE001
                    pass
    raise RuntimeError("unreachable")


print("[1] listing the OpenGWAS catalogue ...")
cache = RAW / "catalogue.json"
if cache.exists() and cache.stat().st_size > 1_000_000:
    payload = json.loads(cache.read_text(encoding="utf-8"))
    print(f"    cached: {len(payload)} datasets")
else:
    payload = json.loads(api("/api/gwasinfo").decode("utf-8", "replace"))
    cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"    {len(payload)} datasets")

rows = [{"id": k, **v} for k, v in payload.items()]
cat = pd.DataFrame(rows)
for c in ("sample_size", "ncase", "ncontrol", "nsnp", "year"):
    if c in cat.columns:
        cat[c] = pd.to_numeric(cat[c], errors="coerce")
cat.to_csv(DERIVED / "opengwas_catalogue.csv", index=False, encoding="utf-8-sig")
print(f"    catalogue -> {DERIVED / 'opengwas_catalogue.csv'}")

print("\n[2] restricting to European-ancestry, MR-eligible, well-powered datasets")
sub = cat.copy()
if "mr" in sub.columns:
    sub = sub[sub.mr.astype(str).isin(["1", "1.0", "True", "true"])]
if "population" in sub.columns:
    sub = sub[sub.population.astype(str).str.contains("European", case=False, na=False)]
if "sample_size" in sub.columns:
    sub = sub[sub.sample_size.fillna(0) >= 10_000]
print(f"    {len(sub)} datasets eligible")

FAMILIES = {
    "renal_function": ["creatinine", "cystatin", "glomerular filtration", "egfr",
                       "urea", "kidney function"],
    "zinc_copper": ["zinc", "copper", "ceruloplasmin"],
    "b_vitamins": ["vitamin b12", "cobalamin", "folate", "homocysteine"],
    "glycaemia": ["type 2 diabetes", "hba1c", "glycated haemoglobin",
                  "fasting glucose", "fasting insulin"],
    "smoking": ["smoking", "cigarettes", "ever smoked", "smoking initiation"],
    "alcohol": ["alcohol", "drinks per week", "alcohol consumption"],
    "lipids_bmi_extra": ["body mass index", "ldl", "hdl", "triglyceride"],
}
trait_col = "trait" if "trait" in sub.columns else None
print("\n[3] shortlist per exposure family")
short: dict[str, pd.DataFrame] = {}
for fam, kws in FAMILIES.items():
    if trait_col is None:
        break
    mask = sub[trait_col].astype(str).str.lower().apply(
        lambda t: any(k in t for k in kws))
    hit = sub[mask].sort_values("sample_size", ascending=False)
    short[fam] = hit
    print(f"\n  --- {fam} ({len(hit)}) ---")
    cols = [c for c in ("id", "trait", "sample_size", "ncase", "ncontrol",
                        "population", "author", "year") if c in hit.columns]
    print(hit.head(12)[cols].to_string(index=False, max_colwidth=52))

out = pd.concat([v.assign(family=k) for k, v in short.items() if len(v)],
                ignore_index=True)
out.to_csv(DERIVED / "opengwas_shortlist.csv", index=False, encoding="utf-8-sig")
print(f"\n-> {DERIVED / 'opengwas_shortlist.csv'} ({len(out)} rows)")
