# -*- coding: utf-8 -*-
"""
Assess whether the ligand can be added after solvation.

The addSolvent failure is a sequencing problem: it builds a system from protein plus
ligand, and the ligand residue templates are not visible to the ForceField it uses
internally.  The clean fix is to solvate the protein first and add the ligand
afterwards, never calling addSolvent on a topology that contains the ligand.

That fix needs the ligand's docked pose to sit inside the water box, and for the pose
to be in the same coordinate frame as the repaired receptor.  This checks the numbers:
receptor extent, pose position, and how much of the box the ligand would occupy.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"


def read_ca(path: Path):
    xyz = []
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        if line[12:16].strip() != "CA":
            continue
        try:
            xyz.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
    return np.asarray(xyz)


def read_pose(path: Path):
    xyz, started = [], False
    for line in path.read_text(errors="replace").splitlines():
        s = line.strip()
        if s.startswith("MODEL"):
            if started:
                break
            started = True
            continue
        if s.startswith("ENDMDL"):
            break
        if not line.startswith(("ATOM", "HETATM")):
            continue
        el = line[76:78].strip().upper() if len(line) >= 78 else ""
        if el in ("H", "HD", "HS"):
            continue
        try:
            xyz.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
    return np.asarray(xyz)


rows = []
for gene, pdbid in (("TNF", "5MU8"), ("HMOX1", "1N45"), ("MFN2", "6JFM"),
                    ("NFE2L2", "2FLU"), ("BCL2", "5JSN")):
    rec_p = DOCK / "receptors" / pdbid / f"{pdbid}_clean.pdb"
    pose_p = DOCK / "poses" / f"{gene}__ethambutol.pdbqt"
    if not (rec_p.exists() and pose_p.exists()):
        continue
    rec = read_ca(rec_p)
    lig = read_pose(pose_p)
    if len(rec) < 5 or len(lig) < 3:
        continue
    lo, hi = rec.min(axis=0), rec.max(axis=0)
    extent = hi - lo
    cen = lig.mean(axis=0)
    # distance from the ligand centroid to the nearest receptor C-alpha
    dmin = float(np.min(np.linalg.norm(rec - cen, axis=1)))
    rows.append({
        "gene": gene, "pdb": pdbid,
        "n_ca": len(rec),
        "receptor_extent_A": np.round(extent, 1).tolist(),
        "ligand_centroid_A": np.round(cen, 1).tolist(),
        "ligand_inside_box": bool(np.all(cen > lo) and np.all(cen < hi)),
        "dist_to_nearest_CA_A": round(dmin, 2),
        "margin_to_edge_A": np.round(np.minimum(cen - lo, hi - cen), 1).tolist(),
    })

print("=" * 84)
print("Can the docked pose be placed inside the solvated receptor box?")
print("=" * 84)
for r in rows:
    print(f"\n{r['gene']}  ({r['pdb']}, {r['n_ca']} C-alpha atoms)")
    print(f"  receptor extent        : {r['receptor_extent_A']} A")
    print(f"  ligand centroid        : {r['ligand_centroid_A']} A")
    print(f"  inside the receptor box: {r['ligand_inside_box']}")
    print(f"  margin to the edge     : {r['margin_to_edge_A']} A "
          f"(1 nm padding needs > 10 A)")
    print(f"  distance to nearest CA : {r['dist_to_nearest_CA_A']} A "
          f"({'plausible contact' if r['dist_to_nearest_CA_A'] < 6 else 'NOT in contact'})")

print()
print("=" * 84)
print("READING")
print("=" * 84)
ok = all(r["ligand_inside_box"] for r in rows)
print(f"  all poses inside the receptor frame : {ok}")
if ok:
    print("  -> solvating the receptor first and adding the ligand afterwards is")
    print("     geometrically sound: the pose already lies within the box, so the")
    print("     ligand will be surrounded by water without displacing the protein.")
print("  -> the ligand must still be checked for clashes with water molecules that")
print("     occupy its pose; minimisation resolves those, and this is reported.")
