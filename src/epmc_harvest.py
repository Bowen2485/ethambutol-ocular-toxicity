# -*- coding: utf-8 -*-
"""Harvest Europe PMC records for ethambutol ocular toxicity + TCM optic neuropathy.

Saves trimmed JSON to data/raw/ for downstream Markdown generation.
"""
import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl._create_unverified_context()
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
os.makedirs(OUTDIR, exist_ok=True)

KEEP = [
    "id", "source", "pmid", "pmcid", "doi", "title", "authorString", "journalTitle",
    "pubYear", "citedByCount", "abstractText", "pubTypeList", "meshHeadingList",
    "isOpenAccess", "firstPublicationDate",
]


def fetch(query, page_size=60, sort="CITED desc", cursor="*"):
    params = {
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": "core",
        "sort": sort,
        "cursorMark": cursor,
    }
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


def trim(rec):
    out = {}
    for k in KEEP:
        v = rec.get(k)
        if k == "abstractText" and v:
            v = v.replace("\n", " ").strip()
        out[k] = v
    return out


def first_author(author_string):
    if not author_string:
        return ""
    return author_string.split(",")[0].strip()


def harvest(tag, queries, page_size=60):
    store = {}
    meta = []
    for q in queries:
        for sort in ("CITED desc", "P_PDATE_D desc"):
            try:
                d = fetch(q, page_size=page_size, sort=sort)
            except Exception as e:  # noqa: BLE001
                meta.append({"query": q, "sort": sort, "error": repr(e)})
                print(f"  !! {tag} [{sort}] {q} -> {e!r}")
                continue
            hits = d.get("hitCount")
            n = 0
            for r in d.get("resultList", {}).get("result", []):
                rec = trim(r)
                key = rec.get("pmid") or rec.get("id")
                if not key:
                    continue
                if key not in store:
                    n += 1
                store[key] = rec
            meta.append({"query": q, "sort": sort, "hitCount": hits, "new": n,
                         "returned": len(d.get("resultList", {}).get("result", []))})
            print(f"  {tag} [{sort}] hits={hits} new={n} :: {q}")
            time.sleep(0.4)
    return store, meta


ETH_QUERIES = {
    "q1_optic_neuropathy": [
        'ethambutol AND "optic neuropathy"',
        'ethambutol AND "optic neuropathy" AND (PUB_YEAR:[2015 TO 2026])',
        'ethambutol AND "optic neuropathy" AND (review OR guideline OR cohort OR incidence)',
        'ethambutol AND "toxic optic neuropathy"',
    ],
    "q2_imaging": [
        'ethambutol AND ("visual evoked potential" OR "optical coherence tomography" OR '
        '"retinal nerve fibre layer" OR "retinal nerve fiber layer" OR "ganglion cell")',
        'ethambutol AND ("optical coherence tomography" OR "retinal nerve fiber layer") '
        'AND (PUB_YEAR:[2015 TO 2026])',
    ],
    "q3_pharmacovigilance": [
        'ethambutol AND (pharmacovigilance OR FAERS OR disproportionality OR '
        '"spontaneous reporting" OR "adverse event reporting") '
        'AND (optic OR ocular OR eye OR vision OR blindness)',
        'ethambutol AND ("adverse drug reaction" OR "drug safety" OR "case report") '
        'AND (optic neuropathy OR visual loss)',
    ],
    "q4_mechanism": [
        'ethambutol AND (mitochondrial OR "oxidative stress" OR zinc OR copper OR lysosome '
        'OR autophagy OR chelat*) AND (optic OR retina* OR ocular OR neuro*)',
        'ethambutol AND (glutamate OR excitotoxicity OR "zinc toxicity" OR "copper toxicity" '
        'OR "metal chelation") AND (optic nerve OR retinal)',
    ],
    "q5_dose_risk": [
        'ethambutol AND (dose OR dosage OR "risk factor" OR incidence OR screening OR '
        '"renal impairment") AND ("optic neuropathy" OR "visual loss" OR "colour vision")',
        'ethambutol AND ("dose-dependent" OR "dose related") AND (optic OR ocular OR visual)',
        'ethambutol AND (screening OR monitoring) AND (vision OR colour OR color OR acuity)',
        'ethambutol AND (incidence OR prevalence) AND ("optic neuropathy" OR "ocular toxicity")',
    ],
    "q6_other_antiTB": [
        '(isoniazid OR rifampicin OR pyrazinamide OR linezolid OR "anti-tuberculosis") '
        'AND ("optic neuropathy" OR "ocular toxicity" OR "visual toxicity")',
        'isoniazid AND ("optic neuropathy" OR "optic neuritis")',
    ],
}

TCM_QUERIES = {
    "t1_tcm_optic": [
        '("traditional Chinese medicine" OR acupuncture OR herbal OR "Chinese herbal") '
        'AND "optic neuropathy"',
        'acupuncture AND ("optic nerve" OR "optic neuropathy" OR glaucoma OR "visual field")',
        '("traditional Chinese medicine" OR acupuncture) AND ("optic nerve" OR "optic neuritis" '
        'OR "ischemic optic neuropathy" OR "traumatic optic neuropathy")',
    ],
    "t2_network_pharm": [
        '"traditional Chinese medicine" AND ("optic nerve" OR retina OR retinal) '
        'AND ("network pharmacology" OR "molecular docking")',
        '("network pharmacology" OR "molecular docking") AND (retina OR "retinal ganglion cell" '
        'OR "optic nerve" OR glaucoma OR "diabetic retinopathy")',
    ],
    "t3_monomers": [
        '(lycium OR "Lycium barbarum" OR "goji" OR "wolfberry") AND ("retinal ganglion cell" '
        'OR "optic nerve" OR retina OR neuroprotect*)',
        '("Chrysanthemum" OR "Chrysanthemum morifolium") AND (retina OR "optic nerve" OR eye) '
        'AND (extract OR flavonoid OR luteolin OR apigenin)',
        '(Astragalus OR astragaloside OR "Astragalus membranaceus") AND (retina OR "optic nerve" '
        'OR "retinal ganglion cell" OR neuroprotect*)',
        '(Salvia miltiorrhiza OR tanshinone OR "danshen") AND (retina OR "optic nerve" '
        'OR "retinal ganglion cell" OR neuroprotect*)',
        '(puerarin OR "Pueraria lobata" OR "Puerariae radix") AND (retina OR "optic nerve" '
        'OR "retinal ganglion cell" OR glaucoma)',
        '("Ginkgo biloba" OR "ginkgo extract" OR EGb761 OR ginkgolide) AND (glaucoma OR retina '
        'OR "optic nerve" OR "visual field")',
        '(breviscapine OR scutellarin OR "Erigeron breviscapus") AND (retina OR "optic nerve" '
        'OR "retinal ganglion cell")',
        '(ligustrazine OR "tetramethylpyrazine") AND (retina OR "optic nerve" '
        'OR "retinal ganglion cell" OR glaucoma)',
        '(Dendrobium OR "Dendrobium officinale" OR dendrobine) AND (retina OR "optic nerve" OR eye)',
        '(Ligustrum lucidum OR "Ligustrum" OR specnuezhenide OR oleanolic acid) AND (retina OR '
        '"optic nerve" OR "retinal ganglion cell")',
        '(Cassia obtusifolia OR "Cassia tora" OR "cassia seed" OR aurantio-obtusin OR '
        '"Semen Cassiae") AND (retina OR "optic nerve" OR eye OR neuroprotect*)',
    ],
    "t4_formulas": [
        '("Liuwei Dihuang" OR "Rehmannia" OR "Erzhi" OR "Qijudihuang" OR "Qiju Dihuang" '
        'OR "Zhumu" OR "Mingmu" OR "Yiqimingmu" OR "Buzhong Yiqi" OR "Danggui Shaoyao") '
        'AND (retina OR "optic nerve" OR eye OR vision OR ocular)',
        '("traditional Chinese medicine" OR "herbal formula" OR decoction) '
        'AND (glaucoma OR "diabetic retinopathy" OR "optic nerve") AND ("network pharmacology")',
    ],
}


def main():
    allmeta = {}
    for tag, qs in ETH_QUERIES.items():
        print(f"== {tag} ==")
        store, meta = harvest(tag, qs, page_size=60)
        allmeta[tag] = meta
        path = os.path.join(OUTDIR, f"epmc_{tag}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=1)
        print(f"   saved {len(store)} records -> {path}\n")

    for tag, qs in TCM_QUERIES.items():
        print(f"== {tag} ==")
        store, meta = harvest(tag, qs, page_size=60)
        allmeta[tag] = meta
        path = os.path.join(OUTDIR, f"epmc_{tag}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=1)
        print(f"   saved {len(store)} records -> {path}\n")

    with open(os.path.join(OUTDIR, "epmc_search_meta.json"), "w", encoding="utf-8") as f:
        json.dump(allmeta, f, ensure_ascii=False, indent=1)
    print("DONE")


if __name__ == "__main__":
    main()
