# -*- coding: utf-8 -*-
"""
Establish the column layout of the crystal-ligand PDB files before parsing them.

RDKit rejects these files, and the reason is not obvious from looking at them: the
records read plausibly but the fields are shifted from the standard PDB columns.  The
fix depends on knowing where each field actually sits, so the ruler is printed rather
than the layout guessed - which has already cost several attempts in this project.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
f = ROOT / "docking" / "validation" / "AMPC" / "crystal_ligand.pdb"
lines = f.read_text(errors="replace").splitlines()
first = lines[0]

print("=" * 92)
print("The first HETATM record, with column numbers")
print("=" * 92)
print(f"  {first!r}")
print(f"  length {len(first)}")
print()
print("  ruler (0-based):")
for start in range(0, len(first), 10):
    seg = first[start:start + 10]
    print(f"    {start:>3d} {seg!r}")

print()
print("=" * 92)
print("Field slices under the standard PDB convention")
print("=" * 92)
FIELDS = {
    "record  (0:6)": (0, 6),
    "serial  (6:11)": (6, 11),
    "name   (12:16)": (12, 16),
    "altLoc  (16)": (16, 17),
    "resName (17:20)": (17, 20),
    "chain   (21)": (21, 22),
    "resSeq (22:26)": (22, 26),
    "icode   (26)": (26, 27),
    "x      (30:38)": (30, 38),
    "y      (38:46)": (38, 46),
    "z      (46:54)": (46, 54),
    "occup  (54:60)": (54, 60),
    "temp   (60:66)": (60, 66),
    "element(76:78)": (76, 78),
}
for label, (a, b) in FIELDS.items():
    print(f"  {label:18s} -> {first[a:b]!r}")

print()
print("=" * 92)
print("What the fields contain for every atom in the file")
print("=" * 92)
print(f"  {'serial':>7s} {'name':>6s} {'resName':>8s} {'chain':>6s} "
      f"{'resSeq':>7s} {'x':>9s} {'element':>8s}")
for ln in lines:
    if not ln.startswith(("ATOM", "HETATM")):
        continue
    print(f"  {ln[6:11].strip():>7s} {ln[12:16].strip():>6s} "
          f"{ln[17:20].strip():>8s} {ln[21:22].strip():>6s} "
          f"{ln[22:26].strip():>7s} {ln[30:38].strip():>9s} "
          f"{ln[76:78].strip():>8s}")

print()
print("=" * 92)
print("How many such files are there, and do they share the layout?")
print("=" * 92)
val = ROOT / "docking" / "validation"
rows = []
for d in sorted(p for p in val.iterdir() if p.is_dir()):
    cl = d / "crystal_ligand.pdb"
    if not cl.exists():
        continue
    ls = [x for x in cl.read_text(errors="replace").splitlines()
          if x.startswith(("ATOM", "HETATM"))]
    lens = {len(x) for x in ls}
    elems = {x[76:78].strip() for x in ls if len(x) >= 78}
    rows.append((d.name, len(ls), sorted(lens), sorted(e for e in elems if e)))
print(f"  {'complex':14s} {'atoms':>6s} {'line lengths':>18s}  elements")
for name, n, lens, elems in rows:
    print(f"  {name:14s} {n:>6d} {str(lens):>18s}  {elems}")
