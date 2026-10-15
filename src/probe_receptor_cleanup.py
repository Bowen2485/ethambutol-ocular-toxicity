# -*- coding: utf-8 -*-
"""
Work out what has to be stripped from each receptor, and whether HMOX1's heme can be
parameterised.

Two facts drive the design:
  * Modeller.addSolvent builds a system internally, so ANY residue the amber14 force
    field cannot template will abort the run.  That is what the JNI detergent in the
    TNF structure was doing, not the docked ligand.
  * Heme is to be kept for HMOX1, so it must be parameterised rather than removed.

This script separates the two categories - disposable additives versus cofactors - and
inspects the heme geometry to see what a parameterisation would have to handle.
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"

# residues that are unambiguously solvent, ions or crystallisation reagents
ADDITIVES = {
    "HOH", "WAT", "DOD", "TIP", "SOL",
    "NA", "CL", "K", "MG", "CA", "ZN", "MN", "FE", "CU", "NI", "CD", "HG", "CS",
    "SO4", "PO4", "NO3", "ACT", "ACY", "EDO", "GOL", "PEG", "PG4", "PGE", "MPD",
    "DMS", "DMF", "TRS", "EPE", "MES", "BOG", "LDA", "C8E", "DXC", "UNX", "UNK",
    "PEO", "EOH", "IPA", "MOH", "FMT", "CIT", "TLA", "MLI", "MLA", "BEZ", "IMD",
    "BME", "DTT", "TCE", "AZI", "BR", "IOD", "F", "SCN", "NH4", "CO3", "BO3",
}
# the five targets being run first, and the PDB each uses
TARGETS = {"TNF": "5MU8", "HMOX1": "1N45", "MFN2": "6JFM",
           "NFE2L2": "2FLU", "BCL2": "5JSN"}

print("=" * 92)
print("1. What each target receptor contains, split into additives and cofactors")
print("=" * 92)
for gene, pdbid in TARGETS.items():
    p = DOCK / "receptors" / pdbid / f"{pdbid}_clean.pdb"
    if not p.exists():
        p = DOCK / "receptors" / pdbid / f"{pdbid}.pdb"
    if not p.exists():
        print(f"\n{gene}: receptor file missing")
        continue
    counts = collections.Counter()
    for line in p.read_text(errors="replace").splitlines():
        if line.startswith(("ATOM", "HETATM")):
            counts[line[17:20].strip()] += 1
    additives = {r: n for r, n in counts.items() if r in ADDITIVES}
    cofactors = {r: n for r, n in counts.items()
                 if r not in ADDITIVES and r not in {
                     "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY",
                     "HIS", "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER",
                     "THR", "TRP", "TYR", "VAL"}}
    print(f"\n{gene}  ({pdbid}, {p.name})")
    print(f"  additives to strip : {additives if additives else 'none'}")
    print(f"  cofactors to keep  : {cofactors if cofactors else 'none'}")

print()
print("=" * 92)
print("2. HMOX1 heme: what would a parameterisation have to handle?")
print("=" * 92)
hem_p = DOCK / "receptors" / "1N45" / "1N45_clean.pdb"
if hem_p.exists():
    lines = [l for l in hem_p.read_text(errors="replace").splitlines()
             if l.startswith(("ATOM", "HETATM")) and l[17:20].strip() == "HEM"]
    print(f"  HEM atoms in the file: {len(lines)}")
    elems = collections.Counter()
    resnames = collections.Counter()
    for l in lines:
        el = l[76:78].strip() if len(l) >= 78 else l[12:16].strip()[:1]
        elems[el] += 1
        resnames[l[17:20].strip()] += 1
    print(f"  elements            : {dict(elems)}")
    print(f"  residue names       : {dict(resnames)}")
    # does an iron atom appear, and with what residue name?
    fe = [l for l in lines if (l[76:78].strip().upper() == "FE"
                               or l[12:16].strip().upper() == "FE")]
    print(f"  iron atoms found    : {len(fe)}")
    for l in fe[:3]:
        print(f"      {l[:80]}")
    # is there a covalent bond to the protein (proximal histidine)?
    his = [l for l in hem_p.read_text(errors="replace").splitlines()
           if l.startswith(("ATOM", "HETATM")) and l[17:20].strip() == "HIS"]
    print(f"  histidines nearby   : {len(his)} atoms "
          f"(a proximal ligand would need an explicit bond)")
    # CONECT records tell us the connectivity the depositor declared
    con = [l for l in hem_p.read_text(errors="replace").splitlines()
           if l.startswith("CONECT")]
    print(f"  CONECT records      : {len(con)}")
else:
    print("  HMOX1 receptor not found")

print()
print("=" * 92)
print("3. Can the heme be read as a molecule for parameterisation?")
print("=" * 92)
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem  # noqa: F401
    print(f"  rdkit available: {Chem.rdBase.rdkitVersion}")
    p = Path(__file__).resolve().parents[1] / "docking" / "ligands" / "ethambutol"
    print("  (heme would be extracted from the receptor into its own SDF first)")
    print("  key question: does the HEM record carry bond orders, or must they be")
    print("  perceived?  Without CONECT and with a metal centre, perception is")
    print("  unreliable, which is the usual reason heme parameterisation fails.")
except Exception as exc:  # noqa: BLE001
    print(f"  rdkit unavailable: {exc}")
