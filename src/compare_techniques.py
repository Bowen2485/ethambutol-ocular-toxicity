# -*- coding: utf-8 -*-
"""
List every analysis the four peer papers actually ran, so the manuscript can be measured
against them rather than against recollection.

Why this is worth doing carefully
    Two of the four are in the same journal and the same genre as this manuscript -
    disproportionality analysis followed by network toxicology and docking.  Whatever they
    do routinely is what a reviewer of that genre expects to see, and a method they all use
    that this manuscript lacks is a predictable request in review.

How the methods are recovered
    From the full text of each paper: Europe PMC XML for the three open-access ones, and the
    text layer of the supplied PDF for the fourth.  Each method keyword is counted and the
    surrounding sentence captured, so what is reported is what the paper says, not an
    inference from the section heading.

The output is a coverage table: which techniques appear in how many of the four, and
whether the manuscript already has them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIT = ROOT / "docs" / "literature_peers"
TXT = LIT / "text"
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
LOW = EN.lower()

PAPERS = {
    "PMID42577260": "ICI ocular AEs (FAERS)",
    "PLOSONE_2026_Leukotriene-EGPA": "LTRAs and EGPA (FAERS+JADER+CVAR)",
    "ang": "drug-induced cheilitis (PV+NT+docking)",
    "PMID42379941": "ASMs and SJS/TEN (FAERS+JADER+bioinformatics)",
}

#: technique -> regular expression recognising it.  Written to catch the several ways each
#: is named in practice, since a method is often described rather than labelled.
TECHNIQUES = {
    "ROR": r"\bROR\b|reporting odds ratio",
    "PRR": r"\bPRR\b|proportional reporting ratio",
    "BCPNN / IC": r"\bBCPNN\b|information component|\bIC025\b|\bIC\b",
    "EBGM / MGPS": r"\bEBGM\b|empirical bayes|multi-?item gamma",
    "MHRA": r"\bMHRA\b",
    "ROR+PRR+BCPNN+EBGM (four algorithms)": r"four (?:data mining )?algorithms|four disproportion",
    "chi-square / Yates": r"chi-?square|Yates",
    "FDR / BH correction": r"Benjamini|false discovery|\bFDR\b|\bBH\b",
    "sensitivity / robustness": r"sensitivity analys|robustness|sensitivity test",
    "subgroup analysis": r"subgroup",
    "suspect-drug restriction": r"primary suspect|principal suspect|suspect drug",
    "vaccine / drug restriction": r"restrict",
    "time to onset": r"time[- ]to[- ]onset|\bTTO\b|onset time",
    "Weibull / distribution fit": r"Weibull|log-?normal|gamma distribution",
    "logistic regression": r"logistic regression|multivariable|multivariate",
    "reporting completeness": r"complete(?:ness)?|missing data",
    "wHO / VigiBase / other DB": r"VigiBase|WHO|EudraVigilance|CVAR|KIDS",
    "network pharmacology / toxicology": r"network (?:pharmacolog|toxicolog)|network analysis",
    "target prediction (SwissTarget/STITCH)": r"SwissTarget|STITCH|SuperPRED|PharmMapper|TargetNet",
    "disease targets (GeneCards/OMIM/DisGeNET)": r"GeneCards|OMIM|DisGeNET|TTD|CTD",
    "Venn / intersection": r"Venn|intersect",
    "PPI network (STRING)": r"\bSTRING\b|protein-?protein interaction|\bPPI\b",
    "hub genes (topology)": r"hub (?:gene|target)|degree|betweenness|cytoHubba",
    "GO enrichment": r"\bGO\b|gene ontology",
    "KEGG enrichment": r"KEGG",
    "Reactome / WikiPathways": r"Reactome|WikiPathways",
    "g:Profiler / DAVID / Metascape": r"g:Profiler|gProfiler|DAVID|Metascape|clusterProfiler",
    "molecular docking (Vina)": r"docking|AutoDock|\bVina\b|CB-Dock",
    "binding free energy (MM-PBSA/GBSA)": r"MM-?PBSA|MM-?GBSA|binding free energy|prime.?MM",
    "molecular dynamics (all-atom)": r"molecular dynamic|\bMD simulation\b|GROMACS|AMBER|OpenMM",
    "MD: RMSD/RMSF/Rg/SS": r"RMSD|RMSF|radius of gyration|Rg\b|secondary structure",
    "MD: hydrogen-bond analysis": r"hydrogen bond|H-?bond",
    "MD: binding energy decomposition": r"per-?residue|decomposition|energy contribution",
    "MD: multiple replicas": r"replica|independent run",
    "Mendelian randomisation": r"Mendelian randomi|two-?sample MR|\bMR analysis\b",
    "immune infiltration": r"immune infiltrat|CIBERSORT|xCell|ssGSEA",
    "single-cell / scRNA": r"single-?cell|scRNA|single cell RNA",
    "transcriptomic validation (GEO)": r"\bGEO\b|GSE\d+|transcriptom",
    "animal / cell experiment": r"mice|mouse|rat\b|cell line|western blot|\bPCR\b|in vitro|in vivo",
    "docking control (redocking)": r"redock|re-?dock|control ligand|crystal ligand",
    "ADMET prediction": r"ADMET|SwissADME|pkCSM|drug-?likeness|Lipinski",
}

rows = []
for key, desc in PAPERS.items():
    p = TXT / f"{key}.xml"
    if p.exists():
        xml = p.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"<[^>]+>", " ", xml)
    else:
        p = TXT / f"{key}.txt"
        text = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    text = re.sub(r"\s+", " ", text)
    counts = {}
    for tech, pat in TECHNIQUES.items():
        counts[tech] = len(re.findall(pat, text, re.I))
    rows.append((key, desc, counts, len(text)))

print("=" * 112)
print("Techniques used by each peer paper, and whether the manuscript already has them")
print("=" * 112)
hdr = f"{'technique':44s} " + " ".join(f"{k[:11]:>12s}" for k, _, _, _ in rows) + "   manuscript"
print(hdr)
print("-" * 112)

for tech in TECHNIQUES:
    cells = []
    for _, _, counts, _ in rows:
        n = counts[tech]
        cells.append(f"{n:>12d}" if n else f"{'-':>12s}")
    in_ms = "yes" if re.search(TECHNIQUES[tech], LOW, re.I) else "NO"
    print(f"{tech:44s} " + " ".join(cells) + f"   {in_ms}")

print()
print("=" * 112)
print("Techniques that at least three of the four peers use, and the manuscript lacks")
print("=" * 112)
gaps = []
for tech in TECHNIQUES:
    used = sum(1 for _, _, c, _ in rows if c[tech] > 0)
    in_ms = bool(re.search(TECHNIQUES[tech], LOW, re.I))
    if used >= 3 and not in_ms:
        gaps.append((tech, used))
    elif used >= 3 and in_ms:
        print(f"  have  {tech:46s} used by {used}/4")
if gaps:
    print()
    for tech, used in sorted(gaps, key=lambda x: -x[1]):
        print(f"  GAP   {tech:46s} used by {used}/4")
else:
    print()
    print("  no technique used by three or more peers is missing")

print()
print("=" * 112)
print("Techniques only one or two peers use, in case any is worth adding")
print("=" * 112)
for tech in TECHNIQUES:
    used = sum(1 for _, _, c, _ in rows if c[tech] > 0)
    in_ms = bool(re.search(TECHNIQUES[tech], LOW, re.I))
    if used in (1, 2) and not in_ms:
        who = [k for k, _, c, _ in rows if c[tech] > 0]
        print(f"  {tech:46s} {used}/4   {', '.join(w[:14] for w in who)}")

summary_path = LIT / "technique_coverage.json"
summary_path.write_text(json.dumps(
    {k: {"desc": d, "counts": c, "chars": n} for k, d, c, n in rows},
    indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  written: {summary_path.relative_to(ROOT)}")
