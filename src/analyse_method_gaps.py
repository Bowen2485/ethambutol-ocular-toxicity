# -*- coding: utf-8 -*-
"""
Compare the methods the peer papers use against this manuscript's, in their own words.

Why this is worth doing from the sentences rather than from a list
    A method counts as available only if it is actually in the papers.  Each entry below is
    searched for the phrases the papers use, and the sentence that matched is printed, so the
    claim that a method is used by N of 4 can be checked rather than taken on trust.  The
    previous attempt at this crashed on a stray comma in the dictionary and wrote placeholder
    citations; both are corrected here, and the output is a table rather than prose.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIT = ROOT / "docs" / "literature_peers" / "text"
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")

#: the four comparator papers
PAPERS = {
    "ICI ocular AEs": "PMID42577260.xml",
    "LTRA / EGPA": "PLOSONE_2026_Leukotriene-EGPA.xml",
    "drug-induced cheilitis": "ang.xml",
    "ASM SJS/TEN": "PMID42379941.xml",
}

METHODS = {
    "Venn intersection of drug and disease targets": r"Venn|Venny|overlapping targets|common targets|shared targets",
    "drug-target sources beyond Open Targets": r"SwissTargetPrediction|STITCH|PharmMapper|SuperPRED|TargetNet|ChEMBL|DrugBank|SEA database|TOXRIC",
    "disease-target sources": r"GeneCards|DisGeNET|OMIM|CTD",
    "PPI network from STRING with a cutoff": r"STRING",
    "hub selection by topology": r"degree centrality|betweenness|closeness|cytoHubba",
    "GO and KEGG enrichment": r"GO and KEGG|KEGG pathway|gene ontology|DAVID|Metascape|clusterProfiler",
    "GEO differential-expression validation": r"GEO|GSE\d+|differentially expressed",
    "molecular docking": r"docking|AutoDock|Vina|CB-Dock",
    "molecular dynamics": r"molecular dynamic|GROMACS|AMBER",
    "binding free energy": r"MM-?PBSA|MM-?GBSA|binding free energy",
    "immune infiltration": r"immune infiltrat|CIBERSORT|xCell",
    "ADMET prediction": r"ADMET|SwissADME|pkCSM|Lipinski",
    "time-to-onset analysis": r"time[- ]to[- ]onset|\bTTO\b|onset time",
    "Weibull or distribution fitting": r"Weibull|log-?normal|gamma distribution",
    "subgroup analysis": r"subgroup",
    "sensitivity analysis": r"sensitivity analys",
    "four disproportionality algorithms together": r"four (?:data mining )?algorithms|four disproportion|ROR.{0,40}PRR.{0,40}BCPNN",
    "FDR correction": r"Benjamini|false discovery|\bFDR\b",
    "restriction to the suspect drug": r"primary suspect|principal suspect",
    "reporting completeness": r"missing (?:data|information)|completeness",
    "separate pharmacovigilance database": r"JADER|VigiBase|EudraVigilance|CVAR|KIDS",
}

bodies = {}
for label, fn in PAPERS.items():
    p = LIT / fn
    if p.exists():
        bodies[label] = re.sub(r"\s+", " ",
                               re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8",
                                                              errors="replace")))
    else:
        bodies[label] = ""

print("=" * 112)
print(f"  {'method':50s} {'peers':>5s}  {'manuscript':>10s}")
print("=" * 112)
rows = []
for label, pat in METHODS.items():
    where = [k for k, v in bodies.items() if re.search(pat, v, re.I)]
    #: the manuscript is searched for the same terms; en-dashes and full stops are normalised
    in_ms = bool(re.search(pat, EN, re.I))
    rows.append({"method": label, "peers": len(where), "where": where,
                 "manuscript": in_ms})
    mark = "have" if in_ms else "MISSING"
    print(f"  {label:50s} {len(where):>5d}  {mark:>10s}")
    if not in_ms and where:
        print(f"      used by: {', '.join(where)}")

print()
print("=" * 112)
print("Methods used by at least two peers that this manuscript lacks")
print("=" * 112)
gaps = [r for r in rows if r["peers"] >= 2 and not r["manuscript"]]
if gaps:
    for r in sorted(gaps, key=lambda x: -x["peers"]):
        print(f"\n  {r['method']}  ({r['peers']}/4 peers)")
        print(f"      {', '.join(r['where'])}")
        #: show the sentence that matched, from the first paper that uses it
        for k in r["where"][:1]:
            pat = METHODS[r["method"]]
            m = re.search(pat, bodies[k], re.I)
            if m:
                s = max(0, m.start() - 200)
                e = min(len(bodies[k]), m.end() + 200)
                print(f"      \"...{bodies[k][s:e].strip()[:330]}...\"")
else:
    print("  none")

print()
print("=" * 112)
print("Methods this manuscript has that the peers mostly lack")
print("=" * 112)
ahead = [r for r in rows if r["manuscript"] and r["peers"] <= 1]
for r in ahead:
    print(f"  {r['method']:50s} {r['peers']}/4 peers")

(ROOT / "results" / "method_gaps.json").write_text(
    json.dumps({"methods": rows, "gaps": gaps}, indent=2, ensure_ascii=False),
    encoding="utf-8")
print()
print(f"  -> results/method_gaps.json")
