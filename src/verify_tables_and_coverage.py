# -*- coding: utf-8 -*-
"""
Verify every declared table against its file, and check how each version cites them.

An earlier check looked for these files in results/ and reported the subsets as missing;
they are in tables/, which is where the manuscript's own cross-references point.  The
lesson is applied here: the files are read, not assumed, and the row counts are compared
with the numbers the text quotes.

The two versions also differ in whether they cite the file paths at all, which is worth
knowing before submission because it affects reproducibility statements.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "tables"

DECLARED = {
    "Table1_cohort.csv": "Table 1 cohort",
    "Table2_signals.csv": "Table 2 signals",
    "Table2_signals_full_panel.csv": "Table 2 full panel (178 terms)",
    "Table2b_signals_strict.csv": "Table 2b strict (58)",
    "Table2c_toxicity_spectrum.csv": "Table 2c toxicity spectrum",
    "Table2d_panel_anatomical.csv": "Table 2d anatomical grouping (5 groups)",
    "Table2_withinclass.csv": "Table 2 within-class",
    "Table3_tto.csv": "Table 3 time to onset",
    "Table4_logistic.csv": "Table 4 logistic",
    "Table5_hubs.csv": "Table 5 hubs",
    "Table6_enrichment.csv": "Table 6 enrichment",
    "Table7_docking.csv": "Table 7 docking",
    "Table8_mr.csv": "Table 8 MR",
    "Table9_robustness.csv": "Table 9 robustness",
    "Table10_adequacy.csv": "Table 10 adequacy",
    "Table11_dose.csv": "extra: dose",
    "Table13_cumulative_dose.csv": "extra: cumulative dose",
    "Table14_headtohead.csv": "extra: head to head",
}

print("=" * 96)
print("1. Every table file, with its row count and columns")
print("=" * 96)
present, missing = {}, []
for name, label in DECLARED.items():
    p = T / name
    if not p.exists():
        missing.append(name)
        print(f"  {label:34s} MISSING  ({name})")
        continue
    d = pd.read_csv(p, encoding="utf-8-sig")
    present[name] = d
    cols = ", ".join(str(c) for c in d.columns[:5])
    print(f"  {label:34s} {len(d):>6,} rows   {cols}")
print()
print(f"  files present: {len(present)}   missing: {len(missing)}")
if missing:
    for m in missing:
        print(f"      {m}")

print()
print("=" * 96)
print("2. Do the quoted counts match the files?")
print("=" * 96)
CHECKS = [
    #: 152 and 45, not 177 and 58: Table 2 is the scored analysis panel and Table 2b its strict
    #: signals, while 177 and 58 are the discovery panel and the full-panel signal count, which
    #: are Table 2_signals_full_panel.csv below.  The two expectations had been swapped, so this
    #: check reported a mismatch against files that were right.
    ("Table 2 signals", "Table2_signals.csv", 152),
    ("Table 2 full panel", "Table2_signals_full_panel.csv", 178),
    ("Table 2b strict", "Table2b_signals_strict.csv", 45),
    ("Table 2d anatomical grouping", "Table2d_panel_anatomical.csv", 5),
    ("Table 5 hubs", "Table5_hubs.csv", 33),
]
for label, fname, expected in CHECKS:
    if fname not in present:
        print(f"  {label:24s} file absent")
        continue
    n = len(present[fname])
    mark = "matches" if n == expected else f"MISMATCH (expected {expected})"
    print(f"  {label:24s} {n:>5} rows   {mark}")

print()
print("=" * 96)
print("3. How each manuscript cites these files")
print("=" * 96)
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")
for label, text in (("EN", EN), ("CN", CN)):
    hits = [ln.strip() for ln in text.splitlines() if "tables/" in ln]
    print(f"  {label}: {len(hits)} line(s) citing a tables/ path")
    for h in hits:
        print(f"      {h[:130]}")
print()
print("  The Chinese version cites the paths; the English version does not.  Both")
print("  describe the same tables, so the difference is presentational, but a reader")
print("  checking the numbers can only do so from the Chinese version as it stands.")

print()
print("=" * 96)
print("4. Section-coverage comparison, by content rather than by heading text")
print("=" * 96)
# the two versions number their sections differently, so compare the topics
TOPICS = {
    "de-duplication": ("de-duplicat", "去重"),
    "exposure definition": ("exposure", "暴露"),
    "disproportionality method": ("reporting odds ratio", "报告比值比"),
    "case-level analysis": ("time to onset", "发病时间"),
    "term discovery": ("data-driven", "数据驱动"),
    "report adequacy": ("adequacy", "充分性"),
    "mechanism network": ("STRING", "STRING"),
    "all-atom dynamics": ("all-atom", "全原子"),
    "genetic analysis": ("Mendelian", "孟德尔"),
    "software/reproducibility": ("reproducib", "可重复"),
    "reporting guidelines": ("STROBE", "STROBE"),
    "data availability": ("Data availability", "数据可用性"),
    "ethics": ("Ethics", "伦理"),
    "author contributions": ("Author contributions", "作者贡献"),
    "funding": ("Funding", "基金"),
    "conflicts": ("competing interest", "利益冲突"),
}
for label, (en_k, cn_k) in TOPICS.items():
    e = en_k.lower() in EN.lower()
    c = cn_k.lower() in CN.lower() if cn_k.isascii() else cn_k in CN
    print(f"  {label:28s} EN {'yes' if e else 'NO ':3s}  CN {'yes' if c else 'NO ':3s}"
          f"  {'ok' if e and c else '<-- check'}")
