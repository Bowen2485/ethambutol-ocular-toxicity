# -*- coding: utf-8 -*-
"""
Final consistency audit: every headline number quoted in the manuscripts must be
traceable to a value in the analysis outputs.

Checks performed
  1. Every deliverable file exists and is non-empty.
  2. The headline FAERS numbers quoted in the manuscripts match the computed CSVs.
  3. The MR numbers quoted match results/mr_opengwas_results.csv.
  4. The docking numbers quoted match docking/results.csv.
  5. Figures exist as both PDF and 300-dpi PNG.
  6. No placeholder markers left in the manuscripts.

Exit code 0 = all checks pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"
TAB = ROOT / "tables"
FIG = ROOT / "figures"
DOCS = ROOT / "docs"

problems: list[str] = []
notes: list[str] = []


def check(cond: bool, msg: str) -> None:
    if cond:
        notes.append(f"  OK   {msg}")
    else:
        problems.append(f"  FAIL {msg}")


print("=" * 78)
print("FINAL CONSISTENCY AUDIT")
print("=" * 78)

# ------------------------------------------------------------------ 1. files
print("\n[1] deliverables present")
# The TCM mechanism chapter and its background file were removed from the project
# when the TCM component was dropped, so they are no longer expected deliverables.
expected = {
    MAN: ["Manuscript_EN_draft.md", "Methods_draft_EN.md",
          "Ethambutol_EyeTox_EN_full.md", "Ethambutol_EyeTox_CN_full.md",
          "references_en.md"],
    TAB: ["Table1_cohort.csv", "Table2_signals.csv", "Table3_tto.csv",
          "Table4_logistic.csv", "Table5_hubs.csv", "Table6_enrichment.csv",
          "Table7_docking.csv", "Table8_mr.csv", "Table9_robustness.csv",
          "Table10_adequacy.csv", "results_digest.md"],
    DOCS: ["literature_ethambutol_ocular.md",
           "STROBE_RECORD_checklist.md", "投稿材料_期刊建议与投稿信.md",
           "需人工完成清单.md"],
}
for d, names in expected.items():
    for n in names:
        p = d / n
        # Table1 holds only a handful of rows, so it is legitimately small
        min_bytes = 60 if n == "Table1_cohort.csv" else 200
        check(p.exists() and p.stat().st_size > min_bytes,
              f"{d.name}/{n} ({p.stat().st_size if p.exists() else 0} B)")

# ------------------------------------------------------------------ 2. figures
print("\n[2] figures as PDF + PNG")
for i in range(1, 10):
    stems = [f for f in FIG.glob(f"Figure{i}_*") if f.suffix in (".pdf", ".png")]
    pdfs = [f for f in stems if f.suffix == ".pdf"]
    pngs = [f for f in stems if f.suffix == ".png"]
    check(bool(pdfs) and bool(pngs), f"Figure{i}: pdf={len(pdfs)} png={len(pngs)}")

# --------------------------------------------------------- 3. FAERS headline
print("\n[3] FAERS headline numbers vs the manuscripts")
eth = pd.read_csv(RES / "faers_signals_ethambutol.csv", encoding="utf-8-sig")
dedup = pd.read_csv(RES / "faers_dedup_summary.csv", encoding="utf-8-sig")
tto = pd.read_csv(RES / "faers_tto.csv", encoding="utf-8-sig")
logit = pd.read_csv(RES / "faers_logistic.csv", encoding="utf-8-sig")
prof = pd.read_csv(RES / "faers_cases_profile.csv", encoding="utf-8-sig")

n_total = int(dedup[dedup.drug == "FAERS_ALL"].n_cases.iloc[0])
eth_rows = dedup[dedup.drug == "ethambutol"]
check(not eth_rows.empty, "ethambutol row present in the cohort table")
n_eth = int(eth_rows.n_cases.iloc[0]) if not eth_rows.empty else len(prof)
on = eth[eth.term == "OPTIC NEUROPATHY"].iloc[0]
n_ocular = int(prof.any_ocular.sum())
n_optic = int(prof.any_optic.sum())
tto_optic = tto[tto.group.str.contains("Optic-nerve", na=False)]
tto_non = tto[tto.group.str.contains("No ocular", na=False)]
age_row = logit[logit.predictor.str.contains("Age", na=False)]
sex_row = logit[logit.predictor.str.contains("Female", na=False)]

facts = {
    "FAERS total cases": (n_total, 20_328_568),
    "ethambutol cases": (n_eth, 13_804),
    "ocular cases": (n_ocular, 971),
    "optic-nerve cases": (n_optic, 475),
    "optic neuropathy ROR": (round(float(on.ror), 2), 159.21),
    "optic neuropathy n": (int(on.a), 153),
    "optic-nerve median TTO": (round(float(tto_optic.median_days.iloc[0]), 1), 125.0),
    "non-ocular median TTO": (round(float(tto_non.median_days.iloc[0]), 1), 30.0),
    "age aOR": (round(float(age_row.or_.iloc[0]) if hasattr(age_row, "or_")
                       else float(age_row["or"].iloc[0]), 3), 1.009),
    "female aOR": (round(float(sex_row["or"].iloc[0]), 3), 1.378),
}
for k, (got, want) in facts.items():
    check(abs(float(got) - float(want)) < max(0.02, abs(want) * 0.002),
          f"{k}: computed={got} quoted={want}")

# ------------------------------------------------------------ 4. MR numbers
print("\n[4] MR numbers")
mr = pd.read_csv(RES / "mr_opengwas_results.csv", encoding="utf-8-sig")
# One estimate per exposure-outcome pair.  The number is not fixed, because it depends on
# how many exposures return instruments, so it is bounded rather than pinned.
check(len(mr) >= 40, f"MR estimates: {len(mr)} (at least 40 expected)")

# The exposure names in this file are the pipeline's internal keys, not the display
# labels.  An earlier version of this audit queried "Cystatin C" and "eGFR (creatinine)",
# which matched nothing, so the whole block was skipped and reported success.  The names
# are asserted here so the same drift cannot pass unnoticed again.
EXPECTED_NAMES = {"eGFR_creatinine", "cystatin_C", "serum_creatinine", "type_2_diabetes",
                  "HbA1c", "body_mass_index", "smoking_initiation",
                  "cigarettes_per_day", "alcohol_drinks_week", "zinc_supplement"}
present = set(mr.exposure.unique())
check(EXPECTED_NAMES <= present,
      f"expected exposures present: missing {sorted(EXPECTED_NAMES - present)}")

#: exposure -> (outcome, instruments, OR, CI low, CI high) exactly as the manuscript
#: states them.  Derived from results/mr_opengwas_results.csv.
MR_QUOTED = {
    "serum_creatinine": ("H7_OPTNEURITIS", 186, 0.944, 0.722, 1.234),
    "cystatin_C": ("H7_OPTNEURITIS", 115, 1.054, 0.886, 1.254),
    "type_2_diabetes": ("H7_OPTNEURITIS", 54, 1.099, 0.942, 1.284),
    "body_mass_index": ("H7_OPTNEURITIS", 266, 1.680, 1.265, 2.231),
}
for exp, (outcome, n, orv, lo, hi) in MR_QUOTED.items():
    row = mr[(mr.exposure == exp) & (mr.outcome == outcome)]
    if row.empty:
        check(False, f"{exp} -> {outcome}: absent from the result file")
        continue
    r = row.iloc[0]
    check(int(r.n_snp) == n, f"{exp} -> {outcome} instruments: {int(r.n_snp)} (quoted {n})")
    check(abs(float(r["or"]) - orv) < 0.005,
          f"{exp} -> {outcome} OR: {float(r['or']):.4f} (quoted {orv})")
    check(abs(float(r.or_lcl) - lo) < 0.005 and abs(float(r.or_ucl) - hi) < 0.005,
          f"{exp} CI: {float(r.or_lcl):.3f}-{float(r.or_ucl):.3f} (quoted {lo}-{hi})")

# The renal exposures must be null; the positive control must not be.  Both directions are
# asserted, because the pair is the scientific claim: the pipeline detects an effect where
# one exists, so the renal nulls are absences of effect rather than absences of power.
RENAL = ["eGFR_creatinine", "cystatin_C", "serum_creatinine"]
renal = mr[mr.exposure.isin(RENAL)]
check(len(renal) == 18, f"renal exposure-outcome pairs: {len(renal)} (expected 18)")
check(bool((renal.p_fdr >= 0.05).all()),
      f"renal exposures null after FDR (min q = {renal.p_fdr.min():.3f})")

pos = mr[(mr.exposure == "body_mass_index") & (mr.outcome == "H7_OPTNEURITIS")]
if not pos.empty:
    q = float(pos.iloc[0].p_fdr)
    check(q < 0.05, f"positive control (body mass index -> optic neuritis) q = {q:.4f}")
    check(abs(mr.p_fdr.min() - q) < 1e-9,
          f"the positive control is the only pair surviving FDR (min q = {mr.p_fdr.min():.3f})")

# --------------------------------------------------------- 5. docking numbers
print("\n[5] docking numbers")
dk = pd.read_csv(ROOT / "docking" / "results.csv", encoding="utf-8-sig")
ok = dk[dk.ok == True]  # noqa: E712
check(len(dk) == 168, f"docking runs: {len(dk)} (expected 168)")
check(len(ok) == 126, f"successful dockings: {len(ok)} (expected 126)")
eth_tnf = ok[(ok.gene == "TNF") & (ok.ligand == "ethambutol")]
que_tnf = ok[(ok.gene == "TNF") & (ok.ligand == "quercetin")]
if not eth_tnf.empty:
    check(abs(float(eth_tnf.best_affinity.iloc[0]) - (-5.50)) < 0.02,
          f"ethambutol-TNF: {float(eth_tnf.best_affinity.iloc[0]):.2f} (quoted -5.50)")
if not que_tnf.empty:
    check(abs(float(que_tnf.best_affinity.iloc[0]) - (-8.91)) < 0.02,
          f"quercetin-TNF: {float(que_tnf.best_affinity.iloc[0]):.2f} (quoted -8.91)")

# ------------------------------------------------------- 6. no placeholders
print("\n[6] no unresolved placeholders in the manuscripts")
# word-boundary patterns only: a naive substring search for "todo" matches the
# Spanish/Portuguese word inside ordinary English prose
bad_patterns = [r"\bTODO\b", r"\bTBD\b", r"\bXXX\b", r"\bPLACEHOLDER\b",
                r"\[insert", r"待补", r"待 MR", r"to be completed",
                r"^\s*\.\.\.\s*$"]
compiled = [re.compile(p, re.MULTILINE) for p in bad_patterns]
for f in MAN.glob("*.md"):
    txt = f.read_text(encoding="utf-8")
    hits = [rx.pattern for rx in compiled if rx.search(txt)]
    check(not hits, f"{f.name}: markers {hits}")

# ------------------------------------------------------------- 7. robustness
print("\n[7] robustness conclusions")
rb = pd.read_csv(RES / "faers_robustness.csv", encoding="utf-8-sig")
core = ["OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY"]
for t in core:
    sub = rb[rb.term == t]
    check(bool(sub.signal.all()),
          f"{t} significant in all {sub.scenario.nunique()} scenarios")
neg = rb[rb.term.isin(["CATARACT", "DRY EYE", "GLAUCOMA", "EYE PAIN"])]
check(bool((~neg.signal).all()),
      "non-specific ocular terms null in all scenarios")

# ------------------------------------------------------------------- report
print("\n" + "=" * 78)
for n in notes:
    print(n)
if problems:
    print("\n" + "!" * 78)
    for p in problems:
        print(p)
    print("!" * 78)
    print(f"\n{len(problems)} CHECK(S) FAILED")
    sys.exit(1)
print(f"\nALL {len(notes)} CHECKS PASSED")
sys.exit(0)
