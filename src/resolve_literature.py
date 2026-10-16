# -*- coding: utf-8 -*-
"""
Resolve the candidate papers to identifiers and check what each one actually reports.

Why the check
    A title alone does not say whether a paper is worth downloading.  Two candidates here look
    relevant from their titles and one of them - the isoniazid interaction paper - may already
    be covered by this manuscript's regimen-stratified analysis, in which case it is a citation
    rather than a gap.  Resolving each to its abstract through Europe PMC, which returns
    structured records, settles that before anything is fetched.

What is produced
    A worklist with DOI, PMID, journal and year for each candidate, the abstract where one is
    available, and a note saying what in this manuscript it bears on.  That is what a reader
    needs in order to decide what to download.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-litcheck/1.0)"}

#: title fragments to resolve, with what each bears on in this manuscript
CANDIDATES = [
    ("Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis", "mechanism"),
    ("Risk factors for ethambutol-induced optic neuropathy: a systematic review", "risk"),
    ("Risk Factors of Optic Neuropathy in Ethambutol Users: Interaction with Isoniazid",
     "risk"),
    ("Incidence and clinical features of ethambutol-induced optic neuropathy in Korea",
     "incidence"),
    ("Incidence, risk factors and ophthalmic clinical characteristic of "
     "ethambutol-induced optic neuropathy", "incidence"),
    ("Characterisation of macular superficial vessel density alteration in preclinical "
     "ethambutol-induced optic neuropathy", "imaging"),
    ("Incidence and prognostic factor of ethambutol-related optic neuropathy", "incidence"),
    ("Deciphering the molecular mechanisms of fluoxetine-induced sexual dysfunction", "method"),
    ("Evaluating Stevens-Johnson Syndrome/Toxic Epidermal Necrolysis Associated With Newer "
     "Antiseizure Medications", "method"),
]


def search(q: str, n: int = 3) -> list[dict]:
    url = (EPMC + "?query=" + urllib.parse.quote('TITLE:"' + q + '"')
           + f"&format=json&resultType=core&pageSize={n}")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=45) as fh:
            d = json.loads(fh.read(1_200_000).decode("utf-8", "replace"))
        return d.get("resultList", {}).get("result", []) or []
    except Exception as e:  # noqa: BLE001
        return [{"__error__": f"{type(e).__name__}: {str(e)[:80]}"}]


print("=" * 104)
print("Resolving the candidate papers")
print("=" * 104)
worklist = []
for q, role in CANDIDATES:
    rs = search(q)
    if not rs:
        print(f"\n  NOT FOUND: {q[:70]}")
        continue
    r = rs[0]
    if "__error__" in r:
        print(f"\n  ERROR {r['__error__']} for {q[:60]}")
        continue
    rec = {
        "query": q,
        "role": role,
        "title": r.get("title", "").rstrip("."),
        "doi": r.get("doi", ""),
        "pmid": r.get("pmid", ""),
        "pmcid": r.get("pmcid", ""),
        "journal": ((r.get("journalInfo") or {}).get("journal") or {}).get("title", ""),
        "year": r.get("pubYear", ""),
        "open_access": r.get("isOpenAccess", ""),
        "in_epmc": r.get("inEPMC", ""),
        "cited_by": r.get("citedByCount", 0),
        "abstract": (r.get("abstractText") or "")[:1400],
    }
    worklist.append(rec)
    print()
    print(f"  {rec['title'][:96]}")
    print(f"      DOI   {rec['doi'] or '(none)'}")
    print(f"      PMID  {rec['pmid']}   PMC {rec['pmcid'] or '-'}   "
          f"{rec['journal']} {rec['year']}")
    print(f"      open access {rec['open_access']}   full text in Europe PMC "
          f"{rec['in_epmc']}   cited by {rec['cited_by']}")
    print(f"      role: {role}")
    time.sleep(0.3)

print()
print("=" * 104)
print("What each bears on")
print("=" * 104)
NOTES = {
    "mechanism": "Reports the ferroptosis mechanism experimentally in a rat model and RGC-5 "
                 "cells.  This manuscript predicted the same pathway from enrichment; the "
                 "paper confirms it and removes any claim to first discovery.  Must be cited "
                 "and the manuscript repositioned as the human-scale characterisation.",
    "risk": "Human risk-factor evidence.  Bears on Section 3.5, where age and sex are "
            "modelled, and on the regimen-stratified analysis in 3.2b.",
    "incidence": "Human incidence.  Bears on the Introduction, where the 0.28%-6.5% range is "
                 "quoted, and on the claim that ascertainment drives the spread.",
    "imaging": "Preclinical OCT angiography.  Bears on the Discussion, where a biomarker for "
               "early detection would be the clinical implication.",
    "method": "A paper in the same genre, useful for method comparison rather than for "
              "content.",
}
for rec in worklist:
    print(f"\n  {rec['role']:10s} {rec['title'][:80]}")
    print(f"      {NOTES.get(rec['role'], '')}")

(OUT / "literature_worklist.json").write_text(
    json.dumps(worklist, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  {len(worklist)} papers resolved -> results/literature_worklist.json")

print()
print("=" * 104)
print("Download list")
print("=" * 104)
for i, rec in enumerate(worklist, 1):
    oa = "  [open access]" if rec["open_access"] == "Y" else "  [subscription]"
    print(f"  {i:>2d}. {rec['title'][:78]}")
    print(f"      https://doi.org/{rec['doi']}{oa}")
