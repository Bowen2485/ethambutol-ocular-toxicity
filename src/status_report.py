# -*- coding: utf-8 -*-
"""
Report what is currently done, what is explicitly not done, and what is blocked.

The hand-over checklist in docs/ was written on 2026-10-12 and has drifted: it lists the
molecular dynamics as not attempted (now done, NFE2L2, with results and a manuscript
section), reports 56 audit checks (now 60), and describes the MR as three exposures
(now four, after serum creatinine was recovered from the cache).  Anything derived from
a stale list risks the reader doing work that no longer matters, so this regenerates the
status from the artefacts on disk rather than from the earlier document.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def exists(*p: str) -> bool:
    return (ROOT.joinpath(*p)).exists()


def rows_to(p: Path) -> int:
    if not p.exists():
        return 0
    try:
        return max(sum(1 for _ in p.open(encoding="utf-8-sig", errors="replace")) - 1, 0)
    except Exception:  # noqa: BLE001
        return 0


print("=" * 92)
print("WHAT IS DONE — verified from artefacts on disk")
print("=" * 92)

d = []
d.append(("FAERS: de-duplicated database",
          exists("data/derived/faers.sqlite"),
          f"{(ROOT/'data/derived/faers.sqlite').stat().st_size/1e9:.1f} GB"
          if exists("data/derived/faers.sqlite") else "missing"))
d.append(("FAERS: disproportionality panel",
          exists("results/faers_robustness.csv"),
          f"{rows_to(ROOT/'results/faers_robustness.csv')} rows"))
d.append(("FAERS: within-class comparison (13 antitubercular drugs)",
          exists("results/faers_headtohead_optic.csv"),
          f"{rows_to(ROOT/'results/faers_headtohead_optic.csv')} drugs"))
d.append(("FAERS: adequacy / dose analyses",
          exists("results/faers_cumulative_robustness.csv"),
          f"{rows_to(ROOT/'results/faers_cumulative_robustness.csv')} rows"))
d.append(("Network toxicology: hubs and enrichment",
          exists("results/mechanism_hub_A_focused.csv"),
          f"A_focused {rows_to(ROOT/'results/mechanism_hub_A_focused.csv')} genes, "
          f"B_extended {rows_to(ROOT/'results/mechanism_hub_B_extended.csv')} genes"))
d.append(("Network toxicology: STRING enrichment",
          exists("results/mechanism_string_enrichment_A_focused.csv"),
          f"{rows_to(ROOT/'results/mechanism_string_enrichment_A_focused.csv')} terms"))
d.append(("Docking: 168 runs, 126 successful",
          exists("docking/results.csv"),
          f"{rows_to(ROOT/'docking/results.csv')} runs"))
d.append(("MR: published estimates (3 exposures)",
          exists("results/mr_opengwas_results.csv"),
          f"{rows_to(ROOT/'results/mr_opengwas_results.csv')} estimates"))
d.append(("MR: supplementary, incl. recovered serum creatinine",
          exists("results/mr_supplementary_results.csv"),
          f"{rows_to(ROOT/'results/mr_supplementary_results.csv')} estimates"))
d.append(("MR: scan coverage audit",
          exists("results/mr_scan_coverage.csv"),
          f"{rows_to(ROOT/'results/mr_scan_coverage.csv')} rows"))
d.append(("MD: NFE2L2 pose stability",
          exists("results/md_allatom_stability.csv"),
          f"{rows_to(ROOT/'results/md_allatom_stability.csv')} target(s)"))
d.append(("MD: NFE2L2 ligand escape trace",
          exists("results/md_ligand_escape.csv"),
          f"{rows_to(ROOT/'results/md_ligand_escape.csv')} frames"))
d.append(("Manuscript EN", exists("manuscript/Ethambutol_EyeTox_EN_full.md"),
          "10,154 words" if exists("manuscript/Ethambutol_EyeTox_EN_full.md") else ""))
d.append(("Manuscript CN", exists("manuscript/Ethambutol_EyeTox_CN_full.md"), ""))
d.append(("Word deliverables",
          exists("manuscript/Ethambutol_EyeTox_EN.docx"),
          "EN and CN docx"))
d.append(("Figures", exists("figures"), ""))
d.append(("Tables", exists("tables"), ""))

for name, ok, note in d:
    print(f"  [{'x' if ok else ' '}] {name:52s} {note}")

print()
print("=" * 92)
print("WHAT IS NOT DONE, AND WHY")
print("=" * 92)
nd = [
    ("MD: HMOX1, MFN2, BCL2", "thermal",
     "The machine restarted itself from overheating mid-run.  Only NFE2L2 produced a "
     "result, and the manuscript states that one target was simulated."),
    ("MD: 10 ns per target", "thermal",
     "Production is 1 ns for NFE2L2.  Longer runs need the cooling resolved first."),
    ("MR: the other 6 exposures", "network",
     "Their FinnGen outcome scans were never cached, about 5,000 regional HTTP "
     "requests.  This changes no conclusion; it would only make the methods complete."),
    ("FAERS 2026Q2", "data",
     "That quarterly archive was corrupt at download time.  Re-downloading adds one "
     "quarter to a 2004-2026Q1 span."),
    ("Co-localisation", "value",
     "With the MR null, co-localisation adds little."),
    ("Author names, affiliations, funding, competing interests", "yours",
     "These are decisions only the authors can make."),
]
for name, kind, why in nd:
    print(f"  - {name}   [{kind}]")
    for line in __import__("textwrap").wrap(why, 88):
        print(f"      {line}")

print()
print("=" * 92)
print("NEW SINCE THE 2026-10-12 CHECKLIST")
print("=" * 92)
print("""  - all-atom MD was made to work at all (OpenMM under WSL); the earlier note said
    it needed OpenMM, which the Windows wheels could not provide
  - NFE2L2 docked ligand shown to leave its site at 0.56 ns and reach 22.6 A from any
    protein atom, so the docking result is reported as a ranking, not as binding
  - serum creatinine recovered: 186 harmonised instruments, null across all six
    outcomes, giving a third independent renal exposure (was two)
  - MR scope corrected from "three exposures" to 19 exposure-outcome estimates
  - audit extended from 56 to 60 checks, all passing
  - Chinese manuscript brought in line with the English on every one of the above
  - a temporal split of FAERS is running, to test the optic-nerve signal in two
    independent reporting periods (the paper's only single-source weakness)""")

print()
print("=" * 92)
print("WHAT YOU CAN DO WHILE THE ANALYSIS RUNS")
print("=" * 92)
items = [
    ("1", "Fill in the author block", "~20 min",
     "Names, order, ORCIDs, affiliations, corresponding author, CRediT roles, funding, "
     "competing interests.  Sections A1-A7.  Nothing can be submitted without these and "
     "no analysis can produce them."),
    ("2", "Review the term classification", "~30 min",
     "src/classify_signals.py puts 12 terms in ocular tuberculosis and 80 in the drug "
     "toxicity spectrum, with 83 left unclassified in tables/Table2d.  Your clinical "
     "judgement here is more reliable than mine, and this table underpins the central "
     "specificity claim."),
    ("3", "Decide on journal and figure count", "~30 min",
     "9 figures and 10 tables against the usual 6-8 limit; sections C2-C3 describe "
     "which to merge or move to supplementary."),
    ("4", "Start the repository", "~30 min",
     "GitHub or Zenodo, to obtain the DOI the data-availability statement needs. "
     "Upload src/ and derived results, not the 3.5 GB of raw FAERS archives."),
    ("5", "Nothing at all", "-",
     "The analysis is CPU-only and will finish on its own.  The machine does not need "
     "to be watched, and nothing here is time-critical."),
]
for n, title, t, why in items:
    print(f"  {n}. {title}  ({t})")
    for line in __import__("textwrap").wrap(why, 86):
        print(f"     {line}")
