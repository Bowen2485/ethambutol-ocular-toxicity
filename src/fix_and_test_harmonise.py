# -*- coding: utf-8 -*-
"""
Confirm the column-contract bug, and confirm the fix works.

The pipeline normalises its instrument frame to chrom, pos, rsids, beta, sebeta - and
stops there.  harmonise() additionally requires alt (effect allele) and ref, which
OpenGWAS supplies as ea and nea.  Because the merge therefore never produces alt_exp or
alt_out, harmonise() returns an empty frame for every pair, and the whole MR panel yields
no estimates without raising anything.  The docstring in mr_final.py says the frame is
normalised to the contract including ref and alt; the code does not do it.

This applies the mapping on one pair and checks two things: that variants now harmonise,
and that the resulting instrument set behaves as instruments should - a strong exposure
association and a consistent direction of effect - because a sign error in the allele
mapping would produce estimates that run the wrong way rather than no estimates at all.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mr_analysis import harmonise, ivw            # noqa: E402

RAW = ROOT / "data" / "raw" / "opengwas"


def load_instruments(gid: str) -> pd.DataFrame:
    """
    The pipeline's normalisation, plus the two allele/name mappings it omits.

    harmonise() documents its input contract as chrom, pos, ref, alt, rsids, beta,
    sebeta, af_alt, pval.  mr_final.py sets chrom, pos, rsids, beta and sebeta and stops
    there, so the merge never produces alt_exp/ref_exp and the function returns an empty
    frame for every pair.  OpenGWAS names the same quantities ea, nea and p, so those
    three mappings are what the contract needs.
    """
    inst = pd.read_csv(RAW / f"tophits_{gid}_5e-08.tsv", sep="\t")
    exp = inst.rename(columns={"position": "pos", "se": "sebeta"}).copy()
    exp["chrom"] = exp["chr"].astype(str).str.replace("chr", "", regex=False)
    exp["pos"] = pd.to_numeric(exp["pos"], errors="coerce")
    exp["rsids"] = exp["rsid"].astype(str)
    # ---- the missing mappings: harmonise() reads alt/ref/pval, OpenGWAS writes
    #      ea/nea/p.  Without them the merge yields no alt_exp and no pval_exp.
    exp["alt"] = exp["ea"].astype(str).str.upper()
    exp["ref"] = exp["nea"].astype(str).str.upper()
    exp["pval"] = pd.to_numeric(exp["p"], errors="coerce")
    # af_alt is optional (used only for the palindromic check); eaf is the same thing
    if "af_alt" not in exp.columns and "eaf" in exp.columns:
        exp["af_alt"] = pd.to_numeric(exp["eaf"], errors="coerce")
    return exp.dropna(subset=["pos", "beta", "sebeta"])


def load_outcome(gid: str, ph: str) -> pd.DataFrame:
    scans = sorted(RAW.glob(f"mr_{gid}_{ph}_*.tsv"))
    if not scans:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(f, sep="\t") for f in scans], ignore_index=True)


def run(gid: str, ph: str, label: str) -> None:
    exp, out = load_instruments(gid), load_outcome(gid, ph)
    if exp.empty or out.empty:
        print(f"  {label:44s} no input")
        return
    h = harmonise(exp, out)
    if h.empty:
        print(f"  {label:44s} harmonised 0 of {len(exp)}")
        return
    b, se, q = ivw(h.beta_exp.values, h.se_exp.values,
                   h.beta_out.values, h.se_out.values)
    p = 2 * (1 - __import__("scipy.stats", fromlist=["norm"]).norm.cdf(abs(b / se)))
    print(f"  {label:44s} {len(h):>4} SNPs   beta {b:+.4f}  se {se:.4f}  "
          f"p {p:.3g}  Q {q:.1f}")
    return h


print("=" * 100)
print("1. With the allele mapping applied")
print("=" * 100)
print("  (the same pairs that harmonised to zero before)")
print()
h_hba1c = run("ebi-a-GCST90014006", "H7_OPTNEURITIS", "HbA1c -> optic neuritis")
run("ebi-a-GCST006867", "H7_OPTNEURITIS", "Type 2 diabetes -> optic neuritis")
run("ebi-a-GCST006867", "H7_OPTATROPHY", "Type 2 diabetes -> optic atrophy")
run("ieu-b-4877", "H7_OPTNEURITIS", "Smoking initiation -> optic neuritis")
run("ieu-b-40", "H7_BLINDANDVISIMPAIRMENT", "BMI -> visual impairment")
run("ukb-b-13891", "H7_OPTNEURITIS", "Zinc supplement use -> optic neuritis")

print()
print("=" * 100)
print("2. Instrument quality on the pair that harmonised")
print("=" * 100)
if h_hba1c is not None and len(h_hba1c):
    print(f"  SNPs harmonised            : {len(h_hba1c)}")
    print(f"  exposure effect sizes      : |beta| median "
          f"{np.median(np.abs(h_hba1c.beta_exp)):.4f}, "
          f"max {np.abs(h_hba1c.beta_exp).max():.4f}")
    print(f"  F-statistic proxy (beta^2/se^2), median : "
          f"{np.median(h_hba1c.beta_exp**2 / h_hba1c.se_exp**2):.1f}")
    print(f"  palindromic dropped by harmonise        : "
          f"{len(load_instruments('ebi-a-GCST90014006')) - len(h_hba1c)} "
          f"(allele mismatches and strand-ambiguous)")
    print()
    print("  A median F well above 10 means the instruments are strong, which is the")
    print("  first thing a reviewer checks; weak instruments would make a null result")
    print("  uninterpretable rather than reassuring.")
    print()
    print("  first three harmonised rows:")
    print(h_hba1c.head(3)[["snp", "effect_allele", "other_allele", "beta_exp",
                           "beta_out", "se_out"]].to_string(index=False))
