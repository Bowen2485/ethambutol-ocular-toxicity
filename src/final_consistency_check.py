# -*- coding: utf-8 -*-
"""
Final consistency check across the manuscripts and the files they promise.

Run after the table rebuild and the version synchronisation, to confirm that every
artefact the text names exists, that the counts it quotes match the files, and that the
two language versions cover the same ground.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
EN = (MS / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (MS / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")

print("=" * 100)
print("1. Table files named in the English version, and whether they exist")
print("=" * 100)
blocks = re.findall(r"`(tables/[^`]+\.csv)`", EN) + \
         re.findall(r"`(results/[^`]+\.(?:csv|json))`", EN)
ok = True
for b in sorted(set(blocks)):
    p = ROOT / b
    exists = p.exists()
    ok &= exists
    print(f"  {'ok     ' if exists else 'MISSING'}  {b}")
print(f"\n  all referenced artefacts present: {ok}")

print()
print("=" * 100)
print("2. Figure files named in the lists, and whether they exist")
print("=" * 100)
figs = sorted(int(m) for m in re.findall(r"\*\*Figure (\d+)\*\*", EN))
for n in figs:
    hits = list((ROOT / "figures").glob(f"Figure{n}_*")) if \
        (ROOT / "figures").exists() else []
    print(f"  Figure {n:>2d}  {len(hits)} file(s)   "
          f"{', '.join(sorted(p.name for p in hits))}")
print(f"\n  figures declared: {figs}")

print()
print("=" * 100)
print("3. Quoted counts against the rebuilt files")
print("=" * 100)
CHECKS = [
    ("Table 2 signals", "tables/Table2_signals.csv", 152, "152 "),
    ("Table 2b strict", "tables/Table2b_signals_strict.csv", 45, "45"),
    ("Table 2c spectrum", "tables/Table2c_toxicity_spectrum.csv", 30, "top 30"),
    ("Table 2d anatomical grouping", "tables/Table2d_panel_anatomical.csv", 5, "152 terms"),
    ("Table 2 full panel", "tables/Table2_signals_full_panel.csv", 178, "178"),
]
for label, rel, expected, quoted in CHECKS:
    p = ROOT / rel
    if not p.exists():
        print(f"  {label:24s} file missing")
        continue
    n = len(pd.read_csv(p, encoding="utf-8-sig"))
    text_ok = quoted in EN or quoted in CN
    print(f"  {label:24s} file {n:>4} rows, expected {expected:>4}  "
          f"{'ok' if n == expected else 'MISMATCH'};  "
          f"text quotes {quoted!r}: {'yes' if text_ok else 'no'}")

print()
print("=" * 100)
print("4. Version parity")
print("=" * 100)
#: The reference-count sentinel is derived from the reference list rather than
#: hard-coded.  It was written when the paper had 28 references and went stale when
#: the list grew to 32, so the check reported a false mismatch on every run.
_refs = (MS / "references_en.md").read_text(encoding="utf-8")
N_REFS = len(re.findall(r"^\s*\d+\.\s", _refs, flags=re.M))

PAIRS = [
    ("de-duplicated cases", "20,328,568", "20 328 568"),
    ("ethambutol cases (toxicology)", "13,804", "13 804"),
    ("ethambutol cases (within class)", "15,573", "15 573"),
    ("JADER cases", "1,054,239", "1,054,239"),
    ("regimen rate ratio", "3.28", "3.28"),
    ("heavy atoms", "fourteen heavy", "14 个重原子"),
    ("rotatable bonds", "nine rotatable", "9 个可旋转键"),
    ("STROBE", "STROBE", "STROBE"),
    ("RECORD-PE", "RECORD-PE", "RECORD-PE"),
    ("GAFF-2.11", "GAFF-2.11", "GAFF-2.11"),
    ("reference count", f"{N_REFS}.", f"{N_REFS} 条"),
]
for label, en_k, cn_k in PAIRS:
    e, c = en_k in EN, cn_k in CN
    print(f"  {label:32s} EN {'yes' if e else 'NO ':3s}  CN {'yes' if c else 'NO ':3s}"
          f"  {'ok' if e and c else '<-- check'}")

print()
print("=" * 100)
print("5. Size")
print("=" * 100)
print(f"  EN: {len(EN.splitlines()):>5} lines, {len(EN.split()):>6} words")
print(f"  CN: {len(CN.splitlines()):>5} lines, "
      f"{len(re.findall(r'[一-鿿]', CN)):>6} Chinese characters")
