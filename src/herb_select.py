# -*- coding: utf-8 -*-
"""For each TCM herb/compound, select the best supporting records compactly."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")

HERBS = {
    "枸杞子/LBP": [r"lycium barbarum", r"\bLBP\b", r"goji", r"wolfberry",
                   r"lycii fructus", r"zeaxanthin"],
    "菊花": [r"chrysanthemum", r"luteolin", r"apigenin", r"chlorogenic acid.*chrysan"],
    "黄芪/黄芪甲苷": [r"astragaloside", r"astragalus", r"calycosin", r"formononetin"],
    "丹参/丹参酮IIA": [r"tanshinone", r"salvia miltiorrhiza", r"salvianolic", r"danshen"],
    "葛根素": [r"puerarin", r"pueraria"],
    "银杏叶提取物": [r"ginkgo", r"EGb ?761", r"ginkgolide", r"bilobalide"],
    "灯盏花素": [r"breviscapine", r"scutellarin", r"erigeron"],
    "川芎嗪": [r"ligustrazine", r"tetramethylpyrazine", r"\bTMP\b"],
    "石斛": [r"dendrobium", r"dendrobine"],
    "女贞子": [r"ligustrum lucidum", r"specnuezhenide", r"oleanolic acid"],
    "决明子": [r"cassia obtusifolia", r"cassia tora", r"semen cassiae", r"aurantio-obtusin",
               r"cassiae"],
    "红景天/其他": [r"salidroside", r"rhodiola", r"baicalin", r"curcumin", r"resveratrol",
                    r"crocetin", r"lycopene"],
}

EYE = re.compile(r"retina|retinal|optic nerve|ganglion cell|glaucoma|ocular|eye|vision|"
                 r"neuroprotect|macul|photoreceptor|RGC", re.I)
PATHWAY = re.compile(r"Nrf2|HO-1|PI3K|Akt|BDNF|TrkB|MAPK|ERK|JNK|p38|NF-?κB|AMPK|mTOR|"
                     r"TLR4|MyD88|Bcl-2|Bax|caspase|mitochondri|apoptosis|autophag|oxidative stress|"
                     r"ROS|SOD|MDA|iNOS|COX-2|TNF-α|IL-6|VEGF|GSK-3|CREB|Sirt1|NLRP3",
                     re.I)


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


def load(*files):
    out = {}
    for f in files:
        p = os.path.join(RAW, f)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for k, r in json.load(fh).items():
                out.setdefault(k, r)
    return list(out.values())


def model_of(blob):
    tags = []
    if re.search(r"\b(mice|mouse|murine|rat|rats|zebrafish|rabbit)\b", blob, re.I):
        tags.append("动物")
    if re.search(r"cell line|cells were|in vitro|cultured|RGC-5|PC12|ARPE-19|MIO-M1|"
                 r"SH-SY5Y|primary retinal", blob, re.I):
        tags.append("细胞")
    if re.search(r"patients|clinical trial|randomi[sz]ed|participants|human subjects|"
                 r"case series|cohort", blob, re.I):
        tags.append("临床/人")
    return "+".join(tags) if tags else "未明确"


def main():
    recs = load("epmc_t3_monomers.json", "epmc_t4_formulas.json",
                "epmc_t2_network_pharm.json", "epmc_s8_tcm_optic_extra.json")
    print(f"# pool size {len(recs)}\n")
    for herb, pats in HERBS.items():
        compiled = [re.compile(p, re.I) for p in pats]
        hits = []
        for r in recs:
            title = r.get("title") or ""
            ab = r.get("abstractText") or ""
            blob = title + " " + ab
            if not any(p.search(blob) for p in compiled):
                continue
            if not EYE.search(blob):
                continue
            ti = sum(1 for p in compiled if p.search(title))
            sc = ti * 12 + (8 if yr(r) >= 2018 else 0) + min(ct(r), 200) / 15.0
            sc += 6 if PATHWAY.search(ab) else 0
            hits.append((sc, r, ab))
        hits.sort(key=lambda x: x[0], reverse=True)
        print(f"\n{'='*100}\n## {herb}  (matched {len(hits)})")
        for sc, r, ab in hits[:7]:
            sents = re.split(r"(?<=[a-z0-9\)])\.\s+", re.sub(r"<[^>]+>", " ", ab))
            pw = [s for s in sents if PATHWAY.search(s)][:2]
            dose = [s for s in sents if re.search(r"\d+\s*(?:mg/kg|µg/ml|ug/ml|μg/mL|mg/mL|"
                                                  r"μM|uM|mM|mg/day|g/kg|mg·kg)", s)][:2]
            print(f"\n  PMID:{r.get('pmid')} DOI:{r.get('doi')} y{yr(r)} c{ct(r)} "
                  f"model={model_of(ab)}")
            print(f"  T: {re.sub(chr(10),' ', r.get('title') or '')[:200]}")
            for s in dose:
                print(f"  DOSE> {re.sub(chr(10),' ',s)[:260]}")
            for s in pw:
                print(f"  PATH> {re.sub(chr(10),' ',s)[:260]}")


if __name__ == "__main__":
    main()
