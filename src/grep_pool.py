# -*- coding: utf-8 -*-
"""Grep the supplementary harvests for specific evidence threads."""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")


def load(tags):
    seen, out = {}, []
    for t in tags:
        p = os.path.join(RAW, f"epmc_{t}.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            recs = json.load(f)
        for k, r in recs.items():
            if k in seen:
                continue
            seen[k] = 1
            out.append(r)
    return out


def yr(r):
    try:
        return int(r.get("pubYear") or 0)
    except (TypeError, ValueError):
        return 0


def ct(r):
    try:
        return int(r.get("citedByCount") or 0)
    except (TypeError, ValueError):
        return 0


def main():
    tags = sys.argv[1].split(",")
    terms = sys.argv[2].split("|")
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    recs = load(tags)
    pats = [re.compile(t, re.I) for t in terms]
    scored = []
    for r in recs:
        blob = (r.get("title") or "") + " " + (r.get("abstractText") or "")
        hits = sum(1 for p in pats if p.search(blob))
        if hits == 0:
            continue
        scored.append((hits * 10 + (5 if yr(r) >= 2018 else 0) + min(ct(r), 300) / 20.0, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    print(f"### tags={tags} terms={terms} matched={len(scored)}")
    for sc, r in scored[:limit]:
        ab = re.sub(r"\s+", " ", (r.get("abstractText") or ""))
        print(f"\nPMID:{r.get('pmid')} DOI:{r.get('doi')} y{yr(r)} c{ct(r)} "
              f"| {r.get('journalTitle')}")
        print(f"  T: {re.sub(chr(10), ' ', r.get('title') or '')}")
        print(f"  A: {(r.get('authorString') or '')[:100]}")
        print(f"  AB: {ab[:1400]}")


if __name__ == "__main__":
    main()
