# -*- coding: utf-8 -*-
"""
Run the pipeline's own harmonise() on the cached scans, for every exposure.

Why
    mr_final.py does build alt/ref from ea/nea before calling harmonise (lines 194-195),
    so the committed code is correct.  Yet results/mr_scan_coverage.csv, written during
    the run that produced the published estimates, records 0 harmonised for serum
    creatinine, HbA1c, smoking, cigarettes per day and body mass index, while eGFR and
    cystatin C succeeded.  Something differed between that run and the code as it now
    stands.

    Rather than reason about which revision ran, this calls the current harmonise()
    directly on the cached scans and reports what it returns.  Whatever it produces now
    is what a fresh run would produce, and that is the number that matters for deciding
    whether the renal null needs recomputing.

Usage
    python src/run_pipeline_harmonise.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"

from mr_analysis import harmonise  # noqa: E402

EXPOSURES = [
    ("ebi-a-GCST90103634", "eGFR (creatinine)", 150),
    ("ebi-a-GCST90025945", "Cystatin C", 146),
    ("ebi-a-GCST90025946", "Serum creatinine", 0),
    ("ebi-a-GCST006867", "Type 2 diabetes", 57),
    ("ebi-a-GCST90014006", "HbA1c", 0),
    ("ieu-b-4877", "Smoking initiation", 0),
    ("ieu-b-25", "Cigarettes per day", 0),
    ("ieu-b-73", "Alcoholic drinks per week", 0),
    ("ukb-b-13891", "Zinc supplement use", 0),
    ("ieu-b-40", "Body mass index", 0),
]
OUTCOMES = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
            "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]


def build_exposure(gid: str) -> pd.DataFrame:
    """Exactly mr_final.py lines 189-204."""
    p = RAW / f"tophits_{gid}_5e-08.tsv"
    if not p.exists():
        return pd.DataFrame()
    exp = pd.read_csv(p, sep="\t")
    exp["chrom"] = exp["chr"].astype(str).str.replace("chr", "", regex=False)
    exp["pos"] = pd.to_numeric(exp["pos"], errors="coerce")
    exp["alt"] = exp["ea"].astype(str).str.upper()
    exp["ref"] = exp["nea"].astype(str).str.upper()
    exp["rsids"] = exp["rsid"].astype(str)
    exp["beta"] = pd.to_numeric(exp["beta"], errors="coerce")
    exp["sebeta"] = pd.to_numeric(exp["sebeta"], errors="coerce")
    exp["af_alt"] = pd.to_numeric(exp.get("eaf"), errors="coerce")
    exp["pval"] = pd.to_numeric(exp.get("p", pd.Series(dtype=float)),
                                errors="coerce") if "p" in exp.columns else float("nan")
    return exp.dropna(subset=["pos", "beta", "sebeta"])


print("=" * 92)
print("Harmonised instrument counts from the current code, per exposure and outcome")
print("=" * 92)
head = f"  {'exposure':26s} {'n':>5s} " + " ".join(f"{o[3:9]:>7s}" for o in OUTCOMES) \
       + f" {'reported':>9s}"
print(head)
rows = []
for gid, label, reported in EXPOSURES:
    exp = build_exposure(gid)
    if exp.empty:
        print(f"  {label:26s} no instruments cached")
        continue
    cells, per_out = [], {}
    for ph in OUTCOMES:
        files = sorted(RAW.glob(f"mr_{gid}_{ph}_*.tsv"))
        if not files:
            cells.append(f"{'-':>7s}")
            per_out[ph] = None
            continue
        out = pd.concat((pd.read_csv(f, sep="\t") for f in files), ignore_index=True)
        h = harmonise(exp, out)
        per_out[ph] = 0 if h.empty else len(h)
        cells.append(f"{per_out[ph]:>7d}")
    best = max((v for v in per_out.values() if v is not None), default=None)
    flag = ""
    if best is not None and reported:
        flag = "  match" if abs(best - reported) <= 3 else "  DIFFERS"
    elif best is not None and not reported:
        flag = "  now works" if best > 0 else ""
    print(f"  {label:26s} {len(exp):>5d} " + " ".join(cells)
          + f" {reported:>9d}{flag}")
    rows.append((label, len(exp), best, reported))

print()
print("=" * 92)
print("Summary")
print("=" * 92)
for label, n_inst, best, reported in rows:
    if best is None:
        print(f"  {label:26s} instruments {n_inst:>4}  no cached scans for any outcome")
    elif best == 0:
        print(f"  {label:26s} instruments {n_inst:>4}  harmonised     0  "
              f"-> genuinely absent from the cached scans")
    else:
        note = "" if not reported else (
            " consistent with the reported estimate" if abs(best - reported) <= 3
            else f" reported as {reported}, so the estimate should be recomputed")
        print(f"  {label:26s} instruments {n_inst:>4}  harmonised {best:>5}  "
              f"->{note}")
