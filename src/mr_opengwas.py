# -*- coding: utf-8 -*-
"""
Step 6 - Two-sample Mendelian randomisation using OpenGWAS instruments.

Run this once an OpenGWAS API token is available:

    python src/mr_opengwas.py --token <TOKEN>

Design
    Ethambutol itself has no genetic instrument (it is an environmental drug
    exposure and no "ethambutol use" GWAS exists), so the MR asks a different,
    answerable question: which of the modifiable traits that the pharmacovigilance
    and network-toxicity steps implicate in ethambutol ocular toxicity are
    causally upstream of the optic-nerve phenotype?

    Exposures (searched on OpenGWAS by trait keyword, restricted to European
    ancestry, sample size >= 10 000, and instruments with p < 5e-8):
        renal function (creatinine, eGFR, cystatin C)   -- ethambutol is renally cleared
        zinc / copper status                            -- zinc-driven lysosomal toxicity
        vitamin B12 / folate / homocysteine              -- nutritional optic neuropathy
        type 2 diabetes / HbA1c                          -- recognised EON risk factor
        smoking                                          -- reported EON risk factor
        alcohol intake                                   -- toxic-nutritional optic neuropathy

    Outcomes (FinnGen R12, tabix-accessed)
        H7_OPTNEURITIS, H7_OPTATROPHY, H7_OPTNERVNAS,
        H7_BLINDANDVISIMPAIRMENT, H7_COULOURVISDEF, H7_VISFIELDDEF

    Estimators
        Wald ratio (1 SNP); IVW with multiplicative random effects; MR-Egger with
        the intercept test; weighted median; Cochran's Q; Steiger directionality.
        LD clumping is delegated to the OpenGWAS API.

Outputs -> results/mr_opengwas_results.csv, results/mr_opengwas_instruments.csv
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
ROOT = SRC.parent
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
RAW = ROOT / "data" / "raw" / "opengwas"
RAW.mkdir(parents=True, exist_ok=True)

from bgzf_tabix import Tabix        # noqa: E402
from mr_analysis import (OUTCOMES, harmonise, run_mr,   # noqa: E402
                         open_tabix, region_scan, parse_lines, _norm_cdf)

GWAS_API = "https://gwas-api.mrcieu.ac.uk"
STATS_API = "https://api.opengwas.io/api"

EXPOSURE_QUERIES = {
    "renal": ["creatinine", "glomerular filtration", "cystatin C", "urea"],
    "zinc_copper": ["zinc", "copper", "ceruloplasmin"],
    "b_vitamins": ["vitamin B12", "folate", "homocysteine"],
    "glycaemia": ["type 2 diabetes", "HbA1c", "fasting glucose", "fasting insulin"],
    "smoking": ["smoking", "cigarettes per day", "ever smoked"],
    "alcohol": ["alcohol", "drinks per week"],
}

HEADERS: dict = {}


def api_get(url: str, tries: int = 4, timeout: int = 180):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode()[:300]
            except Exception:  # noqa: BLE001
                pass
            if exc.code in (401, 403):
                raise RuntimeError(f"OpenGWAS auth failed ({exc.code}): {body}")
            last = f"HTTP {exc.code}: {body}"
            time.sleep(2 * (a + 1))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 * (a + 1))
    raise RuntimeError(f"OpenGWAS request failed: {url} :: {last}")


def api_post(url: str, payload: dict, tries: int = 4, timeout: int = 300):
    body = json.dumps(payload).encode()
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(
                url, data=body, headers={**HEADERS, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode()[:300]
            except Exception:  # noqa: BLE001
                pass
            if exc.code in (401, 403):
                raise RuntimeError(f"OpenGWAS auth failed ({exc.code}): {detail}")
            last = f"HTTP {exc.code}: {detail}"
            time.sleep(2 * (a + 1))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 * (a + 1))
    raise RuntimeError(f"OpenGWAS POST failed: {url} :: {last}")


def find_gwas(term: str, limit: int = 40) -> pd.DataFrame:
    """Locate candidate datasets by trait keyword."""
    q = urllib.parse.quote(term)
    try:
        d = api_get(f"{STATS_API}/gwasinfo?trait={q}&limit={limit}")
    except Exception:
        try:
            d = api_get(f"{GWAS_API}/gwasinfo?trait={q}&limit={limit}")
        except Exception as exc:  # noqa: BLE001
            print(f"  [search] '{term}': {str(exc)[:110]}")
            return pd.DataFrame()
    if isinstance(d, dict):
        rows = [{"id": k, **v} for k, v in d.items()]
    elif isinstance(d, list):
        rows = d
    else:
        rows = []
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    for c in ("sample_size", "ncase", "ncontrol"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "population" in df.columns:
        df = df[df.population.astype(str).str.lower().str.contains("euro", na=True)]
    if "sample_size" in df.columns:
        df = df[df.sample_size.fillna(0) >= 10_000]
    return df


def top_hits(gwas_id: str, p: float = 5e-8, clump_kb: int = 10_000) -> pd.DataFrame:
    """Genome-wide significant, LD-clumped instruments for one dataset."""
    cache = RAW / f"tophits_{gwas_id}_{p:g}_{clump_kb}.tsv"
    if cache.exists():
        return pd.read_csv(cache, sep="\t")
    payload = {"id": [gwas_id], "pval": p, "preclump": True,
               "clump": True, "r2": 0.001, "kb": clump_kb}
    try:
        d = api_post(f"{STATS_API}/tophits", payload)
    except Exception:
        try:
            d = api_post(f"{GWAS_API}/tophits", payload)
        except Exception as exc:  # noqa: BLE001
            print(f"  [tophits] {gwas_id}: {str(exc)[:110]}")
            return pd.DataFrame()
    rows = d if isinstance(d, list) else d.get("data", [])
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df[df.id == gwas_id] if "id" in df.columns else df
    df = df[df.p.notna() & (df.p >= 0)] if "p" in df.columns else df
    keep = [c for c in ("id", "rsid", "chr", "pos", "ea", "nea", "eaf", "beta",
                        "se", "p", "n", "samplesize") if c in df.columns]
    df = df[keep]
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, sep="\t", index=False)
    return df


def finngen_region(tb: Tabix, chrom: str, lo: int, hi: int, tag: str) -> pd.DataFrame:
    cache = RAW / f"out_{tag}.tsv"
    return region_scan(tb, chrom, lo, hi, cache)


def to_harmonise_format(inst: pd.DataFrame, sign_col: str = "beta") -> pd.DataFrame:
    """Reshape an OpenGWAS tophits frame into the columns harmonise() expects."""
    out = pd.DataFrame({
        "chrom": inst["chr"].astype(str),
        "pos": inst["pos"].astype(int),
        "ref": inst["nea"].astype(str).str.upper(),
        "alt": inst["ea"].astype(str).str.upper(),
        "rsids": inst["rsid"].astype(str),
        "beta": pd.to_numeric(inst["beta"], errors="coerce"),
        "sebeta": pd.to_numeric(inst["se"], errors="coerce"),
        "af_alt": pd.to_numeric(inst.get("eaf"), errors="coerce"),
        "pval": pd.to_numeric(inst["p"], errors="coerce"),
    })
    return out.dropna(subset=["beta", "sebeta"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--outcomes", nargs="+", default=list(OUTCOMES))
    ap.add_argument("--p", type=float, default=5e-8)
    args = ap.parse_args()

    HEADERS.update({"Authorization": f"Bearer {args.token}",
                    "User-Agent": "Mozilla/5.0 ethambutol-eon-mr/1.0"})
    print("=" * 78)
    print("STEP 6  two-sample MR with OpenGWAS instruments")
    print("=" * 78)

    # ------------------------------------------------------ 1. exposure datasets
    print("\n[1] searching OpenGWAS for exposure datasets ...")
    chosen: dict[str, dict] = {}
    for family, terms in EXPOSURE_QUERIES.items():
        for term in terms:
            df = find_gwas(term)
            if df.empty:
                continue
            df = df.sort_values("sample_size", ascending=False) if \
                "sample_size" in df.columns else df
            best = df.iloc[0].to_dict()
            key = f"{family}:{term}"
            chosen[key] = best
            print(f"  {key:38s} -> {best.get('id'):16s} "
                  f"n={best.get('sample_size')} {str(best.get('trait'))[:44]}")
            break
    if not chosen:
        print("no exposure datasets found (check the token)")
        return 1

    # -------------------------------------------------------------- 2. outcomes
    print("\n[2] opening FinnGen outcomes ...")
    tbs = {}
    for ph in args.outcomes:
        tb = open_tabix(ph)
        if tb is not None:
            tbs[ph] = tb
    print(f"    {len(tbs)} outcomes available")

    # ------------------------------------------------------------------ 3. MR
    print("\n[3] running MR ...")
    results, inst_rows = [], []
    for key, gwas in chosen.items():
        gid = gwas.get("id")
        if not gid:
            continue
        inst = top_hits(gid, p=args.p)
        if inst.empty:
            print(f"  {key}: no genome-wide significant instruments")
            continue
        print(f"  {key} ({gid}): {len(inst)} independent instruments")
        for _, r in inst.iterrows():
            inst_rows.append({"exposure": key, "gwas_id": gid, **r.to_dict()})
        exp = to_harmonise_format(inst)
        lo, hi = int(exp.pos.min()) - 200_000, int(exp.pos.max()) + 200_000
        chrom = str(exp.iloc[0]["chrom"])
        for ph, tb in tbs.items():
            out = finngen_region(tb, chrom, max(1, lo), hi, f"{gid}_{ph}")
            h = harmonise(exp, out)
            if h.empty:
                continue
            # FinnGen reports beta for ALT; harmonise() already aligned alleles
            res = run_mr(h)
            if not res:
                continue
            res.update({
                "exposure": key, "gwas_id": gid,
                "exposure_trait": gwas.get("trait"),
                "exposure_n": gwas.get("sample_size"),
                "outcome": ph, "outcome_label": OUTCOMES.get(ph, ""),
                "snps": ";".join(h["snp"].astype(str)),
            })
            results.append(res)
            print(f"    {key[:26]:27s} -> {ph:26s} n={res['n_snp']:>2} "
                  f"OR={res.get('or', float('nan')):.3f} p={res.get('p', float('nan')):.3g}")

    if not results:
        print("no MR estimates produced")
        return 1
    df = pd.DataFrame(results)
    if "p" in df.columns:
        ok = df.p.notna()
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
            df["p_fdr"] = np.nan
            df.loc[ok, "p_fdr"] = out
    df.to_csv(RESULTS / "mr_opengwas_results.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(inst_rows).to_csv(RESULTS / "mr_opengwas_instruments.csv",
                                   index=False, encoding="utf-8-sig")
    print(f"\n[done] {len(df)} estimates -> {RESULTS / 'mr_opengwas_results.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
