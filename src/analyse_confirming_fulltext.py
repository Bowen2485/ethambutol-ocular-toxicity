# -*- coding: utf-8 -*-
"""
Read the full text of the confirming paper to establish precisely where this manuscript can
still contribute.

Why the abstract was not enough
    The abstract says ferroptosis, SDHB, Smad4, GPX4 and SLC7A11, which is exactly this
    manuscript's enrichment result.  That establishes the overlap but not the boundary: a
    second paper can only add something the first did not do, and knowing what was done
    requires the methods and results rather than the summary.

What is looked for
    Whether the study had human data at all, or only a rat model and a cell line; whether it
    examined any hub gene other than the five it names; whether it measured dose-response or
    duration; whether it looked at recovery; and what it states as future work.  Each of those
    is a place where a pharmacovigilance analysis can supply what an animal model cannot.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TXT = (ROOT / "docs" / "literature_peers" / "text"
       / "PMC12823716_SDHB_ferroptosis_EON.pdftext.txt")
body = TXT.read_text(encoding="utf-8", errors="replace")
body = re.sub(r"[ \t]+", " ", body)
body = re.sub(r"\n{2,}", "\n", body)

print(f"  text length: {len(body):,} characters")

print()
print("=" * 100)
print("1. Is there any human data?")
print("=" * 100)
HUMAN = {
    "patients": r"\bpatient", "clinical cohort": r"\bcohort\b",
    "human samples": r"human (?:sample|tissue|retina|serum|blood)",
    "autopsy / donor": r"autops|donor (?:eye|retina)|postmortem",
    "clinical trial": r"clinical trial",
    "case series / report": r"case (?:series|report)",
    "human genetics": r"GWAS|genome-wide|polymorphism in patient",
}
for label, pat in HUMAN.items():
    n = len(re.findall(pat, body, re.I))
    print(f"  {label:22s} {n:>4d}")

print()
print("=" * 100)
print("2. Hub genes this manuscript has, and whether the paper measured them")
print("=" * 100)
HUBS = ["TP53", "NFE2L2", "AKT1", "BCL2", "HMOX1", "CASP3", "SOD2", "TNF", "GPX4",
        "MFN2", "SLC7A11", "ACSL4", "SDHB", "OPA1", "SLC25A4", "KEAP1", "MAPK1",
        "IL6", "STAT3", "CAT", "GPX1", "TXN", "NQO1", "HIF1A", "PPARGC1A", "DNM1L",
        "VDAC1", "CYCS", "APAF1", "BAX", "BCL2L1", "FTH1", "FTL"]
named = {h: len(re.findall(r"\b" + h + r"\b", body, re.I)) for h in HUBS}
present = {k: v for k, v in sorted(named.items(), key=lambda x: -x[1]) if v}
absent = sorted(k for k, v in named.items() if not v)
print(f"  named by the paper: {len(present)} of {len(HUBS)}")
for k, v in present.items():
    print(f"      {k:10s} x{v}")
print(f"\n  in this manuscript's hub set but never named ({len(absent)}):")
for i in range(0, len(absent), 8):
    print("      " + ", ".join(absent[i:i + 8]))

print()
print("=" * 100)
print("3. Dose, duration, and recovery")
print("=" * 100)
ASPECTS = {
    "dose levels compared": r"(?:dose|dosage).{0,60}(?:low|high|graded|different)|"
                            r"(?:\d+\s*mg/kg).{0,40}(?:\d+\s*mg/kg)",
    "dose-response stated": r"dose[- ]dependent|dose[- ]response",
    "duration varied": r"(?:for|over)\s+\d+\s*(?:week|day|month)s?",
    "recovery / reversibility": r"recover|reversib|withdrawal|discontinu",
    "dose in humans discussed": r"human[- ]equivalent|equivalent (?:human )?dose|"
                                r"standard human",
}
for label, pat in ASPECTS.items():
    ms = re.findall(pat, body, re.I)
    print(f"  {label:26s} {len(ms):>4d}   "
          f"{'; '.join(str(m)[:40] for m in ms[:3])}")

print()
print("=" * 100)
print("4. What the paper states as future work")
print("=" * 100)
sentences = re.split(r"(?<=[.!?])\s+", body)
KEYS = ("future stud", "future research", "further stud", "remains to be", "warrant",
        "should be validated", "next step", "our study did not", "we did not",
        "limitation of", "limitations of", "not investigated", "beyond the scope")
seen, hits = set(), []
for s in sentences:
    low = s.lower()
    if any(k in low for k in KEYS) and 30 < len(s) < 420:
        if s[:50] in seen:
            continue
        seen.add(s[:50])
        hits.append(s.strip())
for s in hits[:18]:
    print(f"  - {s[:200]}")

print()
print("=" * 100)
print("5. What this manuscript has that the paper does not")
print("=" * 100)
gaps = []
if not re.search(r"\bpatient", body, re.I):
    gaps.append("No patient data at all: the study is a rat model and a cell line")
else:
    n = len(re.findall(r"\bpatient", body, re.I))
    if n < 8:
        gaps.append(f"Patient data incidental ({n} mentions), not a clinical analysis")
gaps.append(f"{len(absent)} of this manuscript's {len(HUBS)} hub genes are never named, so "
            f"their role was not tested")
if not re.search(r"recover|reversib", body, re.I):
    gaps.append("Reversibility was not examined")
if re.search(r"dose[- ]dependent|dose[- ]response", body, re.I):
    gaps.append("A dose-response was described preclinically, but not at human doses")
for g in gaps:
    print(f"  - {g}")

(ROOT / "results" / "confirming_paper_gap.json").write_text(json.dumps(
    {"genes_named": present, "hubs_absent": absent, "gaps": gaps,
     "future_work": hits}, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  -> results/confirming_paper_gap.json")
