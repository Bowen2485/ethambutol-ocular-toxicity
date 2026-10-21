# SDUD archive, 2016–2026

Archived 2026-10-22 from the files supplied by the corresponding author. The eleven annual
Medicaid State Drug Utilization Data releases and one docking binary are stored locally and
recorded in a manifest; nothing in `~/Downloads` was deleted.

## What is where

| Path | Contents | Size |
|---|---|---|
| `data/raw/sdud/` | eleven annual CSVs, 2016–2026, original file names | 4.99 GB |
| `data/raw/sdud/MANIFEST.csv` | year, file name, bytes, SHA-256, source URL, retrieval date | — |
| `tools/gnina.cuda12.8.static` | GNINA docking binary, with `gnina_README.md` | 2.06 GB bytes |
| `src/archive_sdud.py` | the archival script: copy, hash both sides, write the manifest | — |

Every file was hashed before and after copying and the two digests matched. The manifest is the
record of that check.

## Provenance

| Years | File naming | Source |
|---|---|---|
| 2016–2019 | `StateDrugUtilizationData-<year>.csv` | `https://download.medicaid.gov/data/StateDrugUtilizationData-<year>.csv` |
| 2020–2026 | `sdud<year>_updated<month><year>.csv` | `https://download.medicaid.gov/data/<file name>` |

CMS changed the naming convention in 2020; `src/aggregate_sdud_antitubercular.py` recognises both,
which is why the archive keeps the original names rather than renaming them.

## Coverage, and one caveat

The column set is identical across all eleven files (15 columns, `Utilization Type` through
`Non Medicaid Amount Reimbursed`), so one reader handles the whole series.

| File | Rows | Quarters covered |
|---|---|---|
| 2016 | 4,707,527 | 1–4 |
| 2026 | 1,287,884 | **1 only** |

**The 2026 release is a partial year.** A ten-year series should therefore run 2016–2025, with
2026 either excluded or reported separately; using it as an annual denominator would undercount
prescriptions and inflate any per-prescription rate.

## Using it

The aggregation script now globs `sdud<YEAR>_updated*.csv` and
`StateDrugUtilizationData-<YEAR>.csv` across `~/Downloads` and `~/Downloads/Documents`:

```
python src/aggregate_sdud_antitubercular.py
```

It writes `results/sdud_antitubercular.json`. That file currently holds the two-year (2020, 2025)
aggregate used in the earlier version of the paper.

**The current manuscript does not use this denominator.** The per-prescription analysis was
dropped in the 2026-10-21 restructuring, when the paper was rebuilt around the eleven ocular
queries and the three-database replication. The archive is kept because the earlier versions of
the paper cited it and because a time series is now possible; if it is ever reinstated, it belongs
in a supplementary analysis, not in the main text.

## Why the binary is here

`gnina.cuda12.8.static` is a docking engine, unrelated to every analysis in the current paper.
It sits beside `vina.exe` for provenance. The docking work was removed from the manuscript in the
same restructuring, and `tools/gnina_README.md` says so.

## Not committed

Neither `data/raw/sdud/` nor the binary is in the repository: 7 GB of binary data does not belong
in git. `.gitignore` now excludes `data/raw/sdud/`, `tools/gnina.cuda12.8.static`,
`data/derived/` and `data/raw/faers_ascii/`, so an accidental `git add -A` cannot pull them in.
The manifest, this note and the archival script are committed, which is what a reader needs to
locate and re-download the data.
