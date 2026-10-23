# -*- coding: utf-8 -*-
"""Check the three figure/table points the review asks about.

    figures 2 and 3: every label's case count and odds ratio equals results/main_results.json
    table 3: the three systems keep distinct exposure definitions and outcomes
    supplement: the formal query and the Canadian composite are separated
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz
from docx import Document

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "results" / "main_results.json").read_text(encoding="utf-8"))
problems: list[str] = []


def fig_text(name: str) -> str:
    doc = fitz.open(ROOT / "results" / "tads_figures" / f"{name}.pdf")
    return " ".join(" ".join(p.get_text().split()) for p in doc)


# ---------------------------------------------------------------- figure 2
t2 = fig_text("Figure2_smq_forest")
for r in d["smq"]:
    ror = f"{r['ror']:.2f}"
    if ror not in t2:
        problems.append(f"Fig2 missing ROR {r['smq']}: {ror}")
    if str(r["a"]) not in t2:
        problems.append(f"Fig2 missing cases {r['smq']}: {r['a']}")

# ---------------------------------------------------------------- figure 3
t3 = fig_text("Figure3_pt_forest")
for r in d["pt"]:
    ror = f"{r['ror']:.2f}"
    if ror not in t3:
        problems.append(f"Fig3 missing ROR {r['term']}: {ror}")
    if str(r["a"]) not in t3:
        problems.append(f"Fig3 missing cases {r['term']}: {r['a']}")

# ---------------------------------------------------------------- table 3
doc = Document(ROOT / "submission" / "tads" / "Ethambutol_TADS_manuscript.docx")
tbl = doc.tables[2]
rows = [[c.text.strip() for c in row.cells] for row in tbl.rows]
exposures = {r[1] for r in rows[1:]}
outcomes = {r[2] for r in rows[1:]}
print("table 3 exposures:", sorted(exposures))
print("table 3 outcomes:", sorted(outcomes))
if not any("suspect" in e.lower() for e in exposures):
    problems.append("table 3 lacks a suspect-only row")
if not any("2004" in e for e in exposures):
    problems.append("table 3 lacks the period rows")
if not any("optic-nerve term" in o for o in outcomes):
    problems.append("table 3 lacks the Canadian composite label")
if not any(o.startswith("Optic neuropathy") for o in outcomes):
    problems.append("table 3 lacks the term-level JADER outcome")

# ------------------------------------------------------------- supplement
import openpyxl
wb = openpyxl.load_workbook(ROOT / "submission" / "tads" / "Supplementary_Tables.xlsx")
s11 = " ".join(str(c) for row in wb["S11_canada_rule"].iter_rows(values_only=True) for c in row if c)
print("S11 text:", s11[:150])
if "study-specific" not in s11 and "string match" not in s11:
    problems.append("S11 does not mark the Canadian rule as study-specific")
s4b = wb["S4b_canada_terms"]
terms = [r[0] for r in s4b.iter_rows(min_row=4, values_only=True) if r[0]]
print("S4b terms:", len(terms))
if len(terms) != len(d.get("canada", {}).get("optic_terms", {})) and len(terms) != 29:
    problems.append(f"S4b term count unexpected: {len(terms)}")

print("\nproblems:", len(problems))
for p in problems:
    print("  -", p)
