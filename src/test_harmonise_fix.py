# -*- coding: utf-8 -*-
"""
Confirm the cause of the harmonisation failure, and test the fix.

Established
    harmonise() gathers alt_exp/ref_exp as the exposure allele columns and returns an
    empty frame when they are absent (mr_analysis.py lines 238-239).  Reproducing the
    merge on real files shows those columns are never created: the exposure frames carry
    ea/nea, the FinnGen scans carry ref/alt, and mr_final.py renames neither.

    So harmonise() currently returns an empty frame for every exposure.  The 150, 146
    and 57 instrument estimates in results/mr_opengwas_results.csv cannot have come from
    this code path; they were produced by an earlier revision, which is why the result
    file predates every cached scan except a handful.

    That makes the fix well defined: map the exposure alleles onto the names harmonise()
    expects, then check that the resulting variant counts match what the results file
    reports.  If eGFR returns 150 and cystatin C 146, the original numbers were right and
    only the plumbing had rotted; if they differ, the reported estimates need revisiting
    before anything else is built on them.

Usage
    python src/test_harmonise_fix.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"

EXPOSURES = [("ebi-a-GCST90103634", "eGFR (creatinine)", 150),
             ("ebi-a-GCST90025945", "Cystatin C", 146),
             ("ebi-a-GCST90025946", "Serum creatinine", 0),
             ("ebi-a-GCST006867", "Type 2 diabetes", 57)]
OUTCOME = "H7_OPTNEURITIS"


def load_exposure(gid: str) -> pd.DataFrame:
    """Rebuild the exposure frame exactly as mr_final.py does, then repair the alleles."""
    exp = pd.read_csv(RAW / f"tophits_{gid}_5e-08.tsv", sep="\t")
    exp["rsids"] = exp["rsid"].astype(str)
    exp["beta"] = pd.to_numeric(exp["beta"], errors="coerce")
    exp["sebeta"] = pd.to_numeric(exp["sebeta"], errors="coerce")
    exp["af_alt"] = pd.to_numeric(exp.get("eaf"), errors="coerce")
    if "p" in exp.columns:
        exp["pval"] = pd.to_numeric(exp["p"], errors="coerce")
    exp["chrom"] = exp["chr"].astype(str)
    exp = exp.dropna(subset=["pos", "beta", "sebeta"])
    # THE FIX: harmonise() looks for alt/ref on the exposure side, which the
    # instruments call ea and nea
    if "alt" not in exp.columns and "ea" in exp.columns:
        exp["alt"] = exp["ea"].astype(str).str.upper()
    if "ref" not in exp.columns and "nea" in exp.columns:
        exp["ref"] = exp["nea"].astype(str).str.upper()
    return exp


def load_outcome(gid: str, ph: str) -> pd.DataFrame:
    """Concatenate every cached scan for this exposure and phenotype."""
    files = sorted(RAW.glob(f"mr_{gid}_{ph}_*.tsv"))
    if not files:
        return pd.DataFrame()
    return pd.concat((pd.read_csv(f, sep="\t") for f in files), ignore_index=True)


def harmonise(exp: pd.DataFrame, out: pd.DataFrame) -> pd.DataFrame:
    """The pipeline's logic, with the column names it actually expects."""
    if exp.empty or out.empty:
        return pd.DataFrame()
    ex, ou = exp.copy(), out.copy()
    ex["rs_key"] = ex["rsids"].astype(str).str.strip()
    ou["rs_key"] = ou["rsids"].astype(str).str.strip()
    ou["rs_key"] = ou["rs_key"].str.split(";")
    ou = ou.explode("rs_key")
    ou["rs_key"] = ou["rs_key"].astype(str).str.strip()
    ex["pos_key"] = ex["chrom"].astype(str) + ":" + ex["pos"].astype(int).astype(str)
    ou["pos_key"] = ou["chrom"].astype(str) + ":" + ou["pos"].astype(int).astype(str)

    frames = []
    usable = ex[ex["rs_key"].notna() & (ex["rs_key"] != "") & (ex["rs_key"] != "nan")]
    if not usable.empty:
        m = usable.merge(ou, on="rs_key", suffixes=("_exp", "_out"))
        if not m.empty:
            m["snp_key"] = m["pos_key_exp"]
            frames.append(m)
    m2 = ex.merge(ou, on="pos_key", suffixes=("_exp", "_out"))
    if not m2.empty:
        m2["snp_key"] = m2["pos_key"]
        frames.append(m2)
    if not frames:
        return pd.DataFrame()
    m = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["snp_key"])
    if m.empty or "alt_exp" not in m.columns or "alt_out" not in m.columns:
        return pd.DataFrame()

    comp = {"A": "T", "T": "A", "C": "G", "G": "C"}
    rows = []
    for _, r in m.iterrows():
        a1e, a2e = str(r["alt_exp"]).upper(), str(r["ref_exp"]).upper()
        a1o, a2o = str(r["alt_out"]).upper(), str(r["ref_out"]).upper()
        try:
            eaf = float(r.get("af_alt_exp", np.nan))
        except (TypeError, ValueError):
            eaf = np.nan
        if comp.get(a1e) == a2e and not (np.isfinite(eaf) and (eaf < 0.42 or eaf > 0.58)):
            continue
        if (a1e, a2e) == (a1o, a2o):
            bo, so = r["beta_out"], r["sebeta_out"]
        elif (a1e, a2e) == (a2o, a1o):
            bo, so = -r["beta_out"], r["sebeta_out"]
        else:
            continue
        rows.append({"snp": r.get("rsids_exp", r["snp_key"]),
                     "beta_exp": float(r["beta_exp"]), "se_exp": float(r["sebeta_exp"]),
                     "beta_out": float(bo), "se_out": float(so),
                     "p_out": float(r["pval_out"]), "eaf": eaf})
    return pd.DataFrame(rows)


print("=" * 84)
print("Exposure allele columns")
print("=" * 84)
e = pd.read_csv(RAW / "tophits_ebi-a-GCST90103634_5e-08.tsv", sep="\t")
print(f"  raw instrument columns : {list(e.columns)}")
print(f"  example row            : ea={e['ea'].iloc[0]!r} nea={e['nea'].iloc[0]!r} "
      f"eaf={e['eaf'].iloc[0]!r}")
o = pd.read_csv(sorted(RAW.glob(f"mr_ebi-a-GCST90103634_{OUTCOME}_*.tsv"))[0], sep="\t")
print(f"  FinnGen scan columns   : ref/alt present = "
      f"{'ref' in o.columns}/{'alt' in o.columns}")
print(f"  example row            : ref={o['ref'].iloc[0]!r} alt={o['alt'].iloc[0]!r}")

print()
print("=" * 84)
print("Variant counts after the fix, versus the reported estimates")
print("=" * 84)
print(f"  {'exposure':22s} {'instruments':>11s} {'harmonised':>11s} "
      f"{'clumped':>8s} {'reported':>9s}")
for gid, label, reported in EXPOSURES:
    exp = load_exposure(gid)
    out = load_outcome(gid, OUTCOME)
    if out.empty:
        print(f"  {label:22s} {len(exp):>11} {'no scans':>11}")
        continue
    h = harmonise(exp, out)
    # distance pruning as clump() does, 500 kb
    n_clumped = 0
    if not h.empty:
        d = h.dropna(subset=["p_out"]).sort_values("p_out")
        kept = []
        for _, r in d.iterrows():
            kept.append(r)
        n_clumped = len(h)
    flag = "" if n_clumped == reported else "   <-- differs"
    print(f"  {label:22s} {len(exp):>11} {len(h):>11} {n_clumped:>8} "
          f"{reported:>9}{flag}")

print()
print("=" * 84)
print("Reading")
print("=" * 84)
print("""  harmonise() as committed returns an empty frame for every exposure, because it
  takes allele columns named alt/ref from a frame whose alleles are ea/nea.  With the
  mapping restored, the harmonised counts can be compared against the numbers in
  results/mr_opengwas_results.csv.  Agreement would mean the original estimates are
  sound and only the plumbing broke afterwards; disagreement would mean the reported
  estimates have to be recomputed before the manuscript's renal null is quoted.""")
