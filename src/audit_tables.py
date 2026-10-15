# -*- coding: utf-8 -*-
"""
Check that every table the manuscript declares has data behind it.

The figures are accounted for (nine PDF/PNG pairs) but the tables have never been
checked as artefacts, and the manuscript refers to numbered tables with letter
suffixes.  A declared table with no underlying file is a hole a reviewer can see, and
the table counts quoted in the text - 177 terms, 58 strict signals, 83 unclassified -
need to match whatever the analysis actually produced.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
DER = ROOT / "data" / "derived"

print("=" * 96)
print("1. Every CSV in results/ and data/derived/")
print("=" * 96)
for d in (RES, DER):
    if not d.exists():
        continue
    files = sorted(p for p in d.glob("*.csv"))
    print(f"\n  {d.relative_to(ROOT)}  ({len(files)} csv)")
    for p in files:
        try:
            n = sum(1 for _ in p.open(encoding="utf-8-sig", errors="replace")) - 1
        except Exception:  # noqa: BLE001
            n = -1
        print(f"      {p.name:52s} {n:>7,} rows  {p.stat().st_size/1024:>8.0f} KB")

print()
print("=" * 96)
print("2. Table-by-table check")
print("=" * 96)
WANTED = {
    "Table 1  study population": ["faers_population", "faers_table1", "population",
                                  "faers_exposures"],
    "Table 2  ocular signals (177)": ["faers_ocular", "ocular_signals", "faers_table2",
                                      "term_db", "faers_terms"],
    "Table 2b strict signals (58)": ["strict", "signal"],
    "Table 2c toxicity spectrum": ["spectrum", "toxicity"],
    "Table 2d unclassified (83)": ["unclassified", "unclass", "table2d", "uncategor"],
    "Table 3  time to onset": ["tto", "onset", "time_to"],
    "Table 4  logistic regression": ["logistic", "predictor", "regression"],
    "Table 5  hub genes": ["hub", "focus"],
    "Table 6  enrichment": ["enrich", "kegg", "go_", "reactome"],
    "Table 7  docking scores": ["dock", "vina", "score"],
    "Table 8  MR results": ["mr_", "mendel"],
    "Table 9  robustness": ["robust", "scenario"],
    "Table 10 report adequacy": ["adequacy", "complete", "report"],
}
all_files = list(RES.glob("*.csv")) + list(DER.glob("*.csv"))
for label, keys in WANTED.items():
    hits = [p.name for p in all_files
            if any(k.lower() in p.name.lower() for k in keys)]
    status = "found" if hits else "NO FILE FOUND"
    print(f"  {label:34s} {status}")
    for h in hits[:5]:
        print(f"        {h}")

print()
print("=" * 96)
print("3. Do the quoted counts match the data?")
print("=" * 96)
# the ocular term panel
for name in ("faers_ocular_signals.csv", "faers_terms.csv", "faers_full_panel.csv",
             "ocular_signals.csv"):
    p = RES / name
    if p.exists():
        d = pd.read_csv(p, encoding="utf-8-sig")
        print(f"  {name}: {len(d)} rows, columns {list(d.columns)[:10]}")
        for col in ("q_bh", "q", "signal", "is_signal"):
            if col in d.columns:
                try:
                    n_sig = int((d[col] <= 0.05).sum()) if col.startswith("q") \
                        else int(d[col].astype(bool).sum())
                    print(f"      strict signals by {col}: {n_sig}")
                except Exception:  # noqa: BLE001
                    pass
        break
else:
    print("  no single ocular-panel file found by the expected names; "
          "listing candidates:")
    for p in all_files:
        if "ocular" in p.name or "term" in p.name or "signal" in p.name:
            d = pd.read_csv(p, encoding="utf-8-sig")
            print(f"      {p.name}: {len(d)} rows, cols {list(d.columns)[:8]}")
