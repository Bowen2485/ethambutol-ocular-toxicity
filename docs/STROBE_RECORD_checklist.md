# STROBE / RECORD-PE reporting checklist

**Manuscript:** Ocular toxicity of ethambutol in 20.3 million FAERS cases:
pharmacovigilance, network toxicology, molecular docking and genetic interrogation

**Design:** Retrospective pharmacovigilance disproportionality study with
integrated computational mechanism analysis.

**Checklists applied:**
- STROBE (Strengthening the Reporting of Observational Studies in Epidemiology),
  for the case-level and genetic components;
- RECORD-PE (REporting of studies Conducted using Observational Routinely
  collected health Data, PharmacoEpidemiology extension), for the
  pharmacovigilance component.

---

## A. RECORD-PE items specific to routinely collected data

| # | Item | Where addressed | Status |
|---|---|---|---|
| R1.1 | Title/abstract states the data source (FAERS) and the study design | Title; Abstract | ✅ |
| R1.2 | Data sources and access described | Methods 2.2 (FDA quarterly ASCII releases, `fis.fda.gov`) | ✅ |
| R1.3 | Data linkage performed | None — single-source study; stated explicitly | ✅ |
| R2.1 | Study population defined by data source, eligibility, exclusions | Methods 2.2–2.3 | ✅ |
| R3.1 | All codes/algorithms used to define exposures reported | Methods 2.3 (`drugname`, `prod_ai`, case-insensitive substring) | ✅ |
| R3.2 | All codes used to define outcomes reported | Methods 2.3 (73 MedDRA PTs; full list in `data/derived/ocular_terms.csv`) | ✅ |
| R5.1 | Completeness of data documented | Methods 2.2; Results 2.1 (89/90 quarters usable; 2026Q2 archive corrupt) | ✅ |
| R6.1 | Data cleaning and validation described | Methods 2.2 (case-version de-duplication) | ✅ |
| R7.1 | Negative-control / specificity analysis reported | Results 3.2 (non-signal ocular terms listed) | ✅ |
| R8.1 | Software used, with version numbers | Methods 2.9 | ✅ |
| R9.1 | Data access / reproducibility statement | Data availability section; all scripts in `src/` | ✅ |

---

## B. STROBE items

| # | Item | Where addressed | Status |
|---|---|---|---|
| 1a | Title/abstract indicate design | Title, Abstract | ✅ |
| 1b | Structured abstract with key numbers | Abstract | ✅ |
| 2 | Scientific background and rationale | Introduction ¶1–5 | ✅ |
| 3 | Objectives stated | Introduction final ¶ | ✅ |
| 4 | Study design stated early | Methods 2.1 | ✅ |
| 5 | Setting, locations, relevant dates | Methods 2.2 (FDA FAERS, 2004Q1–2026Q2) | ✅ |
| 6a | Eligibility criteria, sources, selection methods | Methods 2.2–2.3 | ✅ |
| 6b | Case-cohort / matching criteria | n/a (whole-database design) | ✅ |
| 7 | Variables: outcomes, exposures, predictors, confounders | Methods 2.3, 2.4, 2.6 | ✅ |
| 8 | Data sources and measurement for each variable | Methods 2.2–2.6 | ✅ |
| 9 | Bias addressed | Discussion 4.6 (spontaneous reporting, notoriety bias, under-reporting) | ✅ |
| 10 | Study size and how it was arrived at | Whole-database census; Methods 2.2 | ✅ |
| 11 | Quantitative variables and how handled | Methods 2.4 (age harmonised across FAERS age codes) | ✅ |
| 12a | Statistical methods including confounder adjustment | Methods 2.4–2.5 | ✅ |
| 12b | Subgroup and interaction analyses | Methods 2.6 (two pre-specified sensitivity analyses) | ✅ |
| 12c | Missing-data handling | Methods 2.4 (age-missingness indicator retained) | ✅ |
| 12d | Loss to follow-up / case-version handling | Methods 2.2 (de-duplication protocol) | ✅ |
| 12e | Sensitivity analyses | Methods 2.6 | ✅ |
| 13a–13c | Participants / flow | Figure 1 (case-selection flow) | ✅ |
| 14a–14c | Descriptive data | Results 3.1, Table 1 | ✅ |
| 15 | Outcome data / numbers | Results 3.2–3.5, Tables 2–7 | ✅ |
| 16a–16c | Main results, CIs, relative and absolute measures | Results 3.2–3.6 | ✅ |
| 17 | Other analyses | Results 3.3 (time to onset), 3.4 (regression) | ✅ |
| 18 | Key results summarised with reference to objectives | Discussion 4.1 | ✅ |
| 19 | Limitations | Discussion 4.6 | ✅ |
| 20 | Interpretation, comparison with other studies | Discussion 4.2–4.5 | ✅ |
| 21 | Generalisability | Discussion 4.5–4.6 | ✅ |
| 22 | Funding | To be inserted by the authors | ⬜ |
| 23 | Data availability | Data availability statement | ✅ |

---

## C. Genetic-analysis items (STROBE-MR alignment, for the MR subsection)

| Item | Requirement | Where addressed | Status |
|---|---|---|---|
| 1 | MR design stated; three core assumptions addressed | Methods 2.7 | ✅ |
| 2 | Data sources with ancestry, sample size, phenotype definitions | Methods 2.7; `tables/Table8_mr.csv` | ✅ |
| 3 | Instrument selection and LD clumping described | Methods 2.7 (p < 5×10⁻⁸; API clumping, r² 0.001, 10 Mb) | ✅ |
| 4 | Harmonisation of effect alleles | Methods 2.7; `harmonise()` in `src/mr_analysis.py` | ✅ |
| 5 | Estimators and sensitivity analyses | Methods 2.7 (Wald, IVW-RE, MR-Egger, weighted median, Cochran Q, Steiger) | ✅ |
| 6 | **Explicit statement that a drug-exposure MR was not attempted, with reasons** | Methods 2.7 + Discussion 4.6 | ✅ |
| 7 | Software and versions | Methods 2.9 | ✅ |

---

## D. Statements of what was deliberately NOT done

These are recorded because their absence is material to interpretation.

1. **No drug-exposure Mendelian randomisation.** Ethambutol is an environmental
   exposure; no "ethambutol use" GWAS exists; no cis-region variant in the
   candidate panel reached genome-wide significance for optic neuropathy in
   FinnGen. An instrument built from non-significant, outcome-derived variants
   would be both underpowered and circular. Reported in Methods 2.7 and
   Discussion 4.6.
2. **No claim of incidence.** FAERS has no exposure denominator; the proportions
   reported are proportions of *reports*, not risks.
3. **No claim that docking predicts biological activity.** Docking scores are
   reported as a prioritisation tool, with the failed redocking control
   (DHFR/methotrexate, RMSD 5.86 Å) disclosed.
4. **No claim that the mechanism network represents direct drug targets.**
   Open Targets holds no human target record for ethambutol (it inhibits
   mycobacterial arabinosyltransferases), so the network is a *downstream effect*
   network reconstructed from literature and phenotype data.
5. **No TCM clinical recommendation.** No study evaluating a TCM intervention in
   an ethambutol ocular toxicity model was identified; the candidate formulae are
   stated explicitly as untested hypotheses.
