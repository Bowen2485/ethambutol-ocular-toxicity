# -*- coding: utf-8 -*-
"""
Confirm why the ligand left a well that is many kT deep.

The well depth in the docked pose is 4-12 kT, which thermal motion cannot overcome, so
the escape must be driven by the receptor rather than by the ligand.  The ligand pushes
back on the receptor beads with an equal and opposite force; if the elastic network is
too soft to resist that, the pocket opens and the ligand falls out of a site that no
longer exists.

This measures how far the receptor beads that line the pocket moved, and compares the
restoring force from the network with the force applied by the ligand.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import md_coarse as md  # noqa: E402

TRAJ = ROOT / "results" / "md_trajectories"
rows = []
for p in sorted(TRAJ.glob("*.npz")):
    d = np.load(p)
    final, lig0, rec0 = d["final"], d["ligand0"], d["receptor0"]
    n_rec = len(rec0)
    rec1 = final[:n_rec]
    lig1 = final[n_rec:]

    # residues lining the pocket in the docked pose
    dr0 = np.linalg.norm(lig0[:, None, :] - rec0[None, :, :], axis=-1)
    lining = np.unique(np.where(dr0 < md.CONTACT_CUT)[1])
    if len(lining) == 0:
        continue
    disp = np.linalg.norm(rec1[lining] - rec0[lining], axis=1)

    # opening of the site: increase in the radius of gyration of the lining residues
    rg0 = np.linalg.norm(rec0[lining] - rec0[lining].mean(axis=0), axis=1).mean()
    rg1 = np.linalg.norm(rec1[lining] - rec1[lining].mean(axis=0), axis=1).mean()

    # force balance in the docked pose
    pos = np.vstack([rec0, lig0]).astype(float)
    pairs, r0, li, ri, lr0, lig_pairs, lig_r0 = md.build_system(rec0, lig0)
    e_tot, f_tot = md.energy_forces(pos, n_rec, pairs, r0, li, ri, lr0,
                                   lig_pairs, lig_r0)
    empty = np.zeros(0, dtype=int)
    _, f_no = md.energy_forces(pos, n_rec, pairs, r0, empty, empty, np.zeros(0),
                               lig_pairs, lig_r0)
    f_contact = f_tot - f_no
    f_on_receptor = np.linalg.norm(f_contact[:n_rec], axis=1).max()
    f_on_ligand = np.linalg.norm(f_contact[n_rec:], axis=1).max()
    # what the network can supply for a 1 A displacement
    net_k = md.K_SPRING * max(len(pairs) // max(n_rec, 1), 1)

    rows.append({
        "gene": p.stem,
        "n_lining_residues": int(len(lining)),
        "lining_displacement_mean_A": round(float(disp.mean()), 2),
        "lining_displacement_max_A": round(float(disp.max()), 2),
        "site_radius_start_A": round(float(rg0), 2),
        "site_radius_end_A": round(float(rg1), 2),
        "site_opening_A": round(float(rg1 - rg0), 2),
        "max_force_on_receptor": round(float(f_on_receptor), 2),
        "max_force_on_ligand": round(float(f_on_ligand), 2),
        "network_stiffness_per_bead": round(float(net_k), 2),
        "ligand_receptor_gap_start_A": round(float(
            np.linalg.norm(lig0[li] - rec0[ri], axis=1).mean()), 2),
        "ligand_receptor_gap_end_A": round(float(
            np.linalg.norm(lig1[li] - rec1[ri], axis=1).mean()), 2),
    })

df = pd.DataFrame(rows)
print("=" * 80)
print("Did the pocket open, or did the ligand leave a rigid pocket?")
print("=" * 80)
print(df.to_string(index=False))

print()
print("=" * 80)
print("READING")
print("=" * 80)
for _, r in df.iterrows():
    if r.site_opening_A > 1.0:
        verdict = (f"the site opened by {r.site_opening_A:.2f} A while the ligand "
                   f"pulled on it, so the ligand left a pocket that the model "
                   f"deformed rather than one that failed")
    else:
        verdict = (f"the site held its shape ({r.site_opening_A:+.2f} A); the "
                   f"ligand's departure is not explained by receptor deformation")
    print(f"  {r.gene:8s} {verdict}")

df.to_csv(ROOT / "results" / "md_receptor_deformation.csv", index=False,
          encoding="utf-8-sig")
print(f"\n-> {ROOT / 'results' / 'md_receptor_deformation.csv'}")
