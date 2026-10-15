# -*- coding: utf-8 -*-
"""
Step 2 - Pharmacovigilance signal analysis on the de-duplicated FAERS warehouse.

Source : data/derived/faers.sqlite (FDA quarterly ASCII releases 2004Q1-2026Q2,
         89 of 90 quarters; 2026Q2 excluded because the archive is corrupt).
Cases  : de-duplicated by the FDA protocol - for each CASEID keep the submission
         with the highest FDA_DT, breaking ties on the highest PRIMARYID.

Drug names live in the `drugname` table (FAERS calls the columns `drugname` and
`prod_ai`; openFDA's harmonised view renames them `medicinalproduct` and
`substance`), so exposure is resolved by joining drugname rather than scanning
the 99-million-row drug table.

For drug D and adverse event E:

                 E+      E-
        D+        a       b        n_D = a + b
        D-        c       d        n_E = a + c
                          N = a + b + c + d

Signal metrics: ROR (Woolf 95% CI), PRR + Yates chi-square, Bayesian Information
Component IC025, Empirical Bayes Geometric Mean EBGM05, Benjamini-Hochberg FDR.

Outputs -> results/
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)
DB = DERIVED / "faers.sqlite"

DRUGS: dict[str, list[str]] = {
    "ethambutol": ["ETHAMBUTOL"],
    "isoniazid": ["ISONIAZID"],
    "rifampicin": ["RIFAMPICIN", "RIFAMPIN"],
    "pyrazinamide": ["PYRAZINAMIDE"],
    "streptomycin": ["STREPTOMYCIN"],
    "linezolid": ["LINEZOLID"],
}


# ------------------------------------------------------------------- statistics
def ror_ci(a, b, c, d, z=1.959964):
    if a == 0:
        return 0.0, 0.0, float("inf")
    A, B, C, D = float(a), float(b), float(c), float(d)
    if min(B, C, D) == 0:
        A, B, C, D = A + 0.5, B + 0.5, C + 0.5, D + 0.5
    ror = (A * D) / (B * C)
    se = math.sqrt(1 / A + 1 / B + 1 / C + 1 / D)
    return ror, ror * math.exp(-z * se), ror * math.exp(z * se)


def prr_stats(a, b, c, d):
    n_d, n_notd = a + b, c + d
    n_e, n_note = a + c, b + d
    n = n_d + n_notd
    if min(n_d, n_notd, n_e, n_note) == 0 or a == 0 or c == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    prr = (a / n_d) / (c / n_notd)
    se = math.sqrt(1 / a - 1 / n_d + 1 / c - 1 / n_notd)
    lo = math.exp(math.log(prr) - 1.959964 * se)
    hi = math.exp(math.log(prr) + 1.959964 * se)
    exp = np.array([[n_d * n_e / n, n_d * n_note / n],
                    [n_notd * n_e / n, n_notd * n_note / n]], dtype=float)
    obs = np.array([[a, b], [c, d]], dtype=float)
    yates = float(np.nansum((np.abs(obs - exp) - 0.5) ** 2 / exp))
    return prr, lo, hi, yates


def _digamma(x: float) -> float:
    r = 0.0
    while x < 6.0:
        r -= 1.0 / x
        x += 1.0
    f = 1.0 / (x * x)
    return (r + math.log(x) - 0.5 / x
            - f * (1 / 12 - f * (1 / 120 - f * (1 / 252 - f * (1 / 240 - f / 132)))))


def _trigamma(x: float) -> float:
    r = 0.0
    while x < 6.0:
        r += 1.0 / (x * x)
        x += 1.0
    f = 1.0 / (x * x)
    return r + 1 / x + f / 2 + f * f / 6 - f ** 3 / 30 + f ** 5 / 42


def ic025(a, b, c, d):
    n = a + b + c + d
    n_e, n_d = a + c, a + b
    if n == 0 or n_e == 0 or n_d == 0:
        return float("nan"), float("nan")
    exp_n = n_e * n_d / n
    ic = math.log2((a + 0.5) / (exp_n + 0.5))
    aa, bb = 1.0 + a, 1.0 + exp_n
    v = (_trigamma(aa) - _trigamma(aa + bb)) / math.log(2) ** 2
    if v <= 0 or not math.isfinite(v):
        return ic, float("nan")
    return ic, ic - 1.959964 * math.sqrt(v)


def _gammainc(s, x):
    if x <= 0:
        return 0.0
    if x < s + 1:
        term, total, n = 1.0 / s, 1.0 / s, s
        for _ in range(3000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        return total * math.exp(-x + s * math.log(x) - math.lgamma(s))
    tiny = 1e-300
    b = x + 1 - s
    cc, dd, h = 1 / tiny, 1 / b, 1 / b
    for i in range(1, 3000):
        an = -i * (i - s)
        b += 2
        dd = an * dd + b
        dd = tiny if abs(dd) < tiny else dd
        cc = b + an / cc
        cc = tiny if abs(cc) < tiny else cc
        dd = 1 / dd
        delta = cc * dd
        h *= delta
        if abs(delta - 1) < 1e-16:
            break
    return 1 - math.exp(-x + s * math.log(x) - math.lgamma(s)) * h


def _gamma_ppf(p, shape, scale):
    lo, hi = 0.0, max(scale * (shape + 10 * math.sqrt(shape) + 20), 1e-9)
    for _ in range(300):
        if _gammainc(shape, hi / scale) >= p:
            break
        hi *= 2
    for _ in range(400):
        mid = (lo + hi) / 2
        if _gammainc(shape, mid / scale) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def ebgm05(a, b, c, d, alpha=0.5, beta=0.5):
    n = a + b + c + d
    n_e, n_d = a + c, a + b
    if n == 0 or n_e == 0 or n_d == 0:
        return float("nan"), float("nan")
    exp_n = max(n_e * n_d / n, 1e-9)
    pa, pb = alpha + a, beta + exp_n
    return math.exp(_digamma(pa) - math.log(pb)), _gamma_ppf(0.05, pa, 1 / pb)


def bh_fdr(pvals) -> np.ndarray:
    p = np.asarray(pvals, dtype=float)
    out = np.full_like(p, np.nan)
    idx = np.where(np.isfinite(p))[0]
    if idx.size == 0:
        return out
    sub, order = p[idx], np.argsort(p[idx])
    ranked, m = sub[order], idx.size
    q, prev = np.empty(m), 1.0
    for k in range(m - 1, -1, -1):
        prev = min(prev, ranked[k] * m / (k + 1))
        q[k] = prev
    res = np.empty(m)
    res[order] = q
    out[idx] = res
    return out


# ------------------------------------------------------------------ DB helpers
def connect(readonly: bool = True) -> sqlite3.Connection:
    if not DB.exists():
        raise SystemExit(f"{DB} not found")
    if readonly:
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=900)
    else:
        con = sqlite3.connect(DB, timeout=1800, isolation_level=None)
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-1000000")
    return con


def build_dedup(refresh: bool = False) -> int:
    con = connect(readonly=False)
    try:
        have = con.execute("SELECT name FROM sqlite_master WHERE type='table' "
                           "AND name='dedup_map'").fetchone()
        if have and not refresh:
            n = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
            print(f"[dedup] reusing dedup_map: {n:,} unique cases")
            return n
        t0 = time.time()
        n_raw = con.execute("SELECT COUNT(*) FROM demo").fetchone()[0]
        print(f"[dedup] {n_raw:,} submitted records -> latest per CASEID ...")
        con.executescript("""
            DROP TABLE IF EXISTS dedup_map;
            CREATE TABLE dedup_map AS
            SELECT caseid, primaryid FROM (
                SELECT caseid, primaryid,
                       ROW_NUMBER() OVER (
                           PARTITION BY caseid
                           ORDER BY COALESCE(fda_dt,'') DESC,
                                    COALESCE(primaryid,'') DESC) AS rn
                FROM demo WHERE caseid IS NOT NULL AND caseid <> ''
            ) WHERE rn = 1;
        """)
        n = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
        print(f"[dedup] {n:,} unique cases ({n_raw - n:,} removed) "
              f"in {time.time()-t0:.0f}s")
        return n
    finally:
        con.close()


def ensure_index_tables(con: sqlite3.Connection) -> None:
    have = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    if "dedup_map" not in have:
        raise SystemExit("dedup_map missing")


def drug_case(con, subs: list[str], roles: tuple[str, ...] | None = None) -> set:
    like = " OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
                        "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?"] * len(subs))
    params: list = []
    for s in subs:
        params += [f"%{s.upper()}%", f"%{s.upper()}%"]
    role_sql = ""
    if roles:
        role_sql = (" AND UPPER(COALESCE(d.role_cod,'')) IN ("
                    + ",".join("?" * len(roles)) + ")")
        params += [r.upper() for r in roles]
    q = f"""SELECT DISTINCT d.caseid FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE ({like}){role_sql}"""
    return {r[0] for r in con.execute(q, params)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", default=str(DERIVED / "ocular_terms.json"))
    ap.add_argument("--drugs", nargs="+", default=list(DRUGS))
    ap.add_argument("--suspect-only", action="store_true")
    args = ap.parse_args()

    refresh = not (DERIVED / "dedup_map.flag").exists()
    N = build_dedup(refresh=False)
    (DERIVED / "dedup_map.flag").write_text("ok", encoding="utf-8")
    print(f"[base] FAERS de-duplicated cases N = {N:,}")

    terms = pd.read_json(args.terms)
    if isinstance(terms, dict):
        terms = pd.DataFrame(terms)
    term_df = pd.DataFrame(terms)
    term_df["term"] = term_df["term"].str.upper()
    term_list = sorted(set(term_df["term"]))

    con = connect(readonly=True)
    print(f"[base] ocular MedDRA terms = {len(term_list)}")

    # whole-database frequency of each term
    ph = ",".join("?" * len(term_list))
    db_counts = dict(con.execute(
        f"""SELECT UPPER(r.pt), COUNT(DISTINCT r.caseid) FROM reac r
            JOIN dedup_map m ON r.primaryid = m.primaryid
            WHERE UPPER(r.pt) IN ({ph}) GROUP BY UPPER(r.pt)""", term_list))
    pd.Series(db_counts, name="n_cases").to_csv(
        DERIVED / "faers_term_counts.csv", encoding="utf-8-sig")

    t0 = time.time()
    summary = []
    rows = []
    for drug in args.drugs:
        subs = DRUGS[drug]
        cases = drug_case(con, subs)
        nd = len(cases)
        summary.append({"drug": drug, "n_cases": nd, "substances": "|".join(subs)})
        print(f"  {drug:14s} {nd:>8,} cases  ({time.time()-t0:.0f}s)")
        if nd == 0:
            continue
        # per-term intersection, computed in SQL for the whole panel at once
        case_q = f"""SELECT DISTINCT d.caseid FROM drug d
                     JOIN dedup_map m ON d.primaryid = m.primaryid
                     JOIN drugname dn ON dn.primaryid = d.primaryid
                                     AND dn.drug_seq = d.drug_seq
                     WHERE ({" OR ".join(["UPPER(COALESCE(dn.drugname,'')) LIKE ? OR UPPER(COALESCE(dn.prod_ai,'')) LIKE ?"] * len(subs))})"""
        cparams: list = []
        for s in subs:
            cparams += [f"%{s.upper()}%", f"%{s.upper()}%"]
        con.execute("DROP TABLE IF EXISTS temp.dc")
        con.execute(f"CREATE TEMP TABLE dc AS {case_q}", cparams)
        con.execute("CREATE INDEX IF NOT EXISTS temp.ix_dc ON dc(caseid)")
        hits = dict(con.execute(
            f"""SELECT UPPER(r.pt), COUNT(DISTINCT r.caseid) FROM reac r
                JOIN dedup_map m ON r.primaryid = m.primaryid
                WHERE UPPER(r.pt) IN ({ph})
                  AND r.caseid IN (SELECT caseid FROM dc)
                GROUP BY UPPER(r.pt)""", term_list))
        con.execute("DROP TABLE temp.dc")
        print(f"    intersections computed for {len(hits)} terms")
        for term in term_list:
            ne = int(db_counts.get(term, 0))
            if ne == 0:
                continue
            a = int(hits.get(term, 0))
            b, c = nd - a, ne - a
            d = N - a - b - c
            if min(b, c, d) < 0:
                raise AssertionError(f"negative cell {drug}/{term}: {a},{b},{c},{d}")
            ror, rlo, rhi = ror_ci(a, b, c, d)
            prr, plo, phi, chi2 = prr_stats(a, b, c, d)
            ic, icl = ic025(a, b, c, d)
            ebgm, elo = ebgm05(a, b, c, d)
            rows.append({"drug": drug, "term": term, "a": a, "b": b, "c": c, "d": d,
                         "n_drug": nd, "n_event": ne, "n_total": N,
                         "ror": ror, "ror_lcl": rlo, "ror_ucl": rhi,
                         "prr": prr, "prr_lcl": plo, "prr_ucl": phi,
                         "chi2_yates": chi2, "ic": ic, "ic025": icl,
                         "ebgm": ebgm, "ebgm05": elo})
    summary.append({"drug": "FAERS_ALL", "n_cases": N, "substances": ""})
    # merge with any earlier run, so a comparator-only invocation cannot drop the
    # index drug's row from the cohort table
    summ_path = RESULTS / "faers_dedup_summary.csv"
    new = pd.DataFrame(summary)
    if summ_path.exists():
        try:
            old = pd.read_csv(summ_path, encoding="utf-8-sig")
            merged = (pd.concat([old, new], ignore_index=True)
                        .drop_duplicates(subset=["drug"], keep="last"))
        except Exception:  # noqa: BLE001
            merged = new
    else:
        merged = new
    order = ["ethambutol", "isoniazid", "rifampicin", "pyrazinamide",
             "streptomycin", "linezolid", "FAERS_ALL"]
    merged["_o"] = merged.drug.map({k: i for i, k in enumerate(order)}).fillna(99)
    merged = merged.sort_values("_o").drop(columns="_o")
    merged.to_csv(summ_path, index=False, encoding="utf-8-sig")

    tab = pd.DataFrame(rows)
    from scipy import stats as st
    tab["p_chi2"] = st.chi2.sf(tab["chi2_yates"].fillna(0).clip(lower=0), df=1)
    tab["q_bh"] = bh_fdr(tab["p_chi2"].values)
    tab = tab.merge(term_df[["term", "group", "source"]].drop_duplicates("term"),
                    on="term", how="left")
    tab["signal_ror"] = (tab.ror_lcl > 1) & (tab.a >= 3)
    tab["signal_prr"] = (tab.prr >= 2) & (tab.chi2_yates >= 4) & (tab.a >= 3)
    tab["signal_ic"] = tab.ic025 > 0
    tab["signal_ebgm"] = tab.ebgm05 > 2
    tab["signal_strict"] = (tab.signal_ror & tab.signal_prr & tab.signal_ic
                            & (tab.q_bh < 0.05))
    tab.to_csv(DERIVED / "faers_2x2.csv", index=False, encoding="utf-8-sig")
    tab[tab.a >= 3].to_csv(RESULTS / "faers_signals_all_drugs.csv",
                           index=False, encoding="utf-8-sig")
    eth = tab[tab.drug == "ethambutol"].sort_values("ror", ascending=False)
    # always refresh the ethambutol-specific table, even when the run covers
    # other drugs only, so the file cannot be lost to a comparator-only run
    if not eth.empty:
        eth.to_csv(RESULTS / "faers_signals_ethambutol.csv", index=False,
                   encoding="utf-8-sig")
    else:
        prev = RESULTS / "faers_signals_ethambutol.csv"
        print(f"[note] no ethambutol rows in this run; keeping the existing "
              f"{prev.name} ({'present' if prev.exists() else 'MISSING'})")

    print("\n=== ethambutol ocular signals (a >= 3) ===")
    cols = ["term", "a", "ror", "ror_lcl", "prr", "ic025", "ebgm05", "q_bh",
            "signal_strict", "group"]
    if not eth.empty:
        print(eth[eth.a >= 3][cols].to_string(index=False, max_colwidth=42))
    con.close()
    print(f"\n-> {RESULTS / 'faers_signals_ethambutol.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
