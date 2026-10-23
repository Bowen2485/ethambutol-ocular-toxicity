# -*- coding: utf-8 -*-
"""Check that the manuscript, the supplement and the results file agree.

The paper says every table and figure is generated from results/main_results.json under a fixed
release tag, so the numbers printed in the PDF and the workbook have to equal the numbers in that
file.  This compares the headline values and the two panels term by term.
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

pdf = fitz.open(ROOT / "submission" / "tads" / "Ethambutol_TADS_manuscript.pdf")
pdf_text = " ".join(" ".join(p.get_text().split()) for p in pdf)

problems: list[str] = []


def expect(label: str, value: str) -> None:
    if value not in pdf_text:
        problems.append(f"PDF missing {label}: {value}")


# ---------------------------------------------------------------- headline values
expect("N", f"{d['N']:,}")
expect("ethambutol cases", f"{d['n_ethambutol']:,}")
smq_on = next(r for r in d["smq"] if r["smq"].startswith("Optic nerve"))
pt_on = next(r for r in d["pt"] if r["term"] == "Optic neuropathy")
expect("optic-nerve query ROR", f"{smq_on['ror']:.2f}")
expect("optic-nerve query cases", str(smq_on["a"]))
expect("optic neuropathy ROR", f"{pt_on['ror']:.2f}")

# ------------------------------------------------------------------ both panels
for r in d["smq"]:
    expect(f"SMQ {r['smq']} ROR", f"{r['ror']:.2f}")
for r in d["pt"]:
    expect(f"PT {r['term']} ROR", f"{r['ror']:.2f}")

# ------------------------------------------------------------------- Word tables
doc = Document(ROOT / "submission" / "tads" / "Ethambutol_TADS_manuscript.docx")
word_cells = set()
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            word_cells.add(c.text.strip())
missing_in_word = [f"{r['smq']}" for r in d["smq"]
                   if f"{r['ror']:.2f}" not in word_cells]
if missing_in_word:
    problems.append(f"Word table lacks ROR for: {missing_in_word[:3]}")

# --------------------------------------------------------------- supplement S1
import openpyxl
wb = openpyxl.load_workbook(ROOT / "submission" / "tads" / "Supplementary_Tables.xlsx")
s1 = wb["S1_terms"]
s1_ror = {}
for row in s1.iter_rows(min_row=4, values_only=True):
    if row[0] and isinstance(row[4], (int, float)):
        s1_ror[str(row[0])] = float(row[4])
for r in d["pt"]:
    got = s1_ror.get(r["term"])
    if got is None:
        problems.append(f"S1 missing term {r['term']}")
    elif abs(got - round(r["ror"], 2)) > 1e-9:
        problems.append(f"S1 ROR mismatch {r['term']}: {got} vs {r['ror']:.2f}")

# --------------------------------------------------------------- release tag
tag = "v2.0-tads-2026-10-21"
if tag not in pdf_text:
    problems.append(f"release tag {tag} not in PDF")

print(f"checked {len(d['smq'])} queries and {len(d['pt'])} terms")
print(f"supplement S1 rows read: {len(s1_ror)}")
print("problems:", len(problems))
for p in problems:
    print("  -", p)
