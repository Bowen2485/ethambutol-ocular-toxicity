#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find out why the ligand residue is not being picked up.

Established facts:
  * complex.pdb contains 38 UNK atoms - that is the ethambutol molecule, confirmed by
    the atom count
  * the analysis reported no ligand, so the selection logic is at fault, not the file

The previous run printed only the first 14 residue names alphabetically, and UNK sorts
after TYR, so it was cut off and the output was misread.  This prints everything.

Run with:
    ~/miniconda3/envs/md/bin/python src/probe_ligand_detection.py
"""
from __future__ import annotations

import collections
from pathlib import Path

import mdtraj as md

ROOT = Path(__file__).resolve().parents[1]
PDB = ROOT / "md_allatom" / "NFE2L2" / "complex.pdb"

print("=" * 84)
print("1. What mdtraj sees in complex.pdb")
print("=" * 84)
top = md.load_topology(str(PDB))
print(f"  atoms    : {top.n_atoms:,}")
print(f"  residues : {top.n_residues:,}")
print(f"  chains   : {top.n_chains}")

print()
print("=" * 84)
print("2. Residue inventory with the attributes the selection uses")
print("=" * 84)
seen = {}
for res in top.residues:
    key = res.name.upper()
    if key not in seen:
        seen[key] = {"n_res": 0, "n_atoms": 0, "is_protein": res.is_protein}
    seen[key]["n_res"] += 1
    seen[key]["n_atoms"] += sum(1 for _ in res.atoms)
print(f"  {'name':8s} {'residues':>9} {'atoms':>8}  is_protein")
for name, info in sorted(seen.items(), key=lambda kv: -kv[1]["n_atoms"]):
    flag = "  <-- candidate ligand" if not info["is_protein"] else ""
    print(f"  {name:8s} {info['n_res']:>9} {info['n_atoms']:>8}  "
          f"{str(info['is_protein']):>10}{flag}")

print()
print("=" * 84)
print("3. The selection rule, applied step by step")
print("=" * 84)
SOLVENT = {"HOH", "WAT", "NA", "CL", "K", "MG", "ZN", "CA", "SO4", "PO4"}
lig, prot, bb = [], [], []
reason = collections.Counter()
for atom in top.atoms:
    rn = atom.residue.name.upper()
    if rn in SOLVENT:
        reason["solvent, skipped"] += 1
        continue
    if atom.residue.is_protein:
        prot.append(atom.index)
        reason["protein"] += 1
        if atom.name in ("CA", "C", "N", "O"):
            bb.append(atom.index)
    else:
        lig.append(atom.index)
        reason["ligand"] += 1
print(f"  {dict(reason)}")
print(f"  ligand atoms selected: {len(lig)}")
print(f"  protein atoms        : {len(prot)}")
print(f"  backbone atoms       : {len(bb)}")

print()
print("=" * 84)
print("4. Does the UNK residue survive a direct lookup?")
print("=" * 84)
unk_res = [r for r in top.residues if r.name.upper() == "UNK"]
print(f"  residues named UNK   : {len(unk_res)}")
for r in unk_res[:3]:
    print(f"    index={r.index} name={r.name!r} is_protein={r.is_protein} "
          f"chain={r.chain.index}")
    print(f"      atoms: {[a.name for a in r.atoms][:12]}")
    print(f"      elements: "
          f"{[str(a.element.symbol) if a.element else None for a in r.atoms][:12]}")
try:
    sel = top.select("resname UNK")
    print(f"  top.select('resname UNK') -> {len(sel)} atoms")
except Exception as exc:  # noqa: BLE001
    print(f"  top.select('resname UNK') failed: {type(exc).__name__}: {exc}")
try:
    sel2 = top.select("not protein and not water and not resname NA CL")
    print(f"  top.select('not protein and not water ...') -> {len(sel2)} atoms")
except Exception as exc:  # noqa: BLE001
    print(f"  that selection failed: {type(exc).__name__}: {exc}")

print()
print("=" * 84)
print("VERDICT")
print("=" * 84)
if len(lig) == 38:
    print("  The selection works here, so the failure in analyse_md.py must come from")
    print("  something else - most likely a different topology being loaded (the DCD")
    print("  header rather than complex.pdb), or an exception before the selection.")
elif len(lig) == 0:
    print("  The selection genuinely finds nothing.  The rule 'not protein and not")
    print("  solvent' is being defeated - see which bucket the UNK atoms fall into")
    print("  above and adjust the rule accordingly.")
else:
    print(f"  The selection found {len(lig)} atoms, which is neither 0 nor the expected")
    print("  38.  Check whether extra residues are being counted as ligand.")
