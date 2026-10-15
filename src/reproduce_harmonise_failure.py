# -*- coding: utf-8 -*-
"""
Replicate the harmonisation path on the real files to find where serum creatinine dies.

Established so far
    * the instruments are cached for all ten exposures
    * serum creatinine's cached FinnGen scans are healthy: 1,477 files, 10.4 million
      variant rows, no empty files
    * 190 of its 370 instruments are present in its own scans by rsID, a higher rate
      than eGFR's 151 of 342
    * yet the pipeline harmonised 0 for serum creatinine and 150 for eGFR
    * the exposure metadata is the same shape for both: id, trait, chr, pos, rsid, ea,
      nea, eaf, beta, sebeta, p, n

    So the failure is inside harmonise().  Reading it, three column names are taken
    from the exposure frame that the instrument files do not have: alt, ref (lines
    250-251) and pval (line 274).  mr_final.py renames rsid->rsids, and copies beta,
    sebeta, af_alt and pval across, but it never creates alt or ref.

    This script reproduces each step on the real files and reports where the count
    reaches zero, so the fix is based on observation rather than inference.

Usage
    python src/reproduce_harmonise_failure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"

PAIRS = [("ebi-a-GCST90103634", "eGFR (creatinine)"),
         ("ebi-a-GCST90025946", "Serum creatinine")]

print("=" * 84)
print("1. Exposure frame as mr_final.py builds it")
print("=" * 84)
frames = {}
for gid, label in PAIRS:
    p = RAW / f"tophits_{gid}_5e-08.tsv"
    exp = pd.read_csv(p, sep="\t")
    # exactly what mr_final.py does before calling harmonise
    exp["rsids"] = exp["rsid"].astype(str)
    exp["beta"] = pd.to_numeric(exp["beta"], errors="coerce")
    exp["sebeta"] = pd.to_numeric(exp["sebeta"], errors="coerce")
    exp["af_alt"] = pd.to_numeric(exp.get("eaf"), errors="coerce")
    if "p" in exp.columns:
        exp["pval"] = pd.to_numeric(exp["p"], errors="coerce")
    exp["chrom"] = exp["chr"]
    exp = exp.dropna(subset=["pos", "beta", "sebeta"])
    frames[gid] = exp
    print(f"  {label:22s} {len(exp):>4} rows")
    print(f"      columns: {list(exp.columns)}")
    for c in ("alt", "ref", "ea", "nea"):
        print(f"      has {c!r}: {c in exp.columns}")

print()
print("=" * 84)
print("2. Outcome frame from a cached scan")
print("=" * 84)
for gid, label in PAIRS:
    files = sorted(RAW.glob(f"mr_{gid}_H7_OPTNEURITIS_*.tsv"))
    if not files:
        print(f"  {label:22s} no scan")
        continue
    d = pd.read_csv(files[0], sep="\t")
    print(f"  {label:22s} {files[0].name}: {len(d)} rows")
    print(f"      columns: {list(d.columns)}")

print()
print("=" * 84)
print("3. Step through harmonise() on real data")
print("=" * 84)

# take one scan per exposure, chosen as the window holding the most instruments
for gid, label in PAIRS:
    exp = frames[gid]
    files = sorted(RAW.glob(f"mr_{gid}_H7_OPTNEURITIS_*.tsv"))
    if not files:
        continue
    # use the scan with the most rows so the test is not limited by window size
    best, best_n = None, -1
    for f in files[:40]:
        try:
            n = sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001
            continue
        if n > best_n:
            best, best_n = f, n
    out = pd.read_csv(best, sep="\t")
    print(f"\n  {label}   (scan {best.name}, {len(out)} rows)")

    ex, ou = exp.copy(), out.copy()
    ex["rs_key"] = ex.get("rsids", pd.Series(dtype=str)).astype(str).str.strip()
    ou["rs_key"] = ou.get("rsids", pd.Series(dtype=str)).astype(str).str.strip()
    ex["pos_key"] = ex["chrom"].astype(str) + ":" + ex["pos"].astype(int).astype(str)
    ou["pos_key"] = ou["chrom"].astype(str) + ":" + ou["pos"].astype(int).astype(str)
    ou["rs_key"] = ou["rs_key"].str.split(";")
    ou = ou.explode("rs_key")
    ou["rs_key"] = ou["rs_key"].astype(str).str.strip()

    usable = ex[ex["rs_key"].notna() & (ex["rs_key"] != "") & (ex["rs_key"] != "nan")]
    print(f"      usable exposure rows        : {len(usable)}")
    m_rs = usable.merge(ou, on="rs_key", suffixes=("_exp", "_out"))
    print(f"      after rsID merge            : {len(m_rs)}")
    m_pos = ex.merge(ou, on="pos_key", suffixes=("_exp", "_out"))
    print(f"      after position merge        : {len(m_pos)}")

    frames_m = [f for f in (m_rs, m_pos) if not f.empty]
    if not frames_m:
        print("      -> no frames to concatenate: harmonise returns empty here")
        continue
    m = pd.concat(frames_m, ignore_index=True)
    if "snp_key" not in m.columns:
        # harmonise sets snp_key on each frame before concatenating
        for fr in frames_m:
            if fr is m_rs and not fr.empty:
                fr["snp_key"] = fr["pos_key_exp"]
            elif not fr.empty:
                fr["snp_key"] = fr["pos_key"]
        m = pd.concat(frames_m, ignore_index=True)
    m = m.drop_duplicates(subset=["snp_key"])
    print(f"      after dedup                 : {len(m)}")
    print(f"      has alt_exp/alt_out columns : "
          f"{'alt_exp' in m.columns}/{'alt_out' in m.columns}")
    if "alt_exp" not in m.columns or "alt_out" not in m.columns:
        print("      -> harmonise returns empty at its column guard (line 238-239)")
        print(f"         columns present: {sorted(m.columns)}")
        continue

    kept = 0
    pal = 0
    mism = 0
    for _, r in m.iterrows():
        a1e, a2e = str(r["alt_exp"]).upper(), str(r["ref_exp"]).upper()
        a1o, a2o = str(r["alt_out"]).upper(), str(r["ref_out"]).upper()
        comp = {"A": "T", "T": "A", "C": "G", "G": "C"}
        if comp.get(a1e) == a2e:
            eaf = r.get("af_alt_exp", np.nan)
            try:
                eaf = float(eaf)
            except (TypeError, ValueError):
                eaf = np.nan
            if not (np.isfinite(eaf) and (eaf < 0.42 or eaf > 0.58)):
                pal += 1
                continue
        if (a1e, a2e) == (a1o, a2o) or (a1e, a2e) == (a2o, a1o):
            kept += 1
        else:
            mism += 1
    print(f"      allele-compatible kept      : {kept}")
    print(f"      dropped palindromic         : {pal}")
    print(f"      dropped allele mismatch     : {mism}")
    if kept:
        r0 = m.iloc[0]
        print(f"      sample row keys -> alt_exp={r0.get('alt_exp')!r} "
              f"ref_exp={r0.get('ref_exp')!r} beta_exp={r0.get('beta_exp')!r} "
              f"pval_exp={r0.get('pval_exp')!r}")
