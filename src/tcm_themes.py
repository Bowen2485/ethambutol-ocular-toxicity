# -*- coding: utf-8 -*-
"""Select TCM optic-neuropathy / acupuncture / formula / network-pharmacology records."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")

THEMES = {
    "针灸-视神经/青光眼": {
        "files": ["epmc_t1_tcm_optic.json", "epmc_s8_tcm_optic_extra.json"],
        "must": [r"acupunctur|electroacupunctur|acupoint|electro-acupunctur|acupuncture"],
        "eye": [r"optic nerve|optic neuropath|glaucoma|retinal ganglion|visual field|"
                r"optic atrophy|visual acuity|retina"],
    },
    "中药复方-视神经/青光眼/视网膜": {
        "files": ["epmc_t1_tcm_optic.json", "epmc_t4_formulas.json"],
        "must": [r"decoction|granule|formula|recipe|pill|fufang|tang\b|wan\b|"
                 r"traditional Chinese medicine|herbal"],
        "eye": [r"optic nerve|optic neuropath|glaucoma|retinal ganglion|optic atrophy|"
                r"retinopathy|visual field|retina"],
    },
    "网络药理学-眼科方药": {
        "files": ["epmc_t2_network_pharm.json", "epmc_t4_formulas.json"],
        "must": [r"network pharmacology|molecular docking|TCMSP|systems pharmacology"],
        "eye": [r"retina|retinopathy|glaucoma|optic nerve|macular|eye|ocular|visual"],
    },
}


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


def load(files):
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
    if re.search(r"\b(mice|mouse|murine|rat|rats|rabbit|zebrafish|in vivo)\b", blob, re.I):
        tags.append("动物")
    if re.search(r"cell line|cells were|in vitro|cultured|RGC-5|PC12|ARPE-19|MIO-M1|"
                 r"SH-SY5Y|iPSC", blob, re.I):
        tags.append("细胞")
    if re.search(r"patients|clinical trial|randomi[sz]ed|participants|human subjects|"
                 r"case series|cohort|volunteers|eyes of", blob, re.I):
        tags.append("临床/人")
    return "+".join(tags) if tags else "未明确"


def main():
    lines = []
    for theme, cfg in THEMES.items():
        recs = load(cfg["files"])
        must = [re.compile(p, re.I) for p in cfg["must"]]
        eye = [re.compile(p, re.I) for p in cfg["eye"]]
        hits = []
        for r in recs:
            title = r.get("title") or ""
            ab = r.get("abstractText") or ""
            blob = title + " " + ab
            if not any(p.search(blob) for p in must):
                continue
            if not any(p.search(blob) for p in eye):
                continue
            sc = sum(1 for p in must if p.search(title)) * 12
            sc += sum(1 for p in eye if p.search(title)) * 8
            sc += sum(1 for p in eye if p.search(ab)) * 2
            sc += 8 if yr(r) >= 2018 else 0
            sc += min(ct(r), 150) / 15.0
            hits.append((sc, r, ab))
        hits.sort(key=lambda x: x[0], reverse=True)
        lines.append(f"\n{'#'*100}\n# {theme}   (matched {len(hits)})\n")
        for sc, r, ab in hits[:22]:
            clean = re.sub(r"<[^>]+>", " ", ab)
            clean = re.sub(r"\s+", " ", clean)
            lines.append(f"\nPMID:{r.get('pmid')} DOI:{r.get('doi')} y{yr(r)} c{ct(r)} "
                         f"model={model_of(ab)} jrnl={r.get('journalTitle')}")
            lines.append(f"  T: {(r.get('title') or '')[:200]}")
            lines.append(f"  A: {(r.get('authorString') or '')[:90]}")
            lines.append(f"  AB: {clean[:1000]}")
    with open(os.path.join(ROOT, "data", "derived", "tcm_themes.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("written", len(lines), "lines")


if __name__ == "__main__":
    main()
