# -*- coding: utf-8 -*-
"""
Propose a category for each of the terms the signal classifier leaves unclassified.

Why a proposal rather than a change
    src/classify_signals.py assigns categories from three explicit lists, deliberately and
    auditorily ("by an explicit, auditable list rather than by keyword guessing"), and 83 terms
    in the 177-term panel appear in none of them.  Extending those lists changes which terms
    count as the drug-toxicity spectrum, and therefore changes the numbers the manuscript
    reports from Table 2c.  So this script writes a review sheet and changes nothing: adopting
    it is the author's decision, and it should be taken deliberately.

What the review sheet shows
    Every unclassified term gets one of five buckets, a one-line reason and a confidence.

        T  drug-toxicity spectrum  - within the axes the manuscript already treats as drug
                                     related (optic nerve, visual function, retina, lens,
                                     ocular surface)
        B  ocular tuberculosis     - infection or its sequelae, expected from the indication
                                     in every comparator arm, as with the 14 terms already listed
        X  non-ocular artefact     - not an ocular disorder at all; admitted by the screening
                                     stem (scler-, macul-, tear-, eye)
        D  ocular comorbidity      - a genuine ocular disorder that is neither drug toxicity nor
                                     tuberculosis: trauma, surgery, tumour, or a separate disease
        U  needs the author        - the terms whose placement depends on clinical judgement

    The D bucket is the substantive finding.  The manuscript's taxonomy has three homes and
    these terms fit none of them: diabetic retinopathy, NMO spectrum disorder, ophthalmic
    migraine, eye injury or contusion, post-surgical codes and an ocular neoplasm.  Left where
    they are they inflate the panel; put into the toxicity spectrum they would be read as drug
    effects.  Both readings are wrong, so the choice is between adding a fourth category that is
    reported but not interpreted, and stating explicitly that unmatched terms are not interpreted.

Writes tables/Table2d_review_proposed.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "tables"

#: not ocular disorders; admitted by the screening stem, with the stem named
X_ARTEFACT = {
    "RASH MACULO-PAPULAR": ("skin rash; the same macul- stem that admits MACULE and RASH "
                            "MACULAR, both already listed as artefacts"),
    "MULTIPLE SCLEROSIS RELAPSE": "neurological disease; matched the scler- stem",
    "SYSTEMIC SCLEROSIS": "connective-tissue disease; matched the scler- stem",
    "INTESTINAL MUCOSAL TEAR": "gastrointestinal; matched the mucosal and tear stems",
    "DECREASED EYE CONTACT": "behavioural term used in neurodevelopmental reporting; matched eye",
    "EXPOSURE VIA EYE CONTACT": "a route-of-exposure code, not a disorder; matched eye",
    "EYE ROLLING": "behavioural sign, one case; matched eye",
    "HALLUCINATION, VISUAL": "neuropsychiatric symptom; ocular only in its modifier",
}

#: infection and its sequelae, which every comparator arm shares through the indication
B_INFECTION = {
    "INFECTIVE UVEITIS": "intraocular infection; the listed set already holds UVEITIS",
    "NECROTISING RETINITIS": "infectious retinitis; the listed set holds NECROTISING HERPETIC "
                             "RETINOPATHY",
    "RETINITIS": "intraocular inflammation, infectious in this population",
    "CONJUNCTIVAL GRANULOMA": "granulomatous inflammation, a tuberculosis-associated form",
    "IRIS ADHESIONS": "sequela of intraocular inflammation rather than a primary drug effect",
}

#: genuine ocular disorders with no home in the three-list taxonomy
D_COMORBIDITY = {
    "DIABETIC RETINOPATHY": "a comorbidity of the cohort, not a drug effect; the same argument "
                            "that excludes ocular tuberculosis applies here",
    "NEUROMYELITIS OPTICA SPECTRUM DISORDER": "a separate autoimmune disease of the optic nerve",
    "OPHTHALMIC MIGRAINE": "a primary headache disorder with visual symptoms",
    "EYE INJURY": "trauma",
    "EYE CONTUSION": "trauma",
    "CONJUNCTIVAL BLEB": "post-surgical finding",
    "CATARACT OPERATION COMPLICATION": "post-surgical; CATARACT OPERATION is listed, but a "
                                       "complication of the operation is not the same claim",
    "OCULAR FISTULA": "usually post-surgical",
    "OCULAR NEOPLASM": "neoplastic disease",
    "OCULAR ROSACEA": "dermatological disease with ocular involvement",
    "CHRONIC GRAFT VERSUS HOST DISEASE IN EYE": "systemic disease manifesting in the eye",
    "ORBITAL APEX SYNDROME": "a syndrome of infective, neoplastic or inflammatory origin",
    "TEARFULNESS": "a mood symptom; lacrimation is carried separately as LACRIMATION INCREASED",
}

#: genuine clinical judgement calls rather than classification calls
U_REVIEW = {
    "EYE SYMPTOM": "a non-specific symptom code; keeping it in the toxicity spectrum is "
                   "defensible only if the panel is said to contain symptom codes",
    "EYE INFECTION": "non-specific infection term; infection axis, but not tuberculosis-specific",
    "HEMIANOPIA HOMONYMOUS": "a retrochiasmal field defect, so neurological rather than "
                             "optic-nerve; the listed set holds HEMIANOPIA HETERONYMOUS",
}

CONFIDENCE = {"T": "high", "B": "medium", "X": "high", "D": "medium", "U": "author"}
T_REASON = ("within the drug-related axes the manuscript already treats as toxicity: optic "
            "nerve, visual function, retina, lens, ocular surface")

src = TAB / "Table2d_unclassified_terms.csv"
rows = list(csv.DictReader(open(src, newline="", encoding="utf-8-sig")))

#: Table 2d is written from the 177-term discovery panel, which still carries the terms Table 2f
#: records as removed (in_panel=False).  The analysis panel is the 152-term classified file, and
#: that is the set the manuscript's counts come from - verified, not assumed: none of Table 2f's
#: 13 terms appears in it.  So each term is marked here, and the counts are reported for the
#: analysis panel, which is the set that actually needs a category.
analysis_terms = {r["term"] for r in csv.DictReader(
    open(ROOT / "results" / "faers_signals_classified.csv", newline="", encoding="utf-8-sig"))}

out = []
for r in rows:
    term = r["term"]
    if term in X_ARTEFACT:
        cat, reason, conf = "X  non-ocular artefact", X_ARTEFACT[term], "high"
    elif term in B_INFECTION:
        cat, reason, conf = "B  ocular tuberculosis", B_INFECTION[term], "medium"
    elif term in D_COMORBIDITY:
        cat, reason, conf = "D  ocular comorbidity", D_COMORBIDITY[term], "medium"
    elif term in U_REVIEW:
        cat, reason, conf = "U  needs the author", U_REVIEW[term], "author"
    else:
        cat, reason, conf = "T  drug-toxicity spectrum", T_REASON, "high"
    out.append({
        "term": term, "group": r["group"], "a": r["a"], "ror": r["ror"],
        "q_bh": r["q_bh"], "signal_strict": r["signal_strict"],
        "in_analysis_panel": term in analysis_terms,
        "proposed_category": cat, "confidence": conf, "reason": reason,
    })

out.sort(key=lambda d: (not d["in_analysis_panel"], d["proposed_category"], -float(d["ror"] or 0)))
dst = TAB / "Table2d_review_proposed.csv"
with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

inpanel = [d for d in out if d["in_analysis_panel"]]
print("=" * 96)
print(f"terms reviewed: {len(out)}  (Table 2d is written from the 177-term discovery panel)")
print(f"  of these, still in the 152-term analysis panel: {len(inpanel)}"
      f"   already removed per Table 2f: {len(out) - len(inpanel)}")
print("=" * 96)
counts: dict[str, int] = {}
strict: dict[str, int] = {}
for d in inpanel:
    counts[d["proposed_category"]] = counts.get(d["proposed_category"], 0) + 1
    if d["signal_strict"] == "True":
        strict[d["proposed_category"]] = strict.get(d["proposed_category"], 0) + 1
for cat in sorted(counts):
    print(f"  {cat:<32} {counts[cat]:>3} terms   {strict.get(cat, 0):>2} of them strict signals")
print(f"  {'(already removed, no action)':<32} {len(out) - len(inpanel):>3} terms")

print()
print("Already removed by Table 2f, so nothing to decide here:")
print("   " + ", ".join(d["term"] for d in out if not d["in_analysis_panel"]))

print()
print("The terms with no home in the three-list taxonomy (bucket D), which is the finding:")
for d in inpanel:
    if d["proposed_category"].startswith("D"):
        print(f"  {d['term']:<44} a={d['a']:>3}  ROR={float(d['ror']):>9.2f}   {d['reason']}")
print()
print("The terms that need a clinical call rather than a classification call (bucket U):")
for d in inpanel:
    if d["proposed_category"].startswith("U"):
        print(f"  {d['term']:<44} {d['reason']}")
print()
print("Adopting this would move terms into and out of the drug-toxicity spectrum, so the")
print("counts reported from Table 2c would change.  Nothing in src/classify_signals.py has")
print("been modified.")
print(f"\n-> {dst.relative_to(ROOT)}")
