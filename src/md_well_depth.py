# -*- coding: utf-8 -*-
"""
Last diagnostic on the reduced model: is the ligand escaping because the well is
shallow relative to thermal energy, or because of a remaining implementation fault?

Two quantities decide this, and neither has been checked yet:

  * the depth of the ligand-receptor well in the docked pose, in units of kT
  * the ligand's kinetic energy along the escape direction, in the same units

A ligand cannot leave a well whose depth greatly exceeds kT, so if the well is deep and
the ligand leaves anyway, something else is wrong.  If the well is shallower than kT,
the escape is simply thermal and says nothing about the pose.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import md_coarse as md  # noqa: E402

DOCK = ROOT / "docking"
KT = md.KB * md.TEMPERATURE
print(f"kT at {md.TEMPERATURE:.0f} K = {KT:.4f} kcal/mol")
print(f"model parameters: K_CONTACT={md.K_CONTACT}, EPS_CONTACT={md.EPS_CONTACT}, "
      f"CONTACT_CUT={md.CONTACT_CUT} A, K_LIGAND={md.K_LIGAND}")

d = pd.read_csv(DOCK / "results.csv", encoding="utf-8-sig")
d = d[(d.ligand == "ethambutol") & (d.ok == True)]  # noqa: E712

rows = []
for gene in ("HMOX1", "MFN2", "TNF"):
    row = d[d.gene == gene]
    if row.empty:
        continue
    pdbid = str(row.iloc[0].pdb).strip()
    rec_p = DOCK / "receptors" / pdbid / f"{pdbid}_clean.pdb"
    if not rec_p.exists():
        rec_p = DOCK / "receptors" / pdbid / f"{pdbid}.pdb"
    lig_p = DOCK / "poses" / f"{gene}__ethambutol.pdbqt"
    if not (rec_p.exists() and lig_p.exists()):
        continue
    rec, _ = md.read_pdb_ca(rec_p)
    lig = md.read_ligand_heavy(lig_p)
    pairs, r0, li, ri, lr0, lig_pairs, lig_r0 = md.build_system(rec, lig)

    # total ligand-receptor energy in the docked pose
    pos = np.vstack([rec, lig]).astype(float)
    e_tot, _ = md.energy_forces(pos, len(rec), pairs, r0, li, ri, lr0,
                                lig_pairs, lig_r0)
    empty = np.zeros(0, dtype=int)
    e_no, _ = md.energy_forces(pos, len(rec), pairs, r0, empty, empty,
                               np.zeros(0), lig_pairs, lig_r0)
    e_contact = e_tot - e_no

    # the well depth: energy of the pose minus energy with the ligand moved 30 A away
    far = pos.copy()
    far[len(rec):] += np.array([0.0, 0.0, 30.0])
    e_far, _ = md.energy_forces(far, len(rec), pairs, r0, li, ri, lr0,
                                lig_pairs, lig_r0)
    e_far_no, _ = md.energy_forces(far, len(rec), pairs, r0, empty, empty,
                                   np.zeros(0), lig_pairs, lig_r0)
    depth = (e_far - e_far_no) - e_contact       # >0 means the pose is favoured

    # thermal kinetic energy available to the ligand's centre of mass
    ke_cm = 1.5 * KT
    rows.append({
        "gene": gene,
        "pose": Path(rec_p).stem,
        "n_contacts": int(len(li)),
        "contact_energy_pose": round(float(e_contact), 3),
        "contact_energy_at_30A": round(float(e_far - e_far_no), 3),
        "well_depth_kcal": round(float(depth), 3),
        "well_depth_in_kT": round(float(depth / KT), 2),
        "kT_at_300K": round(KT, 4),
        "cm_kinetic_energy_kT": round(ke_cm / KT, 2),
    })

df = pd.DataFrame(rows)
print()
print("=" * 78)
print("Ligand-receptor well depth in the docked pose")
print("=" * 78)
print(df.to_string(index=False))

print()
print("=" * 78)
print("READING")
print("=" * 78)
for _, r in df.iterrows():
    if r.well_depth_in_kT < 1.0:
        verdict = (f"well only {r.well_depth_in_kT:.2f} kT deep - shallower than "
                   f"thermal energy, so escape is thermal and says nothing about "
                   f"the pose")
    elif r.well_depth_in_kT < 3.0:
        verdict = (f"well {r.well_depth_in_kT:.2f} kT deep - marginal; escape is "
                   f"expected on a 10 ns timescale")
    else:
        verdict = (f"well {r.well_depth_in_kT:.2f} kT deep - escape would NOT be "
                   f"thermal, so an implementation fault is still present")
    print(f"  {r.gene:8s} {verdict}")

df.to_csv(ROOT / "results" / "md_well_depth.csv", index=False,
          encoding="utf-8-sig")
print(f"\n-> {ROOT / 'results' / 'md_well_depth.csv'}")
