# Optic-nerve-predominant adverse-event reporting with ethambutol: a multi-database pharmacovigilance study with exploratory transcriptomic analysis

**Running title:** Optic-nerve-predominant reporting with ethambutol

**Authors:** Bowen Shi¹ (ORCID 0009-0001-6900-1779), Jing Yan¹*, Zhengzheng Wu¹, Siyuan Yang¹, Yaqin Tan¹, Xuan Wang¹

**Affiliation:** ¹ Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China

**Corresponding author:** Jing Yan, Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China. Email: 20200121047@bucm.edu.cn

---

## Abstract

**Background.** Ethambutol causes an optic neuropathy, and its ocular signal is well recognised. Whether it is concentrated in the optic nerve, rather than a general increase in ocular reporting, is untested against MedDRA's queries.

**Objectives.** To test whether ethambutol reports show an optic-nerve-predominant reporting pattern across ocular queries, and whether it replicates in independent systems.

**Design.** Retrospective disproportionality analysis of case safety reports, with replication and exploratory transcriptomics.

**Methods.** All 90 quarterly FDA Adverse Event Reporting System releases (2004Q1–2026Q2) were de-duplicated by case version. In 15,510 ethambutol cases we computed reporting odds ratios (ROR) for the eleven ocular Standardised MedDRA Queries (narrow sets, MedDRA 29.0), with Benjamini–Hochberg control, and described the terms inside the optic-nerve query against pre-specified controls. Exposure role, period and a fixed-regimen contrast were sensitivity analyses, and the pattern was tested in JADER and Canada Vigilance.

**Results.** The optic-nerve query had the highest ROR (23.51, 95% CI 21.35–25.89; 432 cases); four showed positive signals, three were significantly below 1 and four had intervals spanning 1. Optic neuropathy (165; 116.58, 99.36–136.78) and optic neuritis (156; 23.67, 20.19–27.75) carried it. The four negative controls showed no positive signal; vision blurred did (1.50, 1.28–1.76). A term-level signal was also seen in JADER (optic neuropathy 570.96, 413.50–788.37); Canada Vigilance showed a broader string-matched composite (21.85, 14.13–33.79). The non-specific comparison was possible in FAERS and JADER, not Canada. Among reports with usable dates, median onset was 125 days for optic-nerve events against 33 for non-ocular events. Exploratory transcriptomics did not reproduce selected ferroptosis predictions, whose relevance is uncertain.

**Conclusion.** Ethambutol reports showed an optic-nerve-predominant pattern in FAERS and an optic-nerve-related signal in JADER and Canada Vigilance: a safety signal, not an incidence or causal effect.

**Plain Language Title.** How side-effect reports describe eye problems with the tuberculosis drug ethambutol

**Keywords.** ethambutol; optic neuropathy; pharmacovigilance; disproportionality analysis; MedDRA; spontaneous reporting

---

## Plain Language Summary

Ethambutol is one of the standard drugs used to treat tuberculosis. It can damage the optic nerve, and patients may lose vision if the drug is continued after the damage begins. How often this happens is uncertain, because estimates depend on how closely patients are examined; published figures range from less than one in a hundred to about six in a hundred.

Doctors send reports of suspected side effects to national databases. We studied these reports to ask a narrower question than "how common is the damage": when ethambutol is named in a report that mentions an eye problem, is the problem usually something specific to the optic nerve, or is it any eye complaint at all? Using a standard dictionary that sorts eye problems into eleven categories, one of which is the optic nerve, we found that the optic-nerve category stands out far more than the others, and that everyday complaints such as cataract, dry eye and eye pain are not reported more often than expected. A similar optic-nerve signal appeared in databases from Japan and Canada, although the Canadian data do not allow the same term-by-term comparison of everyday eye complaints.

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

Exposure was defined as the appearance of ethambutol in the report's drug-name fields (`drugname` and `prod_ai`), identified with a case-insensitive substring match on the single name token ETHAMBUTOL. Brand and salt variants were not added to that token in FAERS, so a report naming only a brand product would not be captured; Canada Vigilance was read from the ingredient table for this reason (Section 2.8). No restriction on drug role was applied in the main analysis; restriction to reports naming ethambutol as the primary or secondary suspect drug is a sensitivity analysis. Three comparator drugs were defined in the same way for the within-class analysis: isoniazid, rifampicin and pyrazinamide.

### 2.5 Outcomes

The primary outcome was the Optic nerve disorders narrow Standardised MedDRA Query. Outcomes were defined with MedDRA's own queries rather than with a list assembled for this study: the narrow term lists were read from the MedDRA 29.0 distribution file (`smq_content.asc`), and all eleven ocular queries were evaluated at preferred-term level with the same rules, so that the site of interest could not be selected after the results were seen. The eleven queries are Optic nerve disorders, Retinal disorders, Glaucoma, Lens disorders, Lacrimal disorders, Corneal disorders, Conjunctival disorders, Scleral disorders, Periorbital and eyelid disorders, Ocular infections and Ocular motility disorders. The query set and the control terms were fixed before the disproportionality analyses were run, but the analysis was not prospectively registered and those selections were made after the database data were available. Terms may belong to more than one query, and the set is not claimed to be exhaustive of all ocular terminology.

Preferred terms inside the optic-nerve query were described when they carried at least three exposed cases, and the terms are reported without a selection based on their observed effect size. Six non-specific ocular terms were specified before analysis. Four are negative controls — cataract, dry eye, glaucoma and conjunctivitis — chosen because they are common complaints that a general increase in ocular reporting would raise and that the drug is not expected to cause. Two are non-specific comparators rather than negative controls: eye pain and vision blurred are plausibly drug-related, and vision blurred in particular may accompany optic-nerve injury, so they are reported as comparisons and not as terms expected to be null.

### 2.6 Disproportionality measures and signal definition

For each drug and each outcome the whole-database 2×2 table was constructed from de-duplicated cases. The reporting odds ratio (ROR) with its 95% confidence interval (Woolf) is the primary measure. A term was regarded as a signal when the lower bound of the ROR exceeded 1 and at least three exposed cases were present, a rule fixed before the analysis to avoid signals driven by single reports. Where any cell of a 2×2 table was zero, 0.5 was added to all four cells before the ratio and its interval were computed; the terms affected are identified in the supplementary tables.

Two-sided p values were obtained from a Fisher exact test when the smallest expected cell count fell below 5, and from Pearson's χ² without continuity correction otherwise; the test used is identified for every term in supplementary Table S1. This rule was adopted because the exposed cohort is a small fraction of a 20-million-case database, so several preferred terms have expected counts far below one and the asymptotic approximation is unreliable. Multiplicity was controlled with the Benjamini–Hochberg procedure within two families, stated in advance: the eleven ocular queries, and the fifteen preferred terms described in Section 3.3; the raw p value is reported alongside the adjusted q. A false-discovery rate q below 0.05 was required for a term to be called significant, and both the unadjusted and adjusted values are given where they matter. The ROR is an effect-size measure, the "at least three cases" rule is a stability threshold, and the q value is the multiplicity criterion; the three are reported separately and are not used interchangeably.

### 2.7 Sensitivity analyses

Three analyses test whether the main result depends on a single definition. First, exposure was restricted to reports naming ethambutol as the primary or secondary suspect drug. Second, the database was split by receipt year at 2016, so that each period carries at least forty optic-neuropathy events, and the optic-nerve contrast was recomputed in each period with that period's own de-duplicated case count as the reference population; this tests stability across reporting eras, not generalisability. Cases whose every receipt date precedes 2004 fall outside both periods (57 of 20,692,683); the year distribution is given in supplementary Table S7. Third, within the antitubercular class, the optic-nerve outcome was a composite defined for this comparison as a report containing at least one of four preferred terms — optic neuropathy, optic neuritis, optic atrophy or toxic optic neuropathy, matched in both spellings — and the proportion of reports carrying it was compared between reports naming rifampicin, isoniazid and pyrazinamide with and without ethambutol, a contrast in which the background regimen is held constant by construction. The ratio of those proportions, with a 95% confidence interval from the Katz log method (standard error computed from the four cell counts), is reported rather than an incidence rate ratio, because the denominator is reports rather than treated patients; the composite was formed for this comparison and is not a pre-specified primary outcome.

Age, sex and reporting region were described for the cohort; no regression model of an ocular event is reported, because coefficients from a reports database cannot be read as patient-level risk factors.

### 2.8 External replication

The optic-nerve comparison was run in JADER and in Canada Vigilance, but the two systems do not supply the same endpoint. JADER provides MedDRA/J terms for the optic-nerve and the non-specific terms alike, so the FAERS contrast can be repeated at term level. The Canadian extract carries a composite of every preferred term containing the string OPTIC (29 such terms appear in the extract) and a system-organ-class count, but no term-level control panel. That composite is a study-specific string match, not a re-implementation of the 45-term query: it includes terms whose clinical meaning differs from drug-induced optic neuropathy, such as imaging terms and surgical procedures, so the Canadian analysis is reported as exploratory and is not treated as an equivalent replication. JADER provides MedDRA/J terms and no English column, so each term was mapped to its Japanese equivalent and the mapping is published in the supplement. Every analysed term had a Japanese equivalent, so no term was excluded for mapping failure. Exposure in JADER used the suspect-drug code, with a sensitivity analysis over all drug roles; Canada Vigilance was read with exposure taken from the ingredient table rather than the product name, so that brand-only entries are captured. The 2×2 construction and the interval were identical to those used in FAERS. Because the systems code suspect drugs differently — 1,798 of 3,483 JADER ethambutol cases name the drug as suspect, a much higher proportion than in FAERS — the comparison is by pattern and by direction, not by the magnitude of the ROR, and case counts are shown alongside every estimate.

### 2.9 Time to onset

Within the de-duplicated ethambutol case set, time to onset was computed as the interval between the therapy start date and the event date, restricted to reports with both dates, a non-negative interval and an interval of at most 3,650 days. Distributions are summarised by median and interquartile range, separately for optic-nerve, other ocular and non-ocular events. The proportion of optic-nerve cases with the fields needed for this analysis is reported, because the subset is defined by completeness rather than by sampling.

### 2.10 Exploratory transcriptomic reanalysis

Public series GSE294687, from the study by Cheng and colleagues [18], profiled human induced pluripotent stem cell-derived retinal ganglion-like cells exposed to ethambutol or vehicle in four paired preparations. The original study analysed these data with a count-based model; the reanalysis here uses a paired test on log-transformed counts per million, and is therefore an exploratory reanalysis with a different method rather than a reproduction of the original differential-expression results. Counts were converted to counts per million from the column sums and log2-transformed after adding one; genes with CPM ≥ 1 in at least four samples were retained. Each gene was tested with a paired t-test across the four ethambutol–vehicle pairs, and Benjamini–Hochberg adjustment was applied across every gene tested; genes were called differentially expressed at q < 0.05. Because the published mechanisms make directional predictions, they were evaluated at gene-set level: the mean log2 fold change across the genes each mechanism implicates, and the number of those genes that changed significantly, are reported together with the verdict.

Two features of the experiment bound its interpretation and are stated with the results: the exposure was 8 mM for 24 hours, which is 330 to 800 times the peak plasma concentration at standard dosage, and the preparation is a monoculture of retinal ganglion-like cells, so microglial and Müller glial contributions cannot be observed. A public TPEN-treated human cardiomyocyte line, AC16 (GSE318912), was used as an empirical zinc-chelation reference; it was analysed unpaired there against paired in GSE294687, and the difference in cell type and design bounds what the correlation can show.

The transcriptomic section is exploratory. It was not pre-registered, the directional predictions were assembled from the published literature rather than fixed in advance of our own data, and no result from it is used as evidence for or against a mechanism in patients.

### 2.11 Software and reproducibility

All analyses were run as standalone, re-runnable Python scripts with recorded software versions and random seeds. The de-duplication map, the 2×2 tables, the query-level results, the preferred-term results, the period split and the fixed-regimen contrast are all exported to a single results file (`results/main_results.json`), from which the tables in this paper are generated, so that no number is transcribed by hand. The code, the derived tables and a data dictionary are available at the repository given in the Statements, under the release tag `v2.0-tads-2026-10-21`, which identifies the commit from which the numbers, tables and figures in this manuscript were generated.


## 3. Results

### 3.1 Case flow and cohort

The 90 quarterly FAERS releases contributed 24,812,425 submitted reports; applying the FDA case-version rule left 20,692,683 de-duplicated cases (Figure 1). Ethambutol appeared in 15,510 of them, of which 9,024 (58.2%) named it as the primary or secondary suspect drug, 1,134 as the primary suspect, and 6,486 as a concomitant medication only. Median age was 50 years (IQR 32–67) among the 12,244 cases with a plausible recorded age, and 6,672 of the 13,921 cases with a recorded sex (47.9%) were female. Four hundred and thirty-two cases (2.8%) reported at least one event within the optic-nerve query. The same exposure definition was applied to the two replication databases, in which 3,483 JADER cases and 965 Canada Vigilance reports named ethambutol (Table 1).

### 3.2 The optic-nerve query stands out among the eleven ocular queries

Across the eleven ocular queries, the optic-nerve query returned the highest reporting odds ratio, 23.51 (95% CI 21.35–25.89) on 432 exposed cases, 5.7 times the next highest point estimate (Figure 2, Table 2). The two estimates are not formally compared, and the ratio is reported as a description of the ordering rather than as a test of their difference. Four queries lay significantly above unity — optic nerve 23.51, ocular infections 4.13, retinal 2.18 and ocular motility 2.02 — three lay significantly below it (glaucoma 0.45, lacrimal 0.24, periorbital and eyelid 0.48), and four were null (lens 1.18, corneal 1.08, conjunctival 0.95, scleral 0.88). The queries covering the ocular surface and anterior segment therefore showed no excess, while the query covering the optic nerve showed the largest one.

The elevation of the ocular-infections query (4.13) is not attributable to the drug on this evidence: ethambutol is an antimycobacterial, and the underlying ocular infection can generate terms of that kind, so confounding by indication and channelling is a more economical explanation than a direct drug effect. The retinal elevation (2.18) is compatible with an effect on retinal ganglion cells, which the optic-nerve terms also describe. The motility elevation (2.02) is not interpreted. All four query-level q values were below 0.005.

### 3.3 The terms driving the query, and the pre-specified controls

Sixteen of the query's 45 narrow terms carried at least one ethambutol case and nine carried three or more; all nine were significant after correction (Figure 3). The evidence is carried by the terms with the largest numbers of cases rather than by the largest ratios. Optic neuropathy gave an ROR of 116.58 (99.36–136.78) on 165 cases and optic neuritis 23.67 (20.19–27.75) on 156 cases. The remaining seven were toxic optic neuropathy (232.95, 178.18–304.56; 63 cases), optic atrophy (20.00, 13.36–29.94; 24), papilloedema (5.97, 3.84–9.26; 20), optic nerve disorder (7.62, 3.96–14.68; 9), optic nerve injury (9.45, 4.71–18.95; 8), visual evoked potentials abnormal (30.30, 9.65–95.18; 3) and optic disc hyperaemia (181.83, 54.42–607.55; 3).

The four pre-specified negative controls showed no positive disproportionality signal: cataract 0.89 (0.65–1.22), conjunctivitis 0.81 (0.45–1.46), dry eye 0.28 (0.15–0.52) and glaucoma 0.28 (0.11–0.75). The two non-specific comparators behaved differently from one another: eye pain was reported less often than expected (0.66, 0.45–0.96), whereas vision blurred showed a modest excess (1.50, 1.28–1.76; 151 cases). This pattern is less consistent with a uniform increase across all ocular reporting, although outcome-specific recognition and coding cannot be excluded, and the excess for vision blurred is reported rather than set aside.

### 3.4 Sensitivity: exposure role and reporting period

Restricting exposure to reports naming ethambutol as the primary or secondary suspect drug increased both estimates, because the cohort is smaller and more specifically exposed: the query rose from 23.51 to 35.01 (370 cases exposed) and optic neuropathy from 116.58 to 191.22 (157 cases) (Figure 4).

Splitting the database by receipt year at 2016 gave 4,316 ethambutol cases among 7,189,907 de-duplicated cases in 2004–2016 and 11,194 among 13,502,719 in 2017–2026, which together account for the whole cohort. The optic-nerve contrast was similar in the two periods: 131.72 (100.43–172.76) on 57 exposed cases and 111.66 (91.61–136.10) on 108. The proportion of ethambutol cases reporting optic neuropathy fell from 1.32% to 0.96%, and the proportion of all other reports carrying the term fell from 0.0102% to 0.0087%, so the ratio between the two was stable while both proportions fell. This analysis is within one database and shares its reporting artefacts; it tests stability across reporting eras, not generalisability. The two periods cover 20,692,626 of the 20,692,683 de-duplicated cases; the remaining 57 carry receipt dates before 2004 and fall outside both periods (supplementary Table S7).

Within the antitubercular class, the one comparison in which the background regimen is held constant — reports naming rifampicin, isoniazid and pyrazinamide, partitioned by whether ethambutol is also named — used a composite optic-nerve outcome defined as a report containing at least one of four preferred terms: optic neuropathy, optic neuritis, optic atrophy or toxic optic neuropathy. The proportion of reports carrying that composite was 1.23% (76/6,167) when ethambutol was named, against 0.64% (7/1,098) when it was not, a ratio of reporting proportions of 1.93 (0.89–4.18). The interval includes unity, the unexposed group is small, and the composite was assembled for this comparison rather than fixed as a primary outcome, so the contrast is reported as a supporting analysis and not as a within-class effect.

### 3.5 Replication in two independent national systems

In JADER, the same direction appeared on a much smaller base (Table 3). Among the 1,798 cases naming ethambutol as the suspect drug, optic neuropathy gave an ROR of 570.96 (413.50–788.37) on 73 exposed cases, toxic optic neuropathy 864.62 (426.37–1,753.36) on 19, optic neuritis 52.20 (35.84–76.04) on 30 and optic atrophy 50.25 (15.44–163.55) on 3; cataract, glaucoma and dry eye were null or below unity in the same analysis. Across all drug roles the optic-neuropathy estimate was 304.24 (220.75–419.30) on 75 cases.

In Canada Vigilance, 965 reports named ethambutol, 21 of which carried at least one preferred term containing OPTIC, giving an ROR of 21.85 (14.13–33.79); restricted to the 460 suspect reports the estimate was 44.63 (28.42–70.10) on 20 cases. That composite is broader than the FAERS query and includes terms of different clinical meaning, so it is read as an exploratory optic-related signal rather than as a repeat of the query. The system-organ-class measure for eye disorders was much weaker, 2.60 (2.12–3.18): the organ-system category pools optic-nerve and non-specific events, and the association lives in the former.

The extract of Canada Vigilance available to us carries the optic-nerve composite and the system-organ-class count, but not a term-level control panel comparable to the FAERS one; the term-level control comparison therefore rests on FAERS (Figure 3) and JADER, and the Canadian contribution is the direction of the optic-nerve contrast. The magnitude of these estimates differs between databases by more than an order of magnitude, and is not compared. JADER codes a much higher proportion of ethambutol reports as suspect than FAERS does (1,798 of 3,483 against 9,024 of 15,510), and the systems differ in reporting culture, in the terms available in their languages and in the size of their denominators. The three systems therefore contribute at different levels. FAERS provides the primary contrast between the eleven ocular queries and the term-level control comparison; JADER provides term-level external support, with its own exposure-role definition and a Japanese-to-English mapping; Canada Vigilance provides a broader, string-matched optic-related composite that points in the same direction but is not an equivalent replication. Cross-system replication therefore applies to the direction of the optic-nerve signal, whereas the full internal-control pattern was examined in one database and, at term level, in a second. Case counts are shown alongside every estimate because a large ratio computed on a handful of cases is not the same finding as a moderate ratio computed on hundreds.

### 3.6 Time to onset

Time from starting ethambutol to the reported event could be computed in 2,446 of the 15,510 ethambutol cases (15.8%). In this analysis an optic-nerve event was defined by the case-level term list (17 preferred terms, supplementary Table S9), which is wider than the 45-term query: 472 cases carried at least one of those terms and 83 had a usable interval, against 2,289 cases in the non-ocular group. The absolute number is therefore not comparable with the 432 exposed cases of the query, which use a different term set. Ocular events as a whole numbered 157, of which 83 were optic-nerve and 74 were other ocular events; that group had a median of 113 days (IQR 38–287), and the primary comparison reported here is optic-nerve against non-ocular events. Median interval was 125 days (IQR 63–293) for optic-nerve events and 33 days (IQR 10–100) for non-ocular events. The remaining 13,064 cases (84.2%) lacked a therapy start date, an event date, or an interval within the accepted range, so the analysis rests on the subset with complete dates and that subset is defined by completeness rather than by sampling.

### 3.7 Exploratory transcriptomic reanalysis

The reanalysis of GSE294687 yielded 15,421 genes, of which 2,083 changed at q < 0.05 between ethambutol and vehicle in the paired design. The exposure was 8 mM for 24 hours, 330 to 800 times the peak plasma concentration at standard dosage, so every statement below refers to a millimolar exposure in a monoculture of retinal ganglion-like cells.

Three mechanisms moved in the direction their published accounts predict, at gene-set level. The NRF2 antioxidant programme was the strongest: NFE2L2 itself rose 1.02 log2 and its targets — HMOX1 (+0.98), GCLM (+0.95), TXNRD1, SRXN1, NQO1, SQSTM1 and FTH1 — moved with it, seven of the ten genes significantly, for a mean of +1.045. The autophagy receptors accumulated (SQSTM1 +1.42, MAP1LC3B +1.03; mean +0.797), a pattern compatible with an altered autophagy-associated response, although transcript levels do not establish autophagic flux, and the respiratory-chain subunits fell (mean −0.272, four of twelve significant).

Two other accounts did not behave as predicted. The ferroptosis account predicts SLC7A11 and GPX4 falling; their transcripts rose, SLC7A11 by 3.80 log2, while the iron-handling genes TFRC (+2.00) and FTH1 (+0.31) rose as that account also predicts. The zinc-chelation account was tested against an empirical reference, a TPEN-treated human cell line (GSE318912): TPEN lowered metallothionein (mean −0.17) and raised the SLC39A importers (+0.33), whereas ethambutol raised metallothionein (+0.31) and left the importers unchanged (+0.04), and the two fold-change vectors correlated at r = +0.07 across the 12,201 genes both experiments measured. The two experiments used different cell types, so that correlation bounds rather than settles the comparison.

None of this establishes a mechanism in patients. The predictions were assembled from the literature rather than fixed before our own data were examined, there is no protein measurement, no genotype and no microglial or Müller glial compartment in the preparation, and the concentration is far above therapeutic exposure. What it does show is that selected transcriptional predictions of the ferroptosis account were not reproduced under these conditions, which is a weaker statement than a refutation and is reported as such.


## 4. Discussion

### 4.1 Principal findings

In 15,510 de-duplicated ethambutol cases drawn from 20.7 million FAERS cases, the ocular reporting disproportion was concentrated in the optic-nerve query: it was the highest of the eleven ocular queries tested on MedDRA's own terms, at 23.51 against 4.13 for the next, and the queries covering the ocular surface and anterior segment were at or below background. Within the query the evidence rested on optic neuropathy and optic neuritis, the two terms with the largest numbers of exposed cases, rather than on the terms with the largest ratios. The optic-nerve-related signal was also observed in JADER, and in Canada Vigilance under a broader string-matched definition; the systems differ in reporters, in the coding of suspect drugs and in reporting culture. The non-specific term contrast was reproduced in FAERS and, for the mapped terms, JADER, whereas Canada Vigilance provided supporting evidence only for the optic-nerve signal. Median time to an optic-nerve event was 125 days, against 33 days for non-ocular events in the same case set.

### 4.2 What this adds to previous work

That ethambutol is associated with optic neuropathy is not new, and the finding that its ocular signal is prominent has been reported before [14]. The contribution here is the internal contrast. Previous pharmacovigilance analyses of these drugs reported signal counts aggregated to system organ class [14] or organised the ocular phenotype by organ-system grouping [15]; in either design, a drug that produces a specific optic-nerve injury and a drug that produces a general increase in ocular reporting look alike. Testing the eleven ocular queries against one another, with the optic-nerve query nominated in advance and with pre-specified non-specific terms as controls, separates those two possibilities within the same reports. The optic-nerve-related reporting signal was observed in all three systems, but the evidence was not equivalent across databases. FAERS provided the primary comparison across eleven ocular queries and the pre-specified term-level controls, while JADER provided term-level external support for the mapped terms. Canada Vigilance showed a directionally consistent signal using a broader, study-specific string-matched composite, rather than an equivalent replication of the primary query or of its internal-control pattern. The contrast is less consistent with a uniform increase across all ocular reporting than a single organ-system count would be, but it does not remove differential recognition and coding of suspected toxicity, which remains the main alternative explanation for the pattern.

The design also changes what can be claimed. A signal concentrated in one anatomical category, reproduced in an independent national system, is a stronger basis for a safety hypothesis than a single elevated organ-system count, and it is the kind of pattern that can be checked in other databases. It is not evidence of incidence, and no proportion in this analysis can be set against a clinical incidence, because the denominator is reports rather than treated patients and stimulated reporting for a well-known adverse effect inflates the numerator.

### 4.3 Reporting bias, indication confounding, and what the controls do and do not show

Spontaneous reporting has no denominator, and under-reporting is substantial and non-random. Three biases are relevant, and they act differently on the main result. Notoriety bias — increased reporting of a known adverse effect — raises the absolute ocular signal but does not by itself produce a contrast between optic-nerve terms and cataract, dry eye or glaucoma, because all of them sit in the same reports. Sharing a database and an exposure definition does, however, not make every reporting bias common to all outcomes: a clinician who already suspects ethambutol toxicity may record the optic-nerve diagnosis precisely and leave a visual complaint uncoded. The comparison narrows the range of explanations; it does not eliminate outcome-specific reporting. Differential coding is the more serious concern: clinicians who suspect ethambutol toxicity may code optic neuropathy more precisely than they code a non-specific complaint, which would concentrate the signal in the optic-nerve terms without any difference in underlying incidence. Indication confounding acts in the opposite direction, inflating the ocular signal as a whole; the elevation of the ocular infections query is the clearest example: it may partly reflect confounding by indication and channelling, including the underlying ocular infection, rather than a direct drug effect.

The controls bound the conclusion in both directions. The four negative-control terms did not show positive disproportionality signals, whereas the non-specific comparators were not uniformly null: eye pain was below unity, but vision blurred showed a modest elevation (1.50, 1.28–1.76). The absence of comparable elevations for the negative-control terms is less consistent with a uniform increase in ocular reporting. The vision-blurred signal, and the possibility of outcome-specific recognition and coding, mean that the internal contrast cannot establish anatomical specificity or exclude reporting bias. It also does not show that the negative-control events are not caused by the drug: a true effect that is small relative to background reporting would not appear. The result is a statement about the shape of the reporting signal, not a toxicity profile. Restriction to suspect-drug reports and the period split change the size of the estimate without changing its direction. The fixed-regimen contrast — rifampicin, isoniazid and pyrazinamide with versus without ethambutol — holds the background regimen constant but rests on a small unexposed group, and its interval includes unity; it is reported for completeness rather than as evidence of a within-class effect.

### 4.4 Limits of the transcriptomic exploration

The transcriptomic reanalysis was included because the mechanisms proposed for this toxicity make directional predictions that can be checked in human cells, not because it can resolve the mechanism. Three limits are decisive for how it should be read. The exposure was 8 mM for 24 hours, 330 to 800 times the peak plasma concentration at standard dosage, so the experiment models an acute millimolar insult rather than the months of therapeutic exposure over which the clinical toxicity develops. The preparation is a monoculture of retinal ganglion-like cells, so any contribution from microglia, Müller glia or the retinal vasculature is invisible to it. And the predictions were assembled from the published literature after the data were in hand, so the analysis is exploratory in the strict sense: it can generate hypotheses, and it can show that a predicted direction was not observed, but it cannot confirm or refute a mechanism operating in patients. The antioxidant, autophagic and oxidative-phosphorylation programmes moved in the predicted directions; the ferroptosis account [19] predicted a fall in SLC7A11 and GPX4 and their transcripts rose, so the appropriate conclusion is that selected transcriptional predictions were not reproduced under these conditions, not that ferroptosis has been excluded.

### 4.5 Clinical and regulatory implications

The practical value of a reporting signal of this shape is that it identifies where to look, and it should be read as a reason for clinical vigilance rather than as a basis for a screening schedule. Ethambutol optic neuropathy is managed by stopping the drug, and the damage becomes irreversible once atrophy is established, so detection before that point is what matters. In these data the reported time to onset had a median of 125 days, with 11.0% of optic-nerve events reported within 30 days of starting treatment and 23.2% within 60 days. That median comes from the 17-term case-level definition and the 83 reports with complete dates, not from the 432-case query, and it describes reports with complete dates rather than the incidence we would see in a monitored cohort: reports are a selected subset, the date of onset is recorded retrospectively, and no examinations that were not performed can appear in it. It is therefore consistent with a baseline examination and an early first follow-up, and with the clinical literature in which structural measures predict visual outcome better than initial acuity [10,11,12,13], but it cannot set the interval, and we do not derive one from it.

For regulators and for those who build pharmacovigilance workflows, the transferable point is methodological. The use of pre-specified MedDRA queries and ocular comparators provides a structured assessment of whether disproportionality is uniform across ocular outcomes. It cannot exclude outcome-specific recognition and coding of suspected toxicity. The same design can be applied to other drugs with a suspected site-specific toxicity, and it requires no data beyond what spontaneous reporting systems already publish.

Two designs would move the question forward, and neither can be built from spontaneous reports. A prospective cohort with protocolised baseline and interval ophthalmic assessment — optical coherence tomography and visual field testing, with the examination schedule fixed in advance rather than triggered by symptoms — would give both an incidence and the detection window. A record-linkage study of prescription data to incident optic-neuropathy diagnoses, with renal function and dose as covariates, would test the exposure–response relationship that a reporting database cannot address.

### 4.6 Conclusion

Across three spontaneous-reporting systems, ethambutol reports showed an optic-nerve-predominant pattern in FAERS and an optic-nerve-related signal in JADER and Canada Vigilance; the internal-control comparison was available in FAERS and, at term level, in JADER. These findings characterise a safety signal rather than the incidence or causal effect of ethambutol. The pattern is consistent with a site-specific toxicity and with the clinical literature on ethambutol optic neuropathy, but differential reporting and residual confounding cannot be excluded, and the transcriptomic exploration does not establish a mechanism.

## Statements and Declarations

**Ethics approval and consent to participate.** Not applicable. The study used publicly available,
de-identified aggregate data from pharmacovigilance databases and public gene-expression series. No
human participants were recruited, no identifiable information was accessed, and no ethics
approval was therefore required.

**Consent for publication.** Not applicable. No individual person's data are reported.

**Availability of data and materials.** FAERS quarterly ASCII releases are available from the U.S.
Food and Drug Administration
(https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html); JADER from the Pharmaceuticals
and Medical Devices Agency of Japan; Canada Vigilance from Health Canada (cvponline); GSE294687 and
GSE318912 from NCBI GEO. The derived tables that support the findings — the de-duplication map, the
2×2 tables, `results/main_results.json` and the code that generates every table and figure — are
available at https://github.com/Bowen2485/ethambutol-ocular-toxicity/tree/v2.0-tads-2026-10-21
(release tag `v2.0-tads-2026-10-21`) under an MIT licence.

**Code availability.** All analysis scripts, the data dictionary and the results file are in the
repository named above, under the same release tag. The scripts record the software versions and
random seeds used.

**Funding.** This research received no specific grant from any funding agency in the public,
commercial, or not-for-profit sectors.

**Declaration of conflicting interests.** The authors declare no competing interests.

**Author contributions.** Bowen Shi: conceptualisation, methodology, software, formal analysis,
writing — original draft. Jing Yan: conceptualisation, supervision, writing — review and editing.
Zhengzheng Wu: supervision. Siyuan Yang: writing — review and editing. Yaqin Tan: investigation.
Xuan Wang: visualisation. All authors read and approved the final manuscript.

**Acknowledgements.** None.

**ORCID.** Bowen Shi, 0009-0001-6900-1779.


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

**Figure 3.** Preferred terms within the optic-nerve query, alongside the pre-specified negative
controls and the non-specific ocular comparators. Terms with fewer than three exposed cases are
not plotted. Conventions as in Figure 2.

**Figure 4.** Sensitivity of the optic-nerve estimate to exposure role and reporting period. The
upper four rows compare the preferred term and the query under all-role and suspect-only exposure;
the lower two split the cohort by receipt year at 2016. Conventions as in Figure 2.


## Tables

Table 1. Data sources and exposed cohorts.

| Source | Period | Records | Records naming ethambutol | Exposure definition |
|---|---|---|---|---|
| FAERS quarterly ASCII releases | 2004Q1–2026Q2 (90 quarters) | 24,812,425 submitted; 20,692,683 de-duplicated cases | 15,510 (9,024 as primary or secondary suspect) | Any drug record, case-insensitive substring |
| JADER | September 2026 release | 1,054,239 cases | 3,483 (1,798 as suspect) | Suspect drug code; all roles in sensitivity |
| Canada Vigilance | Extract of 31 May 2026 | 1,266,430 reports | 965 (460 as suspect) | Ingredient table; all roles in main |

Table 2. The eleven ocular Standardised MedDRA Queries (narrow sets, MedDRA 29.0), ethambutol against all other de-duplicated reports.

| Query | Exposed cases | Cases in database | ROR | 95% CI | P | q |
|---|---|---|---|---|---|---|
| Optic nerve disorders | 432 | 25,600 | 23.51 | 21.35–25.89 | <1e-300 | <1e-300 |
| Ocular infections | 127 | 41,375 | 4.13 | 3.47–4.92 | 9.4e-67 | 5.2e-66 |
| Retinal disorders | 164 | 101,220 | 2.18 | 1.87–2.54 | 3.4e-24 | 1.3e-23 |
| Ocular motility disorders | 62 | 41,091 | 2.02 | 1.57–2.59 | 1.8e-08 | 4e-08 |
| Lens disorders | 60 | 67,857 | 1.18 | 0.92–1.52 | 0.1992 | 0.27 |
| Corneal disorders | 18 | 22,172 | 1.08 | 0.68–1.72 | 0.7345 | 0.81 |
| Conjunctival disorders | 70 | 98,182 | 0.95 | 0.75–1.20 | 0.6746 | 0.81 |
| Scleral disorders | 3 | 4,537 | 0.88 | 0.28–2.74 | 1 | 1 |
| Periorbital and eyelid disorders | 29 | 79,763 | 0.48 | 0.34–0.70 | 6.6e-05 | 0.00012 |
| Glaucoma | 13 | 38,632 | 0.45 | 0.26–0.77 | 0.002987 | 0.0047 |
| Lacrimal disorders | 15 | 83,295 | 0.24 | 0.14–0.40 | 1.8e-09 | 4.9e-09 |

P, two-sided P value from Pearson’s χ² test without continuity correction, except for Scleral disorders, where Fisher’s exact test was used because the smallest expected cell count was below 5. Term-level estimates for the nine optic-nerve preferred terms with at least three exposed cases and the six pre-specified controls are in Supplementary Table S1. q, Benjamini–Hochberg adjusted across the eleven ocular queries.

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

ROR, reporting odds ratio. The Canadian outcome is an exploratory composite of every preferred
term containing the string OPTIC (29 such terms appear in the extract); it is not the
45-term query and includes terms of different clinical meaning. A total of
1,308 reports in the full Canada Vigilance database carried at least one of these
terms, and 21 of those reports named ethambutol. The JADER rows report the term-specific
estimate; cataract, glaucoma and dry eye were null or below unity in the same analysis. The two
FAERS period rows use that period's own de-duplicated case count as the reference population.
Estimates are not compared across systems: the proportion of reports naming the drug as suspect
differs by system.

Table 4. Pre-specified negative controls (cataract, dry eye, glaucoma, conjunctivitis) and
non-specific comparators (eye pain, vision blurred) in FAERS.

| Term | Exposed cases | Cases in database | ROR | 95% CI | q |
|---|---|---|---|---|---|
| Cataract | 39 | 58,616 | 0.89 | 0.65–1.22 | 0.48 |
| Dry eye | 10 | 47,855 | 0.28 | 0.15–0.52 | 2.3e-05 |
| Eye pain | 27 | 54,555 | 0.66 | 0.45–0.96 | 0.034 |
| Glaucoma | 4 | 19,045 | 0.28 | 0.11–0.75 | 0.0081 |
| Conjunctivitis | 11 | 18,170 | 0.81 | 0.45–1.46 | 0.48 |
| Vision blurred | 151 | 135,063 | 1.50 | 1.28–1.76 | 1.7e-06 |


## References

1. Chamberlain PD, Sadaka A, Berry S, Lee AG. Ethambutol optic neuropathy. Curr Opin Ophthalmol. 2017;28(6):545-551. doi:10.1097/icu.0000000000000416.
2. Ambika S, Lakshmi KP, Gopal M, Noronha OV. Visual outcomes of toxic optic neuropathy secondary to Ethambutol: A retrospective observational study from India, an endemic country. Indian J Ophthalmol. 2022;70(9):3388-3392. doi:10.4103/ijo.ijo_2996_21.
3. An HR, Lee BJ, Moon Y. Visual Recovery Time in Patients with Ethambutol-induced Toxic Optic Neuropathy. Korean J Ophthalmol. 2024;38(2):91-97. doi:10.3341/kjo.2023.0095.
4. Singh P, Karkhur S, Verma V. Ethambutol-Induced Optic Neuropathy: A Retrospective Study of Incidences and Risk Factors. Cureus. 2025;17(2):e79160. doi:10.7759/cureus.79160.
5. Chaitanuwong P, Srithawatpong S, Ruamviboonsuk P, Apinyawasisuk S, Watcharapanjamart A, Moss HE. Incidence, risk factors and ophthalmic clinical characteristic of ethambutol-induced optic neuropathy: 7-year experience. Front Ophthalmol (Lausanne). 2023;3:1152215. doi:10.3389/fopht.2023.1152215.
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
17. Langan SM, Schmidt SA, Wing K, Ehrenstein V, Nicholls SG, Filion KB, et al. The reporting of studies conducted using observational routinely collected health data statement for pharmacoepidemiology (RECORD-PE). BMJ. 2018;363:k3532. doi:10.1136/bmj.k3532.
18. Cheng HC, Wong YH, Wang AG, Chen SW, Yang YL, Juan HC, et al. Müller glia-mediated protection of retinal ganglion cells from ethambutol-induced neurotoxicity through brain-derived neurotrophic factor. Cell Commun Signal. 2025;23(1):474. doi:10.1186/s12964-025-02478-4.
19. Li Q, Ge W, Zhang Y, Xu Q, Xu J, Zhang Y, et al. Ethambutol induces optic neuropathy through SDHB-mediated ferroptosis in retinal ganglion cells via Smad4 pathway. Hum Cell. 2026;39(2):37. doi:10.1007/s13577-025-01342-4.
