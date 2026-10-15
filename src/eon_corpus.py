# -*- coding: utf-8 -*-
"""Build a curated ethambutol-ocular-toxicity corpus (title-level filter) and mine it."""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DER = os.path.join(ROOT, "data", "derived")

TITLE_MUST = re.compile(r"ethambutol|\bEMB\b|\bEON\b|\bETON\b", re.I)
TITLE_EYE = re.compile(r"optic|ocular|ophthalm|visual|vision|eye|retina|blind|colour|color|"
                       r"chiasm|papill|macul|screen|neuropath", re.I)

DEC = re.compile(r"(\d)\.(\d)")
ABBR = re.compile(r"\b(?:e\.g|i\.e|vs|Dr|Fig|No|approx|ca|mg|kg|etc|et al|yr|mo|wk)\.", re.I)


def split_sentences(blob):
    b = DEC.sub(r"\1<DOT>\2", blob)
    b = ABBR.sub(lambda m: m.group(0)[:-1] + "<DOT>", b)
    b = re.sub(r"<h4>|</h4>|<b>|</b>|<i>|</i>|&lt;|&gt;|&amp;|&nbsp;", " ", b)
    parts = re.split(r"(?<=[a-z0-9\)\%\]])\.\s+(?=[A-Z(])", b)
    out = []
    for p in parts:
        p = re.sub(r"\s+", " ", p.replace("<DOT>", ".")).strip()
        if p:
            out.append(p)
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


def load_corpus():
    seen, out = set(), []
    for path in sorted(glob.glob(os.path.join(RAW, "epmc_*.json"))):
        if path.endswith("search_meta.json") or path.endswith("supp_meta.json"):
            continue
        with open(path, encoding="utf-8") as f:
            recs = json.load(f)
        for r in recs.values():
            k = r.get("pmid") or r.get("id")
            if not k or k in seen:
                continue
            t = r.get("title") or ""
            if TITLE_MUST.search(t) and TITLE_EYE.search(t):
                seen.add(k)
                out.append(r)
    return out


PARAM_SETS = {
    "P1_incidence": [r"incidence", r"prevalence", r"proportion", r"develop"],
    "P2_dose": [r"mg/kg", r"mg per kg", r"dose", r"dosage"],
    "P3_latency": [r"month", r"week", r"year", r"duratio", r"onset", r"latenc", r"exposure"],
    "P4_riskfactors": [r"risk factor", r"renal", r"kidney", r"diabet", r"age", r"alcohol",
                       r"malnutri", r"zinc", r"copper", r"LHON", r"Leber", r"gene",
                       r"polymorph", r"body weight", r"smok", r"hypertens"],
    "P5_recovery": [r"recover", r"improve", r"reversib", r"prognos", r"final", r"outcome",
                    r"resolut"],
    "P6_screening": [r"screen", r"monitor", r"baseline", r"follow", r"recommend", r"guideline",
                     r"OCT", r"evoked", r"perimetr", r"Ishihara", r"acuity"],
    "P7_outcome_oct": [r"RNFL", r"GCIPL", r"ganglion", r"nerve fibre", r"nerve fiber",
                       r"thickness", r"microm", r"µm", r"um\b"],
}


def main():
    corpus = load_corpus()
    print("curated EON corpus size:", len(corpus))
    with open(os.path.join(DER, "eon_corpus.json"), "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=1)

    # a readable index
    with open(os.path.join(DER, "eon_corpus_index.txt"), "w", encoding="utf-8") as f:
        for r in sorted(corpus, key=lambda x: (yr(x), ct(x)), reverse=True):
            f.write(f"PMID:{r.get('pmid')} DOI:{r.get('doi')} y{yr(r)} c{ct(r)}\n")
            f.write(f"  T: {re.sub(chr(10), ' ', r.get('title') or '')}\n")
            f.write(f"  A: {(r.get('authorString') or '')[:120]}\n")
            f.write(f"  J: {r.get('journalTitle')}\n\n")

    for tag, kws in PARAM_SETS.items():
        pats = [re.compile(k, re.I) for k in kws]
        num = re.compile(r"\d")
        rows, seen = [], set()
        for r in corpus:
            blob = (r.get("title") or "") + ". " + (r.get("abstractText") or "")
            for s in split_sentences(blob):
                if not (30 <= len(s) <= 800) or not num.search(s):
                    continue
                hits = sum(1 for p in pats if p.search(s))
                if hits < 2:
                    continue
                key = s[:140].lower()
                if key in seen:
                    continue
                seen.add(key)
                rows.append((hits * 3 + (2 if yr(r) >= 2018 else 0)
                             + min(ct(r), 200) / 40.0, r, s))
        rows.sort(key=lambda x: x[0], reverse=True)
        with open(os.path.join(DER, f"par_{tag}.txt"), "w", encoding="utf-8") as f:
            for sc, r, s in rows:
                f.write(f"PMID:{r.get('pmid')} DOI:{r.get('doi')} y{yr(r)} c{ct(r)} "
                        f"| {(r.get('title') or '')[:110]}\n    > {s}\n\n")
        print(f"  {tag}: {len(rows)}")


if __name__ == "__main__":
    main()
