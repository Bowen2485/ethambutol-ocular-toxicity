# -*- coding: utf-8 -*-
"""
Classify the panel by an objective rule, not by a judgement about causality.

Two earlier attempts failed for the same reason: both asked "is this term evidence of
drug toxicity", which cannot be answered from a term list without assuming the
conclusion.  The second attempt duly labelled optic disc hyperaemia (ratio 232) and
visual pathway disorder (ratio 135) as "not a toxicity candidate", which is not a
defensible reading of those numbers.

The rule used here is anatomical and stated once, so it can be applied by anyone and
disagreed with on its terms:

    group column already assigns every term to Optic nerve, Visual function,
    Retina / macula, Ocular surface / adnexa or Other ocular.  That assignment is
    anatomical and needs no causal judgement.  On top of it, the category column
    already separates ocular tuberculosis - infection manifestations, whose very high
    ratios reflect the disease and not the drug - and non-ocular artefacts.

    The panel is therefore described in four parts, and no term is removed:

        1. optic nerve and visual pathway     (group = Optic nerve)
        2. visual function                    (group = Visual function)
        3. retina and macula                  (group = Retina / macula)
        4. anterior segment, surface, other   (Ocular surface / adnexa, Other ocular)

    with the tuberculosis complications reported separately as a fifth part, excluded
    from the drug-toxicity reading for the reason the manuscript already gives.

This keeps all 177 terms in the panel, keeps all 58 strict signals, and replaces a
causal guess with an anatomical fact plus the manuscript's existing category rule.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
T = ROOT / "tables"

src = pd.read_csv(R / "faers_signals_annotated.csv", encoding="utf-8-sig")

PARTS = {
    "Optic nerve": "1. Optic nerve and visual pathway",
    "Visual function": "2. Visual function",
    "Retina / macula": "3. Retina and macula",
    "Ocular surface / adnexa": "4. Anterior segment and ocular surface",
    "Other ocular": "4. Anterior segment and ocular surface",
}

src["panel_part"] = src.group.map(PARTS).fillna("4. Anterior segment and ocular surface")
src["is_tb_complication"] = src.category == "ocular tuberculosis (disease)"
src["is_nonocular"] = src.category == "non-ocular artefact"
#: the TB complications are reported separately, everything else is the ocular panel
src["in_panel"] = ~src.is_tb_complication

print("=" * 100)
print("1. The panel in four anatomical parts, plus the TB complications separately")
print("=" * 100)
print(f"  {'part':42s} {'terms':>6s} {'strict':>7s} {'signals':>8s}")
for part in sorted(src[src.in_panel].panel_part.unique()):
    sub = src[src.in_panel & (src.panel_part == part)]
    print(f"  {part:42s} {len(sub):>6d} {int(sub.signal_strict.sum()):>7d} "
          f"{int((sub.q_bh <= 0.05).sum()):>8d}")
tb = src[src.is_tb_complication]
print(f"  {'(ocular tuberculosis, excluded from toxicity reading)':42s} "
      f"{len(tb):>6d} {int(tb.signal_strict.sum()):>7d} "
      f"{int((tb.q_bh <= 0.05).sum()):>8d}")

panel = src[src.in_panel]
print()
print(f"  panel total: {len(panel)} terms, {int(panel.signal_strict.sum())} strict "
      f"signals")

print()
print("=" * 100)
print("2. The strict signals in the optic-nerve and visual-function parts")
print("=" * 100)
core = panel[panel.group.isin(["Optic nerve", "Visual function"])
             & panel.signal_strict].sort_values("ror", ascending=False)
print(f"  {'term':42s} {'a':>5s} {'ror':>10s} {'q_bh':>10s} {'part':>34s}")
for _, r in core.iterrows():
    print(f"  {str(r.term)[:42]:42s} {int(r.a):>5d} {r.ror:>10.2f} "
          f"{r.q_bh:>10.2e} {str(r.panel_part)[:34]:>34s}")

print()
print("=" * 100)
print("3. The strict signals in the retina part")
print("=" * 100)
ret = panel[(panel.group == "Retina / macula") & panel.signal_strict].sort_values(
    "ror", ascending=False)
for _, r in ret.iterrows():
    print(f"  {str(r.term)[:42]:42s} {int(r.a):>5d} {r.ror:>10.2f} "
          f"{r.q_bh:>10.2e}")

print()
print("=" * 100)
print("4. The strict signals in the anterior-segment part")
print("=" * 100)
ant = panel[~panel.group.isin(["Optic nerve", "Visual function", "Retina / macula"])
            & panel.signal_strict].sort_values("ror", ascending=False)
for _, r in ant.iterrows():
    print(f"  {str(r.term)[:42]:42s} {int(r.a):>5d} {r.ror:>10.2f} "
          f"{r.q_bh:>10.2e}  ({str(r.group)[:24]})")

print()
print("=" * 100)
print("5. The TB complications, which the manuscript already excludes")
print("=" * 100)
for _, r in tb.sort_values("ror", ascending=False).iterrows():
    print(f"  {str(r.term)[:42]:42s} {int(r.a):>5d} {r.ror:>10.2f} "
          f"{r.q_bh:>10.2e}")

print()
print("=" * 100)
print("6. Summary")
print("=" * 100)
print(f"  panel                       : {len(panel)} terms "
      f"({int(panel.signal_strict.sum())} strict)")
print(f"  optic nerve + visual fn     : "
      f"{int(core.shape[0])} strict signals")
print(f"  retina / macula             : {int(ret.shape[0])} strict signals")
print(f"  anterior segment / other    : {int(ant.shape[0])} strict signals")
print(f"  ocular TB, reported apart   : {len(tb)} terms "
      f"({int(tb.signal_strict.sum())} strict)")
print()
print("  No term is removed from the panel and no causal claim is made about any")
print("  individual term; the parts are anatomical and the TB separation was already")
print("  stated in the manuscript.")

panel.to_csv(R / "faers_signals_classified.csv", index=False, encoding="utf-8-sig")
panel.to_csv(T / "Table2_signals.csv", index=False, encoding="utf-8-sig")
panel[panel.signal_strict].sort_values("q_bh").to_csv(
    T / "Table2b_signals_strict.csv", index=False, encoding="utf-8-sig")
tb.to_csv(T / "Table2e_ocular_tuberculosis.csv", index=False, encoding="utf-8-sig")
print()
print(f"  -> results/faers_signals_classified.csv   ({len(panel)} rows)")
print(f"  -> tables/Table2_signals.csv              ({len(panel)} rows)")
print(f"  -> tables/Table2b_signals_strict.csv      "
      f"({int(panel.signal_strict.sum())} rows)")
print(f"  -> tables/Table2e_ocular_tuberculosis.csv ({len(tb)} rows)")
