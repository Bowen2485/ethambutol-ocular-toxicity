# -*- coding: utf-8 -*-
"""
Verify the two additional PMIDs cited in the Discussion and write them into the
verified-reference store, then report which of the 25 verified references are not
yet cited inline anywhere in the assembled manuscript.
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
MAN = ROOT / "manuscript"

EXTRA = ["39979502", "40444310"]

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 research/1.0"}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def fetch(pmid: str) -> dict | None:
    url = (f"{EPMC}?query=EXT_ID:{pmid}%20AND%20SRC:MED&format=json"
           f"&resultType=core&pageSize=1")
    for a in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
            res = d.get("resultList", {}).get("result", [])
            return res[0] if res else None
        except Exception:  # noqa: BLE001
            time.sleep(2 * (a + 1))
    return None


def strip_tags(t: str) -> str:
    t = re.sub(r"<[^>]+>", "", t or "")
    return re.sub(r"\s+", " ", t.replace("&lt;", "<").replace("&gt;", ">")).strip()


def main() -> int:
    store = json.loads((DER / "references_verified.json").read_text(encoding="utf-8"))
    have = {r["pmid"] for r in store}
    added = 0
    for pmid in EXTRA:
        if pmid in have:
            continue
        rec = fetch(pmid)
        if rec is None:
            print(f"  [{pmid}] NOT FOUND - remove the citation from the text")
            continue
        entry = {
            "pmid": pmid, "verified": True,
            "title": strip_tags(rec.get("title", "")),
            "journal": (rec.get("journalInfo", {}) or {}).get("journal", {}).get("title", ""),
            "year": rec.get("pubYear", ""),
            "authors": rec.get("authorString", ""),
            "doi": rec.get("doi", ""),
            "first_author": (rec.get("authorString", "") or "").split(",")[0].strip(),
            "draft": "", "author_matches": False, "title_matches": False,
            "suggested": "",
        }
        store.append(entry)
        have.add(pmid)
        added += 1
        print(f"  [{pmid}] added: {entry['year']} {entry['journal'][:38]} - "
              f"{entry['title'][:80]}")
        time.sleep(0.4)
    (DER / "references_verified.json").write_text(
        json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[store] {len(store)} verified references ({added} added)")

    # which references are still not cited inline?
    full = (MAN / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
    cited = {int(x) for x in re.findall(r"\[(\d{1,2})(?:[,\-]\d{1,2})*\]", full)}
    cited |= {int(n) for m in re.findall(r"\[([\d,]+)\]", full)
              for n in m.split(",") if n.isdigit()}
    uncited = sorted(set(range(1, len(store) + 1)) - cited)
    print(f"[citations] numbers used inline: {sorted(cited)}")
    print(f"[citations] NOT yet cited inline: {uncited}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
