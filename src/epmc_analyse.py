# -*- coding: utf-8 -*-
"""Rank harvested Europe PMC records and mine quantitative sentences.

Outputs compact, reviewable digests to data/derived/.
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DER = os.path.join(ROOT, "data", "derived")
os.makedirs(DER, exist_ok=True)

CORE_TERMS = ["ethambutol", "optic neuropath", "ocular", "visual", "retina", "optic nerve",
              "colour vision", "color vision", "visual acuity"]

# ---- quantitative patterns -------------------------------------------------
NUM = r"\d+(?:\.\d+)?"
PATTERNS = {
    "dose_mg_kg": re.compile(rf"[^.]{{0,140}}{NUM}\s*(?:mg/kg|mg kg|mg per kg)[^.]{{0,140}}\.", re.I),
    "percent": re.compile(rf"[^.]{{0,160}}{NUM}\s*(?:%|per cent|percent)[^.]{{0,160}}\.", re.I),
    "months": re.compile(rf"[^.]{{0,140}}{NUM}\s*(?:months?|weeks?|years?)[^.]{{0,140}}\.", re.I),
    "incidence": re.compile(
        r"[^.]{0,180}(?:incidence|prevalence|risk of|occurred in|developed in|rate of)"
        r"[^.]{0,200}\.", re.I),
    "recovery": re.compile(
        r"[^.]{0,180}(?:recover|improve|reversib|resolut|prognos)[^.]{0,200}\.", re.I),
    "screening": re.compile(
        r"[^.]{0,180}(?:screen|monitor|baseline|follow-up|surveillance|recommend)"
        r"[^.]{0,200}\.", re.I),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def year(rec):
    try:
        return int(rec.get("pubYear") or 0)
    except (TypeError, ValueError):
        return 0


def cites(rec):
    try:
        return int(rec.get("citedByCount") or 0)
    except (TypeError, ValueError):
        return 0


def text(rec):
    return ((rec.get("title") or "") + " " + (rec.get("abstractText") or "")).lower()


def ptype(rec):
    pts = rec.get("pubTypeList", {}).get("pubType", []) if rec.get("pubTypeList") else []
    return "; ".join(pts)


def relevance(rec, extra=()):
    t = text(rec)
    title = (rec.get("title") or "").lower()
    s = 0
    for term in CORE_TERMS:
        if term in title:
            s += 6
        elif term in t:
            s += 2
    for term in extra:
        if term in title:
            s += 5
        elif term in t:
            s += 2
    ab = rec.get("abstractText") or ""
    if len(ab) > 400:
        s += 3
    if year(rec) >= 2018:
        s += 3
    if year(rec) >= 2022:
        s += 2
    if re.search(r"\b(review|guideline|cohort|randomi|meta-analys|systematic|survey|"
                 r"case series|retrospective|prospective|nationwide)\b", t):
        s += 3
    s += min(cites(rec), 300) / 20.0
    return s


def fmt_authors(rec, n=3):
    a = rec.get("authorString") or ""
    parts = [p.strip() for p in a.split(",") if p.strip()]
    if not parts:
        return "未署名"
    if len(parts) <= n:
        return ", ".join(parts)
    return ", ".join(parts[:n]) + ", et al."


def ident(rec):
    bits = []
    if rec.get("pmid"):
        bits.append(f"PMID: {rec['pmid']}")
    if rec.get("doi"):
        bits.append(f"DOI: {rec['doi']}")
    return " / ".join(bits) if bits else "无 PMID/DOI"


def clean(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    s = s.replace("|", "/")
    return s


def main():
    groups = {}
    for path in sorted(glob.glob(os.path.join(RAW, "epmc_*.json"))):
        name = os.path.basename(path)[5:-5]
        if name == "search_meta":
            continue
        recs = load(path)
        groups[name] = list(recs.values())

    summary = {}
    for name, recs in groups.items():
        ranked = sorted(recs, key=relevance, reverse=True)
        summary[name] = {"total_harvested": len(recs),
                         "with_abstract": sum(1 for r in recs if r.get("abstractText")),
                         "with_pmid": sum(1 for r in recs if r.get("pmid")),
                         "since_2018": sum(1 for r in recs if year(r) >= 2018)}
        lines = [f"# {name}  (n={len(recs)})", ""]
        for i, r in enumerate(ranked[:90], 1):
            lines.append(f"[{i}] score={relevance(r):.1f} cites={cites(r)} "
                         f"year={year(r)} type={ptype(r)[:60]}")
            lines.append(f"    AUTH: {fmt_authors(r)}")
            lines.append(f"    TITLE: {clean(r.get('title'))}")
            lines.append(f"    JRNL: {clean(r.get('journalTitle'))} | {ident(r)}")
            ab = clean(r.get("abstractText"))
            lines.append(f"    ABS: {ab[:900]}")
            lines.append("")
        with open(os.path.join(DER, f"rank_{name}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # ---- quantitative mining over ethambutol groups ------------------------
    eth = []
    for name in ("q1_optic_neuropathy", "q2_imaging", "q3_pharmacovigilance",
                 "q4_mechanism", "q5_dose_risk", "q6_other_antiTB"):
        eth.extend(groups.get(name, []))
    seen = set()
    uniq = []
    for r in eth:
        k = r.get("pmid") or r.get("id")
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    eth = uniq

    quant = {}
    for key, pat in PATTERNS.items():
        rows = []
        for r in sorted(eth, key=relevance, reverse=True):
            blob = clean((r.get("title") or "") + ". " + (r.get("abstractText") or ""))
            if not blob:
                continue
            hits = pat.findall(blob)
            for h in hits[:4]:
                h = h.strip()
                if len(h) < 25:
                    continue
                rows.append({"pmid": r.get("pmid"), "doi": r.get("doi"),
                             "year": year(r), "cites": cites(r),
                             "title": clean(r.get("title"))[:110],
                             "sentence": h})
        quant[key] = rows
        with open(os.path.join(DER, f"quant_{key}.txt"), "w", encoding="utf-8") as f:
            for row in rows[:400]:
                f.write(f"PMID:{row['pmid']} y{row['year']} c{row['cites']} | {row['title']}\n")
                f.write(f"    > {row['sentence']}\n\n")

    with open(os.path.join(DER, "group_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("unique ethambutol records:", len(eth))
    for k, v in quant.items():
        print(f"  quant_{k}: {len(v)} sentences")


if __name__ == "__main__":
    main()
