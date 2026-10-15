# -*- coding: utf-8 -*-
"""
Separate two questions that the previous attempt ran together.

The first version of this classification asked one question - is this term an eye or
vision finding - and removed 75 of 83 terms on the answer.  That was wrong.  Retinal
artery occlusion is unquestionably an ocular finding, and so are cataract, blepharitis
and raised intraocular pressure; whether they are plausible manifestations of ethambutol
toxicity is a different question, and conflating the two shrank the reported panel from
177 terms to 102 and justified it with the wrong reason.

Two fields are written instead:

    panel_member      whether the term is an eye or vision finding, which is what the
                      panel is described as.  Almost all 177 are; the exception is the
                      handful that are not ocular at all or are not findings - a skin
                      rash, a route of exposure, a behavioural descriptor.

    toxicity_candidate whether the term is a plausible manifestation of drug toxicity,
                      as opposed to a disease the patient may have had independently, an
                      investigation result, a procedure, or a non-specific symptom.
                      This is an interpretation and is labelled as one.

The reported signal counts are computed over the panel; the candidate flag is used to
note which signals could be drug effects and which cannot be attributed on the evidence
available.  Nothing is deleted.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
T = ROOT / "tables"

src = pd.read_csv(R / "faers_signals_annotated.csv", encoding="utf-8-sig")

#: not eye or vision findings at all, or not findings - these leave the panel
NOT_PANEL = {
    "RASH MACULO-PAPULAR": "systemic skin reaction",
    "INTESTINAL MUCOSAL TEAR": "gastrointestinal injury",
    "SYSTEMIC SCLEROSIS": "systemic connective-tissue disease",
    "MULTIPLE SCLEROSIS RELAPSE": "neurological disease activity",
    "NEUROMYELITIS OPTICA SPECTRUM DISORDER": "demyelinating disease",
    "OPHTHALMIC MIGRAINE": "neurological disorder",
    "CHRONIC GRAFT VERSUS HOST DISEASE IN EYE": "systemic disease",
    "EXPOSURE VIA EYE CONTACT": "route of exposure, not a finding",
    "DECREASED EYE CONTACT": "behavioural descriptor",
    "EYE ROLLING": "behaviour, not a finding",
    "EYE SYMPTOM": "no defined content",
    "HALLUCINATION, VISUAL": "psychiatric phenomenon",
}

#: ocular and a plausible manifestation of drug toxicity
TOXICITY = {
    "OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "OPTIC NEURITIS",
    "OPTIC ATROPHY", "OPTIC NERVE DISORDER", "OPTIC NEURITIS RETROBULBAR",
    "OPTIC DISCS BLURRED", "OPTIC NERVE CUPPING", "PAPILLOEDEMA",
    "DYSCHROMATOPSIA", "COLOUR VISION TESTS ABNORMAL", "COLOUR BLINDNESS",
    "ACQUIRED COLOUR VISION DEFICIENCY", "VISUAL ACUITY REDUCED",
    "VISUAL FIELD DEFECT", "HEMIANOPIA", "HEMIANOPIA HOMONYMOUS",
    "HEMIANOPIA HETERONYMOUS", "QUADRANOPIA", "SCOTOMA", "BLINDNESS",
    "BLINDNESS UNILATERAL", "BLINDNESS TRANSIENT", "VISUAL IMPAIRMENT",
    "VISION BLURRED", "VISUAL DISTURBANCE", "DIPLOPIA", "PHOTOPHOBIA",
    "LOSS OF VISUAL CONTRAST SENSITIVITY", "VISUAL BRIGHTNESS",
    "PUPILLARY DISORDER", "PUPILLARY LIGHT REFLEX TESTS ABNORMAL",
    "PUPIL FIXED", "PUPILS UNEQUAL", "OCULAR TOXICITY", "RETINAL TOXICITY",
    "RETINAL INJURY", "RETINAL MICROANGIOPATHY", "MACULOPATHY",
    "CYSTOID MACULAR OEDEMA", "MACULAR DEGENERATION", "MACULE",
    "PAPILLARY DISORDER", "IRIS ADHESIONS", "IRIDOCYCLITIS", "IRIDOCELE",
    "CORNEAL REFLEX DECREASED", "CORNEAL OPACITY", "ORBITAL APEX SYNDROME",
    "OCULAR DISCOMFORT", "EYE PAIN", "OCULAR HYPERAEMIA",
    "CONJUNCTIVAL IRRITATION", "CONJUNCTIVAL HYPERAEMIA", "LACRIMATION INCREASED",
    "DRY EYE", "VISION BLURRED", "PHOTOPSIA", "FLASHES",
}

#: investigation results and procedures - real observations, but not the event itself
INVESTIGATION = {
    "VISUAL ACUITY TESTS ABNORMAL", "VISUAL FIELD TESTS ABNORMAL",
    "OPHTHALMOLOGICAL EXAMINATION ABNORMAL", "FUNDOSCOPY ABNORMAL",
    "CATARACT OPERATION COMPLICATION", "VITRECTOMY",
}

print("=" * 100)
print("1. Terms leaving the panel because they are not eye or vision findings")
print("=" * 100)
leaving = src[src.term.isin(NOT_PANEL)]
print(f"  {len(leaving)} terms")
for _, r in leaving.sort_values("a", ascending=False).iterrows():
    print(f"      {str(r.term)[:52]:54s} a={int(r.a):>4d}  ror={r.ror:>8.2f}  "
          f"({NOT_PANEL[r.term]})")

panel = src[~src.term.isin(NOT_PANEL)].copy()
print()
print(f"  panel after removal: {len(panel)} terms, "
      f"{int(panel.signal_strict.sum())} strict signals")

print()
print("=" * 100)
print("2. Within the panel, which strict signals are toxicity candidates")
print("=" * 100)
panel["toxicity_candidate"] = panel.term.isin(TOXICITY)
panel["is_investigation"] = panel.term.isin(INVESTIGATION)
strict = panel[panel.signal_strict]
cand = strict[strict.toxicity_candidate]
noncand = strict[~strict.toxicity_candidate]
print(f"  strict signals in panel          : {len(strict)}")
print(f"  of which toxicity candidates     : {len(cand)}")
print(f"  of which not toxicity candidates : {len(noncand)}")
print()
print("  The non-candidate strict signals, which are ocular findings but whose "
      "attribution")
print("  to the drug the data cannot support:")
print(f"      {'term':44s} {'a':>5s} {'ror':>9s} {'q_bh':>10s}  reason")
for _, r in noncand.sort_values("ror", ascending=False).iterrows():
    if r.term in INVESTIGATION:
        reason = "investigation or procedure"
    elif r.term in NOT_PANEL:
        reason = "not a finding"
    else:
        reason = "independent disease or non-specific"
    print(f"      {str(r.term)[:44]:44s} {int(r.a):>5d} {r.ror:>9.2f} "
          f"{r.q_bh:>10.2e}  {reason}")

print()
print("=" * 100)
print("3. The candidate strict signals - the drug's plausible signature")
print("=" * 100)
print(f"      {'term':44s} {'a':>5s} {'ror':>9s} {'q_bh':>10s}")
for _, r in cand.sort_values("ror", ascending=False).iterrows():
    print(f"      {str(r.term)[:44]:44s} {int(r.a):>5d} {r.ror:>9.2f} "
          f"{r.q_bh:>10.2e}")

print()
print("=" * 100)
print("4. Summary for the manuscript")
print("=" * 100)
print(f"  panel                       : {len(src)} -> {len(panel)} terms")
print(f"  strict signals              : {int(src.signal_strict.sum())} -> "
      f"{int(panel.signal_strict.sum())}")
print(f"  toxicity-candidate signals  : {len(cand)}")
print(f"  removed from the panel      : {len(NOT_PANEL)} terms "
      f"({int(leaving.signal_strict.sum())} of them strict)")

panel.to_csv(R / "faers_signals_classified.csv", index=False,
             encoding="utf-8-sig")
panel.to_csv(T / "Table2_signals.csv", index=False, encoding="utf-8-sig")
panel[panel.signal_strict].sort_values("q_bh").to_csv(
    T / "Table2b_signals_strict.csv", index=False, encoding="utf-8-sig")
print()
print(f"  -> results/faers_signals_classified.csv  ({len(panel)} rows)")
print(f"  -> tables/Table2_signals.csv             ({len(panel)} rows)")
print(f"  -> tables/Table2b_signals_strict.csv     "
      f"({int(panel.signal_strict.sum())} rows)")
