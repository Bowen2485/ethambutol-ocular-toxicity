# -*- coding: utf-8 -*-
"""
Find where the JADER files are actually hosted.

Two pages in the .../suspected-adr/ directory have now been read, and neither contains a
link ending in a data extension, although the 0005 page is headed "information on case
reports of suspected adverse reactions" and mentions 2004 and 2026 - so the listing is
there but the file links are not in the form expected.

Rather than guess again, this prints the raw strings in the page that look like file
references, together with every distinct host and path prefix, so the actual scheme
becomes visible.  It also checks the pages that sit beside 0005 in the directory, in
case the file list lives on a sibling page.
"""
from __future__ import annotations

import collections
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}
BASE = "https://www.pmda.go.jp"
CANDIDATES = [
    f"{BASE}/safety/info-services/drugs/adr-info/suspected-adr/0005.html",
    f"{BASE}/safety/info-services/drugs/adr-info/suspected-adr/0004.html",
    f"{BASE}/safety/info-services/drugs/adr-info/suspected-adr/0006.html",
    f"{BASE}/safety/info-services/drugs/adr-info/0001.html",
]


def get(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        print(f"    {type(exc).__name__} {str(exc)[:60]}")
        return None


for url in CANDIDATES:
    print("=" * 96)
    print(url)
    print("=" * 96)
    html = get(url)
    if not html:
        continue
    print(f"  length {len(html):,}")

    # every distinct host and first path segment
    hosts = collections.Counter()
    prefixes = collections.Counter()
    for m in re.finditer(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', html, re.I):
        raw = m.group(1)
        full = urllib.parse.urljoin(url, raw)
        u = urllib.parse.urlparse(full)
        hosts[u.netloc] += 1
        seg = "/".join(u.path.split("/")[:4])
        prefixes[seg] += 1
    print("  hosts:")
    for h, n in hosts.most_common(8):
        print(f"      {n:>5}  {h}")
    print("  path prefixes:")
    for s, n in prefixes.most_common(10):
        print(f"      {n:>5}  {s}")

    # raw strings that look like archive names, whatever the surrounding markup
    pats = [r'["\'/][^"\']*?\.(?:zip|xls|xlsx|csv|txt|lzh|gz)["\']',
            r'JADER[^<"\']{0,60}',
            r'jader[^<"\']{0,60}',
            r'[0-9]{6,8}[^<"\']{0,40}\.(?:zip|xls|xlsx)']
    found = []
    for pat in pats:
        found += re.findall(pat, html, re.I)
    print(f"  file-name-like strings: {len(found)}")
    for s in list(dict.fromkeys(found))[:18]:
        print(f"      {s[:92]}")

    # is the list perhaps rendered from a JSON or XML endpoint?
    for m in re.finditer(r'(?:ajax|json|xml|api)[^"\']{0,80}', html, re.I):
        pass
    endpoints = set(re.findall(r'["\']([^"\']*(?:json|xml|api)[^"\']*)["\']', html,
                               re.I))
    if endpoints:
        print(f"  possible data endpoints: {len(endpoints)}")
        for e in list(endpoints)[:10]:
            print(f"      {e[:88]}")
    print()
