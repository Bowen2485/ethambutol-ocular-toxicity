# -*- coding: utf-8 -*-
"""
Step 1 (alt) - Acquire the FAERS quarterly ASCII extracts.

openFDA throttles sustained bulk pagination (limit=100 requests hang after a few
hundred calls), so the primary source is the FDA's own quarterly ASCII release:
it is the authoritative, unaggregated FAERS distribution and carries every field
including CASEID (needed for true case-version de-duplication) and the free-text
indications, which openFDA's harmonised view omits.

This script scrapes the official download page and stores the file inventory.
Downloading is a separate step (faers_ascii_load.py) so the inventory can be
inspected before gigabytes are pulled.
"""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
RAW.mkdir(parents=True, exist_ok=True)
DERIVED.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

PAGES = [
    "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html",
    "https://fis.fda.gov/content/Exports/faers_ascii_2012q4.zip",
]


def fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def main() -> None:
    html = fetch(PAGES[0]).decode("utf-8", "replace")
    (RAW / "faers_download_page.html").write_text(html, encoding="utf-8")

    # every absolute URL mentioned on the page
    urls = sorted(set(re.findall(r'https?://[^\s"\'<>\\]+', html)))
    zip_urls = [u for u in urls if u.lower().endswith(".zip")]
    other = [u for u in urls if u not in zip_urls]

    # relative links resolved against the page
    rel = sorted(set(re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I)))
    rel_files = [r for r in rel if r.lower().endswith(".zip")]

    print(f"page bytes            : {len(html):,}")
    print(f"absolute .zip urls    : {len(zip_urls)}")
    for u in zip_urls[:20]:
        print("   ", u)
    print(f"relative .zip links   : {len(rel_files)}")
    for r in rel_files[:40]:
        print("   ", r)
    print(f"other absolute urls   : {len(other)}")
    for u in other[:25]:
        print("   ", u)

    # look for a quarterly table and the standard file naming convention
    quarters = sorted(set(re.findall(r"(\d{4})\s*[qQ]([1-4])", html)))
    print(f"\nquarters mentioned on page: {quarters[:40]}"
          f"{' ...' if len(quarters) > 40 else ''}")

    inv = {
        "page": PAGES[0],
        "page_bytes": len(html),
        "zip_absolute": zip_urls,
        "zip_relative": rel_files,
        "candidate_patterns": {
            "standard": "https://fis.fda.gov/content/Exports/faers_ascii_{YYYY}q{Q}.zip",
            "aers_legacy": "https://fis.fda.gov/content/Exports/aers_ascii_{YYYY}q{Q}.zip",
        },
    }
    (DERIVED / "faers_ascii_inventory.json").write_text(
        json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n-> {DERIVED / 'faers_ascii_inventory.json'}")


if __name__ == "__main__":
    main()
