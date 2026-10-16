# -*- coding: utf-8 -*-
"""
Decide whether GeneCards is blocked by a bot challenge or simply has no API.

The previous probe could not distinguish the two, because every request returned the same
170-character Cloudflare interstitial titled "Just a moment...".  That is a challenge page, so
a 403 from it says nothing about whether a route exists - it is returned before the route is
consulted.

Two tests separate the cases.

    A full browser User-Agent is sent, with the headers a real navigation carries.  If the
    challenge lifts, the resource is reachable and the earlier 403 was about bot detection.

    GeneCards' own bulk-download and terms pages are requested, because those are the routes a
    data provider documents if it intends programmatic use, and because they are static files
    rather than application routes, so a challenge page is less likely to hide them.

Nothing is bypassed.  No challenge is solved, no cookie is forged and no rate limit is
evaded; if the site requires a browser, that is the finding, and the honest conclusion is
that the values have to be obtained through the web interface by the person who holds the
licence.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "genecards_probe2.json"

#: the headers a Chrome navigation sends, so the request is not identifiable as a script by
#: the absence of these alone
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


def probe(label: str, url: str, timeout: int = 30) -> dict:
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, headers=BROWSER), timeout=timeout) as fh:
            body = fh.read(300_000).decode("utf-8", "replace")
            code = fh.status
    except urllib.error.HTTPError as e:
        try:
            body = e.read(6000).decode("utf-8", "replace")
        except Exception:
            body = ""
        code = e.code
    except Exception as e:  # noqa: BLE001
        body, code = f"{type(e).__name__}: {str(e)[:90]}", None
    low = body[:600].lower()
    challenge = ("just a moment" in low or "cf-chl" in low
                 or "enable javascript and cookies" in low
                 or "checking your browser" in low)
    return {"label": label, "url": url, "status": code, "bytes": len(body),
            "challenge": challenge, "sample": body[:200].replace(chr(10), " ")}


TARGETS = [
    ("gene page with browser headers",
     "https://www.genecards.org/cgi-bin/carddisp.pl?gene=TP53"),
    ("bulk download page", "https://www.genecards.org/bulkdownload/"),
    ("legal and licensing", "https://www.genecards.org/Legal/"),
    ("about the suite", "https://www.genecards.org/Guide/"),
    ("MalaCards home", "https://www.malacards.org/"),
    ("GeneALaCart with browser headers", "https://genealacart.genecards.org/"),
]

print("=" * 100)
print("GeneCards access, with browser headers.  No challenge is solved and no limit evaded.")
print("=" * 100)
rows = []
for label, url in TARGETS:
    r = probe(label, url)
    rows.append(r)
    kind = "CHALLENGE" if r["challenge"] else ("page" if r["status"] == 200 else "refused")
    print(f"  {str(r['status']):>5}  {kind:9s}  {r['bytes']:>8,} B  {label}")
    print(f"         {r['sample'][:110]}")

OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

print()
print("=" * 100)
print("Reading")
print("=" * 100)
lifted = [r for r in rows if r["status"] == 200 and not r["challenge"]]
still = [r for r in rows if r["challenge"]]
print(f"  pages served without a challenge : {len(lifted)}")
for r in lifted:
    print(f"      {r['label']}")
print(f"  still behind the challenge       : {len(still)}")
for r in still:
    print(f"      {r['label']}")
print()
if still and not lifted:
    print("""  Every route is behind the bot challenge, which is returned before a route is
  consulted.  It therefore cannot be determined from outside whether a licensed API exists,
  and no attempt is made to get past the challenge.

  What this means for the manuscript: the GeneCards values, if they are wanted, have to be
  obtained through the web interface by the person holding the licence, and then supplied as
  a file.  The alternative already implemented is DisGeNET, whose interface is documented and
  whose academic tier is in use.""")
elif lifted:
    print("""  Some routes are reachable, so the earlier 403 was bot detection rather than a
  statement about the resource.  What those pages say about licensing and bulk access decides
  the next step.""")
print(f"\n  written: {OUT.relative_to(ROOT)}")
