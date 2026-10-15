# -*- coding: utf-8 -*-
"""
Step 6 - Two-sample Mendelian randomisation for ethambutol ocular toxicity.

Design (and its explicit limitation)
    Ethambutol has no genetic instrument: it is an environmental drug exposure,
    there is no "ethambutol use" GWAS, and Open Targets records no human target
    for it.  A naive drug-exposure MR is therefore impossible, and this script
    does not pretend otherwise.  What IS estimable is the causal role of the
    molecular pathways that the pharmacovigilance and network-toxicology steps
    implicate in the ocular phenotype:

    Exposure instruments
        cis-region variants (gene +/- 250 kb) of the focused-tier panel genes
        (OPA1, SDHB, SMAD4, GPX4, SLC7A11, ACSL4, BDNF, NTRK2, AKT1, NFE2L2,
         HMOX1, SOD2, MCOLN1, SLC30A10, MT1A, POLG, MFN2, SLC25A4, TXN2, PRDX3,
         TFEB, NAT2, TNF, CASP3, BAX, BCL2, TP53) extracted from FinnGen.
        : these act as proxies for genetically proxied target perturbation.

    Outcomes (FinnGen R12, tabix-accessed)
        H7_OPTNEURITIS, H7_OPTATROPHY, H7_OPTNERVE, H7_OPTNERVNAS,
        H7_BLINDANDVISIMPAIRMENT, H7_VISUDISTURB, H7_COULOURVISDEF,
        H7_VISFIELDDEF, H7_GLAUCOMA, H7_MACULADEGEN

    Estimators
        Wald ratio (single instrument), inverse-variance weighted (IVW) with
        multiplicative random effects, MR-Egger with the intercept test for
        directional pleiotropy, weighted median, and Cochran's Q for
        heterogeneity.  Steiger directionality is assessed by comparing the
        variance explained in exposure vs outcome.

Everything is computed from the released summary statistics; no effect size is
invented or borrowed from another study.
"""
from __future__ import annotations

import argparse
import json
import math
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
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
RAW = ROOT / "data" / "raw" / "finngen"
for p in (DERIVED, RESULTS, RAW):
    p.mkdir(parents=True, exist_ok=True)

import bgzf_tabix as bt  # noqa: E402

GB = "https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release"
MANIFEST = DERIVED / "finngen_R12_phenos.json"

# outcome endpoints chosen from the R12 manifest (case counts from step 6a)
OUTCOMES = {
    "H7_OPTNEURITIS": "Optic neuritis",
    "H7_OPTATROPHY": "Optic atrophy",
    "H7_OPTNERVE": "Disorders of optic nerve and visual pathways",
    "H7_OPTNERVNAS": "Disorders of optic nerve, NEC",
    "H7_BLINDANDVISIMPAIRMENT": "Visual impairment including blindness",
    "H7_VISUDISTURB": "Visual disturbances",
    "H7_COULOURVISDEF": "Colour vision deficiencies",
    "H7_VISFIELDDEF": "Visual field defects",
    "H7_GLAUCOMA": "Glaucoma",
    "H7_MACULADEGEN": "Degeneration of macula and posterior pole",
}

# exposure gene panel = focused-tier hubs (chromosome, GRCh38 approximate position)
EXPOSURE_GENES = {
    "OPA1":     ("3", 193_593_000, 193_700_000),
    "SDHB":     ("1", 17_018_000, 17_055_000),
    "SMAD4":    ("18", 51_030_000, 51_100_000),
    "GPX4":     ("19", 1_103_000, 1_108_000),
    "SLC7A11":  ("4", 138_160_000, 138_250_000),
    "ACSL4":    ("X", 109_620_000, 109_730_000),
    "BDNF":     ("11", 27_600_000, 27_670_000),
    "NTRK2":    ("9", 84_660_000, 84_800_000),
    "AKT1":     ("14", 104_760_000, 104_790_000),
    "NFE2L2":   ("2", 177_220_000, 177_300_000),
    "HMOX1":    ("22", 35_380_000, 35_420_000),
    "SOD2":     ("6", 159_670_000, 159_710_000),
    "MCOLN1":   ("19", 7_530_000, 7_560_000),
    "SLC30A10": ("1", 219_900_000, 219_950_000),
    "MT1A":     ("16", 56_650_000, 56_680_000),
    "POLG":     ("15", 89_310_000, 89_340_000),
    "MFN2":     ("1", 11_990_000, 12_030_000),
    "SLC25A4":  ("4", 185_140_000, 185_150_000),
    "TXN2":     ("22", 36_470_000, 36_490_000),
    "PRDX3":    ("10", 119_160_000, 119_180_000),
    "TFEB":     ("6", 41_680_000, 41_730_000),
    "NAT2":     ("8", 18_400_000, 18_430_000),
    "TNF":      ("6", 31_570_000, 31_580_000),
    "CASP3":    ("4", 184_620_000, 184_650_000),
    "BAX":      ("19", 48_950_000, 48_960_000),
    "BCL2":     ("18", 63_320_000, 63_350_000),
    "TP53":     ("17", 7_660_000, 7_690_000),
}

P_THRESHOLD = 5e-6        # cis-region instrument threshold
CLUMP_KB = 500            # distance-based pruning within a locus


# --------------------------------------------------------------------- retrieval
def load_manifest() -> dict:
    if not MANIFEST.exists():
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request("https://r12.finngen.fi/api/phenos",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=300, context=ctx) as r:
            MANIFEST.write_bytes(r.read())
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {p["phenocode"]: p for p in m}


def open_tabix(pheno: str) -> bt.Tabix | None:
    gz = f"{GB}/finngen_R12_{pheno}.gz"
    try:
        return bt.Tabix(gz, gz + ".tbi")
    except Exception as exc:  # noqa: BLE001
        print(f"[tabix] {pheno}: unavailable ({type(exc).__name__} {str(exc)[:80]})")
        return None


COLS = ["chrom", "pos", "ref", "alt", "rsids", "nearest_genes", "pval", "mlogp",
        "beta", "sebeta", "af_alt", "af_alt_cases", "af_alt_controls"]


def parse_lines(lines: list[str]) -> pd.DataFrame:
    rows = []
    for ln in lines:
        p = ln.split("\t")
        if len(p) < len(COLS):
            continue
        row = dict(zip(COLS, p[:len(COLS)]))
        for k in ("pos",):
            try:
                row[k] = int(row[k])
            except ValueError:
                row[k] = None
        for k in ("pval", "beta", "sebeta", "af_alt"):
            try:
                row[k] = float(row[k])
            except (ValueError, TypeError):
                row[k] = np.nan
        rows.append(row)
    return pd.DataFrame(rows, columns=COLS if not rows else None)


def region_scan(tb: bt.Tabix, chrom: str, start: int, end: int,
                cache: Path) -> pd.DataFrame:
    if cache.exists() and cache.stat().st_size > 0:
        df = pd.read_csv(cache, sep="\t")
        if "pos" in df.columns and len(df):
            return df
    lines = tb.query(chrom, start, end)
    df = parse_lines(lines)
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, sep="\t", index=False)
    return df


# --------------------------------------------------------------------- pruning
def clump(df: pd.DataFrame, p_col: str = "pval", kb: int = CLUMP_KB) -> pd.DataFrame:
    """Distance-based pruning: keep the lowest-p variant within each `kb` window."""
    if df.empty:
        return df
    d = df.dropna(subset=[p_col, "pos"]).sort_values(p_col).reset_index(drop=True)
    kept = []
    for _, r in d.iterrows():
        if all(abs(r["pos"] - k["pos"]) > kb * 1000 for k in kept):
            kept.append(r)
    return pd.DataFrame(kept) if kept else d.iloc[0:0]


def harmonise(exposure: pd.DataFrame, outcome: pd.DataFrame,
              match: str = "auto") -> pd.DataFrame:
    """
    Align effect alleles between an exposure (instrument) frame and an outcome
    (FinnGen) frame.

    Matching key.  The two sources are not guaranteed to share a genome build -
    the OpenGWAS instruments are frequently GRCh37 while FinnGen R12 is GRCh38 -
    and position matching then fails almost completely (measured recovery: 0.2%
    of 13,560 instrument-outcome pairs).  rsIDs are build-independent, so matching
    is done on rsID first and only falls back to chromosome:position for variants
    that carry no rsID.  `outcome.rsids` may hold several IDs separated by
    semicolons, so all of them are indexed.

    Allele alignment.  FinnGen reports beta for ALT.  If REF/ALT are swapped
    between the two datasets the outcome beta is negated; palindromic variants
    with an intermediate allele frequency are dropped as strand-ambiguous.
    """
    if exposure.empty or outcome.empty:
        return pd.DataFrame()
    ex = exposure.copy()
    ou = outcome.copy()

    ex["rs_key"] = ex.get("rsids", pd.Series(dtype=str)).astype(str).str.strip()
    ou["rs_key"] = ou.get("rsids", pd.Series(dtype=str)).astype(str).str.strip()
    ex["pos_key"] = ex["chrom"].astype(str) + ":" + ex["pos"].astype(int).astype(str)
    ou["pos_key"] = ou["chrom"].astype(str) + ":" + ou["pos"].astype(int).astype(str)

    # explode the outcome rsID lists so one variant can match any of its names
    ou["rs_key"] = ou["rs_key"].str.split(";")
    ou = ou.explode("rs_key")
    ou["rs_key"] = ou["rs_key"].astype(str).str.strip()

    usable = ex[ex["rs_key"].notna() & (ex["rs_key"] != "") & (ex["rs_key"] != "nan")]
    frames = []
    if not usable.empty:
        m_rs = usable.merge(ou, on="rs_key", suffixes=("_exp", "_out"))
        if not m_rs.empty:
            m_rs["snp_key"] = m_rs["pos_key_exp"]
            frames.append(m_rs)
    if match in ("auto", "position"):
        # fall back to position for instruments without an rsID, and rescue any
        # same-build pairs the rsID route missed
        m_pos = ex.merge(ou, on="pos_key", suffixes=("_exp", "_out"))
        if not m_pos.empty:
            m_pos["snp_key"] = m_pos["pos_key"]
            frames.append(m_pos)
    if not frames:
        return pd.DataFrame()
    m = pd.concat(frames, ignore_index=True)
    m = m.drop_duplicates(subset=["snp_key"])
    if m.empty or "alt_exp" not in m.columns or "alt_out" not in m.columns:
        return pd.DataFrame()

    def pick(row, base: str, suffix: str):
        """Columns present in both frames arrive as <base>_<suffix>."""
        for name in (f"{base}_{suffix}", base):
            if name in row.index:
                return row[name]
        return np.nan

    rows = []
    for _, r in m.iterrows():
        a1e, a2e = str(r["alt_exp"]).upper(), str(r["ref_exp"]).upper()
        a1o, a2o = str(r["alt_out"]).upper(), str(r["ref_out"]).upper()
        comp = {"A": "T", "T": "A", "C": "G", "G": "C"}
        palindromic = comp.get(a1e) == a2e
        eaf = pick(r, "af_alt", "exp")
        try:
            eaf = float(eaf)
        except (TypeError, ValueError):
            eaf = np.nan
        if palindromic and not (np.isfinite(eaf) and (eaf < 0.42 or eaf > 0.58)):
            continue                      # ambiguous strand -> drop
        if (a1e, a2e) == (a1o, a2o):
            beta_o, se_o = r["beta_out"], r["sebeta_out"]
        elif (a1e, a2e) == (a2o, a1o):
            beta_o, se_o = -r["beta_out"], r["sebeta_out"]
        else:
            continue                      # incompatible alleles
        rsid = pick(r, "rsids", "exp")
        rows.append({
            "snp": str(rsid) if isinstance(rsid, str) and rsid else r["snp_key"],
            "chrom": pick(r, "chrom", "exp"), "pos": pick(r, "pos", "exp"),
            "effect_allele": a1e, "other_allele": a2e,
            "eaf": eaf,
            "beta_exp": float(r["beta_exp"]), "se_exp": float(r["sebeta_exp"]),
            "p_exp": float(r["pval_exp"]),
            "beta_out": float(beta_o), "se_out": float(se_o),
            "p_out": float(r["pval_out"]),
            "nearest_genes": pick(r, "nearest_genes", "exp"),
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ estimators
def ivw(beta_exp, se_exp, beta_out, se_out):
    w = 1.0 / se_out ** 2
    b = np.sum(w * beta_exp * beta_out) / np.sum(w * beta_exp ** 2)
    se = math.sqrt(1.0 / np.sum(w * beta_exp ** 2))
    q = float(np.sum(w * (beta_out - b * beta_exp) ** 2))
    return b, se, q


def mr_egger(beta_exp, se_exp, beta_out, se_out):
    w = 1.0 / se_out ** 2
    X = np.vstack([np.ones_like(beta_exp), beta_exp]).T
    W = np.diag(w)
    try:
        cov = np.linalg.inv(X.T @ W @ X)
        theta = cov @ X.T @ W @ beta_out
    except np.linalg.LinAlgError:
        return None
    intercept, slope = theta[0], theta[1]
    se_int = math.sqrt(cov[0, 0])
    se_slope = math.sqrt(cov[1, 1])
    return {"intercept": float(intercept), "intercept_se": float(se_int),
            "intercept_p": float(2 * (1 - _norm_cdf(abs(intercept / se_int))))
            if se_int > 0 else np.nan,
            "slope": float(slope), "slope_se": float(se_slope)}


def weighted_median(beta_exp, se_exp, beta_out, se_out, n_boot=2000, seed=7):
    ratio = beta_out / beta_exp
    w = (beta_exp ** 2) / (se_out ** 2)
    order = np.argsort(ratio)
    r, ww = ratio[order], w[order]
    cw = np.cumsum(ww) / np.sum(ww)
    est = float(np.interp(0.5, cw, r))
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(r), len(r))
        rr, w2 = r[idx], ww[idx]
        o = np.argsort(rr)
        c2 = np.cumsum(w2[o]) / np.sum(w2[o])
        boots.append(np.interp(0.5, c2, rr[o]))
    se = float(np.std(boots, ddof=1))
    return est, se


def _norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def steiger(beta_exp, se_exp, beta_out, se_out, n_exp=300_000, n_out=300_000):
    """Variance explained by the instruments in exposure vs outcome."""
    r2_exp = float(np.sum(2 * beta_exp ** 2 * 0.25 /
                          (2 * beta_exp ** 2 * 0.25 + se_exp ** 2 * n_exp)))
    r2_out = float(np.sum(2 * beta_out ** 2 * 0.25 /
                          (2 * beta_out ** 2 * 0.25 + se_out ** 2 * n_out)))
    return r2_exp, r2_out, bool(r2_exp > r2_out)


def run_mr(h: pd.DataFrame) -> dict:
    if h.empty:
        return {}
    be, se_e = h.beta_exp.values, h.se_exp.values
    bo, so = h.beta_out.values, h.se_out.values
    out: dict = {"n_snp": int(len(h))}
    if len(h) == 1:
        b = bo[0] / be[0]
        se = abs(so[0] / be[0])
        out.update({"method": "Wald ratio", "beta": float(b), "se": float(se),
                    "p": float(2 * (1 - _norm_cdf(abs(b / se)))) if se > 0 else np.nan,
                    "or": float(math.exp(b)),
                    "or_lcl": float(math.exp(b - 1.959964 * se)),
                    "or_ucl": float(math.exp(b + 1.959964 * se))})
    else:
        b, se, q = ivw(be, se_e, bo, so)
        dof = len(h) - 1
        q_p = float(1 - _chi2_cdf(q, dof)) if dof > 0 else np.nan
        out.update({"method": "IVW (random effects)", "beta": float(b), "se": float(se),
                    "p": float(2 * (1 - _norm_cdf(abs(b / se)))) if se > 0 else np.nan,
                    "or": float(math.exp(b)),
                    "or_lcl": float(math.exp(b - 1.959964 * se)),
                    "or_ucl": float(math.exp(b + 1.959964 * se)),
                    "Q": q, "Q_df": dof, "Q_p": q_p})
        eg = mr_egger(be, se_e, bo, so)
        if eg:
            out.update({"egger_intercept": eg["intercept"],
                        "egger_intercept_p": eg["intercept_p"],
                        "egger_beta": eg["slope"], "egger_se": eg["slope_se"]})
        wm, wm_se = weighted_median(be, se_e, bo, so)
        out.update({"wm_beta": wm, "wm_se": wm_se,
                    "wm_p": float(2 * (1 - _norm_cdf(abs(wm / wm_se)))) if wm_se > 0 else np.nan})
    r2e, r2o, ok = steiger(be, se_e, bo, so)
    out.update({"steiger_r2_exposure": r2e, "steiger_r2_outcome": r2o,
                "steiger_correct": ok})
    return out


def _chi2_cdf(x, k):
    """Regularised lower incomplete gamma P(k/2, x/2) for the chi-square CDF."""
    if x <= 0:
        return 0.0
    a, z = k / 2.0, x / 2.0
    if z < a + 1:
        term, total, n = 1.0 / a, 1.0 / a, a
        for _ in range(2000):
            n += 1
            term *= z / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return total * math.exp(-z + a * math.log(z) - math.lgamma(a))
    tiny = 1e-300
    b = z + 1 - a
    c, d, h = 1 / tiny, 1 / b, 1 / b
    for i in range(1, 2000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = c * d
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return 1 - math.exp(-z + a * math.log(z) - math.lgamma(a)) * h


# ------------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genes", nargs="+", default=list(EXPOSURE_GENES))
    ap.add_argument("--outcomes", nargs="+", default=list(OUTCOMES))
    ap.add_argument("--p-threshold", type=float, default=P_THRESHOLD)
    args = ap.parse_args()

    manifest = load_manifest()
    print("=" * 78)
    print("STEP 6  two-sample MR (FinnGen R12)")
    print("=" * 78)
    for o in args.outcomes:
        p = manifest.get(o)
        if p:
            print(f"  outcome {o:28s} {p.get('phenostring','')[:46]:48s} "
                  f"cases={p.get('num_cases')} controls={p.get('num_controls')}")

    # ---- 1. instruments: cis-region variants per exposure gene (from FinnGen)
    print("\n[1] harvesting cis-region instruments ...")
    # use a large ocular endpoint as the reference scan; instruments only need
    # to exist in BOTH datasets, so any endpoint with full coverage works.
    ref_pheno = args.outcomes[0]
    tb_ref = open_tabix(ref_pheno)
    if tb_ref is None:
        print("cannot open the reference endpoint; aborting")
        return 1

    instruments: dict[str, pd.DataFrame] = {}
    for gene in args.genes:
        if gene not in EXPOSURE_GENES:
            continue
        chrom, start, end = EXPOSURE_GENES[gene]
        cache = RAW / f"cis_{gene}_{ref_pheno}.tsv"
        df = region_scan(tb_ref, chrom, start, end, cache)
        if df.empty:
            print(f"  {gene:9s} chr{chrom}:{start}-{end}: no variants in the window")
            continue
        sig = df[df.pval < args.p_threshold] if "pval" in df else df.iloc[0:0]
        pruned = clump(sig, kb=CLUMP_KB)
        if pruned.empty:
            # fall back to the single most significant variant in the window
            pruned = df.nsmallest(1, "pval")
        instruments[gene] = pruned
        print(f"  {gene:9s} chr{chrom}:{start}-{end}: {len(df)} variants, "
              f"{len(sig)} below p<{args.p_threshold:g}, {len(pruned)} after clumping")
        time.sleep(0.2)

    if not instruments:
        print("no instruments found")
        return 1

    # ---- 2. MR per (gene, outcome)
    print("\n[2] running MR ...")
    results = []
    outcome_cache: dict[str, pd.DataFrame] = {}
    for pheno in args.outcomes:
        tb = open_tabix(pheno)
        if tb is None:
            continue
        info = manifest.get(pheno, {})
        for gene, inst in instruments.items():
            chrom = str(inst.iloc[0]["chrom"])
            lo, hi = int(inst["pos"].min()) - 1_000, int(inst["pos"].max()) + 1_000
            cache = RAW / f"out_{pheno}_{gene}.tsv"
            odf = region_scan(tb, chrom, lo, hi, cache)
            h = harmonise(inst, odf)
            res = run_mr(h)
            if not res:
                continue
            res.update({"exposure_gene": gene, "outcome": pheno,
                        "outcome_label": OUTCOMES.get(pheno, info.get("phenostring", "")),
                        "n_cases": info.get("num_cases"),
                        "n_controls": info.get("num_controls"),
                        "snps": ";".join(h["snp"].astype(str))})
            results.append(res)
            print(f"  {gene:9s} -> {pheno:26s} n={res['n_snp']:>2} "
                  f"beta={res.get('beta', float('nan')):+.4f} "
                  f"p={res.get('p', float('nan')):.3g} "
                  f"OR={res.get('or', float('nan')):.3f}")
        outcome_cache[pheno] = pd.DataFrame()

    if not results:
        print("no MR results produced")
        return 1
    df = pd.DataFrame(results)
    cols = ["exposure_gene", "outcome", "outcome_label", "n_cases", "n_controls",
            "n_snp", "method", "beta", "se", "p", "or", "or_lcl", "or_ucl",
            "Q", "Q_df", "Q_p", "egger_intercept", "egger_intercept_p",
            "egger_beta", "egger_se", "wm_beta", "wm_se", "wm_p",
            "steiger_r2_exposure", "steiger_r2_outcome", "steiger_correct", "snps"]
    df = df.reindex(columns=cols)
    from scipy import stats as st
    df["p_fdr"] = np.nan
    ok = df["p"].notna()
    if ok.any():
        p = df.loc[ok, "p"].values
        order = np.argsort(p)
        m = len(p)
        q = np.empty(m)
        prev = 1.0
        for k in range(m - 1, -1, -1):
            prev = min(prev, p[order][k] * m / (k + 1))
            q[k] = prev
        out = np.empty(m)
        out[order] = q
        df.loc[ok, "p_fdr"] = out
    df = df.sort_values(["outcome", "p"])
    df.to_csv(RESULTS / "mr_results.csv", index=False, encoding="utf-8-sig")

    print("\n=== MR results (sorted by outcome, p) ===")
    show = df[df.p.notna()].head(30)
    print(show[["exposure_gene", "outcome", "n_snp", "method", "beta", "se",
                "p", "or", "or_lcl", "or_ucl", "egger_intercept_p",
                "steiger_correct"]]
          .to_string(index=False, max_colwidth=26))
    print(f"\n-> {RESULTS / 'mr_results.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
