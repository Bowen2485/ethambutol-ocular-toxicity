# -*- coding: utf-8 -*-
"""
Rebuild the two MR tables from the current result files.

Why this exists
    Table8_mr.csv was written on 2026-10-13 from the then-current
    results/mr_opengwas_results.csv.  That file was regenerated on 2026-10-16 (13 rows to 60,
    27 columns to 29) when the panel gained its positive control and the remaining exposures,
    and Table 8 was never rebuilt.  The published Table 8 is therefore a copy of a file that no
    longer exists in that form, and the stale copy it came from still carries the type 2
    diabetes row computed from the deleted FinnGen caches.

    The renal-function estimates are a separate analysis and are not in Table 8 at all:
    Table 8 is the main panel, whose smallest q is 0.0203 (the body-mass-index positive
    control), so the manuscript's "all q >= 0.87" cannot be read off it.  Those 18 rows come
    from results/mr_supplementary_results.csv and are written here as TableS1.

What it writes
    tables/Table8_mr.csv        the main panel, verbatim from mr_opengwas_results.csv
    tables/TableS1_mr_renal.csv the renal-function analysis, reordered for reading
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"

#: reader-facing columns first, diagnostics after, and nothing dropped
ORDER = ["exposure", "gwas_id", "outcome", "outcome_label", "n_snp", "method",
         "or", "or_lcl", "or_ucl", "p", "p_fdr", "beta", "se",
         "Q", "Q_df", "Q_p", "egger_intercept", "egger_intercept_p",
         "egger_beta", "egger_se", "wm_beta", "wm_se", "wm_p",
         "steiger_r2_exposure", "steiger_r2_outcome", "steiger_correct",
         "exposure_n", "snps"]


def read(name):
    p = RESULTS / name
    with open(p, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        return rd.fieldnames or [], list(rd)


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def reorder(cols):
    return [c for c in ORDER if c in cols] + [c for c in cols if c not in ORDER]


print("=" * 92)
print("1. Table 8 - the main panel")
print("=" * 92)
cols, rows = read("mr_opengwas_results.csv")
print(f"  source: results/mr_opengwas_results.csv, {len(rows)} rows, {len(cols)} columns")
out8 = TABLES / "Table8_mr.csv"
before = out8.read_text(encoding="utf-8-sig").count("\n") if out8.exists() else 0
write(out8, cols, rows)
print(f"  Table8_mr.csv: {before} lines before -> {len(rows) + 1} lines after")
print(f"  {'exposure':<20} {'outcome':<30} {'n_snp':>6} {'OR':>8} {'q':>9}")
for r in rows:
    print(f"  {r['exposure'][:18]:<20} {r['outcome'][:28]:<30} {r['n_snp']:>6} "
          f"{float(r['or']):>8.3f} {float(r['p_fdr']):>9.4f}")
qs = [float(r["p_fdr"]) for r in rows]
print(f"  q range in the main panel: {min(qs):.4f} to {max(qs):.4f}")
print("  the manuscript's 'all q >= 0.87' cannot be read off this table: the positive")
print("  control reaches q = 0.0203 here")

print()
print("=" * 92)
print("2. Table S1 - the renal-function analysis")
print("=" * 92)
cols, rows = read("mr_supplementary_results.csv")
print(f"  source: results/mr_supplementary_results.csv, {len(rows)} rows, {len(cols)} columns")
write(TABLES / "TableS1_mr_renal.csv", reorder(cols), rows)
print(f"  TableS1_mr_renal.csv written, {len(rows) + 1} lines")
print(f"  {'exposure':<20} {'outcome':<30} {'n_snp':>6} {'OR':>8} {'q':>9}")
for r in rows:
    print(f"  {r['exposure'][:18]:<20} {r['outcome'][:28]:<30} {r['n_snp']:>6} "
          f"{float(r['or']):>8.3f} {float(r['p_fdr']):>9.4f}")
qs = [float(r["p_fdr"]) for r in rows]
ns = sorted({int(r["n_snp"]) for r in rows})
print(f"  instruments per exposure: {ns}")
print(f"  q range: {min(qs):.4f} to {max(qs):.4f}  (the manuscript's 'q >= 0.87' is this)")

print()
print("=" * 92)
print("3. The pair the manuscript quotes, cystatin C -> optic neuritis")
print("=" * 92)
for label, cols, rows in (("Table 8 (main panel)", *read("mr_opengwas_results.csv")),
                          ("Table S1 (renal)", *read("mr_supplementary_results.csv"))):
    for r in rows:
        if "ystatin" in r.get("exposure", "") and r.get("outcome") == "H7_OPTNEURITIS":
            print(f"  {label:<24} n_snp={r['n_snp']:>4} "
                  f"OR={float(r['or']):.3f} ({float(r['or_lcl']):.3f}-{float(r['or_ucl']):.3f}) "
                  f"q={float(r['p_fdr']):.4f}")
print()
print("  The manuscript now quotes the Table S1 row, which is the analysis whose instrument")
print("  counts (151/162/186) and smallest q (0.8695) the surrounding sentence already uses.")

print()
print("=" * 92)
print("4. The MR section of tables/results_digest.md")
print("=" * 92)


def fmt(x, nd=2):
    """The same formatter make_tables.py uses, so the digest text is reproducible."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "NA"
    if v != v or v in (float("inf"), float("-inf")):
        return "NA"
    return f"{v:.{nd}f}"


def block(rows, caption, show_all):
    out = [caption, f"Estimates: {len(rows)}",
           "| Exposure | Outcome | SNPs | Method | OR (95% CI) | p |",
           "|---|---|---|---|---|---|"]
    shown = rows if show_all else sorted(
        [r for r in rows if r.get("p") not in (None, "")], key=lambda r: float(r["p"]))[:25]
    for r in shown:
        p = float(r["p"])
        p_txt = "<1e-300" if p == 0 else f"{p:.3g}"
        out.append(f"| {r['exposure']} | {r['outcome']} | {int(r['n_snp'])} | {r['method']} | "
                   f"{fmt(r['or'], 3)} ({fmt(r['or_lcl'], 3)}-{fmt(r['or_ucl'], 3)}) | {p_txt} |")
    return out


_, panel_rows = read("mr_opengwas_results.csv")
_, renal_rows = read("mr_supplementary_results.csv")
new_section = (
    ["## 8. Two-sample MR (OpenGWAS exposures -> FinnGen optic-nerve outcomes)", ""]
    + block(panel_rows, "The main panel, results/mr_opengwas_results.csv", show_all=False)
    + ["", "The renal-function analysis is reported separately as Table S1, because it uses a",
       "wider harmonisation than the main panel; its smallest q is 0.8695. The main panel's",
       "smallest q is 0.0203, from the body-mass-index positive control, so the manuscript's",
       "renal statement 'all q >= 0.87' is a statement about this second block and not about",
       "the first.", ""]
    + block(renal_rows, "The renal-function analysis, results/mr_supplementary_results.csv",
            show_all=True)
)

DIGEST = TABLES / "results_digest.md"
lines = DIGEST.read_text(encoding="utf-8").split("\n")
start = next(i for i, ln in enumerate(lines) if ln.startswith("## 8. Two-sample MR"))
end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
old_len = end - start
lines[start:end] = new_section + [""]
DIGEST.write_text("\n".join(lines), encoding="utf-8")
print(f"  section 8 replaced: {old_len} lines -> {len(new_section) + 1} lines")
print(f"  main panel estimates listed: {len(block(panel_rows, '', False)) - 4} of "
      f"{len(panel_rows)} (top 25 by p, as make_tables.py does)")
print(f"  renal estimates listed: {len(renal_rows)} of {len(renal_rows)}")
print()
print("  Note: results_digest.md and Table 8 are both written by src/make_tables.py, which")
print("  rebuilds every table from results/*.csv.  A full run of that script would produce this")
print("  same section 8 and this same Table 8; only these two were rebuilt here, so that the")
print("  other tables are not churned on the eve of submission.")
print("=" * 92)
