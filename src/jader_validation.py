# -*- coding: utf-8 -*-
"""
External validation of the optic-nerve signal in JADER, the Japanese ADR database.

Why this is the test that matters
    Every pharmacovigilance finding in the paper comes from FAERS.  A split of FAERS by
    receipt year showed the signal is not an artefact of one reporting era, but both
    halves share the same reporters, the same submission routes and the same structural
    biases - so it cannot be a property of the drug rather than of the database.  JADER
    is a separate national system with different reporters and a different reporting
    culture, so agreement between the two is evidence of a different order.

    openFDA was rejected for this purpose: it serves FAERS, so replicating a FAERS
    finding in it would be circular.

Terms
    JADER stores Japanese MedDRA/J preferred terms and has no English column, so the
    mapping was read out of the data rather than assumed:
        OPTIC NEUROPATHY        -> 視神経症
        OPTIC NEURITIS          -> 視神経炎
        OPTIC ATROPHY           -> 視神経萎縮
        TOXIC OPTIC NEUROPATHY  -> 中毒性視神経症
        VISUAL ACUITY REDUCED   -> 視力低下
        VISUAL FIELD DEFECT      -> 視野欠損
        COLOUR VISION DEFICIENCY -> 色覚異常
        cataract 白内障, glaucoma 緑内障, dry eye ドライアイ (negative controls)

Exposure
    JADER marks each drug line with 医薬品の関与, taking one of three values:
    被疑薬 (suspect), 併用薬 (concomitant) and 相互作用 (interaction).  The primary
    analysis uses 被疑薬 only, which is JADER's counterpart of the FAERS primary/secondary
    suspect restriction, and a sensitivity analysis uses all roles.

    2x2 per term:
        a = cases with a suspect-ethambutol line and the term
        b = cases with a suspect-ethambutol line and not the term
        c = other cases with the term
        d = other cases without the term
        ROR = (a/b)/(c/d), Woolf confidence interval, chi-square with Yates correction

Usage
    python src/jader_validation.py
"""
from __future__ import annotations

import collections
import csv
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
JADER = ROOT / "data" / "raw" / "jader"
RESULTS = ROOT / "results"
ENC = "shift_jis"

#: ethambutol as it appears in the Japanese generic-name column
ETHAMBUTOL = ["エタンブトール"]
#: antitubercular comparators, used for the within-class denominator
ANTITB = {
    "イソニアジド": "isoniazid",
    "リファンピシン": "rifampicin",
    "ピラジナミド": "pyrazinamide",
    "ストレプトマイシン": "streptomycin",
    "エタンブトール": "ethambutol",
}

#: reaction term sets; the values are the exact MedDRA/J strings present in the data
TERMS = {
    "optic neuropathy": ["視神経症"],
    "optic neuritis": ["視神経炎"],
    "optic atrophy": ["視神経萎縮"],
    "toxic optic neuropathy": ["中毒性視神経症"],
    "visual acuity reduced": ["視力低下", "視力障害"],
    "visual field defect": ["視野欠損"],
    "colour vision deficiency": ["色覚異常", "異常３色覚", "後天性色覚異常"],
    "cataract": ["白内障"],
    "glaucoma": ["緑内障"],
    "dry eye": ["ドライアイ"],
}
CONTROLS = ["cataract", "glaucoma", "dry eye"]


def ror_ci(a: int, b: int, c: int, d: int, z: float = 1.959964):
    """ROR with a Woolf interval, matching the FAERS analysis."""
    if a == 0:
        return 0.0, 0.0, float("inf")
    A, B, C, D = float(a), float(b), float(c), float(d)
    if min(B, C, D) == 0:
        A, B, C, D = A + 0.5, B + 0.5, C + 0.5, D + 0.5
    ror = (A * D) / (B * C)
    se = math.sqrt(1 / A + 1 / B + 1 / C + 1 / D)
    return ror, ror * math.exp(-z * se), ror * math.exp(z * se)


def yates_chi2(a: int, b: int, c: int, d: int) -> float:
    n = a + b + c + d
    if n == 0:
        return 0.0
    num = n * (abs(a * d - b * c) - n / 2) ** 2
    den = (a + b) * (c + d) * (a + c) * (b + d)
    return num / den if den else 0.0


def load_cases() -> set[str]:
    """Every case identifier in the demo table."""
    out = set()
    with (JADER / "demo202609.csv").open(encoding=ENC, errors="replace",
                                          newline="") as fh:
        rd = csv.reader(fh)
        next(rd)
        for row in rd:
            if row and row[0].strip():
                out.add(row[0].strip())
    return out


def load_events() -> tuple[dict, dict]:
    """case -> set of matched term groups, and raw term frequencies."""
    case_terms: dict[str, set] = collections.defaultdict(set)
    freq = collections.Counter()
    with (JADER / "reac202609.csv").open(encoding=ENC, errors="replace",
                                         newline="") as fh:
        rd = csv.reader(fh)
        next(rd)
        for row in rd:
            if len(row) < 4:
                continue
            cid, term = row[0].strip(), row[3].strip()
            if not cid or not term:
                continue
            freq[term] += 1
            for group, strings in TERMS.items():
                if term in strings:
                    case_terms[cid].add(group)
    return case_terms, freq


def load_exposure() -> tuple[dict, dict]:
    """case -> set of suspect drugs, and case -> set of all drugs mentioned."""
    suspect: dict[str, set] = collections.defaultdict(set)
    anyrole: dict[str, set] = collections.defaultdict(set)
    with (JADER / "drug202609.csv").open(encoding=ENC, errors="replace",
                                         newline="") as fh:
        rd = csv.reader(fh)
        next(rd)
        for row in rd:
            if len(row) < 6:
                continue
            cid, role, generic = row[0].strip(), row[3].strip(), row[4].strip()
            brand = row[5].strip()
            if not cid:
                continue
            name = generic or brand
            if role == "被疑薬":
                suspect[cid].add(name)
            anyrole[cid].add(name)
    return suspect, anyrole


def main() -> int:
    print("[1] loading case identifiers")
    all_cases = load_cases()
    N = len(all_cases)
    print(f"    {N:,} cases in demo202609.csv")

    print("[2] loading reactions and mapping to the FAERS term groups")
    case_terms, freq = load_events()
    print(f"    {len(case_terms):,} cases carry at least one mapped term")
    for g, s in TERMS.items():
        n = sum(freq[x] for x in s)
        print(f"      {g:26s} {n:>8,} reaction records")

    print("[3] loading drugs")
    suspect, anyrole = load_exposure()
    emb_suspect = {c for c, d in suspect.items()
                   if any(any(e in x for e in ETHAMBUTOL) for x in d)}
    emb_any = {c for c, d in anyrole.items()
               if any(any(e in x for e in ETHAMBUTOL) for x in d)}
    print(f"    cases with ethambutol as a suspect drug : {len(emb_suspect):,}")
    print(f"    cases mentioning ethambutol in any role : {len(emb_any):,}")

    rows = []
    for label, emb in (("suspect only", emb_suspect),
                       ("any role", emb_any)):
        for group in TERMS:
            have = {c for c in all_cases if group in case_terms.get(c, ())}
            a = len(emb & have)
            b = len(emb) - a
            c_ = len(have) - a
            d = N - a - b - c_
            ror, lo, hi = ror_ci(a, b, c_, d)
            rows.append({
                "analysis": label, "term": group,
                "a": a, "b": b, "c": c_, "d": d,
                "n_ethambutol": len(emb), "n_event": len(have),
                "ror": round(ror, 3) if math.isfinite(ror) else "",
                "ror_lcl": round(lo, 3) if math.isfinite(lo) else "",
                "ror_ucl": round(hi, 3) if math.isfinite(hi) else "",
                "chi2_yates": round(yates_chi2(a, b, c_, d), 3),
                "signal": bool(a >= 3 and lo > 1) if math.isfinite(lo) else False,
                "control": group in CONTROLS,
            })

    df = pd.DataFrame(rows)
    out = RESULTS / "jader_validation.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")

    print()
    print("=" * 100)
    print("JADER results, ethambutol as the suspect drug (counterpart of FAERS PS/SS)")
    print("=" * 100)
    sub = df[df.analysis == "suspect only"]
    print(f"  {'term':26s} {'a':>5s} {'events':>8s} {'ROR':>9s} "
          f"{'95% CI':>19s} {'chi2':>8s}  signal")
    for _, r in sub.iterrows():
        ci = (f"{r.ror_lcl}-{r.ror_ucl}" if r.ror_lcl != "" else "-")
        print(f"  {r.term:26s} {r.a:>5} {r.n_event:>8,} "
              f"{(f'{r.ror:.2f}' if r.ror != '' else '-'):>9s} {ci:>19s} "
              f"{r.chi2_yates:>8.1f}  {r.signal}"
              + ("   [control]" if r.control else ""))

    print()
    print("=" * 100)
    print("Ethambutol against a within-class denominator")
    print("=" * 100)
    # every case whose suspect drugs include any antitubercular agent
    att = {c for c, d in suspect.items()
           if any(any(a in x for a in ANTITB) for x in d)}
    print(f"  cases with any antitubercular drug as suspect: {len(att):,}")
    for group in TERMS:
        have = {c for c in att if group in case_terms.get(c, ())}
        a = len(emb_suspect & have)
        b = len(emb_suspect) - a
        others = att - emb_suspect
        c_ = len(others & have)
        d = len(others) - c_
        ror, lo, hi = ror_ci(a, b, c_, d)
        ci = f"{lo:.2f}-{hi:.2f}" if math.isfinite(lo) else "-"
        print(f"  {group:26s} a={a:>4}  ROR={ror if math.isfinite(ror) else 0:>8.2f} "
              f"({ci})" + ("   [control]" if group in CONTROLS else ""))

    print()
    print(f"-> {out}")
    print()
    print("=" * 100)
    print("How to read this against FAERS")
    print("=" * 100)
    print("""  The two databases are not directly comparable in magnitude: JADER is a tenth the
  size, and its reporting culture, its suspect-drug coding and its population all
  differ.  What matters is whether the same pattern appears - an optic-nerve signal
  present, and the non-specific ocular terms absent.  A pattern that repeats in an
  independent national system is evidence about the drug; a magnitude that happens to
  match would be a coincidence.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
