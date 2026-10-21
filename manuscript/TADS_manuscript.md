# Optic-nerve-predominant adverse-event reporting with ethambutol: a multi-database pharmacovigilance study with exploratory transcriptomic analysis

**Running title:** Optic-nerve-predominant reporting with ethambutol

**Authors:** Bowen Shi¹, Jing Yan¹*, Zhengzheng Wu¹, Siyuan Yang¹, Yaqin Tan¹, Xuan Wang¹

**Affiliation:** ¹ Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China

**Corresponding author:** Jing Yan, Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China. Email: 20200121047@bucm.edu.cn

---

## Abstract

**Background.** Ethambutol causes an optic neuropathy, and its ocular reporting signal is well recognised. Whether that signal is concentrated in the optic nerve, rather than reflecting a general increase in ocular reporting, has not been tested against MedDRA's own ocular queries.

**Objectives.** To test whether ethambutol reports show an optic-nerve-predominant reporting pattern across the ocular queries, and whether that pattern replicates in independent national systems.

**Design.** Retrospective disproportionality analysis of individual case safety reports, with replication in two further national systems and a short exploratory transcriptomic reanalysis.

**Methods.** All 90 quarterly FDA Adverse Event Reporting System releases (2004Q1–2026Q2) were de-duplicated by case version. In 15,510 ethambutol cases we computed reporting odds ratios (ROR) for the eleven ocular Standardised MedDRA Queries (narrow sets, MedDRA 29.0), with Benjamini–Hochberg control across the eleven, and described the preferred terms inside the optic-nerve query against pre-specified control terms. Exposure role, reporting period and a fixed-regimen contrast were examined as sensitivity analyses, and the pattern was tested in JADER and Canada Vigilance.

**Results.** The optic-nerve query had the highest ROR of the eleven (23.51, 95% CI 21.35–25.89; 432 cases); four queries lay above unity, three below and four were null. Optic neuropathy (165 cases; 116.58, 99.36–136.78) and optic neuritis (156 cases; 23.67, 20.19–27.75) carried the evidence. Control terms were mostly at or below background, but vision blurred showed a modest excess (1.50, 1.28–1.76). The pattern replicated in JADER (optic neuropathy 570.96, 413.50–788.37) and Canada Vigilance (21.85, 14.13–33.79). Median onset was 125 days, against 33 days for non-ocular events.

**Conclusion.** Across three spontaneous-reporting systems, ethambutol showed a reproducible optic-nerve-predominant reporting pattern: a safety signal, not the incidence or causal effect of the drug.

**Keywords.** ethambutol; optic neuropathy; pharmacovigilance; disproportionality analysis; MedDRA; spontaneous reporting

---

## Plain Language Summary

Ethambutol is one of the standard drugs used to treat tuberculosis. It can damage the optic nerve, and patients may lose vision if the drug is continued after the damage begins. How often this happens is uncertain, because estimates depend on how closely patients are examined; published figures range from less than one in a hundred to about six in a hundred.

Doctors send reports of suspected side effects to national databases. We studied these reports to ask a narrower question than "how common is the damage": when ethambutol is named in a report that mentions an eye problem, is the problem usually something specific to the optic nerve, or is it any eye complaint at all? Using a standard dictionary that sorts eye problems into eleven categories, one of which is the optic nerve, we found that the optic-nerve category stands out far more than the others, and that everyday complaints such as cataract, dry eye and eye pain are not reported more often than expected. The same pattern appeared in databases from Japan and Canada.

Reports of side effects cannot tell us how many people are actually harmed, and they are influenced by which side effects doctors recognise and choose to report. What they can show is a consistent pattern across countries. That pattern supports watching vision carefully in people taking ethambutol, especially in the first months of treatment.

---

## 1. Introduction

Ethambutol has been part of first-line antitubercular chemotherapy since the 1960s, and it is the drug in that regimen whose toxicity most often forces a change of treatment. Its characteristic adverse effect is a bilateral, painless, slowly progressive optic neuropathy that preferentially damages the papillomacular bundle, producing loss of visual acuity, dyschromatopsia, central or caecocentral scotomas and, when the drug is continued, optic atrophy [1,2,3].

The frequency reported for this toxicity depends on how carefully patients are looked for. Retrospective chart review yields 0.28–0.5% [4,5], a nationwide insurance cohort gives a cumulative incidence of 0.9% [6], and prospective multidisciplinary screening with visual evoked potentials and optical coherence tomography gives 6.5% [7], with subclinical injury in up to 46% of eyes in one six-month study [8]. The variability is itself the clinical problem: a toxicity that is common in prospective series and rare in chart review is one that is not being looked for. Recovery is incomplete and slow, with 50–77% of eyes improving after withdrawal over a mean of about 15 months and retinal nerve fibre layer thinning persisting despite visual recovery [2,3,9], so the case for early detection rests on the assumption that the injury can be recognised before it is irreversible.

At the scale needed to characterise a reporting pattern, the evidence comes from spontaneous reporting systems. FAERS has been mined for these drugs before: Mao and Ou applied five signal-detection methods to the four first-line antitubercular drugs and reported that ethambutol carried more eye-disorder signals than the other three, but their analysis drew on 978 ethambutol reports from 2021Q1 to 2025Q3 and reported signal counts by system organ class, without multiplicity control, within-class comparators or control terms [14]. Pharmacovigilance based on VigiBase has likewise been organised by organ-system grouping rather than by term-level disproportionality against comparators [15]. Neither design can distinguish a signal concentrated in the optic nerve from a general increase in ocular reporting for a drug that clinicians already associate with eye problems.

The question this study addresses is therefore deliberately narrow: among ethambutol reports, is the reporting disproportion concentrated in the optic-nerve phenotype relative to the other ocular phenotypes, and does that pattern reproduce in other national systems? We pre-specified the eleven ocular Standardised MedDRA Queries, so that the comparison of the optic-nerve query against the rest does not depend on a term list assembled after the results were seen. We describe the preferred terms that drive the optic-nerve query, test the pattern against pre-specified non-specific ocular terms and in sensitivity analyses, and replicate it in the Japanese JADER and Canada Vigilance databases. A reanalysis of a public human retinal ganglion-like cell transcriptome is reported as a short exploratory adjunct; it is not used to establish a mechanism.

Throughout, the estimates are disproportionality measures in a spontaneous-reporting database. They describe how often a term is reported with the drug relative to other reports, not how often the adverse effect occurs in treated patients, and they cannot establish a causal effect. The analyses were designed and are reported within that boundary.


## 2. Methods

### 2.1 Design and reporting

This is a retrospective pharmacovigilance study of disproportionality in spontaneous adverse-event reports, with replication in two independent national systems and a short exploratory reanalysis of public transcriptomic data. Reporting follows the READUS-PV statement for disproportionality analyses in spontaneous reporting databases [16], with the RECORD-PE extension of STROBE for the pharmacoepidemiological components [17]. The completed checklist is provided as a supplementary file.

One specification is designated the main analysis and is the only one labelled "main". Every other definition of exposure, outcome or reference population is named and reported as a sensitivity analysis, and the label used in the text is the label used in the tables and the supplement.

### 2.2 Data sources and period

FAERS reports were obtained from the FDA quarterly ASCII releases from 2004Q1 to 2026Q2, ninety quarters in all, retrieved from the official distribution endpoint. These are the unaggregated files; the harmonised openFDA view was not used as the primary source because it omits the raw `CASEID` and `FDA_DT` fields required for case-version de-duplication. JADER, the Japanese system maintained by the Pharmaceuticals and Medical Devices Agency, was analysed from its September 2026 release (1,054,239 cases, 5,038,223 drug records and 1,751,879 reaction records). Canada Vigilance was analysed from Health Canada's case-level extract (cvponline, 31 May 2026), which holds 1,266,430 reports coded to MedDRA 29.0.

### 2.3 Case de-duplication

A case may be re-submitted in a later quarter when new information arrives, so several versions of one `CASEID` can coexist. Following the FDA's own convention, only the most recent version was retained, defined as the record with the highest `FDA_DT`, with ties broken by the highest `PRIMARYID`. All FAERS analyses are on this de-duplicated case set. The submission count, the de-duplicated count and the number removed are reported in the case flow (Figure 1).

### 2.4 Exposure

Exposure was defined as the appearance of ethambutol in the report's drug-name fields (`drugname` and `prod_ai`), identified with a case-insensitive substring match on the single name token ETHAMBUTOL. Brand and salt variants were not added to that token in FAERS, so a report naming only a brand product would not be captured; Canada Vigilance was read from the ingredient table for this reason (Section 2.8). No restriction on drug role was applied in the main analysis; restriction to reports naming ethambutol as the primary or secondary suspect drug is a sensitivity analysis. Five comparator drugs were defined in the same way for the within-class analysis: isoniazid, rifampicin, pyrazinamide, streptomycin and linezolid.

### 2.5 Outcomes

The primary outcome was the Optic nerve disorders narrow Standardised MedDRA Query. Outcomes were defined with MedDRA's own queries rather than with a list assembled for this study: the narrow term lists were read from the MedDRA 29.0 distribution file (`smq_content.asc`), and all eleven ocular queries were evaluated at preferred-term level with the same rules, so that the site of interest could not be selected after the results were seen. The eleven queries are Optic nerve disorders, Retinal disorders, Glaucoma, Lens disorders, Lacrimal disorders, Corneal disorders, Conjunctival disorders, Scleral disorders, Periorbital and eyelid disorders, Ocular infections and Ocular motility disorders. Terms may belong to more than one query, and the set is not claimed to be exhaustive of all ocular terminology.

Preferred terms inside the optic-nerve query were described when they carried at least three exposed cases, and the terms are reported without a selection based on their observed effect size. Six non-specific ocular terms were specified before analysis. Four are negative controls — cataract, dry eye, glaucoma and conjunctivitis — chosen because they are common complaints that a general increase in ocular reporting would raise and that the drug is not expected to cause. Two are non-specific comparators rather than negative controls: eye pain and vision blurred are plausibly drug-related, and vision blurred in particular may accompany optic-nerve injury, so they are reported as comparisons and not as terms expected to be null.

### 2.6 Disproportionality measures and signal definition

For each drug and each outcome the whole-database 2×2 table was constructed from de-duplicated cases. The reporting odds ratio (ROR) with its 95% confidence interval (Woolf) is the primary measure. The proportional reporting ratio with its χ² statistic and the Bayesian information component (IC025, Norén prior) were computed as complementary measures and are reported in the supplementary tables. A term was regarded as a signal when the lower bound of the ROR exceeded 1 and at least three exposed cases were present, a rule fixed before the analysis to avoid signals driven by single reports. Where any cell of a 2×2 table was zero, 0.5 was added to all four cells before the ratio and its interval were computed; the terms affected are identified in the supplementary tables.

Multiplicity was controlled with the Benjamini–Hochberg procedure within two families, stated in advance: the eleven ocular queries, and the fifteen preferred terms described in Section 3.3. A false-discovery rate q below 0.05 was required for a term to be called significant, and both the unadjusted and adjusted values are given where they matter. The ROR is an effect-size measure, the "at least three cases" rule is a stability threshold, and the q value is the multiplicity criterion; the three are reported separately and are not used interchangeably.

### 2.7 Sensitivity analyses

Three analyses test whether the main result depends on a single definition. First, exposure was restricted to reports naming ethambutol as the primary or secondary suspect drug. Second, the database was split by receipt year at 2016, so that each period carries at least forty optic-neuropathy events, and the optic-nerve contrast was recomputed in each period with that period's own de-duplicated case count as the reference population; this tests stability across reporting eras, not generalisability. Third, within the antitubercular class, the optic-nerve rate was compared between reports naming rifampicin, isoniazid and pyrazinamide with and without ethambutol, a contrast in which the background regimen is held constant by construction. Strata in which the groups differ in disease state — in particular isoniazid-only reports, largely latent-infection prophylaxis — are reported but not used as evidence.

Age, sex and reporting region were examined in a multivariable logistic model of an ocular event within the ethambutol cases. These coefficients are reported in the supplement and are not interpreted as patient-level risk factors, because the database records reports rather than patients.

### 2.8 External replication

The same panel was run in JADER and in Canada Vigilance. JADER provides MedDRA/J terms and no English column, so each term was mapped to its Japanese equivalent and the mapping is published in the supplement, together with the terms that could not be mapped. Exposure in JADER used the suspect-drug code, with a sensitivity analysis over all drug roles; Canada Vigilance was read with exposure taken from the ingredient table rather than the product name, so that brand-only entries are captured. The 2×2 construction and the interval were identical to those used in FAERS. Because the systems code suspect drugs differently — 1,798 of 3,483 JADER ethambutol cases name the drug as suspect, a much higher proportion than in FAERS — the comparison is by pattern and by direction, not by the magnitude of the ROR, and case counts are shown alongside every estimate.

### 2.9 Time to onset

Within the de-duplicated ethambutol case set, time to onset was computed as the interval between the therapy start date and the event date, restricted to reports with both dates, a non-negative interval and an interval of at most 3,650 days. Distributions are summarised by median and interquartile range, separately for optic-nerve, other ocular and non-ocular events. The proportion of optic-nerve cases with the fields needed for this analysis is reported, because the subset is defined by completeness rather than by sampling.

### 2.10 Exploratory transcriptomic reanalysis

GSE294687 profiled human induced pluripotent stem cell-derived retinal ganglion-like cells exposed to ethambutol or vehicle in four paired preparations. The series was reanalysed with a paired test on log2 counts per million, and genes were called differentially expressed at a Benjamini–Hochberg q below 0.05. Because the published mechanisms make directional predictions, they were evaluated at gene-set level: the mean log2 fold change across the genes each mechanism implicates, and the number of those genes that changed significantly, are reported together with the verdict.

Two features of the experiment bound its interpretation and are stated with the results: the exposure was 8 mM for 24 hours, which is 330 to 800 times the peak plasma concentration at standard dosage, and the preparation is a monoculture of retinal ganglion-like cells, so microglial and Müller glial contributions cannot be observed. A public TPEN-treated human cell line (GSE318912) was used as an empirical zinc-chelation reference; the comparison is reported with the caveat that the two experiments used different cell types.

The transcriptomic section is exploratory. It was not pre-registered, the directional predictions were assembled from the published literature rather than fixed in advance of our own data, and no result from it is used as evidence for or against a mechanism in patients.

### 2.11 Software and reproducibility

All analyses were run as standalone, re-runnable Python scripts with recorded software versions and random seeds. The de-duplication map, the 2×2 tables, the query-level results and the preferred-term results are exported from a single results file (`results/main_results.json`), from which the tables in this paper are generated, so that no number is transcribed by hand. The code, the derived tables and a data dictionary are available at the repository given in the Statements, under a tagged release that corresponds to this manuscript.


## 3. Results

### 3.1 Case flow and cohort

The 90 quarterly FAERS releases contributed 24,812,425 submitted reports; applying the FDA case-version rule left 20,692,683 de-duplicated cases (Figure 1). Ethambutol appeared in 15,510 of them, of which 9,024 (58.2%) named it as the primary or secondary suspect drug, 1,134 as the primary suspect, and 6,486 as a concomitant medication only. Median age was 50 years (IQR 32–67) among the 12,244 cases with a plausible recorded age, and 6,672 of the 13,921 cases with a recorded sex (47.9%) were female. Four hundred and thirty-two cases (2.8%) reported at least one event within the optic-nerve query. The same exposure definition was applied to the two replication databases, in which 3,483 JADER cases and 965 Canada Vigilance reports named ethambutol (Table 1).

### 3.2 The optic-nerve query stands out among the eleven ocular queries

Across the eleven ocular queries, the optic-nerve query returned the highest reporting odds ratio, 23.51 (95% CI 21.35–25.89) on 432 exposed cases, 5.7 times the next highest point estimate (Figure 2, Table 2). The two estimates are not formally compared, and the ratio is reported as a description of the ordering rather than as a test of their difference. Four queries lay significantly above unity — optic nerve 23.51, ocular infections 4.13, retinal 2.18 and ocular motility 2.02 — three lay significantly below it (glaucoma 0.45, lacrimal 0.24, periorbital and eyelid 0.48), and four were null (lens 1.18, corneal 1.08, conjunctival 0.95, scleral 0.88). The queries covering the ocular surface and anterior segment therefore showed no excess, while the query covering the optic nerve showed the largest one.

The elevation of the ocular-infections query (4.13) is not attributable to the drug on this evidence: ethambutol is an antimycobacterial, and ocular tuberculosis itself generates terms of that kind, so indication and channelling are the more economical explanation. The retinal elevation (2.18) is compatible with an effect on retinal ganglion cells, which the optic-nerve terms also describe. The motility elevation (2.02) is not interpreted. All four query-level q values were below 0.005.

### 3.3 The terms driving the query, and the pre-specified controls

Sixteen of the query's 45 narrow terms carried at least one ethambutol case and nine carried three or more; all nine were significant after correction (Figure 3). The evidence is carried by the terms with the largest numbers of cases rather than by the largest ratios. Optic neuropathy gave an ROR of 116.58 (99.36–136.78) on 165 cases and optic neuritis 23.67 (20.19–27.75) on 156 cases. The remaining seven were toxic optic neuropathy (232.95, 178.18–304.56; 63 cases), optic atrophy (20.00, 13.36–29.94; 24), papilloedema (5.97, 3.84–9.26; 20), optic nerve disorder (7.62, 3.96–14.68; 9), optic nerve injury (9.45, 4.71–18.95; 8), visual evoked potentials abnormal (30.30, 9.65–95.18; 3) and optic disc hyperaemia (181.83, 54.42–607.55; 3).

The three negative controls were at or below background: cataract 0.89 (0.65–1.22; 39 cases), dry eye 0.28 (0.15–0.52; 10) and glaucoma 0.28 (0.11–0.75; 4), the last two significantly below unity. The two non-specific comparators behaved differently from one another: conjunctivitis was null at 0.81 (0.45–1.46; 11) and eye pain was slightly below unity at 0.66 (0.45–0.96; 27), whereas vision blurred showed a modest excess at 1.50 (1.28–1.76) on 151 cases. That excess is an order of magnitude below the optic-neuropathy estimate and is compatible with either a drug effect or the way a non-specific visual complaint is coded; it is reported rather than dismissed because it is the one control term that moved in the same direction as the optic-nerve terms.

### 3.4 Sensitivity: exposure role and reporting period

Restricting exposure to reports naming ethambutol as the primary or secondary suspect drug increased both estimates, because the cohort is smaller and more specifically exposed: the query rose from 23.51 to 35.01 (370 cases exposed) and optic neuropathy from 116.58 to 191.22 (157 cases) (Figure 4).

Splitting the database by receipt year at 2016 gave 4,316 ethambutol cases among 7,189,907 de-duplicated cases in 2004–2016 and 11,194 among 13,502,719 in 2017–2026, which together account for the whole cohort. The optic-nerve contrast was similar in the two periods: 131.72 (100.43–172.76) on 57 exposed cases and 111.66 (91.61–136.10) on 108. The proportion of ethambutol cases reporting optic neuropathy fell from 1.32% to 0.96%, and the proportion of all other reports carrying the term fell from 0.0102% to 0.0087%, so the ratio between the two was stable while both proportions fell. This analysis is within one database and shares its reporting artefacts; it tests stability across reporting eras, not generalisability.

Within the antitubercular class, the one comparison in which the background regimen is held constant — reports naming rifampicin, isoniazid and pyrazinamide, partitioned by whether ethambutol is also named — gave an optic-nerve rate of 1.23% (76/6,167) with ethambutol against 0.64% (7/1,098) without, a rate ratio of 1.93 (0.89–4.18). The interval includes unity and the unexposed group is small, so this contrast is consistent in direction with the rest of the analysis but is not statistically significant on its own, and it is reported as a supporting analysis rather than as the basis of a within-class claim.

### 3.5 Replication in two independent national systems

In JADER, the same direction appeared on a much smaller base (Table 3). Among the 1,798 cases naming ethambutol as the suspect drug, optic neuropathy gave an ROR of 570.96 (413.50–788.37) on 73 exposed cases, toxic optic neuropathy 864.62 (426.37–1,753.36) on 19, optic neuritis 52.20 (35.84–76.04) on 30 and optic atrophy 50.25 (15.44–163.55) on 3; cataract, glaucoma and dry eye were null or below unity in the same analysis. Across all drug roles the optic-neuropathy estimate was 304.24 (220.75–419.30) on 75 cases.

In Canada Vigilance, 965 reports named ethambutol, 21 of which carried an optic term, giving an ROR of 21.85 (14.13–33.79); restricted to the 460 suspect reports the estimate was 44.63 (28.42–70.10) on 20 cases. The system-organ-class measure for eye disorders was much weaker, 2.60 (2.12–3.18), which is the contrast the query-level analysis makes internally: the organ-system category pools the optic-nerve and non-specific events, and the association lives in the former.

The extract of Canada Vigilance available to us carries the optic-nerve composite and the system-organ-class count, but not a term-level control panel comparable to the FAERS one; the term-level control comparison therefore rests on FAERS (Figure 3) and JADER, and the Canadian contribution is the direction of the optic-nerve contrast. The magnitude of these estimates differs between databases by more than an order of magnitude, and is not compared. JADER codes a much higher proportion of ethambutol reports as suspect than FAERS does (1,798 of 3,483 against 9,024 of 15,510), and the systems differ in reporting culture, in the terms available in their languages and in the size of their denominators. What replicates across the three systems is the pattern — a strong optic-nerve signal accompanied by the absence of a signal in the non-specific terms — and the case counts, which are shown alongside every estimate because a large ratio computed on a handful of cases is not the same finding as a moderate ratio computed on hundreds.

### 3.6 Time to onset

Time from starting ethambutol to the reported event could be computed in 2,446 cases. The median was 125 days (IQR 63–293; 90th percentile 636) for optic-nerve events, against 33 days (IQR 10–100) for non-ocular events in the same case set. This distribution also fixes when surveillance would have to begin: 11.0% of optic-nerve events were reported within 30 days of starting treatment and 23.2% within 60 days, with the earliest decile at 28 days. Only 27.8% of the optic-nerve cases carried age, sex and a therapy start date together, so this analysis rests on the minority of reports that are completely documented, and the subset is defined by completeness rather than by sampling.

### 3.7 Exploratory transcriptomic reanalysis

The reanalysis of GSE294687 yielded 15,421 genes, of which 2,083 changed at q < 0.05 between ethambutol and vehicle in the paired design. The exposure was 8 mM for 24 hours, 330 to 800 times the peak plasma concentration at standard dosage, so every statement below refers to a millimolar exposure in a monoculture of retinal ganglion-like cells.

Three mechanisms moved in the direction their published accounts predict, at gene-set level. The NRF2 antioxidant programme was the strongest: NFE2L2 itself rose 1.02 log2 and its targets — HMOX1 (+0.98), GCLM (+0.95), TXNRD1, SRXN1, NQO1, SQSTM1 and FTH1 — moved with it, seven of the ten genes significantly, for a mean of +1.045. The autophagy receptors accumulated (SQSTM1 +1.42, MAP1LC3B +1.03; mean +0.797), the pattern of a flux blockade rather than of increased degradation, and the respiratory-chain subunits fell (mean −0.272, four of twelve significant).

Two other accounts did not behave as predicted. The ferroptosis account predicts SLC7A11 and GPX4 falling; their transcripts rose, SLC7A11 by 3.80 log2, while the iron-handling genes TFRC (+2.00) and FTH1 (+0.31) rose as that account also predicts. The zinc-chelation account was tested against an empirical reference, a TPEN-treated human cell line (GSE318912): TPEN lowered metallothionein (mean −0.17) and raised the SLC39A importers (+0.33), whereas ethambutol raised metallothionein (+0.31) and left the importers unchanged (+0.04), and the two fold-change vectors correlated at r = +0.07 across the 12,201 genes both experiments measured. The two experiments used different cell types, so that correlation bounds rather than settles the comparison.

None of this establishes a mechanism in patients. The predictions were assembled from the literature rather than fixed before our own data were examined, there is no protein measurement, no genotype and no microglial or Müller glial compartment in the preparation, and the concentration is far above therapeutic exposure. What it does show is that selected transcriptional predictions of the ferroptosis account were not reproduced under these conditions, which is a weaker statement than a refutation and is reported as such.


## 4. Discussion

### 4.1 Principal findings

In 15,510 de-duplicated ethambutol cases drawn from 20.7 million FAERS cases, the ocular reporting disproportion was concentrated in the optic-nerve query: it was the highest of the eleven ocular queries tested on MedDRA's own terms, at 23.52 against 4.13 for the next, and the queries covering the ocular surface and anterior segment were at or below background. Within the query the evidence rested on optic neuropathy and optic neuritis, the two terms with the largest numbers of exposed cases, rather than on the terms with the largest ratios. The same pattern — a strong optic-nerve signal with no excess in the non-specific terms — appeared in JADER and in Canada Vigilance, systems with different reporters, different coding of suspect drugs and different reporting cultures. Median time to an optic-nerve event was 125 days, against 33 days for non-ocular events in the same case set.

### 4.2 What this adds to previous work

That ethambutol is associated with optic neuropathy is not new, and the finding that its ocular signal is prominent has been reported before [14]. The contribution here is the internal contrast. Previous pharmacovigilance analyses of these drugs reported signal counts aggregated to system organ class [14] or organised the ocular phenotype by organ-system grouping [15]; in either design, a drug that produces a specific optic-nerve injury and a drug that produces a general increase in ocular reporting look alike. Testing the eleven ocular queries against one another, with the optic-nerve query nominated in advance and with pre-specified non-specific terms as controls, separates those two possibilities within the same reports. That contrast is what replicates across the three systems, and it is less consistent with a uniform increase across all ocular reporting than a single organ-system count would be. It does not remove differential recognition and coding of suspected toxicity, which remains the main alternative explanation for the pattern.

The design also changes what can be claimed. A signal that is concentrated in one anatomical category, in three systems, is a stronger basis for a safety hypothesis than a single elevated organ-system count, and it is the kind of pattern that can be checked in other databases. It is not evidence of incidence, and the absolute proportions reported here — 6.21% of ethambutol cases with any ocular event, 3.04% with an optic-nerve event — sit at the upper end of the published clinical range because stimulated reporting for a well-known adverse effect inflates the numerator and the denominator is reports rather than exposures.

### 4.3 Reporting bias, indication confounding, and what the controls do and do not show

Spontaneous reporting has no denominator, and under-reporting is substantial and non-random. Three biases are relevant, and they act differently on the main result. Notoriety bias — increased reporting of a known adverse effect — raises the absolute ocular signal but does not by itself produce a contrast between optic-nerve terms and cataract, dry eye or glaucoma, because all of them sit in the same reports. Sharing a database and an exposure definition does, however, not make every reporting bias common to all outcomes: a clinician who already suspects ethambutol toxicity may record the optic-nerve diagnosis precisely and leave a visual complaint uncoded. The comparison narrows the range of explanations; it does not eliminate outcome-specific reporting. Differential coding is the more serious concern: clinicians who suspect ethambutol toxicity may code optic neuropathy more precisely than they code a non-specific complaint, which would concentrate the signal in the optic-nerve terms without any difference in underlying incidence. Indication confounding acts in the opposite direction, inflating the ocular signal as a whole; the elevation of the ocular infections query is the clearest example, and it is best explained by ocular tuberculosis itself rather than by the drug.

The controls bound the conclusion in both directions. The absence of a signal for cataract, dry eye, eye pain and glaucoma makes a general increase in ocular reporting an unlikely explanation for the optic-nerve result, but it does not establish that these events are not caused by the drug: a true effect that is small relative to the background reporting rate would not appear. The result is therefore a statement about the shape of the reporting signal, not a toxicity profile. Restriction to suspect-drug reports and the period split change the size of the estimate without changing its direction. The fixed-regimen contrast — rifampicin, isoniazid and pyrazinamide with versus without ethambutol — holds the background regimen constant but rests on a small unexposed group, and its interval includes unity; it is reported for completeness rather than as evidence of a within-class effect.

### 4.4 Limits of the transcriptomic exploration

The transcriptomic reanalysis was included because the mechanisms proposed for this toxicity make directional predictions that can be checked in human cells, not because it can resolve the mechanism. Three limits are decisive for how it should be read. The exposure was 8 mM for 24 hours, 330 to 800 times the peak plasma concentration at standard dosage, so the experiment models an acute millimolar insult rather than the months of therapeutic exposure over which the clinical toxicity develops. The preparation is a monoculture of retinal ganglion-like cells, so any contribution from microglia, Müller glia or the retinal vasculature is invisible to it. And the predictions were assembled from the published literature after the data were in hand, so the analysis is exploratory in the strict sense: it can generate hypotheses, and it can show that a predicted direction was not observed, but it cannot confirm or refute a mechanism operating in patients. The antioxidant, autophagic and oxidative-phosphorylation programmes moved in the predicted directions; the ferroptosis account [18] predicted a fall in SLC7A11 and GPX4 and their transcripts rose, so the appropriate conclusion is that selected transcriptional predictions were not reproduced under these conditions, not that ferroptosis has been excluded.

### 4.5 Clinical and regulatory implications

The practical value of a reporting signal of this shape is that it identifies where to look. Ethambutol optic neuropathy is treatable only by stopping the drug, and the damage becomes irreversible once atrophy is established, so the clinical task is detection before that point. In these data 11.0% of optic-nerve events were reported within 30 days of starting treatment and 23.2% within 60 days, with a median of 125 days; a surveillance schedule whose first assessment falls at three months would therefore sit after a substantial minority of events. That is an argument for a baseline examination and an early first follow-up, and it is consistent with the clinical literature in which structural measures predict visual outcome better than initial acuity [10,11,12,13]. The data cannot define the optimal interval, because the reports do not record examinations that were not performed.

For regulators and for those who build pharmacovigilance workflows, the transferable point is methodological. A MedDRA query set nominated in advance, used as its own internal comparison and paired with pre-specified non-specific controls, gives a signal that is robust to the objection that the drug simply generates more ocular reports. The same design can be applied to other drugs with a suspected site-specific toxicity, and it requires no data beyond what spontaneous reporting systems already publish.

Two designs would move the question forward, and neither can be built from spontaneous reports. A prospective cohort with protocolised baseline and interval ophthalmic assessment — optical coherence tomography and visual field testing, with the examination schedule fixed in advance rather than triggered by symptoms — would give both an incidence and the detection window. A record-linkage study of prescription data to incident optic-neuropathy diagnoses, with renal function and dose as covariates, would test the exposure–response relationship that a reporting database cannot address.

### 4.6 Conclusion

Across three spontaneous-reporting systems, ethambutol showed a reproducible optic-nerve-predominant adverse-event reporting pattern. These findings characterise a safety signal rather than the incidence or causal effect of ethambutol. The pattern is consistent with a site-specific toxicity and with the clinical literature on ethambutol optic neuropathy, but differential reporting and residual confounding cannot be excluded, and the transcriptomic exploration does not establish a mechanism.

## Statements

**Ethics approval and consent to participate.** Not required. The study used publicly available,
de-identified aggregate data from pharmacovigilance databases and public gene-expression series.
No human participants were recruited and no identifiable information was accessed.

**Data availability.** FAERS quarterly ASCII releases are available from the U.S. Food and Drug
Administration (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html); JADER from the
Pharmaceuticals and Medical Devices Agency of Japan; Canada Vigilance from Health Canada
(cvponline); GSE294687 and GSE318912 from NCBI GEO. The derived tables that support the findings
— the de-duplication map, the 2×2 tables, `results/main_results.json` and the code that generates
every table and figure — are available at
https://github.com/Bowen2485/ethambutol-ocular-toxicity under an MIT licence.

**Funding.** This research received no specific grant from any funding agency in the public,
commercial, or not-for-profit sectors.

**Declaration of conflicting interests.** The authors declare no competing interests.

**Author contributions.** Bowen Shi: conceptualisation, methodology, software, formal analysis,
writing — original draft. Jing Yan: conceptualisation, supervision, writing — review and editing.
Zhengzheng Wu: supervision. Siyuan Yang: writing — review and editing. Yaqin Tan: investigation.
Xuan Wang: visualisation. All authors read and approved the final manuscript.

**Acknowledgements.** None.

## Figure legends

**Figure 1.** Case flow in the three spontaneous-reporting systems. FAERS releases were
de-duplicated by case version; the ethambutol cohort was defined by any drug record naming the
drug, and split by drug role. JADER and Canada Vigilance were analysed independently with the
exposure definitions given in Table 1.

**Figure 2.** The eleven ocular Standardised MedDRA Queries (narrow sets) in FAERS, ethambutol
against all other de-duplicated reports. Points are reporting odds ratios with 95% confidence
intervals on a logarithmic axis; the dashed line marks unity. Red, interval above unity; blue,
interval below unity; grey, interval includes unity. The number of exposed cases is given at the
right.

**Figure 3.** Preferred terms inside the optic-nerve query (upper panel) and the pre-specified
non-specific control terms (lower panel). Terms with fewer than three exposed cases are not
plotted. Conventions as in Figure 2.

**Figure 4.** Sensitivity of the optic-nerve estimate to exposure role and reporting period. The
upper four rows compare the preferred term and the query under all-role and suspect-only
exposure; the lower two split the cohort by receipt year at 2016. Conventions as in Figure 2.


## Tables

Table 1. Data sources and exposed cohorts.

| Source | Period | Records | Records naming ethambutol | Exposure definition |
|---|---|---|---|---|
| FAERS quarterly ASCII releases | 2004Q1–2026Q2 (90 quarters) | 24,812,425 submitted; 20,692,683 de-duplicated cases | 15,510 (9,024 as primary or secondary suspect) | Any drug record, case-insensitive substring |
| JADER | September 2026 release | 1,054,239 cases | 3,483 (1,798 as suspect) | Suspect drug code; all roles in sensitivity |
| Canada Vigilance | Extract of 31 May 2026 | 1,266,430 reports | 965 (460 as suspect) | Ingredient table; all roles in main |

Table 2. The eleven ocular Standardised MedDRA Queries (narrow sets, MedDRA 29.0), ethambutol against all other de-duplicated reports.

| Query | Narrow terms | Exposed cases | Cases in database | ROR | 95% CI | q |
|---|---|---|---|---|---|---|
| Optic nerve disorders | 45 | 432 | 25,600 | 23.51 | 21.35–25.89 | <1e-300 |
| Ocular infections | 110 | 127 | 41,375 | 4.13 | 3.47–4.92 | 5.2e-66 |
| Retinal disorders | 208 | 164 | 101,220 | 2.18 | 1.87–2.54 | 1.3e-23 |
| Ocular motility disorders | 69 | 62 | 41,091 | 2.02 | 1.57–2.59 | 4e-08 |
| Lens disorders | 40 | 60 | 67,857 | 1.18 | 0.92–1.52 | 0.27 |
| Corneal disorders | 114 | 18 | 22,172 | 1.08 | 0.68–1.72 | 0.81 |
| Conjunctival disorders | 83 | 70 | 98,182 | 0.95 | 0.75–1.20 | 0.81 |
| Scleral disorders | 31 | 3 | 4,537 | 0.88 | 0.28–2.74 | 0.83 |
| Periorbital and eyelid disorders | 104 | 29 | 79,763 | 0.48 | 0.34–0.70 | 0.00012 |
| Glaucoma | 52 | 13 | 38,632 | 0.45 | 0.26–0.77 | 0.0047 |
| Lacrimal disorders | 61 | 15 | 83,295 | 0.24 | 0.14–0.40 | 4.9e-09 |

Table 3. The optic-nerve outcome in the three systems, by exposure definition.

| System | Exposure | Outcome | Exposed cases | ROR (95% CI) |
|---|---|---|---|---|
| FAERS | Any role (main) | Optic neuropathy | 165 | 116.58 (99.36–136.78) |
| FAERS | Any role (main) | Optic-nerve query | 432 | 23.51 (21.35–25.89) |
| FAERS | Suspect only | Optic neuropathy | 157 | 191.22 (162.29–225.31) |
| FAERS | Suspect only | Optic-nerve query | 370 | 35.01 (31.53–38.87) |
| FAERS | Any role, 2004–2016 | Optic neuropathy | 57 | 131.72 (100.43–172.76) |
| FAERS | Any role, 2017–2026 | Optic neuropathy | 108 | 111.66 (91.61–136.10) |
| JADER | Suspect only | Optic neuropathy | 73 | 570.96 (413.50–788.37) |
| JADER | Any role | Optic neuropathy | 75 | 304.24 (220.75–419.30) |
| Canada Vigilance | Any role | Any optic-nerve term | 21 | 21.85 (14.13–33.79) |
| Canada Vigilance | Suspect only | Any optic-nerve term | 20 | 44.63 (28.42–70.10) |

ROR, reporting odds ratio. "Any optic-nerve term" is a composite of 21 MedDRA preferred terms in
the Canadian extract; the exposed-case count is the number of reports carrying at least one of
them, not the number of terms. The JADER rows report the term-specific estimate; cataract,
glaucoma and dry eye were null or below unity in the same analysis. The two FAERS period rows use
that period's own de-duplicated case count as the reference population. Estimates are not compared
across systems: the proportion of reports naming the drug as suspect differs by system.

Table 4. Non-specific ocular terms in FAERS (pre-specified controls).

| Term | Exposed cases | Cases in database | ROR | 95% CI | q |
|---|---|---|---|---|---|
| Cataract | 39 | 58,616 | 0.89 | 0.65–1.22 | 0.48 |
| Dry eye | 10 | 47,855 | 0.28 | 0.15–0.52 | 2.1e-05 |
| Eye pain | 27 | 54,555 | 0.66 | 0.45–0.96 | 0.034 |
| Glaucoma | 4 | 19,045 | 0.28 | 0.11–0.75 | 0.0081 |
| Conjunctivitis | 11 | 18,170 | 0.81 | 0.45–1.46 | 0.48 |
| Vision blurred | 151 | 135,063 | 1.50 | 1.28–1.76 | 1e-06 |


## References

1. Chamberlain PD, Sadaka A, Berry S, Lee AG. Ethambutol optic neuropathy. Curr Opin Ophthalmol. 2017;28(6):545-551. doi:10.1097/icu.0000000000000416.
2. Ambika S, Lakshmi KP, Gopal M, Noronha OV. Visual outcomes of toxic optic neuropathy secondary to Ethambutol: A retrospective observational study from India, an endemic country. Indian J Ophthalmol. 2022;70(9):3388-3392. doi:10.4103/ijo.ijo_2996_21.
3. An HR, Lee BJ, Moon Y. Visual Recovery Time in Patients with Ethambutol-induced Toxic Optic Neuropathy. Korean J Ophthalmol. 2024;38(2):91-97. doi:10.3341/kjo.2023.0095.
4. Singh P, Karkhur S, Verma V. Ethambutol-Induced Optic Neuropathy: A Retrospective Study of Incidences and Risk Factors. Cureus. 2025;17(2):e79160. doi:10.7759/cureus.79160.
5. Chaitanuwong P, Srithawatpong S, Ruamviboonsuk P, Apinyawasisuk S, Watcharapanjamart A, Moss HE. Incidence, risk factors and ophthalmic clinical characteristic of ethambutol-induced optic neuropathy: 7-year experience. Front Ophthalmol (Lausanne). 2023;3:. doi:10.3389/fopht.2023.1152215.
6. Lee S, Ryu WY, Kang D, Lee JK. Prevalence and Incidence of Ethambutol-Induced Optic Neuropathy and Its Risk Factors in Korea: A Nationwide Population-Based Study. J Korean Med Sci. 2025;40(20):e65. doi:10.3346/jkms.2025.40.e65.
7. Liu SS, Feng SC, Wu MF, Chin CS, Chen HC, Huang WC. Programmatic Assessment of Ethambutol-Related Optic Neuropathy in Patients with Mycobacterial Infections: A Prospective Observational Cohort Study. Infect Dis Ther. 2025;14(10):2391-2404. doi:10.1007/s40121-025-01219-x.
8. Mandal S, Saxena R, Dhiman R, Mohan A, Padhy SK, Phuljhele S, et al. Prospective study to evaluate incidence and indicators for early detection of ethambutol toxicity. Br J Ophthalmol. 2021;105(7):1024-1028. doi:10.1136/bjophthalmol-2020-316897.
9. Sachdeva G, Dhiman R, Raj D, Lavanya G, Mohan A, Pujari A, et al. Evaluation of visual function and OCT parameters in ethambutol-induced optic neuropathy: a longitudinal study. Br J Ophthalmol. 2026;110(2):185-190. doi:10.1136/bjo-2025-327475.
10. Lee JY, Choi JH, Park KA, Oh SY. Ganglion Cell Layer and Inner Plexiform Layer as Predictors of Vision Recovery in Ethambutol-Induced Optic Neuropathy: A Longitudinal OCT Analysis. Invest Ophthalmol Vis Sci. 2018;59(5):2104-2109. doi:10.1167/iovs.17-22988.
11. Kang MC, Eun HW, Park KA, Oh SY. Optical Coherence Tomography Parameters and Optimal Cut-off Values for Predicting Visual Prognosis in Ethambutol-Induced Optic Neuropathy. J Neuroophthalmol. 2024;44(4):559-564. doi:10.1097/wno.0000000000002092.
12. Han KE, Yoon H, Choi H, Lee JE, Kim SJ. Factors affecting visual outcome in patients with toxic optic neuropathy caused by ethambutol. Sci Rep. 2025;15(1):6257. doi:10.1038/s41598-025-90663-3.
13. Sheth J, Sachdeva V, Goyal A, Parikh A, Nalawade R, Nanavati H, et al. Clinical profile and visual outcomes in ethambutol-induced toxic optic neuropathy. Indian J Ophthalmol. 2025;73(Suppl 3):S484-S491. doi:10.4103/ijo.ijo_1807_24.
14. Mao Q, Ou ZM. Mining of adverse reaction signals and medication insights of anti-tuberculosis drugs based on the FAERS database. Asia-Pacific Medical Frontiers. 2026;1(3):1-18.
15. Suresh J, Kumar R, Hissar S, Shukla S, Vivekanandan K. Ocular toxicity associated with Ethambutol in the South-East Asia Region. Int Ophthalmol. 2026;46(1):251. doi:10.1007/s10792-026-04131-6.
16. Fusaroli M, Salvo F, Begaud B, AlShammari TM, Bate A, Battini V, et al. The Reporting of a Disproportionality Analysis for Drug Safety Signal Detection Using Individual Case Safety Reports in PharmacoVigilance (READUS-PV): Development and Statement. Drug Saf. 2024;47(6):575-584. doi:10.1007/s40264-024-01421-9.
17. Langan SM, Schmidt SA, Wing K, Ehrenstein V, Nicholls SG, Filion KB, et al. The reporting of studies conducted using observational routinely collected health data statement for pharmacoepidemiology (RECORD-PE). BMJ. 2018;363:. doi:10.1136/bmj.k3532.
18. Li Q, Ge W, Zhang Y, Xu Q, Xu J, Zhang Y, et al. Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis in retinal ganglion cells via Smad4 pathway. Hum Cell. 2026;39(2):37. doi:10.1007/s13577-025-01342-4.
