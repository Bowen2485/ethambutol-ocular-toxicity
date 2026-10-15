# -*- coding: utf-8 -*-
"""
Compute the MR estimates that the cache already supports but that were never produced.

What was found
    results/mr_scan_coverage.csv records zero harmonised instruments for serum
    creatinine, HbA1c, smoking initiation, cigarettes per day, alcohol intake, zinc
    supplement use and body mass index, so the published renal null rests on eGFR and
    cystatin C alone.

    Running the pipeline's own harmonise() on the cached scans shows that two of those
    zeros were not properties of the data:
        eGFR              151 harmonised   (reported 150)
        Cystatin C        162 harmonised   (reported 146)
        Serum creatinine  186 harmonised   (reported 0)
    Serum creatinine shares its instrument regions with eGFR and cystatin C, so its
    outcome scans were already on disk.  It can therefore be completed with no network
    access at all, and doing so adds a second renal exposure to the null.

    The remaining seven exposures have no cached scans, because no run ever scanned
    their regions.  They need HTTP range requests against the FinnGen bucket and cannot
    be finished here.

What this does
    Runs the pipeline's own harmonise() and run_mr() - imported, not reimplemented - over
    the cached scans for the exposures that have them, and writes
    results/mr_supplementary_results.csv in the same shape as the published file.

Usage
    python src/run_mr_supplementary.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"
RESULTS = ROOT / "results"

from mr_analysis import OUTCOMES, harmonise, run_mr  # noqa: E402

EXPOSURES = [
    ("ebi-a-GCST90103634", "eGFR (creatinine)", 1_004_040),
    ("ebi-a-GCST90025945", "Cystatin C", 437_846),
    ("ebi-a-GCST90025946", "Serum creatinine", 437_660),
]
OUTCOME_KEYS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
                "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]


def build_exposure(gid: str) -> pd.DataFrame:
    """Exactly the transformation mr_final.py applies before harmonise()."""
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
    exp["pval"] = (pd.to_numeric(exp["p"], errors="coerce")
                   if "p" in exp.columns else pd.NA)
    return exp.dropna(subset=["pos", "beta", "sebeta"])


def main() -> int:
    rows = []
    for gid, label, n_exp in EXPOSURES:
        exp = build_exposure(gid)
        if exp.empty:
            print(f"  {label:22s} no instruments")
            continue
        print(f"\n  {label}  ({len(exp)} instruments, already LD-clumped by OpenGWAS)")
        for ph in OUTCOME_KEYS:
            files = sorted(RAW.glob(f"mr_{gid}_{ph}_*.tsv"))
            if not files:
                print(f"    {ph:28s} no cached scans")
                continue
            out = pd.concat((pd.read_csv(f, sep="\t") for f in files),
                            ignore_index=True)
            h = harmonise(exp, out)
            if h.empty:
                print(f"    {ph:28s} nothing harmonised from {len(out):,} variants")
                continue
            res = run_mr(h)
            if not res:
                print(f"    {ph:28s} {len(h)} variants, no estimate")
                continue
            res.update({
                "exposure": label, "gwas_id": gid, "exposure_n": n_exp,
                "outcome": ph, "outcome_label": OUTCOMES.get(ph, ""),
                "snps": ";".join(h["snp"].astype(str)),
            })
            rows.append(res)
            print(f"    {ph:28s} n={res.get('n_snp'):>4}  beta={res.get('beta'):+.4f}  "
                  f"p={res.get('p'):.4g}")

    if not rows:
        print("\nno estimates produced")
        return 1

    df = pd.DataFrame(rows)
    # the published file keeps one estimate per exposure-outcome, the one with the most
    # instruments; reproduce that so the two files are directly comparable
    df = (df.sort_values("n_snp", ascending=False)
            .drop_duplicates(["exposure", "outcome"], keep="first")
            .reset_index(drop=True))
    if "p" in df.columns:
        ok = df["p"].notna() & (df["n_snp"] > 0)
        try:
            from statsmodels.stats.multitest import multipletests
            if ok.any():
                df.loc[ok, "p_fdr"] = multipletests(df.loc[ok, "p"], method="fdr_bh")[1]
        except Exception:  # noqa: BLE001
            m = int(ok.sum())
            if m:
                order = df.loc[ok, "p"].rank(method="first")
                df.loc[ok, "p_fdr"] = (df.loc[ok, "p"] * m / order).clip(upper=1.0)

    out_p = RESULTS / "mr_supplementary_results.csv"
    cols = list(df.columns)
    front = [c for c in ("exposure", "gwas_id", "outcome", "outcome_label", "n_snp",
                         "beta", "se", "p", "p_fdr", "or", "or_lcl", "or_ucl")
             if c in cols]
    df = df[front + [c for c in cols if c not in front]]
    df.to_csv(out_p, index=False, encoding="utf-8-sig")
    print(f"\n-> {out_p}  ({len(df)} estimates)")

    print("\n" + "=" * 84)
    print("Summary: exposure x outcome")
    print("=" * 84)
    piv = df.pivot_table(index="exposure", columns="outcome", values="n_snp",
                         aggfunc="max")
    print(piv.to_string())
    print()
    print("  Every p above is the IVW estimate.  Compare with the published file for the")
    print("  exposures it already covered; the new row is serum creatinine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
