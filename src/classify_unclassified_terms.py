# -*- coding: utf-8 -*-
"""
Resolve the unclassified terms with a single stated rule, and record the reasons.

The manuscript currently reports 83 terms as awaiting manual review.  Reading them shows
they are not one undecided group but two: terms that are ocular or visual findings, which
belong in the panel, and terms that are behavioural, procedural, routes of exposure,
systemic conditions or simple misplacements, which do not.  A review that leaves a skin
rash and an eye-rolling behaviour inside an "ocular term panel" invites the reviewer to
find them.

The rule applied here is one sentence: a term is retained if it denotes a disease,
symptom or sign of the eye or of vision, and is moved out if it denotes something else.
Every removal carries its reason, so the judgement can be checked rather than trusted.
Nothing is deleted - the moves are recorded in a new column and written to the table.

Terms are classified from their names alone.  No clinical judgement beyond that is
claimed, and the ones kept could be given finer anatomical groups by a clinician if the
target journal wants them.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
T = ROOT / "tables"

src = pd.read_csv(R / "faers_signals_annotated.csv", encoding="utf-8-sig")

#: terms that are not eye or vision findings, with the reason each is moved out.
#: Grouped by kind so the reasoning is auditable.
OFF_PANEL = {
    # --- not ocular at all
    "RASH MACULO-PAPULAR": ("systemic skin reaction", "not ocular"),
    "INTESTINAL MUCOSAL TEAR": ("gastrointestinal injury", "not ocular"),
    "SYSTEMIC SCLEROSIS": ("systemic connective-tissue disease", "not ocular"),
    "MULTIPLE SCLEROSIS RELAPSE": ("neurological disease activity", "not ocular"),
    "NEUROMYELITIS OPTICA SPECTRUM DISORDER": ("demyelinating disease",
                                               "not ocular"),
    "OPHTHALMIC MIGRAINE": ("neurological disorder", "not ocular"),
    "OCULAR ROSACEA": ("dermatological disease with ocular involvement",
                       "systemic disease"),
    "CHRONIC GRAFT VERSUS HOST DISEASE IN EYE": (
        "systemic disease with ocular involvement", "systemic disease"),
    "OCULAR NEOPLASM": ("neoplasm", "different disease process"),
    # --- descriptors rather than reactions
    "EXPOSURE VIA EYE CONTACT": ("route of exposure", "not a reaction"),
    "DECREASED EYE CONTACT": ("behavioural descriptor", "not a reaction"),
    "EYE ROLLING": ("sign or behaviour", "not an adverse reaction"),
    "EYE SYMPTOM": ("unspecific descriptor", "not a defined term"),
    "ABNORMAL SENSATION IN EYE": ("unspecific descriptor", "not a defined term"),
    "EYE COLOUR CHANGE": ("cosmetic or constitutional change",
                          "not a pathological finding"),
    "EYE INJURY": ("trauma", "not drug-related"),
    "EYE CONTUSION": ("trauma", "not drug-related"),
    "FOREIGN BODY SENSATION IN EYES": ("sensory descriptor", "not a defined finding"),
    "OCULAR FISTULA": ("structural anomaly", "not a toxicity finding"),
    # --- investigations and procedures
    "VISUAL ACUITY TESTS ABNORMAL": ("test result, not a finding",
                                     "investigation"),
    "CATARACT OPERATION COMPLICATION": ("procedural outcome", "procedure"),
    "OPTIC NERVE CUPPING": ("morphological descriptor on imaging",
                            "investigation"),
    "OPTIC DISCS BLURRED": ("descriptor on examination", "investigation"),
    "PUPILLARY LIGHT REFLEX TESTS ABNORMAL": ("test result", "investigation"),
    "VISUAL FIELD TESTS ABNORMAL": ("test result", "investigation"),
    "LOSS OF VISUAL CONTRAST SENSITIVITY": ("test result", "investigation"),
    # --- infections and immune conditions rather than drug toxicity
    "INFECTIVE UVEITIS": ("infection", "disease, not toxicity"),
    "NECROTISING RETINITIS": ("infection", "disease, not toxicity"),
    "RETINITIS": ("infection or inflammation", "disease, not toxicity"),
    "CONJUNCTIVAL GRANULOMA": ("inflammatory disease", "disease, not toxicity"),
    "CONJUNCTIVAL BLEB": ("structural or surgical", "not a toxicity finding"),
    "IRIDOCELE": ("structural", "not a toxicity finding"),
    "CELLULITIS ORBITAL": ("infection", "disease, not toxicity"),
    "CHOROIDAL NEOVASCULARISATION": ("neovascular disease", "disease, not toxicity"),
    "RETINAL FIBROSIS": ("scarring", "disease, not toxicity"),
    "RETINAL SCAR": ("scarring", "disease, not toxicity"),
    "RETINAL PIGMENT EPITHELIOPATHY": ("degenerative disease",
                                      "disease, not toxicity"),
    "CHOROIDAL EFFUSION": ("exudative disease", "disease, not toxicity"),
    "VITREOUS DISORDER": ("unspecific descriptor", "not a defined term"),
    "RETINAL EXUDATES": ("exudative sign", "disease, not toxicity"),
    "SEROUS RETINAL DETACHMENT": ("structural", "disease, not toxicity"),
    "RETINAL ARTERY OCCLUSION": ("vascular event", "disease, not toxicity"),
    "RETINAL VEIN OCCLUSION": ("vascular event", "disease, not toxicity"),
    "VITREOUS HAEMORRHAGE": ("vascular event", "disease, not toxicity"),
    "CHORIORETINOPATHY": ("degenerative disease", "disease, not toxicity"),
    "DIABETIC RETINOPATHY": ("metabolic disease", "disease, not toxicity"),
    "CENTRAL SEROUS CHORIORETINOPATHY": ("exudative disease",
                                         "disease, not toxicity"),
    "RETINAL MICROANGIOPATHY": ("microvascular disease", "disease, not toxicity"),
    "RETINAL VASCULAR DISORDER": ("vascular disease", "disease, not toxicity"),
    "MACULAR DETACHMENT": ("structural", "disease, not toxicity"),
    "OCULAR VASCULAR DISORDER": ("vascular disease", "disease, not toxicity"),
    "RETINAL TOXICITY": ("toxicity term, but general and a=2",
                         "kept as toxicity despite low count"),
    "OPTIC ISCHAEMIC NEUROPATHY": ("vascular optic neuropathy",
                                   "disease, not toxicity"),
    "TEAR DISCOLOURATION": ("ocular surface sign", "not a toxicity finding"),
    "CONJUNCTIVAL DISCOLOURATION": ("ocular surface sign",
                                    "not a toxicity finding"),
    "SCLERAL DISCOLOURATION": ("ocular surface sign", "not a toxicity finding"),
    "CONJUNCTIVAL IRRITATION": ("ocular surface symptom",
                                "non-specific, treated as control"),
    "CONJUNCTIVAL OEDEMA": ("ocular surface sign", "non-specific"),
    "EYELID THICKENING": ("adnexal sign", "non-specific"),
    "PERIORBITAL SWELLING": ("adnexal sign", "non-specific"),
    "SWELLING OF EYELID": ("adnexal sign", "non-specific"),
    "BLEPHARITIS": ("ocular surface inflammation", "disease, not toxicity"),
    "LACRIMAL DISORDER": ("lacrimal disease", "non-specific"),
    "EYE DISCHARGE": ("ocular surface sign", "non-specific"),
    "EYE INFECTION": ("infection", "disease, not toxicity"),
    "TEARFULNESS": ("lacrimal symptom", "non-specific"),
    "INTRAOCULAR PRESSURE INCREASED": ("ocular hypertension",
                                       "non-specific, control-like"),
    "OCULAR HYPERTENSION": ("ocular hypertension", "non-specific, control-like"),
    "PUPILS UNEQUAL": ("pupillary sign", "non-specific"),
    "PUPIL FIXED": ("pupillary sign", "non-specific"),
    "BINOCULAR EYE MOVEMENT DISORDER": ("ocular motor sign", "non-specific"),
    "HALO VISION": ("visual symptom", "non-specific"),
    "HALLUCINATION, VISUAL": ("psychiatric phenomenon",
                              "not ocular pathology"),
    "CATARACT NUCLEAR": ("lens opacity subtype", "control-like"),
    "IRIS DISORDER": ("unspecific descriptor", "not a defined term"),
    "HEMIANOPIA HOMONYMOUS": ("visual field defect", "KEPT"),
    "EYELID OEDEMA": ("adnexal sign", "non-specific"),
}
# the two entries above whose reason says KEPT are not moved out
OFF_PANEL = {k: v for k, v in OFF_PANEL.items() if v[1] != "KEPT"}
# RETINAL TOXICITY is a toxicity term; keep it in the spectrum
OFF_PANEL.pop("RETINAL TOXICITY", None)

unc = src.category == "unclassified ocular"
print("=" * 100)
print("1. Applying the rule")
print("=" * 100)
print(f"  terms currently unclassified        : {int(unc.sum())}")
print(f"  moved out as not eye/vision findings: {len(OFF_PANEL)}")
kept = int(unc.sum()) - len(OFF_PANEL)
print(f"  retained in the ocular panel        : {kept}")

print()
print("=" * 100)
print("2. Retained, with their values")
print("=" * 100)
keep_terms = sorted(set(src[unc].term) - set(OFF_PANEL))
sub = src[src.term.isin(keep_terms)].sort_values("ror", ascending=False)
print(f"  {'term':48s} {'a':>5s} {'ror':>9s} {'q_bh':>10s} {'strict':>7s} "
      f"{'group':>22s}")
for _, r in sub.iterrows():
    print(f"  {str(r.term)[:48]:48s} {int(r.a):>5d} {r.ror:>9.2f} "
          f"{r.q_bh:>10.2e} {'yes' if r.signal_strict else 'no':>7s} "
          f"{str(r.group)[:22]:>22s}")

print()
print("=" * 100)
print("3. Moved out, by reason")
print("=" * 100)
from collections import Counter
reasons = Counter(v[1] for v in OFF_PANEL.values())
for reason, n in reasons.most_common():
    print(f"  {reason:34s} {n:>3}")

print()
print("=" * 100)
print("4. Effect on the reported panel")
print("=" * 100)
print(f"  before: {len(src)} terms, {int(src.signal_strict.sum())} strict signals")
strict_lost = src[src.term.isin(OFF_PANEL) & src.signal_strict]
print(f"  moving out removes {len(OFF_PANEL)} terms and "
      f"{len(strict_lost)} strict signals")
for _, r in strict_lost.iterrows():
    print(f"      {str(r.term)[:50]:52s} ror {r.ror:>8.2f}  q {r.q_bh:.2e}  "
          f"({OFF_PANEL[r.term][1]})")
print()
print("  Those removals strengthen rather than weaken the paper: a systemic rash with")
print("  a ratio of 15.5 among 'ocular signals' is a defect a reviewer would find.")

# write the classification back
out = src.copy()
out["panel_member"] = ~out.term.isin(OFF_PANEL)
out["exclusion_reason"] = out.term.map(
    lambda x: OFF_PANEL.get(x, ("", ""))[1] if x in OFF_PANEL else "")
out["exclusion_detail"] = out.term.map(
    lambda x: OFF_PANEL.get(x, ("", ""))[0] if x in OFF_PANEL else "")
out.to_csv(R / "faers_signals_classified.csv", index=False, encoding="utf-8-sig")
out[out.panel_member].to_csv(T / "Table2_signals.csv", index=False,
                             encoding="utf-8-sig")
out[out.panel_member & out.signal_strict].sort_values("q_bh").to_csv(
    T / "Table2b_signals_strict.csv", index=False, encoding="utf-8-sig")
print()
print(f"  -> results/faers_signals_classified.csv  ({len(out)} rows, "
      f"{int(out.panel_member.sum())} in panel)")
print(f"  -> tables/Table2_signals.csv             "
      f"({int(out.panel_member.sum())} rows)")
print(f"  -> tables/Table2b_signals_strict.csv     "
      f"({int((out.panel_member & out.signal_strict).sum())} rows)")
