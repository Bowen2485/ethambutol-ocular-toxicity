# -*- coding: utf-8 -*-
"""
Establish what the peer papers actually did to obtain GeneCards data, and what GeneCards
actually offers.

The question being answered
    Two of the four comparator papers assemble disease targets from GeneCards and DisGeNET.
    I have been assuming they called an API, and that a GeneCards key would let this
    manuscript do the same.  Neither assumption has been checked, and the first probe of
    genecards.org returned 403, which says what a bare request gets and not what the resource
    provides.

What is checked
    First, the two papers.  Their methods sections are read for the sentence that describes
    how the GeneCards set was obtained, because a paper that filtered by relevance score used
    the web interface and a paper that queried an endpoint used the API, and those are
    different provenance claims to make in a manuscript.

    Second, the endpoints.  GeneCards proper is offered by the Weizmann Institute with a
    licence, and the same group publishes GeneCards Suite and the MalaCards and GeneALaCart
    tools, so the paths that exist are not only genecards.org.  Each is requested once and the
    reply inspected for data rather than for a status code.

No credentials are used: the point is to learn what is reachable and what is gated.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIT = ROOT / "docs" / "literature_peers" / "text"
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

print("=" * 100)
print("1. What the peer papers wrote about obtaining GeneCards data")
print("=" * 100)

for key in ("ang", "PMID42379941", "PLOSONE_2026_Leukotriene-EGPA"):
    p = LIT / f"{key}.xml"
    if p.exists():
        body = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
    else:
        p = LIT / f"{key}.txt"
        if not p.exists():
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"\s+", " ", body)
    hits = []
    for m in re.finditer(r"GeneCards", body):
        s = max(0, m.start() - 260)
        e = min(len(body), m.end() + 260)
        hits.append(body[s:e].strip())
    seen = set()
    print(f"\n  {key}: {len(hits)} mention(s)")
    for h in hits[:3]:
        # keep the sentence around the mention
        frag = h.replace("  ", " ")
        if frag[:80] in seen:
            continue
        seen.add(frag[:80])
        print(f"      ...{frag}...")

print()
print("=" * 100)
print("2. What GeneCards endpoints answer")
print("=" * 100)
UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
      "Accept": "application/json, text/html, */*"}


def probe(label: str, url: str, timeout: int = 25) -> dict:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            body = fh.read(200_000).decode("utf-8", "replace")
            code = fh.status
    except urllib.error.HTTPError as e:
        try:
            body = e.read(4000).decode("utf-8", "replace")
        except Exception:
            body = ""
        code = e.code
    except Exception as e:  # noqa: BLE001
        body, code = f"{type(e).__name__}: {str(e)[:90]}", None
    html = "<!doctype html" in body[:400].lower() or "<html" in body[:400].lower()
    is_json = body.lstrip().startswith(("{", "["))
    return {"label": label, "url": url, "status": code, "bytes": len(body),
            "html": html, "json": is_json, "sample": body[:170].replace("\n", " ")}


ENDPOINTS = [
    ("GeneCards gene page", "https://www.genecards.org/cgi-bin/carddisp.pl?gene=TP53"),
    ("GeneCards search API path", "https://www.genecards.org/api/v1/genes/TP53"),
    ("GeneCards suggestions", "https://www.genecards.org/api/v1/suggest?q=TP53"),
    ("GeneALaCart", "https://genealacart.genecards.org/"),
    ("GeneCards Suite", "https://www.genecards.org/Suite/"),
    ("MalaCards disease page", "https://www.malacards.org/card/optic_atrophy"),
    ("MalaCards API path", "https://www.malacards.org/api/v1/diseases/optic_atrophy"),
    ("GeneCards robots", "https://www.genecards.org/robots.txt"),
]

rows = []
for label, url in ENDPOINTS:
    r = probe(label, url)
    rows.append(r)
    kind = "JSON" if r["json"] else ("HTML" if r["html"] else "other")
    print(f"  {str(r['status']):>5}  {kind:5s}  {len(r['sample']):>3d}ch  {label:32s} "
          f"{r['sample'][:72]}")

# robots.txt tells whether automated access is contemplated at all
robots = next((r for r in rows if r["label"].endswith("robots")), None)
if robots and not robots["html"] and robots["status"] == 200:
    print()
    print("  robots.txt, which says what automated access is permitted:")
    for line in robots["sample"].split(chr(92) + "n")[:6]:
        print(f"      {line}")

(OUT / "genecards_probe.json").write_text(
    json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

print()
print("=" * 100)
print("3. Reading")
print("=" * 100)
json_ok = [r for r in rows if r["json"] and r["status"] == 200]
print(f"  endpoints returning JSON with status 200: {len(json_ok)}")
for r in json_ok:
    print(f"      {r['label']}")
print("""  A 403 on the gene page means a browser-like request is refused; it does not by itself
  say whether a licensed API exists.  The decision rests on what the peer papers describe,
  which is printed above, and on whether any endpoint here returns data.""")
print(f"\n  written: {(OUT / 'genecards_probe.json').relative_to(ROOT)}")
