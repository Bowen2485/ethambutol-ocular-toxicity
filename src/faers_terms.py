# -*- coding: utf-8 -*-
"""
Step 2a - Define the ocular adverse-event (AE) term list from the real FAERS data.

Two complementary sources:
  (A) data-driven  : ocular MedDRA preferred terms that actually occur in the
                     ethambutol reports (lexical SMQ-style screen over the
                     flattened case table).
  (B) hypothesis-  : a curated panel covering the recognised ethambutol ocular
      driven         toxicity spectrum (optic nerve, visual function, retina,
                     ocular surface, other).

Every candidate term is then verified against openFDA by an exact integer count,
so a term that does not exist in FAERS can never enter the analysis.

Output: data/derived/ocular_terms.json / .csv
"""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)

API = "https://api.fda.gov/drug/event.json"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FAERS-research/1.0"}
SLEEP = 0.42

# --------------------------------------------------------------- ocular lexicon
OCULAR_PATTERNS = [
    r"\bEYE", r"\bEYES", r"\bOCUL", r"\bOPHTHALM", r"\bVISUAL", r"\bVISION",
    r"\bSIGHT", r"\bBLIND", r"\bOPTIC", r"\bRETIN", r"\bMACUL", r"\bVITREOUS",
    r"\bCHOROID", r"\bCONJUNCTIV", r"\bCORNE", r"\bIRIS\b", r"\bIRID",
    r"\bUVE", r"\bSCLER", r"\bLACRIMAL", r"\bLACRIMATION", r"\bTEAR",
    r"\bPUPIL", r"\bPTOSIS", r"\bDIPLOPIA", r"\bNYSTAGMUS", r"\bPHOTOPHOBIA",
    r"\bSCOTOMA", r"\bAMBLYOPIA", r"\bCATARACT", r"\bGLAUCOMA",
    r"\bPAPILLOEDEMA", r"\bPAPILLEDEMA", r"\bPAPILLITIS", r"\bCHALAZION",
    r"\bBLEPHAR", r"\bEYELID", r"\bPERIORBITAL", r"\bORBITAL",
    r"\bDYSCHROMATOPSIA", r"\bCHROMATOPSIA", r"\bHEMIANOPIA", r"\bQUADRANTANOPIA",
    r"\bFUNDUS", r"\bRETROBULBAR", r"\bCOLOUR VISION", r"\bCOLOR VISION",
    r"\bVISUAL FIELD", r"\bVISUAL ACUITY", r"\bVISUAL IMPAIRMENT",
    r"\bOCULAR", r"\bEYEBALL", r"\bOPTIC NERVE", r"\bOPTIC DISC",
    r"\bEYE PAIN", r"\bEYE IRRITATION", r"\bDRY EYE", r"\bEYE DISORDER",
]

CURATED: dict[str, list[str]] = {
    "Optic nerve": [
        "OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
        "OPTIC NERVE DISORDER", "OPTIC DISC DISORDER", "PAPILLOEDEMA",
        "RETROBULBAR NEURITIS", "OPTIC NERVE INJURY", "PAPILLARY OEDEMA",
        "OPTIC ISCHAEMIC NEUROPATHY",
    ],
    "Visual function": [
        "BLINDNESS", "VISUAL IMPAIRMENT", "VISUAL ACUITY REDUCED",
        "VISION BLURRED", "VISUAL FIELD DEFECT", "SCOTOMA", "HEMIANOPIA",
        "DIPLOPIA", "PHOTOPHOBIA", "COLOUR VISION DEFECT", "DYSCHROMATOPSIA",
        "CHROMATOPSIA", "NYSTAGMUS", "AMBLYOPIA", "BLINDNESS TRANSIENT",
        "BLINDNESS UNILATERAL", "BLINDNESS BILATERAL", "SUDDEN VISUAL LOSS",
        "VISUAL EVOKED POTENTIAL ABNORMAL", "VISUAL DISTURBANCE",
        "PHOTOPSIA", "METAMORPHOPSIA", "DIPLOPIA DIPLOPIA",
    ],
    "Retina / macula": [
        "RETINOPATHY", "MACULOPATHY", "MACULAR DEGENERATION",
        "RETINAL DISORDER", "RETINAL HAEMORRHAGE", "RETINAL OEDEMA",
        "RETINAL VEIN OCCLUSION", "RETINAL ARTERY OCCLUSION",
        "CYSTOID MACULAR OEDEMA", "CHORIORETINOPATHY", "RETINAL DETACHMENT",
        "CENTRAL SEROUS CHORIORETINOPATHY", "RETINAL PIGMENT EPITHELIOPATHY",
        "RETINAL EXUDATES", "MACULAR OEDEMA", "RETINAL NERVE FIBRE LAYER THINNING",
        "RETINAL VASCULAR DISORDER",
    ],
    "Ocular surface / adnexa": [
        "OCULAR HYPERAEMIA", "EYE PAIN", "EYE IRRITATION", "DRY EYE",
        "CONJUNCTIVITIS", "LACRIMATION INCREASED", "EYELID OEDEMA",
        "PERIORBITAL OEDEMA", "BLEPHARITIS", "KERATITIS", "CORNEAL DISORDER",
        "PTOSIS", "OCULAR DISCOMFORT", "EYE PRURITUS", "EYE SWELLING",
        "LACRIMAL DISORDER", "EYE MOVEMENT DISORDER",
    ],
    "Other ocular": [
        "CATARACT", "GLAUCOMA", "UVEITIS", "IRIDOCYCLITIS", "VITRITIS",
        "VITREOUS FLOATERS", "OCULAR VASCULAR DISORDER",
        "PUPILLARY REFLEX IMPAIRED", "OCULOGYRIC CRISIS", "IRIS DISORDER",
        "OCULAR TOXICITY", "EYE HAEMORRHAGE", "INTRAOCULAR PRESSURE INCREASED",
    ],
}


def request_json(url: str, tries: int = 8) -> dict:
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            body = b""
            try:
                body = exc.read()
            except Exception:  # noqa: BLE001
                pass
            if exc.code == 404:
                return {"meta": {"results": {"total": 0}}}
            last = exc
            time.sleep((1.8 ** attempt) if exc.code in (403, 429)
                       or b"API_KEY_MISSING" in body else 0.9 * (attempt + 1))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"openFDA request failed: {url} :: {last}")


def term_total(term: str) -> int:
    url = (f"{API}?search="
           f"{urllib.parse.quote(f'patient.reaction.reactionmeddrapt:\"{term}\"')}&limit=1")
    return int(request_json(url)["meta"]["results"]["total"])


def main() -> None:
    cases_path = DERIVED / "faers_ethambutol_cases.csv"
    records: list[dict] = []
    seen: set[str] = set()

    if cases_path.exists():
        cases = pd.read_csv(cases_path, encoding="utf-8-sig")
        rx = re.compile("|".join(OCULAR_PATTERNS))
        counter: dict[str, int] = {}
        for blob in cases["reactions"].dropna():
            for term in str(blob).split(" ; "):
                term = term.strip()
                if term:
                    counter[term] = counter.get(term, 0) + 1
        print(f"[A] {len(counter)} distinct MedDRA PTs across {len(cases)} "
              f"ethambutol reports")
        for term, n in sorted(counter.items(), key=lambda kv: -kv[1]):
            if rx.search(term):
                records.append({"term": term, "group": "Data-driven (in-index)",
                                "source": "FAERS ethambutol reports", "n_index": n})
                seen.add(term)
        print(f"    ocular-looking terms kept: {len(records)}")
    else:
        print(f"[A] {cases_path.name} not found - data-driven screen skipped")

    n_curated = 0
    for group, terms in CURATED.items():
        for term in dict.fromkeys(terms):
            if term in seen:
                continue
            seen.add(term)
            records.append({"term": term, "group": group, "source": "Curated panel",
                            "n_index": None})
            n_curated += 1
    print(f"[B] curated candidates to verify: {n_curated}")

    print("[C] verifying every candidate against openFDA exact counts ...")
    dropped = []
    for i, rec in enumerate(records, 1):
        n = term_total(rec["term"])
        rec["in_faers"] = n
        if n == 0:
            dropped.append(rec["term"])
        if i % 25 == 0:
            print(f"    {i}/{len(records)}")
    records = [r for r in records if r["in_faers"]]

    out_json = DERIVED / "ocular_terms.json"
    out_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    df = pd.DataFrame(records)
    df.to_csv(DERIVED / "ocular_terms.csv", index=False, encoding="utf-8-sig")

    print(f"\n[D] kept {len(df)} terms; dropped {len(dropped)} absent from FAERS")
    if dropped:
        print("    dropped:", dropped)
    print("\nterms by group:")
    print(df.groupby("group").size().to_string())
    print(f"\n-> {out_json}")


if __name__ == "__main__":
    main()
