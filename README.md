# Ethambutol and optic-nerve adverse-event reporting

Analysis code and derived results for a multi-database pharmacovigilance study of ethambutol,
reported as:

> **Optic-nerve-predominant adverse-event reporting with ethambutol: a multi-database
> pharmacovigilance study with exploratory transcriptomic analysis**

The manuscript is `manuscript/TADS_manuscript.md`; the review PDF is
`submission/Ethambutol_TADS_manuscript.pdf`; the supplementary tables are
`submission/Supplementary_Tables.xlsx`.

## What the study asks

Ethambutol is a first-line antitubercular drug whose optic-nerve toxicity is long established, so
the question is not whether the signal exists. It is whether the ocular signal is *concentrated in
the optic nerve* rather than being part of a general increase in ocular reporting, and whether
that pattern reproduces in other national reporting systems. Eleven ocular MedDRA queries are
nominated in advance and compared against one another inside the same reports, with pre-specified
non-specific terms as controls.

## Data and current results

| Quantity | Value |
|---|---|
| FAERS releases | 90 quarterly ASCII releases, 2004Q1-2026Q2 |
| Submitted reports | 24,812,425 |
| De-duplicated cases | 20,692,683 |
| Cases naming ethambutol | 15,510 (9,024 as primary or secondary suspect) |
| Optic-nerve query | 432 exposed cases, ROR 23.51 (21.35-25.89) |
| Optic neuropathy | 165 exposed cases, ROR 116.58 (99.36-136.78) |
| Optic neuritis | 156 exposed cases, ROR 23.67 (20.19-27.75) |
| Replication | JADER (optic neuropathy 570.96, 413.50-788.37) and Canada Vigilance (21.85, 14.13-33.79) |

## Reproducing the numbers

One script rebuilds every number in the paper from the warehouse:

    python src/build_main_results.py      # writes results/main_results.json, main_smq.csv, main_pt.csv

The period-split sensitivity is recomputed with each period's own denominator by

    python src/audit_period_and_strict.py

The figures, the manuscript tables and the supplementary workbook are generated from
`results/main_results.json`:

    python src/make_figures_tads.py
    python src/build_tads_manuscript.py
    python src/build_tads_pdf.py
    python src/build_supplement.py

`src/audit_tads.py` checks the assembled paper: citations against the reference list, abstract and
main-text length, placeholders, and the headline numbers against the results file.

## Important correction recorded here

An earlier version of the period-split sensitivity used the whole-database case count in the
reference cell of each period's 2x2 table, which overstated both periods (379.28 and 171.17
instead of 131.72 and 111.66). The corrected values, and the period denominators they rest on, are
in `results/audit_period_strict.json` and `results/main_results.json`.

Two preferred terms exist in `reac` in two spellings (`Optic neuropathy` and `OPTIC NEUROPATHY`);
an analysis that matched only one spelling counted 151 rather than 165 exposed cases. All counts in
this repository match both spellings.

## Data dictionary

`results/main_results.json` contains:

| Key | Meaning |
|---|---|
| `N` | de-duplicated FAERS cases |
| `n_ethambutol`, `n_ethambutol_suspect` | cases naming the drug, any role / as PS or SS |
| `case_flow` | counts at each step of the flow diagram |
| `smq` | one object per ocular query: narrow-term count, exposed cases, database cases, ROR, CI, q, suspect-only estimate |
| `pt` | one object per preferred term: group (optic nerve or control), exposed cases, database cases, ROR, CI, q, suspect-only estimate |
| `temporal` | per-period 2x2 cells, period denominator, ROR, CI and the two proportions |
| `strict_token` | why a whole-token variant is not a separate analysis |

## Legacy analyses

The repository also contains code from an earlier, broader version of this project: network
toxicology, molecular docking, all-atom molecular dynamics and two-sample Mendelian
randomisation. **None of these is used in the current manuscript.** They are kept for provenance
and are not part of the analysis reported in the paper.

## Licence

MIT. See `LICENSE`.
