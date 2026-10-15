# -*- coding: utf-8 -*-
"""
Step 9 - Publication tables and a machine-generated results digest.

Everything here is derived directly from the analysis outputs; no number is
transcribed by hand.  The digest is the source of truth for the Results section.

Outputs (tables/)
    Table1_cohort.csv     FAERS case counts per exposure
    Table2_signals.csv    ethambutol ocular signals vs comparator drugs
    Table3_tto.csv        time to ocular onset
    Table4_logistic.csv   multivariable logistic regression
    Table5_hubs.csv       focused-tier hub genes
    Table6_enrichment.csv leading enriched terms
    Table7_docking.csv    docking matrix
    Table8_mr.csv         Mendelian randomisation estimates
    results_digest.md     every headline number in one place
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
DOCK = ROOT / "docking"
TABLES.mkdir(parents=True, exist_ok=True)

digest: list[str] = ["# Results digest (auto-generated)\n"]


def note(line: str = "") -> None:
    digest.append(line)


def read(path: Path, **kw) -> pd.DataFrame:
    if not path.exists():
        print(f"[skip] {path.name} not found")
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig", **kw)


def fmt(x, nd=2):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(v):
        return "NA"
    return f"{v:.{nd}f}"


# ---------------------------------------------------------------- Table 1
t1 = read(RESULTS / "faers_dedup_summary.csv")
if not t1.empty:
    # the comparator case counts come from the drug-signal table, which covers
    # every anti-tuberculosis drug; the summary file only holds the index drug
    comp = read(RESULTS / "faers_signals_all_drugs.csv")
    if not comp.empty:
        counts = (comp.groupby("drug")["n_drug"].first().reset_index()
                    .rename(columns={"drug": "Exposure", "n_drug": "Cases"}))
        counts["Substance terms"] = counts["Exposure"].str.upper()
        t1n = t1.rename(columns={"drug": "Exposure", "n_cases": "Cases",
                                 "substances": "Substance terms"})
        merged = pd.concat([t1n, counts], ignore_index=True)
        merged = merged.drop_duplicates(subset=["Exposure"], keep="first")
        order = ["ethambutol", "isoniazid", "rifampicin", "pyrazinamide",
                 "streptomycin", "linezolid", "FAERS_ALL"]
        merged["_o"] = merged.Exposure.map({k: i for i, k in enumerate(order)})
        t1 = merged.sort_values("_o").drop(columns="_o")
    else:
        t1 = t1.rename(columns={"drug": "Exposure", "n_cases": "Cases",
                                "substances": "Substance terms"})
    t1.to_csv(TABLES / "Table1_cohort.csv", index=False, encoding="utf-8-sig")
    note("## 1. Study population (FAERS, de-duplicated)\n")
    note("| Exposure | Cases |")
    note("|---|---|")
    for _, r in t1.iterrows():
        note(f"| {r['Exposure']} | {int(r['Cases']):,} |")
    note()

# ---------------------------------------------------------------- Table 2
t2 = read(RESULTS / "faers_signals_all_drugs.csv")
if not t2.empty:
    keep = ["drug", "term", "group", "a", "n_drug", "n_event", "ror", "ror_lcl",
            "ror_ucl", "prr", "chi2_yates", "ic025", "ebgm05", "q_bh",
            "signal_ror", "signal_prr", "signal_ic", "signal_strict"]
    t2 = t2[[c for c in keep if c in t2.columns]]
    t2.to_csv(TABLES / "Table2_signals.csv", index=False, encoding="utf-8-sig")
    eth = t2[t2.drug == "ethambutol"]
    strict = eth[eth.signal_strict == True]  # noqa: E712
    note("## 2. Ethambutol ocular disproportionality\n")
    note(f"Tested ocular MedDRA preferred terms: {len(eth)}; "
         f"strict signals: {len(strict)}")
    note()
    note("| MedDRA PT | n | ROR (95% CI) | PRR | IC025 | EBGM05 | q |")
    note("|---|---|---|---|---|---|---|")
    for _, r in strict.sort_values("ror", ascending=False).iterrows():
        note(f"| {r['term'].title()} | {int(r['a'])} | "
             f"{fmt(r['ror'])} ({fmt(r['ror_lcl'])}-{fmt(r['ror_ucl'])}) | "
             f"{fmt(r['prr'])} | {fmt(r['ic025'])} | {fmt(r['ebgm05'])} | "
             f"{'<1e-300' if r['q_bh'] == 0 else f'{r[chr(113)+chr(95)+chr(98)+chr(104)]:.2e}'} |")
    note()
    # specificity statement: which ocular terms are NOT signals
    neg = eth[(eth.a >= 3) & (eth.signal_strict != True)]  # noqa: E712
    if not neg.empty:
        note("Non-signal ocular terms (a >= 3), i.e. specificity controls: "
             + ", ".join(f"{t.title()} (ROR {fmt(v)})"
                         for t, v in zip(neg.term, neg.ror)) + "\n")
    # comparator contrast
    comp = t2[(t2.drug != "ethambutol") & (t2.term == "OPTIC NEUROPATHY")]
    if not comp.empty:
        note("Optic-neuropathy ROR by exposure: "
             + "; ".join(f"{r['drug']} {fmt(r['ror'])}"
                         for _, r in comp.sort_values("ror", ascending=False)
                         .iterrows()) + "\n")

# ---------------------------------------------------------------- Table 3
t3 = read(RESULTS / "faers_tto.csv")
if not t3.empty:
    t3.to_csv(TABLES / "Table3_tto.csv", index=False, encoding="utf-8-sig")
    note("## 3. Time from ethambutol start to reported event\n")
    note("| Group | n | median (d) | IQR (d) | P90 (d) |")
    note("|---|---|---|---|---|")
    for _, r in t3.iterrows():
        note(f"| {r['group']} | {int(r['n'])} | {fmt(r['median_days'],1)} | "
             f"{fmt(r['q25_days'],1)}-{fmt(r['q75_days'],1)} | "
             f"{fmt(r['p90_days'],1)} |")
    note()

# ---------------------------------------------------------------- Table 4
t4 = read(RESULTS / "faers_logistic.csv")
if not t4.empty:
    t4.to_csv(TABLES / "Table4_logistic.csv", index=False, encoding="utf-8-sig")
    note("## 4. Multivariable logistic regression (outcome: any ocular AE)\n")
    note("| Predictor | aOR | 95% CI | p |")
    note("|---|---|---|---|")
    for _, r in t4.iterrows():
        note(f"| {r['predictor']} | {fmt(r['or'],3)} | "
             f"{fmt(r['or_lcl'],3)}-{fmt(r['or_ucl'],3)} | "
             f"{'<1e-30' if r['p'] == 0 else f'{r[chr(112)]:.3g}'} |")
    note()

# ---------------------------------------------------------------- Table 5
t5 = read(RESULTS / "mechanism_hub_A_focused.csv")
if not t5.empty:
    t5.to_csv(TABLES / "Table5_hubs.csv", index=False, encoding="utf-8-sig")
    note("## 5. Focused-tier PPI hubs (STRING, confidence >= 0.4)\n")
    note("| Gene | Degree | Betweenness | Literature papers | Core panel |")
    note("|---|---|---|---|---|")
    for _, r in t5.head(25).iterrows():
        note(f"| {r['gene']} | {int(r['degree'])} | {fmt(r['betweenness'],4)} | "
             f"{int(r.get('n_lit_papers', 0))} | "
             f"{'yes' if r.get('in_core_panel') else 'no'} |")
    note()

# ---------------------------------------------------------------- Table 6
t6 = read(RESULTS / "mechanism_enrichment_A_focused.csv")
if not t6.empty:
    sig = t6[(t6.significant == True) &  # noqa: E712
             t6.source.isin(["GO:BP", "GO:CC", "GO:MF", "KEGG", "REAC", "WP"])]
    lead = []
    for src, g in sig.groupby("source"):
        lead.append(g.nsmallest(6, "p_value"))
    lead = pd.concat(lead).sort_values("p_value") if lead else pd.DataFrame()
    if not lead.empty:
        lead[["source", "term_id", "term_name", "p_value", "intersection_size",
              "term_size", "genes"]].to_csv(TABLES / "Table6_enrichment.csv",
                                            index=False, encoding="utf-8-sig")
        note("## 6. Leading enriched terms (focused panel, FDR < 0.05)\n")
        note("| Source | Term | p | Genes in term |")
        note("|---|---|---|---|")
        for _, r in lead.iterrows():
            note(f"| {r['source']} | {r['term_name']} | {r['p_value']:.2e} | "
                 f"{int(r['intersection_size'])}/{int(r['term_size'])} |")
        note()

# ---------------------------------------------------------------- Table 7
t7 = read(DOCK / "results.csv")
if not t7.empty:
    ok = t7[t7.ok == True]  # noqa: E712
    mat = ok.pivot_table(index="ligand", columns="gene", values="best_affinity",
                         aggfunc="min")
    if "ethambutol" in mat.index:
        mat = mat.reindex([r for r in mat.index if r != "ethambutol"]
                          + ["ethambutol"])
    mat.to_csv(TABLES / "Table7_docking.csv", encoding="utf-8-sig")
    note("## 7. Molecular docking (AutoDock Vina, kcal/mol)\n")
    note(f"Runs: {len(t7)}; successful: {len(ok)}; failed: {len(t7) - len(ok)} "
         f"(large flexible ligands that failed PDBQT conversion)\n")
    note("| Ligand | " + " | ".join(mat.columns) + " |")
    note("|---" * (len(mat.columns) + 1) + "|")
    for lig, row in mat.iterrows():
        note(f"| {lig} | " + " | ".join(fmt(v, 1) for v in row.values) + " |")
    note()
    val_path = DOCK / "validation" / "redocking_validation.csv"
    val = read(val_path)
    if not val.empty:
        note("Redocking validation: "
             + "; ".join(f"{r['target']}/{r['ligand']} RMSD {fmt(r.get('top_pose_rmsd_A'))} A "
                         f"({'pass' if r.get('passed') else 'fail'})"
                         for _, r in val.iterrows()) + "\n")

# ---------------------------------------------------------------- Table 8
t8 = read(RESULTS / "mr_opengwas_results.csv")
if not t8.empty:
    t8.to_csv(TABLES / "Table8_mr.csv", index=False, encoding="utf-8-sig")
    note("## 8. Two-sample MR (OpenGWAS exposures -> FinnGen optic-nerve outcomes)\n")
    note(f"Estimates: {len(t8)}")
    show = t8[t8.p.notna()].nsmallest(25, "p")
    note("| Exposure | Outcome | SNPs | Method | OR (95% CI) | p |")
    note("|---|---|---|---|---|---|")
    for _, r in show.iterrows():
        note(f"| {r['exposure']} | {r['outcome']} | {int(r['n_snp'])} | "
             f"{r['method']} | {fmt(r['or'],3)} "
             f"({fmt(r['or_lcl'],3)}-{fmt(r['or_ucl'],3)}) | "
             f"{'<1e-300' if r['p'] == 0 else f'{r[chr(112)]:.3g}'} |")
    note()

# --------------------------------------------------------------- provenance
note("## Provenance\n")
for name in ("faers_ingest_report.json", "extract_progress.json"):
    p = DERIVED / name
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            note(f"- {name}: {len(d)} entries recorded")
        except Exception:  # noqa: BLE001
            pass
note(f"- FAERS quarters ingested: "
     f"{len(list((ROOT / 'data' / 'raw' / 'faers_ascii').glob('*.zip')))}")
note(f"- Ocular MedDRA terms tested: "
     f"{len(read(DERIVED / 'ocular_terms.csv'))}")

(TABLES / "results_digest.md").write_text("\n".join(digest), encoding="utf-8")
print("\n".join(digest[:8]))
print(f"\n[ok] digest -> {TABLES / 'results_digest.md'}")
print(f"[ok] tables -> {TABLES}")
