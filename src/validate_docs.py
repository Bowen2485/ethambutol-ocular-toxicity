# -*- coding: utf-8 -*-
"""Validate the two deliverables:
   * every PMID cited must exist in the Europe PMC harvest (or resolve live)
   * every DOI cited must match the recorded DOI
   * report line counts and quote sanity
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DOCS = os.path.join(ROOT, "docs")


def load_db():
    out = {}
    for p in glob.glob(os.path.join(RAW, "epmc_*.json")):
        if p.endswith("meta.json"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, dict):
            for k, r in d.items():
                if isinstance(r, dict):
                    pm = str(r.get("pmid") or k)
                    out.setdefault(pm, r)
    return out


def main():
    db = load_db()
    jmap = json.load(open(os.path.join(ROOT, "data", "derived", "journal_map.json"),
                         encoding="utf-8"))
    print(f"harvest DB records: {len(db)}  |  journal_map: {len(jmap)}\n")
    ok = True
    for name in ("literature_ethambutol_ocular.md", "tcm_optic_neuropathy_background.md"):
        path = os.path.join(DOCS, name)
        if not os.path.exists(path):
            print(f"!! MISSING {path}")
            ok = False
            continue
        text = open(path, encoding="utf-8").read()
        lines = text.splitlines()
        pmids = sorted(set(re.findall(r"PMID:\s*(\d{4,9})", text)))
        dois = sorted(set(re.findall(r"DOI:\s*(10\.\d{4,9}/[^\s|,\]]+)", text)))
        print("=" * 78)
        print(f"FILE: {path}")
        print(f"  lines           : {len(lines)}")
        print(f"  chars           : {len(text)}")
        print(f"  unique PMIDs    : {len(pmids)}")
        print(f"  unique DOIs     : {len(dois)}")
        missing = [p for p in pmids if p not in db and p not in jmap]
        print(f"  PMIDs NOT in harvest/journal_map: {missing if missing else 'none'}")
        if missing:
            ok = False
        # DOI consistency: compare against the whole table row containing the PMID
        bad_doi = []
        for p in pmids:
            rec = db.get(p) or jmap.get(p)
            true = (rec or {}).get("doi")
            if not true:
                continue
            # find all DOI strings that appear on the same line as this PMID
            for line in lines:
                if f"PMID: {p}" in line or f"PMID:{p}" in line:
                    found = re.findall(r"DOI:\s*(10\.\d{4,9}/[^\s|,\]]+)", line)
                    for f in found:
                        if f.rstrip(".") != true.rstrip("."):
                            bad_doi.append((p, f, true))
        print(f"  DOI mismatches  : {bad_doi if bad_doi else 'none'}")
        if bad_doi:
            ok = False
        # index coverage
        idx_start = text.rfind("引用记录索引")
        if idx_start > 0:
            tail = text[idx_start:]
            idx_pmids = set(re.findall(r"\|\s*(\d{4,9})\s*\|", tail))
            absent = [p for p in pmids if p not in idx_pmids]
            print(f"  cited PMIDs absent from index table: {absent if absent else 'none'}")
        # quote sanity
        odd = [i + 1 for i, l in enumerate(lines)
               if l.count('"') % 2 == 1 and '"' in l]
        print(f"  lines with odd ASCII-quote count: {len(odd)} {odd[:8]}")
        # 未检索到 occurrences
        print(f"  '未检索到' 出现次数: {text.count('未检索到')}")
        # check for stray replacement markers
        for marker in ("<DOT>", "{{", "}}", "None |"):
            if marker in text:
                print(f"  !! stray marker '{marker}' found {text.count(marker)} times")
                ok = False
    print("=" * 78)
    print("VALIDATION:", "PASS" if ok else "ISSUES FOUND")


if __name__ == "__main__":
    main()
