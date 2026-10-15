# -*- coding: utf-8 -*-
"""Herb selector v2: require retina/RGC/optic-nerve-specific evidence."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")

HERBS = {
    "枸杞子/LBP": [r"lycium barbarum", r"\bLBP\b", r"goji", r"wolfberry"],
    "菊花": [r"chrysanthemum", r"luteolin", r"apigenin"],
    "黄芪/黄芪甲苷": [r"astragaloside", r"astragalus", r"calycosin"],
    "丹参/丹参酮IIA": [r"tanshinone", r"salvia miltiorrhiza", r"salvianolic"],
    "葛根素": [r"puerarin", r"pueraria"],
    "银杏叶提取物": [r"ginkgo", r"EGb ?761", r"ginkgolide"],
    "灯盏花素": [r"breviscapine", r"scutellarin"],
    "川芎嗪": [r"ligustrazine", r"tetramethylpyrazine"],
    "石斛": [r"dendrobium", r"dendrobine"],
    "女贞子": [r"ligustrum lucidum", r"specnuezhenide"],
    "决明子": [r"cassia obtusifolia", r"cassia tora", r"semen cassiae", r"aurantio-obtusin"],
    "其他(红景天/黄芩/姜黄/白藜芦醇)": [r"salidroside", r"baicalin", r"curcumin", r"resveratrol",
                                        r"crocetin"],
}

# must appear in TITLE, or >=2 times in abstract
RETINA = re.compile(r"retin|optic nerve|ganglion cell|glaucoma|ocular|RGC|macul|"
                    r"photoreceptor|neuroprotect|eye\b|visual", re.I)
RETINA_STRONG = re.compile(r"retinal ganglion|optic nerve|glaucoma|retinopathy|retina|"
                           r"optic neuropath|photoreceptor|macul", re.I)
PATHWAY = re.compile(r"Nrf2|HO-1|PI3K|Akt|BDNF|TrkB|MAPK|ERK|JNK|p38|NF-?κB|AMPK|mTOR|TLR4|"
                     r"MyD88|Bcl-2|Bax|caspase|mitochondri|apoptos|autophag|oxidative stress|"
                     r"ROS\b|SOD\b|MDA\b|iNOS|COX-2|TNF-α|IL-6|VEGF|GSK-3|CREB|Sirt1|NLRP3|"
                     r"Keap1|NQO1|CAT\b|GPx", re.I)


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
    if re.search(r"\b(mice|mouse|murine|rat|rats|zebrafish|rabbit|in vivo)\b", blob, re.I):
        tags.append("动物")
    if re.search(r"cell line|cells were|in vitro|cultured|RGC-5|PC12|ARPE-19|MIO-M1|"
                 r"SH-SY5Y|primary retinal|iPSC", blob, re.I):
        tags.append("细胞")
    if re.search(r"patients|clinical trial|randomi[sz]ed|participants|human subjects|"
                 r"case series|cohort|volunteers", blob, re.I):
        tags.append("临床/人")
    return "+".join(tags) if tags else "未明确"


def main():
    files = ["epmc_t3_monomers.json", "epmc_t4_formulas.json", "epmc_t2_network_pharm.json",
             "epmc_s8_tcm_optic_extra.json"]
    recs = load(*files)
    out = [f"# pool size {len(recs)}\n"]
    for herb, pats in HERBS.items():
        compiled = [re.compile(p, re.I) for p in pats]
        hits = []
        for r in recs:
            title = r.get("title") or ""
            ab = r.get("abstractText") or ""
            blob = title + " " + ab
            if not any(p.search(blob) for p in compiled):
                continue
            # require retina-specific evidence
            strong_title = RETINA_STRONG.search(title)
            strong_n = len(RETINA_STRONG.findall(ab))
            if not strong_title and strong_n < 2:
                continue
            ti = sum(1 for p in compiled if p.search(title))
            sc = ti * 15 + (10 if strong_title else 0) + min(strong_n, 8) * 3
            sc += 8 if yr(r) >= 2018 else 0
            sc += min(ct(r), 200) / 15.0
            sc += 10 if PATHWAY.search(title + ab) else 0
            hits.append((sc, r, ab))
        hits.sort(key=lambda x: x[0], reverse=True)
        out.append(f"\n{'='*100}\n## {herb}  (matched {len(hits)})")
        for sc, r, ab in hits[:6]:
            clean = re.sub(r"<[^>]+>", " ", ab)
            sents = re.split(r"(?<=[a-z0-9\)%])\.\s+", clean)
            pw = [s for s in sents if PATHWAY.search(s)][:2]
            dose = [s for s in sents if re.search(
                r"\d+\s*(?:mg/kg|µg/ml|ug/ml|μg/mL|mg/mL|μM|uM|mM|mg/day|g/kg|mg·kg|µM)", s)][:2]
            ret = [s for s in sents if RETINA_STRONG.search(s)][:2]
            out.append(f"\n  PMID:{r.get('pmid')} DOI:{r.get('doi')} y{yr(r)} c{ct(r)} "
                       f"model={model_of(ab)}")
            out.append(f"  T: {re.sub(chr(10),' ', r.get('title') or '')[:190]}")
            for s in ret:
                out.append(f"  EYE> {re.sub(chr(10),' ',s)[:250]}")
            for s in dose:
                out.append(f"  DOSE> {re.sub(chr(10),' ',s)[:230]}")
            for s in pw:
                out.append(f"  PATH> {re.sub(chr(10),' ',s)[:230]}")
    with open(os.path.join(ROOT, "data", "derived", "herb_select2.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(out))
    print("written", len(out), "lines")


if __name__ == "__main__":
    main()
