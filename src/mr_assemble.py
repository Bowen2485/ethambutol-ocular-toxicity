# -*- coding: utf-8 -*-
"""
Step 6d - Assemble the MR estimates from the cached regional scans.

The tabix reader is fixed and roughly 3,100 regional scans (15.6 million FinnGen
variants) are already on disk.  Re-running the whole fetch loop is unnecessary and
slow, so this script rebuilds the exposure-outcome estimates directly from the
cache: for every instrument it finds the cached scan covering its genomic
position, harmonises the alleles, and runs the estimators.  Missing windows are
reported rather than silently ignored.

Outputs -> results/mr_opengwas_results.csv, results/mr_opengwas_instruments.csv,
           results/mr_scan_coverage.csv
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
ROOT = SRC.parent
RAW = ROOT / "data" / "raw" / "opengwas"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

from mr_analysis import harmonise, run_mr        # noqa: E402

EXPOSURE_LABELS = {
    "ebi-a-GCST90103634": "eGFR (creatinine)",
    "ebi-a-GCST90025945": "Cystatin C",
    "ebi-a-GCST90025946": "Serum creatinine",
    "ebi-a-GCST006867": "Type 2 diabetes",
    "ebi-a-GCST90014006": "HbA1c",
    "ieu-b-4877": "Smoking initiation",
    "ieu-b-25": "Cigarettes per day",
    "ieu-b-73": "Alcoholic drinks per week",
    "ukb-b-13891": "Zinc supplement use",
    "ieu-b-40": "Body mass index",
}
OUTCOME_LABELS = {
    "H7_OPTNEURITIS": "Optic neuritis",
    "H7_OPTATROPHY": "Optic atrophy",
    "H7_OPTNERVNAS": "Disorders of optic nerve, NEC",
    "H7_BLINDANDVISIMPAIRMENT": "Visual impairment including blindness",
    "H7_COULOURVISDEF": "Colour vision deficiencies",
    "H7_VISFIELDDEF": "Visual field defects",
}

SCAN_RE = re.compile(
    r"^mr(?:w|big)?_(?P<gwas>.+)_(?P<outcome>H7_[A-Z]+)_(?P<chrom>[0-9XY]+)_(?P<wi>\d+)\.tsv$")


def load_scans() -> dict[tuple[str, str, str], list[Path]]:
    """
    Index the cached regional scans by (exposure id, outcome, chromosome).

    Two cache layouts are understood: the per-window files written by
    mr_fetch_scoped.py (`mrw_<gwas>_<outcome>_<chrom>_<window>.tsv`) and the
    earlier per-chromosome files (`mr_<gwas>_<outcome>_<chrom>_<window>.tsv`).
    Both carry the same columns.
    """
    out: dict[tuple[str, str, str], list[Path]] = {}
    patterns = ["mrw_*.tsv", "mr_*.tsv"]
    for pat in patterns:
        for f in RAW.glob(pat):
            m = SCAN_RE.match(f.name)
            if not m:
                continue
            key = (m.group("gwas"), m.group("outcome"), m.group("chrom"))
            out.setdefault(key, []).append(f)
    return out


def load_scan(paths: list[Path], chrom: str) -> pd.DataFrame:
    frames = []
    for p in paths:
        if p.stat().st_size <= 1:
            continue
        try:
            frames.append(pd.read_csv(p, sep="\t"))
        except Exception:  # noqa: BLE001
            continue
    if not frames:
        return pd.DataFrame()
    d = pd.concat(frames, ignore_index=True)
    d = d[d["chrom"].astype(str) == str(chrom)]
    return d.drop_duplicates(subset=["pos"])


def main() -> int:
    scans = load_scans()
    print(f"[cache] {sum(len(v) for v in scans.values())} scan files across "
          f"{len(scans)} (exposure, outcome, chromosome) groups")

    # normalise the instrument files once
    inst_frames: dict[str, pd.DataFrame] = {}
    for f in sorted(RAW.glob("tophits_*.tsv")):
        d = pd.read_csv(f, sep="\t")
        if d.empty:
            continue
        gid = str(d["id"].iloc[0]) if "id" in d.columns else \
            f.name[len("tophits_"):-len("_5e-08.tsv")]
        d = d.copy()
        d["chrom"] = d["chr"].astype(str).str.replace("chr", "", regex=False)
        d["pos"] = pd.to_numeric(d["pos"], errors="coerce")
        d["alt"] = d["ea"].astype(str).str.upper()
        d["ref"] = d["nea"].astype(str).str.upper()
        d["rsids"] = d["rsid"].astype(str)
        d["beta"] = pd.to_numeric(d["beta"], errors="coerce")
        d["sebeta"] = pd.to_numeric(d["sebeta"], errors="coerce")
        d["af_alt"] = pd.to_numeric(d.get("eaf"), errors="coerce")
        d["pval"] = pd.to_numeric(d.get("p"), errors="coerce")
        d = d.dropna(subset=["pos", "beta", "sebeta"])
        inst_frames[gid] = d
    print(f"[instruments] {len(inst_frames)} exposure datasets")

    results, coverage = [], []
    for gid, inst in inst_frames.items():
        label = EXPOSURE_LABELS.get(gid, gid)
        for outcome in OUTCOME_LABELS:
            harmonised: list[pd.DataFrame] = []
            missing_total = 0
            for chrom, grp in inst.groupby("chrom"):
                paths = scans.get((gid, outcome, str(chrom)))
                if not paths:
                    missing_total += len(grp)
                    continue
                out = load_scan(paths, str(chrom))
                if out.empty:
                    missing_total += len(grp)
                    continue
                h = harmonise(grp, out)
                if not h.empty:
                    harmonised.append(h)
                missing_total += len(grp) - len(h)
            coverage.append({"exposure": label, "gwas_id": gid,
                             "outcome": outcome, "instruments": len(inst),
                             "harmonised": sum(len(h) for h in harmonised),
                             "not_found": missing_total})
            if not harmonised:
                continue
            # ONE estimate per exposure-outcome pair, from every instrument that
            # could be harmonised across all windows (not one estimate per window)
            allh = (pd.concat(harmonised, ignore_index=True)
                      .drop_duplicates(subset=["snp"]))
            res = run_mr(allh)
            if not res:
                continue
            res.update({
                "exposure": label, "gwas_id": gid, "outcome": outcome,
                "outcome_label": OUTCOME_LABELS[outcome],
                "snps": ";".join(allh["snp"].astype(str)[:40]),
            })
            results.append(res)

    cov = pd.DataFrame(coverage)
    cov.to_csv(RESULTS / "mr_scan_coverage.csv", index=False, encoding="utf-8-sig")
    print(f"\n[coverage] overall harmonisation rate: "
          f"{cov.harmonised.sum()}/{cov.instruments.sum()} = "
          f"{100 * cov.harmonised.sum() / max(cov.instruments.sum(), 1):.1f}%")
    print(cov.groupby("exposure")[["instruments", "harmonised"]].sum().to_string())

    if not results:
        print("\nno estimates could be assembled from the cache")
        return 1
    df = pd.DataFrame(results)
    ok = df["p"].notna()
    df["p_fdr"] = np.nan
    if ok.any():
        p = df.loc[ok, "p"].values
        order = np.argsort(p)
        m = len(p)
        q, prev = np.empty(m), 1.0
        for k in range(m - 1, -1, -1):
            prev = min(prev, p[order][k] * m / (k + 1))
            q[k] = prev
        out = np.empty(m)
        out[order] = q
        df.loc[ok, "p_fdr"] = out
    df = df.sort_values(["outcome", "p"])
    df.to_csv(RESULTS / "mr_opengwas_results.csv", index=False,
              encoding="utf-8-sig")
    print(f"\n[done] {len(df)} estimates -> {RESULTS / 'mr_opengwas_results.csv'}")
    show = df[df.p.notna() & (df.n_snp >= 3)].head(40)
    if not show.empty:
        print(show[["exposure", "outcome_label", "n_snp", "method", "or",
                    "or_lcl", "or_ucl", "p", "p_fdr", "egger_intercept_p",
                    "steiger_correct"]]
              .to_string(index=False, max_colwidth=26))
    else:
        print("no estimate used >= 3 instruments; showing all:")
        print(df.head(30)[["exposure", "outcome_label", "n_snp", "method", "or",
                           "p"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
