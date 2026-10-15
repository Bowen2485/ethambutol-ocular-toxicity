# -*- coding: utf-8 -*-
"""
Establish ethambutol's structure by measurement rather than recall.

Two attempts to write the SMILES from memory have produced reference molecules with the
wrong formula - the first had primary amines written as protonated secondary amines, the
second was one carbon short - and both were caught only by an assertion on the formula.
Rather than guess a third time, every candidate is built and its formula printed, so the
right structure is identified from the output.

Ethambutol is the only drug in the antitubercular set whose formula is C10H24N2O2, and
the ligand file being validated reports exactly that at 38 atoms, so the candidates are
scored against that.
"""
from __future__ import annotations

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

TARGET_FORMULA = "C10H24N2O2"

CANDIDATES = {
    "A  N,N'-linked, Et + CH2OH per side":
        "CC[C@@H](CO)NC[C@@H](CC)CO",
    "B  N,N'-linked, Me + EtOH per side":
        "C[C@@H](CCO)NC[C@@H](C)CCO",
    "C  each N bears ethyl and hydroxymethyl on separate carbons":
        "CCC(CO)NCC(CO)CC",
    "D  two-carbon diamine core, Et and CH2OH on each centre":
        "CCC(CO)NCC(CC)CO",
    "E  as D but explicit stereochemistry":
        "CC[C@H](CO)NC[C@H](CC)CO",
    "F  the literature form, N-(2-hydroxyethyl) variant":
        "CCC(CO)NCCNC(CC)CO",
}

print("=" * 92)
print(f"target: {TARGET_FORMULA} with 10 C, 2 N, 2 O, 38 atoms including hydrogens")
print("=" * 92)
rows = []
for label, smi in CANDIDATES.items():
    m = Chem.MolFromSmiles(smi)
    if m is None:
        print(f"  {label:58s}  INVALID SMILES")
        continue
    formula = rdMolDescriptors.CalcMolFormula(m)
    atoms = m.GetNumAtoms()
    heavy = m.GetNumHeavyAtoms()
    match = "  <== MATCHES" if formula == TARGET_FORMULA else ""
    print(f"  {label:58s}  {formula:14s} heavy {heavy:>2d}  all-H {atoms:>2d}{match}")
    rows.append((label, smi, formula, heavy, atoms))

print()
print("=" * 92)
print("The candidate that matches, with its descriptors")
print("=" * 92)
best = [r for r in rows if r[2] == TARGET_FORMULA]
if not best:
    print("  none of the candidates matches the target formula")
else:
    for label, smi, formula, heavy, atoms in best:
        m = Chem.MolFromSmiles(smi)
        mh = Chem.AddHs(m)
        print(f"  {label}")
        print(f"      SMILES              : {smi}")
        print(f"      formula             : {formula}")
        print(f"      heavy atoms         : {heavy}")
        print(f"      atoms with hydrogen : {mh.GetNumAtoms()}")
        print(f"      rotatable (strict)  : "
              f"{Descriptors.NumRotatableBonds(m, Descriptors.NumRotatableBondsOptions.Strict)}")
        print(f"      HBD / HBA           : {Descriptors.NumHDonors(m)} / "
              f"{Descriptors.NumHAcceptors(m)}")
        print(f"      TPSA                : {Descriptors.TPSA(m):.1f}")
        print(f"      cLogP               : {Descriptors.MolLogP(m):.2f}")
        # ethambutol has two stereocentres and is marketed as the (S,S) form
        print(f"      stereocentres       : "
              f"{len(Chem.FindMolChiralCenters(m, includeUnassigned=True))}")
        print()

print("=" * 92)
print("Cross-check against the ligand file that was actually simulated")
print("=" * 92)
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "results" / "ligand_parameter_validation.json"
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"  file reports: {d.get('formula')} / {d.get('total_atoms')} atoms / "
          f"charge {d.get('formal_charge')}")
print("  The ligand file itself is parsed independently by the validation script, "
      "so its composition is not taken from here.")
