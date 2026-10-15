# -*- coding: utf-8 -*-
"""
Step 6a - Reconnaissance of FinnGen endpoints available for the MR analysis.

FinnGen publishes a per-release phenotype API (JSON) that already carries the
case/control counts needed to judge whether an endpoint is powered for a
two-sample MR, plus the URLs of the tabix-indexed summary statistics.

Output: data/derived/finngen_endpoints.csv  (all endpoints)
        data/derived/finngen_eye_endpoints.csv  (ocular / neuro-ocular subset)
"""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

RELEASES = {
    "R12": "https://r12.finngen.fi/api/phenos",
    "R13": "https://r13.finngen.fi/api/phenos",
}

# Ocular + neuro-ocular + relevant systemic candidate-outcome keywords
EYE_RE = re.compile(
    r"(OPTIC|OPHT|OPHTH|OCUL|EYE|VISUAL|VISION|BLIND|RETIN|MACUL|GLAUCOM|"
    r"CATARACT|CORNEA|CONJUNCTIV|UVEITIS|IRIS|IRIDO|SCLER|LACRIMAL|STRABISM|"
    r"REFRACT|MYOPIA|HYPERMETROP|AMBLYOP|DIPLOPIA|NYSTAGMUS|PAPILL|CHORIORETIN|"
    r"VITREOUS|DETACHMENT_OF_RETINA|COLOUR|COLOR_VISION)", re.I)

# Systemic traits that are mechanistically plausible mediators / confounders for
# ethambutol ocular toxicity (renal clearance, zinc/copper handling, diabetes).
SYS_RE = re.compile(
    r"(TUBERCUL|DIABETES|RENAL|KIDNEY|NEPHRO|CREATININ|GLOMERUL|UREA|"
    r"ZINC|COPPER|CERULOPLASMIN|VITAMIN_B|FOLATE|ALCOHOL|MITOCHONDRI|"
    r"NEUROPATH|SMOK)", re.I)


def get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
        return resp.read()


def load_release(tag: str, url: str) -> pd.DataFrame:
    cache = DERIVED / f"finngen_{tag}_phenos.json"
    if cache.exists():
        payload = json.loads(cache.read_text(encoding="utf-8"))
    else:
        payload = json.loads(get(url).decode("utf-8", "replace"))
        cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    rows = []
    for p in payload:
        rows.append({
            "release": tag,
            "phenocode": p.get("phenocode"),
            "phenostring": p.get("phenostring"),
            "category": p.get("category"),
            "n_cases": p.get("num_cases"),
            "n_controls": p.get("num_controls"),
            "n_samples": p.get("num_samples"),
            "gc_lambda": p.get("gc_lambda"),
            "assoc_files": " | ".join(p.get("assoc_files") or []),
        })
    return pd.DataFrame(rows)


def main() -> None:
    frames = []
    for tag, url in RELEASES.items():
        try:
            df = load_release(tag, url)
            print(f"[ok] {tag}: {len(df)} endpoints")
            frames.append(df)
        except Exception as exc:  # noqa: BLE001
            print(f"[fail] {tag}: {type(exc).__name__} {str(exc)[:120]}")
    if not frames:
        raise SystemExit("no FinnGen release could be loaded")

    allp = pd.concat(frames, ignore_index=True)
    # case/control counts can arrive as strings
    for col in ("n_cases", "n_controls", "n_samples"):
        allp[col] = pd.to_numeric(allp[col], errors="coerce")
    allp.to_csv(DERIVED / "finngen_endpoints.csv", index=False, encoding="utf-8-sig")

    eye = allp[allp.phenostring.fillna("").str.contains(EYE_RE) |
               allp.phenocode.fillna("").str.contains(EYE_RE)].copy()
    eye = eye.sort_values(["release", "n_cases"], ascending=[True, False])
    eye.to_csv(DERIVED / "finngen_eye_endpoints.csv", index=False, encoding="utf-8-sig")

    print(f"\n=== ocular / neuro-ocular endpoints: {len(eye)} ===")
    cols = ["release", "phenocode", "phenostring", "n_cases", "n_controls"]
    for tag in RELEASES:
        sub = eye[eye.release == tag]
        print(f"\n--- {tag} ({len(sub)}) ---")
        print(sub[cols].to_string(index=False, max_colwidth=70))

    sysdf = allp[allp.phenostring.fillna("").str.contains(SYS_RE)].copy()
    sysdf = sysdf.sort_values(["release", "n_cases"], ascending=[True, False])
    sysdf.to_csv(DERIVED / "finngen_systemic_endpoints.csv", index=False, encoding="utf-8-sig")
    print(f"\n=== systemic candidate endpoints: {len(sysdf)} "
          f"-> data/derived/finngen_systemic_endpoints.csv ===")
    print("sample of the largest:")
    print(sysdf[(sysdf.release == "R12")][cols].head(20).to_string(index=False, max_colwidth=70))


if __name__ == "__main__":
    main()
