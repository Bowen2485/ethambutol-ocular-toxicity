# Optic-nerve-predominant adverse-event reporting with ethambutol: a multi-database pharmacovigilance study with exploratory transcriptomic analysis

**Running title:** Optic-nerve-predominant reporting with ethambutol

**Authors:** Bowen Shi¹ (ORCID 0009-0001-6900-1779), Jing Yan¹*, Zhengzheng Wu¹, Siyuan Yang¹, Yaqin Tan¹, Xuan Wang¹

**Affiliation:** ¹ Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China

**Corresponding author:** Jing Yan, Eye Hospital, China Academy of Chinese Medical Sciences, 33 Lugu Road, Shijingshan District, Beijing 100040, China. Email: 20200121047@bucm.edu.cn

---

## Abstract

**Background.** Ethambutol's ocular signal is well recognised; whether reporting is concentrated in the optic nerve rather than generally ocular is untested against MedDRA's queries.

**Objectives.** To test for an optic-nerve-predominant pattern across ocular queries and its replication in independent systems.

**Design.** Retrospective disproportionality analysis with replication and exploratory transcriptomics.

**Methods.** All 90 quarterly FDA Adverse Event Reporting System (FAERS) releases (2004Q1–2026Q2) were de-duplicated by case version; in 15,510 ethambutol cases we computed reporting odds ratios (ROR) for the eleven ocular Standardised MedDRA Queries (narrow, MedDRA 29.0) with Benjamini–Hochberg control and pre-specified non-specific terms; exposure role, period and a fixed-regimen contrast were sensitivity analyses; the pattern was tested in JADER and Canada Vigilance.

**Results.** The optic-nerve query had the highest ROR (23.51, 95% CI 21.35–25.89; 432 cases); four showed positive signals, three were below 1 and four spanned 1. Optic neuropathy (165; 116.58, 99.36–136.78) and optic neuritis (156; 23.67, 20.19–27.75) carried it. Negative controls showed no positive signal; vision blurred did (1.50, 1.28–1.76). JADER showed a term-level signal (optic neuropathy 570.96, 413.50–788.37); Canada Vigilance a broader string-matched composite (21.85, 14.13–33.79); the non-specific comparison was possible in FAERS and JADER only. Median onset among dated reports: 125 days (optic-nerve) versus 33 (non-ocular). Transcriptomics did not reproduce selected ferroptosis predictions.

**Conclusion.** Ethambutol reports showed an optic-nerve-predominant pattern in FAERS and an optic-nerve-related signal in JADER and Canada Vigilance: a safety signal, not an incidence or causal effect.

**Plain Language Title.** How side-effect reports describe eye problems with the tuberculosis drug ethambutol

**Keywords.** ethambutol; optic neuropathy; pharmacovigilance; disproportionality analysis; MedDRA; spontaneous reporting

---

## Plain Language Summary

Ethambutol is one of the standard drugs used to treat tuberculosis. It can damage the optic nerve, and patients may lose vision if the drug is continued after the damage begins. How often this happens is uncertain, because estimates depend on how closely patients are examined; published figures range from less than one in a hundred to about six in a hundred.

Doctors send reports of suspected side effects to national databases. We studied these reports to ask a narrower question than "how common is the damage": when ethambutol is named in a report that mentions an eye problem, is the problem usually something specific to the optic nerve, or is it any eye complaint at all? Using a standard dictionary that sorts eye problems into eleven categories, one of which is the optic nerve, we found that the optic-nerve category stands out far more than the others, and that everyday complaints such as cataract, dry eye and eye pain are not reported more often than expected. A similar optic-nerve signal appeared in databases from Japan and Canada, although the Canadian data do not allow the same term-by-term comparison of everyday eye complaints.

Reports of side effects cannot tell us how many people are actually harmed, and they are influenced by which side effects doctors recognise and choose to report. What they can show is a consistent pattern across countries. What the pattern supports is vigilance rather than a timetable: clinicians should ask about and watch for visual symptoms in people taking ethambutol and follow existing clinical guidance on monitoring. This study did not test any particular follow-up interval, and the 125-day median describes reports with complete dates, not the point at which damage usually begins.

---

## 1. Introduction

Ethambutol has been part of first-line antitubercular chemotherapy since the 1960s, and it is the drug in that regimen whose toxicity most often forces a change of treatment. Its characteristic adverse effect is a bilateral, painless, slowly progressive optic neuropathy that preferentially damages the papillomacular bundle, producing loss of visual acuity, dyschromatopsia, central or caecocentral scotomas and, when the drug is continued, optic atrophy [1,2,3].

The frequency reported for this toxicity depends on how carefully patients are looked for. Retrospective chart review yields 0.28–0.5% [4,5], a nationwide insurance cohort gives a cumulative incidence of 0.9% [6], and prospective multidisciplinary screening with visual evoked potentials and optical coherence tomography gives 6.5% [7], with subclinical injury in up to 46% of eyes in one six-month study [8]. The variability is itself the clinical problem: a toxicity that is common in prospective series and rare in chart review is one that is not being looked for. Recovery is incomplete and slow, with 50–77% of eyes improving after withdrawal over a mean of about 15 months and retinal nerve fibre layer thinning persisting despite visual recovery [2,3,9], so the case for early detection rests on the assumption that the injury can be recognised before it is irreversible.

At the scale needed to characterise a reporting pattern, the evidence comes from spontaneous reporting systems. FAERS has been mined for these drugs before: Mao and Ou applied five signal-detection methods to the four first-line antitubercular drugs and reported that ethambutol carried more eye-disorder signals than the other three, but their analysis drew on 978 ethambutol reports from 2021Q1 to 2025Q3 and reported signal counts by system organ class, without multiplicity control, within-class comparators or control terms [14]. Pharmacovigilance based on VigiBase has likewise been organised by organ-system grouping rather than by term-level disproportionality against comparators [15]. Neither design can distinguish a signal concentrated in the optic nerve from a general increase in ocular reporting for a drug that clinicians already associate with eye problems.

The question this study addresses is therefore deliberately narrow: among ethambutol reports, is the reporting disproportion concentrated in the optic-nerve phenotype relative to the other ocular phenotypes, and does that pattern reproduce in other national systems? We pre-specified the eleven ocular Standardised MedDRA Queries, so that the comparison of the optic-nerve query against the rest does not depend on a term list assembled after the results were seen. We describe the preferred terms that drive the optic-nerve query, test the pattern against pre-specified non-specific ocular terms and in sensitivity analyses, and replicate it in the Japanese JADER and Canada Vigilance databases. A reanalysis of a public human retinal ganglion-like cell transcriptome is reported as a short exploratory adjunct; it is not used to establish a mechanism.

Throughout, the estimates are disproportionality measures in a spontaneous-reporting database. They describe how often a term is reported with the drug relative to other reports, not how often the adverse effect occurs in treated patients, and they cannot establish a causal effect. The analyses were designed and are reported within that boundary.
