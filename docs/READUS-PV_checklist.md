# READUS-PV checklist — completed

Manuscript: *Optic-nerve-predominant adverse-event reporting with ethambutol: a multi-database
pharmacovigilance study with exploratory transcriptomic analysis*

Checklist: READUS-PV (Fusaroli M, et al. Drug Saf. 2024;47(6):575-584), the 32 recommendations in
14 items, downloaded from the statement's site on 2026-10-21. Section numbers refer to the
manuscript in `manuscript/TADS_manuscript.md` and to the PDF in
`submission/tads/Ethambutol_TADS_manuscript.pdf`.

| # | Recommendation (abridged) | Where reported | How it is addressed |
|---|---|---|---|
| 1a | Identify the study as a disproportionality analysis; name the data type and database(s) | Title | "…a multi-database pharmacovigilance study"; abstract names FAERS, JADER and Canada Vigilance and states the design |
| 1b | Name the adverse event(s) and drug(s) under study | Title | Ethambutol; optic-nerve adverse-event reporting |
| 2a | Describe the drug and its use, the event and its frequency, and existing knowledge | §1 ¶1–2 | Ethambutol as first-line antitubercular therapy; optic neuropathy phenotype; published frequencies (0.28–0.5%, 0.9%, 6.5%, 46% of eyes) with sources |
| 2b | State the rationale for the analysis | §1 ¶3–4 | Existing FAERS/VigiBase work reports organ-system signal counts without internal controls; the analysis tests whether the signal is optic-nerve-specific |
| 2c | Explain why ICSR databases and disproportionality are suitable | §1 ¶3–4 | Spontaneous reports are the only source at this scale; the internal query-vs-query contrast is what ICSRs can support, and its limits are stated |
| 3 | State specific objectives, naming event, drug and reference group, and any pre-specified hypothesis | §1 ¶4, §2.5 | Primary outcome = Optic nerve disorders narrow SMQ; reference = all other de-duplicated reports; eleven ocular queries nominated in advance; pre-specified controls |
| 4a | Identify the design and data type | §2.1 | "Retrospective pharmacovigilance study of disproportionality in spontaneous adverse-event reports" |
| 4b | Outline the whole design including primary and sensitivity analyses | §2.1, §2.7, Figure 1 | One designated main specification; three sensitivity analyses named (suspect role, reporting period, fixed-regimen comparison); replication; exploratory transcriptome |
| 5a | Database name, custodian, coverage, coding thesaurus | §2.2, Table 1 | FDA FAERS (2004Q1–2026Q2, 90 quarters), PMDA JADER (Sep 2026), Health Canada cvponline (31 May 2026); MedDRA 29.0 |
| 5b | Extraction dates and all pre-processing, transformation and exclusions | §2.2–2.3, Figure 1 | Release dates given per system; case-version de-duplication rule (latest FDA_DT per CASEID) and the numbers removed |
| 6a | Study population and any restriction | §2.3–2.4, §3.1, Table 1 | De-duplicated FAERS cases 2004Q1–2026Q2; ethambutol anywhere in the drug records, any role in the main analysis |
| 6b | Nature and meaning of key variables | §2.3–2.5 | Case version, drug role (PS/SS/concomitant), PT, narrow SMQ set, receipt year, onset interval |
| 6c | Justify any grouping of drugs or events; state the role considered | §2.4–2.5, §2.7 | Exposure from the drug-name fields (drugname, prod_ai) with a single-token substring match; any role in main, suspect-only as sensitivity; events grouped by MedDRA's own narrow query sets, not by a list assembled here; queries overlap and are not claimed exhaustive. The time-to-onset analysis additionally used a 17-term case-level definition, provided in Supplementary Table S9 |
| 6d | Any additional data source, its type, and how it interacts with the ICSRs | §2.10 | Public transcriptome series GSE294687 and GSE318912, used only as an exploratory adjunct and never pooled with the reporting data |
| 7a | Descriptive analyses: variables, tests, thresholds | §2.6, §3.1 | Counts and proportions; demographics; two-sided Fisher exact test where the smallest expected count is below 5 and Pearson χ² without continuity correction otherwise; BH within two stated families |
| 7b | Disproportionality measure(s) and signal threshold, with rationale | §2.6 | ROR with Woolf 95% CI is the only signal measure; signal = lower CI > 1 and ≥3 exposed cases; q < 0.05 as the multiplicity criterion, with the raw p reported alongside |
| 7c | Sensitivity analyses and control of confounding | §2.7, §3.4, Figure 4 | Suspect-role restriction; receipt-year split at 2016; fixed-regimen comparison (RIF+INH+PZA ± ethambutol); the fixed-regimen contrast is the only within-class comparison quoted as evidence |
| 7d | Case-by-case analysis variables and methods, if performed | — | Not performed; stated as a limitation of the design rather than an omission |
| 7e | Statistical methods for other data sources | §2.8, §2.10 | Same 2×2 construction and interval in JADER and Canada Vigilance; paired test on log2 CPM and gene-set summaries for the transcriptome |
| 8a | Number of reports at each stage, with reasons for exclusion | §3.1, Figure 1, Table 1 | 24,812,425 submitted → 20,692,683 de-duplicated → 15,510 ethambutol → 9,024 suspect; replication counts in Table 1 |
| 8b | Key demographic and clinical characteristics of cases | §3.1 | Median age 50 years (IQR 32–67; 12,244 with a plausible value); 6,672/13,921 with a recorded sex (47.9%) female |
| 9 | All results with confidence intervals, including sensitivity analyses | §3.2–3.5, Tables 2–4, Figures 2–4 | Every estimate carries a 95% CI and the exposed case count |
| 10 | Case-by-case analysis results and causality assessment, if applicable | — | Not performed; no causality assessment is claimed |
| 11 | Discuss key results against the objectives and the literature; separate expected from emerging findings | §4.1–4.2 | The drug–optic neuropathy association is treated as expected; the increment claimed is the internal contrast and its replication |
| 12a | External validity to the general population | §4.3 | Reporting populations are not patient populations; the absence of a denominator and differential coding are discussed |
| 12b | Relevance to clinical practice | §4.5 | Onset distribution and its implication for baseline and early follow-up |
| 12c | Propose further study designs | §4.5 | Prospective cohort with protocolised ophthalmic assessment; record linkage of prescriptions to incident diagnoses |
| 13 | General and specific limitations, including that disproportionality cannot prove causation or measure incidence; confounding and reporting bias, and mitigation | §4.3–4.4, §4.6 | Notoriety bias, differential coding, indication confounding (ocular infections), absence of a denominator; transcriptome limits (8 mM/24 h, monoculture, post-hoc predictions) |
| 14a | Funding source and the role of funders | Statements | No specific funding |
| 14b | Commercial and intellectual conflicts of interest | Statements | None declared |
| 14c | Institutional approval needed or granted | Statements | Ethics approval not required; de-identified public data |
| 14d | Data availability, code availability including software versions, protocol registration | §2.11, Statements | Repository with code and derived tables; scripts record software versions and seeds; no registration — the analysis plan is described in Methods and the one main specification is named |

## Items not met, stated rather than implied

- **7d and 10 (case-by-case analysis and causality assessment).** No individual case review was
  performed. The design cannot support a causality assessment, and none is claimed.
- **14d (protocol registration).** The analysis was not prospectively registered. The consequence
  is stated where it matters: the transcriptomic predictions are labelled post hoc, and the SMQ and
  control sets are described as nominated in advance of the analysis but after the data were
  available, which is weaker than a registered protocol.
