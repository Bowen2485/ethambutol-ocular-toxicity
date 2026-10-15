# Ethambutol ocular toxicity: pharmacovigilance, network toxicology and genetic analysis

Analysis code for a study of ethambutol's ocular toxicity in the FDA Adverse Event
Reporting System, integrated with network toxicology, molecular docking, all-atom
molecular dynamics and two-sample Mendelian randomisation.

## What the study asks

Ethambutol's optic-nerve toxicity is long established, so the question is not whether the
signal exists but whether it is *specific*.  A drug that damages the optic nerve should
produce signals for optic-nerve and colour-vision terms while leaving non-specific ocular
complaints - dry eye, eye pain, cataract, glaucoma - at or below the background rate.
That internal contrast is the primary result, and the analysis is built around testing
it rather than around reporting the signal itself.

## What the code does

| Stage | Scripts | Output |
|---|---|---|
| FAERS ingestion and case-version de-duplication | `faers_*.py` | 20,328,568 de-duplicated cases from 90 quarterly ASCII releases |
| Disproportionality analysis | `faers_signals*.py` | ROR, PRR, IC025, EBGM05 with Benjamini-Hochberg control over 177 ocular terms |
| Within-class comparison | `regimen_stratified.py` | Regimen-stratified rate ratios that hold co-prescription constant |
| Temporal validation | `faers_temporal_validation.py` | The signal reproduced in two independent reporting eras |
| External validation | `jader_validation.py` | Replication in JADER, the Japanese database |
| Reporting-intensity check | `build_tb_denominator.py` | WHO tuberculosis burden as a partial exposure denominator |
| Network toxicology | `mechanism_*.py` | Pathway enrichment and hub ranking |
| Docking | `docking_run.py` | AutoDock Vina scores with a seven-complex redocking validation panel |
| Molecular dynamics | `run_md_allatom.py`, `analyse_md.py` | OpenMM all-atom trajectories and stability metrics |
| Mendelian randomisation | `mr_final.py`, `mr_analysis.py` | Two-sample MR, IVW, MR-Egger, weighted median, Cochran Q, Steiger |
| Audit | `final_audit.py` | 60 consistency checks over the manuscript's claims |

## Rerunning it

### Requirements

Python 3.11 or later with `numpy`, `pandas`, `scipy`, `statsmodels`, `networkx`,
`matplotlib`, `rdkit`, `mdtraj`.  Docking needs AutoDock Vina 1.2 and Open Babel 3.1.
Molecular dynamics needs OpenMM with a CUDA platform and AmberTools for ligand
parameterisation; it was run under WSL2 with conda-forge OpenMM 8.6.1.

### Data

**No data is included in this repository** - it amounts to 42 GB.  Every source is
publicly available and free to download:

| Source | Used for | Where |
|---|---|---|
| FAERS quarterly ASCII | the pharmacovigilance analysis | https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html |
| JADER | external validation | https://www.pmda.go.jp/english/rs-sb-std/rs/0009.html |
| WHO Global Health Observatory | tuberculosis burden denominator | https://ghoapi.azureedge.net/api/ |
| Open Targets | drug mechanism and disease associations | GraphQL API v4 |
| STRING v12 | protein interaction network | https://string-db.org |
| g:Profiler | functional enrichment | https://biit.cs.ut.ee/gprofiler |
| PubChem | compound structures | https://pubchem.ncbi.nlm.nih.gov |
| RCSB PDB | experimental structures | https://www.rcsb.org |
| OpenGWAS | genetic instruments | https://gwas.mrcieu.ac.uk |
| FinnGen release 12 | outcome summary statistics | gs://finngen-public-data-r12 |

Place downloaded files under `data/raw/` following the layout the scripts expect; each
script states its inputs in its docstring.

### One credential is required

The Mendelian randomisation retrieves instruments from OpenGWAS, which requires a free
API token.  `mr_final.py` and `opengwas_catalogue.py` read it from
`data/raw/opengwas/token.txt`.  That file is **not** in this repository and must not be
committed.  Obtain a token from your OpenGWAS account and write it to that path.

## What the analysis found, in one paragraph

Of 13,804 de-duplicated ethambutol cases, 971 (7.03%) reported an ocular event and 475
(3.44%) an optic-nerve event.  The optic-nerve signal is strong (optic neuropathy ROR
159.21, 95% CI 134.65-188.25) while every non-specific ocular term is null (dry eye 0.42,
cataract 0.86, eye pain 0.64, glaucoma 0.38).  The pattern replicates in a second
reporting era and in JADER.  Within the antitubercular class, co-prescription makes the
naive drug-versus-drug comparison uninterpretable; holding the regimen fixed, adding
ethambutol to rifampicin, isoniazid and pyrazinamide raises the optic-nerve rate from
0.36% to 1.16% (rate ratio 3.28, 95% CI 1.03-10.40).  Network analysis points to
ferroptosis, and that prediction was independently confirmed experimentally in 2026.

## Repository layout

```
src/            analysis scripts, each self-documenting
manuscript/     the manuscript in English and Chinese, and the reference list
tables/         numbered tables as CSV
figures/        figures as PNG (for reading) and PDF (for print)
results/        result tables produced by the analysis
docs/           literature review, method notes, reporting checklist
```

## Limits stated in the paper, repeated here

The docking protocol reproduced crystal poses for ligands up to 13 heavy atoms and failed
from 19 upward; ethambutol has 14 heavy atoms, so it falls in the interval the panel
brackets but does not fill.  The all-atom simulation covers one target over 1 ns.  The
Mendelian randomisation cannot address the drug itself, because ethambutol has no genetic
instrument; it addresses modifiable traits instead.
