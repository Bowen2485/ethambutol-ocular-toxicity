# -*- coding: utf-8 -*-
"""Targeted supplementary Europe PMC searches for specific quantitative parameters."""
import json
import os
import ssl
import time
import urllib.parse
import urllib.request

CTX = ssl._create_unverified_context()
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
HEADERS = {"User-Agent": "Mozilla/5.0"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw")
os.makedirs(OUT, exist_ok=True)

KEEP = ["id", "source", "pmid", "pmcid", "doi", "title", "authorString", "journalTitle",
        "pubYear", "citedByCount", "abstractText", "pubTypeList", "firstPublicationDate"]

QUERIES = {
    "s1_classic_dose": [
        'ethambutol AND optic AND (dosage OR toxicity) AND (PUB_YEAR:[1960 TO 1990])',
        'ethambutol AND ("retrobulbar neuritis" OR "ocular toxicity") AND (PUB_YEAR:[1960 TO 1995])',
        'ethambutol AND "dose" AND ("ocular toxicity" OR "optic neuritis") AND (PUB_YEAR:[1970 TO 2000])',
    ],
    "s2_genetics": [
        'ethambutol AND (CYP1A2 OR NAT2 OR polymorphism OR "genetic susceptibility" OR '
        '"gene polymorphism") AND (optic OR ocular OR visual)',
        'ethambutol AND (LHON OR "Leber hereditary optic neuropathy" OR mtDNA OR OPA1)',
        'ethambutol AND ("mitochondrial DNA" OR haplogroup) AND (optic neuropathy OR retinal)',
    ],
    "s3_metals": [
        'ethambutol AND (zinc OR copper OR "metal" OR chelat*) AND '
        '("retinal ganglion" OR "optic nerve" OR neurotoxicity OR "zinc toxicity")',
        'ethambutol AND (glutamate OR "excitotoxicity" OR "NMDA") AND (retina OR "optic nerve")',
        'ethambutol AND (lysosom* OR autophagy OR "ferroptosis" OR "oxidative stress") AND '
        '(retina OR "retinal ganglion" OR "optic nerve")',
        'ethambutol AND (mitochondrial OR "complex I" OR "respiratory chain") AND '
        '("retinal ganglion" OR "optic nerve" OR retina)',
    ],
    "s4_prognosis": [
        'ethambutol AND ("visual recovery" OR "visual prognosis" OR "prognostic factor" OR '
        '"final visual acuity") AND "optic neuropathy"',
        'ethambutol AND "optic neuropathy" AND (discontinuation OR "stopping" OR withdrawal) '
        'AND (recovery OR outcome OR prognosis)',
        'ethambutol AND (treatment OR corticosteroid OR "vitamin" OR neuroprotect*) AND '
        '"optic neuropathy" AND (management OR therapy OR outcome)',
    ],
    "s5_screening": [
        'ethambutol AND ("vision screening" OR "ophthalmologic monitoring" OR '
        '"visual monitoring") AND (tuberculosis OR recommendation OR guideline)',
        'ethambutol AND ("color vision" OR "colour vision" OR "visual acuity") AND '
        '(baseline OR "at baseline") AND (recommend* OR monitor* OR frequency)',
        'ethambutol AND ("optic neuropathy") AND (WHO OR "World Health Organization" OR '
        '"national program*" OR "treatment guideline" OR "package insert")',
    ],
    "s6_faers_pv": [
        'ethambutol AND (FAERS OR VigiBase OR "EudraVigilance" OR "adverse event reporting system")',
        'ethambutol AND ("disproportionate" OR "disproportionality" OR "reporting odds ratio" OR '
        '"pharmacovigilance signal") AND (optic OR eye OR ocular OR vision)',
        'ethambutol AND ("real-world" OR "post-marketing" OR "postmarketing") AND '
        '(optic neuropathy OR visual)',
    ],
    "s7_other_drugs": [
        'linezolid AND ("optic neuropathy" OR "optic nerve")',
        'isoniazid AND (optic OR ocular) AND (toxicity OR neuropathy)',
        'clofazimine OR bedaquiline OR delamanid AND ("optic neuropathy" OR ocular) AND toxicity',
        '(vigabatrin OR amiodarone OR chloroquine OR hydroxychloroquine) AND '
        '("optic neuropathy" OR "ocular toxicity")',
    ],
    "s8_tcm_optic_extra": [
        '("Qingmang" OR "qing mang" OR "optic atrophy") AND ("traditional Chinese medicine" OR '
        'acupuncture OR "herbal medicine")',
        '("Zhujing" OR "Zhu Jing Wan" OR "Lycium" OR "Cassia") AND (retina OR "optic nerve" OR '
        '"retinal ganglion cell" OR macular)',
        '(electroacupuncture OR acupuncture) AND ("retinal ganglion cell" OR "optic nerve") '
        'AND (rat OR mice OR mouse OR animal model)',
    ],
}


def fetch(query, page_size=60, sort="CITED desc"):
    params = {"query": query, "format": "json", "pageSize": str(page_size),
              "resultType": "core", "sort": sort}
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90, context=CTX) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed: {query}: {last!r}")


def main():
    meta = {}
    for tag, qs in QUERIES.items():
        store = {}
        meta[tag] = []
        for q in qs:
            for sort in ("CITED desc", "P_PDATE_D desc"):
                try:
                    d = fetch(q, sort=sort)
                except Exception as e:  # noqa: BLE001
                    print(f"  !! {tag} {q} -> {e!r}")
                    continue
                n = 0
                for r in d.get("resultList", {}).get("result", []):
                    rec = {k: (r.get(k).replace("\n", " ").strip()
                               if k == "abstractText" and r.get(k) else r.get(k))
                           for k in KEEP}
                    key = rec.get("pmid") or rec.get("id")
                    if not key:
                        continue
                    if key not in store:
                        n += 1
                    store[key] = rec
                meta[tag].append({"query": q, "sort": sort,
                                  "hitCount": d.get("hitCount"), "new": n})
                print(f"  {tag} [{sort}] hits={d.get('hitCount')} new={n} :: {q[:80]}")
                time.sleep(0.4)
        with open(os.path.join(OUT, f"epmc_{tag}.json"), "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=1)
        print(f"   saved {len(store)} -> epmc_{tag}.json\n")
    with open(os.path.join(OUT, "epmc_supp_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print("DONE")


if __name__ == "__main__":
    main()
