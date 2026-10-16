# -*- coding: utf-8 -*-
"""
Read the paper that experimentally confirms this manuscript's mechanism, to find what it does
not cover.

Why this matters now
    The search turned up "Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis
    in retinal ganglion cells via Smad4 pathway" (Human Cell, 2026, doi
    10.1007/s13577-025-01342-4).  Its abstract reports what this manuscript's enrichment
    analysis predicted independently: ferroptosis as the death mode, SLC7A11 and GPX4 down,
    SDHB inhibited, and Smad4 as the transcription factor controlling SDHB.  That is a strong
    external validation of the network, and it also means the mechanism is no longer this
    manuscript's to claim as a discovery.

What is extracted here
    The limitations the authors state, the future work they propose, and the observations they
    did not make - because whatever is absent from a paper that confirms the mechanism is
    exactly where a second paper can still contribute.  The gene symbols the paper names are
    collected too, so its coverage can be compared with this manuscript's hub set directly.

Nothing here is taken as instruction; the file is read as data.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XML = (ROOT / "docs" / "literature_peers" / "text"
       / "PMC12823716_SDHB_ferroptosis_EON.xml")
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

raw = XML.read_text(encoding="utf-8", errors="replace")
#: strip tags but keep paragraph and section boundaries as newlines
body = re.sub(r"<(?:title|p|sec|abstract|fig|caption)[^>]*>", "\n", raw)
body = re.sub(r"<[^>]+>", " ", body)
body = re.sub(r"[ \t]+", " ", body)
body = re.sub(r"\n\s*\n+", "\n", body).strip()

print("=" * 100)
print("1. What the paper states as its own limitations and future work")
print("=" * 100)
sentences = re.split(r"(?<=[.!?])\s+", body)
KEYS = ("limitation", "limitations", "further stud", "future stud", "remains to be",
        "remains unclear", "not fully", "warrant", "should be", "in vivo", "clinical",
        "our study did not", "we did not", "fails to", "cannot")
hits, seen = [], set()
for s in sentences:
    low = s.lower()
    if any(k in low for k in KEYS) and 40 < len(s) < 520:
        k = s[:60]
        if k in seen:
            continue
        seen.add(k)
        hits.append(s.strip())
for s in hits[:22]:
    print(f"  - {s}")
print(f"\n  {len(hits)} such statements found")

print()
print("=" * 100)
print("2. Gene and protein symbols the paper names")
print("=" * 100)
SYMS = ["SDHB", "SMAD4", "GPX4", "SLC7A11", "ACSL4", "HMOX1", "NFE2L2", "KEAP1", "TP53",
        "TNF", "IL6", "STAT3", "AKT1", "BCL2", "CASP3", "SOD2", "CAT", "GPX1", "TXN",
        "NQO1", "HIF1A", "PPARGC1A", "DNM1L", "MFN2", "VDAC1", "CYCS", "APAF1", "BAX",
        "BCL2L1", "FTH1", "FTL", "OPA1", "SLC25A4", "MAPK1", "PPARG", "BDNF", "NTRK2",
        "TFEB", "SDHA", "GCLC", "GCLM", "NQO1", "HMOX1", "XCT", "FSP1", "ACSL4", "LPCAT3"]
found = {s: len(re.findall(r"\b" + s + r"\b", body, re.I)) for s in SYMS}
present = {k: v for k, v in sorted(found.items(), key=lambda x: -x[1]) if v}
absent = [k for k, v in found.items() if not v]
print(f"  named by the paper ({len(present)}):")
for k, v in present.items():
    print(f"      {k:10s} x{v}")
print(f"\n  of this manuscript's hubs, NOT named by the paper ({len(absent)}):")
print(f"      {', '.join(absent)}")

print()
print("=" * 100)
print("3. What the paper is about, in its own section titles")
print("=" * 100)
titles = re.findall(r"<title>([^<]{4,120})</title>", raw)
for t in titles[:26]:
    print(f"  - {re.sub(r'<[^>]+>', '', t).strip()}")

print()
print("=" * 100)
print("4. The gap this creates for a second paper")
print("=" * 100)
print("""  The paper establishes the mechanism in a rat model and a cell line.  What a
  pharmacovigilance analysis can add, and what this manuscript already has, is the other half:
  how often the toxicity occurs in humans, whether the ocular phenotype is specific to the
  optic nerve, whether it replicates in an independent database, whether the dose or the
  duration carries the risk, and whether the ferroptosis genes it names are expressed in
  human retina.  Those are questions a rat model cannot answer.

  The two together are stronger than either, and the manuscript should be positioned that way:
  the computational prediction came first and has now been confirmed experimentally, so the
  contribution is not the mechanism but the human-scale characterisation of it.""")

(OUT / "confirming_paper_analysis.json").write_text(json.dumps(
    {"pmid": "41563626", "doi": "10.1007/s13577-025-01342-4",
     "title": ("Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis in "
               "retinal ganglion cells via Smad4 pathway"),
     "journal": "Human Cell", "year": 2026,
     "genes_named": present, "hubs_not_named": absent,
     "limitation_statements": hits}, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n  -> results/confirming_paper_analysis.json")
