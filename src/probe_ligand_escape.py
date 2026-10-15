#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Trace where the ligand actually went, and whether the protein moved with it.

What is already established from md.log:
    temperature 299-302 K, density 1.035-1.038 g/mL, potential energy flat, 231-237
    ns/day.  The system is therefore healthy: no box collapse, no overheating, no
    energy blow-up.  The earlier guess that the box had collapsed is wrong.

What remains ambiguous:
    the ligand RMSD stays near 1.8 A while the receptor backbone RMSD jumps from 2 A to
    13 A at 0.60 ns, and contact survival reaches zero at the same moment.  Two very
    different explanations fit that pattern and require different wording in the paper:
      * the ligand diffused into the bulk solvent, so the docked pose was a surface
        artefact and never a binding site
      * the protein rearranged and pushed the ligand out, so the pose was real but not
        maintained
    The ligand's distance to the protein separates them: a ligand in bulk solvent is
    many angstroms from any protein atom; one displaced by a conformational change
    stays in contact.

Outputs
    results/md_ligand_escape.csv   per-frame minimum distance and centroid offset
    a printed trace at coarse intervals
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

try:
    import mdtraj as md
except ImportError:
    sys.exit("mdtraj not installed")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "md_allatom"
REPORT_PS = 10.0
EQUIL_PS = 500.0
# minimum protein-ligand atom distance beyond which the ligand counts as detached
DETACHED_NM = 0.8          # 8 A: no van der Waals contact at all


def main() -> int:
    # reuse the grouping, contact and trajectory helpers already validated in analyse_md
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from analyse_md import find_groups, newest_traj, trajectory_matches_topology

    genes = sys.argv[1:] or sorted(p.name for p in OUT.iterdir()
                                   if p.is_dir() and newest_traj(p) is not None)
    if not genes:
        sys.exit("no trajectories found")

    all_rows = []
    for gene in genes:
        d = OUT / gene
        traj_p = newest_traj(d)
        top_p = d / "complex.pdb"
        if traj_p is None or not top_p.exists():
            print(f"  {gene}: no trajectory")
            continue
        # The same guard analyse_md uses.  It was added there first and forgotten here,
        # so this script still raised "xyz must be shape (Any, 79191, 3). You supplied
        # (1, 78930, 3)" on the leftover HMOX1 trajectory while analyse_md skipped it
        # cleanly.  A guard in one of two readers is not a guard.
        if not trajectory_matches_topology(traj_p, top_p, gene):
            continue
        top = md.load_topology(str(top_p))
        lig, prot, bb = find_groups(top, gene)
        if not len(lig) or not len(prot):
            print(f"  {gene}: ligand or protein not identified")
            continue
        align = bb if len(bb) else prot

        ref = None
        for block in md.iterload(str(traj_p), top=str(top_p), chunk=1):
            ref = block[0]
            break
        if ref is None:
            continue
        ref.superpose(ref, 0, atom_indices=align)

        # every ligand-protein pair, used to find the closest approach per frame
        pairs = np.array([(l, p) for l in lig for p in prot], dtype=np.int64)

        skip = int(EQUIL_PS / REPORT_PS)
        total = 0
        for block in md.iterload(str(traj_p), top=str(top_p), chunk=200):
            total += block.n_frames
        total = max(total - skip, 0)
        if total == 0:
            print(f"  {gene}: no production frames")
            continue

        rows, seen = [], 0
        for block in md.iterload(str(traj_p), top=str(top_p), chunk=50, skip=skip):
            nb = block.n_frames
            block.superpose(ref, 0, atom_indices=align)
            dist = np.asarray(md.compute_distances(block, pairs), dtype=float)
            if dist.ndim == 1:
                dist = dist.reshape(nb, -1)
            dmin = dist.min(axis=1) * 10.0                    # nm -> A
            # offset of the ligand centroid from its starting position, measured in the
            # same aligned frame so the comparison is meaningful
            lig_c = block.xyz[:, lig, :].mean(axis=1)
            ref_c = ref.xyz[0, lig, :].mean(axis=0)
            offset = np.linalg.norm(lig_c - ref_c, axis=1) * 10.0
            for j in range(nb):
                rows.append([gene, seen + j, round((seen + j) * REPORT_PS / 1000.0, 3),
                             round(float(dmin[j]), 2), round(float(offset[j]), 2)])
            seen += nb

        all_rows.extend(rows)
        print(f"\n  {gene}: ligand-protein closest approach over time")
        print(f"    {'time(ns)':>9} {'min dist(A)':>12} {'offset(A)':>10}  state")
        step = max(len(rows) // 12, 1)
        for r in rows[::step] + [rows[-1]]:
            state = ("detached" if r[3] > DETACHED_NM * 10 else
                     "in contact" if r[3] < 5.0 else "nearby")
            print(f"    {r[2]:>9.2f} {r[3]:>12.2f} {r[4]:>10.2f}  {state}")
        det = [r for r in rows if r[3] > DETACHED_NM * 10]
        first = det[0] if det else None
        print(f"  {gene}: detached in {len(det)}/{len(rows)} frames"
              + (f"; first detached at {first[2]:.2f} ns "
                 f"(closest approach {first[3]:.2f} A)" if first else
                 "; never fully detached"))

    if all_rows:
        p = ROOT / "results" / "md_ligand_escape.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["target", "frame", "time_ns", "min_dist_A", "centroid_offset_A"])
            w.writerows(all_rows)
        print(f"\n-> {p}")

    print("\n" + "=" * 76)
    print("HOW TO READ THIS")
    print("=" * 76)
    print("  minimum distance above ~8 A means no contact with any protein atom, so the")
    print("  ligand is in bulk solvent and the docked pose was a surface artefact.")
    print("  a minimum distance that stays small while contacts are lost means the")
    print("  protein rearranged underneath a ligand that never left its vicinity.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
