# -*- coding: utf-8 -*-
"""
Decide which redocking results are trustworthy before re-running anything.

The first expanded run validated nine systems in one pass.  CA2 appeared three times -
3HS4, 3M04 and 1AZM - and the validation directory was keyed by target name alone, so
each CA2 run overwrote the previous one's box file and ligand file in place.  Any CA2
result whose box does not enclose its own ligand is therefore a bookkeeping artefact,
not a docking outcome.

The clean evidence available: the box-to-ligand offset for each directory.  Where it is
zero the box was computed from that directory's own ligand and the RMSD is meaningful;
where it is tens of angstroms the ligand lay outside the search space and the RMSD says
nothing about the protocol.

This separates the two, so the re-run set contains only what genuinely needs repeating.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "docking" / "validation"
AGG = VAL / "redocking_validation.csv"


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
    return (np.asarray([vals["center_x"], vals["center_y"], vals["center_z"]])
            if len(vals) == 3 else None)


print("=" * 90)
print("Per-system evidence")
print("=" * 90)
print(f"  {'dir':14s} {'ligand':14s} {'heavy':>6s} {'box offset':>11s} "
      f"{'RMSD':>8s}  verdict")
print("  " + "-" * 86)

trustworthy, suspect, failed = [], [], []
for d in sorted(VAL.iterdir()):
    if not d.is_dir():
        continue
    j = d / "validation.json"
    box_p, lig_p = d / "redock.box.txt", d / "crystal_ligand.pdb"
    rec = json.loads(j.read_text(encoding="utf-8")) if j.exists() else {}
    lig = rec.get("ligand") or "-"
    heavy = rec.get("ligand_heavy_atoms")
    rms = rec.get("top_pose_rmsd_A")
    if not (box_p.exists() and lig_p.exists()):
        print(f"  {d.name:14s} {str(lig):14s} {str(heavy):>6s} {'-':>11s} "
              f"{'-':>8s}  no box or ligand file")
        failed.append(d.name)
        continue
    bc, lc = box_centre(box_p), centroid(lig_p)
    off = float(np.linalg.norm(bc - lc)) if (bc is not None and lc is not None) else -1
    if off < 0:
        verdict = "unparsed"
        failed.append(d.name)
    elif off > 12.0:
        verdict = "BOX MISSED THE LIGAND - artefact"
        suspect.append((d.name, lig, heavy))
    elif rms is None or heavy is None:
        # the box is fine but no result was recorded, which is how a failed ligand
        # preparation shows up: AMPC's boron-containing ligand cannot be typed by
        # obabel, so nothing was docked
        verdict = "box correct but no result recorded"
        failed.append(d.name)
    else:
        verdict = "box correct - RMSD meaningful"
        trustworthy.append((d.name, lig, heavy, rms, rec.get("passed")))
    print(f"  {d.name:14s} {str(lig):14s} {str(heavy):>6s} {off:>11.1f} "
          f"{(f'{rms:.3f}' if isinstance(rms, (int, float)) else '-'):>8s}  {verdict}")

print()
print("=" * 90)
print("Results that stand, box confirmed correct")
print("=" * 90)
print(f"  {'system':16s} {'ligand':14s} {'heavy':>6s} {'RMSD(A)':>9s}  pass")
for name, lig, heavy, rms, passed in sorted(trustworthy, key=lambda x: x[2] or 0):
    print(f"  {name:16s} {lig:14s} {heavy:>6} {rms:>9.3f}  {passed}")

print()
print("=" * 90)
print("Needs repeating, box did not contain the ligand")
print("=" * 90)
for name, lig, heavy in suspect:
    print(f"  {name:16s} {lig:14s} {heavy} heavy atoms")

print()
print("=" * 90)
print("Re-run set")
print("=" * 90)
print("""  Systems to repeat with the corrected per-structure directories:
      CA2:3M04:BE7    the 10-heavy-atom component, matched to ethambutol
      CA2:3M04:BE9    the 19-heavy-atom component
      CA2:1AZM:AZM    the second CA2 structure
      BACE1:2OH4:PTR  timed out on the structure download
  Systems already sound and not repeated:
      CA2:3HS4  TRYPSIN:3PTB  DHFR:1RG7  PNP:1B8O  HSP90:1UYG
  Dropped, with the reason recorded:
      AMPC:1FSY       the ligand contains boron; obabel emits an atom type that Vina
                      rejects ("Atom type B is not a valid AutoDock type"), so no
                      docking is possible for it with this toolchain""")
