
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
