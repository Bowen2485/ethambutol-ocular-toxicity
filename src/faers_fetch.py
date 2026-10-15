# -*- coding: utf-8 -*-
"""
Step 1 - FAERS data acquisition via the openFDA drug/event API.

Downloads every FAERS report in which ethambutol appears as a medicinal product,
plus a comparator arm (other first-line anti-tuberculosis drugs), and flattens the
nested JSON into analysis-ready tables.

Usage:
    python faers_fetch.py            # incremental: reuses the on-disk cache
    python faers_fetch.py --refresh  # ignore cache and re-download
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
RAW.mkdir(parents=True, exist_ok=True)
DERIVED.mkdir(parents=True, exist_ok=True)

API = "https://api.fda.gov/drug/event.json"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FAERS-research/1.0"}

# Name fragments that identify a first-line anti-tuberculosis drug inside
# patient.drug.medicinalproduct (openFDA substitutes are case-insensitive).
DRUG_TERMS = {
    "ethambutol": "ETHAMBUTOL",
    "isoniazid": "ISONIAZID",
    "rifampicin": "RIFAMPICIN",
    "pyrazinamide": "PYRAZINAMIDE",
}

# Excipient / combination-product fragments that must NOT be mistaken for a
# standalone exposure of the drug of interest.
COMBINATION_MARKERS = ("RIFAMPICIN", "ISONIAZID", "PYRAZINAMIDE", "RIFABUTIN",
                       "STREPTOMYCIN", "LEVOFLOXACIN", "MOXIFLOXACIN", "ETHIONAMIDE")

PAGE = 100
SLEEP = 0.34  # openFDA allows 240 requests/min without a key


def _request(url: str, tries: int = 6) -> dict:
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90, context=CTX) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:           # openFDA returns 404 for zero matches
                return {"results": [], "meta": {"results": {"total": 0}}}
            last = exc
            time.sleep(2 ** attempt)
        except Exception as exc:          # noqa: BLE001
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"openFDA request failed after {tries} tries: {url} :: {last}")


def total_for(search: str) -> int:
    url = f"{API}?search={urllib.parse.quote(search)}&limit=1"
    return int(_request(url)["meta"]["results"]["total"])


def fetch_all(search: str, tag: str, refresh: bool = False) -> list[dict]:
    """Download every report matching `search`, cached as JSONL."""
    cache = RAW / f"faers_{tag}.jsonl"
    if cache.exists() and not refresh:
        rows = [json.loads(line) for line in cache.open(encoding="utf-8") if line.strip()]
        print(f"[cache] {tag}: {len(rows)} reports from {cache.name}")
        return rows

    grand = total_for(search)
    print(f"[fetch] {tag}: {grand} reports expected")
    rows: list[dict] = []
    skip = 0
    tmp = cache.with_suffix(".jsonl.part")
    with tmp.open("w", encoding="utf-8") as fh:
        while skip < grand:
            url = (f"{API}?search={urllib.parse.quote(search)}"
                   f"&limit={PAGE}&skip={skip}")
            payload = _request(url)
            batch = payload.get("results", [])
            if not batch:
                break
            for rec in batch:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            rows.extend(batch)
            fh.flush()
            skip += len(batch)
            if skip % 1000 < PAGE:
                print(f"    {skip}/{grand}")
            time.sleep(SLEEP)
    tmp.replace(cache)
    print(f"[fetch] {tag}: saved {len(rows)} reports -> {cache.name}")
    return rows


def flatten(records: list[dict], drug_key: str) -> pd.DataFrame:
    """Return a case-level table with one row per deduplicated FAERS report."""
    cases = []
    for rec in records:
        pid = str(rec.get("primaryid") or rec.get("safetyreportid") or "")
        patient = rec.get("patient", {}) or {}
        age_raw = patient.get("patientonsetage")
        try:
            age = float(age_raw) if age_raw not in (None, "") else None
        except (TypeError, ValueError):
            age = None
        wt_raw = patient.get("patientweight")
        try:
            weight = float(wt_raw) if wt_raw not in (None, "") else None
        except (TypeError, ValueError):
            weight = None

        reactions = patient.get("reaction", []) or []
        rterms = [str(r.get("reactionmeddrapt", "")).upper() for r in reactions]
        rterms = [t for t in rterms if t]

        # Drug-level records for the drug of interest in this case
        idx_drugs = []
        for d in patient.get("drug", []) or []:
            name = str(d.get("medicinalproduct", "")).upper()
            if DRUG_TERMS[drug_key] in name:
                idx_drugs.append(d)
        if not idx_drugs:
            continue

        role_rank = {"PRIMARY SUSPECT": 0, "SECONDARY SUSPECT": 1, "CONCOMITANT": 2,
                     "INTERACTING": 3, "": 4, None: 4}
        idx_drugs.sort(key=lambda d: role_rank.get(
            str(d.get("drugcharacterization", "")).upper().replace("_", " "), 4))
        primary = idx_drugs[0]

        def _txt(v):
            if v is None:
                return ""
            if isinstance(v, list):
                return " | ".join(str(x) for x in v)
            return str(v)

        indication = " | ".join(
            filter(None, (_txt(d.get("drugindication")) for d in idx_drugs)))
        daily_dose = " | ".join(
            filter(None, (_txt(d.get("daily_dose")) for d in idx_drugs)))
        route = " | ".join(
            filter(None, (_txt(d.get("route")) for d in idx_drugs)))

        dechallenge = " | ".join(filter(None, (
            _txt(d.get("drugreactionreported")) for d in idx_drugs)))
        # structured rechallenge / dechallenge actions
        acts = []
        for d in idx_drugs:
            for key in ("actiondrug", "drugadditional"):
                if d.get(key):
                    acts.append(_txt(d.get(key)))
        action = " | ".join(acts)

        cases.append({
            "primaryid": pid,
            "case_id": str(rec.get("caseid") or pid),
            "receivedate": rec.get("receivedate"),
            "receiptdate": rec.get("receiptdate"),
            "transmissiondate": rec.get("transmissiondate"),
            "serious": rec.get("serious"),
            "seriousnessdeath": rec.get("seriousnessdeath"),
            "seriousnesslifethreatening": rec.get("seriousnesslifethreatening"),
            "seriousnesshospitalization": rec.get("seriousnesshospitalization"),
            "seriousnessdisabling": rec.get("seriousnessdisabling"),
            "seriousnesscongenitalanomali": rec.get("seriousnesscongenitalanomali"),
            "seriousnessother": rec.get("seriousnessother"),
            "country": rec.get("occurcountry") or rec.get("primarysourcecountry"),
            "reporter": rec.get("primarysource", {}).get("reportercountry") if isinstance(rec.get("primarysource"), dict) else None,
            "qualification": rec.get("primarysource", {}).get("qualification") if isinstance(rec.get("primarysource"), dict) else None,
            "sex": patient.get("patientsex"),
            "age": age,
            "age_unit": patient.get("patientonsetageunit"),
            "weight": weight,
            "n_reactions": len(rterms),
            "reactions": " ; ".join(rterms),
            "outcome_death": int(any(str(r.get("reactionoutcome")) == "5" for r in reactions)),
            "outcome_lifethreat": int(any(str(r.get("reactionoutcome")) == "4" for r in reactions)),
            "outcome_hospital": int(any(str(r.get("reactionoutcome")) == "2" for r in reactions)),
            "outcome_disability": int(any(str(r.get("reactionoutcome")) == "3" for r in reactions)),
            "n_drugs": len(patient.get("drug", []) or []),
            "drug_role": str(primary.get("drugcharacterization", "")).upper().replace("_", " "),
            "indication": indication,
            "daily_dose": daily_dose,
            "route": route,
            "dechallenge_rechallenge": dechallenge,
            "action_drug": action,
            "therapy_start": primary.get("drugstartdate"),
            "therapy_end": primary.get("drugenddate"),
            "therapy_duration": primary.get("drugduration"),
            "therapy_duration_unit": primary.get("drugdurationunit"),
            "narrative": "",   # deliberately not used; narrative is unstructured
        })
    case_df = pd.DataFrame(cases)
    return case_df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--drug", default="ethambutol", choices=list(DRUG_TERMS))
    args = ap.parse_args()

    term = DRUG_TERMS[args.drug]
    search = f'patient.drug.medicinalproduct:"{term}"'

    manifesto = {"drug": args.drug, "term": term, "generated": time.strftime("%Y-%m-%d %H:%M:%S")}

    # whole-database denominator
    manifesto["faers_total_reports"] = total_for('_exists_:receivedate')
    print("FAERS total reports:", manifesto["faers_total_reports"])

    recs = fetch_all(search, args.drug, refresh=args.refresh)
    manifesto["index_reports_raw"] = len(recs)

    case_df = flatten(recs, args.drug)
    case_df = case_df.drop_duplicates(subset=["primaryid"], keep="first")
    manifesto["index_reports_dedup"] = int(len(case_df))
    case_df.to_csv(DERIVED / f"faers_{args.drug}_cases.csv", index=False, encoding="utf-8-sig")

    # comparator arms (first-line ATT drugs other than ethambutol)
    comparators = {}
    for key in ("isoniazid", "rifampicin", "pyrazinamide"):
        comparators[key] = total_for(f'patient.drug.medicinalproduct:"{DRUG_TERMS[key]}"')
        print(f"  {key}: {comparators[key]}")
    manifesto["comparator_totals"] = comparators

    (DERIVED / "faers_manifest.json").write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== manifest ===")
    print(json.dumps(manifesto, indent=2, ensure_ascii=False))
    print("\ncase table ->", DERIVED / f"faers_{args.drug}_cases.csv",
          f"shape={case_df.shape}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
