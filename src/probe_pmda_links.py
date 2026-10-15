# -*- coding: utf-8 -*-
"""
Show what the PMDA page actually links to, so the JADER archive URLs can be found.

The extension test found nothing, which means the links do not end in .zip or .csv -
PMDA serves its files under paths such as /files/ with the name embedded earlier in the
URL, and some listings are rendered by script rather than present in the served HTML.
Rather than guess at a URL scheme, this prints the distinct link shapes so the pattern
is visible, and searches for the words that would accompany a data download
("JADER", "reaction", "adverse", "download", "ファイル", "ダウンロード").
"""
from __future__ import annotations

import collections
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}
PAGE = ("https://www.pmda.go.jp/safety/info-services/drugs/adr-info/"
        "suspected-adr/0003.html")


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[tuple[str, str]] = []
        self._cur, self._text, self._in = None, [], False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self._in, self._cur, self._text = True, d["href"], []

    def handle_data(self, data):
        if self._in:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._in:
            self.items.append((self._cur or "", " ".join("".join(self._text).split())))
            self._in = False


req = urllib.request.Request(PAGE, headers=UA)
with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
    html = r.read().decode("utf-8", "replace")
print(f"page length: {len(html):,} characters")

p = Links()
p.feed(html)
print(f"anchor links: {len(p.items)}")

print()
print("=" * 92)
print("Link shapes (path patterns, deduplicated)")
print("=" * 92)
shapes = collections.Counter()
for href, _ in p.items:
    path = urllib.parse.urlparse(href).path
    shape = re.sub(r"[0-9]{4,}", "N", path)
    shape = re.sub(r"[0-9]+", "n", shape)
    shapes[shape] += 1
for shape, n in shapes.most_common(24):
    print(f"  {n:>4}  {shape[:100]}")

print()
print("=" * 92)
print("Links whose text or href mentions a data download")
print("=" * 92)
KEYS = ("jader", "download", "ダウンロード", "ファイル", "reaction", "副作用",
        "adverse", "csv", "excel", "zip", "データ")
hits = [(h, t) for h, t in p.items
        if any(k in (h + " " + t).lower() for k in KEYS)]
print(f"  {len(hits)} matches")
for h, t in hits[:36]:
    print(f"      {t[:56]:56s} {h[:84]}")

print()
print("=" * 92)
print("Any link pointing at a file directory")
print("=" * 92)
files = [(h, t) for h, t in p.items if "/files/" in h or "file" in h.lower()]
print(f"  {len(files)} links")
for h, t in files[:24]:
    print(f"      {t[:50]:50s} {h[:88]}")

print()
print("=" * 92)
print("Does the page reference JADER in its raw HTML at all?")
print("=" * 92)
for term in ("JADER", "jader", "副作用", "医薬品医療機器総合機構"):
    print(f"  {term!r}: {html.count(term)} occurrences")
m = [mm.start() for mm in re.finditer("JADER", html)]
for pos in m[:4]:
    print(f"      ...{html[max(0,pos-120):pos+160]}...".replace("\n", " ")[:260])
