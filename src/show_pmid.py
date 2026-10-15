# -*- coding: utf-8 -*-
"""Print full records for a list of PMIDs, from all harvests combined."""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")


def load_all():
    out = {}
    for p in glob.glob(os.path.join(RAW, "epmc_*.json")):
        if p.endswith("meta.json"):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, dict):
            for k, r in d.items():
                if isinstance(r, dict) and ("title" in r or "pmid" in r):
                    out.setdefault(str(r.get("pmid") or k), r)
    return out


def main():
    pmids = [x.strip() for x in sys.argv[1].split(",") if x.strip()]
    db = load_all()
    print(f"# db={len(db)} requested={len(pmids)}")
    for pm in pmids:
        r = db.get(pm)
        if not r:
            print(f"\n### PMID:{pm}  >>> NOT FOUND in harvest <<<")
            continue
        ab = re.sub(r"<[^>]+>", " ", r.get("abstractText") or "")
        ab = re.sub(r"\s+", " ", ab).strip()
        print(f"\n### PMID:{pm} | DOI:{r.get('doi')} | {r.get('pubYear')} | "
              f"cites={r.get('citedByCount')}")
        print(f"T: {r.get('title')}")
        print(f"A: {(r.get('authorString') or '')[:130]}")
        print(f"J: {r.get('journalTitle')}")
        print(f"AB: {ab}")


if __name__ == "__main__":
    main()
