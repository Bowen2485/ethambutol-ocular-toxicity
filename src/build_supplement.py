# -*- coding: utf-8 -*-
"""Supplementary tables as a single Excel workbook.

The review asked for the term-level and sensitivity results to be available for verification, and
for the cross-database control comparison to be shown rather than asserted.  One workbook with a
sheet per table is the format journals accept for supplementary tables.

Sheets
    S1_terms        every preferred term reported in the paper, both exposure definitions
    S2_sensitivity  the main estimate and the three sensitivity specifications
    S3_jader        the full JADER panel, both exposure definitions, controls included
    S4_canada       the Canadian cells and the optic-term frequencies
    S5_flow         case flow
    S6_zero_cells   terms whose 2x2 contained a zero cell, with the correction applied
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = ROOT / "submission" / "tads" / "Supplementary_Tables.xlsx"

d = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
reg = json.loads((RES / "audit_regimen.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- S1 terms
NEGATIVE = {"Cataract", "Dry eye", "Glaucoma", "Conjunctivitis"}
rows = []
for r in d["pt"]:
    group = ("optic nerve" if r["group"] == "optic nerve"
             else ("negative control" if r["term"] in NEGATIVE else "non-specific comparator"))
    rows.append({
        "Term": r["term"], "Group": group, "Exposed cases": r["a"],
        "Cases in database": r["n_event"], "ROR": round(r["ror"], 2),
        "95% CI lower": round(r["ror_lcl"], 2), "95% CI upper": round(r["ror_ucl"], 2),
        "q (BH)": r["q_bh"], "Exposed cases, suspect only": r["a_suspect"],
        "ROR, suspect only": round(r["ror_suspect"], 2),
    })
s1 = pd.DataFrame(rows).sort_values(["Group", "ROR"], ascending=[True, False])

# ---------------------------------------------------------- S2 sensitivity
on = next(r for r in d["pt"] if r["term"] == "Optic neuropathy")
smq = next(r for r in d["smq"] if r["smq"].startswith("Optic nerve"))
t1, t2 = d["temporal"]["2004-2016"], d["temporal"]["2017-2026"]
s2 = pd.DataFrame([
    {"Specification": "Main: any drug role, whole database",
     "Outcome": "Optic-nerve query", "Exposed cases": smq["a"], "ROR": round(smq["ror"], 2),
     "95% CI": f"{smq['ror_lcl']:.2f}-{smq['ror_ucl']:.2f}"},
    {"Specification": "Main: any drug role, whole database",
     "Outcome": "Optic neuropathy", "Exposed cases": on["a"], "ROR": round(on["ror"], 2),
     "95% CI": f"{on['ror_lcl']:.2f}-{on['ror_ucl']:.2f}"},
    {"Specification": "Suspect drug only", "Outcome": "Optic-nerve query",
     "Exposed cases": smq["a_suspect"], "ROR": round(smq["ror_suspect"], 2), "95% CI": ""},
    {"Specification": "Suspect drug only", "Outcome": "Optic neuropathy",
     "Exposed cases": on["a_suspect"], "ROR": round(on["ror_suspect"], 2), "95% CI": ""},
    {"Specification": f"Receipt year 2004-2016 (N={t1['N_period']:,})",
     "Outcome": "Optic neuropathy", "Exposed cases": t1["a"], "ROR": round(t1["ror"], 2),
     "95% CI": f"{t1['ror_lcl']:.2f}-{t1['ror_ucl']:.2f}"},
    {"Specification": f"Receipt year 2017-2026 (N={t2['N_period']:,})",
     "Outcome": "Optic neuropathy", "Exposed cases": t2["a"], "ROR": round(t2["ror"], 2),
     "95% CI": f"{t2['ror_lcl']:.2f}-{t2['ror_ucl']:.2f}"},
    {"Specification": "Fixed regimen: RIF+INH+PZA with ethambutol",
     "Outcome": "Optic-nerve event, rate ratio", "Exposed cases": reg["strata"]["rifampicin+isoniazid+pyrazinamide+ethambutol"]["n"],
     "ROR": f"{reg['rate_ratio']:.2f} (rate ratio)",
     "95% CI": f"{reg['rate_ratio_lcl']:.2f}-{reg['rate_ratio_ucl']:.2f}"},
    {"Specification": "Fixed regimen: RIF+INH+PZA without ethambutol",
     "Outcome": "Optic-nerve event, rate ratio (reference)", "Exposed cases": reg["strata"]["rifampicin+isoniazid+pyrazinamide"]["n"],
     "ROR": "reference", "95% CI": ""},
])

# ---------------------------------------------------------------- S3 JADER
s3 = pd.read_csv(RES / "jader_validation.csv", encoding="utf-8-sig")

# --------------------------------------------------------------- S4 Canada
can = json.loads((RES / "canada_vigilance_ethambutol.json").read_text(encoding="utf-8"))
s4 = pd.DataFrame([{
    "Exposure": c["exposure"], "Event": c["event"], "Exposed cases": c["a"],
    "Exposed cohort": c["n_exposed"], "Cases in database": c["n_event"], "N": c["N"],
    "ROR": round(c["ror"], 2), "95% CI lower": round(c["ror_lcl"], 2),
    "95% CI upper": round(c["ror_ucl"], 2),
} for c in can["cells"]])

# ----------------------------------------------------------------- S5 flow
s5 = pd.DataFrame([{"Stage": k, "n": v} for k, v in d["case_flow"].items()])

# ----------------------------------------------------------- S6 zero cells
zero = []
for r in d["pt"]:
    if r["a"] == 0 or r["n_event"] == 0:
        zero.append({"Term": r["term"], "Exposed cases": r["a"],
                     "Cases in database": r["n_event"], "Note": "zero cell, 0.5 added to all cells"})
s6 = pd.DataFrame(zero) if zero else pd.DataFrame(
    [{"Term": "none", "Exposed cases": "", "Cases in database": "",
      "Note": "no zero cell in the reported panel"}])

# ------------------------------------------------------- S7 period coverage
cov = json.loads((RES / "audit_period_coverage.json").read_text(encoding="utf-8"))
s7 = pd.DataFrame([
    {"Item": "De-duplicated cases", "n": cov["dedup_rows"]},
    {"Item": "Cases with at least one receipt date in 2004-2026", "n": cov["inrange_cases"]},
    {"Item": "Cases whose every receipt date precedes 2004 (outside both periods)",
     "n": cov["pre2004_cases"]},
])

with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    s1.to_excel(xw, sheet_name="S1_terms", index=False)
    s2.to_excel(xw, sheet_name="S2_sensitivity", index=False)
    s3.to_excel(xw, sheet_name="S3_jader", index=False)
    s4.to_excel(xw, sheet_name="S4_canada", index=False)
    s5.to_excel(xw, sheet_name="S5_flow", index=False)
    s6.to_excel(xw, sheet_name="S6_zero_cells", index=False)
    s7.to_excel(xw, sheet_name="S7_period_coverage", index=False)

print(f"written {OUT.relative_to(ROOT)}")
for name, frame in (("S1", s1), ("S2", s2), ("S3", s3), ("S4", s4), ("S5", s5),
                    ("S6", s6), ("S7", s7)):
    print(f"  {name}: {len(frame)} rows")
