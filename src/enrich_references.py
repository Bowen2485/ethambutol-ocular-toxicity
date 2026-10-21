# -*- coding: utf-8 -*-
"""Rebuild the reference list in Vancouver style from Europe PMC metadata.

The previous list carried authors, title and DOI but often no volume, issue or pages, and two
entries ran together.  Europe PMC is queried by DOI for the 18 references actually cited, and
each entry is rebuilt as

    Authors (first six, then et al.). Title. Journal. Year;Volume(Issue):Pages. doi:...

Entries without a DOI keep the text they had and are flagged in the output.

Writes manuscript/TADS_references.md, which src/build_tads_manuscript.py uses when present.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
text = (MAN / "TADS_manuscript.md").read_text(encoding="utf-8")
block = text[text.find("## References"):]
entries: dict[int, str] = {}
for m in re.finditer(r"^(\d{1,2})\.\s+(.+?)(?=\n\d{1,2}\.\s|\Z)", block, re.M | re.S):
    entries[int(m.group(1))] = " ".join(m.group(2).split())


def fetch(doi: str) -> dict | None:
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22"
           + urllib.parse.quote(doi) + "%22&format=json&resultType=core")
    try:
        with urllib.request.urlopen(url, timeout=30) as fh:
            payload = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"  network error for {doi}: {exc}")
        return None
    hits = payload.get("resultList", {}).get("result", [])
    return hits[0] if hits else None


def authors(rec: dict) -> str:
    names = [a.get("fullName") or a.get("lastName", "") for a in
             rec.get("authorList", {}).get("author", [])]
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) > 6:
        return ", ".join(names[:6]) + ", et al"
    return ", ".join(names)


out: list[str] = []
missing: list[int] = []
for n in sorted(entries):
    entry = entries[n]
    m = re.search(r"10\.\d{4,9}/[^\s;]+", entry)
    if not m:
        missing.append(n)
        out.append(f"{n}. {entry}")
        continue
    doi = m.group(0).rstrip(".")
    rec = fetch(doi)
    if not rec:
        missing.append(n)
        out.append(f"{n}. {entry}")
        continue
    journal = rec.get("journalInfo", {}).get("journal", {}).get("medlineAbbreviation") \
        or rec.get("journalTitle", "")
    year = rec.get("pubYear", "")
    vol = rec.get("journalInfo", {}).get("volume") or rec.get("journalVolume", "")
    issue = rec.get("journalInfo", {}).get("issue") or rec.get("issue", "")
    pages = rec.get("pageInfo", "")
    title = rec.get("title", "").rstrip(".")
    auth = authors(rec)
    bits = [f"{auth}. " if auth else "", f"{title}. ", f"{journal}. " if journal else ""]
    loc = year
    if vol:
        loc += f";{vol}"
        if issue:
            loc += f"({issue})"
        elif pages:
            loc += ":"
        if pages and issue:
            loc += f":{pages}"
    bits.append(loc + ". " if loc else "")
    bits.append(f"doi:{doi}.")
    out.append(f"{n}. " + "".join(bits).replace("..", ".").strip())
    print(f"  {n:2d}. {journal} {year};{vol}({issue}):{pages}")
    time.sleep(0.35)

(MAN / "TADS_references.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"\nwritten manuscript/TADS_references.md ({len(out)} entries; "
      f"no DOI, left unchanged: {missing})")
