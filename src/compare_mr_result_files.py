# -*- coding: utf-8 -*-
"""Compare the MR result files across the two trees, field by field.

Written because a stale copy of mr_opengwas_results.csv is what Table8_mr.csv and the
manuscript's renal paragraph were built from, and the copies differ between the working
tree and the published repository.  Writes nothing.
"""
import csv
from pathlib import Path

W = Path(r"C:\Users\20200\Downloads\论文\投稿\Ethambutol_EyeTox")
R = Path(r"C:\Users\20200\Downloads\论文\投稿\ethambutol-ocular-toxicity")


def rows(p):
    if not p.exists():
        return None, None
    with open(p, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        return rd.fieldnames, list(rd)


def show(label, path):
    head, rs = rows(path)
    print("=" * 100)
    print(f"{label}\n  {path}")
    if head is None:
        print("  ABSENT")
        return
    print(f"  columns ({len(head)}): {','.join(head)}")
    print(f"  rows: {len(rs)}")
    key = "exposure" if "exposure" in (head or []) else head[0]
    print(f"  {'exposure':<46} {'n_snp':>6} {'or':>8} {'or_lcl':>8} {'or_ucl':>8} {'p_fdr':>9}")
    for r in rs:
        def g(k):
            return r.get(k, "")
        print(f"  {str(g(key))[:44]:<46} {str(g('n_snp')):>6} "
              f"{float(g('or')):>8.3f} {float(g('or_lcl')):>8.3f} {float(g('or_ucl')):>8.3f} "
              f"{str(g('p_fdr'))[:9]:>9}")


show("WORK TREE  mr_opengwas_results.csv  (2026-10-16)", W / "results" / "mr_opengwas_results.csv")
show("REPOSITORY mr_opengwas_results.csv (2026-10-13)", R / "results" / "mr_opengwas_results.csv")
show("WORK TREE  mr_supplementary_results.csv", W / "results" / "mr_supplementary_results.csv")
show("REPOSITORY mr_supplementary_results.csv", R / "results" / "mr_supplementary_results.csv")
show("WORK TREE  tables/Table8_mr.csv (the published table)", W / "tables" / "Table8_mr.csv")
show("REPOSITORY tables/Table8_mr.csv", R / "tables" / "Table8_mr.csv")

print("=" * 100)
print("Target pair, cystatin C -> optic neuritis, wherever it appears in the working tree:")
for label, p in (
    ("mr_opengwas_results.csv", W / "results" / "mr_opengwas_results.csv"),
    ("mr_supplementary_results.csv", W / "results" / "mr_supplementary_results.csv"),
    ("Table8_mr.csv", W / "tables" / "Table8_mr.csv"),
):
    head, rs = rows(p)
    for r in rs:
        exp = r.get("exposure", "")
        out = r.get("outcome", "")
        if "ystatin" in exp and out == "H7_OPTNEURITIS":
            print(f"  {label:<30} n_snp={r.get('n_snp'):>4} "
                  f"OR={float(r.get('or')):.4f} "
                  f"({float(r.get('or_lcl')):.4f}-{float(r.get('or_ucl')):.4f}) "
                  f"q={float(r.get('p_fdr')):.4f}")
print("=" * 100)
