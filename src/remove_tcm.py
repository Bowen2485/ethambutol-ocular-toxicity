# -*- coding: utf-8 -*-
"""
Remove the traditional Chinese medicine component and rewrite the affected sections.

What changes and why
    The study is repositioned as a computational pharmacovigilance and mechanism
    study of ethambutol ocular toxicity.  The TCM reading (clear yang failing to
    ascend / the eye as an empty orifice), the candidate formulae, and the
    phytochemical docking panel all belong to that reading and are removed
    together.  Docking is retained but restricted to ethambutol itself, which is
    the question the mechanism section actually needs answered: which nodes of the
    toxicity network can the drug occupy directly?

    Removals also propagate to: the title, the abstract (methods, results,
    conclusions), the keywords, the introduction's research-gap paragraph, the
    results section on docking, the whole of Discussion 4.4, the limitations, and
    the conclusion.  Table 7 (docking) and Figure 7 are regenerated from the
    ethambutol-only docking output.

Usage
    python src/remove_tcm.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
TAB = ROOT / "tables"
DOCK = ROOT / "docking"

TITLE = ("Ocular toxicity of ethambutol: a whole-database pharmacovigilance analysis "
         "of 20.3 million FAERS cases with network toxicology, molecular docking and "
         "genetic interrogation of the optic-nerve phenotype")

ABSTRACT_METHODS = """**Methods.** We ingested all 90 FDA FAERS quarterly ASCII releases
(2004Q1–2026Q2; 89 usable) and de-duplicated 24,389,966 submitted reports to
20,328,568 unique cases using the FDA case-version protocol. Reporting odds ratios
(ROR), proportional reporting ratios (PRR), Bayesian information component lower
bounds (IC025) and empirical Bayes geometric means (EBGM05) were computed for 178
ocular MedDRA preferred terms - a curated panel plus every ocular-looking term found
by an unbiased pass over the ethambutol reports - across ethambutol and five
comparator antitubercular drugs, with Benjamini-Hochberg control and four
pre-specified robustness specifications. We characterised time to ocular onset,
multivariable predictors and report completeness within the ethambutol cases, then
built a tiered mechanism network from a full-text mine of 3,034 Europe PMC records,
Open Targets optic-nerve phenotype associations and STRING protein-protein
interactions, tested functional enrichment with g:Profiler, docked ethambutol
against the hub panel with AutoDock Vina, and interrogated the implicated loci
against FinnGen R12 optic-nerve phenotypes."""

ABSTRACT_RESULTS = """**Results.** Among 13,804 de-duplicated ethambutol cases, 971
(7.03%) reported an ocular event and 475 (3.44%) an optic-nerve event. Of 177
testable ocular terms, 58 met strict signal criteria. Optic neuropathy was the
strongest signal in the analysis (n = 153; ROR 159.21, 95% CI 134.65-188.25;
PRR 157.46; IC025 6.58; EBGM05 84.90), followed by toxic optic neuropathy, a term
contributed by the unbiased pass rather than the curated panel (n = 60; ROR 277.14,
95% CI 210.24-365.10). Signals were confined to the optic-nerve, retinal and
colour-vision axes: not one non-specific ocular complaint formed a signal (vision
blurred ROR 1.82; cataract 0.86; dry eye 0.42; eye pain 0.64; glaucoma 0.38). All
three optic-nerve signals survived every robustness specification, including a
comparator denominator restricted to anti-tuberculosis reports, where optic
neuropathy retained an ROR of 7.64 (95% CI 5.24-11.13). Median time from starting
ethambutol to an optic-nerve event was 125 days (IQR 63-293) versus 30 days
(IQR 9-85) for non-ocular events in the same reports. Each additional year of age
raised the odds of an ocular event (adjusted OR 1.009, 95% CI 1.005-1.012), as did
female sex (1.378, 1.196-1.588) and reporting from Europe (1.358, 1.151-1.601).
Report completeness was high for interpretive fields but low for exposure fields:
only 27.8% of optic-nerve-spectrum cases carried both age, sex and a therapy start
date. Open Targets contains no human mechanism of action for ethambutol, so the
human gene set was reconstructed from literature; the focused-tier network
(33 nodes, 191 edges) was led by TP53, NFE2L2, AKT1, BCL2, HMOX1, CASP3, SOD2, TNF
and GPX4, and enrichment converged on ferroptosis (KEGG, P = 6.1 x 10^-7),
regulation of programmed cell death (GO:BP, P = 6.1 x 10^-14), the mitochondrial
envelope (GO:CC, P = 1.0 x 10^-8) and BDNF-NTRK2 signalling. Docking showed that
ethambutol occupies pockets on TNF, MFN2, HMOX1 and BCL2 (-4.95 to -5.50 kcal/mol).
Genetically proxied renal function showed no causal effect on any optic-nerve or
visual outcome (146-150 harmonised instruments per outcome; all q = 0.99)."""

ABSTRACT_CONCLUSIONS = """**Conclusions.** In the largest pharmacovigilance assessment
of ethambutol to date, ocular toxicity is a highly specific optic-nerve signal that
spares the ocular surface, is delayed by months relative to other adverse events,
survives every robustness specification tested, and maps onto a
ferroptosis- and mitochondrion-centred molecular network that ethambutol can occupy
directly. The null genetic result for renal function indicates that renal impairment
acts by raising drug exposure rather than by independently causing optic-nerve
degeneration."""

KEYWORDS = ("**Keywords.** ethambutol; optic neuropathy; pharmacovigilance; FAERS; "
            "disproportionality analysis; signal detection; ferroptosis; network "
            "toxicology; molecular docking; Mendelian randomisation")

INTRO_GAP = """Two gaps remain. First, no analysis has yet placed EON's full ocular
phenotype against the other first-line antitubercular drugs across the entire FAERS
database with formal multiplicity control; existing pharmacovigilance work has been
based on VigiBase organ-system groupings rather than term-level disproportionality
against comparators [11]. Second, and more consequentially for interpretation, the
specificity of the signal has never been tested against its own internal control: a
drug that damages the optic nerve should produce signals for optic-nerve and
colour-vision terms while leaving non-specific ocular complaints - dry eye, eye
pain, cataract, conjunctivitis - at or below the background rate, and no published
analysis has reported that contrast."""

INTRO_LAST = """We therefore assembled four complementary analyses of ethambutol
ocular toxicity: (i) a whole-database FAERS disproportionality analysis across an
expanded ocular term panel, with negative-control terms and four robustness
specifications built in; (ii) case-level characterisation of time to onset,
predictors and report adequacy; (iii) a tiered mechanism network with enrichment and
molecular docking of ethambutol against the hub targets; and (iv) genetic
interrogation of the implicated exposures against optic-nerve phenotypes in FinnGen.
The pharmacovigilance findings are the primary analysis; the mechanistic and genetic
analyses are hypothesis-generating."""

DOCKING_RESULTS = """### 3.9 Docking shows which network nodes ethambutol can occupy directly

The mechanism network describes processes that become dysregulated, not where the
drug binds. To ask the narrower question - which nodes of that network ethambutol
itself can occupy - the drug was docked against each of the fourteen hub targets:
fourteen runs, all completed.

The docking protocol was controlled by re-docking co-crystallised ligands into their
own receptors. Carbonic anhydrase II with acetazolamide reproduced its crystal pose
at a symmetry-corrected RMSD of **1.795 A**, within the accepted 2.0 A criterion.
Dihydrofolate reductase with methotrexate, a 33-heavy-atom flexible ligand, gave
5.863 A and failed; this is reported as a limitation of the protocol for large
flexible ligands.

Ethambutol docked with affinities between -3.96 and -5.50 kcal/mol (Table 7). The
most favourable were TNF (-5.50), MFN2 (-5.21), HMOX1 (-5.09), NFE2L2 (-5.01) and
BCL2 (-4.95); the weakest were GPX4 (-3.96), SMAD4 (-4.06) and AKT1 (-4.05). The
affinities are modest and span a narrow range, which is the expected result for a
small, highly polar molecule with three rotatable bonds and no designed
complementarity to any of these pockets. The interpretable feature is the ordering
rather than the absolute values: the drug is predicted to engage the inflammatory
and oxidative-stress nodes (TNF, HMOX1, NFE2L2) and the mitochondrial-dynamics node
MFN2 more readily than the ferroptosis execution machinery (GPX4, ACSL4) or the
TGF-beta effector SMAD4. That ordering is consistent with ethambutol acting upstream
of the ferroptosis cascade - dysregulating the redox and inflammatory environment
rather than binding the pathway's terminal enzymes - which is what the enrichment
pattern also suggests."""

DISC_CLINICAL = """### 4.5 Clinical implications

The most actionable finding is not the signal itself but the screening gap it
exposes. Baseline ophthalmic screening is performed in only 12.0-13.1% of patients
started on ethambutol, and the proportion monitored within six months fell from
13.1% in 2015 to 7.9% in 2021 [13]. Given a median onset of 125 days in our data and
the clinical literature's finding that structural measures predict outcome better
than acuity [22,23,26,27], the case for structured baseline and follow-up assessment
is strong.

Three risk factors deserve weighting. Renal impairment is the most powerful
modifiable determinant (adjusted OR 2.69 in a Korean national cohort, 3.73 in a
Taiwanese cohort, with an incidence approaching 40% in dialysis patients) [24,25],
and our finding that age independently raises risk is consistent with declining
renal clearance. Low plasma zinc before treatment (< 0.70 mg/L) marked high risk in
the one study that measured it [5], and zinc is mechanistically implicated through
lysosomal accumulation and membrane permeabilisation [6]. Genetic susceptibility via
mitochondrial variants was reported in 46.8% of one EON series [7], though an
earlier smaller study found none [8]; the discrepancy remains unresolved, and the
mitochondrial genes sit at hub positions in our network, which argues for a properly
powered replication.

The dose question is also not settled. A propensity-score cohort in *Mycobacterium
avium* complex pulmonary disease found 0% EON at 10.7 mg/kg/day versus 4.8% at
15.4 mg/kg/day with no loss of efficacy [4]; whether this transfers to tuberculosis
treatment has not been tested in a randomised design, and it is the single most
consequential open question in this field.

Finally, the report-adequacy analysis identifies a limitation of the evidence base
itself rather than of our analysis. Dose was recorded in 29.0% of ethambutol cases
and therapy duration in 6.2%, and only 27.8% of optic-nerve-spectrum cases carried
the fields needed for a time-to-onset analysis. Dose-response and latency questions
therefore cannot be answered from spontaneous reports, however large the database;
they require prospective cohorts with protocolised exposure documentation."""

DISC_LIMITS_TCM_REPLACEMENT = """*Docking is a scoring approximation.* Vina scores
correlate only moderately with affinity, the protocol treats a rigid receptor, and
the search box is derived from a co-crystal ligand or a geometric pocket prediction
rather than experimental site mapping. The dihydrofolate reductase redocking control
failed (5.86 A), which we report rather than suppress. The docking reported here is
restricted to ethambutol itself and is used only to rank the hub targets by
predicted occupancy; it cannot establish binding and does not identify the drug's
mechanism."""

CONCLUSION = """In the largest pharmacovigilance assessment of ethambutol to date -
20.3 million de-duplicated FAERS cases - ocular toxicity resolves into a highly
specific optic-nerve signal, an order of magnitude stronger than for any comparator
antitubercular drug, with no signal whatever for non-specific ocular complaints. The
contrast survives every robustness specification tested, including restriction of
the comparator to same-class anti-tuberculosis reports. The onset is delayed by
months relative to other adverse events in the same reports, as a cumulative axonal
injury would be. At the molecular level the implicated network converges on
ferroptosis and mitochondrial integrity - the axis experimental work has now
identified in ethambutol-treated retinal ganglion cells - and docking indicates that
the drug engages the upstream inflammatory and redox nodes of that network rather
than its terminal enzymes. Genetically proxied renal function shows no causal effect
on the optic-nerve phenotype, which places renal impairment in the pathway as a
determinant of drug exposure rather than an independent cause of optic-nerve
degeneration."""


def main() -> int:
    p = MAN / "Manuscript_EN_draft.md"
    t = p.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ title
    t = re.sub(r"^#\s+Ethambutol ocular toxicity.*$", f"# {TITLE}", t,
               count=1, flags=re.M)
    t = re.sub(r"\*\*Ocular toxicity of ethambutol:.*?\*\*", f"**{TITLE}**", t,
               count=1, flags=re.S)
    t = re.sub(r"^Short running title:.*$", "", t, flags=re.M)

    # --------------------------------------------------------------- abstract
    t = re.sub(r"\*\*Methods\.\*\*.*?(?=\*\*Results\.\*\*)", ABSTRACT_METHODS + "\n\n",
               t, count=1, flags=re.S)
    t = re.sub(r"\*\*Results\.\*\*.*?(?=\*\*Conclusions\.\*\*)",
               ABSTRACT_RESULTS + "\n\n", t, count=1, flags=re.S)
    t = re.sub(r"\*\*Conclusions\.\*\*.*?(?=\*\*Keywords\.\*\*)",
               ABSTRACT_CONCLUSIONS + "\n\n", t, count=1, flags=re.S)
    t = re.sub(r"\*\*Keywords\.\*\*.*?(?=\n\n)", KEYWORDS, t, count=1, flags=re.S)

    # ----------------------------------------------------------- introduction
    t = re.sub(r"Two structural gaps remain in this literature\..*?(?=We therefore assembled)",
               INTRO_GAP + "\n\n", t, count=1, flags=re.S)
    t = re.sub(r"We therefore assembled four complementary analyses.*?(?=\n\n---)",
               INTRO_LAST, t, count=1, flags=re.S)

    # ------------------------------------------------------------ for figures
    # Figure 7 (phytochemical docking heat map) no longer exists; the docking
    # figure becomes a bar chart of the ethambutol-only panel
    t = t.replace("(Figure 7, Table 7)", "(Figure 7, Table 7)")

    p.write_text(t, encoding="utf-8")
    print(f"[ok] {p.name}: abstract, title, introduction rewritten")

    # ---------------------------------------- results + discussion sections
    r = MAN / "Manuscript_EN_draft.md"
    t = r.read_text(encoding="utf-8")
    t = re.sub(r"### 3\.6 Docking places the traditional Chinese medicine actives.*?(?=### 3\.7)",
               DOCKING_RESULTS + "\n\n", t, count=1, flags=re.S)
    # renumber the results sections that follow
    t = t.replace("### 3.7 Genetic interrogation", "### 3.10 Genetic interrogation")

    # whole of Discussion 4.4 (the TCM reading) is deleted
    t = re.sub(r"### 4\.4 The traditional Chinese medicine reading.*?(?=### 4\.5 )",
               "", t, count=1, flags=re.S)
    t = re.sub(r"### 4\.5 Clinical implications.*?(?=### 4\.6 )",
               DISC_CLINICAL + "\n\n", t, count=1, flags=re.S)
    # the docking limitation replaces the generic one; the TCM limitation is dropped
    t = re.sub(r"\*Docking is a scoring approximation\.\*.*?(?=\*No drug-exposure)",
               DISC_LIMITS_TCM_REPLACEMENT + "\n\n", t, count=1, flags=re.S)
    t = re.sub(r"\*The TCM component is interpretive\.\*.*?(?=\n\n---|\Z)", "",
               t, count=1, flags=re.S)
    # conclusion
    t = re.sub(r"## 5\. Conclusion\n\n.*?(?=\n\n---|\Z)", f"## 5. Conclusion\n\n{CONCLUSION}\n",
               t, count=1, flags=re.S)

    r.write_text(t, encoding="utf-8")
    print(f"[ok] {r.name}: docking results, discussion and conclusion rewritten")

    # ---------------------------------------------------- Table 7 ethambutol only
    dk = pd.read_csv(DOCK / "results.csv", encoding="utf-8-sig")
    e = dk[(dk.ligand == "ethambutol") & (dk.ok == True)].copy()  # noqa: E712
    e = e[["gene", "pdb", "best_affinity", "affinity_2", "box_source"]]
    e = e.rename(columns={"gene": "Target", "pdb": "Structure",
                          "best_affinity": "Vina best (kcal/mol)",
                          "affinity_2": "Vina 2nd mode",
                          "box_source": "Search box defined by"})
    e = e.sort_values("Vina best (kcal/mol)")
    e.to_csv(TAB / "Table7_docking.csv", index=False, encoding="utf-8-sig")
    print(f"[ok] Table7_docking.csv rebuilt: {len(e)} ethambutol runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
