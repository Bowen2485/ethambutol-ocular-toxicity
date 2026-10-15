# -*- coding: utf-8 -*-
"""
Inventory the non-standard residues in every receptor file.

The receptor for TNF carries 1794 atoms of a residue named JNI, which is the actual
reason addSolvent cannot build a system - not the docked ligand.  A crystallographic
additive, detergent or lipid left in the file cannot be templated by the protein force
field, and PDBFixer will happily protonate it first.  Every receptor is examined so
the cleanup step can be written against the real contents.
"""
from __future__ import annotations

import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"

# the 20 standard residues plus common caps and ions that force fields handle
STANDARD = set("""ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER
THR TRP TYR VAL HID HIE HIP CYX ASH GLH LYN ACE NME NALA NARG NASN NASP NCYS
NGLN NGLU NGLY NHIS NILE NLEU NLYS NMET NPHE NPRO NSER NTHR NTRP NTYR NVAL
HOH WAT TIP SOL NA CL K MG ZN CA MN FE SO4 PO4""".split())

rows = []
for d in sorted(DOCK.glob("receptors/*")):
    if not d.is_dir():
        continue
    pdbid = d.name.replace("_AF", "")
    cand = None
    for name in (f"{pdbid}_clean.pdb", f"{pdbid}.pdb"):
        if (d / name).exists():
            cand = d / name
            break
    if cand is None:
        # alphafold models are named differently
        hits = list(d.glob("*.pdb"))
        cand = hits[0] if hits else None
    if cand is None:
        continue
    counts = collections.Counter()
    het = collections.Counter()
    for line in cand.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        res = line[17:20].strip()
        counts[res] += 1
        if line.startswith("HETATM"):
            het[res] += 1
    nonstd = {r: n for r, n in counts.items() if r not in STANDARD}
    total_nonstd = sum(nonstd.values())
    rows.append({
        "pdb": pdbid,
        "file": cand.name,
        "n_atoms": sum(counts.values()),
        "n_residue_types": len(counts),
        "nonstandard_types": len(nonstd),
        "nonstandard_atoms": total_nonstd,
        "nonstandard": dict(sorted(nonstd.items(), key=lambda kv: -kv[1])[:8]),
    })

print("=" * 96)
print("Non-standard residues present in each receptor file")
print("=" * 96)
for r in sorted(rows, key=lambda x: -x["nonstandard_atoms"]):
    flag = "  <-- must be stripped" if r["nonstandard_atoms"] > 50 else ""
    print(f"\n{r['pdb']:8s} {r['file']:22s} {r['n_atoms']:>7,} atoms, "
          f"{r['nonstandard_types']} non-standard type(s), "
          f"{r['nonstandard_atoms']:,} atoms{flag}")
    if r["nonstandard"]:
        print(f"    {r['nonstandard']}")

print()
print("=" * 96)
print("SUMMARY")
print("=" * 96)
bad = [r["pdb"] for r in rows if r["nonstandard_atoms"] > 50]
print(f"  receptors carrying substantial non-standard content: {len(bad)}")
print(f"    {bad}")
print()
print("  These residues are crystallisation additives, detergents or lipids.  They")
print("  cannot be templated by amber14 and they are not part of the biological")
print("  assembly, so each receptor must be reduced to protein before solvation.")
