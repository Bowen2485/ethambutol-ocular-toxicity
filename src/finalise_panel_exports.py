# -*- coding: utf-8 -*-
"""
Write the final table exports and the numbers the manuscript should quote.

Established by reading the source table rather than by classifying by hand:
    the panel holds 177 terms
    14 of them are not ocular findings - 2 the analysis already flagged plus 12 more,
      including a systemic rash with 177 reports, a route-of-exposure term, an
      eye-rolling behaviour and two non-ocular diseases
    12 are ocular tuberculosis manifestations, which the manuscript already excludes
      from the toxicity reading and which occupy the top of the ratio ranking
      (choroid tubercles 2208, serpiginous choroiditis 1474, intermediate uveitis 1472)
    leaving 151 ocular terms of which 44 are strict signals

The manuscript currently says 177 terms and 58 strict signals and describes 83 as
awaiting manual review.  All three statements need correcting, and this writes both the
files and the replacement figures so the text and the tables agree.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
T = ROOT / "tables"

src = pd.read_csv(R / "faers_signals_annotated.csv", encoding="utf-8-sig")

NON_OCULAR = {
    "MACULE", "RASH MACULAR",                     # flagged by the analysis itself
    "RASH MACULO-PAPULAR", "INTESTINAL MUCOSAL TEAR", "SYSTEMIC SCLEROSIS",
    "MULTIPLE SCLEROSIS RELAPSE", "NEUROMYELITIS OPTICA SPECTRUM DISORDER",
    "OPHTHALMIC MIGRAINE", "CHRONIC GRAFT VERSUS HOST DISEASE IN EYE",
    "EXPOSURE VIA EYE CONTACT", "DECREASED EYE CONTACT", "EYE ROLLING",
    "EYE SYMPTOM", "HALLUCINATION, VISUAL",
}
# 'MACULE' is listed by the analysis as a non-ocular artefact, but a macule is also a
# retinal finding.  It is kept on the ocular side and the decision is recorded, because
# removing a term on an ambiguous label would be worse than keeping it and saying so.
NON_OCULAR.discard("MACULE")

src["in_panel"] = ~src.term.isin(NON_OCULAR)
src["is_tb"] = src.category == "ocular tuberculosis (disease)"

nonoc = src[~src.in_panel]
tb = src[src.in_panel & src.is_tb]
oc = src[src.in_panel & ~src.is_tb]

print("=" * 100)
print("Final composition")
print("=" * 100)
print(f"  source table                 : {len(src):>4} terms, "
      f"{int(src.signal_strict.sum()):>3} strict")
print(f"  not ocular findings          : {len(nonoc):>4} terms, "
      f"{int(nonoc.signal_strict.sum()):>3} strict  "
      f"(reported separately, Table 2f)")
print(f"  ocular tuberculosis          : {len(tb):>4} terms, "
      f"{int(tb.signal_strict.sum()):>3} strict  "
      f"(reported separately, Table 2e)")
print(f"  ocular panel                 : {len(oc):>4} terms, "
      f"{int(oc.signal_strict.sum()):>3} strict")

print()
print("=" * 100)
print("The 14 non-ocular terms, and what they were contributing")
print("=" * 100)
print(f"  {'term':46s} {'a':>5s} {'ror':>10s} {'strict':>7s}")
for _, r in nonoc.sort_values("a", ascending=False).iterrows():
    print(f"  {str(r.term)[:46]:46s} {int(r.a):>5d} {r.ror:>10.2f} "
          f"{'yes' if r.signal_strict else 'no':>7s}")

print()
print("=" * 100)
print("The 12 ocular tuberculosis terms, which top the ratio ranking")
print("=" * 100)
print(f"  {'term':46s} {'a':>5s} {'ror':>10s} {'rank in panel':>14s}")
ranked = src.sort_values("ror", ascending=False).reset_index(drop=True)
for _, r in tb.sort_values("ror", ascending=False).iterrows():
    pos = int(ranked[ranked.term == r.term].index[0]) + 1
    print(f"  {str(r.term)[:46]:46s} {int(r.a):>5d} {r.ror:>10.2f} {pos:>14d}")

print()
print("=" * 100)
print("Anatomical composition of the ocular panel")
print("=" * 100)
print(f"  {'group':28s} {'terms':>6s} {'strict':>7s}")
for g, n in oc.group.value_counts().items():
    s = int(oc[oc.group == g].signal_strict.sum())
    print(f"  {str(g):28s} {n:>6d} {s:>7d}")

print()
print("=" * 100)
print("The optic nerve and colour vision terms, which carry the argument")
print("=" * 100)
KEY = ["OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY", "OPTIC NEURITIS",
       "OPTIC ATROPHY", "DYSCHROMATOPSIA", "COLOUR VISION TESTS ABNORMAL",
       "COLOUR BLINDNESS", "VISUAL FIELD DEFECT", "VISION BLURRED", "DRY EYE",
       "CATARACT", "EYE PAIN", "GLAUCOMA"]
for _, r in oc[oc.term.isin(KEY)].sort_values("ror", ascending=False).iterrows():
    print(f"  {str(r.term)[:34]:34s} a={int(r.a):>4d}  ror={r.ror:>9.2f}  "
          f"q={r.q_bh:.2e}  {'strict' if r.signal_strict else ''}")

# ---- write
oc.to_csv(R / "faers_signals_classified.csv", index=False, encoding="utf-8-sig")
oc.to_csv(T / "Table2_signals.csv", index=False, encoding="utf-8-sig")
oc[oc.signal_strict].sort_values("q_bh").to_csv(
    T / "Table2b_signals_strict.csv", index=False, encoding="utf-8-sig")
tb.to_csv(T / "Table2e_ocular_tuberculosis.csv", index=False, encoding="utf-8-sig")
nonoc.to_csv(T / "Table2f_non_ocular_terms.csv", index=False, encoding="utf-8-sig")
print()
print("=" * 100)
print("Written, and the figures the manuscript should quote")
print("=" * 100)
print(f"  tables/Table2_signals.csv               {len(oc)} rows")
print(f"  tables/Table2b_signals_strict.csv       "
      f"{int(oc.signal_strict.sum())} rows")
print(f"  tables/Table2e_ocular_tuberculosis.csv  {len(tb)} rows")
print(f"  tables/Table2f_non_ocular_terms.csv     {len(nonoc)} rows")
print()
print(f"  text should say: {len(oc)} ocular terms, "
      f"{int(oc.signal_strict.sum())} of them strict signals, with {len(tb)} ocular "
      f"tuberculosis manifestations and {len(nonoc)} non-ocular terms reported "
      f"separately.")
