# -*- coding: utf-8 -*-
"""
Step through harmonise() to find where the 197 rsID matches are lost.

The rsID route should yield 197 matched instruments and harmonise() returns nothing, so
the loss happens inside.  Rather than reason about which line drops them, each stage is
executed here on the same inputs and its output size printed, so the stage that empties
is identified.

This matters beyond one pair: if harmonise() silently returns nothing whatever the
input, every exposure-outcome estimate in the panel is missing for a reason that has
nothing to do with the data.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"

inst = pd.read_csv(RAW / "tophits_ebi-a-GCST90014006_5e-08.tsv", sep="\t")
exp = inst.rename(columns={"position": "pos", "se": "sebeta"}).copy()
exp["chrom"] = exp["chr"].astype(str).str.replace("chr", "", regex=False)
exp["pos"] = pd.to_numeric(exp["pos"], errors="coerce")
exp["rsids"] = exp["rsid"].astype(str)
exp = exp.dropna(subset=["pos", "beta", "sebeta"])

scans = sorted(RAW.glob("mr_ebi-a-GCST90014006_H7_OPTNEURITIS_*.tsv"))
ou = pd.concat([pd.read_csv(f, sep="\t") for f in scans], ignore_index=True)

print("=" * 96)
print("Replicating harmonise() stage by stage")
print("=" * 96)
print(f"  exposure rows : {len(exp)}   outcome rows : {len(ou)}")

ex, o = exp.copy(), ou.copy()
ex["rs_key"] = ex.get("rsids", pd.Series(dtype=str)).astype(str).str.strip()
o["rs_key"] = o.get("rsids", pd.Series(dtype=str)).astype(str).str.strip()
print(f"  after rs_key  : exposure {len(ex)}  outcome {len(o)}")
print(f"      exposure rs_key sample : {ex['rs_key'].head(4).tolist()}")
print(f"      outcome  rs_key sample : {o['rs_key'].head(4).tolist()}")

ex["pos_key"] = ex["chrom"].astype(str) + ":" + ex["pos"].astype(int).astype(str)
o["pos_key"] = o["chrom"].astype(str) + ":" + o["pos"].astype(int).astype(str)

o["rs_key"] = o["rs_key"].str.split(";")
o = o.explode("rs_key")
o["rs_key"] = o["rs_key"].astype(str).str.strip()
print(f"  after explode : outcome {len(o)}")

usable = ex[ex["rs_key"].notna() & (ex["rs_key"] != "") & (ex["rs_key"] != "nan")]
print(f"  usable exposure rows : {len(usable)}")

m_rs = usable.merge(o, on="rs_key", suffixes=("_exp", "_out"))
print(f"  after rsID merge     : {len(m_rs)}")
print(f"      resulting columns  : {list(m_rs.columns)[:24]}")
if len(m_rs):
    print(f"      pos_key_exp present: {'pos_key_exp' in m_rs.columns}")
    print(f"      pos_key_out present: {'pos_key_out' in m_rs.columns}")
    print(f"      alt_exp present    : {'alt_exp' in m_rs.columns}")
    print(f"      alt_out present    : {'alt_out' in m_rs.columns}")

m_pos = ex.merge(o, on="pos_key", suffixes=("_exp", "_out"))
print(f"  after position merge : {len(m_pos)}")

print()
print("=" * 96)
print("The check that returns an empty frame")
print("=" * 96)
print(f"  condition: if m.empty or 'alt_exp' not in m.columns or 'alt_out' not in m.columns")
if len(m_rs):
    print(f"      m_rs not empty            : True")
    print(f"      'alt_exp' in m_rs.columns : {'alt_exp' in m_rs.columns}")
    print(f"      'alt_out' in m_rs.columns : {'alt_out' in m_rs.columns}")
    print()
    print("  The exposure frame from the OpenGWAS instrument file has columns "
          f"{list(exp.columns)}")
    print("  and the outcome frame has columns " + str(list(ou.columns)))
    print()
    if "alt" not in exp.columns:
        print("  => the exposure side has no 'alt' column, so the merge cannot produce")
        print("     alt_exp, and harmonise() returns empty regardless of how many")
        print("     variants matched.  The instrument file uses 'ea'/'nea' for the")
        print("     effect and other alleles, not 'alt'/'ref'.")
if len(m_pos):
    print(f"      position route also yields {len(m_pos)} rows but needs the same "
          f"columns")
