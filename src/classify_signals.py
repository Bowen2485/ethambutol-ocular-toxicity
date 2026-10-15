# -*- coding: utf-8 -*-
"""
Separate the two things the expanded ocular panel captures:

  (i)  drug-induced optic-nerve toxicity  - the ethambutol signal proper
  (ii) ocular tuberculosis               - disease-related terms that share the
       tuberculosis indication with every comparator drug, so they inflate the
       panel without informing drug safety

This classification is applied to the signal table so the manuscript can report
the drug-toxicity spectrum and the disease spectrum separately.  Terms are
assigned by an explicit, auditable list rather than by keyword guessing.

Outputs -> results/faers_signals_annotated.csv, tables/Table2c_toxicity_spectrum.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
TAB = ROOT / "tables"

# mycobacterial / tuberculosis disease manifestations in the eye: present because
# the patient has tuberculosis, and equally expected for every anti-TB drug
TB_DISEASE = {
    "CHOROID TUBERCLES", "TUBERCULOSIS OF EYE", "SERPIGINOUS CHOROIDITIS",
    "CHOROIDITIS", "INTERMEDIATE UVEITIS", "NECROTISING HERPETIC RETINOPATHY",
    "NECROTISING SCLERITIS", "ORBITAL MYOSITIS", "RETINAL VASCULITIS",
    "IRIDOCYCLITIS", "UVEITIS", "VITRITIS", "CHORIORETINITIS",
    "CHORIORETINAL INFLAMMATION",
}

# terms that are not ocular at all and entered the panel through a lexical
# artefact of the screening pattern (e.g. "MACULE" is a skin lesion)
NON_OCULAR_ARTEFACT = {"MACULE", "RASH MACULAR", "ERYTHEMA NODOSUM"}

# the drug-toxicity spectrum: optic nerve, visual function, retina and lens
TOXICITY = {
    "OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "OPTIC NEURITIS",
    "OPTIC ATROPHY", "OPTIC NERVE DISORDER", "OPTIC NERVE INJURY",
    "OPTIC DISC DISORDER", "OPTIC DISC HAEMORRHAGE", "OPTIC DISC HYPERAEMIA",
    "PAPILLOEDEMA", "VISUAL PATHWAY DISORDER", "RETROBULBAR NEURITIS",
    "HEREDITARY OPTIC ATROPHY",
    "BLINDNESS", "BLINDNESS UNILATERAL", "BLINDNESS BILATERAL",
    "BLINDNESS TRANSIENT", "SUDDEN VISUAL LOSS", "VISUAL IMPAIRMENT",
    "VISUAL ACUITY REDUCED", "VISUAL DISTURBANCE", "VISION BLURRED",
    "VISUAL FIELD DEFECT", "SCOTOMA", "HEMIANOPIA", "HEMIANOPIA HETERONYMOUS",
    "QUADRANTANOPIA", "DIPLOPIA", "COLOUR VISION DEFECT", "COLOUR BLINDNESS",
    "COLOUR BLINDNESS ACQUIRED", "COLOUR VISION TESTS ABNORMAL",
    "DYSCHROMATOPSIA", "CHROMATOPSIA", "COLOUR VISION DEFECT",
    "VISUAL EVOKED POTENTIALS ABNORMAL", "VISUAL EVOKED POTENTIAL ABNORMAL",
    "NYSTAGMUS", "AMBLYOPIA", "PHOTOPHOBIA", "PHOTOPSIA", "METAMORPHOPSIA",
    "OPHTHALMOPLEGIA", "OCULOGYRIC CRISIS", "PUPILLARY REFLEX IMPAIRED",
    "EYE MOVEMENT DISORDER", "OCULAR TOXICITY",
    "MACULOPATHY", "MACULAR DEGENERATION", "MACULAR OEDEMA",
    "CYSTOID MACULAR OEDEMA", "RETINOPATHY", "RETINAL DISORDER",
    "RETINAL HAEMORRHAGE", "RETINAL OEDEMA", "RETINAL DETACHMENT",
    "VITREOUS DETACHMENT", "VITREOUS FLOATERS", "VITREOUS OPACITIES",
    "CATARACT", "CATARACT SUBCAPSULAR", "CATARACT OPERATION",
    "CORNEAL OPACITY", "CORNEAL DISORDER", "CORNEAL DEPOSITS",
    "KERATITIS", "CONJUNCTIVAL HYPERAEMIA", "CONJUNCTIVAL HAEMORRHAGE",
    "CONJUNCTIVITIS", "DRY EYE", "EYE PAIN", "EYE IRRITATION",
    "OCULAR HYPERAEMIA", "OCULAR DISCOMFORT", "EYE PRURITUS", "EYE SWELLING",
    "EYELID OEDEMA", "PERIORBITAL OEDEMA", "EYELID PTOSIS", "BLEPHAROSPASM",
    "LACRIMATION INCREASED", "EYE DISORDER", "EYE INFLAMMATION",
    "EYE HAEMORRHAGE", "OCULAR ICTERUS", "GLAUCOMA",
}


def classify(term: str) -> str:
    t = str(term).upper()
    if t in NON_OCULAR_ARTEFACT:
        return "non-ocular artefact"
    if t in TB_DISEASE:
        return "ocular tuberculosis (disease)"
    if t in TOXICITY:
        return "drug-toxicity spectrum"
    return "unclassified ocular"


def main() -> int:
    df = pd.read_csv(RES / "faers_signals_ethambutol.csv", encoding="utf-8-sig")
    df["category"] = df.term.map(classify)
    df = df.sort_values(["category", "ror"], ascending=[True, False])
    df.to_csv(RES / "faers_signals_annotated.csv", index=False,
              encoding="utf-8-sig")

    print("=== signal categories ===")
    print(df.groupby("category").agg(
        n_terms=("term", "size"),
        n_signals=("signal_strict", "sum")).to_string())

    tox = df[(df.category == "drug-toxicity spectrum") & (df.signal_strict == True)]  # noqa: E712
    tox.nlargest(30, "ror").to_csv(TAB / "Table2c_toxicity_spectrum.csv",
                                   index=False, encoding="utf-8-sig")
    print("\n=== leading drug-toxicity-spectrum signals (a >= 3) ===")
    print(tox.nlargest(28, "ror")[["term", "group", "a", "ror", "ror_lcl",
                                   "prr", "ic025", "ebgm05"]]
          .to_string(index=False, max_colwidth=34))

    print("\n=== ocular tuberculosis terms (reported for completeness) ===")
    tb = df[df.category == "ocular tuberculosis (disease)"]
    print(tb.nlargest(12, "ror")[["term", "a", "ror", "ic025", "signal_strict"]]
          .to_string(index=False, max_colwidth=34))

    print("\n=== unclassified terms (need manual review) ===")
    unc = df[df.category == "unclassified ocular"]
    print(f"  {len(unc)} terms; the largest by count:")
    print(unc.nlargest(15, "a")[["term", "a", "ror", "signal_strict"]]
          .to_string(index=False, max_colwidth=34))
    unc.to_csv(TAB / "Table2d_unclassified_terms.csv", index=False,
               encoding="utf-8-sig")
    print(f"\n-> {RES / 'faers_signals_annotated.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
