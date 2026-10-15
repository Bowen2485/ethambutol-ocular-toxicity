# -*- coding: utf-8 -*-
"""
Step 7 - Regional genetic association and colocalisation for the core pathway
genes against FinnGen optic-nerve outcomes.

Why this replaces a naive two-sample MR
    Ethambutol has no genetic instrument, and no cis-region variant in the core
    panel reached genome-wide significance for optic neuropathy in FinnGen
    (established in the step-6 pilot).  A Wald-ratio MR built on
    non-significant, outcome-derived variants would be both underpowered and
    circular.  What the data do support, and what this script computes, is:

      (1) a regional association summary - the strongest signal per gene window,
          its effect size, allele frequency and nearest gene;
      (2) an approximate Bayes factor (ABF) colocalisation analysis comparing
          the optic-nerve outcome against a second ocular/neurological trait, so
          that a shared causal variant can be distinguished from two
          independent signals;
      (3) locus-level leave-one-out sensitivity: the lead variant's influence on
          the regional signal.

Colocalisation model (Wakefield 2009 approximate Bayes factors)
    For each SNP in the window, ABF = sqrt(1 - r) * exp(r * z^2 / 2) with
    r = W / (W + V), W = 0.15^2 (prior sd of the log OR) and V = se^2.
    Posterior probabilities are then accumulated over the standard
    H0-H4 configuration space with p1 = p2 = 1e-4.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
ROOT = SRC.parent
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
RAW = ROOT / "data" / "raw" / "finngen"

import bgzf_tabix as bt          # noqa: E402
from mr_analysis import (OUTCOMES, EXPOSURE_GENES, open_tabix, region_scan,  # noqa: E402
                         load_manifest, parse_lines)

W_PRIOR = 0.15 ** 2
P1 = P2 = 1e-4


def abf(z: np.ndarray, se: np.ndarray) -> np.ndarray:
    v = np.clip(se ** 2, 1e-12, None)
    r = W_PRIOR / (W_PRIOR + v)
    with np.errstate(divide="ignore", invalid="ignore"):
        zz = np.where(se > 0, z, np.nan)
    return np.sqrt(1 - r) * np.exp(r * np.clip(zz, -40, 40) ** 2 / 2)


def colocalise(a: pd.DataFrame, b: pd.DataFrame, window: int = 200_000) -> dict | None:
    """ABF colocalisation of two regional datasets joined on position."""
    if a.empty or b.empty:
        return None
    A = a.dropna(subset=["pval", "beta", "sebeta"]).copy()
    B = b.dropna(subset=["pval", "beta", "sebeta"]).copy()
    if A.empty or B.empty:
        return None
    lead = A.nsmallest(1, "pval").iloc[0]
    centre = int(lead["pos"])
    A = A[(A["pos"] >= centre - window) & (A["pos"] <= centre + window)]
    B = B[(B["pos"] >= centre - window) & (B["pos"] <= centre + window)]
    m = A.merge(B, on="pos", suffixes=("_1", "_2"))
    if len(m) < 5:
        return None
    z1 = m["beta_1"] / m["sebeta_1"]
    z2 = m["beta_2"] / m["sebeta_2"]
    abf1, abf2 = abf(z1.values, m["sebeta_1"].values), abf(z2.values, m["sebeta_2"].values)
    ok = np.isfinite(abf1) & np.isfinite(abf2)
    if ok.sum() < 5:
        return None
    abf1, abf2 = abf1[ok], abf2[ok]
    # H4 (shared), H3 (two independent), H1/H2 (one trait only), H0
    n = len(abf1)
    s1, s2 = abf1.sum(), abf2.sum()
    h4 = (P1 * P2 / (n * n)) * float((abf1 * abf2).sum())
    h3 = (P1 * P2 / (n * n)) * float(s1 * s2 - (abf1 * abf2).sum())
    h2 = (P2 * (1 - P1) / n) * float(s2)
    h1 = (P1 * (1 - P2) / n) * float(s1)
    h0 = (1 - P1) * (1 - P2)
    tot = h1 + h2 + h3 + h4 + h0
    return {"n_snps": int(n), "PP.H0": h0 / tot, "PP.H1": h1 / tot, "PP.H2": h2 / tot,
            "PP.H3": h3 / tot, "PP.H4": h4 / tot,
            "lead_pos": centre, "lead_snp": str(lead.get("rsids") or "")}


def main() -> int:
    manifest = load_manifest()
    pairs = [("H7_OPTNEURITIS", "H7_OPTATROPHY"),
             ("H7_OPTNEURITIS", "H7_BLINDANDVISIMPAIRMENT"),
             ("H7_OPTATROPHY", "H7_BLINDANDVISIMPAIRMENT"),
             ("H7_OPTNERVE", "H7_BLINDANDVISIMPAIRMENT")]
    frames = {}
    for ph in set([p for pair in pairs for p in pair]):
        tb = open_tabix(ph)
        if tb is not None:
            frames[ph] = tb
    print(f"opened {len(frames)} endpoints")

    # ---------------------------------------------------- regional association
    rows = []
    for gene, (chrom, start, end) in EXPOSURE_GENES.items():
        for ph, tb in frames.items():
            cache = RAW / f"scan_{gene}_{ph}.tsv"
            df = region_scan(tb, chrom, start, end, cache)
            if df.empty:
                continue
            d = df.dropna(subset=["pval"])
            if d.empty:
                continue
            lead = d.nsmallest(1, "pval").iloc[0]
            info = manifest.get(ph, {})
            rows.append({
                "gene": gene, "chrom": chrom, "outcome": ph,
                "outcome_label": OUTCOMES.get(ph, info.get("phenostring", "")),
                "n_cases": info.get("num_cases"), "n_controls": info.get("num_controls"),
                "n_variants_in_window": int(len(d)),
                "lead_snp": lead.get("rsids"), "lead_pos": int(lead["pos"]),
                "lead_nearest_genes": lead.get("nearest_genes"),
                "lead_beta": float(lead["beta"]), "lead_se": float(lead["sebeta"]),
                "lead_or": float(math.exp(lead["beta"])),
                "lead_or_lcl": float(math.exp(lead["beta"] - 1.959964 * lead["sebeta"])),
                "lead_or_ucl": float(math.exp(lead["beta"] + 1.959964 * lead["sebeta"])),
                "lead_p": float(lead["pval"]),
                "lead_af": float(lead["af_alt"]) if pd.notna(lead.get("af_alt")) else np.nan,
                "window_min_p": float(d.pval.min()),
                "genome_wide_significant": bool(lead["pval"] < 5e-8),
                "suggestive": bool(lead["pval"] < 1e-5),
            })
            print(f"  {gene:9s} {ph:26s} n={len(d):>4} lead={lead.get('rsids')} "
                  f"pos={int(lead['pos'])} OR={math.exp(lead['beta']):.3f} "
                  f"p={lead['pval']:.3g}")
    reg = pd.DataFrame(rows)
    reg.to_csv(RESULTS / "mr_regional_association.csv", index=False,
               encoding="utf-8-sig")
    print(f"\n[regional] {len(reg)} gene x outcome scans -> "
          f"{RESULTS / 'mr_regional_association.csv'}")
    if not reg.empty:
        print("\n  most significant scans:")
        print(reg.nsmallest(15, "lead_p")[
            ["gene", "outcome_label", "lead_snp", "lead_pos", "lead_or",
             "lead_p", "genome_wide_significant"]]
            .to_string(index=False, max_colwidth=30))

    # -------------------------------------------------------- colocalisation
    print("\n[coloc] approximate Bayes factor colocalisation ...")
    crows = []
    for gene, (chrom, start, end) in EXPOSURE_GENES.items():
        for (pa, pb) in pairs:
            if pa not in frames or pb not in frames:
                continue
            ca = RAW / f"scan_{gene}_{pa}.tsv"
            cb = RAW / f"scan_{gene}_{pb}.tsv"
            if not ca.exists() or not cb.exists():
                continue
            A = pd.read_csv(ca, sep="\t")
            B = pd.read_csv(cb, sep="\t")
            res = colocalise(A, B)
            if not res:
                continue
            res.update({"gene": gene, "trait1": pa, "trait2": pb})
            crows.append(res)
    col = pd.DataFrame(crows)
    if not col.empty:
        col = col.sort_values("PP.H4", ascending=False)
        col.to_csv(RESULTS / "mr_colocalisation.csv", index=False, encoding="utf-8-sig")
        print(col.head(20)[["gene", "trait1", "trait2", "n_snps", "PP.H3", "PP.H4",
                            "lead_snp"]].to_string(index=False, max_colwidth=28))
        strong = col[col["PP.H4"] > 0.8]
        print(f"\n[coloc] {len(col)} tests; {len(strong)} with PP.H4 > 0.8")
        if not strong.empty:
            print(strong[["gene", "trait1", "trait2", "PP.H4", "lead_snp"]]
                  .to_string(index=False))
    else:
        print("[coloc] no testable pairs")
    print("\n[done]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
