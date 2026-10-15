# -*- coding: utf-8 -*-
"""
Inventory the cheminformatics tooling available on this side.

The all-atom simulations used GAFF-2.11 parameters with AM1-BCC charges, and no check
of those parameters exists anywhere in the project.  Before designing one, it matters
what is actually available here: RDKit can build the molecule, enumerate its rotamers
and assign GAFF atom types through its own implementation, but the semi-empirical
charges were computed by antechamber under Linux, and if that is only reachable through
WSL then any validation has to be structured around that constraint.

This also checks whether a crystallographic structure of ethambutol itself exists in the
project, since the strongest available test of a small-molecule force field is whether
it reproduces an experimental geometry.
"""
from __future__ import annotations

import importlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

print("=" * 92)
print("1. Python chemistry packages")
print("=" * 92)
for mod in ("rdkit", "openbabel", "openmm", "pdbfixer", "MDAnalysis", "mdtraj",
            "numpy", "scipy", "pandas", "Bio"):
    try:
        m = importlib.import_module(mod)
        v = getattr(m, "__version__", "")
        print(f"  {mod:14s} available   {v}")
    except ImportError:
        print(f"  {mod:14s} not installed")

print()
print("=" * 92)
print("2. Other tools")
print("=" * 92)
for exe in ("obabel", "antechamber", "parmchk2", "sqm", "tleap", "vina",
            "wsl", "python", "git"):
    p = shutil.which(exe)
    print(f"  {exe:14s} {p if p else 'not on PATH'}")

print()
print("=" * 92)
print("3. RDKit's own GAFF typing (used only if RDKit is present)")
print("=" * 92)
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.MolFromSmiles("CCN(CC)CC(CO)NC")  # placeholder, replaced below
    print(f"  MolFromSmiles works: {m is not None}")
except Exception as exc:  # noqa: BLE001
    print(f"  RDKit unusable: {type(exc).__name__}: {str(exc)[:80]}")

print()
print("=" * 92)
print("4. Ethambutol-related structures already in the project")
print("=" * 92)
hits = []
for pat in ("*.mol2", "*.sdf", "*.mol", "*.pdb", "*.pdbqt", "*.frcmod", "*.prmtop",
            "*.lib", "*.prepi", "*.in", "*.json"):
    for p in ROOT.rglob(pat):
        s = str(p)
        if "tools" in s or "site-packages" in s or ".git" in s:
            continue
        low = p.name.lower()
        if any(k in low for k in ("ethambutol", "emb", "ligand", "lig")):
            hits.append(p)
print(f"  files whose name mentions the ligand: {len(hits)}")
for p in sorted(hits)[:40]:
    print(f"      {p.relative_to(ROOT)}  ({p.stat().st_size/1024:.0f} KB)")

print()
print("=" * 92)
print("5. What the all-atom script actually does for parameters")
print("=" * 92)
src = ROOT / "src" / "run_md_allatom.py"
if src.exists():
    txt = src.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, ln in enumerate(txt, 1):
        s = ln.strip()
        if any(k in s for k in ("antechamber", "parmchk", "gaff", "GAFF", "bcc",
                                "sqm", "mol2", "frcmod", "amber14", "ForceField",
                                "charge", "net_charge", "resname", "LIG")):
            print(f"  {i:5d}: {s[:112]}")
