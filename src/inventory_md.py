# -*- coding: utf-8 -*-
"""
Inventory the molecular dynamics work to see what is and is not covered by a check.

The redocking panel validates the docking protocol.  It says nothing about the force
field used in the all-atom simulations, and the MD section rests on a single target with
a 1 ns production run in which the ligand left the site.  Before proposing any further
simulation, it matters to establish what parameters were used, whether the ligand
parameters were derived in a standard way, and how many targets have any trajectory at
all - because a reviewer will ask whether the ligand's force-field description was
validated, and the honest answer has to be known in advance.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

print("=" * 96)
print("1. MD outputs present")
print("=" * 96)
for sub in ("md", "md_allatom", "output/md", "results/md", "data/md",
            "md_runs", "wsl_md"):
    d = ROOT / sub
    if d.exists():
        files = sorted(p for p in d.rglob("*") if p.is_file())
        print(f"  {sub}: {len(files)} files")
        by_ext: dict[str, int] = {}
        for p in files:
            by_ext[p.suffix] = by_ext.get(p.suffix, 0) + 1
        print(f"      by extension: {by_ext}")
        for p in files[:24]:
            print(f"      {p.relative_to(ROOT)}  ({p.stat().st_size/1024:.0f} KB)")

print()
print("=" * 96)
print("2. Any trajectory or parameter file anywhere in the project")
print("=" * 96)
pats = ["*.dcd", "*.nc", "*.xtc", "*.pdb", "*.mol2", "*.frcmod", "*.prmtop",
        "*.gro", "*.log"]
found: dict[str, list[Path]] = {}
for pat in pats:
    hits = [p for p in ROOT.rglob(pat)
            if "tools" not in str(p) and "site-packages" not in str(p)
            and ".git" not in str(p)]
    if hits:
        found[pat] = hits
        print(f"  {pat:10s} {len(hits):>5} files")
for pat, hits in found.items():
    print()
    print(f"  --- {pat} (first 12) ---")
    for p in sorted(hits)[:12]:
        print(f"      {p.relative_to(ROOT)}  ({p.stat().st_size/1024:.0f} KB)")

print()
print("=" * 96)
print("3. The MD stability summary")
print("=" * 96)
for name in ("md_allatom_stability.csv", "md_stability.csv", "md_summary.csv"):
    for d in (ROOT / "results", ROOT / "data" / "derived", ROOT):
        p = d / name
        if p.exists():
            print(f"  {p.relative_to(ROOT)}")
            df = pd.read_csv(p)
            with pd.option_context("display.width", 170,
                                   "display.max_columns", 40):
                print(df.to_string(index=False))
            print()

print("=" * 96)
print("4. Where the ligand parameters come from")
print("=" * 96)
for name in ("run_md_allatom.py", "analyse_md.py", "md_ligand.py",
             "prepare_ligand.py", "docking_run.py"):
    p = ROOT / "src" / name
    if not p.exists():
        continue
    txt = p.read_text(encoding="utf-8", errors="replace")
    hits = [ln.strip() for ln in txt.splitlines()
            if any(k in ln for k in ("gaff", "GAFF", "bcc", "BCC", "antechamber",
                                     "sqm", "parmchk", "forcefield", "force_field",
                                     "amber", "AMBER", "openmm", "OpenMM",
                                     "hydration", "addSolvent", "TIMESTEP",
                                     "REPORT_PS", "nanometer"))]
    if hits:
        print(f"  --- {name} ---")
        for h in hits[:14]:
            print(f"      {h[:112]}")

print()
print("=" * 96)
print("5. What the manuscript says about the MD")
print("=" * 96)
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(
    encoding="utf-8")
import re
for m in re.finditer(r"[^\n]*\b(GAFF|AM1-BCC|force field|force-field|1 ns|"
                     r"nanosecond|single target|one target)\b[^\n]*", EN):
    print(f"      {m.group(0).strip()[:150]}")
