# -*- coding: utf-8 -*-
"""
Measure reachability of the PMDA hosts, separating slowness from blockage.

The bulk-download page timed out at 90 seconds, but other Japanese and international
hosts answered earlier in the same session, so the cause is not obvious: it could be a
slow host, a route that is throttled, or a page that streams without ever closing.  A
single timeout cannot tell those apart.

This times a short request to each relevant host, with and without a HEAD, so the
behaviour is quantified rather than assumed.
"""
from __future__ import annotations

import socket
import ssl
import time
import urllib.error
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}

HOSTS = [
    ("info.pmda.go.jp", "/fukusayoudb/CsvDownload.jsp"),
    ("info.pmda.go.jp", "/"),
    ("www.pmda.go.jp", "/safety/info-services/drugs/adr-info/suspected-adr/0005.html"),
    ("www.vigiaccess.org", "/"),
    ("api.fda.gov", "/drug/event.json?limit=1"),
]


def timed(url: str, timeout: int = 30, method: str = "GET") -> tuple:
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA, method=method)
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            head = r.read(4096) if method == "GET" else b""
            return (time.time() - t0, r.status, len(head))
    except urllib.error.HTTPError as exc:
        return (time.time() - t0, f"HTTP {exc.code}", 0)
    except Exception as exc:  # noqa: BLE001
        return (time.time() - t0, type(exc).__name__, 0)


print("=" * 92)
print("DNS resolution")
print("=" * 92)
for host, _ in HOSTS:
    t0 = time.time()
    try:
        ip = socket.gethostbyname(host)
        print(f"  {host:24s} -> {ip:16s} ({time.time()-t0:.2f}s)")
    except Exception as exc:  # noqa: BLE001
        print(f"  {host:24s} -> FAILED {type(exc).__name__} ({time.time()-t0:.2f}s)")

print()
print("=" * 92)
print("Timed requests, 25 s timeout each")
print("=" * 92)
for host, path in HOSTS:
    url = f"https://{host}{path}"
    for method in ("HEAD", "GET"):
        dt, status, n = timed(url, timeout=25, method=method)
        print(f"  {host:22s} {method:5s} {dt:6.2f}s  {str(status):>14s}  "
              f"{n:>6} bytes")
    print()

print("=" * 92)
print("Reading")
print("=" * 92)
print("""  A status with a short elapsed time means the host is reachable.  A timeout at 25 s
  on both HEAD and GET, while DNS resolves, points to a blocked or heavily throttled
  route rather than a missing host.  That distinction decides whether the JADER fetch
  is worth retrying from this machine or has to be done elsewhere.""")
