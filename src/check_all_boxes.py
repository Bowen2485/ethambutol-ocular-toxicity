# -*- coding: utf-8 -*-
"""
Check every validation directory for a box that does not contain its own ligand.

An earlier CA2 result reported 54 A because two CA2 structures had shared one directory
and the second run's ligand file was paired with the first run's box.  That fault is
fixed, but the same symptom has appeared again for CA2:3M04 with the 10-atom BE7
component, which returned 18.1 A.  Before that number is treated as a docking failure it
has to be established that the box actually enclosed the ligand, because the two causes
are indistinguishable from the RMSD alone.

The check is direct: measure the distance from the box centre to the centroid of the
crystal ligand that was docked, and compare it with half the box width.  Anything beyond
that and the ligand lay outside the search space, so the top-ranked pose could not have
been the crystal pose whatever the protocol.

Usage
    python src/check_all_boxes.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "docking" / "validation"
BOX_WIDTH = 24.0
HALF = BOX_WIDTH / 2.0


def centroid(p: Path) -> np.ndarray | None:
    xs = []
    for ln in p.read_text(errors="replace").splitlines():
        if ln.startswith(("ATOM", "HETATM")):
            try:
                xs.append([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])
            except ValueError:
                continue
    return np.asarray(xs).mean(axis=0) if xs else None


def box(p: Path) -> tuple[np.ndarray | None, float]:
    vals = {}
    for ln in p.read_text(errors="replace").splitlines():
        for k in ("center_x", "center_y", "center_z", "size_x"):
            if ln.strip().startswith(k):
                try:
                    vals[k] = float(ln.split("=")[1])
                except (IndexError, ValueError):
                    pass
    c = (np.asarray([vals["center_x"], vals["center_y"], vals["center_z"]])
         if {"center_x", "center_y", "center_z"} <= vals.keys() else None)
    return c, vals.get("size_x", BOX_WIDTH)


rows = []
for d in sorted(VAL.iterdir()):
    if not d.is_dir():
        continue
    bp, lp, jp = d / "redock.box.txt", d / "crystal_ligand.pdb", d / "validation.json"
    rec = json.loads(jp.read_text(encoding="utf-8")) if jp.exists() else {}
    if not (bp.exists() and lp.exists()):
        rows.append((d.name, rec.get("ligand"), rec.get("ligand_heavy_atoms"),
                     None, rec.get("top_pose_rmsd_A"), "no box/ligand file"))
        continue
    c, size = box(bp)
    lc = centroid(lp)
    if c is None or lc is None:
        rows.append((d.name, rec.get("ligand"), rec.get("ligand_heavy_atoms"),
                     None, rec.get("top_pose_rmsd_A"), "unparsed"))
        continue
    off = float(np.linalg.norm(c - lc))
    # the ligand must fit inside the box, so its centroid must be within half a width
    # of the centre; allow a small margin for the ligand's own radius
    status = ("OK" if off <= size / 2.0
              else "BOX MISSED THE LIGAND - RMSD meaningless")
    rows.append((d.name, rec.get("ligand"), rec.get("ligand_heavy_atoms"), off,
                 rec.get("top_pose_rmsd_A"), status))

print("=" * 100)
print("Box containment, all validation directories")
print("=" * 100)
print(f"  {'dir':16s} {'ligand':14s} {'heavy':>6s} {'offset':>8s} {'half-box':>9s} "
      f"{'RMSD':>8s}  status")
print("  " + "-" * 96)
for name, lig, heavy, off, rms, status in rows:
    off_s = f"{off:.1f}" if off is not None else "-"
    heavy_s = str(heavy) if heavy is not None else "-"
    rms_s = f"{rms:.3f}" if isinstance(rms, (int, float)) else "-"
    print(f"  {name:16s} {str(lig):14s} {heavy_s:>6s} {off_s:>8s} {HALF:>9.1f} "
          f"{rms_s:>8s}  {status}")

print()
print("=" * 100)
print("Summary")
print("=" * 100)
good = [r for r in rows if r[5] == "OK" and isinstance(r[4], (int, float))]
bad_box = [r for r in rows if "MISSED" in r[5]]
print(f"  boxes that contain their ligand        : {len(good)}")
for name, lig, heavy, off, rms, _ in sorted(good, key=lambda r: r[2] or 0):
    verdict = "pass" if rms <= 2.0 else "fail"
    print(f"      {name:16s} {str(lig):14s} {heavy:>3} heavy  RMSD {rms:>7.3f}  "
          f"{verdict}")
print(f"  boxes that do not                      : {len(bad_box)}")
for name, lig, heavy, off, rms, _ in bad_box:
    print(f"      {name:16s} {str(lig):14s} {heavy:>3} heavy  offset {off:.1f} A")
