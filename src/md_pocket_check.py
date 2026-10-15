# -*- coding: utf-8 -*-
"""
Inspect a saved trajectory to say plainly whether the ligand stayed in its pocket.

Contact retention of 8% is ambiguous on its own: it could mean the ligand left, or
that a handful of long-range contacts dominate the count while the core of the pose is
intact.  This measures, from the saved final configuration:

  * displacement of the ligand centroid from its docked position
  * distance from the ligand centroid to the centroid of the residues that formed the
    pose's contacts, at the start and at the end
  * how many of the pose's contacts are still within the contact cutoff
  * the same restricted to the tightest contacts, which are the ones that define
    a pose
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results" / "md_trajectories"
CONTACT_CUT = 5.5

if not RES.is_dir():
    print(f"no trajectories at {RES}")
    sys.exit(1)

rows = []
for p in sorted(RES.glob("*.npz")):
    d = np.load(p)
    final = d["final"]
    lig0 = d["ligand0"]
    rec0 = d["receptor0"]
    n_rec = len(rec0)
    lig1 = final[n_rec:]
    rec1 = final[:n_rec]

    # contacts that defined the pose
    dr0 = np.linalg.norm(lig0[:, None, :] - rec0[None, :, :], axis=-1)
    li, ri = np.where(dr0 < CONTACT_CUT)
    tight = dr0[li, ri] < 3.6
    dr1 = np.linalg.norm(lig1[li] - rec1[ri], axis=1)

    cen0, cen1 = lig0.mean(axis=0), lig1.mean(axis=0)
    pocket0 = rec0[np.unique(ri)].mean(axis=0)
    pocket1 = rec1[np.unique(ri)].mean(axis=0)

    rows.append({
        "gene": p.stem,
        "n_contacts_pose": int(len(li)),
        "ligand_centroid_shift_A": round(float(np.linalg.norm(cen1 - cen0)), 2),
        "pocket_centroid_shift_A": round(float(np.linalg.norm(pocket1 - pocket0)), 2),
        "lig_to_pocket_start_A": round(float(np.linalg.norm(cen0 - pocket0)), 2),
        "lig_to_pocket_end_A": round(float(np.linalg.norm(cen1 - pocket1)), 2),
        "contacts_within_cut_end": int(np.sum(dr1 <= CONTACT_CUT)),
        "contact_retention_pct": round(100 * float(np.mean(dr1 <= CONTACT_CUT)), 1),
        "tight_contacts": int(tight.sum()),
        "tight_retention_pct": round(
            100 * float(np.mean(dr1[tight] <= CONTACT_CUT)), 1) if tight.any() else np.nan,
        "mean_contact_dist_start_A": round(float(dr0[li, ri].mean()), 2),
        "mean_contact_dist_end_A": round(float(dr1.mean()), 2),
    })

import pandas as pd  # noqa: E402

df = pd.DataFrame(rows)
print("=" * 78)
print("Did the ligand stay in its pocket?")
print("=" * 78)
print(df[["gene", "ligand_centroid_shift_A", "lig_to_pocket_start_A",
          "lig_to_pocket_end_A", "contact_retention_pct", "tight_retention_pct",
          "mean_contact_dist_start_A", "mean_contact_dist_end_A"]]
      .to_string(index=False))

print()
print("=" * 78)
print("Reading")
print("=" * 78)
for _, r in df.iterrows():
    verdict = ("stayed in the pocket"
               if r.ligand_centroid_shift_A < 2.5 and r.contact_retention_pct > 50
               else "moved out of the docked pose"
               if r.ligand_centroid_shift_A > 4.0
               else "partially displaced")
    print(f"  {r.gene:8s} centroid moved {r.ligand_centroid_shift_A:>5.2f} A, "
          f"contacts retained {r.contact_retention_pct:>5.1f}% "
          f"(tight {r.tight_retention_pct:>5.1f}%) -> {verdict}")

df.to_csv(ROOT / "results" / "md_pocket_check.csv", index=False,
          encoding="utf-8-sig")
print(f"\n-> {ROOT / 'results' / 'md_pocket_check.csv'}")
