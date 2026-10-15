# -*- coding: utf-8 -*-
"""
Extract the JADER download links from the PMDA page.

JADER is the Japanese adverse drug event report database, maintained by the
Pharmaceuticals and Medical Devices Agency.  It is the only clearly independent,
freely downloadable case-level source reachable from here:

    openFDA       is FAERS by another route, so using it to replicate a FAERS finding
                  would be circular and is not a validation at all
    EudraVigilance requires an EMA account and a data-use agreement
    VigiBase       requires UMC membership
    VigiAccess     is public but aggregated, with no per-case drug and reaction fields,
                   so a 2x2 table cannot be built from it

What JADER contains, per report: a case identifier, the drug name and its role, and the
reaction terms.  That is exactly the structure the disproportionality analysis needs.

This script parses the listing page for file links.  It downloads nothing.
"""
from __future__ import annotations

import re
import ssl
import urllib.error
import urllib.request
from html.parser import HTMLParser

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}

PAGES = [
    "https://www.pmda.go.jp/safety/info-services/drugs/adr-info/suspected-adr/0003.html",
    "https://www.pmda.go.jp/english/reviews/psr-hp/0011.html",
]


class Links(HTMLParser):
    """Collect href and src attributes with their anchor text."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[tuple[str, str]] = []
        self._cur: str | None = None
        self._text: list[str] = []
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a":
            self._in_a = True
            self._cur = d.get("href")
            self._text = []
        if "href" in d and tag != "a":
            self.hrefs.append((d["href"], ""))

    def handle_data(self, data):
        if self._in_a:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            if self._cur:
                self.hrefs.append((self._cur, "".join(self._text).strip()))
            self._in_a = False
            self._cur = None


found = []
for page in PAGES:
    print("=" * 92)
    print(f"Page: {page}")
    print("=" * 92)
    try:
        req = urllib.request.Request(page, headers=UA)
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            html = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        print(f"  HTTP {exc.code}")
        continue
    except Exception as exc:  # noqa: BLE001
        print(f"  {type(exc).__name__}")
        continue

    p = Links()
    p.feed(html)
    seen = set()
    hits = []
    for href, text in p.hrefs:
        if not href or href in seen:
            continue
        seen.add(href)
        low = href.lower()
        # JADER archives are published as zip or excel files, often with a date in the
        # name; the listing page also carries links to explanatory PDFs we do not want
        if any(low.endswith(e) or e + "?" in low for e in
               (".zip", ".xls", ".xlsx", ".csv", ".gz", ".lzh")):
            hits.append((href, text))
    print(f"  {len(p.hrefs)} links on the page; {len(hits)} look like data files")
    for href, text in hits[:40]:
        full = href if href.startswith("http") else \
            urllib.parse.urljoin(page, href) if hasattr(urllib, "parse") else href
        print(f"      {text[:52]:52s} {href[:88]}")
        found.append((full, text))

    # also note any links whose text mentions the database by name
    named = [(h, t) for h, t in p.hrefs if "jader" in (h + t).lower()]
    if named:
        print(f"  links mentioning JADER: {len(named)}")
        for h, t in named[:14]:
            print(f"      {t[:50]:50s} {h[:86]}")

print()
print("=" * 92)
print("Summary")
print("=" * 92)
if found:
    print(f"  {len(found)} candidate data files identified")
    print("  Downloading them is the next step; each quarterly archive is tens of MB and")
    print("  the full series runs from 2004, so the fetch is small compared with FAERS.")
else:
    print("  No direct data links were found.  The PMDA pages may load their file lists")
    print("  through JavaScript, in which case the archives have to be located manually")
    print("  or through the PMDA's file server listing.")
