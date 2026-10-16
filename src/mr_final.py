# -*- coding: utf-8 -*-
"""
Step 6 - Two-sample Mendelian randomisation: modifiable exposures -> optic-nerve
phenotypes in FinnGen R12.

Question
    Ethambutol has no genetic instrument, so a drug-exposure MR is impossible.
    The answerable question is which modifiable traits that the pharmacovigilance
    and network-toxicity steps implicate in ethambutol ocular toxicity lie
    causally upstream of the optic-nerve phenotype.

Exposures (chosen from the OpenGWAS catalogue: European ancestry, MR-eligible,
n >= 10 000, largest available per trait)
    eGFR (creatinine)          ebi-a-GCST90103634   n = 1 004 040   renal clearance
    Cystatin C                 ebi-a-GCST90025945   n =   437 846
    Serum creatinine           ebi-a-GCST90025946   n =   437 660
    Type 2 diabetes            ebi-a-GCST006867     n =   655 666   recognised EON risk
    HbA1c                      ebi-a-GCST90014006   n =   389 889
    Smoking initiation         ieu-b-4877           n =   607 291   reported EON risk
    Cigarettes per day         ieu-b-25             n =   337 334
    Alcoholic drinks per week  ieu-b-73             n =   335 394
    Zinc supplement use        ukb-b-13891          n =   461 384   zinc-lysosome axis
    Vitamin B12 preparation    ukb-b-18819          n =   462 933   nutritional optic neuropathy
    Body mass index            ieu-b-40             n =   681 275   positive control

Outcomes (FinnGen R12, tabix-accessed with the local BGZF reader)
    H7_OPTNEURITIS, H7_OPTATROPHY, H7_OPTNERVNAS, H7_BLINDANDVISIMPAIRMENT,
    H7_COULOURVISDEF, H7_VISFIELDDEF

Estimators: Wald ratio, IVW (multiplicative random effects), MR-Egger with the
intercept test, weighted median, Cochran's Q, Steiger directionality.
Instruments: p < 5e-8 with LD clumping delegated to the OpenGWAS API.

Outputs -> results/mr_opengwas_results.csv, results/mr_opengwas_instruments.csv
"""
from __future__ import annotations

import http.client
import json
import math
import ssl
import sys
import time
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

from bgzf_tabix import Tabix                                    # noqa: E402
from mr_analysis import (OUTCOMES, harmonise, run_mr,            # noqa: E402
                         open_tabix, region_scan)

TOKEN = (RAW / "token.txt").read_text(encoding="utf-8").strip()
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HOST = "api.opengwas.io"

EXPOSURES: dict[str, dict] = {
    "eGFR_creatinine": {"id": "ebi-a-GCST90103634", "n": 1_004_040,
                        "label": "Estimated glomerular filtration rate (creatinine)"},
    "cystatin_C": {"id": "ebi-a-GCST90025945", "n": 437_846,
                   "label": "Cystatin C levels"},
    "serum_creatinine": {"id": "ebi-a-GCST90025946", "n": 437_660,
                         "label": "Creatinine levels"},
    "type_2_diabetes": {"id": "ebi-a-GCST006867", "n": 655_666,
                        "label": "Type 2 diabetes"},
    "HbA1c": {"id": "ebi-a-GCST90014006", "n": 389_889,
              "label": "Glycated haemoglobin HbA1c"},
    "smoking_initiation": {"id": "ieu-b-4877", "n": 607_291,
                           "label": "Smoking initiation"},
    "cigarettes_per_day": {"id": "ieu-b-25", "n": 337_334,
                           "label": "Cigarettes per day"},
    "alcohol_drinks_week": {"id": "ieu-b-73", "n": 335_394,
                            "label": "Alcoholic drinks per week"},
    "zinc_supplement": {"id": "ukb-b-13891", "n": 461_384,
                        "label": "Zinc dietary supplement use"},
    "vitamin_B12": {"id": "ukb-b-18819", "n": 462_933,
                    "label": "Vitamin B12 preparation use"},
    "body_mass_index": {"id": "ieu-b-40", "n": 681_275,
                        "label": "Body mass index (positive control)"},
}

OUTCOME_ORDER = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
                 "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]


def api(path: str, method: str = "GET", body=None, timeout: int = 300,
        tries: int = 5) -> bytes:
    last = None
    for a in range(tries):
        conn = None
        try:
            conn = http.client.HTTPSConnection(HOST, 443, timeout=timeout, context=CTX)
            h = {"User-Agent": "Mozilla/5.0", "Connection": "close",
                 "Accept": "application/json",
                 "Authorization": f"Bearer {TOKEN}"}
            if body is not None:
                h["Content-Type"] = "application/json"
            conn.request(method, path, body=body, headers=h)
            r = conn.getresponse()
            data = r.read()
            if r.status == 429:
                wait = int(r.getheader("Retry-After") or 30)
                print(f"      throttled, sleeping {wait}s")
                time.sleep(wait)
                continue
            if r.status != 200:
                raise RuntimeError(f"HTTP {r.status}: {data[:200]!r}")
            return data
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(3 * (a + 1))
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:  # noqa: BLE001
                    pass
    raise RuntimeError(f"OpenGWAS request failed: {path} :: {last}")


def instruments(gwas_id: str, p: float = 5e-8, kb: int = 10_000) -> pd.DataFrame:
    cache = RAW / f"tophits_{gwas_id}_{p:g}.tsv"
    if cache.exists() and cache.stat().st_size > 1:
        return pd.read_csv(cache, sep="\t")
    d = json.loads(api("/api/tophits", "POST", json.dumps({
        "id": [gwas_id], "pval": p, "preclump": True, "clump": True,
        "r2": 0.001, "kb": kb}).encode()).decode("utf-8", "replace"))
    rows = d if isinstance(d, list) else d.get("data", [])
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df[df["id"] == gwas_id] if "id" in df.columns else df
    keep = [c for c in ("id", "trait", "chr", "position", "rsid", "ea", "nea",
                        "eaf", "beta", "se", "p", "n") if c in df.columns]
    df = df[keep].rename(columns={"position": "pos", "se": "sebeta"})
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, sep="\t", index=False)
    return df


def main() -> int:
    ap = sys.argv[1:]
    p_thresh = float(ap[0]) if ap else 5e-8
    print("=" * 78)
    print("STEP 6  two-sample MR: modifiable exposures -> optic-nerve phenotypes")
    print("=" * 78)

    # ---------------------------------------------------------- outcomes first
    print("\n[1] opening FinnGen R12 outcomes ...")
    tbs: dict[str, Tabix] = {}
    for ph in OUTCOME_ORDER:
        tb = open_tabix(ph)
        if tb is not None:
            tbs[ph] = tb
            print(f"    {ph:28s} ready")
    if not tbs:
        print("no outcomes available")
        return 1

    # ------------------------------------------------------------------ MR loop
    print(f"\n[2] running MR (instrument threshold p < {p_thresh:g}) ...")
    results: list[dict] = []
    inst_rows: list[dict] = []
    for name, meta in EXPOSURES.items():
        gid = meta["id"]
        try:
            inst = instruments(gid, p=p_thresh)
        except Exception as exc:  # noqa: BLE001
            print(f"  {name:22s} instruments FAILED: {str(exc)[:100]}")
            continue
        if inst.empty:
            print(f"  {name:22s} no genome-wide significant instruments")
            continue
        print(f"  {name:22s} {gid:20s} {len(inst):>4} instruments "
              f"(n={meta['n']:,})")
        for _, r in inst.iterrows():
            inst_rows.append({"exposure": name, "gwas_id": gid, **r.to_dict()})

        exp = inst.copy()
        # normalise to the column contract expected by harmonise():
        # chrom, pos, ref, alt, rsids, beta, sebeta, af_alt, pval
        exp["chrom"] = exp["chr"].astype(str).str.replace("chr", "", regex=False)
        exp["pos"] = pd.to_numeric(exp["pos"], errors="coerce")
        exp["alt"] = exp["ea"].astype(str).str.upper()
        exp["ref"] = exp["nea"].astype(str).str.upper()
        exp["rsids"] = exp["rsid"].astype(str)
        exp["beta"] = pd.to_numeric(exp["beta"], errors="coerce")
        exp["sebeta"] = pd.to_numeric(exp["sebeta"], errors="coerce")
        exp["af_alt"] = pd.to_numeric(exp.get("eaf"), errors="coerce")
        if "p" in exp.columns:
            exp["pval"] = pd.to_numeric(exp["p"], errors="coerce")
        elif "pval" not in exp.columns:
            exp["pval"] = np.nan
        exp = exp.dropna(subset=["pos", "beta", "sebeta"])
        if exp.empty:
            continue
        # The instrument span may cross chromosomes; scan per chromosome.  Within a
        # chromosome the instruments are grouped into windows so that neither memory nor
        # the tabix chunk read grows without bound.
        #
        # The harmonised variants are POOLED across every window and chromosome before any
        # estimate is computed.  An earlier version called run_mr inside the window loop
        # and then kept, per exposure-outcome pair, the single window with the most SNPs.
        # That discarded almost the whole instrument set: serum creatinine harmonised 186
        # instruments across the genome and every reported estimate used four of them, so
        # the confidence intervals described four SNPs while the manuscript quoted the 186
        # as the instrument count.  Pooling is the correct procedure for two-sample MR -
        # the instruments are independent and belong to one analysis, not to a series of
        # window-wise analyses.
        pooled: dict[str, list] = {ph: [] for ph in tbs}
        window_stats = {"windows": 0, "scans": 0, "no_variants": 0, "harmonised": 0}

        for chrom, grp in exp.groupby("chrom"):
            grp = grp.sort_values("pos")
            positions = grp["pos"].astype(int).tolist()
            windows: list[list[int]] = []
            for p in positions:
                lo_w, hi_w = max(1, p - 250_000), p + 250_000
                if windows and lo_w <= windows[-1][1] + 2_000_000:
                    windows[-1][1] = max(windows[-1][1], hi_w)
                else:
                    windows.append([lo_w, hi_w])
            print(f"      chr{chrom}: {len(grp)} instruments in {len(windows)} "
                  f"window(s)")
            for wi, (lo, hi) in enumerate(windows):
                sub = grp[(grp["pos"] >= lo) & (grp["pos"] <= hi)]
                if sub.empty:
                    continue
                window_stats["windows"] += 1
                for ph, tb in tbs.items():
                    try:
                        out = region_scan(tb, chrom, lo, hi,
                                          RAW / f"mr_{gid}_{ph}_{chrom}_{wi}.tsv")
                    except Exception as exc:  # noqa: BLE001
                        print(f"      outcome scan failed {ph}: {str(exc)[:80]}")
                        continue
                    window_stats["scans"] += 1
                    if out is None or out.empty:
                        window_stats["no_variants"] += 1
                        continue
                    h = harmonise(sub, out)
                    if h.empty:
                        continue
                    window_stats["harmonised"] += len(h)
                    pooled[ph].append(h)

        # one estimate per exposure-outcome pair, on the pooled instrument set
        for ph, frames in pooled.items():
            if not frames:
                print(f"      {ph}: no harmonised instruments")
                continue
            h = pd.concat(frames, ignore_index=True)
            # a variant can sit in two overlapping windows; keep one row per variant
            h = h.drop_duplicates(subset=["snp"]).reset_index(drop=True)
            if h.empty:
                continue
            res = run_mr(h)
            if not res:
                continue
            res.update({
                "exposure": name, "exposure_label": meta["label"],
                "gwas_id": gid, "exposure_n": meta["n"],
                "outcome": ph, "outcome_label": OUTCOMES.get(ph, ""),
                "snps": ";".join(h["snp"].astype(str)),
            })
            results.append(res)
            print(f"      {ph:28s} {res['n_snp']:>4} instruments pooled   "
                  f"beta {res['beta']:+.4f}  se {res['se']:.4f}")
        print(f"      -> {sum(1 for r in results if r['exposure'] == name)} "
              f"exposure-outcome estimates so far "
              f"({time.time() - T0:.0f}s)")
        print(f"         windows {window_stats['windows']}, scans "
              f"{window_stats['scans']}, scans with no variants "
              f"{window_stats['no_variants']}, harmonised rows "
              f"{window_stats['harmonised']}")

    if not results:
        print("no MR estimates produced")
        return 1

    df = pd.DataFrame(results)
    # One estimate per exposure-outcome pair is produced above, on the pooled instrument
    # set, so the collapse that used to happen here is gone.  It kept the window with the
    # most SNPs and discarded the rest, which is what reduced a 186-instrument analysis to
    # four SNPs; leaving it in place would silently undo the pooling.  The guard below
    # keeps the file well-formed if a duplicate ever appears.
    df = (df.sort_values("n_snp", ascending=False)
            .drop_duplicates(["exposure", "outcome"], keep="first")
            .reset_index(drop=True))
    if len(df) != len(results):
        print(f"  WARNING: {len(results) - len(df)} duplicate exposure-outcome rows "
              f"collapsed; pooling should have produced one each")
    if "p" in df.columns:
        ok = df["p"].notna() & (df["n_snp"] > 0)
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
    cols = ["exposure", "exposure_label", "gwas_id", "exposure_n", "outcome",
            "outcome_label", "n_snp", "method", "beta", "se", "p", "p_fdr",
            "or", "or_lcl", "or_ucl", "Q", "Q_df", "Q_p", "egger_intercept",
            "egger_intercept_p", "egger_beta", "egger_se", "wm_beta", "wm_se",
            "wm_p", "steiger_r2_exposure", "steiger_r2_outcome",
            "steiger_correct", "snps"]
    df = df.reindex(columns=[c for c in cols if c in df.columns])
    df = df.sort_values(["outcome", "p"])
    df.to_csv(RESULTS / "mr_opengwas_results.csv", index=False,
              encoding="utf-8-sig")
    pd.DataFrame(inst_rows).to_csv(RESULTS / "mr_opengwas_instruments.csv",
                                   index=False, encoding="utf-8-sig")

    print("\n=== MR estimates (top 40 by p) ===")
    show = df[df.p.notna()].head(40)
    print(show[["exposure", "outcome", "n_snp", "method", "beta", "se", "p",
                "or", "or_lcl", "or_ucl", "egger_intercept_p",
                "steiger_correct"]]
          .to_string(index=False, max_colwidth=22))
    print(f"\n-> {RESULTS / 'mr_opengwas_results.csv'} ({len(df)} estimates)")
    return 0


T0 = time.time()

if __name__ == "__main__":
    raise SystemExit(main())
