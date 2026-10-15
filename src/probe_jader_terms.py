# -*- coding: utf-8 -*-
"""
Find how ethambutol and the optic-nerve terms are written in JADER, by searching the data.

JADER stores drug names in Japanese and reaction terms as Japanese MedDRA/J preferred
terms.  There is no English column anywhere in the four tables, so nothing can be
matched without first establishing the Japanese strings.  Guessing them would be the
same mistake that cost time repeatedly on the FAERS side, so this searches the real
tables and reports what it actually finds.

Order of work:
    1. search drug202609.csv for candidate katakana spellings of ethambutol and the
       comparator antitubercular drugs, and report the exact strings present with their
       case counts
    2. dump the reaction terms whose Japanese text contains an ocular character, so the
       optic-nerve vocabulary can be read off rather than assumed
    3. report the distribution of the involvement code (医薬品の関与), which is JADER's
       equivalent of the FAERS role code and decides what the exposure definition is
"""
from __future__ import annotations

import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JADER = ROOT / "data" / "raw" / "jader"
ENC = "shift_jis"

#: first guess at the drug spellings, to be confirmed or corrected by what is found
DRUG_NEEDLES = {
    "ethambutol": ["エタンブトール"],
    "isoniazid": ["イソニアジド"],
    "rifampicin": ["リファンピシン", "リファンピシン"],
    "pyrazinamide": ["ピラジナミド"],
    "streptomycin": ["ストレプトマイシン"],
}
#: characters that only appear in ocular terms; used to dump the relevant vocabulary
OCULAR_CHARS = "眼視網膜虹彩角膜結膜涙瞳孔盲色覚視野緑内障白内障複視眼球"


def search_drugs() -> tuple[dict, collections.Counter]:
    """Count distinct case IDs per matching generic name."""
    path = JADER / "drug202609.csv"
    hits: dict[str, collections.Counter] = {k: collections.Counter()
                                            for k in DRUG_NEEDLES}
    involvement = collections.Counter()
    n = 0
    with path.open(encoding=ENC, errors="replace", newline="") as fh:
        rd = csv.reader(fh)
        header = next(rd)
        for row in rd:
            n += 1
            if len(row) < 6:
                continue
            involvement[row[3].strip()] += 1   # 医薬品の関与
            generic = row[4].strip()
            brand = row[5].strip()
            if not generic and not brand:
                continue
            for key, needles in DRUG_NEEDLES.items():
                for nd in needles:
                    if nd in generic or nd in brand:
                        hits[key][row[0].strip()] += 1
                        break
    print(f"  drug rows read: {n:,}")
    print()
    print("  involvement codes (医薬品の関与):")
    for k, v in involvement.most_common():
        print(f"      {k:16s} {v:>10,}")
    print()
    print("  matches:")
    for key, ctr in hits.items():
        if ctr:
            print(f"      {key:16s} {len(ctr):>7,} distinct cases   "
                  f"needles tried: {DRUG_NEEDLES[key]}")
        else:
            print(f"      {key:16s} NOT FOUND with {DRUG_NEEDLES[key]}")
    return hits, involvement


def dump_ocular_terms(limit: int = 260) -> None:
    """Every reaction term containing an ocular character, with its frequency."""
    path = JADER / "reac202609.csv"
    cnt = collections.Counter()
    n = 0
    with path.open(encoding=ENC, errors="replace", newline="") as fh:
        rd = csv.reader(fh)
        next(rd)
        for row in rd:
            n += 1
            if len(row) < 4:
                continue
            term = row[3].strip()
            if term and any(ch in term for ch in OCULAR_CHARS):
                cnt[term] += 1
    print(f"  reaction rows read: {n:,}")
    print(f"  distinct ocular-ish terms: {len(cnt):,}")
    print()
    for term, c in cnt.most_common(limit):
        print(f"      {c:>8,}  {term}")


print("=" * 100)
print("1. Drug names present in JADER")
print("=" * 100)
hits, involvement = search_drugs()

print()
print("=" * 100)
print("2. Ocular reaction vocabulary")
print("=" * 100)
dump_ocular_terms()
