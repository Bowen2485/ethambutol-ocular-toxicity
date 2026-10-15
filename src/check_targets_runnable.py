# -*- coding: utf-8 -*-
"""Check which targets can actually run, and estimate their wall-clock cost."""
from __future__ import annotations

import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "receptors_clean"

STD = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
       "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"}
SOLVENT = {"HOH", "NA", "CL", "K", "MG", "ZN", "CA", "SO4", "PO4", "ACT", "EDO"}

TARGETS = [("TNF", "5MU8"), ("HMOX1", "1N45"), ("BCL2", "5JSN"),
           ("NFE2L2", "2FLU"), ("MFN2", "6JFM")]

print("=" * 78)
print("1. Can each target run as prepared?")
print("=" * 78)
results = {}
for gene, pdbid in TARGETS:
    p = CLEAN / pdbid / f"{pdbid}_protein.pdb"
    if not p.exists():
        print(f"  {gene:8s} cleaned receptor missing")
        continue
    counts = collections.Counter()
    for line in p.read_text(errors="replace").splitlines():
        if line.startswith(("ATOM", "HETATM")):
            counts[line[17:20].strip()] += 1
    nonstd = {r: n for r, n in counts.items() if r not in STD and r not in SOLVENT}
    total = sum(counts.values())
    status = "runnable" if not nonstd else f"BLOCKED by {nonstd}"
    results[gene] = total
    print(f"  {gene:8s} {pdbid:6s} {total:>8,} atoms in the file   {status}")

print()
print("=" * 78)
print("2. Estimated wall clock at the measured rate")
print("=" * 78)
# measured: 234 ns/day on a 45,545-atom solvated system (NFE2L2)
BASE_ATOMS = 45545
BASE_RATE = 234.0          # ns/day
NS_TOTAL = 1.5             # 0.5 ns equilibration + 1 ns production

print(f"  measured throughput: {BASE_RATE:.0f} ns/day on {BASE_ATOMS:,} atoms")
print(f"  time scales roughly with atom count")
print()
print(f"  {'target':10s} {'atoms(file)':>12s} {'est. solvated':>14s} {'1.5 ns':>10s}")
for gene, atoms in results.items():
    # solvation multiplies the atom count; NFE2L2 went from 4,533 to 45,545, a factor
    # of about 10, which is applied here as a rough guide
    est = atoms * 10
    hours = NS_TOTAL / (BASE_RATE * BASE_ATOMS / est / 24)
    print(f"  {gene:10s} {atoms:>12,} {est:>14,} {hours*60:>8.0f} min")

print()
print("=" * 78)
print("3. HMOX1 and its heme")
print("=" * 78)
hem = CLEAN / "1N45" / "HEM.pdb"
print(f"  HEM extracted separately : {hem.exists()}")
print(f"  present in the protein file: "
      f"{'yes' if 'HEM' in (CLEAN / '1N45' / '1N45_protein.pdb').read_text(errors='replace') else 'no'}")
print()
print("  The protein file is protein-only, so HMOX1 will RUN, but without its heme.")
print("  That changes the active site: HMOX1 is a heme oxygenase and the heme is its")
print("  substrate and catalytic centre.  A simulation without it describes the apoprotein.")
print("  Either run it and describe it as the apoprotein, or parameterise the heme first.")
