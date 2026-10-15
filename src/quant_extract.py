# -*- coding: utf-8 -*-
"""v2 quantitative mining: proper sentence splitting (decimal-safe) + keyword targeting."""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DER = os.path.join(ROOT, "data", "derived")
os.makedirs(DER, exist_ok=True)

ETH_GROUPS = ["q1_optic_neuropathy", "q2_imaging", "q3_pharmacovigilance",
              "q4_mechanism", "q5_dose_risk", "q6_other_antiTB"]

# protect decimals / abbreviations before splitting
DEC = re.compile(r"(\d)\.(\d)")
ABBR = re.compile(r"\b(?:e\.g|i\.e|vs|Dr|Fig|No|approx|ca|mg|kg|etc|et al|yr|mo|wk)\.", re.I)


def split_sentences(blob):
    b = DEC.sub(r"\1<DOT>\2", blob)
    b = ABBR.sub(lambda m: m.group(0)[:-1] + "<DOT>", b)
    b = re.sub(r"<h4>|</h4>|<b>|</b>|<i>|</i>|&lt;|&gt;|&amp;", " ", b)
    parts = re.split(r"(?<=[a-z0-9\)\%\]])\.\s+(?=[A-Z(])", b)
    out = []
    for p in parts:
        p = p.replace("<DOT>", ".").strip()
        p = re.sub(r"\s+", " ", p)
        if p:
            out.append(p)
    return out


TOPICS = {
    "incidence_rate": [r"\bincidence\b", r"\bprevalence\b", r"\boccurred in\b",
                       r"\bdeveloped (?:EON|ON|optic)\b", r"\brisk of (?:EON|ON)\b"],
    "dose_threshold": [r"mg/kg", r"mg per kg", r"daily dose", r"dose[- ]dependent",
                       r"dose[- ]related", r"cumulative dose"],
    "risk_factors": [r"risk factor", r"renal", r"diabet", r"\bage\b", r"alcohol",
                     r"malnutri", r"zinc", r"copper", r"LHON", r"Leber",
                     r"polymorphism", r"CYP1A2", r"NAT2", r"body weight", r"genetic"],
    "recovery": [r"recover", r"improve", r"reversib", r"resolut", r"prognos",
                 r"final visual acuity", r"outcome"],
    "screening": [r"screen", r"monitor", r"baseline", r"follow[- ]up", r"surveillance",
                  r"recommend", r"guideline", r"color vision", r"colour vision",
                  r"visual evoked", r"OCT", r"perimetr"],
    "mechanism": [r"mitochondri", r"oxidative stress", r"glutamate", r"zinc",
                  r"copper", r"lysosom", r"autophag", r"ferroptosis", r"chelat",
                  r"complex I", r"apoptosis", r"BDNF", r"mTOR", r"ROS"],
}

NUMRE = re.compile(r"\d")


def load_all(groups):
    seen, out = set(), []
    for g in groups:
        p = os.path.join(RAW, f"epmc_{g}.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            recs = json.load(f)
        for r in recs.values():
            k = r.get("pmid") or r.get("id")
            if k in seen:
                continue
            seen.add(k)
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
    recs = load_all(ETH_GROUPS)
    print("ethambutol unique records:", len(recs))
    for topic, kws in TOPICS.items():
        pats = [re.compile(k, re.I) for k in kws]
        rows = []
        for r in recs:
            blob = (r.get("title") or "") + ". " + (r.get("abstractText") or "")
            if not blob.strip():
                continue
            for s in split_sentences(blob):
                if not NUMRE.search(s):
                    continue
                if len(s) < 40 or len(s) > 700:
                    continue
                if sum(1 for p in pats if p.search(s)) >= 1:
                    rows.append({
                        "pmid": r.get("pmid"), "doi": r.get("doi"),
                        "year": yr(r), "cites": ct(r),
                        "title": re.sub(r"\s+", " ", r.get("title") or "")[:120],
                        "sentence": s,
                        "score": sum(1 for p in pats if p.search(s)) * 3
                                 + (2 if yr(r) >= 2018 else 0)
                                 + min(ct(r), 200) / 40.0,
                    })
        rows.sort(key=lambda x: x["score"], reverse=True)
        # de-dup identical sentences
        seen, uniq = set(), []
        for row in rows:
            key = row["sentence"][:160].lower()
            if key in seen:
                continue
            seen.add(key)
            uniq.append(row)
        with open(os.path.join(DER, f"q2_{topic}.txt"), "w", encoding="utf-8") as f:
            for row in uniq:
                f.write(f"PMID:{row['pmid']} DOI:{row['doi']} y{row['year']} c{row['cites']} "
                        f"| {row['title']}\n    > {row['sentence']}\n\n")
        print(f"  {topic}: {len(uniq)} sentences")


if __name__ == "__main__":
    main()
