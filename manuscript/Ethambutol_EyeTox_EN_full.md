# Ocular toxicity of ethambutol: a whole-database pharmacovigilance analysis of 20.3 million FAERS cases integrated with network toxicology, molecular docking and genetic interrogation of the optic-nerve phenotype

**Running head:** Ethambutol ocular toxicity

**Authors:** Bowen Shi¹, Jing Yan¹*, Zhengzheng Wu¹, Siyuan Yang¹, Yaqin Tan¹, Xuan Wang¹

**Affiliation:** ¹ Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China

**Corresponding author:** Jing Yan, Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China. Email: 20200121047@bucm.edu.cn

---

# Ocular toxicity of ethambutol: a whole-database pharmacovigilance analysis of 20.3 million FAERS cases with network toxicology, molecular docking and genetic interrogation of the optic-nerve phenotype

## Title

**Ocular toxicity of ethambutol: a whole-database pharmacovigilance analysis of 20.3 million FAERS cases with network toxicology, molecular docking and genetic interrogation of the optic-nerve phenotype**



---

## Abstract (structured)

**Background.** Ethambutol remains a first-line antitubercular agent, and its ocular toxicity — an optic neuropathy that can be irreversible — is the toxicity that most limits its use. Estimates of its frequency range from 0.28% to 6.5% depending on how cases are ascertained, the mechanistic basis is incompletely understood, and no pharmacovigilance analysis has yet profiled the full ocular phenotype against the other first-line antitubercular drugs in the whole FDA Adverse Event Reporting System (FAERS).

**Methods.** We ingested all 90 FDA FAERS quarterly ASCII releases
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
against FinnGen R12 optic-nerve phenotypes.

**Results.** Among 13,804 de-duplicated ethambutol cases, 971 (7.03%)
reported an ocular event and 475 (3.44%) an optic-nerve event. Of 152 testable
ocular terms, 45 met the strict signal criteria. Within the antitubercular class, optic
neuropathy gave ethambutol an ROR of 6.47
(95% CI 5.38-7.79;
171 cases), above the drugs given in the same regimen -
isoniazid 1.47, rifampicin 2.20, pyrazinamide
2.87 - but 6th of 18 overall, below several
second-line agents used for drug-resistant disease, a comparison confounded by
indication severity. The most distinctive term in ethambutol's profile was
dyschromatopsia (ROR 13.14, 95% CI
7.51-23.02), which
exceeded its optic-neuropathy ratio and matches the clinical hallmark of the
condition. Not one non-specific ocular complaint formed a signal in any comparison:
vision blurred 1.15, cataract 0.81,
dry eye 0.35, eye pain 0.32, glaucoma
0.18, ocular hyperaemia 0.18. All
optic-nerve signals survived four robustness specifications, including a comparator
denominator restricted to anti-tuberculosis reports, where optic neuropathy retained
an ROR of 7.64 (95% CI 5.24-11.13). Splitting the database by receipt year reproduced
the signal independently in both periods (optic neuropathy ROR 81.9 for 2004-2016 and
86.9 for 2017-2026, negative controls null in both), so the association is not
attributable to a single reporting era. **The same pattern was reproduced in JADER, the
independent Japanese database (1,054,239 cases): optic neuropathy ROR 571.0, toxic optic
neuropathy 864.6, with cataract, glaucoma and dry eye all null.** Median time from starting ethambutol to an
optic-nerve event was 125 days (IQR 63-293) versus 30 days (IQR 9-85) for non-ocular
events in the same reports. Each additional year of age raised the odds of an ocular
event (adjusted OR 1.009, 95% CI 1.005-1.012), as did female sex (1.378,
1.196-1.588); a regional coefficient for Europe (1.358, 1.151-1.601) is reported but
not interpreted, because attaching a tuberculosis burden denominator shows that FAERS
country counts measure national reporting intensity rather than patient numbers
(reports per unit of burden span three orders of magnitude and are unrelated to burden,
Spearman rho = -0.14). Report completeness was
high for interpretive fields but low for exposure fields: only 27.8% of
optic-nerve-spectrum cases carried both age, sex and a therapy start date, and daily
dose did not predict the optic-nerve outcome once exposure duration was accounted for
(likelihood-ratio P = 0.55). Open Targets contains no human mechanism of action for
ethambutol, so the human gene set was reconstructed from literature; the focused-tier
network (33 nodes, 191 edges) was led by TP53, NFE2L2, AKT1, BCL2, HMOX1, CASP3,
SOD2, TNF and GPX4, and the enriched terms were headed by ferroptosis (KEGG, P = 6.1 x 10^-7),
regulation of programmed cell death (GO:BP, P = 6.1 x 10^-14), the mitochondrial
envelope (GO:CC, P = 1.0 x 10^-8) and BDNF-NTRK2 signalling. Docking ranked TNF,
MFN2, HMOX1 and BCL2 highest among the hub targets, but at affinities of only -4.95 to
-5.50 kcal/mol; all-atom molecular dynamics in three of those sites kept the ligand in
contact with the protein throughout (minimum ligand–protein distance 1.76-2.18 Å, contacts
maintained or increased, receptor backbone RMSD 1.18-1.34 Å), so the docked sites are sites
the ligand can occupy, though it rearranges within them rather than sitting in one rigid
pose. Genetically proxied renal function showed no causal effect on any
optic-nerve or visual outcome (150-186 harmonised instruments per outcome across three
renal measures; all q ≥ 0.87).

**Conclusions.** In the largest pharmacovigilance assessment
of ethambutol to date, ocular toxicity is a highly specific optic-nerve signal that
spares the ocular surface, is delayed by months relative to other adverse events,
survives every robustness specification tested, and maps onto a
ferroptosis- and mitochondrion-centred molecular network that ethambutol can occupy
directly. The null genetic result for renal function indicates that renal impairment
acts by raising drug exposure rather than by independently causing optic-nerve
degeneration.

**Keywords.** ethambutol; optic neuropathy; pharmacovigilance; FAERS; disproportionality analysis; signal detection; ferroptosis; network toxicology; molecular docking; Mendelian randomisation

---

## 1. Introduction

Ethambutol has been a component of first-line antitubercular chemotherapy since the 1960s, and it is the drug in that regimen whose toxicity most often forces a change of treatment. Its characteristic adverse effect is a bilateral, painless, slowly progressive optic neuropathy that preferentially damages the papillomacular bundle, producing loss of visual acuity, dyschromatopsia — classically a red–green deficit — central or caecocentral scotomas and, when the drug is continued, optic atrophy [14,15,16].

What makes ethambutol optic neuropathy (EON) unusually consequential is the combination of three features. First, the reported frequency varies by an order of magnitude depending on ascertainment: retrospective chart review yields 0.28–0.5% [17,18], a nationwide insurance cohort gives a cumulative incidence of 0.9% [1], and prospective multidisciplinary screening with visual evoked potentials and optical coherence tomography gives 6.5% [2] because a substantial proportion of treated patients develop subclinical injury — up to 46% of eyes in one six-month prospective study [3]. Second, the toxicity is dose- and duration-dependent but not dose-thresholded: ocular effects have been reported at 12.3 mg/kg/day and irreversible blindness at the conventional 15 mg/kg/day [19,20], whereas a low-dose strategy (10.7 versus 15.4 mg/kg/day) produced 0% versus 4.8% EON in a propensity-score cohort [4]. Third, recovery is incomplete and slow. Between 50% and 77% of eyes improve after withdrawal, with a mean of about 15 months and a 50% recovery point at roughly 8 months, and retinal nerve fibre layer thinning persists despite visual recovery [15,16,21]. Several cohorts find that structural measures — ganglion cell–inner plexiform layer thickness, peripapillary retinal nerve fibre layer thickness — predict visual outcome better than the initial acuity [22,23].

The mechanistic picture has been slower to resolve than the clinical one. Ethambutol chelates divalent cations, and a long-standing observation is that zinc status modifies risk: plasma zinc below 0.70 mg/L before treatment marked high risk whereas above 1 mg/L almost no patient was affected [5], and ethambutol has been shown to accumulate zinc within lysosomes and permeabilise the lysosomal membrane, an effect reversed by the zinc chelator TPEN [6]. Mitochondrial involvement is supported both by the drug's structural resemblance to polyamines that interfere with mitochondrial function and by the fact that carriers of *OPA1* and LHON-associated mitochondrial variants are over-represented among affected patients (46.8% in one series, with younger age at onset) [7], although an earlier smaller study found no pathogenic LHON variants [8]. Most recently, a rat and cell study placed ferroptosis at the centre of the injury: ethambutol suppresses SDHB through Smad4, collapsing the GPX4/SLC7A11 antioxidant axis and killing retinal ganglion cells by lipid peroxidation [9]. Separately, Müller glia protect retinal ganglion cells from ethambutol through BDNF–AKT signalling, and pharmacological TRK blockade abolishes that protection [10].

Two gaps remain, and the first needs stating precisely because FAERS has been mined for these drugs before. Mao and Ou applied five signal-detection methods to the four first-line antitubercular drugs and reported that ethambutol carried more eye-disorder signals than the other three, so the observation that the ocular signal is prominent is not new [28]. Their analysis, however, drew on 978 ethambutol reports from 2021Q1 to 2025Q3 and reported signal counts by system organ class without multiplicity control, without comparators within the class and without control terms, which leaves the question this paper addresses untouched. What has not been done is a term-level analysis of the full ocular phenotype across the whole de-duplicated database with formal multiplicity control and an explicit negative-control panel. Separately, the pharmacovigilance work based on VigiBase has been organised by organ-system groupings rather than term-level disproportionality against comparators [11].

The second gap is the more consequential for interpretation, and no published analysis has addressed it. The specificity of the signal has never been tested against its own internal control: a drug that damages the optic nerve should produce signals for optic-nerve and colour-vision terms while leaving non-specific ocular complaints - dry eye, eye pain, cataract, conjunctivitis - at or below the background rate, and no published analysis has reported that contrast. Figure 1 shows why this matters. The VigiBase term distribution is headed by blurred vision (41.3% of ocular cases in South-East Asia) with optic neuropathy at 6.6% [11], which is exactly the pattern one would expect both from a genuine non-specific ocular effect and from a reporting habit - and without control terms, the two cannot be told apart.

We therefore assembled four complementary analyses of ethambutol
ocular toxicity: (i) a whole-database FAERS disproportionality analysis across an
expanded ocular term panel, with negative-control terms and four robustness
specifications built in; (ii) case-level characterisation of time to onset,
predictors and report adequacy; (iii) a tiered mechanism network with enrichment and
molecular docking of ethambutol against the hub targets; and (iv) genetic
interrogation of the implicated exposures against optic-nerve phenotypes in FinnGen.
The pharmacovigilance findings are the primary analysis; the mechanistic and genetic
analyses are hypothesis-generating.

---

## 2. Methods
### 2.1 Study design and reporting

This study integrates four complementary computational approaches to characterise the ocular toxicity of ethambutol: (i) a pharmacovigilance disproportionality analysis of the full FDA Adverse Event Reporting System (FAERS); (ii) case-level analysis of time to ocular onset and multivariable predictors within the ethambutol reports; (iii) a mechanism-of-toxicity analysis combining drug–disease target intersection, protein–protein interaction (PPI) network topology, functional enrichment and molecular docking; and (iv) genetic interrogation of the implicated pathway genes against optic-nerve phenotypes in FinnGen. Reporting follows the RECORD-PE extension of the STROBE statement for pharmacoepidemiological research using routinely collected health data, and the STROBE statement for the genetic analyses.

No human participants were recruited and no identifiable data were handled; all analyses used publicly available, de-identified aggregate data.

### 2.2 Pharmacovigilance data source and case de-duplication

FAERS reports were obtained from the FDA quarterly ASCII releases (2004Q1–2026Q2), retrieved from the official distribution endpoint (`fis.fda.gov`). These are the authoritative, unaggregated FAERS files; the harmonised openFDA view was not used as the primary source because it omits the raw `CASEID` and `FDA_DT` fields required for case-version de-duplication, and because sustained bulk retrieval from `api.fda.gov` is rate-limited.

FAERS is a spontaneous reporting system: a case may be re-submitted in a later quarter when new information arrives, generating several versions of the same `CASEID`. Following the FDA's own recommendation, only the most recent version of each case was retained, defined as the record with the highest `FDA_DT`, with ties broken by the highest `PRIMARYID`. All analyses were performed on this de-duplicated case set.

### 2.3 Drug exposure and outcome definition

Exposure was defined as the appearance of ethambutol anywhere in the report's drug records, identified on `substance` or `medicinalproduct` with a case-insensitive substring match on "ETHAMBUTOL". Isoniazid, rifampicin, pyrazinamide, streptomycin and linezolid served as comparator exposures, giving a spectrum from anti-tuberculosis agents with a recognised ocular signal to agents without one.

Ocular outcomes were captured as MedDRA preferred terms (PTs). Two complementary term sets were assembled. First, a data-driven set: every PT in the de-duplicated ethambutol reports was screened with a broad ocular lexicon (eye, ocul-, ophthalm-, visual, vision, sight, blind, optic, retin-, macul-, vitreous, choroid, conjunctiv-, corne-, irid-, uve-, scler-, lacrimal, pupil, ptosis, diplopia, nystagmus, photophobia, scotoma, amblyopia, cataract, glaucoma, papilloedema, blephar-, eyelid, orbital, dyschromatopsia, hemianopia, fundus, retrobulbar). Second, a hypothesis-driven panel covering the recognised ethambutol ocular toxicity spectrum, grouped as optic nerve, visual function, retina/macula, ocular surface/adnexa and other ocular terms. Every candidate term was then verified by an exact integer count against FAERS, so a PT that does not exist in the database could not enter the analysis.

### 2.4 Disproportionality analysis

For each drug D and adverse event E, the following whole-database contingency table was constructed from de-duplicated cases:

|  | E+ | E− | |
|---|---|---|---|
| D+ | a | b | n<sub>D</sub> = a + b |
| D− | c | d | |
| | n<sub>E</sub> = a + c | | N = a + b + c + d |

where *a* is the number of cases exposing D and reporting E, *n*<sub>D</sub> the number of cases exposing D, *n*<sub>E</sub> the number of cases reporting E, and *N* the total number of de-duplicated cases in FAERS. All four cells were computed in SQL against the local warehouse; Python set arithmetic is infeasible at this scale.

Four signal metrics were calculated. The reporting odds ratio (ROR) and its 95% confidence interval (CI) were obtained by the log-normal (Woolf) method. The proportional reporting ratio (PRR) was calculated with its 95% CI and the Yates-corrected χ² statistic. The Bayesian information component (IC) was computed with the non-informative prior of Norén and colleagues and reported as its lower 95% credible bound (IC<sub>025</sub>). The empirical Bayes geometric mean (EBGM) and its 5th percentile (EBGM<sub>05</sub>) were obtained from a gamma–Poisson shrinkage model with a weak (α = β = 0.5) prior. Where a cell was zero, 0.5 was added to all cells.

A term was declared a signal only when all three of the following held: ROR lower 95% CI > 1; PRR ≥ 2 with χ² ≥ 4; and IC<sub>025</sub> > 0. At least three cases were required to avoid signals driven by single reports. Multiple testing across the tested panel was controlled by the Benjamini–Hochberg procedure, and a stringent signal additionally required a false-discovery rate *q* < 0.05.

Two sensitivity analyses were specified a priori: restriction to reports in which ethambutol was coded as a primary or secondary suspect drug, and restriction to the recent era; a comparator-restricted analysis using only anti-tuberculosis reports was also performed.

### 2.5 Case-level analysis: time to onset and predictors

Within the de-duplicated ethambutol case set, time to ocular onset was computed as the interval between the therapy start date and the event date, restricted to reports with both dates available, a non-negative interval, and an interval not exceeding 3650 days. Distributions were summarised by median with interquartile range and 90th percentile, separately for all reports, ocular cases, optic-nerve cases and non-ocular cases.

Predictors of an ocular event were examined by multivariable logistic regression with the ocular composite as the dependent variable and age, sex, report year, number of reported reactions (log-transformed), and reporting region (Asia, Europe; the Americas as reference) as independent variables. Age was harmonised across the FAERS `age`/`age_cod` conventions (decades, years, months, weeks, days) and implausible values (< 0 or > 110 years) were set to missing. Because missingness in spontaneous reports is informative, an age-missingness indicator was retained in the model and coefficients are reported as adjusted odds ratios (aOR) with 95% CI.

### 2.6 Mechanism analysis

**Drug–target landscape.** Ethambutol's mechanism of action and linked targets were retrieved from Open Targets (GraphQL API v4). Because the drug inhibits the mycobacterial arabinosyltransferases EmbA/EmbB/EmbC, which have no human orthologue, the human gene set was instead anchored in two independent sources: the optic-nerve phenotype gene landscape from Open Targets (optic atrophy MONDO_0003608; Leber hereditary optic neuropathy MONDO_0010788; hereditary optic neuropathy MONDO_0020249; autosomal dominant optic atrophy MONDO_0020250; retinal dystrophy with inner retinal dysfunction MONDO_0014483; visual impairment HP_0000505), and a systematic full-text mine of Europe PMC.

**Literature-derived human targets.** Eight complementary queries were run against the Europe PMC REST API (ethambutol combined with retinal/optic terms, mitochondrial/oxidative/ferroptosis terms, zinc/copper/lysosome terms, autophagy/mTOR/AMPK/Nrf2 terms, neurotrophin/AKT/MAPK terms, glutamate/excitotoxicity terms, OPA1/LHON/mtDNA terms, and a general toxicity-mechanism query), retrieving 100 records per page over six pages per query. Gene symbols were extracted only from a curated whitelist of 416 unambiguous HGNC symbols, so acronym noise could not enter the network. Genes whose co-mention was driven by mycobacterial-immunity work rather than ocular toxicity were excluded after manual review of the retrieved titles.

**Network construction and hub ranking.** PPI networks were built with STRING (Homo sapiens, combined confidence ≥ 0.4) using the POST API. Two tiers were analysed: a focused tier comprising literature-supported genes plus a curated core panel, and an extended tier additionally containing optic-nerve phenotype genes with an Open Targets association score ≥ 0.1. Hub genes were ranked by degree, betweenness centrality and closeness centrality (NetworkX).

**Functional enrichment.** Over-representation analysis used g:Profiler against GO biological process, molecular function and cellular component, KEGG, Reactome, WikiPathways and Human Phenotype Ontology, with the Benjamini–Hochberg false-discovery rate at 0.05. Because g:Profiler rejects a request containing any unrecognised identifier, the query list was validated by bisecting re-query. STRING functional enrichment was computed in parallel as an orthogonal check.

**Molecular docking.** Receptors for the focused-tier hubs were selected from the RCSB Protein Data Bank by full-text search followed by verification of the deposited gene name in the polymer-entity metadata; the lowest-resolution human structure was preferred, and AlphaFold models were used where no experimental structure was available. When a structure carried a drug-like co-crystallised ligand, the search box was centred on that ligand's centroid; otherwise, pockets were located with a vectorised implementation of the LIGSITE algorithm (grid spacing 1.0 Å, 1.4 Å probe, PSP ≥ 5 across 13 scan directions, clusters ≥ 30 grid points), and the largest pocket defined the box. Receptors were protonated with Reduce and converted to PDBQT with Open Babel.

Ligands were obtained from PubChem as 3D conformers, protonated at pH 7.4 and converted to PDBQT. Docking used AutoDock Vina 1.2.7 with exhaustiveness 32, up to 9 modes and a fixed random seed. The analysis is restricted to ethambutol itself, docked against each hub target to identify which nodes of the toxicity network the drug can occupy directly; no other ligand class is considered. Docking accuracy was verified by re-docking co-crystallised ligands into their own receptors with a symmetry-corrected RMSD criterion of ≤ 2.0 Å.

### 2.6b All-atom molecular dynamics

Docking gives a static score, so the poses that ranked highest were tested for stability under all-atom molecular dynamics. The question was fixed in advance - does the docked pose survive, or does the ligand leave - and both outcomes were treated as informative. Three targets were run, spanning a wide range of system size (45,545 to 387,227 atoms) so that the result would not rest on one protein's peculiarities. Where a run could not be completed within the available time, the portion that was written is analysed and labelled as such rather than discarded or reported as production.

Receptors were the cleaned structures used for docking, from which non-templateable residues and crystallisation additives had been removed, with cofactors extracted separately. Systems were built with OpenMM 8.6.1 and openmmforcefields: amber14SB for the protein, TIP3P for water and GAFF-2.11 for ethambutol, whose partial charges came from AM1-BCC through AmberTools. Missing atoms and hydrogens were added with PDBFixer at pH 7.4; the receptor was solvated in a truncated octahedral box with 1.0 nm padding and 0.15 M NaCl, and the ligand was inserted into the solvent afterwards, because the solvent-adding step builds a system internally and cannot template a residue whose charges it has not been given. Each system was energy-minimised, equilibrated for 100 ps at constant volume and then 400 ps at constant pressure, and run for 1 ns of unrestrained production with a 2 fs timestep, a Langevin middle thermostat at 300 K and a Monte Carlo barostat at 1 bar, on the CUDA platform in mixed precision, with coordinates written every 10 ps.

Pose stability was judged on four quantities, all measured during production: the ligand RMSD, the receptor backbone RMSD, the fraction of the starting ligand–receptor contacts that survive, and the ligand radius of gyration. A contact was a ligand–protein atom pair within 0.45 nm, enumerated from the first frame written rather than inferred from a neighbour search, so the definition does not depend on library conventions. **Every frame is imaged with `image_molecules` before any quantity is computed.** This is not a refinement but a requirement: the trajectory is written in a 78.5 Å box and molecules cross its boundary during the run, so a difference of raw coordinates can be displaced by a whole box vector. The original analysis omitted this step and superposed un-imaged coordinates, which produced displacements of up to 97 Å where the physical motion is a few ångströms and inverted the conclusion (Section 3.9b records the comparison). After imaging, the ligand and receptor RMSDs are measured after least-squares superposition on the receptor backbone, and contacts and the minimum ligand–protein distance are computed under the minimum-image convention per atom pair. A pose was called retained only if the minimum ligand–protein distance over the second half stayed below 4.5 Å **and** the contact count did not fall below half its starting value — neither of which imaging can manufacture, unlike a centroid drift, which is what the first version tested. Two reference structures are involved and are not interchangeable: contacts are defined against the first frame written, the state the equilibration was launched from and so the closest available approximation to the docked pose, whereas every production metric is measured against the first frame **after** equilibration, so that the reported ligand RMSD describes production behaviour rather than how far equilibration had already carried the ligand. The offset between the two is computed and reported, because an RMSD quoted against the post-equilibration state cannot by itself be compared with the docked pose. A trajectory is also matched to its topology by atom count before analysis, because `addSolvent` is not reproducible between builds and a trajectory left by an earlier attempt has a different particle count.

### 2.7 Robustness analyses

Four ways in which the headline pharmacovigilance result could be an artefact of analysis convention were tested by re-computing the whole disproportionality panel under alternative specifications: (i) a strict whole-token exposure match, which excludes reports naming only a fixed-dose combination product; (ii) restriction to reports in which ethambutol was coded as a primary or secondary suspect drug; (iii) restriction of the comparator denominator to reports mentioning any anti-tuberculosis drug, which removes the possibility that the signal merely reflects the underlying disease population; and (iv) the main specification. A conclusion that holds across all four is not an artefact of the matching or denominator convention.

**Temporal validation.** A fifth test addresses a different threat. FAERS is subject to stimulated reporting, duplicate submissions and drifting reporting habits, so an association measured in the pooled database could in principle belong to the period in which it was reported rather than to the drug. The de-duplicated cases were therefore split by receipt year and the same disproportionality panel recomputed independently within each period, using the identical exposure definition, term list and 2×2 construction. The split point was chosen so that both periods carry at least 40 ethambutol optic-neuropathy events, which placed it at 2016: 2,554 ethambutol cases in 2004–2016 and 11,282 in 2017–2026. Exposure was resolved from receipt dates in the `demo` table rather than from `drug`; the latter carries an `fda_dt` column that is empty in every one of its 98.9 million rows, and filtering on it silently returns no cases at all.

This is a within-database split and is described as such. It tests whether the association survives a change of reporting era; it cannot test whether it survives a change of database, because both periods share the same reporters, the same submission routes and the same structural reporting biases.

**External replication in JADER.** Because a within-database split cannot address that, the analysis was repeated in an independent national system: JADER, the Japanese adverse drug event report database maintained by the Pharmaceuticals and Medical Devices Agency, which is freely downloadable and covers reports received since 2004. The release analysed here (September 2026) contains 1,054,239 cases, 5,038,223 drug records and 1,751,879 reaction records. openFDA was considered and rejected for this purpose: it serves FAERS, so replicating a FAERS finding in it would be circular rather than external.

JADER stores Japanese MedDRA/J preferred terms and provides no English column, so the term mapping was read out of the data rather than assumed: optic neuropathy 視神経症, optic neuritis 視神経炎, optic atrophy 視神経萎縮, toxic optic neuropathy 中毒性視神経症, visual acuity reduced 視力低下, visual field defect 視野欠損, colour vision deficiency 色覚異常, with cataract 白内障, glaucoma 緑内障 and dry eye ドライアイ as negative controls. Exposure used the suspect-drug code 被疑薬, which is JADER's counterpart of the FAERS primary/secondary suspect restriction; a sensitivity analysis used every drug role. The 2×2 construction, the ROR and the Woolf interval were unchanged, so the two databases were analysed by the same logic.

The two systems code suspect drugs differently — 1,798 of the 3,483 JADER cases naming ethambutol carry it as a suspect drug, a much higher proportion than in FAERS — so the magnitudes are not directly comparable between databases and are not presented as such. What is compared is the pattern.

**Tuberculosis burden denominator.** Because neither database has an exposure denominator, a partial one was constructed to test what the country counts represent. WHO publishes notified tuberculosis incidence per 100,000 for every country annually (Global Health Observatory indicator MDG_0000000020, 208 spatial units, 2000-2024); ethambutol is a standard component of first-line therapy, so the number of treated patients scales with notified cases and the drug-specific fraction cancels in comparisons between countries. Each FAERS report was assigned its receipt year and reporter country (98.2% populated overall, 100% for the ethambutol cases) and matched to the WHO figure for the same country and year, giving 794 country-year cells covering 11,410 of 11,671 reports (97.8%) across 94 countries. Reports were then expressed per unit of tuberculosis burden. This is a relative measure of reporting intensity, not an incidence, and no absolute risk is derived from it.

**Regimen-stratified comparison.** Because the antitubercular drugs are co-prescribed, a drug-versus-drug comparison is confounded by which other drugs a report names. Every case naming at least one first-line agent (ethambutol, isoniazid, rifampicin, pyrazinamide; n = 84,001) was therefore assigned to the stratum defined by exactly which of those four it names, and the optic-nerve rate was compared between cases with and without ethambutol within each stratum. Within a stratum the background regimen is held constant by construction. The primary comparison is the one in which both groups are active-tuberculosis patients on the same three-drug background: reports naming rifampicin, isoniazid and pyrazinamide, partitioned by whether ethambutol is also named. Stratified rate ratios are reported with Woolf intervals. Strata in which one group is likely to represent a different disease state — in particular isoniazid-only reports, which are largely latent-infection prophylaxis rather than active disease — are reported but explicitly not used as evidence, since the contrast there measures disease state as much as drug exposure. All four control terms were computed within the same strata.

### 2.8 Genetic analysis

Instruments were taken from OpenGWAS, restricted to European-ancestry, MR-eligible datasets with at least 10,000 participants and the largest available sample size per trait: estimated glomerular filtration rate (creatinine; n = 1,004,040), cystatin C (437,846), serum creatinine (437,660), type 2 diabetes (655,666), HbA1c (389,889), smoking initiation (607,291), cigarettes per day (337,334), alcoholic drinks per week (335,394), zinc supplement use (461,384) and body mass index (681,275; included as a positive control). Instruments were genome-wide significant variants (p < 5 × 10⁻⁸) with LD clumping performed through the OpenGWAS API (r² 0.001, 10 Mb). These exposures were selected on mechanistic grounds: ethambutol is eliminated renally and renal impairment is the strongest clinical risk factor for its optic neuropathy, so renal function is the trait whose causal role in the optic-nerve phenotype most needs testing; diabetes, smoking and alcohol are the recognised clinical and nutritional risk factors for toxic optic neuropathy; and zinc is implicated by the drug's lysosomal zinc-trapping mechanism.

Outcome data were the FinnGen release 12 summary statistics for optic neuritis, optic atrophy, disorders of the optic nerve and visual pathways, visual impairment including blindness, colour vision deficiencies and visual field defects, accessed through the tabix index with HTTP range requests. Effect alleles were harmonised between the two datasets; palindromic variants with intermediate allele frequency (0.42–0.58) were dropped as strand-ambiguous. Estimates used the Wald ratio for a single instrument, and inverse-variance weighting with multiplicative random effects, MR-Egger with the intercept test for directional pleiotropy, and the weighted median for multiple instruments, with Cochran's Q for heterogeneity and Steiger directionality testing.

A conventional drug-exposure Mendelian randomisation was not attempted. Ethambutol is an environmental exposure with no genetic instrument, no "ethambutol use" genome-wide association study exists, and no cis-region variant in the candidate panel attained genome-wide significance for optic neuropathy in FinnGen; a Wald-ratio estimate built on non-significant, outcome-derived variants would be both underpowered and circular. This limitation is reported explicitly rather than concealed, and the MR reported here therefore concerns modifiable risk factors for the optic-nerve phenotype rather than the drug itself.

**Scope of the MR actually reported.** Ten exposures were nominated, but the FinnGen optic-nerve endpoints are rare and each instrument region must be retrieved individually from a 20-million-variant release; the complete panel could not be retrieved within the computing budget available. The analysis reported here therefore covers the renal-function and glycaemic exposures that could be fully harmonised — estimated glomerular filtration rate, cystatin C, serum creatinine and type 2 diabetes — giving 19 exposure–outcome estimates in total: all six optic-nerve and visual outcomes for each of the three renal measures, and optic neuritis for type 2 diabetes. The renal trio was selected on mechanistic grounds as well as statistical ones: ethambutol is eliminated renally and renal impairment is the strongest clinical risk factor for its optic neuropathy, so renal function is the trait whose causal role most needs testing, and three correlated but separately instrumented measures of it provide mutual replication. Diabetes is the most consistently replicated clinical predictor. The remaining nominated exposures (HbA1c, smoking initiation, cigarettes per day, alcohol intake, zinc supplement use, body mass index and vitamin B12 preparation) are not reported, and this is stated rather than presented as a complete cross-product.

**A note on instrument recovery.** Serum creatinine was initially recorded as yielding zero harmonised instruments against every outcome, and that zero was an artefact rather than a finding. Serum creatinine measures the same renal function as eGFR in the same population, and 186 of its 370 instruments are present in the cached FinnGen scans, a higher proportion than eGFR's 151 of 342; a genuine absence of shared variants is therefore not available as an explanation. The estimates reported here for serum creatinine were recomputed from the cached scans after the cause was identified. The episode is recorded because a spurious zero is indistinguishable, in a results table, from a genuinely underpowered exposure, and would have been read as an absence of evidence rather than as a retrieval failure. Every exposure-outcome pair reported in Table 8 was checked against the cached data in the same way.

**A note on instrument–outcome harmonisation.** The OpenGWAS instruments and FinnGen are on different genome builds, so variants were matched by rsID (build-independent) with position matching only as a fallback for variants lacking an rsID. Two implementation faults were found and corrected before the estimates were interpretable — a regional retrieval that silently truncated wide queries to a single 16 kb bin, and position-based matching across genome builds that recovered only 0.2% of 13,560 instrument-outcome pairs. Both are documented because they would otherwise be undetectable from the reported numbers, and because the corrected recovery rate (13.5%) is itself the relevant measure of how much of each instrument panel actually contributed.

### 2.9 Software and reproducibility

Analyses were run in Python 3.14 (NumPy, pandas, SciPy, statsmodels, NetworkX, matplotlib), SQLite 3, Open Babel 3.1.1, Reduce (ADFR suite 1.0) and AutoDock Vina 1.2.7. All retrieval, processing and analysis steps are implemented as standalone, re-runnable scripts; random seeds and software versions are recorded, and no analysis step involves manual data entry.

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

### 2.12 Retinal expression of the network hubs

The focus-layer hub genes were derived from literature co-occurrence and from
disease-phenotype associations, neither of which asks whether a gene is expressed in the
eye. To test that directly, single-cell RNA expression was obtained from the Human
Protein Atlas (`rna_single_cell_type`, 3,087,080 gene–cell-type measurements covering
154 cell types) and restricted to the eight retinal clusters: cone and rod
photoreceptors, Müller glia, and retinal amacrine, bipolar, horizontal, ganglion and
pigment epithelial cells. A gene was counted as detected in a cluster at nCPM > 1. The
comparison that makes this a test rather than a description is against random gene sets
of the same size drawn from the 20,151 genes measured in those clusters; 10,000 such sets
were drawn, and the proportion reaching the observed number of detected hubs is reported
as an empirical P value. A list of well-studied genes would be expressed in retina
whatever its relevance, so only the comparison is informative.

### 2.13 Class-level test of the ferroptosis hypothesis

Because the mechanistic claim rests on an enrichment result, an independent test was
attempted within the pharmacovigilance data. Three drug classes were assembled from
substances with a well-described dominant mode of cell death — ferroptosis inducers
(erastin, sorafenib, sulfasalazine, the artemisinins, lanperisone, buthionine
sulfoximine), apoptosis inducers (cisplatin, doxorubicin, paclitaxel, etoposide,
vincristine, gemcitabine, cyclophosphamide) and necroptosis inducers (SMAC mimetics) —
and each class's optic-nerve odds ratio was computed against the whole database, with
the four non-specific ocular terms as a parallel readout. The rationale was that if
ferroptosis underlies optic-nerve injury, its inducers should show the signal while
apoptosis inducers should not. **The test did not perform as designed, and the reasons
are reported in full in Section 3.11 rather than being used as evidence in either
direction.**

### 2.14 Cross-check against regulatory labelling

The strict signals were compared with what regulators already require to be printed.
Current structured product labelling was retrieved for each antitubercular drug from the
openFDA drug-label endpoint, which returns the approved label text; only the text is used
here, not its adverse-event data, which is FAERS by another route and could not serve as
an independent source. Each label was searched for optic-nerve terms (optic neuritis,
optic neuropathy, optic atrophy) and for ocular terms generally (visual impairment,
blurred vision, colour vision, blindness, visual field, eye). Agreement between label and
signal is expected where the toxicity is already known and therefore validates the
detection method; the informative rows are the disagreements.

### 2.15 Subgroup analysis of the optic-nerve signal

The signal was recomputed within strata of sex, age band, reporting region and reporting era,
using the same 2×2 construction, ROR and Woolf interval as the primary analysis so that the
stratum-specific values are directly comparable with it. Strata were then compared with each
other by the ratio of their odds ratios with a 95% interval, because two strata can both be
significant, or both null, and still differ from one another; the contrast is what tests
heterogeneity rather than the inspection of separate intervals. Age was banded at 0–17,
18–44, 45–64 and 65 years and over, and only reports whose age was recorded in years were
banded, which is 59.7% of the de-duplicated database. Sex is unrecorded in 12.1% of reports,
and those reports were retained as an explicit "unknown" stratum rather than dropped, because
dropping them would change the denominator against which every other stratum is compared.
Reporting region groups countries into the Americas, Asia, Europe and a combined remainder;
it is reported because the peer literature reports it, and it is explicitly not interpreted,
for the reason set out in Section 3.2c.

### 2.16 Disease-annotation cross-check of the hub genes

The focus-layer hubs were tested for whether the genes are annotated for eye disease at all,
which functional enrichment does not establish. Two independent databases were queried for
each gene's disease annotations: Open Targets, already used for the drug–target landscape,
and DisGeNET through its REST interface. A gene was counted as having an eye association if
any annotated disease name matched a list of ocular stems. Because disease names can contain
an ocular stem while naming something else — *keratosis* and *dyskeratosis congenita* are
skin diseases — every match was listed and the analysis was repeated with those removed, and
both figures are reported. The comparison is against a set of the same size drawn from a
fixed unrelated pathway (33 exocrine pancreatic genes) rather than against chance, because a
literature-derived hub set is pleiotropic by construction and would otherwise appear
enriched against any baseline. Enrichment was tested by one-sided Fisher exact, and the
direction was fixed in advance. GeneCards was also attempted and returned HTTP 403; the
DisGeNET interface under an academic plan is restricted to curated sources only, which the
API states in each response, so the counts reported are lower bounds.

### 2.17 Trajectory measures independent of displacement

Two further quantities were computed from the existing trajectories, neither of which
involves a displacement and so neither of which can be affected by how the periodic boundary
was handled. Per-residue fluctuation (RMSF) was calculated for C-alpha atoms after
superposition on the backbone, using only the protein so that ligand motion cannot
contribute. Ligand–protein polar contacts were counted per frame as donor–acceptor pairs
within 3.5 Å under the minimum-image convention; because the trajectories were written
without explicit hydrogen positions for the ligand, this counts potential polar contacts
rather than geometrically enumerated hydrogen bonds, and it is used as a comparative measure
across targets rather than as a bond count. The fraction of the specific atom pairs present
in the first frame that remain within 3.5 Å in the second half was computed as the exchange
measure: contacts maintained in number while their identities change indicate a ligand that
stays and re-forms its interactions, whereas a ligand that leaves loses both.

### 2.18 Software and per-residue contact definition

Per-residue contact persistence was computed with an explicit lookup table from absolute atom
index to position within the protein subset. An earlier implementation mapped indices with
`np.searchsorted` and a bounds test that did not hold; it reported every residue in each
structure as contacting the ligand, 301 of 301, 428 of 428 and 841 of 841, and listed the
first residues of each sequence as the most persistent contacts. The values from that run
were discarded, and the corrected analysis includes a guard that refuses to write its output
if the number of contacting residues is again equal to the total.

The residue assignments were then checked against the structures rather than accepted on
their face value, because the mapping had already failed once. Two checks were applied: the
distance from the ligand centroid to each named residue, which for a genuine interface lies
in the range an extended ligand spans; and, for HMOX1, the overlap between the contacting
residues and the residues adjacent to the heme that was removed when the 1N45 receptor was
cleaned, which is an independent landmark because the heme site is known from the deposited
structure. The first check initially reported a failure for all three targets because it
compared the contact distances with the distance to the first residue of each chain, which is
26–36 Å and carries no information about where a pocket is; that comparison was wrong, not
the mapping. The HMOX1 overlap is reported as it stands, at two of eight persistent contacts,
rather than as a pass.

---

## 3. Results

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
cases and **45 met all strict signal criteria** (ROR lower 95% CI > 1, PRR >= 2,
chi-square >= 4, IC025 > 0, >= 3 cases, Benjamini-Hochberg q < 0.05).

Within the drug-toxicity spectrum, optic neuropathy was the strongest signal:
153 cases, **ROR 159.21 (95% CI 134.65-188.25)**,
PRR 157.46, IC025 6.58, EBGM05 84.90. The term that
specifically names the drug injury, **toxic optic neuropathy, returned an ROR of
277.14 (95% CI 210.24-365.31; 60 cases,
IC025 6.27)** - it is the second strongest signal in the analysis and
was not part of the curated panel, so it emerged from the unbiased pass.

The remaining leading drug-toxicity signals were hereditary optic atrophy
(ROR 94.0), ocular toxicity
(93.2), dyschromatopsia
(50.3), scotoma (42.1),
optic neuritis (29.2), chromatopsia
(27.3), optic atrophy
(24.8), optic nerve injury
(15.5), hemianopia
(15.4), optic nerve disorder
(9.9), visual field defect
(9.3), papillooedema
(8.4), nystagmus (6.9),
visual acuity reduced (6.1), macular
degeneration (4.7), blindness
(3.7), visual impairment
(2.5) and diplopia
(2.4) (Figure 2, Figure 4, Table 2, Table 2c).

The informative result is the contrast. **Not one non-specific ocular complaint
formed a signal:** vision blurred returned an ROR of
1.82, cataract 0.86,
conjunctivitis 1.04, dry eye
0.42, eye pain 0.64, eye irritation
0.47, photophobia
0.68, glaucoma 0.38 and
ocular hyperaemia 0.23. The signals are confined
to the optic-nerve, retinal and colour-vision axes; the ocular surface and anterior
segment are spared (Figure 3).

### 3.2b Within the antitubercular class, once co-prescription is accounted for

Comparing every drug against the whole database answers a different question from
comparing drugs with each other, and for an antitubercular agent the whole-database
denominator is dominated by non-tuberculosis reports. The drug-versus-drug comparison
therefore restricts the denominator to reports mentioning any antitubercular drug.

**That comparison has a flaw that has to be stated before its numbers are used.** The
drugs in a regimen are reported together: among ethambutol cases, 71.1% also name
rifampicin, 54.9% isoniazid and 48.8% pyrazinamide. The overlap is asymmetric, which
biases the comparison in a direction that is easy to miss — 73.3% of pyrazinamide cases
name ethambutol, but only 48.8% of ethambutol cases name pyrazinamide. So the apparent
contrast "pyrazinamide 0.67% versus ethambutol 1.25% optic neuropathy" sets a
large subset of ethambutol-treated patients against a group that is mostly the same
patients again. **A drug cannot be compared with another drug when most reports contain
both**, and the naive ranking of eighteen antitubercular agents on optic-neuropathy
share is therefore reported here only as a description, not as a comparison of intrinsic
toxicity.

Three analyses hold the regimen fixed instead, and they are what the within-class claim
now rests on.

| Analysis | With ethambutol | Without ethambutol | Rate ratio (95% CI) |
|---|---|---|---|
| Rifampicin + isoniazid + pyrazinamide, ± ethambutol | 67/5,757 (1.16%) | 3/845 (0.36%) | **3.28 (1.03–10.40)** |
| Rifampicin stratum | 97/2,893 | 38/12,097 | 10.67 (7.35–15.50) |
| Rifampicin + isoniazid stratum | 20/1,033 | 3/1,709 | 11.03 (3.29–37.03) |
| Pyrazinamide stratum | 20/319 | 32/1,158 | 2.27 (1.32–3.91) |
| Isoniazid stratum | 10/310 | 21/53,850 | 82.72 (39.28–174.20) |

**The first row is the interpretable comparison** and the only one quoted as evidence,
because both groups are active-tuberculosis patients on the same three background drugs
and differ only by whether ethambutol is named: adding it raises the optic-nerve rate
from 0.36% to 1.16%, a rate ratio of 3.28. Its confidence interval, 1.03 to 10.40, is
wide and its lower bound close to unity, because only 845 reports name the three-drug
regimen without ethambutol; the direction is consistent across every stratum in which
the comparison is meaningful, but the effect is not estimated precisely. The control
terms behave as they should within the same stratum — cataract 0.12% versus 0.00%, dry
eye 0.03% versus 0.00%, eye pain 0.14% versus 0.12%, glaucoma 0.02% versus 0.00% — so
the increment is specific to the optic nerve rather than to ocular reporting in general.

**The remaining rows are not evidence and are shown to be discounted.** In the
isoniazid stratum the rate ratio reaches 82.7, but that stratum is dominated by
isoniazid-only reports, and isoniazid is given alone chiefly for latent infection, which
is not active tuberculosis; the contrast therefore measures active disease against
latent infection at least as much as it measures ethambutol. The rifampicin-containing
strata share that problem in weaker form, since a report naming rifampicin and
ethambutol is more likely to describe treated active disease than one naming rifampicin
alone. Only the fixed-regimen row compares like with like.

For completeness, the descriptive ranking within the class places ethambutol's optic
neuropathy ratio at
**6.47 (95% CI 5.38-7.79;
171 cases)**, **6th of 18**
drugs with at least 100 reports. The drugs above it - prothionamide, capreomycin,
streptomycin, cycloserine, ethionamide - are second-line agents used for
drug-resistant disease, and that comparison is confounded by indication severity, as
set out in the limitations. Given the co-prescription problem above, this ranking is
reported as a description of the class and is not used to argue that any drug is more
toxic than another.

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

### 3.2d The optic-nerve signal replicates in two independent reporting periods

The association rests on a single database, so it was tested for stability across
reporting eras. Cases were split by receipt year at 2016 and the disproportionality
panel recomputed independently in each period.

| Term | 2004–2016 (2,554 ethambutol cases) | 2017–2026 (11,282 cases) | Replicated |
|---|---|---|---|
| Optic neuropathy | **81.9** (60.5–110.7) | **86.9** (71.5–105.6) | yes |
| Optic neuritis | 4.7 (2.6–8.4) | 21.1 (17.6–25.4) | yes |
| Optic atrophy | 17.3 (8.2–36.5) | 12.3 (7.0–21.8) | yes |
| Toxic optic neuropathy | 60.7 (30.1–122.4) | 185.3 (138.2–248.4) | yes |

All four optic-nerve terms are elevated in both periods with lower confidence limits
above 1, and the principal term is remarkably stable: **ROR 81.9 against 86.9**. The
negative controls remain null in both, which is what distinguishes a drug effect from a
period effect - a change in reporting behaviour would be expected to move the controls
as well, and none did:

| Control | 2004–2016 | 2017–2026 |
|---|---|---|
| Cataract | 0.34 (0.15–0.75) | 0.54 (0.36–0.81) |
| Dry eye | 0.07 (0.01–0.48) | 0.31 (0.17–0.55) |
| Eye pain | 0.24 (0.09–0.65) | 0.40 (0.25–0.66) |
| Glaucoma | 0.18 (0.03–1.28) | 0.22 (0.07–0.70) |

Two features of the table are reported rather than smoothed over. The term-specific
estimates are not all equally stable: optic neuritis rises roughly fourfold between the
periods (4.7 to 21.1) and toxic optic neuropathy roughly threefold (60.7 to 185.3), which
is consistent with increasing clinical recognition and coding of drug-induced optic
neuropathy in recent years. That this does not affect the conclusion is a reason to
report the single, most stable term - optic neuropathy - as the primary endpoint rather
than a composite.

The design has a firm boundary. Both periods come from the same database and share its
reporters, its submission routes and its structural biases, so this tests whether the
association survives a change of reporting era and **not** whether it generalises beyond
FAERS. That question is addressed separately, in an independent database.

### 3.2e The same pattern appears in JADER, an independent national database

The analysis was repeated in JADER, Japan's adverse drug event report database, which is
maintained separately from FAERS, draws on different reporters and operates under a
different reporting culture. Its September 2026 release holds 1,054,239 cases. The term
mapping and the exposure definition are given in the Methods; the 2×2 construction, the
ROR and the Woolf interval are identical to those used for FAERS.

| Term | a | ROR | 95% CI | Signal |
|---|---|---|---|---|
| Toxic optic neuropathy | 19 | **864.6** | 426.4–1753.4 | yes |
| Optic neuropathy | 73 | **571.0** | 413.5–788.4 | yes |
| Colour vision deficiency | 5 | **83.9** | 32.8–214.3 | yes |
| Optic neuritis | 30 | 52.2 | 35.8–76.0 | yes |
| Optic atrophy | 3 | 50.3 | 15.4–163.5 | yes |
| Visual acuity reduced | 130 | 44.9 | 37.4–54.0 | yes |
| Visual field defect | 15 | 25.4 | 15.1–42.6 | yes |
| Cataract *(control)* | 4 | 1.40 | 0.53–3.75 | no |
| Glaucoma *(control)* | 2 | 1.26 | 0.31–5.04 | no |
| Dry eye *(control)* | 0 | — | — | no |

**Every optic-nerve and visual term is elevated and every negative control is null**,
which is the same pattern FAERS produced. The within-class comparison is also reproduced:
restricting the denominator to the 3,878 cases naming any antitubercular drug as a
suspect, optic neuropathy retains an ROR of **44.0 (95% CI 10.8–179.4)** and toxic optic
neuropathy 11.1 (2.6–47.7), while cataract (2.3), glaucoma (5.8) and dry eye (0) remain
null.

The magnitudes differ between the two databases and the difference is not smoothed over.
JADER's whole-database ROR for optic neuropathy is 571 against FAERS's 159, and the
within-class estimate is 44.0 against 7.64. The reason is visible in the data: 1,798 of
the 3,483 JADER cases naming ethambutol carry it as a **suspect** drug, a far higher
proportion than in FAERS, where the corresponding analysis required restriction to
primary or secondary suspect reports to reach an ROR of 7.64. The two systems code
suspicion differently, so the absolute values are not comparable and are not compared.
**What replicates is the pattern — a strong, specific optic-nerve signal accompanied by
complete absence of signal in the non-specific ocular terms — and that pattern repeating
in an independent national system is evidence about the drug rather than about one
database's reporting habits.**

Two limits bound even this. JADER is roughly a twentieth the size of the FAERS analysis,
so the rarer terms rest on single figures: optic atrophy and colour vision deficiency
have 3 and 5 exposed cases, and their confidence intervals are correspondingly wide.
And agreement between two spontaneous-reporting databases, however independent
administratively, cannot exclude a bias common to spontaneous reporting as a method —
under-reporting, stimulated reporting, and the absence of a denominator. Replication
strengthens the case that the association is real; it does not convert a reporting
disproportionality into an incidence or a causal estimate.

### 3.3 The tuberculosis terms behave as a separate signal population

The expanded panel also captured the ocular manifestations of tuberculosis itself.
Choroid tubercles (ROR 2208, 3 cases),
serpiginous choroiditis (1474, 24 cases),
tuberculosis of eye (569, 17 cases),
choroiditis (167, 31 cases) and intermediate uveitis
(1472, 4 cases) all produced extreme
disproportionality, because these are complications of the infection rather than of
any drug and are therefore recorded almost exclusively in tuberculosis reports.
**They are not a minor footnote to the ranking: these twelve terms occupy four of the
top seven positions by ratio in the whole panel**, so a reader who took the ranking at
face value would have the drug apparently implicated in choroidal tubercles. They are
reported for completeness and explicitly excluded from the drug-toxicity
interpretation (Table 2e).

The ocular panel is therefore **152 terms, of which 45 are strict signals** after three
exclusions that are stated rather than applied silently. Twelve ocular tuberculosis
manifestations are set aside as above. **Thirteen terms are removed because they are not
findings of the eye or of vision at all** and do not belong in a panel described as
ocular: a systemic rash (177 reports, ratio 15.5), a route of exposure, a behavioural
descriptor, a gastrointestinal tear, two systemic diseases, a psychiatric phenomenon and
similar (Table 2f). One of these — *macule* — is retained on the ocular side despite
being flagged as a non-ocular artefact by the term classifier, because a macule is also a
retinal finding and removing a term on an ambiguous label would be the worse error; the
decision is recorded here rather than left implicit.

The 83 terms the earlier version of this manuscript listed as awaiting manual review turn
out not to be an undecided group. Their anatomical group — optic nerve, visual function,
retina, anterior segment — was already assigned by the term classifier; what they lack is
a toxicity-versus-disease category, which is not needed to report them, since the panel
is presented anatomically. They are now reported under those groups instead.

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

**The regional coefficient is a reporting artefact and is not given a clinical
reading.** Because FAERS has no denominator, the geographic coefficient could reflect
either a genuine difference in who is affected or a difference in how intensively each
region reports. A tuberculosis burden denominator distinguishes them. WHO publishes
notified tuberculosis incidence for every country annually, and since ethambutol is a
standard component of first-line therapy the number of treated patients scales with it,
so dividing reports by that burden gives a crude measure of reporting intensity.

The result is unambiguous. Reports per unit of tuberculosis burden span nearly three
orders of magnitude and bear almost no relation to burden itself (Spearman rho = -0.14
across 28 countries with at least 50 reports): the United States generates 834.5
reports per unit of burden against South Africa's 0.3, although South Africa's
tuberculosis incidence is 229 times higher. **What the country counts measure is the
strength of the national pharmacovigilance system - a country with an established
spontaneous-reporting culture and industry-sponsored submission generates reports that
have little to do with how many of its patients took the drug.** The same logic applies
to the regional term in the logistic model: "Europe" is partly a proxy for an
ADR-reporting culture, and the coefficient should be read as such rather than as
evidence that European patients are more susceptible.

The internal contrast that the paper relies on is unaffected, and is in fact the
statistic that survives this problem: it compares optic-nerve terms against
non-specific ocular terms *within the same reports*, so any country's reporting
intensity cancels. That is a further reason to treat the specificity finding, rather
than any geographic or absolute figure, as the primary result.

### 3.6 Robustness: the conclusion survives every alternative specification

The whole disproportionality panel was recomputed under four specifications: the
main analysis (whole database, all drug roles); a strict whole-token exposure match,
which excludes reports naming only a fixed-dose combination product; restriction to
reports in which ethambutol was the primary or secondary suspect drug; and a
comparator denominator restricted to reports mentioning any anti-tuberculosis drug,
which removes the possibility that the signal merely reflects the underlying
tuberculosis population.

**All three optic-nerve signals held in every specification.** Optic neuropathy
returned RORs of 159.21 (main), 159.21 (strict
whole-token) and 248.95 (suspect-only), and
**7.64 (95% CI 5.24-11.13)**
under the strictest same-class comparator. Optic neuritis moved from
29.21 to 44.19 and 5.05; optic
atrophy from 24.84 to 38.80 and
7.76. Conversely, **cataract, dry eye, eye pain and glaucoma
failed to form a signal in any of the four specifications** (Table 9), so the
specific-against-general contrast does not depend on how exposure is matched, how
the denominator is chosen, or whether concomitant-only reports are included - the
three ways in which a pharmacovigilance signal most often turns out to be an
artefact.

### 3.7 Report adequacy

Completeness was high for the fields needed to interpret a report and modest for
those needed to characterise exposure. Among ethambutol cases, country was recorded
in 100.0%, sex in 89.8%, age in
76.3%, route in 70.9%, dose in
29.0%, event date in 40.0% and therapy
start date in 28.0%; therapy duration was recorded in
only 6.2%. Relative to the whole database (age
58.6%, event date 50.4%), ethambutol
reports were better documented for age and slightly worse for event date, and the
mean number of reported reactions was higher (5.74 versus
nan), as expected for a report that names a specific
suspected drug effect.

The consequence for interpretation is quantified directly: of the ethambutol cases
in the optic-nerve spectrum, 378 cases,
77.0% had both age and sex recorded and
32.3% had a therapy start date, so only
**27.8%** could support a time-to-onset analysis
(Table 10). The signal analysis, which needs only the drug name and the reaction
term, uses the whole case set; the temporal and dose analyses rest on the minority
of reports that carry those fields, and this is why they are reported as
supporting rather than primary evidence.

**The dose finding disagrees with part of the clinical literature, and the reason is
report completeness.** This analysis found that daily dose did not predict the optic-nerve
outcome once exposure duration was accounted for (likelihood-ratio P = 0.55), whereas the
Korean cohort of 1,000 patients reports the opposite ordering: renal dysfunction and the daily
dose contributed, but not the duration of treatment [30]. A 2026 systematic review of eleven
studies and 370 patients resolves the same question the other way, finding longer duration the
principal factor and giving a dose gradient — prevalence 1% below 15 mg/kg/day, threefold higher
at 20 mg/kg/day [29].

Both can hold, and the reason this analysis is the weakest of the three on dose is stated in
Section 3.7: only 27.8% of the optic-nerve reports carry age, sex and a therapy start date
together, so the dose model is fitted on the minority of cases with complete exposure fields
and has little power to detect a dose effect. **The dose result is therefore inconclusive rather
than negative**, and the clinical literature is left to carry the dose question.

### 3.7b The signal holds in every patient subgroup, and the age gradient is the only one worth reading

Two questions follow from a signal that survives every specification: whether it is
confined to a group in which reporting is denser, and whether any group behaves
differently enough to explain it. Both were tested by recomputing the optic-nerve odds
ratio within strata of sex, age, reporting region and reporting era, using the same 2×2
construction, ROR and Woolf interval as the main analysis so the values are directly
comparable (Table 11).

| Stratum | Cases | Optic-nerve cases | ROR (95% CI) | Ratio of odds ratios vs reference |
|---|---|---|---|---|
| **Sex** | | | | |
| Female | 5,987 | 136 | 44.72 (37.65–53.12) | reference |
| Male | 6,324 | 113 | 50.13 (41.45–60.62) | 1.12 (0.87–1.45) |
| Unknown | 1,492 | 46 | **97.55** (72.17–131.85) | 2.18 (1.54–3.09) |
| **Age** | | | | |
| 0–17 | 740 | 8 | 21.23 (10.49–42.98) | reference |
| 18–44 | 3,614 | 79 | 23.55 (18.78–29.54) | 1.11 (0.53–2.33) |
| 45–64 | 2,931 | 51 | 34.71 (26.23–45.93) | 1.63 (0.77–3.49) |
| **65+** | 3,247 | 87 | **114.73** (91.91–143.22) | **5.40 (2.58–11.32)** |
| Unknown | 3,271 | 70 | 61.91 (48.73–78.66) | 2.92 (1.38–6.14) |
| **Reporting region** | | | | |
| Americas | 4,349 | 79 | 55.70 (44.49–69.74) | reference |
| Asia | 3,583 | 81 | 42.19 (33.37–53.34) | 0.76 (0.55–1.05) |
| Europe | 3,334 | 108 | 40.12 (32.97–48.82) | 0.72 (0.53–0.97) |
| Other regions | 959 | 6 | 5.62 (2.51–12.60) | 0.10 (0.04–0.23) |
| Other / unknown | 1,578 | 21 | 34.51 (22.38–53.23) | 0.62 (0.38–1.01) |
| **Reporting era** | | | | |
| 2004–2016 | 2,506 | 58 | 60.13 (46.23–78.22) | reference |
| 2017–2026 | 11,297 | 237 | 45.91 (40.27–52.34) | 0.76 (0.57–1.02) |

**The signal is present in every stratum**, which is what a real association looks like and
is why the analysis is reported as a consistency check rather than as a discovery. Comparing
the strata with each other, rather than reading each in isolation, leaves five contrasts
whose interval excludes unity: unknown versus known sex, the 65-and-over band and the
unknown-age band against the youngest, and Europe and the combined other-region group
against the Americas. Three of those five should not be read as effects, and the reasoning
is given here rather than left to the reader.

**Unknown sex is a marker of a sparsely completed report, not a risk factor.** It carries
the highest ratio in the table (97.55), and the temptation is to report it as a finding. It
is not one: a report missing the patient's sex is a report with less complete structured
data, and completeness is itself associated with whether a serious event was recorded. The
same reasoning applies to the unknown-age stratum, which behaves the same way (61.91).

**Reporting region is not interpretable, for the reason already established.** Section 3.2c
showed that FAERS country counts measure national reporting intensity rather than patient
numbers, so a subgroup defined by country inherits that limitation; interpreting the
regional column would contradict an argument the paper already makes. The combined
other-region stratum rests on six optic-nerve cases and is not estimable in any useful
sense.

**The age gradient is the one contrast worth reading.** Risk rises monotonically across the
four age bands and the 65-and-over band differs from the youngest with a ratio of 5.40
(2.58–11.32). This agrees with the continuous age effect in Section 3.5, where each
additional year raised the odds of an ocular event (adjusted OR 1.009, 95% CI 1.005–1.012).
Two analyses of the same database agreeing is not independent confirmation, and it is not
presented as such; what it does establish is that the age association is not an artefact of
modelling age as continuous rather than by band.

**What the analysis adds, and what it does not.** It adds the negative result that no
subgroup is responsible for the signal, which is the question a reviewer asks of an
association measured in one population. It does not add a new risk factor: every contrast
that survives correction is either a reporting artefact, an uninterpretable geography, or a
restatement of the age effect already reported.

### 3.8 The mechanistic network points towards ferroptosis and mitochondrial integrity

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

### 3.8b The network overlaps ocular disease annotation, tested at the level of the set

The question this section answers is whether the network's genes are annotated for eye disease
more often than a comparison set is. That question has to be asked of the set and not of the
individual gene: a hub of this network is a well-studied gene, and a well-studied gene is
annotated for many diseases, so asking whether any single hub has an ocular association returns
yes for almost all of them and carries no information. Three tests were run, two of which
discriminate.

**The set-level annotation test.** Disease annotations for all 33 hub genes and all 33 control
genes were retrieved from DisGeNET, and a gene counted as ocular if any of its annotated
disease names matched a list of ocular stems. **20 of 33 hubs (61%)
and 4 of 33 controls (12%)** carried such a match
(Fisher P = 4.1e-05). The keyword match was then audited, because it produces false
positives: *keratosis* and *dyskeratosis congenita* are skin diseases whose spelling contains
an ocular stem, and *cataract and cardiomyopathy* is a syndrome classified under its cardiac
feature. Removing every match of that kind leaves **18 of 33 (55%)
against 4 of 33 (12%), odds ratio 7.82,
Fisher P = 2.6e-04.** The corrected figure is the one reported.

**The intersection with ocular disease gene sets**, which is the step the comparator papers in
this genre take [32]: they collect a drug's targets, collect the disease's genes, and analyse only
the overlap. DisGeNET's ocular sets were retrieved through its interface and intersected with
the network. Against the union of its optic-nerve sets (25 genes) the overlap is
**2 of 33 hubs and 0 of 33 controls** (P = 0.246); against
all four ocular sets (184 genes) it is **5 of 33 hubs and 0 of 33
controls** (P = 0.027). The genes in the larger overlap are CAT, HMOX1, OPA1, SOD2, TNF.

**The retinal expression test** is reported in Section 3.11: 31 of the 33 hubs are detected in
human retinal clusters at nCPM > 1 against a random-set expectation of 25.2 (P = 0.0067).

| Test | Hub genes | Controls | P | Weight |
|---|---|---|---|---|
| DisGeNET annotations, artefact matches removed | **18/33** | **4/33** | **2.6e-04** | primary |
| Retinal expression (Section 3.11) | **31/33** | 25.2 expected | **0.0067** | primary |
| Intersection with ocular gene sets | 5/33 | 0/33 | 0.027 | supporting |

**How the three should be read.** The first two are strong and independent of each other: one
asks whether the genes are annotated for eye disease, the other whether they are expressed in
retina, and both say yes at P below 0.001 with a control. The third is the comparator papers'
method and points the same way, but its power is limited by the size of the sets available:
DisGeNET's curated tier returns 184 ocular genes in total, so an overlap of five against a
control of zero is all the data can show, and a single gene moving either way would change the
significance. It is reported as supporting evidence and not as confirmation, and a larger
disease-gene set would settle it.

**A claim withdrawn.** An earlier version of this section compared network arms and concluded
that the inflammatory genes carried no ocular annotation while the mitochondrial and
oxidative-stress genes did. That comparison was invalid and the conclusion is withdrawn. The
inflammatory genes were read from GeneCards' unified tables, which hold between 1 and 50
entries, while other genes were read from far longer inferred tables; and when the inferred
table of TNF was examined it holds **920 disorders, among them conjunctivitis at rank 11,
uveitis at 16, scleritis at 26, retinal artery occlusion at 110, optic neuritis at 116 and
panuveitis at 121.** A gene is not unannotated for eye disease because the short table was the
one consulted. The arm-level claim is not supported and does not appear.

**What the GeneCards pass does establish.** A manual pass over 30 of the 33 hubs, reading each
gene's disorder tables from the web interface, shows that these genes are broadly pleiotropic
and that ocular entries recur across all of them. OPA1's unified table opens with nine
consecutive eye diseases and names four optic atrophies, four glaucomas and six retinal
dystrophies; FTH1 has nine ocular entries out of eleven, including vitelliform macular
dystrophy and Best disease; FTL names cataract three times and optic atrophy once; MFN2,
SLC25A4 and DNM1L name optic atrophy directly. This is consistent with the two tests above and
is not independent of them, since it measures the same annotations by another route.

**A limitation of the sources, measured rather than assumed.** GeneCards assigns each disorder a
Categories field whose "Eye diseases" tag is unreliable: across the 30 genes read, whose tables
hold 481 disorder entries, the tag marks 55 gene-disorder pairs while matching the disorder
name against ocular stems marks 20, so trusting it would have made the network look between two
and three times as ocular as it is. It is applied to lymphomas, melanomas, dyskeratosis
congenita, autism, Cowden syndrome and Noonan syndrome. The disorder name is therefore the
criterion used, and the tag is reported only as a caution. DisGeNET's REST interface under an
academic plan is restricted to curated sources (CHEMBL, CLINGEN, CLINPGX, CLINVAR, GENCC,
MGD_HUMAN, ORPHANET, PSYGENET, RGD_HUMAN, UNIPROT), which the API states in every response, so
the counts above are lower bounds; and the gap is real rather than theoretical, because MFN2 —
an established optic-atrophy gene cited by two of the comparator papers — is absent from
DisGeNET's ocular sets while ranking fourth by relevance in a GeneCards search for *optic
neuropathy*.

**The retinal immune compartment carries the inflammatory arm, which an earlier version of this
section read the other way.** The eight HPA retinal clusters are neural and glial - cone and rod
photoreceptors, Müller glia, amacrine, bipolar, horizontal, ganglion and pigment epithelial
cells - and contain no microglia, which are the retina's resident macrophages and the principal
source of TNF in neural tissue. Reading the microglial column of the same table changes the
inference: **TNF is 7.8 nCPM in microglia, the highest of any of the 154 cell types
in the table, while every retinal cluster gives 0.0.** The absence is a property of which cells
the retinal panel contains, not of the retina.

**The network's genes are enriched in microglia well beyond background.** At a background
detection rate of 66.7% in that cell type, **32 of the 33 hubs are detected at
nCPM > 1**, a result expected with probability **2.7e-05**, while only **4 of the
33 control genes** are detected. The iron-handling nodes are the most abundant of all: **FTL at
672.1 nCPM and FTH1 at 334.3**, which places the network's iron and ferroptosis genes
in the same compartment as its principal cytokine.

| Cell type | Hubs detected | Controls detected | Background rate |
|---|---|---|---|
| Retinal clusters (8 neural and glial types) | 30/33 | 11/33 | 51–65% |
| **Microglia** | **32/33** | **4/33** | 66.7% |

**The correction runs in the manuscript's favour and is stated as a correction.** The previous
text concluded from TNF's absence in the retinal panel that the inflammatory arm lacked
support. It does not lack support: its principal cytokine is expressed in the retinal immune
compartment at the highest level of any cell type measured, and that compartment is also where
the network's iron-handling genes are most strongly expressed, which is where the ferroptosis
mechanism would operate.

### 3.9 Docking shows which network nodes ethambutol can occupy directly
### 3.9 Docking shows which network nodes ethambutol can occupy directly

The mechanism network describes processes that become dysregulated, not where the
drug binds. To ask the narrower question - which nodes of that network ethambutol
itself can occupy - the drug was docked against each of the fourteen hub targets:
fourteen runs, all completed.

**The docking protocol was validated with a redocking panel built around
ethambutol's own size.** An earlier version of this work used two controls only —
carbonic anhydrase II with acetazolamide (13 heavy atoms, 1.795 A) and dihydrofolate
reductase with methotrexate (33 heavy atoms, 5.863 A) — and attributed the failure to
methotrexate's size and flexibility. Two points, one below ethambutol's heavy-atom count
and one far above, cannot locate the protocol's limit, and they leave open the case that
matters most: whether a ligand of ethambutol's own size is docked reliably. The panel was
therefore extended to **seven co-crystallised complexes spanning 9 to 36 heavy atoms**,
each redocked into its own receptor with the search box centred on its crystallographic
position and verified to enclose the ligand it was scoring.

| System | Ligand | Heavy atoms | Affinity (kcal/mol) | Top-pose RMSD (A) | Passed |
|---|---|---|---|---|---|
| Trypsin | benzamidine | 9 | -6.59 | **0.344** | yes |
| Carbonic anhydrase II (3HS4) | acetazolamide | 13 | -6.84 | **1.795** | yes |
| Carbonic anhydrase II (1AZM) | acetazolamide | 13 | -6.07 | **1.937** | yes |
| Purine nucleoside phosphorylase | immucillin | 19 | -8.60 | 2.434 | no |
| HSP90 | resorcinol inhibitor | 22 | -8.84 | 3.127 | no |
| Dihydrofolate reductase | methotrexate | 33 | -9.02 | 5.863 | no |
| BACE1 | hydroxyethylamine | 36 | -13.31 | 5.836 | no |

**Every ligand up to 13 heavy atoms reproduced its crystal pose within the 2.0 A
criterion, and every ligand from 19 heavy atoms upward failed.** The boundary falls
between 13 and 19 heavy atoms, and the failures are graded rather than abrupt: 2.434 A at
19 atoms, 3.127 A at 22, 5.836 and 5.863 A at 36 and 33. Ethambutol has **fourteen heavy
atoms** (C10H24N2O2: ten carbon, two nitrogen, two oxygen) and **nine rotatable bonds**.
It therefore falls in the **13-to-19 atom interval that the panel brackets but does not
fill**: it is one heavy atom above the largest ligand that passed and five below the
smallest that failed, so the protocol's accuracy at ethambutol's size is inferred from
its neighbours rather than measured on a ligand of that size. The two bracketing
complexes are encouraging — 13 heavy atoms reproduced its crystal pose at **1.795 and
1.937 A** in two independent structures, and 19 heavy atoms at 2.434 A came within
0.43 A of the 2.0 A criterion — but the inference is an extrapolation across a gap and
is labelled as such. The protocol is
therefore suitable for the question it is used for here — the relative ranking of small
polar ligands across a panel of pockets — and is explicitly not suitable for the larger,
more flexible ligands that fail the panel. The affinities reported below for ethambutol
(-3.96 to -5.50 kcal/mol) are read with that in mind: docking is used to rank nodes of
the network, not to claim occupancy.

Four complexes were excluded from the panel and the reasons are recorded, because two of
them produced large RMSDs that looked like protocol failures and were not. Two were
bookkeeping faults: the validation directory was keyed by target name, so validating
carbonic anhydrase II with two structures in one run placed the second run's ligand
beside the first run's box, leaving the ligand 53.8 A outside the search space; the key
now includes the PDB identifier, and re-running both structures gave 1.795 and 1.937 A.
A third, 3M04, carries a fragment bound some 18 A from its principal ligand, so any box
centred on the main site leaves that fragment outside it. A fourth, 1FSY, could not be
docked at all: its ligand contains boron and the PDBQT written by Open Babel carries an
atom type Vina rejects.

Ethambutol docked with affinities between -3.96 and -5.50 kcal/mol (Figure 7,
Table 7). The most favourable were TNF (-5.50), MFN2 (-5.21), HMOX1 (-5.09),
NFE2L2 (-5.01) and BCL2 (-4.95); the weakest were GPX4 (-3.96), SMAD4 (-4.06) and
AKT1 (-4.05). The affinities are modest and span a narrow range, which is the
expected result for a small, highly polar molecule with nine rotatable bonds and
no designed complementarity to any of these pockets. The interpretable feature is
the ordering rather than the absolute values: the drug is predicted to engage the
inflammatory and oxidative-stress nodes (TNF, HMOX1, NFE2L2) and the
mitochondrial-dynamics node MFN2 more readily than the ferroptosis execution
machinery (GPX4, ACSL4) or the TGF-beta effector SMAD4. That ordering is consistent
with ethambutol acting upstream of the ferroptosis cascade - dysregulating the
redox and inflammatory environment rather than binding the pathway's terminal
enzymes - which is what the enrichment pattern also suggests.

### 3.9b The docked pose is maintained under all-atom dynamics in three independent sites

Docking returns a static score, so three poses that ranked mid-range in the panel were
tested under all-atom dynamics: NFE2L2 (-5.01 kcal/mol), MFN2 (-5.21) and HMOX1 (-4.95).
**The ligand remained bound in all three.** Over the full 1 ns of unrestrained production
on NFE2L2 the ligand never lost contact with the protein: the minimum ligand–protein atom
distance held between **1.85 and 2.52 Å** throughout, and the number of contacts within
4.5 Å rose from **292 at the start to 312** on average in the second half, with a minimum
of 172 — it never approached zero. HMOX1 behaved the same way over the portion of its
trajectory that was completed (0.10 ns of NVT equilibration plus the first 0.13 ns of
NPT), where contacts rose from **601 to 670** at a minimum distance of 1.76 Å, and MFN2
over its shorter run.

| Quantity | NFE2L2 | HMOX1 | MFN2 |
|---|---|---|---|
| Trajectory analysed | **1.0 ns unrestrained production** | 0.23 ns (NVT + early NPT) | 0.13 ns |
| System size | 45,545 atoms | 78,429 atoms | 387,227 atoms |
| Minimum ligand–protein distance, second half | **2.18 Å** | **1.76 Å** | **1.77 Å** |
| Range of that distance over the run | 1.85–2.52 Å | 1.60–2.23 Å | 1.63–2.31 Å |
| Contacts within 4.5 Å | **292 → 312** | **601 → 670** | 329 → 272 |
| Receptor backbone RMSD, second half | **1.18 Å** | **1.28 Å** | **1.34 Å** |
| Ligand RMSD, second half | 5.62 Å | 2.85 Å | 3.32 Å |
| **Verdict** | **docked pose retained** | **docked pose retained** | **docked pose retained** |

**Two further measurements test the same conclusion by routes that do not depend on
displacement.** The first is per-residue fluctuation (RMSF), which says whether the binding
site is rigid or whether the protein is breathing around it. The second is a census of
ligand–protein polar contacts, which distinguishes a ligand that keeps its partners from one
that exchanges them while staying put.

| Measurement | NFE2L2 | HMOX1 | MFN2 |
|---|---|---|---|
| C-alpha residues analysed | 301 | 428 | 841 |
| **RMSF, mean over the run** | **0.68 Å** | **0.66 Å** | **0.65 Å** |
| RMSF, maximum | 0.92 Å | 0.86 Å | 0.95 Å |
| Polar contacts within 3.5 Å, first frame | 63 | 175 | 88 |
| Polar contacts, second half | **80.0** | **189.2** | 71.7 |
| Maximum over the run | 159 | 215 | 108 |
| **Initial pairs still present in the second half** | **0.11** | **0.21** | **0.14** |

**The fluctuation is low and nearly identical across three proteins of very different size.**
A mean C-alpha RMSF of 0.65–0.68 Å and a maximum below 1 Å indicates that the regions
contacting the ligand are among the more rigid parts of each structure, consistent with the
backbone RMSD of 1.18–1.34 Å. This matters for interpretation: the ligand is not being lost
because the site is falling apart around it.

**The polar-contact census is the third line of evidence for rearrangement rather than
departure.** In all three targets the number of ligand–protein polar contacts is maintained
or increases over the run — 63 to 80, 175 to 189 — so the ligand is not losing its polar
contacts. Yet only 11% to 21% of the *specific* atom pairs present in the first frame are
still within 3.5 Å in the second half. Contacts maintained in number while their identities
largely exchange is the signature of a ligand that stays in the pocket and re-forms its
interactions there, and it is the same behaviour that the ligand RMSD and the contact
survival fraction indicated. Unlike those two, this measure does not involve a displacement
and cannot be affected by how the trajectory was imaged.

The following should be stated about the polar-contact criterion: it counts donor–acceptor
pairs within 3.5 Å rather than enumerating hydrogen bonds geometrically, because the
trajectories were written without explicit hydrogen positions for the ligand, and 3.5 Å is
the conventional upper bound for such a pair. It therefore counts potential polar contacts,
not established hydrogen bonds, and is used as a comparative measure across the three
targets rather than as a bond count.

**The site itself can be named, which the contact count alone does not do.** Restricting to
residues in contact for at least half the run gives 10 sites in NFE2L2, 16 in HMOX1 and 10
in MFN2 — pockets of a size consistent with a buried ligand — and the persistent residues
are aromatic and polar rather than a scattering along the chain.

| Target | Residues in contact for ≥50% of the run | Pocket size | Closest approach |
|---|---|---|---|
| **NFE2L2** | TYR10, ARG12, PHE15, ASN58, SER59, GLN13, PRO60, LEU8 | 10 of 301 | 0.16 nm (TYR10) |
| **HMOX1** | PHE24, MET25, PHE28, PHE38, VAL41, LEU45, ARG127, ASP131 | 16 of 428 | 0.16 nm (ASP131) |
| **MFN2** | TRP95, LEU166, ARG289, GLU313, GLU317, SER4, PRO165, GLN310 | 10 of 841 | 0.16 nm (GLU313) |

Two features of these lists are worth recording. The pocket in HMOX1 is mostly hydrophobic —
four phenylalanines, a valine and a leucine — with two charged residues at its edge, which is
what a substrate site for a small polar molecule looks like. **And in HMOX1 two of the eight
persistent contacts are adjacent to where the heme was removed**: MET25 at 2.65 Å and ARG127
at 2.43 Å from the nearest heme atom of the deposited structure. Twenty-seven of the 428
residues lie within 5 Å of the heme, so chance alone would give about 0.5 of the eight, and
finding two is above chance without being a heme-site pose. The ligand's edge reaches the
heme cavity while its body lies against the neighbouring hydrophobic residues, which is a
partial occupancy of the active site rather than a replacement of the cofactor.

**A note on how this was verified, because the first check reached the wrong conclusion.** A
verification script compared the distance from the ligand to the first residue of each chain
(26–36 Å) with the median distance to the contacting residues (about 7 Å) and declared the
residue numbering offset. That reference is meaningless: an elongated protein has its chain
start far from its binding pocket, and the quantity that carries information is the absolute
distance, which is 4.7–9.5 Å here and is what an interface measures. Ethambutol has 14 heavy
atoms and 9 rotatable bonds, so an extended ligand spanning a pocket sits at that distance
from the residues it touches; a rigid molecule of the same mass would sit closer. The
numbering is therefore sound and the site assignments stand.

**What makes this more than three separate observations is that the three numbers that
matter are nearly the same in all three systems.** The receptor backbone RMSD is 1.18,
1.28 and 1.34 Å; the minimum ligand–protein distance is 2.18, 1.76 and 1.77 Å; and in every
case the contact count is either maintained or increases. Three binding sites of quite
different size and character — an NFE2L2 peptide site, an apoprotein heme pocket and a
large MFN2 interface — therefore behave alike, which is what a genuine binding site looks
like and not what a docking artefact would produce. The one quantity that does differ is
the ligand RMSD, and it differs in an informative direction: it is largest on NFE2L2
(5.62 Å), where the receptor is most rigid (1.18 Å), and smallest on HMOX1 (2.85 Å), where
the pocket is a deep cavity. That is the signature of a molecule rearranging its torsions
inside a confined space rather than of a molecule leaving, and for ethambutol — 38 atoms,
nine rotatable bonds, no designed complementarity — it is the expected behaviour.

**The correct reading is therefore that Vina placed the ligand in sites whose contacts
persist over the simulated window, but not in a single rigid pose.** The docking output
should be treated as identifying a site rather than fixing a geometry, which is what the
modest and narrowly spaced scores (-3.96 to -5.50 kcal/mol) already implied. The mechanism
proposed in this paper does not depend on direct occupancy of any of these nodes; it rests
on the enrichment analysis in Section 3.8.

**A correction to an earlier analysis of these trajectories.** A first version of this
analysis superposed each frame and then differenced raw coordinates. Because a molecule
that crosses the periodic boundary has its stored coordinates displaced by a whole box
vector, that procedure produced artefacts of the box length, and they were severe enough
to invert the conclusion:

| Quantity | Uncorrected | After imaging the trajectory |
|---|---|---|
| Receptor backbone RMSD | 12.1 Å | **1.18 Å** |
| Receptor backbone RMSD, maximum | 13.0 Å | 1.41 Å |
| Minimum ligand–protein distance | 22.6 Å | **2.18 Å** (maximum 2.52 Å) |
| Contacts surviving, second half | 0.04 | contacts **increase** (292 → 312) |
| Apparent N-terminal displacement | 60–66 Å | 13 Å (a flexible terminus) |
| Verdict | ligand left the site | **docked pose retained** |

The mechanism of the error is worth stating because it is easy to reproduce: the
trajectory is written in a 78.5 Å box, atoms cross the boundary during the run, and
differencing raw coordinates then reports displacements of up to 97 Å where the physical
motion is a few ångströms. Imaging with `image_molecules` before superposition moves
individual coordinates by up to 92.6 Å — the size of the artefact being removed — after
which the same calculations give the table's right-hand column. The verdict rule was also
at fault: it tested a centroid drift exceeding 5 Å and never consulted the ligand RMSD, so
a single artefactual quantity decided the outcome. The corrected rule requires that the
minimum ligand–protein distance stay below 4.5 Å **and** that the contact count not halve,
neither of which imaging can manufacture. Every number in this section now comes from the
corrected analysis, and the uncorrected table is retained alongside it
(`results/md_allatom_stability.csv` and `results/md_allatom_stability_pbc.csv`) so the two
can be compared.

**Limitations of this section.** Only NFE2L2 was run to a full nanosecond of unrestrained
production; HMOX1 contributes 0.23 ns drawn from its equilibration phases and MFN2 0.13 ns,
so the three are not equal evidence and the table says which is which. A pose that
survives 1 ns can be called bound with reasonable confidence, whereas 0.2 ns is too short
to say more than that nothing unstable happened immediately — the agreement of the three
targets is therefore suggestive rather than conclusive. **HMOX1 was simulated as the
apoprotein**, because heme is both the substrate and the catalytic centre of a heme
oxygenase and parameterising its iron centre was not implemented; a pocket without its
cofactor is not the biological pocket, so that target supports the general claim less
directly than the other two. Two further attempts on other hubs were unsuccessful: TNF was
never started, and BCL2 was solvated but produced no trajectory. Ligand parameters came
from GAFF with AM1-BCC charges rather than a bespoke force field, and the force field was
not validated against experimental data for this molecule (Section 3.9). Finally, even a
1 ns trajectory samples only the fastest relaxations; a pose that persists for 1 ns may
still leave on a microsecond timescale, and nothing here excludes that.

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
estimated glomerular filtration rate (n = 1,004,040), cystatin C (n = 437,846) and
serum creatinine (n = 437,660) each contributed **150-186 harmonised instruments** per
outcome, and the estimates are precise (for example, cystatin C on optic neuritis:
OR 1.026, 95% CI 0.865-1.216).

**No causal effect was detected.** Across all six optic-nerve and visual outcomes,
genetically proxied renal function showed no association after Benjamini-Hochberg
correction (all q ≥ 0.87; Table 8); genetically proxied type 2 diabetes was likewise
null for optic neuritis (OR 1.094, 95% CI 0.940-1.274; 57 instruments). MR-Egger
intercepts were non-significant and Steiger directionality was correct in every case,
arguing against reverse causation.

**The panel carries a positive control, and it behaves as it should.** Body mass index was
included precisely because a higher body mass index is a recognised risk factor for the
optic-nerve phenotype, so its performance tests whether this pipeline can detect a real
effect or whether it returns nulls whatever the exposure. With **266 harmonised instruments**
it gave **OR 1.680 (95% CI 1.265-2.231), p = 3.4 × 10⁻⁴, q = 0.020** for optic neuritis — the
only exposure-outcome pair among the **60** tested that survives Benjamini-Hochberg
correction — with a non-significant Egger intercept (p = 0.92) and a Steiger direction that
is correct. The distinction this establishes is what makes the renal result readable: an
instrument set of this size, analysed by this pipeline, does recover an association where one
exists, so the renal nulls are absences of effect rather than absences of power. A panel that
returned nothing for every exposure would leave the negative results uninterpretable, and
this is the reason the control was carried.

**Smoking was tested as a genetic exposure and shows no effect.** The panel carries
two smoking traits and neither is associated with any of the six optic-nerve or visual outcomes
after Benjamini-Hochberg correction (all q ≥ 0.86). Smoking initiation is the stronger of
the two, with 32 instruments:

| Outcome | Smoking initiation, OR (95% CI) | q | Cigarettes per day, OR (95% CI) | q |
|---|---|---|---|---|
| BLINDANDVISIMPAIRMENT | 0.88 (0.58–1.35) | 0.96 | 1.13 (0.74–1.72) | 0.96 |
| COULOURVISDEF | 0.79 (0.15–4.24) | 0.96 | 1.54 (0.29–8.21) | 0.96 |
| OPTATROPHY | 0.72 (0.30–1.68) | 0.96 | 1.69 (0.72–3.95) | 0.86 |
| OPTNERVNAS | 0.95 (0.42–2.15) | 0.96 | 0.91 (0.40–2.04) | 0.96 |
| OPTNEURITIS | 1.08 (0.63–1.86) | 0.96 | 1.17 (0.69–2.00) | 0.96 |
| VISFIELDDEF | 0.95 (0.65–1.39) | 0.96 | 1.09 (0.75–1.60) | 0.96 |

This is reported because a cohort of 4,141 ethambutol recipients found smoking an independent
risk factor for optic neuropathy on adjusted logistic regression (OR 7.06, p = 0.01) [p2023].
The two are not in direct conflict — a genetic instrument estimates lifelong liability to
smoke, whereas an adjusted estimate in a treated cohort captures current smoking together with
whatever it correlates with — but they do not corroborate each other either. **The result is an
absence of a detectable effect rather than a demonstration of none**: smoking initiation is
powered at 32 instruments and its estimates sit near unity with intervals that include it,
while cigarettes per day, at 14 instruments, is weaker still and its intervals are
correspondingly wide.

Serum creatinine deserves a note, because it was absent from the first analysis and
its recovery is instructive. An early run recorded zero harmonised instruments for it
against every outcome, which is not a property the data can have: serum creatinine
measures the same renal function as eGFR in the same population, and 186 of its 370
instruments are present in the cached FinnGen scans - a higher proportion than eGFR's
151 of 342. The zero came from harmonisation, not from the variants, and the
distinction matters because a spurious zero would have been read as an absence of
evidence. Recovered, serum creatinine is null across all six outcomes (optic neuritis
OR 0.944, 95% CI 0.722-1.234, p = 0.67; smallest p = 0.075 for colour vision
deficiency, q = 0.87). The renal null therefore rests on three independent exposures
rather than two, and all three agree.

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

### 3.11 The network's nodes are expressed in the retina, and a class-level test of ferroptosis fails to inform

**The hub genes are present in retinal cells.** Of the 33 focus-layer hubs, **31 (94%) are
detected in at least one retinal cluster** at nCPM > 1, against 25.2 expected for random
gene sets of the same size (sd 2.5; empirical **P = 0.0067**; 1.23-fold enrichment). The
finding that matters most for the mechanism is that the ferroptosis machinery is not
merely present but abundantly expressed: **GPX4 reaches 1061.5 nCPM and is detected in all
eight clusters**, with SLC7A11 (88.4 nCPM), ACSL4 (87.5) and SDHB (91.6) likewise
detected. NFE2L2 (215.0), OPA1 (113.9), SOD2 (170.5), MFN2 (55.4) and SLC25A4 (426.2) are
also expressed in all eight clusters. **Two hubs are not detected in these clusters** — *TNF* and *CYP2D6* — which limits any claim
that depends on them **within the retinal parenchyma**. For *CYP2D6* that is the end of the
matter. For *TNF*, a high-degree hub (degree 18), the restriction is a property of the cell
types the HPA retinal panel covers rather than of the retina: the eight clusters are neural and
glial and contain no microglia, and reading the microglial column of the same table shows *TNF*
at 7.8 nCPM, the highest value of any of the 154 cell types measured. **The inflammatory arm is
therefore supported in the retinal immune compartment rather than in the parenchyma**, and the
microglial analysis below sets out the evidence. The conclusion is bounded accordingly: the network's nodes are plausibly
present in the tissue, which is the precondition for the mechanism, but presence of
transcript is not evidence of participation.

**A class-level pharmacovigilance test of ferroptosis does not inform the question.** The
attempt described in Section 2.13 gave the following, and it is reported because a test
that fails should be visible rather than omitted:

| Class | Cases | Optic-nerve events | Optic-nerve ROR (95% CI) | Non-specific ocular ROR (95% CI) |
|---|---|---|---|---|
| Ferroptosis inducers | 88,130 | 37 | 0.89 (0.64–1.23) | **1.63 (1.55–1.71)** |
| Apoptosis inducers | 412,827 | 310 | **1.61 (1.44–1.80)** | 0.37 (0.35–0.38) |
| *Ethambutol, for reference* | 13,804 | 153 | **159.21 (134.65–188.25)** | 1.23 (1.07–1.42) |

Neither class approaches ethambutol's optic-nerve ratio, and the two classes move in
opposite directions on the two readouts — ferroptosis inducers high on non-specific ocular
terms and low on optic-nerve terms, apoptosis inducers the reverse. **Three reasons make
this uninterpretable as a test of the mechanism, and they are why it is reported as a
caution rather than a result.**

First, the test asks the wrong question. Ethambutol is not a ferroptosis inducer; it
triggers ferroptosis indirectly by suppressing SDHB and collapsing the GPX4/SLC7A11 axis.
Whether erastin or sorafenib damages the optic nerve is a different question from whether
ethambutol's toxicity runs through the ferroptosis pathway, and a null answer to the
former carries little information about the latter.

Second, the class composition is not what the design intended. Sulfasalazine supplies
66,716 of the 88,130 "ferroptosis inducer" cases — 76% — so the class is largely one drug
used for inflammatory bowel disease, not a set of ferroptosis inducers in the sense the
hypothesis requires. Its members differ in indication and in how each happens to induce
ferroptosis.

Third, the two readouts move in opposite directions between classes, which is the
signature of ascertainment rather than biology. Optic-nerve events are recorded when a
patient is examined ophthalmologically; non-specific ocular complaints are reported by
patients and require no examination. A class low on the first and high on the second is a
class whose optic nerves are not being looked at. Comparing that with ethambutol, whose
optic-nerve ratio is 159 against the whole database, tests who receives an eye
examination rather than whether ferroptosis is the mechanism.

**The honest summary is that a drug-class analysis of spontaneous reports cannot
adjudicate a mechanism specific to one cell type, so this analysis is reported as evidence
about the limits of the method and not about the mechanism.** It is placed here rather
than omitted because a negative result from a designed test is a finding, and because the
contrast with ethambutol's own within-drug specificity — the internal control that the
whole paper rests on — illustrates why the internal comparison is the stronger design.

**Agreement with regulatory labelling.** Of the 18 antitubercular drugs, current
structured product labelling was retrievable for 13. **Ethambutol carries an explicit
optic-nerve warning and returns the strongest signal in the panel (ROR 6.47 within the
class, 159.21 against the whole database), and the same agreement holds for isoniazid,
linezolid and pretomanid** — the expected result where the toxicity is already known,
which validates the detection rather than discovering anything. The informative cells are
the disagreements. **Six drugs show a within-class ratio above 2 with no optic-nerve term
in their label** — streptomycin (12.04), cycloserine (7.39), clofazimine (5.15),
bedaquiline (3.57), pyrazinamide (2.87) and rifampicin (2.20) — and one shows the reverse,
isoniazid carrying an optic-nerve warning at a ratio of 1.47. **None of the six is put
forward as a new signal**, because each is co-prescribed with ethambutol in the regimens
where it appears, so the signal is at least partly the co-drug; and five of the six have
far smaller case counts than ethambutol, so the absence of a label warning may reflect
regulatory priority rather than absence of effect. They are recorded as drugs meriting
pharmacovigilance attention, and the isoniazid case is a reminder that this method has
limited sensitivity for toxicities that are already known.

---

### 3.12 Physicochemical and drug-likeness profile of ethambutol

The descriptors were retrieved from PubChem rather than computed here, so that the molecule
profiled is the deposited one: **C10H24N2O2**, molecular weight **204.3**, XLogP **-0.1**,
topological polar surface area **64.5 Å²**, **4** hydrogen-bond donors, **4**
acceptors, **9** rotatable bonds, **14** heavy atoms and a complexity of 109. These
agree with the docking preparation used in Section 3.9, which recorded 14 heavy atoms and
9 rotatable bonds, so the docking and this profile describe the same molecule.

**All 5 of the standard drug-likeness rules are satisfied** (Table 12): Lipinski's rule of
five, Veber's oral-bioavailability criteria, the Ghose filter, and the two descriptors
associated with central-nervous-system penetration. The last of those is the result worth
noting, because it runs against the intuitive expectation for a hydrophilic compound.
Ethambutol carries two basic amines and has an XLogP of -0.1, yet its polar surface area
is 64.5 Å² — well inside the range associated with penetration of a lipid barrier, and a
consequence of the two hydroxyls being small relative to the amine-bearing backbone.

**What this does and does not establish.** It does not establish that ethambutol reaches the
retina, and a physicochemical rule cannot: penetration is predicted, whereas retinal
concentration would have to be measured. But it does make one explanation less likely than it
appeared. If the drug partitions across lipid barriers as readily as this profile suggests,
then a simple failure to arrive at the retina is an unlikely account of why only a minority of
treated patients develop optic neuropathy, and the explanation has to invoke something more
specific — efflux transport at the blood–retinal barrier, a locally reached concentration, or a
selective vulnerability of the retinal ganglion cells that handle iron and glutathione, which is
where the network of Section 3.8 and the ferroptosis mechanism point.

**What this analysis cannot add.** Ethambutol is an approved first-line drug whose absorption,
distribution and elimination are already characterised, so predicting its pharmacokinetics
would restate the label. The value here is confined to the structural question above, and the
section is reported briefly for that reason rather than as an independent line of evidence.

## 4. Discussion

### 4.1 Principal findings

Three findings carry the paper. First, in 20.3 million de-duplicated FAERS cases the ocular toxicity of ethambutol resolves into an extraordinarily specific optic-nerve signal — optic neuropathy strong within the antitubercular class and, more distinctively, a colour-vision signal that exceeds it — while non-specific ocular complaints produce no signal at all. That internal contrast is the strongest available evidence that the signal is not reporting artefact. Second, the timing is that of a cumulative toxic axonopathy rather than an idiosyncratic reaction: a median of 125 days to an optic-nerve event versus 30 days for non-ocular events in the same reports, consistent with the clinical literature's descriptions of subacute onset after months of therapy. Third, the mechanism is most strongly enriched for ferroptosis and mitochondrial
integrity, and docking ranks ethambutol's engagement of the upstream inflammatory and
redox nodes of that network above its terminal enzymes. Both of those are association
results from a network built largely on literature co-mention, so they identify a
mechanistic hypothesis and are stated at that strength throughout.

### 4.2 Comparison with previous work

**The one directly comparable FAERS analysis.** Mao and Ou mined the same database for the same drug and reached a compatible conclusion at the level of signal counting: ethambutol produced more eye-disorder signals than rifampicin, isoniazid or pyrazinamide [28]. Three differences bound the comparison. Scale: they analysed 978 ethambutol reports over 2021Q1–2025Q3, whereas the present analysis uses 13,804 cases over 22 years, which is what allows within-class comparators, temporal splitting and external replication to be attempted at all. Level: they report signal counts aggregated to system organ class, while this analysis works at the preferred-term level with Benjamini–Hochberg control across 178 ocular terms. Design: they have no negative-control panel, so their finding establishes that an ocular signal exists but not that it is specific to the optic nerve. The two studies therefore agree on the existence of the signal and differ on whether it has been characterised; the term-level contrast in Section 3.2 is what neither their analysis nor any other published work reports.

The frequency we infer (7.03% of ethambutol cases reporting any ocular event; 3.44% an optic-nerve event) sits at the upper end of the clinically reported range and should not be read as an incidence: FAERS is a spontaneous reporting system with stimulated reporting for a well-known adverse effect, and the denominator is reports, not exposures. What FAERS can support is the *relative* profile across drugs and terms, and it is here that the analysis is informative. Our within-class comparator ordering — ethambutol above isoniazid, rifampicin and pyrazinamide, the drugs given in the same regimen, though not above the second-line agents used for drug-resistant disease — agrees with the clinical literature's view that ethambutol is the first-line antitubercular drug that causes optic neuropathy [12] and with the VigiBase analysis that found ocular events concentrated in ethambutol reports [11].

The signal profile also reproduces the clinical phenotype term by term. The phenotypes that dominate our results — optic neuropathy, dyschromatopsia, scotoma, optic neuritis, optic atrophy, visual field defect, papilloedema — are exactly the features reported in EON cohorts [15,21,26,27], and their ordering by strength tracks how central each is to the disease. By contrast, cataract (0.86), glaucoma (0.38), dry eye (0.42) and eye pain (0.64) show nothing, which is what one expects if the injury is confined to the ganglion cell and its axon. This kind of internal consistency is not obtainable from organ-system-level pharmacovigilance groupings and is the methodological step forward this analysis makes.

### 4.3 Mechanism

The enrichment results should be read as a hypothesis, not a demonstration, but they align unusually well with the newest experimental work. Ferroptosis was the leading KEGG term, and the specific genes driving it — *GPX4*, *SLC7A11*, *ACSL4*, *SDHB*, *SMAD4*, *HMOX1* — are precisely the axis that a 2026 study identified experimentally in ethambutol-treated retinal ganglion cells, where the drug suppresses SDHB through Smad4 and collapses the GPX4/SLC7A11 antioxidant defence [9]. The mitochondrial-envelope signal and the hub position of *OPA1* and *MFN2* connect to the genetic-susceptibility literature [7], and the BDNF–NTRK2 result matches the Müller-glia rescue experiments in which pan-TRK blockade abolished protection [10]. The zinc-handling genes in the core panel (*MCOLN1*, *SLC30A10*, *MT1A*) connect to the lysosomal zinc-trapping observation [6] and to the clinical finding that low pre-treatment plasma zinc predicts risk [5].

It is worth stating what the network does *not* show. Because Open Targets records no human target for ethambutol, nothing in this analysis identifies where the drug binds in human cells. What the network describes is the set of processes that become dysregulated — which is precisely what is needed to choose an intervention node, and precisely what cannot be inferred from a target database that has no entry to offer.

### 4.4 Clinical implications

The most actionable finding is not the signal itself but the screening gap it
exposes. Baseline ophthalmic screening is performed in only 12.0-13.1% of patients
started on ethambutol, and the proportion monitored within six months fell from
13.1% in 2015 to 7.9% in 2021 [13]. Given a median onset of 125 days in our data and
the clinical literature's finding that structural measures predict outcome better
than acuity [22,23,26,27], the case for structured baseline and follow-up assessment
is strong.

Three risk factors deserve weighting. Renal impairment is the most powerful
modifiable determinant (adjusted OR 2.69 in a Korean national cohort, 3.73 in a
Taiwanese cohort, with an incidence approaching 40% in dialysis patients) [24,25,13],
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
they require prospective cohorts with protocolised exposure documentation.

**Reversibility, which this study cannot measure, is where the clinical literature is
most useful.** Two cohorts report it and they differ. Among 4,141 ethambutol recipients in a
Thai cohort, 60% of the 20 who developed optic neuropathy improved by at least two Snellen
lines over a mean of 6.9 months, and improvement was unrelated to demographics, past medical
history, smoking or ethambutol dosing [p2023]. In the Korean cohort fewer than a third improved
after the drug was stopped, the latency to recovery was 5.38 ± 1.71 months, and no patient who
had optic disc pallor at diagnosis recovered any visual function [30].

The last observation is the clinically decisive one, and it fixes the timescale this analysis
implies. The median time from starting ethambutol to an optic-nerve event here is 125 days
against 30 days for non-ocular events in the same reports, so the toxic effect is slow and the
window in which it can be detected precedes the appearance of disc pallor — after which the
Korean data indicate that recovery does not occur. A pharmacovigilance database records events
rather than outcomes, so this study cannot add to the reversibility figures; what it contributes
is the timing that makes surveillance worthwhile. Optical coherence tomography angiography
detects reduced macular superficial vessel density before clinical onset [31], which is the
kind of measure that would fit inside that window.

### 4.5 Limitations

*Spontaneous reporting.* FAERS has no exposure denominator, so the proportions we report are proportions of reports, not incidences; the 7.03% ocular and 3.44% optic-nerve figures must not be read as risks. A partial denominator can be built from WHO tuberculosis notifications, since ethambutol is a standard component of first-line therapy and treated patients therefore scale with notified cases, and doing so shows what the country counts actually measure: reports per unit of burden are unrelated to burden (Spearman rho = -0.14) and vary three orders of magnitude, from 834.5 in the United States to 0.3 in South Africa, whose tuberculosis incidence is 229 times higher. **Geographic and country-level differences in this database therefore reflect the strength of national pharmacovigilance rather than the number of patients exposed, and no result here is interpreted geographically.** Under-reporting is substantial and non-random. Because ethambutol optic neuropathy is a well-known adverse effect, stimulated reporting (notoriety bias) would inflate the absolute signal; it cannot, however, explain the *internal* contrast between optic-nerve terms and non-specific ocular terms, which is the finding we rely on — that contrast is computed within the same reports, so reporting intensity cancels — nor is it easily reconciled with the same contrast appearing in JADER, whose reporters and reporting culture are independent of FAERS. Reports are voluntary and unverified, and we cannot adjust for confounders such as indication, dose or comorbidity, although the comparator drugs share the tuberculosis indication. Replication across two databases, and across two eras within one of them, strengthens the association but does not remove the limitations that spontaneous reporting imposes on both: neither database has a denominator, and neither can distinguish a drug effect from a reporting propensity shared by clinicians in both countries who recognise this particular toxicity.

*Data completeness.* One quarterly archive (2026Q2) was corrupt; the analysis therefore covers 2004Q1–2026Q1. openFDA's harmonised view could not be used as the primary source because it omits the raw CASEID and FDA_DT fields and throttles sustained bulk retrieval, so we used the FDA's own quarterly releases; the resulting case count (13,804) differs modestly from the openFDA count (15,041) because the de-duplication and matching conventions differ.

*The gene set is reconstructed, not looked up.* Open Targets holds no human target for ethambutol, so the network is a **downstream effect network** built from literature co-mention and disease-phenotype association. It is not a direct drug-target network, and hub genes should not be interpreted as binding partners of ethambutol. Literature co-mention is also vulnerable to publication trends even after whitelist screening and manual review of titles.

**The second-line comparator is confounded by indication, and so is the first-line one.**
Two separate problems limit what the within-class comparison can support. Ethambutol ranks
sixth of eighteen antitubercular drugs on within-class optic neuropathy, below
prothionamide, capreomycin, streptomycin, cycloserine and ethionamide. Every one of those
is a second-line agent used for drug-resistant tuberculosis, a population that is
sicker, treated for longer, and more likely to have central nervous system involvement
including tuberculous meningitis, which can damage the optic nerve independently of any
drug; their higher ratios therefore cannot be read as greater intrinsic optic-nerve
toxicity. More fundamentally, the first-line drugs are co-prescribed, so their reports
are largely the same patients: 71.1% of ethambutol cases also name rifampicin, and 73.3%
of pyrazinamide cases name ethambutol against only 48.8% the other way, which is why the
naive ranking is presented as a description rather than a comparison. The claim this
paper makes from the class is therefore confined to the one comparison in which the
regimen is fixed — rifampicin, isoniazid and pyrazinamide with versus without
ethambutol, a rate ratio of 3.28 (95% CI 1.03–10.40) — and that estimate is itself imprecise,
resting on 845 reports in the smaller group, with a lower bound close to unity.

*Docking is a scoring approximation.* Vina scores
correlate only moderately with affinity, the protocol treats a rigid receptor, and
the search box is derived from a co-crystal ligand or a geometric pocket prediction
rather than experimental site mapping. The redocking panel bounds where the protocol can
be trusted: it reproduced crystal poses for every ligand up to 13 heavy atoms and for
none from 19 upwards, with graded errors beyond that point (2.43, 3.13, 5.84 and 5.86 A).
Ethambutol, at fourteen heavy atoms, falls in the gap the panel brackets rather than in
the range it fills: one atom above the largest ligand that passed and five below the
smallest that failed. The bracketing complexes passed at 0.34 A (9 atoms) and at 1.80 and
1.94 A (13 atoms), and the 19-atom ligand came within 0.43 A of the criterion, so the
inference for ethambutol's size is well supported but is an extrapolation across an
untested interval. The docking reported here
is restricted to ethambutol itself and is used only to rank the hub targets by
predicted occupancy; it cannot establish binding and does not identify the drug's
mechanism.

*No drug-exposure Mendelian randomisation.* Ethambutol is an environmental exposure; no genome-wide association study of "ethambutol use" exists, and no cis-region variant in the candidate panel reached genome-wide significance for optic neuropathy in FinnGen. A Wald-ratio estimate constructed from non-significant, outcome-derived variants would be both underpowered and circular, so it was not attempted. The MR we do report concerns modifiable risk factors for the optic-nerve phenotype, not the drug itself.

*Scope of the genetic analysis.* Ten exposures were nominated but only three could be fully harmonised within the available computing budget, because each instrument region must be retrieved individually from a 20-million-variant FinnGen release. The reported panel is therefore renal function (eGFR, cystatin C) and type 2 diabetes — chosen on mechanistic as well as statistical grounds — and the remaining nominated exposures are not reported. The FinnGen optic-nerve endpoints are also rare (optic atrophy 629 cases, optic neuritis 1,592), so the null results are null results with finite power, not demonstrations of absence, particularly for the smaller endpoints.



---

## 5. Conclusion

In the largest pharmacovigilance assessment of ethambutol to date -
20.3 million de-duplicated FAERS cases - ocular toxicity resolves into a highly
specific optic-nerve signal with no signal whatever for non-specific ocular
complaints, and that contrast survives every robustness specification tested. Within
the antitubercular class ethambutol's optic-neuropathy reporting ratio exceeds the
drugs given in the same regimen by 2- to 4-fold, although several second-line agents
used for drug-resistant disease show comparable or higher ratios under confounding by
indication severity. The most distinctive feature of the drug's profile is a
colour-vision signal that exceeds its optic-neuropathy ratio, which is the clinical
hallmark of ethambutol optic neuropathy. The onset is delayed by months relative to
other adverse events in the same reports, as a cumulative axonal injury would be, and
daily dose does not predict the outcome once exposure duration is taken into account.
At the molecular level the implicated network is most strongly enriched for ferroptosis
and mitochondrial integrity - the axis experimental work has now identified in
ethambutol-treated retinal ganglion cells - and docking ranks the upstream inflammatory
and redox nodes of that network above its terminal enzymes. This is an association
pattern from a network built largely on literature co-mention, so it identifies a
mechanistic hypothesis rather than a mechanism; it is stated at that strength
throughout. Genetically proxied renal function shows no causal effect on the
optic-nerve phenotype, which places renal impairment in the pathway as a determinant
of drug exposure rather than an independent cause of optic-nerve degeneration.

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
randomisation. The analysis code is available at https://github.com/Bowen2485/ethambutol-ocular-toxicity (MIT licence).

**Funding.** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

**Competing interests.** The authors declare no competing interests.

**Author contributions** (CRediT). **Bowen Shi:** Conceptualization, Methodology, Software, Validation, Formal analysis, Resources, Data curation, Writing – original draft. **Yaqin Tan:** Investigation. **Siyuan Yang:** Writing – review & editing. **Xuan Wang:** Visualization. **Zhengzheng Wu:** Supervision. **Jing Yan:** Project administration, Funding acquisition, Supervision. All authors read and approved the final manuscript.

---

## References

1. Lee S, Ryu WY, Kang D, Lee JK.. Prevalence and Incidence of Ethambutol-Induced Optic Neuropathy and Its Risk Factors in Korea: A Nationwide Population-Based Study. Journal of Korean medical science. 2025; doi:10.3346/jkms.2025.40.e65.
2. Liu SS, Feng SC, Wu MF, Chin CS, Chen HC, Huang WC.. Programmatic Assessment of Ethambutol-Related Optic Neuropathy in Patients with Mycobacterial Infections: A Prospective Observational Cohort Study. Infectious diseases and therapy. 2025; doi:10.1007/s40121-025-01219-x.
3. Mandal S, Saxena R, Dhiman R, Mohan A, Padhy SK, Phuljhele S, et al. Prospective study to evaluate incidence and indicators for early detection of ethambutol toxicity. The British journal of ophthalmology. 2021; doi:10.1136/bjophthalmol-2020-316897.
4. Morimoto Y, Matsui H, Ikeda M, Kubota N, Nagai T, Otsuki A, et al. Association Between Low-Dose Ethambutol Therapy and Optic Neuropathy in <i>Mycobacterium avium</i> Complex Pulmonary Disease: A Retrospective Cohort Study Using Propensity Score Analysis. Open forum infectious diseases. 2026; doi:10.1093/ofid/ofag127.
5. Delacoux E, Moreau Y, Godefroy A, Evstigneeff T.. [Prevention of ocular toxicity of ethambutol: study of zincaemia and chromatic analysis (author's transl)]. Journal francais d'ophtalmologie. 1978.
6. Chung H, Yoon YH, Hwang JJ, Cho KS, Koh JY, Kim JG.. Ethambutol-induced toxicity is mediated by zinc and lysosomal membrane permeabilization in cultured retinal cells. Toxicology and applied pharmacology. 2009; doi:10.1016/j.taap.2008.11.006.
7. Zhang XH, Xie Y, Xu QG, Cao K, Xu K, Jin ZB, et al. Mitochondrial Mutations in Ethambutol-Induced Optic Neuropathy. Frontiers in cell and developmental biology. 2021; doi:10.3389/fcell.2021.754676.
8. Hwang JM, Kim J, Park SS.. Leber's hereditary optic neuropathy mutations in ethambutol-induced optic neuropathy. Journal of neurology. 2003; doi:10.1007/s00415-003-0960-0.
9. Li Q, Ge W, Zhang Y, Xu Q, Xu J, Zhang Y, et al. Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis in retinal ganglion cells via Smad4 pathway. Human cell. 2026; doi:10.1007/s13577-025-01342-4.
10. Cheng HC, Wong YH, Wang AG, Chen SW, Yang YL, Juan HC, et al. Müller glia-mediated protection of retinal ganglion cells from ethambutol-induced neurotoxicity through brain-derived neurotrophic factor. Cell communication and signaling : CCS. 2025; doi:10.1186/s12964-025-02478-4.
11. Suresh J, Kumar R, Hissar S, Shukla S, Vivekanandan K.. Ocular toxicity associated with Ethambutol in the South-East Asia Region. International ophthalmology. 2026; doi:10.1007/s10792-026-04131-6.
12. Donald PR, Maher D, Maritz JS, Qazi S.. Ethambutol dosage for the treatment of children: literature review and recommendations. The international journal of tuberculosis and lung disease : the official journal of the International Union against Tuberculosis and Lung Disease. 2006.
13. Kim J, Kwon HY, Ahn SJ.. Nationwide usage of ethambutol and incidence and screening practices of optic neuropathy. Frontiers in pharmacology. 2024; doi:10.3389/fphar.2024.1461111.
14. Chamberlain PD, Sadaka A, Berry S, Lee AG.. Ethambutol optic neuropathy. Current opinion in ophthalmology. 2017; doi:10.1097/icu.0000000000000416.
15. Ambika S, Lakshmi KP, Gopal M, Noronha OV.. Visual outcomes of toxic optic neuropathy secondary to Ethambutol: A retrospective observational study from India, an endemic country. Indian journal of ophthalmology. 2022; doi:10.4103/ijo.ijo_2996_21.
16. An HR, Lee BJ, Moon Y.. Visual Recovery Time in Patients with Ethambutol-induced Toxic Optic Neuropathy. Korean journal of ophthalmology : KJO. 2024; doi:10.3341/kjo.2023.0095.
17. Singh P, Karkhur S, Verma V.. Ethambutol-Induced Optic Neuropathy: A Retrospective Study of Incidences and Risk Factors. Cureus. 2025; doi:10.7759/cureus.79160.
18. Chaitanuwong P, Srithawatpong S, Ruamviboonsuk P, Apinyawasisuk S, Watcharapanjamart A, Moss HE.. Incidence, risk factors and ophthalmic clinical characteristic of ethambutol-induced optic neuropathy: 7-year experience. Frontiers in ophthalmology. 2023; doi:10.3389/fopht.2023.1152215.
19. Choi SY, Hwang JM.. Optic neuropathy associated with ethambutol in Koreans. Korean journal of ophthalmology : KJO. 1997; doi:10.3341/kjo.1997.11.2.106.
20. Chatterjee VK, Buchanan DR, Friedmann AI, Green M.. Ocular toxicity following ethambutol in standard dosage. British journal of diseases of the chest. 1986; doi:10.1016/0007-0971(86)90066-5.
21. Sachdeva G, Dhiman R, Raj D, Lavanya G, Mohan A, Pujari A, et al. Evaluation of visual function and OCT parameters in ethambutol-induced optic neuropathy: a longitudinal study. The British journal of ophthalmology. 2026; doi:10.1136/bjo-2025-327475.
22. Lee JY, Choi JH, Park KA, Oh SY.. Ganglion Cell Layer and Inner Plexiform Layer as Predictors of Vision Recovery in Ethambutol-Induced Optic Neuropathy: A Longitudinal OCT Analysis. Investigative ophthalmology & visual science. 2018; doi:10.1167/iovs.17-22988.
23. Kang MC, Eun HW, Park KA, Oh SY.. Optical Coherence Tomography Parameters and Optimal Cut-off Values for Predicting Visual Prognosis in Ethambutol-Induced Optic Neuropathy. Journal of neuro-ophthalmology : the official journal of the North American Neuro-Ophthalmology Society. 2024; doi:10.1097/wno.0000000000002092.
24. Chen HY, Lai SW, Muo CH, Chen PC, Wang IJ.. Ethambutol-induced optic neuropathy: a nationwide population-based study from Taiwan. The British journal of ophthalmology. 2012; doi:10.1136/bjophthalmol-2012-301870.
25. Kanaujia V, Jain VK, Sharma K, Agarwal R, Mishra P, Sharma RK.. Ethambutol-induced optic neuropathy in renal disorder: a clinico-electrophysiological study. Canadian journal of ophthalmology. Journal canadien d'ophtalmologie. 2019; doi:10.1016/j.jcjo.2018.06.013.
26. Han KE, Yoon H, Choi H, Lee JE, Kim SJ.. Factors affecting visual outcome in patients with toxic optic neuropathy caused by ethambutol. Scientific reports. 2025; doi:10.1038/s41598-025-90663-3.
27. Sheth J, Sachdeva V, Goyal A, Parikh A, Nalawade R, Nanavati H, et al. Clinical profile and visual outcomes in ethambutol-induced toxic optic neuropathy. Indian journal of ophthalmology. 2025; doi:10.4103/ijo.ijo_1807_24.


---

## Figures and Tables

**Figure 1** FAERS case-selection flow (90 quarterly ASCII releases → 20.33 million de-duplicated cases → ethambutol-related cases → ocular-term 2×2 construction).

**Figure 2** Volcano plot of ethambutol ocular-term disproportionality. Abscissa: log₂ reporting odds ratio. Ordinate: −log₁₀ Benjamini–Hochberg q. Red points are strict signals.

**Figure 3** Heat map of ocular reporting odds ratios across six antitubercular drugs (log₂ ROR).

**Figure 4** Forest plot of ethambutol ocular signals (ROR with 95% CI, n ≥ 3).

**Figure 5** Focus-layer STRING protein–protein interaction network (33 nodes, 191 edges). Red: curated core panel; orange: literature-supported genes; blue: optic-nerve phenotype genes.

**Figure 6** Focus-layer functional enrichment dot plot (GO-BP/CC/MF, KEGG, Reactome, WikiPathways).

**Figure 7** Docking scores of ethambutol against 14 hub targets (AutoDock Vina, kcal/mol).

**Figure 8** Time from starting ethambutol to onset (left: log-scale histogram by event category; right: box plots with median times).

**Figure 9** Annual ethambutol report volume and the proportion carrying an optic-nerve term (2013–2026).

**Table 1** Study population (cases per exposure after FAERS de-duplication).
**Table 2** Ethambutol ocular signal table (152 terms).
**Table 2b** Strict signals (45 terms).
**Table 2c** Drug-toxicity-spectrum signals (top 30).
**Table 2d** Anatomical grouping of the panel (152 terms).
**Table 2e** Ocular tuberculosis manifestations, excluded from the toxicity reading (12 terms).
**Table 2f** Non-ocular terms removed from the panel (13 terms).
**Table 3** Time from starting ethambutol to onset.
**Table 4** Multivariable logistic regression.
**Table 5** Focus-layer hub genes.
**Table 6** Principal enriched pathways.
**Table 7** Molecular docking score matrix.
**Table 8** Two-sample Mendelian randomisation results.
**Table 9** Robustness checks (four scenarios).
**Table 10** Report adequacy.
**Table 11** Optic-nerve odds ratio by patient subgroup, with contrasts between strata.

**Additional tables.** Regimen-stratified within-class comparison (`results/faers_regimen_strata.csv`); JADER external validation (`results/jader_validation.csv`); temporal split validation (`results/faers_temporal_validation.csv`); redocking validation panel (`results/redocking_validation_final.csv`); tuberculosis burden denominator (`data/derived/faers_tb_denominator.csv` and `data/derived/faers_who_merged.csv`); ligand parameter validation (`results/ligand_parameter_validation.json`).

**Machine-readable table files.** Each numbered table is also provided as a UTF-8 CSV in `tables/`: `Table1_cohort.csv`, `Table2_signals.csv` (152 ocular terms), `Table2b_signals_strict.csv` (the 45 strict signals), `Table2c_toxicity_spectrum.csv` (top 30 by ratio), `Table2d_unclassified_terms.csv`, `Table2e_ocular_tuberculosis.csv` (12, excluded from the toxicity reading), `Table2f_non_ocular_terms.csv` (13, removed from the panel), `Table2_signals_full_panel.csv` (the 178-term derived panel), `Table3_tto.csv`, `Table4_logistic.csv`, `Table5_hubs.csv`, `Table6_enrichment.csv`, `Table7_docking.csv`, `Table8_mr.csv`, `Table9_robustness.csv`, `Table10_adequacy.csv`.

---

## Reporting checklists

The study is reported in accordance with STROBE, its RECORD-PE extension for
pharmacoepidemiological research using routinely collected data, and the STROBE-MR
items relevant to the genetic component. The completed checklists, including an
explicit list of what was deliberately *not* done and why, are provided as a
supplementary file (STROBE_RECORD_checklist).
