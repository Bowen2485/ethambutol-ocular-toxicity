# -*- coding: utf-8 -*-
"""
Establish precisely which panel terms are not ocular, using the source table's own flag.

Three classification attempts have been made and the first two were wrong, so the last
one is grounded in a column that already exists: the analysis itself set category =
'non-ocular artefact' for terms it recognised as belonging to something other than the
eye.  That label is the starting point, not a judgement invented here.

This reports the terms so labelled, checks whether any ocular term was left out of the
panel, and produces the counts the manuscript needs.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
T = ROOT / "tables"

src = pd.read_csv(R / "faers_signals_annotated.csv", encoding="utf-8-sig")

print("=" * 100)
print("1. The source table's own categories")
print("=" * 100)
print(src.category.value_counts().to_string())

print()
print("=" * 100)
print("2. Terms the source flags as non-ocular artefacts")
print("=" * 100)
art = src[src.category == "non-ocular artefact"]
print(f"  {len(art)} term(s)")
for _, r in art.iterrows():
    print(f"      {str(r.term)[:56]:58s} a={int(r.a):>4d}  ror={r.ror:>9.2f}  "
          f"q={r.q_bh:.2e}  group={r.group}")

print()
print("=" * 100)
print("3. Terms whose group is an ocular one but whose term is plainly not ocular")
print("=" * 100)
# identified by reading the term list; each carries the reason
EXTRA_NOT_OCULAR = {
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
    "EYE SYMPTOM": "no defined clinical content",
    "HALLUCINATION, VISUAL": "psychiatric phenomenon",
}
found = src[src.term.isin(EXTRA_NOT_OCULAR)]
not_currently_flagged = found[found.category != "non-ocular artefact"]
print(f"  {len(EXTRA_NOT_OCULAR)} term(s) identified, of which "
      f"{len(not_currently_flagged)} are not flagged by the source")
print()
print(f"  {'term':48s} {'a':>5s} {'ror':>9s} {'flagged already':>16s}  reason")
for _, r in found.sort_values("a", ascending=False).iterrows():
    print(f"  {str(r.term)[:48]:48s} {int(r.a):>5d} {r.ror:>9.2f} "
          f"{'yes' if r.category == 'non-ocular artefact' else 'NO':>16s}  "
          f"{EXTRA_NOT_OCULAR[r.term]}")

print()
print("=" * 100)
print("4. The effect on the reported counts")
print("=" * 100)
all_nonocular = set(art.term) | set(EXTRA_NOT_OCULAR)
panel = src[~src.term.isin(all_nonocular)]
tb = panel[panel.category == "ocular tuberculosis (disease)"]
oc = panel[panel.category != "ocular tuberculosis (disease)"]
print(f"  source table                 : {len(src)} terms, "
      f"{int(src.signal_strict.sum())} strict")
print(f"  non-ocular terms             : {len(all_nonocular)} "
      f"({int(src[src.term.isin(all_nonocular)].signal_strict.sum())} strict)")
print(f"  ocular tuberculosis          : {len(tb)} terms, "
      f"{int(tb.signal_strict.sum())} strict")
print(f"  ocular panel                 : {len(oc)} terms, "
      f"{int(oc.signal_strict.sum())} strict")
print()
print("  Strict signals among the non-ocular terms that would leave:")
for _, r in src[src.term.isin(all_nonocular) & src.signal_strict].sort_values(
        "ror", ascending=False).iterrows():
    print(f"      {str(r.term)[:48]:50s} ror {r.ror:>9.2f}  q {r.q_bh:.2e}")

print()
print("=" * 100)
print("5. Anatomical composition of the ocular panel")
print("=" * 100)
print(f"  {'group':30s} {'terms':>6s} {'strict':>7s}")
for g, n in oc.group.value_counts().items():
    s = int(oc[oc.group == g].signal_strict.sum())
    print(f"  {str(g):30s} {n:>6d} {s:>7d}")

print()
print("=" * 100)
print("6. What the 83 previously 'unclassified' terms actually are")
print("=" * 100)
unc = src[src.category == "unclassified ocular"]
print(f"  {len(unc)} terms carry no toxicity-versus-disease category, and their")
print("  anatomical group breaks down as:")
for g, n in unc.group.value_counts().items():
    print(f"      {str(g):30s} {n:>4}")
print()
print(f"  of which not ocular by the rule above: "
      f"{len(unc[unc.term.isin(all_nonocular)])}")
print(f"  of which strict signals: {int(unc.signal_strict.sum())}")
print()
print("  So they are not one undecided group: they are ocular terms whose anatomical")
print("  group is already assigned and whose toxicity-versus-disease category was")
print("  never needed, mixed with a few terms that should not be in the panel at all.")

# write the corrected exports
oc.to_csv(R / "faers_signals_classified.csv", index=False, encoding="utf-8-sig")
oc.to_csv(T / "Table2_signals.csv", index=False, encoding="utf-8-sig")
oc[oc.signal_strict].sort_values("q_bh").to_csv(
    T / "Table2b_signals_strict.csv", index=False, encoding="utf-8-sig")
tb.to_csv(T / "Table2e_ocular_tuberculosis.csv", index=False, encoding="utf-8-sig")
src[src.term.isin(all_nonocular)].to_csv(
    T / "Table2f_non_ocular_terms.csv", index=False, encoding="utf-8-sig")
print()
print(f"  -> tables/Table2_signals.csv              ({len(oc)} rows)")
print(f"  -> tables/Table2b_signals_strict.csv      "
      f"({int(oc.signal_strict.sum())} rows)")
print(f"  -> tables/Table2e_ocular_tuberculosis.csv ({len(tb)} rows)")
print(f"  -> tables/Table2f_non_ocular_terms.csv    ({len(all_nonocular)} rows)")
