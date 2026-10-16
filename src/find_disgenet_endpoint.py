# -*- coding: utf-8 -*-
"""
Find the working DisGeNET interface by testing the plausible forms once, systematically.

What is established already
    www.disgenet.org redirects to disgenet.com, so the platform has moved.  On the old
    domain every /api/ path returns the same 12,572-byte HTML document with status 200 -
    including a path invented for the test - which proves the server is not routing those
    requests to an API at all.  A key cannot fix that; the host is wrong.

What this does
    Tests the combinations that the migration makes plausible: the new host, with the key as
    a bearer header and as a query parameter, against the routes the public documentation and
    the ToolUniverse client refer to.  A response counts only if it parses as JSON, so an
    HTML page cannot be mistaken for data.

    If nothing works the answer is reported as "the interface is elsewhere", together with
    what to look for in the account page, rather than guessed at further.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = (ROOT / "credential" / "disgenet_key.txt").read_text(
    encoding="utf-8", errors="replace").strip().split()[-1].strip('"').strip("'")

HOSTS = ["https://disgenet.com", "https://www.disgenet.com",
         "https://api.disgenet.com", "https://www.disgenet.org"]
ROUTES = ["/api/gda/summary/TP53", "/api/gda/gene/TP53", "/api/gene/7157",
          "/api/v1/gda/summary/TP53", "/api/v1/gene/7157"]
AUTH = {
    "bearer": {"Authorization": f"Bearer {KEY}"},
    "x-api-key": {"x-api-key": KEY},
    "query api_key": None,      # handled by appending to the URL
    "query key": None,
}
BASE_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
                "Accept": "application/json"}


def try_request(url: str, headers: dict) -> tuple[int | None, str]:
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, headers={**BASE_HEADERS, **headers}),
                timeout=25) as fh:
            return fh.status, fh.read(300_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(3000).decode("utf-8", "replace")
        except Exception:
            return e.code, ""
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {str(e)[:90]}"


def parses(body: str):
    s = body.lstrip()
    if not s.startswith(("[", "{")):
        return None
    try:
        return json.loads(body)
    except Exception:
        return None


print("=" * 100)
print("DisGeNET interface probe")
print("=" * 100)
print(f"  key: {KEY[:4]}...{KEY[-4:]}  ({len(KEY)} characters)")
print()

hits = []
for host in HOSTS:
    for route in ROUTES:
        for label, hdr in AUTH.items():
            url = host + route
            headers = dict(hdr) if hdr else {}
            if label == "query api_key":
                url += ("&" if "?" in url else "?") + "api_key=" + urllib.parse.quote(KEY)
            elif label == "query key":
                url += ("&" if "?" in url else "?") + "key=" + urllib.parse.quote(KEY)
            status, body = try_request(url, headers)
            parsed = parses(body)
            if parsed is not None:
                n = len(parsed) if isinstance(parsed, list) else 1
                print(f"  DATA  {host}{route}  via {label}   status {status}  "
                      f"{n} record(s)")
                print(f"        {body[:200]}")
                hits.append({"host": host, "route": route, "auth": label,
                             "url": url, "records": n})
                break
        if hits and hits[-1]["host"] == host and hits[-1]["route"] == route:
            break
    # a single host-level result is enough to move on
    if hits and hits[-1]["host"] == host:
        continue

print()
print("=" * 100)
print("What a representative failure looks like")
print("=" * 100)
status, body = try_request("https://disgenet.com/api/gda/summary/TP53",
                           {"Authorization": f"Bearer {KEY}"})
print(f"  status {status}, {len(body):,} bytes")
print(f"  {body[:220]}")

print()
print("=" * 100)
print("Result")
print("=" * 100)
if hits:
    print(f"  working combinations: {len(hits)}")
    for h in hits:
        print(f"      {h['url']}   via {h['auth']}")
    (ROOT / "results" / "disgenet_endpoint.json").write_text(
        json.dumps(hits, indent=2, ensure_ascii=False), encoding="utf-8")
else:
    print("""  No combination returned JSON.  Since the old host serves its own web page for every
  /api/ path, the interface has moved with the disgenet.com migration and its address is
  not recoverable by guessing.

  What to look for: sign in at disgenet.com, and on the account or 'Tools' page there is an
  API section that states the base URL and the header the key goes in.  That page is the
  authoritative source, and pasting its example request here is enough to finish this.""")
