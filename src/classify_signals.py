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
    # added in the review: intraocular infection and its sequelae, which every comparator arm
    # shares through the tuberculosis indication, as with the terms above
    "CONJUNCTIVAL GRANULOMA", "INFECTIVE UVEITIS", "NECROTISING RETINITIS",
    "IRIS ADHESIONS", "RETINITIS",
}

# terms that are not ocular at all and entered the panel through a lexical
# artefact of the screening pattern (e.g. "MACULE" is a skin lesion)
NON_OCULAR_ARTEFACT = {
    "MACULE", "RASH MACULAR", "ERYTHEMA NODOSUM",
    # added in the review; all eight are removed from the panel by Table 2f, and listing them
    # here is what makes the 177-term discovery panel carry no unclassified term at all
    "RASH MACULO-PAPULAR", "SYSTEMIC SCLEROSIS", "DECREASED EYE CONTACT",
    "EXPOSURE VIA EYE CONTACT", "EYE ROLLING", "INTESTINAL MUCOSAL TEAR",
    "HALLUCINATION, VISUAL", "MULTIPLE SCLEROSIS RELAPSE",
}

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
    # Added after the review recorded in tables/Table2d_review_proposed.csv.  These 55 terms
    # were in the 177-term discovery panel but in none of the three lists, so they were reported
    # as unclassified while plainly belonging to the drug-related axes.  The clearest case for
    # adopting them was internal: OPTIC ISCHAEMIC NEUROPATHY, OPTIC NEURITIS RETROBULBAR, OPTIC
    # NERVE CUPPING, RETINAL TOXICITY and RETINAL INJURY are optic-nerve and retinal terms
    # sitting in an unclassified list, in a paper whose claim is that the signal is specific to
    # the optic nerve.  Only one of the 55 is a strict signal (RETINAL INJURY, ROR 17.6), so the
    # counts move by one term.
    "OPTIC NEURITIS RETROBULBAR", "RETINAL MICROANGIOPATHY",
    "LOSS OF VISUAL CONTRAST SENSITIVITY", "VISUAL FIELD TESTS ABNORMAL",
    "RETINAL FIBROSIS", "TEAR DISCOLOURATION", "IRIDOCELE", "OPTIC DISCS BLURRED",
    "CONJUNCTIVAL IRRITATION", "CONJUNCTIVAL DISCOLOURATION", "RETINAL INJURY",
    "OPTIC NERVE CUPPING", "PUPILLARY LIGHT REFLEX TESTS ABNORMAL",
    "CORNEAL REFLEX DECREASED", "VISUAL BRIGHTNESS", "VISUAL ACUITY TESTS ABNORMAL",
    "BINOCULAR EYE MOVEMENT DISORDER", "PUPILLARY DISORDER", "IRIS DISORDER",
    "RETINAL VASCULAR DISORDER", "MACULAR DETACHMENT", "CELLULITIS ORBITAL",
    "SCLERAL DISCOLOURATION", "EYELID THICKENING", "CHOROIDAL NEOVASCULARISATION",
    "RETINAL SCAR", "RETINAL PIGMENT EPITHELIOPATHY", "CHOROIDAL EFFUSION",
    "VITREOUS DISORDER", "PUPILS UNEQUAL", "CONJUNCTIVAL OEDEMA", "HALO VISION",
    "LACRIMAL DISORDER", "PUPIL FIXED", "RETINAL TOXICITY", "EYE COLOUR CHANGE",
    "CATARACT NUCLEAR", "OCULAR VASCULAR DISORDER", "RETINAL EXUDATES",
    "SEROUS RETINAL DETACHMENT", "OCULAR HYPERTENSION", "VITREOUS HAEMORRHAGE",
    "CHORIORETINOPATHY", "OPTIC ISCHAEMIC NEUROPATHY", "ABNORMAL SENSATION IN EYE",
    "RETINAL ARTERY OCCLUSION", "RETINAL VEIN OCCLUSION", "PERIORBITAL SWELLING",
    "FOREIGN BODY SENSATION IN EYES", "BLEPHARITIS", "EYE DISCHARGE",
    "SWELLING OF EYELID", "INTRAOCULAR PRESSURE INCREASED",
    "CENTRAL SEROUS CHORIORETINOPATHY", "HEMIANOPIA HOMONYMOUS",
}

#: Ocular findings that are neither drug toxicity nor tuberculosis: trauma, surgery, tumour,
#: a cohort comorbidity, or a symptom code with no localising value.  These are reported and
#: explicitly excluded from the toxicity reading, in the same way as the tuberculosis set, so
#: that they neither inflate the toxicity spectrum nor disappear from it.  Two of them are
#: strict signals (OCULAR FISTULA, CATARACT OPERATION COMPLICATION); excluding them from the
#: toxicity reading does not remove them from the 152-term panel count.
OTHER_OCULAR_EXCLUDED = {
    "OCULAR FISTULA", "ORBITAL APEX SYNDROME", "CONJUNCTIVAL BLEB",
    "CATARACT OPERATION COMPLICATION", "OCULAR ROSACEA", "OCULAR NEOPLASM",
    "EYE INJURY", "EYE CONTUSION", "DIABETIC RETINOPATHY", "TEARFULNESS",
    "EYE INFECTION", "EYE SYMPTOM",
    # the three of this group that Table 2f also removes from the panel; the classifier runs over
    # the 177-term discovery panel, which still contains them, so leaving them out here would
    # leave three terms uncategorised
    "CHRONIC GRAFT VERSUS HOST DISEASE IN EYE", "OPHTHALMIC MIGRAINE",
    "NEUROMYELITIS OPTICA SPECTRUM DISORDER",
}


def classify(term: str) -> str:
    t = str(term).upper()
    if t in NON_OCULAR_ARTEFACT:
        return "non-ocular artefact"
    if t in TB_DISEASE:
        return "ocular tuberculosis (disease)"
    if t in OTHER_OCULAR_EXCLUDED:
        return "other ocular (excluded)"
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

    excluded = df[df.category == "other ocular (excluded)"]
    excluded.to_csv(TAB / "Table2g_other_ocular.csv", index=False,
                    encoding="utf-8-sig")
    print("\n=== other ocular, excluded from the toxicity reading ===")
    print(f"  {len(excluded)} terms, {int(excluded.signal_strict.sum())} of them strict signals")
    print(excluded.nlargest(12, "ror")[["term", "a", "ror", "signal_strict"]]
          .to_string(index=False, max_colwidth=34))

    #: Table 2d is captioned "Anatomical grouping of the panel (152 terms)" in the manuscript,
    #: while the file it wrote held the 83 terms that had no category - a caption that did not
    #: describe its own file.  It now holds what the caption says: one row per anatomical group,
    #: with the number of terms, the number of strict signals, and the group's leading term.
    #: Listing all 152 rows would only duplicate Table 2, which is the same panel in signal order.
    panel_p = RES / "faers_signals_classified.csv"
    if panel_p.exists():
        panel = pd.read_csv(panel_p, encoding="utf-8-sig")
        strict = panel.signal_strict == True  # noqa: E712
        rows_summary = []
        for grp, sub in panel.groupby("group", dropna=False):
            #: lead with the strongest strict signal rather than the largest ratio: a term with a
            #: ratio of 4415 from a single report leads nothing, and would have been the entry
            #: for two of the five groups.
            sig_only = sub[sub.signal_strict == True]  # noqa: E712
            pick = (sig_only if len(sig_only) else sub).sort_values("ror", ascending=False)
            rows_summary.append({
                "group": grp,
                "n_terms": len(sub),
                "n_strict_signals": int((sub.signal_strict == True).sum()),  # noqa: E712
                "leading_signal": pick.iloc[0]["term"],
                "leading_ror": round(float(pick.iloc[0]["ror"]), 2),
                "leading_cases": int(pick.iloc[0]["a"]),
            })
        panel_out = pd.DataFrame(rows_summary).sort_values("n_strict_signals", ascending=False)
        print(f"\n  panel: {len(panel)} terms, {int(strict.sum())} strict signals "
              f"across {len(panel_out)} anatomical groups")
    else:
        panel_out = df[df.category != "unclassified ocular"]
        print("  [note] results/faers_signals_classified.csv absent; using the annotated panel")
    panel_out.to_csv(TAB / "Table2d_panel_anatomical.csv", index=False, encoding="utf-8-sig")
    print(f"-> {TAB / 'Table2d_panel_anatomical.csv'}  "
          f"({len(panel_out)} rows, anatomical grouping)")

    unc = df[df.category == "unclassified ocular"]
    print("\n=== terms with no category ===")
    print(f"  {len(unc)} of {len(df)}"
          + (f": {sorted(unc.term)[:8]}" if len(unc) else " (the review closed the last of them)"))

    stale = TAB / "Table2d_unclassified_terms.csv"
    if stale.exists():
        stale.unlink()
        print(f"  removed the superseded {stale.name}; its content is now "
              f"Table2d_panel_anatomical.csv, which is what the manuscript's caption describes")
    print(f"\n-> {RES / 'faers_signals_annotated.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
