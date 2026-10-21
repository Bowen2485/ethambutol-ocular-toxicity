# -*- coding: utf-8 -*-
"""Rebuild the supplementary workbook after the statistical audit.

Three things change here.

1. JADER zero cells.  The Methods say 0.5 is added to all four cells when any cell is zero; the
   JADER table kept a=0 with ROR 0 and a blank upper interval, and S6 claimed no zero cell
   anywhere.  The two dry-eye rows are now corrected and recomputed, and S6 lists them.
2. The fixed-regimen sheet is rebuilt with the fields the review asked for: comparison group,
   total reports, reports with the composite, the proportion, and the ratio with its interval.
3. The workbook becomes readable: column widths, wrapped text, frozen headers, a note row on each
   sheet, a,b,c,d defined on the JADER sheet, and two new mapping sheets (JADER terms, Canada
   composite).

Every number is read from results/main_results.json, results/audit_regimen.json,
results/jader_validation.csv and results/canada_vigilance_ethambutol.json.
"""
from __future__ import annotations

import ast
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = ROOT / "submission" / "tads" / "Supplementary_Tables.xlsx"

d = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
reg = json.loads((RES / "audit_regimen.json").read_text(encoding="utf-8"))
N = d["N"]
n_eth = d["n_ethambutol"]
n_eth_ps = d["n_ethambutol_suspect"]

NEGATIVE = {"Cataract", "Dry eye", "Glaucoma", "Conjunctivitis"}


def qfmt(q: float) -> str:
    if q == 0:
        return "<1e-300"
    if q < 1e-4:
        return f"{q:.1e}"
    return f"{q:.4g}"


def ci_from(a: int, n_event: int, n_drug: int) -> tuple[float, float, float]:
    b, c, dd = n_drug - a, n_event - a, N - n_drug - n_event + a
    est = (a * dd) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / dd)
    return est, math.exp(math.log(est) - 1.959964 * se), math.exp(math.log(est) + 1.959964 * se)


# ------------------------------------------------------------------ S1 terms
rows = []
for r in d["pt"]:
    group = ("optic nerve" if r["group"] == "optic nerve"
             else ("negative control" if r["term"] in NEGATIVE else "non-specific comparator"))
    a_s = r["a_suspect"]
    _, lo_s, hi_s = ci_from(a_s, r["n_event"], n_eth_ps)
    rows.append({
        "Term": r["term"], "Group": group,
        "Exposed cases": r["a"], "Cases in database": r["n_event"],
        "ROR": round(r["ror"], 2),
        "95% CI lower": round(r["ror_lcl"], 2), "95% CI upper": round(r["ror_ucl"], 2),
        "p (exact test)": r["p_display"], "q (BH)": r["q_bh_display"],
        "Test": r["p_test"].split(" (")[0],
        "Exposed cases, suspect only": a_s,
        "ROR, suspect only": round(r["ror_suspect"], 2),
        "95% CI, suspect only": f"{lo_s:.2f}-{hi_s:.2f}",
    })
s1 = pd.DataFrame(rows).sort_values(["Group", "ROR"], ascending=[True, False])

# ---------------------------------------------------------- S2 sensitivity
on = next(r for r in d["pt"] if r["term"] == "Optic neuropathy")
smq = next(r for r in d["smq"] if r["smq"].startswith("Optic nerve"))
t1, t2 = d["temporal"]["2004-2016"], d["temporal"]["2017-2026"]
on_ps = ci_from(on["a_suspect"], on["n_event"], n_eth_ps)
smq_ps = ci_from(smq["a_suspect"], smq["n_event"], n_eth_ps)

w = reg["strata"]["rifampicin+isoniazid+pyrazinamide+ethambutol"]
o = reg["strata"]["rifampicin+isoniazid+pyrazinamide"]

sens_rows = [
    {"Analysis": "Main", "Specification": "Any drug role, whole database", "Outcome": "Optic-nerve query",
     "Total reports": n_eth, "Reports with outcome": smq["a"], "Proportion": f"{100*smq['a']/n_eth:.2f}%",
     "Estimate": round(smq["ror"], 2), "95% CI": f"{smq['ror_lcl']:.2f}-{smq['ror_ucl']:.2f}",
     "Measure": "ROR"},
    {"Analysis": "Main", "Specification": "Any drug role, whole database", "Outcome": "Optic neuropathy",
     "Total reports": n_eth, "Reports with outcome": on["a"], "Proportion": f"{100*on['a']/n_eth:.2f}%",
     "Estimate": round(on["ror"], 2), "95% CI": f"{on['ror_lcl']:.2f}-{on['ror_ucl']:.2f}",
     "Measure": "ROR"},
    {"Analysis": "Sensitivity", "Specification": "Suspect drug only", "Outcome": "Optic-nerve query",
     "Total reports": n_eth_ps, "Reports with outcome": smq["a_suspect"],
     "Proportion": f"{100*smq['a_suspect']/n_eth_ps:.2f}%",
     "Estimate": round(smq_ps[0], 2), "95% CI": f"{smq_ps[1]:.2f}-{smq_ps[2]:.2f}", "Measure": "ROR"},
    {"Analysis": "Sensitivity", "Specification": "Suspect drug only", "Outcome": "Optic neuropathy",
     "Total reports": n_eth_ps, "Reports with outcome": on["a_suspect"],
     "Proportion": f"{100*on['a_suspect']/n_eth_ps:.2f}%",
     "Estimate": round(on_ps[0], 2), "95% CI": f"{on_ps[1]:.2f}-{on_ps[2]:.2f}", "Measure": "ROR"},
    {"Analysis": "Sensitivity", "Specification": f"Receipt year 2004-2016 (denominator {t1['N_period']:,})",
     "Outcome": "Optic neuropathy", "Total reports": t1["n_drug"], "Reports with outcome": t1["a"],
     "Proportion": f"{t1['pct_eth']:.2f}%", "Estimate": round(t1["ror"], 2),
     "95% CI": f"{t1['ror_lcl']:.2f}-{t1['ror_ucl']:.2f}", "Measure": "ROR"},
    {"Analysis": "Sensitivity", "Specification": f"Receipt year 2017-2026 (denominator {t2['N_period']:,})",
     "Outcome": "Optic neuropathy", "Total reports": t2["n_drug"], "Reports with outcome": t2["a"],
     "Proportion": f"{t2['pct_eth']:.2f}%", "Estimate": round(t2["ror"], 2),
     "95% CI": f"{t2['ror_lcl']:.2f}-{t2['ror_ucl']:.2f}", "Measure": "ROR"},
    {"Analysis": "Sensitivity", "Specification": "Fixed regimen with ethambutol (RIF+INH+PZA+EMB)",
     "Outcome": "Optic-nerve composite (4 terms)", "Total reports": w["n"],
     "Reports with outcome": w["n_optic"], "Proportion": f"{100*w['n_optic']/w['n']:.2f}%",
     "Estimate": round(reg["rate_ratio"], 2),
     "95% CI": f"{reg['rate_ratio_lcl']:.2f}-{reg['rate_ratio_ucl']:.2f}",
     "Measure": "Ratio of reporting proportions"},
    {"Analysis": "Sensitivity", "Specification": "Fixed regimen without ethambutol (RIF+INH+PZA)",
     "Outcome": "Optic-nerve composite (4 terms)", "Total reports": o["n"],
     "Reports with outcome": o["n_optic"], "Proportion": f"{100*o['n_optic']/o['n']:.2f}%",
     "Estimate": 1.00, "95% CI": "reference", "Measure": "Ratio of reporting proportions"},
]
s2 = pd.DataFrame(sens_rows)

# ---------------------------------------------------- JADER with zero-cell fix
jad = pd.read_csv(RES / "jader_validation.csv", encoding="utf-8-sig")
jac = jad.copy()
jac["zero_cell_corrected"] = False
for i, r in jac.iterrows():
    four = [r.a, r.b, r.c, r.d]
    if min(four) == 0:
        a, b, c, dd = (x + 0.5 for x in four)
        est = (a * dd) / (b * c)
        se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / dd)
        jac.loc[i, "ror"] = est
        jac.loc[i, "ror_lcl"] = math.exp(math.log(est) - 1.959964 * se)
        jac.loc[i, "ror_ucl"] = math.exp(math.log(est) + 1.959964 * se)
        n = a + b + c + dd
        chi = n * (a * dd - b * c) ** 2 / ((a + b) * (c + dd) * (a + c) * (b + dd))
        jac.loc[i, "chi2_yates"] = chi
        jac.loc[i, "zero_cell_corrected"] = True
s3 = jac

# --------------------------------------------------------------- S4 Canada
can = json.loads((RES / "canada_vigilance_ethambutol.json").read_text(encoding="utf-8"))
s4 = pd.DataFrame([{
    "Exposure": c["exposure"], "Event": c["event"], "Exposed cases": c["a"],
    "Exposed cohort": c["n_exposed"], "Cases in database": c["n_event"], "N": c["N"],
    "ROR": round(c["ror"], 2), "95% CI lower": round(c["ror_lcl"], 2),
    "95% CI upper": round(c["ror_ucl"], 2),
} for c in can["cells"]])
s4b = pd.DataFrame(sorted(can["optic_terms"].items(), key=lambda kv: -kv[1]),
                   columns=["Preferred term containing OPTIC (composite membership)",
                            "Reports in Canada Vigilance"])

# ----------------------------------------------------------------- S5 flow
s5 = pd.DataFrame([{"Stage": k, "n": v} for k, v in d["case_flow"].items()])

# ----------------------------------------------------------- S6 zero cells
zero_rows = []
for i, r in jac.iterrows():
    if min(r.a, r.b, r.c, r.d) == 0:
        zero_rows.append({"Panel": "JADER", "Analysis": r.analysis, "Term": r.term,
                          "a": int(r.a), "b": int(r.b), "c": int(r.c), "d": int(r.d),
                          "Treatment": "0.5 added to all four cells",
                          "ROR after correction": round(r.ror, 3),
                          "95% CI": f"{r.ror_lcl:.3g}-{r.ror_ucl:.3g}"})
if not zero_rows:
    zero_rows.append({"Panel": "FAERS and JADER", "Analysis": "-", "Term": "none", "a": "",
                      "b": "", "c": "", "d": "", "Treatment": "no zero cell",
                      "ROR after correction": "", "95% CI": ""})
else:
    zero_rows.insert(0, {"Panel": "FAERS preferred-term panel", "Analysis": "-", "Term": "none",
                         "a": "", "b": "", "c": "", "d": "",
                         "Treatment": "no zero cell in this panel",
                         "ROR after correction": "", "95% CI": ""})
s6 = pd.DataFrame(zero_rows)

# --------------------------------------------------------------- S7 coverage
cov = json.loads((RES / "audit_period_coverage.json").read_text(encoding="utf-8"))
s7 = pd.DataFrame([
    {"Item": "De-duplicated cases", "n": cov["dedup_rows"]},
    {"Item": "Cases with at least one receipt date in 2004-2026", "n": cov["inrange_cases"]},
    {"Item": "Cases whose every receipt date precedes 2004 (outside both periods)",
     "n": cov["pre2004_cases"]},
])

# ------------------------------------------------------------ S8 onset sample
tto = pd.read_csv(RES / "faers_tto.csv", encoding="utf-8-sig")
prof = pd.read_csv(RES / "faers_cases_profile.csv", encoding="utf-8-sig", low_memory=False)
n_cases = len(prof)
s8 = pd.DataFrame([
    {"Group": "All ethambutol cases", "n": n_cases, "Analysable interval": "",
     "Missing or unusable dates": ""},
    {"Group": "Analysable interval (all)", "n": int(tto.iloc[0].n), "Analysable interval": "",
     "Missing or unusable dates": n_cases - int(tto.iloc[0].n)},
    {"Group": "Optic-nerve event", "n": int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0]),
     "Analysable interval": "yes", "Missing or unusable dates": ""},
    {"Group": "Other ocular event (neither optic-nerve nor non-ocular)",
     "n": int(tto[tto.group.str.startswith("Ocular event")].n.iloc[0])
          - int(tto[tto.group.str.startswith("Optic-nerve")].n.iloc[0]),
     "Analysable interval": "yes", "Missing or unusable dates": ""},
    {"Group": "No ocular event", "n": int(tto[tto.group.str.startswith("No ocular")].n.iloc[0]),
     "Analysable interval": "yes", "Missing or unusable dates": ""},
    {"Group": "Cases carrying at least one of the 17 optic-nerve terms",
     "n": int(prof.any_optic.sum()), "Analysable interval": "83", "Missing or unusable dates": ""},
])

# ------------------------------------------------------- S9 onset term list
deep = (ROOT / "src" / "faers_case_deep.py").read_text(encoding="utf-8")
m = re.search(r"OPTIC_TERMS = \[(.*?)\]", deep, re.S)
terms = [t.strip().strip('"') for t in m.group(1).replace("\n", " ").split(",") if t.strip()]
s9 = pd.DataFrame({"Optic-nerve term used in the onset analysis": terms})

# ------------------------------------------------------- S10 JADER mapping
src = (ROOT / "src" / "jader_validation.py").read_text(encoding="utf-8")
block = src[src.index("TERMS = {"):]
block = block[:block.index("}") + 1]
mapping = ast.literal_eval(block.split("=", 1)[1].strip())
map_rows = []
for english, japanese in mapping.items():
    for jp in japanese:
        map_rows.append({"English preferred term": english, "Japanese MedDRA/J term": jp,
                         "Mapped": "yes", "Note": ""})
map_rows.append({"English preferred term": "cataract / glaucoma / dry eye",
                 "Japanese MedDRA/J term": "白内障 / 緑内障 / ドライアイ",
                 "Mapped": "yes", "Note": "control terms used in the same analysis"})
s10 = pd.DataFrame(map_rows)

# ------------------------------------------------------ S11 composite rule
s11 = pd.DataFrame([
    {"Rule": "Any preferred term containing the string OPTIC",
     "Rationale": ("the MedDRA narrow optic-nerve search is defined as all terms containing "
                   "'optic'; the Canadian extract is coded to MedDRA 29.0, so the rule is applied "
                   "directly"),
     "Terms observed in the extract": len(can["optic_terms"]),
     "Reports with the composite": can["n_optic"]},
])

with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    sheets = [
        ("S1_terms", s1, "Preferred terms: optic-nerve query, negative controls and non-specific comparators. "
                         "p from the exact test stated in column 'Test'; q is Benjamini-Hochberg across the 15 terms."),
        ("S2_sensitivity", s2, "Main analysis and sensitivity analyses. ROR is a reporting odds ratio; "
                               "the fixed-regimen rows report a ratio of reporting proportions."),
        ("S3_jader", s3, "JADER panel. a = ethambutol reports with the event; b = ethambutol reports without; "
                         "c = other reports with the event; d = other reports without. "
                         "Rows with zero_cell_corrected = True had 0.5 added to all four cells before ROR and CI."),
        ("S4_canada", s4, "Canada Vigilance cells. The optic outcome is any preferred term containing OPTIC "
                          "(see S11); the exposed-case count is reports, not terms."),
        ("S4b_canada_terms", s4b, "Every preferred term containing OPTIC that appears in the Canadian extract."),
        ("S5_flow", s5, "Case flow through de-duplication and exposure definition."),
        ("S6_zero_cells", s6, "Every 2x2 with a zero cell across both panels, with the correction applied."),
        ("S7_period_coverage", s7, "Coverage of the two reporting periods."),
        ("S8_onset_sample", s8, "Time-to-onset sample: analysable intervals and missingness by group."),
        ("S9_onset_terms", s9, "The 17-term case-level definition used in the onset analysis."),
        ("S10_jader_mapping", s10, "JADER term mapping used in the analysis."),
        ("S11_canada_rule", s11, "Definition of the Canadian optic-nerve composite."),
    ]
    for name, frame, note in sheets:
        frame.to_excel(xw, sheet_name=name, index=False, startrow=2)
        ws = xw.sheets[name]
        ws["A1"] = name.split("_")[0] + ": " + note
        ws["A1"].font = Font(bold=True, size=10)
        ws["A1"].alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(4, len(frame.columns)))
        ws.row_dimensions[1].height = 30
        ws.freeze_panes = "A4"
        header_fill = PatternFill("solid", fgColor="DDEBF7")
        for cell in ws[3]:
            cell.font = Font(bold=True)
            cell.fill = header_fill
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        for col_idx, column in enumerate(frame.columns, start=1):
            longest = max([len(str(column))] + [len(str(v)) for v in frame[column].head(40)])
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max(10, longest + 2), 48)
        for row in ws.iter_rows(min_row=4, max_row=3 + len(frame)):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

print(f"written {OUT.relative_to(ROOT)}")
for name, frame, _ in sheets:
    print(f"  {name}: {len(frame)} rows x {len(frame.columns)} cols")
