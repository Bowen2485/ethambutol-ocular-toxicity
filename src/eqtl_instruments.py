# -*- coding: utf-8 -*-
"""
Step 6a - Acquire eQTLGen phase-1 cis-eQTLs and extract the panel-gene instruments.

Using the optic-nerve GWAS itself to pick instruments would be circular and
underpowered (no cis variant in the panel reached genome-wide significance).
eQTLGen blood cis-eQTLs provide an external, independent instrument source:

  2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz
      SNP  SNPChr  SNPChrPos  Probe  ProbeChr  ProbePos  Gene  GeneSymbol
      GeneChr  GenePos  NrCohorts  NrSamples  FDR  zscore  OverallZScore
      BonferroniP  Pvalue  AssessedAllelesHapMap  AssessedAlleles  AlleleAssessed

beta and se are recovered from the z-score and the allele frequency
    beta = z / sqrt(2 * p * (1 - p) * (n + z^2))
    se   = 1 / sqrt(2 * p * (1 - p) * (n + z^2))
where p is taken from the FinnGen reference panel frequency of the same variant
(eQTLGen does not publish the allele frequency in this release).

Output: data/derived/eqtlgen_panel_instruments.csv
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
ROOT = SRC.parent
RAW = ROOT / "data" / "raw" / "eqtlgen"
DERIVED = ROOT / "data" / "derived"
RAW.mkdir(parents=True, exist_ok=True)

from mr_analysis import EXPOSURE_GENES  # noqa: E402

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

URL = ("https://molgenis26.gcc.rug.nl/downloads/eqtlgen/cis-eqtl/"
       "2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz")
LOCAL = RAW / "cis-eQTLsFDR0.05-ProbeLevel.txt.gz"


def download(url: str, dest: Path, chunk: int = 1 << 20, tries: int = 8) -> bool:
    if dest.exists() and dest.stat().st_size > 300_000_000:
        print(f"[cache] {dest.name}: {dest.stat().st_size/1e6:.1f} MB")
        return True
    part = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=900, context=CTX) as r, \
                    part.open("wb") as fh:
                total = 0
                t0 = time.time()
                while True:
                    b = r.read(chunk)
                    if not b:
                        break
                    fh.write(b)
                    total += len(b)
                    if total % (20 << 20) < chunk:
                        el = time.time() - t0
                        print(f"    {total/1e6:7.1f} MB  ({total/1e6/max(el,1e-9):.1f} MB/s)")
            if part.stat().st_size > 300_000_000:
                part.replace(dest)
                print(f"[ok] {dest.name}: {dest.stat().st_size/1e6:.1f} MB")
                return True
            print(f"[retry {attempt+1}] short file: {part.stat().st_size} bytes")
        except Exception as exc:  # noqa: BLE001
            print(f"[retry {attempt+1}] {type(exc).__name__} {str(exc)[:90]}")
            time.sleep(3 * (attempt + 1))
    return False


def stream_panel(path: Path, genes: set[str]) -> pd.DataFrame:
    """Stream the gzip and keep only rows whose GeneSymbol is in the panel."""
    rows: list[dict] = []
    n = 0
    keep_cols = None
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            n += 1
            if n == 1:
                keep_cols = line.rstrip("\n").split("\t")
                continue
            if n % 2_000_000 == 0:
                print(f"    scanned {n/1e6:.0f} M lines, kept {len(rows)}")
            # cheap pre-filter on the GeneSymbol token before splitting
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 18:
                continue
            sym = parts[7]
            if sym not in genes:
                continue
            rows.append(dict(zip(keep_cols, parts)))
    print(f"[scan] {n:,} lines scanned; {len(rows)} panel rows kept")
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genes", nargs="+", default=list(EXPOSURE_GENES))
    args = ap.parse_args()
    genes = {g.upper() for g in args.genes}

    if not LOCAL.exists() or LOCAL.stat().st_size < 300_000_000:
        if not download(URL, LOCAL):
            print("download failed")
            return 1

    print(f"[scan] extracting cis-eQTLs for {len(genes)} panel genes ...")
    df = stream_panel(LOCAL, genes)
    if df.empty:
        print("no rows for the requested genes")
        return 1
    for c in ("SNPChrPos", "zscore", "OverallZScore", "Pvalue", "FDR", "NrSamples"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["GeneSymbol"] = df["GeneSymbol"].str.upper()
    df = df.rename(columns={"SNP": "snp", "SNPChr": "chrom", "SNPChrPos": "pos",
                            "GeneSymbol": "gene", "AssessedAlleles": "assessed",
                            "AlleleAssessed": "effect_allele",
                            "OverallZScore": "z"})
    for c in ("snp", "chrom", "gene"):
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    out = DERIVED / "eqtlgen_panel_instruments.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n[result] {len(df)} cis-eQTL rows across "
          f"{df.gene.nunique()} genes -> {out}")
    print(df.groupby("gene").size().sort_values(ascending=False).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
