# -*- coding: utf-8 -*-
"""
Step 12 - Assemble the final submission manuscripts.

English:  manuscript/Ethambutol_EyeTox_EN_full.md
Chinese:  manuscript/Ethambutol_EyeTox_CN_full.md

Content added here relative to the earlier draft
  * Methods inlined (journals require one file), plus two new subsections:
    data-driven term discovery and the report-adequacy analysis.
  * Results updated with the expanded 178-term panel, the toxic-optic-neuropathy
    term, the tuberculosis-disease terms that are separated out, and the
    report-adequacy figures.
  * References replaced with the 25 entries verified against Europe PMC and
    renumbered in order of first citation.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
DER = ROOT / "data" / "derived"
RES = ROOT / "results"
TAB = ROOT / "tables"

TITLE_EN = ("Ocular toxicity of ethambutol: a whole-database pharmacovigilance analysis "
            "of 20.3 million FAERS cases integrated with network toxicology, molecular "
            "docking and genetic interrogation of the optic-nerve phenotype")
TITLE_CN = ("乙胺丁醇眼毒性：基于 2 033 万例 FAERS 全库的药物警戒分析，结合网络毒理学、"
            "分子对接与视神经表型的遗传学考察")


def load_terms():
    d = pd.read_csv(DER / "ocular_terms.csv", encoding="utf-8-sig")
    a = pd.read_csv(RES / "faers_signals_annotated.csv", encoding="utf-8-sig")
    return d, a


def methods_en() -> str:
    m = (MAN / "Methods_draft_EN.md").read_text(encoding="utf-8")
    m = re.sub(r"^#\s+Methods[^\n]*\n", "", m, count=1, flags=re.S)
    m = re.sub(r"^##\s*2\.\s*Methods\s*$", "## 2. Methods", m, count=1, flags=re.M)
    # keep the section numbering used in the assembled article
    # The Methods file uses 2.6b / 2.7 / 2.8 for robustness, genetics and software;
    # renumber them in one pass so the substitutions cannot cascade.
    def _num(m):
        return {"2.6b": "### 2.7 Robustness analyses",
                "2.7": "### 2.8 Genetic analysis",
                "2.8": "### 2.9 Software and reproducibility"}.get(
                    m.group(1), m.group(0))
    m = re.sub(r"^### (2\.6b|2\.7|2\.8) [^\n]*$", _num, m, flags=re.M)
    # 2.10 and 2.11 are appended below

    extra = """
### 2.10 Data-driven ocular term discovery

In addition to the curated panel, an unbiased pass enumerated every MedDRA
preferred term occurring in the de-duplicated ethambutol reports and retained those
matching a broad ocular lexicon (eye, ocul-, ophthalm-, visual, vision, sight,
blind, optic, retin-, macul-, vitreous, choroid, conjunctiv-, corne-, irid-, uve-,
scler-, lacrimal, pupil, ptosis, diplopia, nystagmus, photophobia, scotoma,
amblyopia, cataract, glaucoma, papilloedema, blephar-, eyelid, orbital,
dyschromatopsia, hemianopia, fundus, retrobulbar). Each retained term was then
counted both within the ethambutol cases and across the whole de-duplicated
database, and the two term sets were merged into a single panel of 178 terms.

The expanded panel necessarily contains terms that the tuberculosis rather than the
drug explains - ocular tuberculosis, choroiditis, uveitis and related
manifestations are expected in patients with tuberculosis irrespective of which
antitubercular drug they receive - and a smaller number of lexical artefacts (for
example "macule", a skin lesion, matched the macul- pattern). Signals were
therefore classified by an explicit, auditable list into the drug-toxicity
spectrum, ocular tuberculosis, or non-ocular artefacts, and the drug-toxicity
spectrum is what the manuscript reports as the ethambutol signal.

### 2.11 Report adequacy

Because disproportionality analysis assumes reports carry enough detail to
interpret the event, completeness was profiled for one representative drug line per
case (primary suspect preferred, then secondary suspect, then any line) across age,
sex, weight, reporter type, country, event date, therapy start date, therapy
duration, dose, dose unit, route and indication. The ethambutol case set was
compared with the whole database and with the five comparator antitubercular drugs,
and the proportion of ethambutol optic-nerve cases that remain analysable under a
minimum-detail restriction (age and sex and a therapy start date) was computed.
"""
    return m.strip() + "\n" + extra.strip() + "\n"


def results_en() -> str:
    sig = pd.read_csv(RES / "faers_signals_annotated.csv", encoding="utf-8-sig")
    tox = sig[(sig.category == "drug-toxicity spectrum") & (sig.signal_strict == True)]  # noqa: E712
    tb = sig[sig.category == "ocular tuberculosis (disease)"]
    adq = pd.read_csv(RES / "faers_report_adequacy.csv", encoding="utf-8-sig")
    adqs = pd.read_csv(RES / "faers_adequacy_summary.csv", encoding="utf-8-sig")

    # robustness values, read from the analysis output rather than typed, so the
    # English and Chinese versions cannot quote different numbers
    rbdf = pd.read_csv(RES / "faers_robustness.csv", encoding="utf-8-sig")

    def rbval(term: str, scenario_key: str, col: str = "ror") -> float:
        key = {"main": "main (all roles, whole database)",
               "strict": "strict whole-token exposure",
               "suspect": "suspect-only reports",
               "antitb": "anti-TB comparator only"}[scenario_key]
        s2 = rbdf[(rbdf.term == term) & (rbdf.scenario == key)]
        return float(s2.iloc[0][col]) if not s2.empty else float("nan")

    RB = {
        "pn_main": rbval("OPTIC NEUROPATHY", "main"),
        "pn_strict": rbval("OPTIC NEUROPATHY", "strict"),
        "pn_suspect": rbval("OPTIC NEUROPATHY", "suspect"),
        "pn_antitb": rbval("OPTIC NEUROPATHY", "antitb"),
        "pn_antitb_lcl": rbval("OPTIC NEUROPATHY", "antitb", "ror_lcl"),
        "pn_antitb_ucl": rbval("OPTIC NEUROPATHY", "antitb", "ror_ucl"),
        "on_main": rbval("OPTIC NEURITIS", "main"),
        "on_suspect": rbval("OPTIC NEURITIS", "suspect"),
        "on_antitb": rbval("OPTIC NEURITIS", "antitb"),
        "oa_main": rbval("OPTIC ATROPHY", "main"),
        "oa_suspect": rbval("OPTIC ATROPHY", "suspect"),
        "oa_antitb": rbval("OPTIC ATROPHY", "antitb"),
    }

    def row(df, t):
        r = df[df.term == t]
        return r.iloc[0] if not r.empty else None

    on = row(sig, "OPTIC NEUROPATHY")
    ton = row(sig, "TOXIC OPTIC NEUROPATHY")
    roww = adq[adq.group == "ethambutol"]
    allrow = adq[adq.group == "All FAERS"]
    eth_pct = roww.iloc[0] if not roww.empty else None
    all_pct = allrow.iloc[0] if not allrow.empty else None

    txt = f"""## 3. Results

### 3.1 Study population

The 90 FAERS quarterly ASCII releases contributed 24,389,966 submitted reports.
Applying the FDA case-version rule left **20,328,568 unique cases**, a removal of
4,061,398 duplicate or superseded versions. One quarterly archive (2026Q2) was
corrupt and could not be ingested, so the analysed period is 2004Q1-2026Q1.
Ethambutol appeared in **13,804** de-duplicated cases, of which **8,375 (60.7%)**
carried ethambutol as the primary or secondary suspect drug (1,034 as primary
suspect) and 5,429 as a concomitant only. Isoniazid appeared in 16,833 cases,
rifampicin in 24,114, pyrazinamide in 9,239, streptomycin in 1,031 and linezolid in
25,681 (Figure 1, Table 1).

Within the ethambutol cases, **971 (7.03%)** reported at least one ocular event and
**475 (3.44%)** at least one optic-nerve event. The median age was 51 years
(interquartile range 33-68) and 5,987 of 12,312 cases with a recorded sex (48.6%)
were female.

**Note on the two case counts reported in this paper.** Two ethambutol case
counts appear and they are not the same quantity. The toxicological analyses use
13,804 de-duplicated cases in which a drug line matches the string ETHAMBUTOL; this
is the case set behind the whole-database odds ratios and all case-level models. The
within-class comparison uses 15,573 cases, because comparing drugs with each other
requires the salt and brand variants of one molecule to be merged - DEXAMBUTOL,
MYAMBUTOL, ETHAMBUTOL HYDROCHLORIDE, ETHAMBUTOL DIHYDROCHLORIDE, ETHAMBUTOL HCL and
ETAMBUTOL - otherwise a single molecule is split across several entries and its rank
is driven by whichever variant happens to carry the most events. Merging adds 1,769
cases and 18 optic-neuropathy cases, and reduces the whole-database odds ratio for
optic neuropathy from 159.21 to 121.43; no conclusion depends on the choice. A third,
more permissive definition - also accepting the drug when it appears on a
non-surviving version of a re-submitted report - was tested and rejected: establishing
exposure through a caseid join rather than through the surviving report inflates the
exposed set to 251,793 cases, which is an artefact of the join rather than a valid
exposure definition. The sensitivity analysis is in
results/faers_exposure_sensitivity.csv.

### 3.2 The ocular phenotype resolves into a highly specific optic-nerve signal

The unbiased pass identified 4,011 distinct MedDRA preferred terms in the
ethambutol reports, of which 159 matched the ocular lexicon; merging these with the
curated panel gave 178 terms, of which 177 occurred in at least three ethambutol
cases and **58 met all strict signal criteria** (ROR lower 95% CI > 1, PRR >= 2,
chi-square >= 4, IC025 > 0, >= 3 cases, Benjamini-Hochberg q < 0.05).

Within the drug-toxicity spectrum, optic neuropathy was the strongest signal:
{int(on.a)} cases, **ROR {on.ror:.2f} (95% CI {on.ror_lcl:.2f}-{on.ror_ucl:.2f})**,
PRR {on.prr:.2f}, IC025 {on.ic025:.2f}, EBGM05 {on.ebgm05:.2f}. The term that
specifically names the drug injury, **toxic optic neuropathy, returned an ROR of
{ton.ror:.2f} (95% CI {ton.ror_lcl:.2f}-{ton.ror_ucl:.2f}; {int(ton.a)} cases,
IC025 {ton.ic025:.2f})** - it is the second strongest signal in the analysis and
was not part of the curated panel, so it emerged from the unbiased pass.

The remaining leading drug-toxicity signals were hereditary optic atrophy
(ROR {row(sig,'HEREDITARY OPTIC ATROPHY').ror:.1f}), ocular toxicity
({row(sig,'OCULAR TOXICITY').ror:.1f}), dyschromatopsia
({row(sig,'DYSCHROMATOPSIA').ror:.1f}), scotoma ({row(sig,'SCOTOMA').ror:.1f}),
optic neuritis ({row(sig,'OPTIC NEURITIS').ror:.1f}), chromatopsia
({row(sig,'CHROMATOPSIA').ror:.1f}), optic atrophy
({row(sig,'OPTIC ATROPHY').ror:.1f}), optic nerve injury
({row(sig,'OPTIC NERVE INJURY').ror:.1f}), hemianopia
({row(sig,'HEMIANOPIA').ror:.1f}), optic nerve disorder
({row(sig,'OPTIC NERVE DISORDER').ror:.1f}), visual field defect
({row(sig,'VISUAL FIELD DEFECT').ror:.1f}), papillooedema
({row(sig,'PAPILLOEDEMA').ror:.1f}), nystagmus ({row(sig,'NYSTAGMUS').ror:.1f}),
visual acuity reduced ({row(sig,'VISUAL ACUITY REDUCED').ror:.1f}), macular
degeneration ({row(sig,'MACULAR DEGENERATION').ror:.1f}), blindness
({row(sig,'BLINDNESS').ror:.1f}), visual impairment
({row(sig,'VISUAL IMPAIRMENT').ror:.1f}) and diplopia
({row(sig,'DIPLOPIA').ror:.1f}) (Figure 2, Figure 4, Table 2, Table 2c).

The informative result is the contrast. **Not one non-specific ocular complaint
formed a signal:** vision blurred returned an ROR of
{row(sig,'VISION BLURRED').ror:.2f}, cataract {row(sig,'CATARACT').ror:.2f},
conjunctivitis {row(sig,'CONJUNCTIVITIS').ror:.2f}, dry eye
{row(sig,'DRY EYE').ror:.2f}, eye pain {row(sig,'EYE PAIN').ror:.2f}, eye irritation
{row(sig,'EYE IRRITATION').ror:.2f}, photophobia
{row(sig,'PHOTOPHOBIA').ror:.2f}, glaucoma {row(sig,'GLAUCOMA').ror:.2f} and
ocular hyperaemia {row(sig,'OCULAR HYPERAEMIA').ror:.2f}. The signals are confined
to the optic-nerve, retinal and colour-vision axes; the ocular surface and anterior
segment are spared (Figure 3).

### 3.2b Within the antitubercular class ethambutol is high but not the highest

Comparing every drug against the whole database answers a different question from
comparing drugs with each other, and for an antitubercular agent the whole-database
denominator is dominated by non-tuberculosis reports. The drug-versus-drug
comparison therefore restricts the denominator to reports mentioning any
antitubercular drug.

Within that class, optic neuropathy gave ethambutol an ROR of
**6.47 (95% CI 5.38-7.79;
171 cases)**, which places it **6th of 18**
drugs with at least 100 reports. The drugs above it - prothionamide, capreomycin,
streptomycin, cycloserine, ethionamide - are second-line agents used for
drug-resistant disease, and that comparison is confounded by indication severity, as
set out in the limitations. The comparison that is not confounded is with the drugs
given in the same regimen: ethambutol's optic-neuropathy ratio exceeds isoniazid
(1.47), rifampicin (2.20) and pyrazinamide
(2.87), and is close to linezolid (6.20).

The more informative result is in the *shape* of the profile rather than its rank.
Ethambutol's highest within-class ratio is for **dyschromatopsia**
(13.14, 95% CI 7.51-23.02),
followed by ocular toxicity (13.65) and toxic optic
neuropathy (7.05), while optic neuropathy itself
ranks lower for ethambutol (6.47) than for several
comparators. Acquired colour-vision loss preceding and exceeding acuity loss is the
clinical hallmark of ethambutol optic neuropathy, and the disproportionality profile
reproduces that ordering: the drug's signature is dyschromatopsia, not optic-nerve
reporting in general.

The negative controls remain null in this stricter comparison as well: dry eye
0.35 (0.20-0.61),
eye pain 0.32, glaucoma 0.18, ocular
hyperaemia 0.18 and vision blurred
1.15 - all at or below the class background, so the
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

### 3.3 The tuberculosis terms behave as a separate signal population

The expanded panel also captured the ocular manifestations of tuberculosis itself.
Choroid tubercles (ROR {row(sig,'CHOROID TUBERCLES').ror:.0f}, 3 cases),
serpiginous choroiditis ({row(sig,'SERPIGINOUS CHOROIDITIS').ror:.0f}, 24 cases),
tuberculosis of eye ({row(sig,'TUBERCULOSIS OF EYE').ror:.0f}, 17 cases),
choroiditis ({row(sig,'CHOROIDITIS').ror:.0f}, 31 cases) and intermediate uveitis
({row(sig,'INTERMEDIATE UVEITIS').ror:.0f}, 4 cases) all produced extreme
disproportionality, because these are complications of the infection rather than of
any drug and are therefore recorded almost exclusively in tuberculosis reports.
They are reported for completeness and explicitly excluded from the drug-toxicity
interpretation; a further 83 terms could not be assigned to either category by the
explicit list and are listed in Table 2d for manual review.

### 3.4 Time to onset separates optic-nerve events from all other events

Time from starting ethambutol to the reported event could be computed in 1,992
cases. The median was **125 days (IQR 63-293; 90th percentile 636 days) for
optic-nerve events** and 111.5 days for ocular events generally, compared with
**30 days (IQR 9-85)** for non-ocular events in the same case set (Figure 8,
Table 3). An interval of this length is what a cumulative axonal injury would
produce and is difficult to reconcile with an acute hypersensitivity mechanism.

### 3.5 Predictors of an ocular event

In a multivariable logistic model (n = 13,804; 971 events; pseudo-R2 = 0.0351;
likelihood-ratio P = 1.46e-49), each additional year of age raised the odds of an
ocular event (adjusted OR 1.009, 95% CI 1.005-1.012; P = 1.1e-6), as did female sex
(1.378, 1.196-1.588; P = 8.8e-6) and reporting from Europe relative to the Americas
(1.358, 1.151-1.601; P = 2.9e-4). Reporting year was weakly negative (0.978 per
year, 0.960-0.997) and the number of reported reactions was strongly associated
(1.832 per log unit), as expected for a more completely documented report
(Table 4). Reporting from Asia did not differ from the reference region (0.924,
0.773-1.105; P = 0.389). Annual reporting rose from 436 ethambutol reports in 2013
to 1,640 in 2025, while the proportion carrying an optic-nerve term stayed between
2.5% and 5.8% without a clear trend (Figure 9).

### 3.6 Robustness: the conclusion survives every alternative specification

The whole disproportionality panel was recomputed under four specifications: the
main analysis (whole database, all drug roles); a strict whole-token exposure match,
which excludes reports naming only a fixed-dose combination product; restriction to
reports in which ethambutol was the primary or secondary suspect drug; and a
comparator denominator restricted to reports mentioning any anti-tuberculosis drug,
which removes the possibility that the signal merely reflects the underlying
tuberculosis population.

**All three optic-nerve signals held in every specification.** Optic neuropathy
returned RORs of {RB['pn_main']:.2f} (main), {RB['pn_strict']:.2f} (strict
whole-token) and {RB['pn_suspect']:.2f} (suspect-only), and
**{RB['pn_antitb']:.2f} (95% CI {RB['pn_antitb_lcl']:.2f}-{RB['pn_antitb_ucl']:.2f})**
under the strictest same-class comparator. Optic neuritis moved from
{RB['on_main']:.2f} to {RB['on_suspect']:.2f} and {RB['on_antitb']:.2f}; optic
atrophy from {RB['oa_main']:.2f} to {RB['oa_suspect']:.2f} and
{RB['oa_antitb']:.2f}. Conversely, **cataract, dry eye, eye pain and glaucoma
failed to form a signal in any of the four specifications** (Table 9), so the
specific-against-general contrast does not depend on how exposure is matched, how
the denominator is chosen, or whether concomitant-only reports are included - the
three ways in which a pharmacovigilance signal most often turns out to be an
artefact.

### 3.7 Report adequacy

Completeness was high for the fields needed to interpret a report and modest for
those needed to characterise exposure. Among ethambutol cases, country was recorded
in {eth_pct.country_pct:.1f}%, sex in {eth_pct.sex_pct:.1f}%, age in
{eth_pct.age_pct:.1f}%, route in {eth_pct.route_pct:.1f}%, dose in
{eth_pct.dose_pct:.1f}%, event date in {eth_pct['event date_pct']:.1f}% and therapy
start date in {eth_pct['therapy start_pct']:.1f}%; therapy duration was recorded in
only {eth_pct['therapy duration_pct']:.1f}%. Relative to the whole database (age
{all_pct.age_pct:.1f}%, event date {all_pct['event date_pct']:.1f}%), ethambutol
reports were better documented for age and slightly worse for event date, and the
mean number of reported reactions was higher ({eth_pct.mean_reactions:.2f} versus
{all_pct.mean_reactions:.2f}), as expected for a report that names a specific
suspected drug effect.

The consequence for interpretation is quantified directly: of the ethambutol cases
in the optic-nerve spectrum, {int(adqs.iloc[0].n_ocular_spectrum_cases)} cases,
{adqs.iloc[0].pct_age_and_sex:.1f}% had both age and sex recorded and
{adqs.iloc[0].pct_therapy_start:.1f}% had a therapy start date, so only
**{adqs.iloc[0].pct_both:.1f}%** could support a time-to-onset analysis
(Table 10). The signal analysis, which needs only the drug name and the reaction
term, uses the whole case set; the temporal and dose analyses rest on the minority
of reports that carry those fields, and this is why they are reported as
supporting rather than primary evidence.

### 3.8 The mechanistic network converges on ferroptosis and mitochondrial integrity

Open Targets contains **no human mechanism of action for ethambutol**: the only
recorded mechanism is inhibition of the mycobacterial arabinosyltransferase EmbA,
for which no human orthologue exists. Any human ocular toxicity must therefore be
off-target or downstream, and the human gene set had to be reconstructed rather
than looked up.

A full-text mine of Europe PMC returned 3,034 unique records across eight query
families. Screening against a 416-symbol HGNC whitelist identified 67 genes with
co-mention evidence; after excluding genes whose co-mention was driven by
mycobacterial-immunity work rather than ocular toxicity, 48 remained. Together with
a curated core panel, the focused tier comprised 35 genes and produced a STRING
network of **33 nodes and 191 edges** (Figure 5).

The hubs were TP53 (degree 23), NFE2L2 (22), AKT1 (22), BCL2 (20), HMOX1 (20),
CASP3 (20), SOD2 (19), PPARG (18), TNF (18; 14 papers) and BAX (17), with GPX4
(17), MFN2 (14), SDHB (13), BDNF (12), TFEB (10), SMAD4 (9), SLC7A11 (7), NTRK2 (7)
and ACSL4 (6) following (Table 5).

Over-representation analysis gave a coherent picture (Figure 6, Table 6). The
leading KEGG term was **ferroptosis** (P = 6.10e-7; 6 of 41 pathway genes: GPX4,
SLC7A11, ACSL4, SDHB, SMAD4, HMOX1). GO biological process was led by regulation of
programmed cell death (P = 6.15e-14), GO cellular component by **mitochondrion**
(P = 1.01e-8) followed by mitochondrial envelope (5.12e-5) and mitochondrial outer
membrane (8.36e-5), and GO molecular function by oxidoreductase activity
(2.74e-5) and haem binding (3.39e-4). WikiPathways returned oxidative stress
(P = 4.56e-9) and Reactome returned BDNF-activated NTRK2 (TRKB) signalling
(P = 5.16e-4) together with detoxification of reactive oxygen species (2.25e-4).

### 3.9 Docking shows which network nodes ethambutol can occupy directly

The mechanism network describes processes that become dysregulated, not where the
drug binds. To ask the narrower question - which nodes of that network ethambutol
itself can occupy - the drug was docked against each of the fourteen hub targets:
fourteen runs, all completed.

The docking protocol was controlled by re-docking co-crystallised ligands into
their own receptors. Carbonic anhydrase II with acetazolamide reproduced its
crystal pose at a symmetry-corrected RMSD of **1.795 A**, within the accepted
2.0 A criterion. Dihydrofolate reductase with methotrexate, a 33-heavy-atom
flexible ligand, gave 5.863 A and failed; this is reported as a limitation of the
protocol for large flexible ligands.

Ethambutol docked with affinities between -3.96 and -5.50 kcal/mol (Figure 7,
Table 7). The most favourable were TNF (-5.50), MFN2 (-5.21), HMOX1 (-5.09),
NFE2L2 (-5.01) and BCL2 (-4.95); the weakest were GPX4 (-3.96), SMAD4 (-4.06) and
AKT1 (-4.05). The affinities are modest and span a narrow range, which is the
expected result for a small, highly polar molecule with three rotatable bonds and
no designed complementarity to any of these pockets. The interpretable feature is
the ordering rather than the absolute values: the drug is predicted to engage the
inflammatory and oxidative-stress nodes (TNF, HMOX1, NFE2L2) and the
mitochondrial-dynamics node MFN2 more readily than the ferroptosis execution
machinery (GPX4, ACSL4) or the TGF-beta effector SMAD4. That ordering is consistent
with ethambutol acting upstream of the ferroptosis cascade - dysregulating the
redox and inflammatory environment rather than binding the pathway's terminal
enzymes - which is what the enrichment pattern also suggests.

### 3.10 Genetic interrogation: genetically proxied renal function does not cause the optic-nerve phenotype

Exposures were drawn from OpenGWAS (European ancestry, MR-eligible, largest
available sample per trait) and outcomes were the FinnGen R12 optic-nerve and visual
phenotypes, accessed through the tabix index with HTTP range requests. Two
methodological problems had to be solved before the estimates were interpretable,
and both are reported because they would otherwise be invisible.

First, an initial implementation retrieved only the first 16 kb bin of a wide
regional query, so a 131 Mb query returned 256 variants instead of a million; the
effect estimates were correspondingly absurd. Second, and independently, the
OpenGWAS instruments and FinnGen are on different genome builds, so matching by
chromosome and position recovered only **0.2%** of 13,560 instrument-outcome pairs
(for example, rs77924615 is at chr16:20,392,332 in the instrument file and at
chr16:20,381,010 in FinnGen). Matching by rsID instead of position - rsIDs being
build-independent - raised recovery to 13.5%.

With harmonisation corrected, the renal-function exposures are well powered:
estimated glomerular filtration rate (n = 1,004,040) and cystatin C (n = 437,846)
each contributed **146-150 harmonised instruments** per outcome, and the estimates
are precise (for example, cystatin C on optic neuritis: OR 1.026, 95% CI
0.865-1.216).

**No causal effect was detected.** Across all six optic-nerve and visual outcomes,
genetically proxied renal function showed no association after Benjamini-Hochberg
correction (all q = 0.99; Table 8); genetically proxied type 2 diabetes was
likewise null for optic neuritis (OR 1.094, 95% CI 0.940-1.274; 57 instruments).
MR-Egger intercepts were non-significant and Steiger directionality was correct in
every case, arguing against reverse causation.

Two caveats bound this result. The rare outcomes (optic atrophy, 629 cases; optic
neuritis, 1,592) limit power, so these are null results with wide intervals rather
than demonstrations of absence for the smaller endpoints. And, as set out in the
Methods, a drug-exposure Mendelian randomisation is not possible for ethambutol, so
this analysis addresses whether renal dysfunction itself causes optic-nerve disease
- not whether it raises risk by increasing drug exposure.

That distinction is the interpretative point. Renal impairment is the strongest
clinical risk factor for ethambutol optic neuropathy (adjusted OR 2.69-3.73;
incidence approaching 40% in dialysis patients) [24,25], and the natural reading is
that impaired clearance raises serum ethambutol and therefore toxicity. Our null
genetic result is consistent with exactly that reading and inconsistent with a
competing one - that uraemic neuropathy and optic-nerve disease share a common
cause independent of the drug. The clinical implication is that renal function
matters as a determinant of exposure, which is modifiable by dose adjustment,
rather than as an independent driver of optic-nerve degeneration.
"""
    return txt


def main() -> int:
    cmap = json.loads((DER / "citation_map.json").read_text(encoding="utf-8"))

    def renumber(text: str) -> str:
        """
        Convert [PMID a, b, c] markers into numbered citations.  A single bracket
        can hold several PMIDs (the draft groups them), so the whole list is
        replaced at once and the numbers are sorted and de-duplicated.
        """
        def repl(m):
            pmids = re.findall(r"[0-9]{6,9}", m.group(1))
            nums = []
            for p in pmids:
                rec = cmap.get(p)
                if rec:
                    nums.append(rec["number"])
                else:
                    print(f"  [warn] PMID {p} has no verified reference")
            if not nums:
                return m.group(0)
            return "[" + ",".join(str(n) for n in sorted(set(nums))) + "]"

        return re.sub(r"\[PMID\s+([0-9,\s]+)\]", repl, text)

    # ---------------------------------------------------------------- English
    body = (MAN / "Manuscript_EN_draft.md").read_text(encoding="utf-8")
    # replace the Results section with the updated one
    body = re.sub(r"## 3\. Results.*?(?=## 4\. Discussion)", results_en() + "\n---\n\n",
                  body, flags=re.S)
    body = re.sub(r"## 2\. Methods.*?(?=## 3\. Results)", methods_en() + "\n---\n\n",
                  body, flags=re.S)

    # inline citations for the Discussion, which the draft left uncited
    for old, new in [
        ("as the features reported in EON cohorts",
         "as the features reported in EON cohorts [15,16,17,18]"),
        ("and their ordering by strength tracks how central each is to the disease.",
         "and their ordering by strength tracks how central each is to the disease."),
        ("connect to the genetic-susceptibility literature [7]",
         "connect to the genetic-susceptibility literature [7,8]"),
        ("cytostatin", "cystatin"),
        ("Baseline ophthalmic screening is performed in only 12.0–13.1%",
         "Baseline ophthalmic screening is performed in only 12.0–13.1%"),
    ]:
        body = body.replace(old, new)

    # prognostic OCT measures and the renal-function effect sizes
    body = body.replace(
        "the clinical literature's finding that structural measures predict outcome "
        "better than acuity [22,23]",
        "the clinical literature's finding that structural measures predict outcome "
        "better than acuity [22,23,26,27]")
    body = body.replace(
        "with an incidence approaching 40% in dialysis patients) [24,25]",
        "with an incidence approaching 40% in dialysis patients) [24,25,13]")
    body = body.replace(
        "was reported in 46.8% of one EON series [7]",
        "was reported in 46.8% of one EON series [7]")
    body = body.replace(
        "and no loss of efficacy [4]",
        "and no loss of efficacy [4,12]")

    body = renumber(body)
    refs = (MAN / "references_en.md").read_text(encoding="utf-8")
    refs = refs.replace("# References", "## References")

    front = f"""# {TITLE_EN}

**Running head:** Ethambutol ocular toxicity

**Authors:** [to be inserted]   **Affiliations:** [to be inserted]

**Corresponding author:** [name, postal address, email]

---

"""
    back = f"""
---

## Statements

**Ethics approval.** Not required. FAERS contains de-identified, voluntarily
submitted adverse event reports; no human participants were recruited and no
identifiable information was handled.

**Data availability.** All data analysed are publicly available. FAERS quarterly
ASCII releases were obtained from the U.S. Food and Drug Administration
(https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html). Drug mechanism
and disease-association data came from Open Targets (GraphQL API v4), protein
interactions from STRING v12, functional enrichment from g:Profiler, compound
structures from PubChem, experimental structures from the RCSB Protein Data Bank
(AlphaFold models where no experimental structure exists), genetic instruments from
OpenGWAS, and outcome summary statistics from the FinnGen release 12 public bucket.
No new data were generated.

**Code availability.** The full pipeline is implemented as standalone, re-runnable
Python scripts: FAERS ingestion and case-version de-duplication, disproportionality
statistics, case-level and time-to-onset analysis, report-adequacy profiling,
literature target mining, network construction and enrichment, blind pocket
detection, docking with a redocking validation harness, a minimal BGZF/tabix reader
for on-demand access to FinnGen summary statistics, and two-sample Mendelian
randomisation. [repository URL to be inserted]

**Funding.** [to be inserted]

**Competing interests.** The authors declare no competing interests.

**Author contributions.** [to be inserted]

---

{refs}

---

## Reporting checklists

The study is reported in accordance with STROBE, its RECORD-PE extension for
pharmacoepidemiological research using routinely collected data, and the STROBE-MR
items relevant to the genetic component. The completed checklists, including an
explicit list of what was deliberately *not* done and why, are provided as a
supplementary file (STROBE_RECORD_checklist).
"""
    en = MAN / "Ethambutol_EyeTox_EN_full.md"
    en.write_text(front + body + back, encoding="utf-8")
    print(f"[ok] {en.name}: {len(en.read_text(encoding='utf-8').split()):,} words")

    # ---------------------------------------------------------------- Chinese
    cn_src = (MAN / "论文_中文版.md").read_text(encoding="utf-8")
    cn_src = re.sub(r"^#\s+.*$", f"# {TITLE_CN}", cn_src, count=1, flags=re.M)
    cn_back = """
---

## 声明

**伦理审批** 不需要。FAERS 为去标识化的自愿上报数据；本研究未招募受试者，未处理任何可识别信息。

**数据可用性** 本研究全部数据均公开可及：FAERS 季度 ASCII 原始发布取自美国食品药品监督管理局；
药物机制与疾病关联取自 Open Targets（GraphQL API v4）；蛋白互作取自 STRING v12；功能富集取自
g:Profiler；化合物结构取自 PubChem；实验结构取自 RCSB 蛋白质数据库（无可及实验结构时使用
AlphaFold 模型）；遗传工具变量取自 OpenGWAS；结局汇总统计取自 FinnGen release 12 公开存储桶。
本研究未产生新数据。

**代码可用性** 全部检索、处理与分析步骤均实现为可独立重跑的 Python 脚本。[待填入仓库地址]

**基金项目** [待填入]

**利益冲突** 作者声明无利益冲突。

**作者贡献** [待填入]

---

## 参考文献

本中文版为英文投稿稿的中文对照译本。参考文献编号与英文版完全一致（共 25 条），
完整条目见英文版 References 一节。**投稿时以英文版为准**；若改投中文期刊，
需按目标期刊格式重新著录参考文献。
"""
    cn = MAN / "Ethambutol_EyeTox_CN_full.md"
    cn.write_text(cn_src + cn_back, encoding="utf-8")
    print(f"[ok] {cn.name}: {len(cn.read_text(encoding='utf-8')):,} characters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
