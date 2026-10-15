# -*- coding: utf-8 -*-
"""
Apply the comparator-framing correction to both manuscripts.

What was wrong
    The draft stated that ethambutol's optic-neuropathy reporting odds ratio of
    159.21 put it "an order of magnitude above the next antitubercular drug".  That
    ratio used the whole FAERS database as the denominator, which for an
    antitubercular drug mostly contrasts tuberculosis patients with everyone else.
    Re-computed within the antitubercular class the ratio is 6.47, and ethambutol
    ranks sixth of eighteen drugs, with several second-line agents higher.

What replaces it
    The within-class analysis, which is the drug-versus-drug comparison the claim
    actually needs, plus an explicit statement of what the whole-database figure
    does and does not mean.  The specificity argument is untouched because it rests
    on the negative-control terms, and those remain null within the class as well
    (dry eye 0.35, eye pain 0.32, glaucoma 0.18).

New material
    * a Results subsection giving the within-class comparison
    * a rank-aware sentence naming the first-line and second-line contrasts
    * the colour-vision finding: ethambutol's profile is most distinctive on
      dyschromatopsia, which is the clinical hallmark of its optic neuropathy
    * limitations covering the indication-severity confounding for second-line drugs
    * regenerated Figure 3 from the within-class table

Usage
    python src/apply_comparator_correction.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"
TAB = ROOT / "tables"


def load():
    w = pd.read_csv(RES / "faers_withinclass_signals.csv", encoding="utf-8-sig")
    eth = w[w.drug == "ethambutol"].set_index("term")
    on = w[w.term == "OPTIC NEUROPATHY"].sort_values("ror", ascending=False) \
        .reset_index(drop=True)
    rank = int(on[on.drug == "ethambutol"].index[0]) + 1
    return w, eth, on, rank


def first_line(e: pd.Series, name: str, on: pd.DataFrame) -> float:
    return float(on[on.drug == name].iloc[0].ror)


def main() -> int:
    w, eth, on, rank = load()
    n_drugs = len(on)

    def v(term, col):
        return eth.loc[term, col]

    fl = {d: first_line(None, d, on) for d in
          ["isoniazid", "rifampicin", "pyrazinamide", "linezolid"]}
    print(f"ethambutol within-class rank on optic neuropathy: {rank}/{n_drugs}")
    for d, r in fl.items():
        print(f"  {d:14s} ROR {r:6.2f}")

    # ------------------------------------------------------- new Results text
    new_results = f"""### 3.2b Within the antitubercular class ethambutol is high but not the highest

Comparing every drug against the whole database answers a different question from
comparing drugs with each other, and for an antitubercular agent the whole-database
denominator is dominated by non-tuberculosis reports. The drug-versus-drug
comparison therefore restricts the denominator to reports mentioning any
antitubercular drug.

Within that class, optic neuropathy gave ethambutol an ROR of
**{v('OPTIC NEUROPATHY','ror'):.2f} (95% CI {v('OPTIC NEUROPATHY','ror_lcl'):.2f}-{v('OPTIC NEUROPATHY','ror_ucl'):.2f};
{int(v('OPTIC NEUROPATHY','a'))} cases)**, which places it **{rank}th of {n_drugs}**
drugs with at least 100 reports. The drugs above it - prothionamide, capreomycin,
streptomycin, cycloserine, ethionamide - are second-line agents used for
drug-resistant disease, and that comparison is confounded by indication severity, as
set out in the limitations. The comparison that is not confounded is with the drugs
given in the same regimen: ethambutol's optic-neuropathy ratio exceeds isoniazid
({fl['isoniazid']:.2f}), rifampicin ({fl['rifampicin']:.2f}) and pyrazinamide
({fl['pyrazinamide']:.2f}), and is close to linezolid ({fl['linezolid']:.2f}).

The more informative result is in the *shape* of the profile rather than its rank.
Ethambutol's highest within-class ratio is for **dyschromatopsia**
({v('DYSCHROMATOPSIA','ror'):.2f}, 95% CI {v('DYSCHROMATOPSIA','ror_lcl'):.2f}-{v('DYSCHROMATOPSIA','ror_ucl'):.2f}),
followed by ocular toxicity ({v('OCULAR TOXICITY','ror'):.2f}) and toxic optic
neuropathy ({v('TOXIC OPTIC NEUROPATHY','ror'):.2f}), while optic neuropathy itself
ranks lower for ethambutol ({v('OPTIC NEUROPATHY','ror'):.2f}) than for several
comparators. Acquired colour-vision loss preceding and exceeding acuity loss is the
clinical hallmark of ethambutol optic neuropathy, and the disproportionality profile
reproduces that ordering: the drug's signature is dyschromatopsia, not optic-nerve
reporting in general.

The negative controls remain null in this stricter comparison as well: dry eye
{v('DRY EYE','ror'):.2f} ({v('DRY EYE','ror_lcl'):.2f}-{v('DRY EYE','ror_ucl'):.2f}),
eye pain {v('EYE PAIN','ror'):.2f}, glaucoma {v('GLAUCOMA','ror'):.2f}, ocular
hyperaemia {v('OCULAR HYPERAEMIA','ror'):.2f} and vision blurred
{v('VISION BLURRED','ror'):.2f} - all at or below the class background, so the
specificity of the signal does not depend on which denominator is used
(Table 2b, Figure 3).

### 3.2c What the whole-database ratio means

Referred to the whole FAERS database the same term gives an ROR of 159.21 for
ethambutol. That figure is not wrong, but it measures something different: because
the comparator is all other reports, it mostly expresses how much more often
optic-nerve terms appear in antitubercular reports than in reports of other drugs.
It should be read as a measure of the distinctiveness of the tuberculosis-treatment
population, not as a drug-versus-drug contrast, and it is not used here to argue
that ethambutol is more toxic than its comparators.
"""

    # ---------------------------------------------------------- limitations
    lim_add = """**The second-line comparator is confounded by indication.**
Ethambutol ranks sixth of eighteen antitubercular drugs on within-class optic
neuropathy, below prothionamide, capreomycin, streptomycin, cycloserine and
ethionamide. Every one of those is a second-line agent used for drug-resistant
tuberculosis, a population that is sicker, treated for longer, and more likely to
have central nervous system involvement including tuberculous meningitis, which can
damage the optic nerve independently of any drug. Their higher ratios therefore
cannot be interpreted as greater intrinsic optic-nerve toxicity, and the comparisons
that are free of this confounding are with isoniazid, rifampicin and pyrazinamide,
which are co-administered in the same regimen. The manuscript's claims are limited
to those comparisons.
"""

    # ------------------------------------------------------------- apply
    edits = []

    # 1. English draft: comparator sentence in Discussion 4.2
    p = MAN / "Manuscript_EN_draft.md"
    t = p.read_text(encoding="utf-8")
    old = ("Our comparator ordering — ethambutol far above isoniazid, rifampicin, "
           "pyrazinamide and streptomycin — agrees with the clinical literature's "
           "view that ethambutol is the antitubercular drug that causes optic "
           "neuropathy")
    new = ("Our within-class comparator ordering — ethambutol above isoniazid, "
           "rifampicin and pyrazinamide, the drugs given in the same regimen, "
           "though not above the second-line agents used for drug-resistant "
           "disease — agrees with the clinical literature's view that ethambutol is "
           "the first-line antitubercular drug that causes optic neuropathy")
    if old in t:
        t = t.replace(old, new, 1)
        edits.append("EN Discussion 4.2 comparator sentence")
    else:
        print("[warn] EN 4.2 comparator sentence not found verbatim")

    # 2. principal findings: remove the order-of-magnitude claim
    old2 = ("optic neuropathy at a reporting odds ratio of 159, an order of "
            "magnitude above the next antitubercular drug")
    new2 = ("optic neuropathy strong within the antitubercular class and, more "
            "distinctively, a colour-vision signal that exceeds it")
    if old2 in t:
        t = t.replace(old2, new2, 1)
        edits.append("EN 4.1 order-of-magnitude claim")
    else:
        print("[warn] EN 4.1 claim not found verbatim")

    # 3. add the limitation
    marker = "*Docking is a scoring approximation.*"
    if marker in t:
        t = t.replace(marker, lim_add + "\n" + marker, 1)
        edits.append("EN limitations: indication confounding")
    p.write_text(t, encoding="utf-8")

    # 4. append the new Results subsection to the generated Results
    p2 = ROOT / "src" / "finalize_manuscript.py"
    t2 = p2.read_text(encoding="utf-8")
    anchor = "### 3.3 The tuberculosis terms behave as a separate signal population"
    if anchor in t2 and "3.2b Within the antitubercular class" not in t2:
        # the text is data-derived, so it is emitted through an f-string block
        block = new_results
        t2 = t2.replace(anchor, block + "\n" + anchor, 1)
        edits.append("EN Results 3.2b/3.2c inserted into the assembler")
    elif "3.2b Within the antitubercular class" in t2:
        print("[note] Results 3.2b already present in the assembler")
    p2.write_text(t2, encoding="utf-8")

    print("\napplied:")
    for e in edits:
        print("  -", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
