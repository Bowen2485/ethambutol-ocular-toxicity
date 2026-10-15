# -*- coding: utf-8 -*-
"""
Check whether the pre-existing cache also holds one phenotype's data in six files.

The files written during this session are byte-identical across phenotypes, because the
fetch script queried one phenotype and copied the result to all six on the reasoning
that the variant positions are shared.  The positions are shared; the effect sizes are
not, so that reasoning was wrong and those files have to be rewritten.

The immediate question is whether the same fault is present in the 4,825 files that were
already cached, because if it is, the Mendelian randomisation results reported in the
manuscript rest on phenotype-identical outcome data and are not what they claim to be.
That is answerable directly: compare one window across two phenotypes in an older
exposure.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opengwas"
PHENOS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
          "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]

print("=" * 100)
print("Pre-existing cache: eGFR (ebi-a-GCST90103634), written in an earlier session")
print("=" * 100)
OLD = "ebi-a-GCST90103634"
rows = []
for ph in PHENOS:
    files = sorted(RAW.glob(f"mr_{OLD}_{ph}_*_0.tsv"))
    if not files:
        print(f"  {ph:26s} window 0 not found")
        continue
    f = files[0]
    d = pd.read_csv(f, sep="\t")
    rows.append({"phenotype": ph, "file": f.name, "rows": len(d),
                 "beta_mean": round(d.beta.mean(), 6),
                 "beta_sd": round(d.beta.std(), 6),
                 "md5": hashlib.md5(f.read_bytes()).hexdigest()[:12]})
s = pd.DataFrame(rows)
print(s.to_string(index=False))
print()
for col in ("rows", "beta_mean", "beta_sd", "md5"):
    vals = s[col].tolist()
    print(f"  {col:10s} distinct values: {len(set(vals))} of {len(vals)}")

print()
print("=" * 100)
print("Same check on a second older exposure: cystatin C")
print("=" * 100)
OLD2 = "ebi-a-GCST90025945"
rows2 = []
for ph in PHENOS:
    files = sorted(RAW.glob(f"mr_{OLD2}_{ph}_*_0.tsv"))
    if not files:
        continue
    f = files[0]
    d = pd.read_csv(f, sep="\t")
    rows2.append({"phenotype": ph, "rows": len(d),
                  "beta_mean": round(d.beta.mean(), 6),
                  "md5": hashlib.md5(f.read_bytes()).hexdigest()[:12]})
s2 = pd.DataFrame(rows2)
print(s2.to_string(index=False))
print()
for col in ("rows", "beta_mean", "md5"):
    vals = s2[col].tolist()
    print(f"  {col:10s} distinct values: {len(set(vals))} of {len(vals)}")

print()
print("=" * 100)
print("Which exposures are affected")
print("=" * 100)
NEW = ["ukb-b-13891", "ieu-b-25", "ieu-b-73", "ieu-b-4877",
       "ebi-a-GCST006867", "ebi-a-GCST90014006", "ieu-b-40"]
OLD_EXPOSURES = ["ebi-a-GCST90103634", "ebi-a-GCST90025945", "ebi-a-GCST90025946"]
print(f"  written this session ({len(NEW)}): {NEW}")
print(f"  pre-existing        ({len(OLD_EXPOSURES)}): {OLD_EXPOSURES}")
print()
for gid in OLD_EXPOSURES:
    files = sorted(RAW.glob(f"mr_{gid}_*_0.tsv"))
    if len(files) < 2:
        print(f"  {gid:22s} fewer than two phenotype files for window 0")
        continue
    hashes = {}
    for f in files:
        ph = next((p for p in PHENOS if f"_{p}_" in f.name), "?")
        hashes[ph] = hashlib.md5(f.read_bytes()).hexdigest()[:10]
    distinct = len(set(hashes.values()))
    verdict = ("PHENOTYPE-IDENTICAL - affected" if distinct == 1
               else f"phenotype-specific ({distinct} distinct) - sound")
    print(f"  {gid:22s} {verdict}")
