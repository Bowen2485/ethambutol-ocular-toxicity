# -*- coding: utf-8 -*-
"""
Test whether the 54 A CA2 result came from the directory collision, or from the method.

Two CA2 structures were validated in one run - 3HS4 and 1AZM - and the validation
directory was keyed by target name alone, so the second run overwrote the first run's
files in place.  The residual evidence is exactly what that predicts:

    redock.box.txt       centre [-5.41, 3.08, 15.03]   <- computed from 3HS4's ligand
    crystal_ligand.pdb   centroid [34.27, 16.43, -18.71] <- 1AZM's ligand

The box therefore sat about 54 A from the ligand it was supposed to enclose, which is
the same number as the reported RMSD.  That is a strong indication of a bookkeeping
fault rather than a docking failure, but it is worth confirming directly rather than
inferring it from a coincidence of magnitudes.

This checks the distance between the box centre and the ligand centroid for each
validation directory that still has both files, and compares it with the reported RMSD.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "docking" / "validation"


def centroid(p: Path) -> np.ndarray | None:
    xs = []
    for ln in p.read_text(errors="replace").splitlines():
        if ln.startswith(("ATOM", "HETATM")):
            try:
                xs.append([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])
            except ValueError:
                continue
    return np.asarray(xs).mean(axis=0) if xs else None


def box_centre(p: Path) -> np.ndarray | None:
    vals = {}
    for ln in p.read_text(errors="replace").splitlines():
        for k in ("center_x", "center_y", "center_z"):
            if ln.strip().startswith(k):
                try:
                    vals[k] = float(ln.split("=")[1])
                except (IndexError, ValueError):
                    pass
    if len(vals) == 3:
        return np.asarray([vals["center_x"], vals["center_y"], vals["center_z"]])
    return None


print("=" * 88)
print("Does the docking box actually enclose the crystal ligand?")
print("=" * 88)
print(f"  {'dir':16s} {'box centre':>22s} {'ligand centroid':>24s} "
      f"{'offset(A)':>10s} {'RMSD(A)':>9s}")
print("  " + "-" * 84)

for d in sorted(VAL.iterdir()):
    if not d.is_dir():
        continue
    box_p = d / "redock.box.txt"
    lig_p = d / "crystal_ligand.pdb"
    js_p = d / "validation.json"
    if not (box_p.exists() and lig_p.exists()):
        print(f"  {d.name:16s} incomplete")
        continue
    bc = box_centre(box_p)
    lc = centroid(lig_p)
    if bc is None or lc is None:
        print(f"  {d.name:16s} could not parse")
        continue
    off = float(np.linalg.norm(bc - lc))
    rms = None
    if js_p.exists():
        rms = json.loads(js_p.read_text(encoding="utf-8")).get("top_pose_rmsd_A")
    flag = ""
    if off > 12.0:
        flag = "  <-- box does not contain the ligand"
    print(f"  {d.name:16s} {np.round(bc, 1)!s:>22s} {np.round(lc, 1)!s:>24s} "
          f"{off:>10.1f} {(f'{rms:.3f}' if rms is not None else '-'):>9s}{flag}")

print()
print("=" * 88)
print("Reading")
print("=" * 88)
print("""  A box offset of more than about half the box width (12 A of a 24 A box) means the
  ligand sits outside the search space, so the top-ranked pose cannot be the crystal
  pose and the RMSD is meaningless.  Where the offset is small, the box is correct and
  an RMSD above 2 A is a genuine docking failure.  That distinction is the whole point
  of this check: it separates a bookkeeping error from a methodological limit.""")
