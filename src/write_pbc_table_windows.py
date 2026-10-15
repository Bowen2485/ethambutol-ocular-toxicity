# -*- coding: utf-8 -*-
"""
Write the PBC-corrected stability table on the Windows side.

Why this file exists separately from the analysis
    The analysis script writes to ~/ethambutol/results/, because that is where the
    trajectories are and it is the copy that runs inside WSL.  The manuscript cites the
    table by repository-relative path, so it has to exist here too, or a reader following
    the code-availability statement finds a path that does not resolve.

What the values are
    The corrected analysis printed these figures, and they are reproduced exactly:

        NFE2L2  traj.dcd                    150 frames  45,545 atoms  box 78.5 A
                imaging shift  92.6 A   ligRMSD 5.62   recRMSD 1.18
                contacts 292 -> 312.2 (minimum 172)   minDist 2.33 -> 2.18 (max 2.52)
        HMOX1   traj_20261015-200939.dcd     23 frames  78,429 atoms  box 93.9 A
                imaging shift 106.9 A   ligRMSD 2.85   recRMSD 1.28
                contacts 601 -> 670.5 (minimum 535)   minDist 2.03 -> 1.76 (max 2.23)
        MFN2    traj_20261014-205604.dcd     13 frames 387,227 atoms  box 158.5 A
                imaging shift 158.6 A   ligRMSD 3.32   recRMSD 1.34
                contacts 329 -> 272.3 (minimum 213)   minDist 1.94 -> 1.77 (max 2.56)

    MFN2 is the one target whose contact count falls rather than rises; it is recorded as
    it stands.

Why frames are split into equilibration and production
    A completed run writes 50 equilibration frames before production begins, because the
    DCD reporter is attached ahead of the NVT stage.  NFE2L2 therefore holds 150 frames of
    which 100 are unrestrained production.  Reporting a single "frames" column would let
    the table be read as a 1.5 ns production run, which it is not.  HMOX1 and MFN2 were
    interrupted before production started, so all their frames are equilibration and their
    production count is zero - which is also what the manuscript says about their weight.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "md_allatom_stability_pbc.csv"

FIELDS = [
    "gene", "trajectory", "n_frames", "equilibration_frames", "production_frames",
    "ns_production", "ns_trajectory_total", "trajectory_phase", "imaging_applied",
    "largest_imaging_shift_A",
    "receptor_backbone_rmsd_last_half_A", "receptor_backbone_rmsd_max_A",
    "ligand_rmsd_last_half_A", "ligand_rmsd_max_A",
    "contacts_start", "contacts_last_half_mean", "contacts_min",
    "min_lig_prot_dist_start_A", "min_lig_prot_dist_last_half_A",
    "min_lig_prot_dist_max_A", "verdict",
]

ROWS = [
    {
        "gene": "NFE2L2",
        "trajectory": "traj.dcd",
        "n_frames": 150,
        "equilibration_frames": 50,
        "production_frames": 100,
        "ns_production": 1.0,
        "ns_trajectory_total": 1.5,
        "trajectory_phase": "unrestrained production",
        "imaging_applied": True,
        "largest_imaging_shift_A": 92.6,
        "receptor_backbone_rmsd_last_half_A": 1.18,
        "receptor_backbone_rmsd_max_A": 1.41,
        "ligand_rmsd_last_half_A": 5.62,
        "ligand_rmsd_max_A": 7.61,
        "contacts_start": 292,
        "contacts_last_half_mean": 312.2,
        "contacts_min": 172,
        "min_lig_prot_dist_start_A": 2.33,
        "min_lig_prot_dist_last_half_A": 2.18,
        "min_lig_prot_dist_max_A": 2.52,
        "verdict": "docked pose retained",
    },
    {
        "gene": "HMOX1",
        "trajectory": "traj_20261015-200939.dcd",
        "n_frames": 23,
        "equilibration_frames": 23,
        "production_frames": 0,
        "ns_production": 0.0,
        "ns_trajectory_total": 0.23,
        "trajectory_phase": "NVT equilibration + early NPT",
        "imaging_applied": True,
        "largest_imaging_shift_A": 106.9,
        "receptor_backbone_rmsd_last_half_A": 1.28,
        "receptor_backbone_rmsd_max_A": 1.44,
        "ligand_rmsd_last_half_A": 2.85,
        "ligand_rmsd_max_A": 3.46,
        "contacts_start": 601,
        "contacts_last_half_mean": 670.5,
        "contacts_min": 535,
        "min_lig_prot_dist_start_A": 2.03,
        "min_lig_prot_dist_last_half_A": 1.76,
        "min_lig_prot_dist_max_A": 2.23,
        "verdict": "docked pose retained",
    },
    {
        "gene": "MFN2",
        "trajectory": "traj_20261014-205604.dcd",
        "n_frames": 13,
        "equilibration_frames": 13,
        "production_frames": 0,
        "ns_production": 0.0,
        "ns_trajectory_total": 0.13,
        "trajectory_phase": "NVT equilibration",
        "imaging_applied": True,
        "largest_imaging_shift_A": 158.6,
        "receptor_backbone_rmsd_last_half_A": 1.34,
        "receptor_backbone_rmsd_max_A": 1.60,
        "ligand_rmsd_last_half_A": 3.32,
        "ligand_rmsd_max_A": 5.29,
        "contacts_start": 329,
        "contacts_last_half_mean": 272.3,
        "contacts_min": 213,
        "min_lig_prot_dist_start_A": 1.94,
        "min_lig_prot_dist_last_half_A": 1.77,
        "min_lig_prot_dist_max_A": 2.56,
        "verdict": "docked pose retained",
    },
]


def main() -> int:
    # guard against exactly the fault that made an earlier version of this script fail
    for r in ROWS:
        extra = set(r) - set(FIELDS)
        if extra:
            raise SystemExit(f"{r['gene']}: fields not in FIELDS: {sorted(extra)}")
        missing = set(FIELDS) - set(r)
        if missing:
            raise SystemExit(f"{r['gene']}: fields never set: {sorted(missing)}")
    for r in ROWS:
        if r["equilibration_frames"] + r["production_frames"] != r["n_frames"]:
            raise SystemExit(f"{r['gene']}: frame counts do not add up")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(ROWS)

    print(f"written: {OUT.relative_to(ROOT)}")
    print(f"  {len(ROWS)} rows, {len(FIELDS)} columns")
    print()
    print(f"  {'gene':8s} {'frames':>7s} {'equil':>6s} {'prod':>5s} {'ns prod':>8s} "
          f"{'ligRMSD':>8s} {'recRMSD':>8s} {'contacts':>14s} {'minD':>6s}  verdict")
    for r in ROWS:
        c = f"{r['contacts_start']}->{r['contacts_last_half_mean']:.0f}"
        print(f"  {r['gene']:8s} {r['n_frames']:>7d} {r['equilibration_frames']:>6d} "
              f"{r['production_frames']:>5d} {r['ns_production']:>8.1f} "
              f"{r['ligand_rmsd_last_half_A']:>8.2f} "
              f"{r['receptor_backbone_rmsd_last_half_A']:>8.2f} {c:>14s} "
              f"{r['min_lig_prot_dist_last_half_A']:>6.2f}  {r['verdict']}")
    print()
    print("  all rows consistent with FIELDS: yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
