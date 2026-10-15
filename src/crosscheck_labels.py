# -*- coding: utf-8 -*-
"""
Compare the disproportionality signals against the drugs' official label warnings.

Why this matters for the paper
    The analysis reports 58 strict signals, but nothing has checked them against what
    regulators already require to be printed.  That comparison is informative in both
    directions:

        a drug with a label warning and no signal      reporting or power problem
        a drug with a signal and no label warning      a potential new safety signal,
                                                       which is the substantive finding
                                                       a pharmacovigilance paper can offer

Source
    The FDA's openFDA drug-label endpoint carries the current structured product
    labelling for approved products, including the warnings and adverse-reactions
    sections as free text.  It is used here only for the label text, which is not the
    same thing as using openFDA's adverse-event data - that would be FAERS by another
    route and could not serve as external validation.

Method
    For each antitubercular drug in the within-class panel, the label text is retrieved
    and searched for optic-nerve terms.  The result is set beside the drug's optic
    neuropathy reporting odds ratio from the paper's own within-class analysis.
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}

#: the generic names used by the within-class panel
DRUGS = {
    "ethambutol": "ethambutol",
    "isoniazid": "isoniazid",
    "rifampicin": "rifampin",
    "pyrazinamide": "pyrazinamide",
    "streptomycin": "streptomycin",
    "linezolid": "linezolid",
    "clofazimine": "clofazimine",
    "bedaquiline": "bedaquiline",
    "ethionamide": "ethionamide",
    "prothionamide": "prothionamide",
    "capreomycin": "capreomycin",
    "amikacin": "amikacin",
    "moxifloxacin": "moxifloxacin",
    "levofloxacin": "levofloxacin",
    "cycloserine": "cycloserine",
    "para-aminosalicylic acid": "aminosalicylic acid",
    "delamanid": "delamanid",
    "pretomanid": "pretomanid",
}
OPTIC_TERMS = ["optic neuritis", "optic neuropathy", "optic atrophy",
               "visual impairment", "blurred vision", "visual acuity",
               "colour vision", "color vision", "blindness", "visual field",
               "ophthalmic", "eye"]
RESTRICTED = ["optic neuritis", "optic neuropathy", "optic atrophy"]


def fetch_label(name: str) -> str:
    """Return the concatenated label text for a generic name, or ''."""
    params = urllib.parse.urlencode({
        "search": f'openfda.generic_name:"{name}"',
        "limit": 3,
    })
    url = f"https://api.fda.gov/drug/label.json?{params}"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            j = json.loads(r.read())
    except Exception:  # noqa: BLE001
        return ""
    parts = []
    for res in j.get("results", []):
        for key in ("warnings", "adverse_reactions", "boxed_warning",
                    "warnings_and_cautions", "indications_and_usage"):
            for v in res.get(key, []) or []:
                if isinstance(v, str):
                    parts.append(v)
    return " ".join(parts).lower()


print("=" * 96)
print("1. Retrieving label text")
print("=" * 96)
labels = {}
for label, generic in DRUGS.items():
    text = fetch_label(generic)
    labels[label] = text
    state = f"{len(text):,} chars" if text else "not retrieved"
    print(f"  {label:26s} {generic:22s} {state}")
    time.sleep(0.8)

print()
print("=" * 96)
print("2. Label warnings versus the paper's signals")
print("=" * 96)
sig_path = ROOT / "results" / "faers_withinclass_signals.csv"
sig = pd.read_csv(sig_path, encoding="utf-8-sig")
optic = sig[sig.term.astype(str).str.upper() == "OPTIC NEUROPATHY"]
ror_by_drug = dict(zip(optic.drug, optic.ror)) if len(optic) else {}

rows = []
print(f"  {'drug':26s} {'ROR':>9s} {'label: optic':>13s} {'label: any eye':>15s}")
for label in DRUGS:
    text = labels.get(label, "")
    restricted = [t for t in RESTRICTED if t in text]
    anyeye = [t for t in OPTIC_TERMS if t in text]
    ror_val = ror_by_drug.get(label)
    print(f"  {label:26s} "
          f"{(f'{ror_val:.2f}' if ror_val is not None else '-'):>9s} "
          f"{('yes' if restricted else 'no'):>13s} "
          f"{('yes' if anyeye else 'no'):>15s}")
    rows.append({
        "drug": label, "generic": DRUGS[label],
        "ror_optic_neuropathy": round(float(ror_val), 3)
        if ror_val is not None else None,
        "label_optic_terms": "; ".join(restricted),
        "label_any_eye_terms": "; ".join(anyeye[:6]),
        "label_retrieved": bool(text),
    })

print()
print("=" * 96)
print("3. The informative cells")
print("=" * 96)
have_label = [r for r in rows if r["label_retrieved"]]
sig_no_label = [r for r in have_label
                if r["ror_optic_neuropathy"] and r["ror_optic_neuropathy"] > 2
                and not r["label_optic_terms"]]
label_no_sig = [r for r in have_label if r["label_optic_terms"]
                and (not r["ror_optic_neuropathy"]
                     or r["ror_optic_neuropathy"] <= 2)]
print(f"  labels retrieved: {len(have_label)} of {len(rows)}")
print()
print(f"  signal (ROR > 2) but no optic term in the label: {len(sig_no_label)}")
for r in sig_no_label:
    print(f"      {r['drug']:26s} ROR {r['ror_optic_neuropathy']:.2f}")
print()
print(f"  optic term in the label but no signal: {len(label_no_sig)}")
for r in label_no_sig:
    print(f"      {r['drug']:26s} ROR {r['ror_optic_neuropathy']}")

out = ROOT / "results" / "label_vs_signal.csv"
pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
print()
print(f"-> {out.relative_to(ROOT)}")
print()
print("=" * 96)
print("Reading")
print("=" * 96)
print("""  Agreement between label and signal is expected for the drugs whose ocular toxicity
  clinicians already know, so it validates rather than discovers.  The informative rows
  are the disagreements: a signal without a label warning is a candidate new finding,
  and a label warning without a signal points to a reporting or power limitation in this
  database.""")
