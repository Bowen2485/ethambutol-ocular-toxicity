# -*- coding: utf-8 -*-
"""
Step 2 - Disproportionality analysis (the pharmacovigilance core).

openFDA refuses `count` aggregations with limit>100 for keyless callers (it
returns 403 API_KEY_MISSING), so every cell of the 2x2 table is obtained from
the exact integer `meta.results.total`, which is both cheaper and more precise.

Contingency table for drug D and adverse event E, over the whole FAERS database:

                 E+            E-
        D+       a             b            n_D   = a + b   (reports naming D)
        D-       c             d            n_notD
                n_E           n_notE       N     = grand total

    a = reports naming D and reporting E
    n_D = reports naming D
    n_E = reports reporting E  (all drugs)
    N  = all reports in the database
    b = n_D - a ;  c = n_E - a ;  d = N - a - b - c

Signal metrics
    ROR      = (a*d)/(b*c),       95% CI by the log-normal (Woolf) method
    PRR      = [a/n_D]/[c/(N-n_D)], chi-square on the 2x2 table
    IC025    = lower 95% credible bound of the Bayesian Information Component
    EBGM05   = lower 95% bound of the Empirical Bayes Geometric Mean (gamma-Poisson)
    chi2     = Mantel-Haenszel / Pearson chi-square with Yates correction

Outputs
    data/derived/faers_2x2_<drug>.csv   raw counts and metrics per drug x term
    data/derived/faers_signals_<drug>.csv  filtered signal table
    results/faers_disproportionality.md    readable report
"""
from __future__ import annotations

import argparse
import json
import math
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
DERIVED.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

API = "https://api.fda.gov/drug/event.json"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FAERS-research/1.0"}
SLEEP = 0.42

DRUG_TERMS = {
    "ethambutol": "ETHAMBUTOL",
    "isoniazid": "ISONIAZID",
    "rifampicin": "RIFAMPICIN",
    "pyrazinamide": "PYRAZINAMIDE",
    "streptomycin": "STREPTOMYCIN",
    "linezolid": "LINEZOLID",
}

# WHO-UMC / EU EMA signal criteria
ROR_CRIT = ("ROR lower 95% CI > 1", "a >= 3")
PRR_CRIT = ("PRR >= 2", "chi2 >= 4", "a >= 3")
IC_CRIT = "IC025 > 0"


# --------------------------------------------------------------------- API layer
def _request(url: str, tries: int = 8) -> dict:
    """GET with back-off; openFDA returns 403 (fake API_KEY_MISSING) when throttled."""
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120, context=CTX) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            body = b""
            try:
                body = exc.read()
            except Exception:  # noqa: BLE001
                pass
            if exc.code == 404:                      # genuine zero matches
                return {"results": [], "meta": {"results": {"total": 0}}}
            throttled = exc.code in (403, 429) or b"API_KEY_MISSING" in body
            last = exc
            time.sleep((1.8 ** attempt) if throttled else (0.9 * (attempt + 1)))
        except Exception as exc:                     # noqa: BLE001
            last = exc
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"openFDA request failed after {tries} tries: {url} :: {last}")


_COUNT_CACHE: dict[str, int] = {}
_CACHE_FILE = DERIVED / "openfda_count_cache.json"


def _load_cache() -> None:
    if _CACHE_FILE.exists():
        try:
            _COUNT_CACHE.update(json.loads(_CACHE_FILE.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            pass


def _save_cache() -> None:
    _CACHE_FILE.write_text(json.dumps(_COUNT_CACHE, ensure_ascii=False, indent=0),
                           encoding="utf-8")


def exact_count(search: str, use_cache: bool = True) -> int:
    """Exact number of FAERS reports matching `search` (integer, not capped)."""
    if use_cache and search in _COUNT_CACHE:
        return _COUNT_CACHE[search]
    url = f"{API}?search={urllib.parse.quote(search)}&limit=1"
    n = int(_request(url)["meta"]["results"]["total"])
    _COUNT_CACHE[search] = n
    time.sleep(SLEEP)
    return n


# ------------------------------------------------------------------- statistics
def ror_ci(a: int, b: int, c: int, d: int, z: float = 1.959964) -> tuple[float, float, float]:
    """Reporting odds ratio and its log-normal 95% CI (Haldane-Anscombe if needed)."""
    A, B, C, D = a, b, c, d
    if 0 in (A, B, C, D):
        A, B, C, D = A + 0.5, B + 0.5, C + 0.5, D + 0.5
        if a == 0:
            return 0.0, 0.0, float("inf")
    ror = (A * D) / (B * C)
    se = math.sqrt(1 / A + 1 / B + 1 / C + 1 / D)
    return ror, ror * math.exp(-z * se), ror * math.exp(z * se)


def prr_chi2(a: int, b: int, c: int, d: int) -> tuple[float, float, float, float]:
    """Proportional reporting ratio, its 95% CI and the chi-square statistics."""
    n_d, n_notd = a + b, c + d
    n_e, n_note = a + c, b + d
    n = n_d + n_notd
    if min(n_d, n_notd, n_e, n_note) == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    p1, p2 = a / n_d, c / n_notd
    prr = p1 / p2 if p2 else float("inf")
    se = math.sqrt((1 / a if a else float("nan")) - 1 / n_d
                   + (1 / c if c else float("nan")) - 1 / n_notd)
    lo = math.exp(math.log(prr) - 1.959964 * se) if prr > 0 else 0.0
    hi = math.exp(math.log(prr) + 1.959964 * se) if prr > 0 else float("inf")
    # Pearson chi-square (no continuity correction) and with Yates correction
    exp = np.array([[n_d * n_e / n, n_d * n_note / n],
                    [n_notd * n_e / n, n_notd * n_note / n]])
    obs = np.array([[a, b], [c, d]], dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        chi2 = float(np.nansum((obs - exp) ** 2 / exp))
    yates = float(np.nansum((np.abs(obs - exp) - 0.5) ** 2 / exp))
    return prr, lo, hi, yates


def ic025(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """
    Bayesian Information Component (Norén 2006) with a non-informative prior
    (alpha=beta=1 => alpha_i=1+0, beta_i=1+1) and its 95% lower credible bound.
    """
    n = a + b + c + d
    n_e, n_d = a + c, a + b
    if n == 0 or n_e == 0 or n_d == 0:
        return float("nan"), float("nan")
    exp_n = n_e * n_d / n
    ic = math.log2((a + 0.5) / (exp_n + 0.5))
    # variance from a gamma approximation of the posterior of the rate ratio
    aa, bb = 1.0 + a, 1.0 + exp_n
    v = (1 / math.log(2) ** 2) * (_digamma_derivative(aa) - _digamma_derivative(aa + bb))
    if v <= 0 or not math.isfinite(v):
        return ic, float("nan")
    return ic, ic - 1.959964 * math.sqrt(v)


def _digamma(x: float) -> float:
    """Digamma via the asymptotic series after upward recurrence."""
    r = 0.0
    while x < 6.0:
        r -= 1.0 / x
        x += 1.0
    f = 1.0 / (x * x)
    return (r + math.log(x) - 0.5 / x
            - f * (1 / 12 - f * (1 / 120 - f * (1 / 252 - f * (1 / 240 - f / 132)))))


def _digamma_derivative(x: float) -> float:
    """Trigamma function (derivative of digamma)."""
    r = 0.0
    while x < 6.0:
        r += 1.0 / (x * x)
        x += 1.0
    f = 1.0 / (x * x)
    return (r + 1 / x + f / 2 + f * f / 6 - f ** 3 / 30 + f ** 5 / 42)


def ebgm05(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """
    Empirical Bayes Geometric Mean (MGPS-style gamma-Poisson shrinkage) and the
    5th percentile of its posterior.  Prior: alpha=0.5, beta=0.5 (a weak,
    conservative shrinkage prior); exposure = expected count under independence.
    """
    n = a + b + c + d
    n_e, n_d = a + c, a + b
    if n == 0 or n_e == 0 or n_d == 0:
        return float("nan"), float("nan")
    exp_n = max(n_e * n_d / n, 1e-9)
    alpha, beta = 0.5, 0.5
    post_a, post_b = alpha + a, beta + exp_n
    ebgm = math.exp(_digamma(post_a) - math.log(post_b))
    lo = _gamma_ppf(0.05, post_a, scale=1 / post_b)
    return ebgm, lo


def _gamma_ppf(p: float, shape: float, scale: float = 1.0) -> float:
    """Gamma quantile by bisection on the regularised lower incomplete gamma."""
    if shape <= 0:
        return float("nan")
    lo, hi = 0.0, max(scale * (shape + 10 * math.sqrt(shape) + 10), 1e-9)
    while _gammainc(shape, hi / scale) < p and hi < 1e12:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if _gammainc(shape, mid / scale) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _gammainc(s: float, x: float) -> float:
    """Regularised lower incomplete gamma P(s, x) (series + continued fraction)."""
    if x <= 0:
        return 0.0
    if x < s + 1:
        term = 1.0 / s
        total = term
        n = s
        for _ in range(1000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return total * math.exp(-x + s * math.log(x) - math.lgamma(s))
    # Lentz continued fraction for Q(s, x)
    tiny = 1e-300
    b = x + 1 - s
    cc, dd = 1 / tiny, 1 / b
    h = dd
    for i in range(1, 1000):
        an = -i * (i - s)
        b += 2
        dd = an * dd + b
        if abs(dd) < tiny:
            dd = tiny
        cc = b + an / cc
        if abs(cc) < tiny:
            cc = tiny
        dd = 1 / dd
        delta = cc * dd
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    q = math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    return 1 - q


# ------------------------------------------------------------------ analysis run
def build_table(drug_key: str, terms: list[str], grand_total: int,
                drug_search: str) -> pd.DataFrame:
    n_d = exact_count(drug_search)
    print(f"[{drug_key}] reports naming the drug: {n_d}")
    rows = []
    for i, term in enumerate(terms, 1):
        ev_search = f'patient.reaction.reactionmeddrapt:"{term}"'
        a = exact_count(f"{drug_search} AND {ev_search}")
        n_e = exact_count(ev_search)
        b, c = n_d - a, n_e - a
        dd = grand_total - a - b - c
        ror, ror_lo, ror_hi = ror_ci(a, b, c, dd)
        prr, prr_lo, prr_hi, chi2 = prr_chi2(a, b, c, dd)
        ic, ic_lo = ic025(a, b, c, dd)
        ebgm, ebgm_lo = ebgm05(a, b, c, dd)
        rows.append({
            "drug": drug_key, "term": term,
            "a": a, "b": b, "c": c, "d": dd,
            "n_drug": n_d, "n_event": n_e, "n_total": grand_total,
            "ror": ror, "ror_lcl": ror_lo, "ror_ucl": ror_hi,
            "prr": prr, "prr_lcl": prr_lo, "prr_ucl": prr_hi,
            "chi2_yates": chi2, "ic": ic, "ic025": ic_lo,
            "ebgm": ebgm, "ebgm05": ebgm_lo,
        })
        if i % 20 == 0:
            print(f"    {i}/{len(terms)} terms")
    df = pd.DataFrame(rows)
    # Benjamini-Hochberg FDR over the analysed panel
    from scipy import stats as st
    p = st.chi2.sf(df["chi2_yates"].fillna(0).clip(lower=0), df=1)
    order = np.argsort(p.values)
    ranked = p.values[order]
    m = len(ranked)
    q = np.empty(m)
    prev = 1.0
    for k in range(m - 1, -1, -1):
        prev = min(prev, ranked[k] * m / (k + 1))
        q[k] = prev
    out = np.empty(m)
    out[order] = q
    df["p_chi2"] = p.values
    df["q_bh"] = out
    df["signal_ror"] = (df.ror_lcl > 1) & (df.a >= 3)
    df["signal_prr"] = (df.prr >= 2) & (df.chi2_yates >= 4) & (df.a >= 3)
    df["signal_ic"] = df.ic025 > 0
    df["signal_ebgm"] = df.ebgm05 > 2
    df["signal_any"] = df.signal_ror | df.signal_prr | df.signal_ic
    df["signal_strict"] = df.signal_ror & df.signal_prr & df.signal_ic & (df.q_bh < 0.05)
    return df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugs", nargs="+", default=["ethambutol"])
    ap.add_argument("--terms", default=str(DERIVED / "ocular_terms.json"))
    ap.add_argument("--limit-terms", type=int, default=0,
                    help="0 = use every ocular term that occurs in the index drug")
    args = ap.parse_args()

    _load_cache()
    terms_payload = json.loads(Path(args.terms).read_text(encoding="utf-8"))
    term_df = pd.DataFrame(terms_payload)
    terms = list(dict.fromkeys(term_df["term"].tolist()))
    if args.limit_terms:
        terms = terms[:args.limit_terms]
    print(f"[setup] {len(terms)} ocular MedDRA preferred terms")

    grand_total = exact_count("receivedate:[19000101 TO 29991231]")
    print(f"[setup] FAERS grand total reports: {grand_total:,}")

    frames = []
    for drug in args.drugs:
        term_name = DRUG_TERMS[drug]
        search = f'patient.drug.medicinalproduct:"{term_name}"'
        frames.append(build_table(drug, terms, grand_total, search))
        _save_cache()

    all2x2 = pd.concat(frames, ignore_index=True)
    all2x2 = all2x2.merge(term_df[["term", "group", "source"]].drop_duplicates("term"),
                          on="term", how="left")
    all2x2.to_csv(DERIVED / f"faers_2x2_{'_'.join(args.drugs)}.csv",
                  index=False, encoding="utf-8-sig")

    mask = (all2x2.a >= 1) & (all2x2.signal_any | all2x2.signal_strict)
    signals = all2x2[mask].sort_values(["drug", "signal_strict", "ror"],
                                       ascending=[True, False, False])
    signals.to_csv(DERIVED / f"faers_signals_{'_'.join(args.drugs)}.csv",
                   index=False, encoding="utf-8-sig")
    _save_cache()
    print(f"\n[done] {len(all2x2)} drug x term rows; {len(signals)} with a signal")
    print(f"  -> {DERIVED / f'faers_2x2_{chr(95).join(args.drugs)}.csv'}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
