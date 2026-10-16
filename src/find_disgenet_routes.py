# -*- coding: utf-8 -*-
"""
Locate the DisGeNET API's own route list, then use it.

The previous probe established that api.disgenet.com is the API host: it answers an unknown
path with {"message":"Resource not found"} and status 404, which is a routed API replying,
not a web server serving its single-page application.  The path guessed in that probe was
not the right one.

Rather than enumerate plausible paths, the API's own specification is requested first.  If it
is published the routes and parameters come from the source and nothing is guessed.  Only if
it is absent are the common shapes tried.

The key is read from file and never printed.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = (ROOT / "credential" / "disgenet_key.txt").read_text(
    encoding="utf-8", errors="replace").strip().split()[-1].strip('"').strip("'")

H = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
     "Accept": "application/json, text/plain, */*",
     "Authorization": f"Bearer {KEY}"}
BASES = ["https://api.disgenet.com", "https://api.disgenet.com/api"]


def get(url: str, timeout: int = 25):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=H),
                                    timeout=timeout) as fh:
            return fh.status, fh.read(600_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(6000).decode("utf-8", "replace")
        except Exception:
            return e.code, ""
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {str(e)[:90]}"


print("=" * 98)
print("1. Looking for a published specification")
print("=" * 98)
SPECS = ["/openapi.json", "/swagger.json", "/api/openapi.json", "/api/swagger.json",
         "/docs", "/redoc", "/api/docs", "/v3/api-docs", "/api-docs"]
spec_url = None
for base in BASES:
    for path in SPECS:
        status, body = get(base + path)
        s = body.lstrip()
        interesting = (status == 200 and (s.startswith("{") or s.startswith("["))) \
            or (status == 200 and "swagger" in body.lower())
        if interesting:
            print(f"  FOUND {base+path}  status {status}  {len(body):,} bytes")
            spec_url = base + path
            break
        if status not in (404, 403):
            print(f"  status {status}  {base+path}  {body[:80]!r}")
    if spec_url:
        break

routes: list[str] = []
if spec_url:
    status, body = get(spec_url)
    try:
        spec = json.loads(body)
    except Exception:
        spec = {}
    paths = spec.get("paths") or {}
    print(f"\n  routes declared in the specification: {len(paths)}")
    for p in sorted(paths)[:60]:
        methods = ",".join(sorted(k.upper() for k in paths[p] if k.islower()))
        print(f"      {methods:12s} {p}")
        routes.append(p)
    (ROOT / "results" / "disgenet_openapi.json").write_text(
        json.dumps(spec, indent=2)[:2_000_000], encoding="utf-8")
    print(f"\n  specification saved: results/disgenet_openapi.json")
else:
    print("  no specification found at the usual locations")

if not routes:
    print()
    print("=" * 98)
    print("2. No specification, so the documented shapes are tried once")
    print("=" * 98)
    CANDIDATES = [
        "/gda/summary/TP53", "/gda/gene/TP53", "/gene/7157", "/gene/TP53",
        "/v1/gda/summary/TP53", "/v1/gene/7157", "/api/v1/gda/summary/TP53",
        "/entities/gene/TP53", "/entity/gene/TP53", "/gda/TP53", "/disease/C0029463",
        "/gda/summary?gene=TP53", "/search?q=TP53",
    ]
    for base in BASES:
        for path in CANDIDATES:
            status, body = get(base + path)
            s = body.lstrip()
            if s.startswith(("{", "[")):
                try:
                    parsed = json.loads(body)
                except Exception:
                    continue
                if isinstance(parsed, dict) and set(parsed) == {"message"}:
                    if "not found" not in str(parsed.get("message", "")).lower():
                        print(f"  message  {base+path}  status {status}  {body[:120]}")
                    continue
                n = len(parsed) if isinstance(parsed, list) else len(parsed)
                print(f"  DATA     {base+path}  status {status}  {n} key(s)/record(s)")
                print(f"           {body[:200]}")
                routes.append(path)
    if routes:
        print(f"\n  working routes: {sorted(set(routes))}")

print()
print("=" * 98)
print("Conclusion")
print("=" * 98)
if routes:
    print(f"  usable route(s) found: {sorted(set(routes))}")
    print("  The hub-gene annotation can now be run against DisGeNET.")
else:
    print("""  The API host answers, but neither a published specification nor any documented route
  shape was accepted, so the address of the endpoints is still unknown and guessing further
  would waste attempts.

  One thing settles it, and it takes a moment: sign in at disgenet.com and open the account
  or Tools page.  There is an API section showing the base URL and a sample request with the
  header the key belongs in.  Pasting that sample here is enough.""")
