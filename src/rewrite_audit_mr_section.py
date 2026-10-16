# -*- coding: utf-8 -*-
"""
Replace the MR section of final_audit.py with checks that actually run.

The section had four defects, discovered one after another while repairing the first:

    an IndentationError introduced by the repair itself,
    exposure names that no longer match the result file - "Cystatin C" against
      "cystatin_C" and "eGFR (creatinine)" against "eGFR_creatinine" - so both blocks
      filtered to an empty frame and every check inside them was skipped without
      reporting anything,
    instrument counts and odds ratios left over from the per-window pipeline that
      reported 146 and 1.026 where the pooled pipeline reports 115 and 1.054,
    an assertion that every estimate is null after correction, which contradicts the
      positive control the panel is designed to carry.

A silently skipped check is the worst of these, because it reports success.  The
replacement therefore asserts what the manuscript now claims, and it fails loudly if an
exposure name drifts again.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "final_audit.py"
t = P.read_text(encoding="utf-8")

start = t.find("# ------------------------------------------------------------ 4. MR numbers")
end = t.find("# --------------------------------------------------------- 5. docking numbers")
if start < 0 or end < 0:
    raise SystemExit("could not locate the MR section boundaries")

NEW = '''# ------------------------------------------------------------ 4. MR numbers
print("\\n[4] MR numbers")
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

'''

t = t[:start] + NEW + t[end:]
P.write_text(t, encoding="utf-8")
print("  written")

import ast
try:
    ast.parse(P.read_text(encoding="utf-8"))
    print("  syntax: OK")
except SyntaxError as e:
    print(f"  syntax ERROR at line {e.lineno}: {e.msg}")
    raise SystemExit(1)

print()
print("=" * 94)
print("Re-running the audit")
print("=" * 94)
r = subprocess.run(["python", str(P)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in [l for l in out.splitlines() if l.strip()][-14:]:
    print(f"  {line}")
