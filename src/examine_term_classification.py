# -*- coding: utf-8 -*-
"""
Show the two classification columns side by side, for every term.

The table has both a 'group' column, which is anatomical (Optic nerve, Retina / macula,
Visual function, Ocular surface / adnexa, Other ocular), and a 'category' column, which
is interpretive (drug-toxicity spectrum, ocular tuberculosis, non-ocular artefact,
unclassified ocular).  The manuscript reports 83 terms awaiting review under the second,
so the question is which of them are genuinely unplaced and which already carry enough
information to decide.

Printing the two together also exposes terms that are not ocular at all, which matters
because the panel is presented as an ocular one.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
src = pd.read_csv(ROOT / "results" / "faers_signals_annotated.csv",
                  encoding="utf-8-sig")

print("=" * 104)
print("1. The two columns crossed")
print("=" * 104)
ct = pd.crosstab(src.group, src.category)
print(ct.to_string())

print()
print("=" * 104)
print("2. Terms whose group says they are ocular but whose category is unclassified")
print("=" * 104)
unc = src[src.category == "unclassified ocular"]
print(f"  {len(unc)} terms, by anatomical group:")
for g, n in unc.group.value_counts().items():
    print(f"      {str(g):26s} {n:>3}")

print()
print("=" * 104)
print("3. Terms in the panel that are not ocular conditions")
print("=" * 104)
# signs, procedures, routes, systemic conditions and misplacements, identified by
# reading each term rather than by a rule
NOT_OCULAR_CONDITION = {
    "RASH MACULO-PAPULAR": "systemic skin reaction, not ocular",
    "INTESTINAL MUCOSAL TEAR": "gastrointestinal, not ocular",
    "SYSTEMIC SCLEROSIS": "systemic connective-tissue disease",
    "MULTIPLE SCLEROSIS RELAPSE": "neurological disease activity",
    "EXPOSURE VIA EYE CONTACT": "route of exposure, not a reaction",
    "EYE ROLLING": "a sign or behaviour, not an adverse reaction",
    "DECREASED EYE CONTACT": "behavioural or social, not ocular pathology",
    "CHRONIC GRAFT VERSUS HOST DISEASE IN EYE": "systemic disease with ocular "
                                                 "involvement",
    "OCULAR ROSACEA": "dermatological disease with ocular involvement",
    "OCULAR NEOPLASM": "neoplasm, a different disease process from drug toxicity",
    "OPHTHALMIC MIGRAINE": "neurological, not ocular pathology",
    "CATARACT OPERATION COMPLICATION": "a procedural outcome",
    "OCULAR FISTULA": "structural, of uncertain relation to the drug",
    "NEUROMYELITIS OPTICA SPECTRUM DISORDER": "demyelinating disease",
}
print(f"  {'term':46s} {'a':>5s} {'why it is not a drug-toxicity term':44s}")
for _, r in src[src.term.isin(NOT_OCULAR_CONDITION)].sort_values(
        "a", ascending=False).iterrows():
    print(f"  {str(r.term)[:46]:46s} {int(r.a):>5d} "
          f"{NOT_OCULAR_CONDITION[r.term][:44]:44s}")

print()
print("=" * 104)
print("4. Terms that are the drug's known signature but were left unclassified")
print("=" * 104)
SIGNATURE = ["OPTIC NEURITIS RETROBULBAR", "OPTIC DISCS BLURRED",
             "LOSS OF VISUAL CONTRAST SENSITIVITY", "VISUAL FIELD TESTS ABNORMAL",
             "VISUAL ACUITY TESTS ABNORMAL", "OPTIC NERVE CUPPING",
             "RETINAL TOXICITY", "VISUAL BRIGHTNESS", "PUPILLARY DISORDER",
             "PUPILLARY LIGHT REFLEX TESTS ABNORMAL", "IRIS ADHESIONS",
             "IRIDOCELE", "RETINAL INJURY"]
sub = src[src.term.isin(SIGNATURE)].sort_values("ror", ascending=False)
print(f"  {'term':46s} {'a':>5s} {'ror':>9s} {'q_bh':>10s} {'strict':>7s} "
      f"{'group':>22s}")
for _, r in sub.iterrows():
    print(f"  {str(r.term)[:46]:46s} {int(r.a):>5d} {r.ror:>9.2f} "
          f"{r.q_bh:>10.2e} {'yes' if r.signal_strict else 'no':>7s} "
          f"{str(r.group)[:22]:>22s}")

print()
print("=" * 104)
print("5. How much of the signal the unclassified terms carry")
print("=" * 104)
tot = len(src)
strict_all = int(src.signal_strict.sum())
strict_unc = int(unc.signal_strict.sum())
print(f"  panel total                   : {tot} terms")
print(f"  strict signals, whole panel   : {strict_all}")
print(f"  strict signals, unclassified  : {strict_unc}  "
      f"({100*strict_unc/max(strict_all,1):.0f}% of all strict signals)")
print()
print("  So excluding every unclassified term would remove "
      f"{strict_unc} of {strict_all} strict signals;")
print("  the classification matters for the reported profile and cannot be left to")
print("  the reader.")
