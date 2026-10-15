# -*- coding: utf-8 -*-
"""
Check the PMDA bulk-download page for JADER.

A literature search returned the URL of the PMDA's own bulk-download page for the
adverse-reaction report dataset:

    https://www.info.pmda.go.jp/fukusayoudb/CsvDownload.jsp

Note the host: info.pmda.go.jp, not www.pmda.go.jp.  The pages read earlier were on the
www host and are JavaScript shells, which is why no file links were found there; the
www host also linked once to info.pmda.go.jp, a hint that the data lives on the other
host.  This checks that directly.

The page is a JSP listing rather than a static index, so the file links may be absolute
URLs into a data directory.  This prints every link it finds, and the likely archives.
"""
from __future__ import annotations

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
URL = "https://www.info.pmda.go.jp/fukusayoudb/CsvDownload.jsp"


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[tuple[str, str]] = []
        self._cur, self._text, self._in = None, [], False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self._in, self._cur, self._text = True, d["href"], []
        # some JSP listings use onclick handlers or form inputs instead of anchors
        for k in ("onclick", "value"):
            if k in d and isinstance(d[k], str) and any(
                    e in d[k].lower() for e in (".zip", ".csv", ".xls", ".txt")):
                self.items.append((d[k], f"[{tag} {k}]"))

    def handle_data(self, data):
        if self._in:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._in:
            self.items.append((self._cur or "",
                               " ".join("".join(self._text).split())))
            self._in = False


print("=" * 92)
print(f"Fetching {URL}")
print("=" * 92)
try:
    req = urllib.request.Request(URL, headers=UA)
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        html = r.read().decode("utf-8", "replace")
        print(f"  HTTP {r.status}, {len(html):,} characters")
except urllib.error.HTTPError as exc:
    raise SystemExit(f"  HTTP {exc.code}")
except Exception as exc:  # noqa: BLE001
    raise SystemExit(f"  {type(exc).__name__}: {exc}")

p = Links()
p.feed(html)
print(f"  anchors and file-bearing attributes: {len(p.items)}")

FILE_EXT = (".zip", ".csv", ".xls", ".xlsx", ".txt", ".lzh", ".gz")
data = []
for href, text in p.items:
    low = href.lower()
    if any(e in low for e in FILE_EXT):
        data.append((urllib.parse.urljoin(URL, href), text))

print()
print("=" * 92)
print(f"File links: {len(data)}")
print("=" * 92)
for u, t in data[:50]:
    print(f"  {t[:46]:46s} {u[:80]}")

print()
print("=" * 92)
print("All link path shapes")
print("=" * 92)
shapes = {}
for href, text in p.items:
    u = urllib.parse.urlparse(urllib.parse.urljoin(URL, href))
    key = re.sub(r"[0-9]+", "N", u.path)
    shapes.setdefault(key, []).append((href, text))
for k in list(shapes)[:20]:
    n = len(shapes[k])
    print(f"  {n:>4}  {k[:88]}")

print()
print("=" * 92)
print("Raw strings that look like archive names")
print("=" * 92)
pats = [r'[A-Za-z0-9_\-]+\.(?:zip|csv|xls|xlsx|txt|lzh)',
        r'href\s*=\s*["\']([^"\']+)["\']',
        r'location\.href\s*=\s*["\']([^"\']+)["\']']
hits = []
for pat in pats:
    hits += re.findall(pat, html, re.I)
uniq = list(dict.fromkeys(hits))
print(f"  {len(uniq)} distinct strings")
for s in uniq[:30]:
    print(f"      {s[:92]}")

if not data:
    print()
    print("  No file links.  The page may require a session or may build its list by")
    print("  script; the printable text of the page is shown below so the structure is")
    print("  visible rather than guessed at.")
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = " ".join(text.split())
    print(f"  visible text, first 1200 characters:\n      {text[:1200]}")
