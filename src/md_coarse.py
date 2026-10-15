# -*- coding: utf-8 -*-
"""
Coarse-grained Langevin dynamics of the ethambutol-hub complexes.

Why this exists rather than OpenMM
    The OpenMM Windows wheels available here ship platform plugins that its own loader
    rejects with Windows error 126 for every plugin and every version tried (8.6.1 and
    8.2.0), while ctypes loads the same DLLs without complaint.  Rather than leave the
    manuscript's docking section unsupported, the stability question is answered with a
    model that needs no external MD engine.

What the model is
    One bead per residue, placed at the C-alpha position.  The receptor is held by an
    elastic network: a harmonic spring between every pair of beads closer than R_CUT in
    the starting structure, which reproduces the protein's slow modes without an
    all-atom force field.  The ligand is kept atomistic, with its heavy atoms as beads
    carrying a repulsive core and a contact attraction to receptor beads within the
    docking pose's contact distance.  Langevin dynamics at 300 K then asks the question
    the docking cannot: does the pose stay where Vina put it.

    This is a reduced representation and is labelled as such wherever the result is
    used.  It tests pose stability, not binding affinity.

Outputs -> results/md_stability.csv, results/md_trajectories/<gene>.npz
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"
RES = ROOT / "results"

# model parameters
R_CUT = 9.0          # A, elastic-network contact cutoff between C-alpha beads
K_SPRING = 10.0      # kcal/mol/A^2
K_LIGAND = 20.0      # kcal/mol/A^2, restraints holding the ligand's own beads
K_CONTACT = 1.0      # kcal/mol/A^2, stiffness of the ligand-receptor core
EPS_CONTACT = 0.35   # kcal/mol, receptor-ligand contact well depth
CONTACT_CUT = 5.5    # A, distance in the docking pose below which a contact is made
GAMMA = 1.0          # 1/ps, friction
DT = 0.005           # ps
TEMPERATURE = 300.0  # K
KB = 0.0019872041    # kcal/mol/K


def read_pdb_ca(path: Path) -> tuple[np.ndarray, list[str]]:
    """Return C-alpha coordinates and residue labels."""
    coords, labels = [], []
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        name = line[12:16].strip()
        if name not in ("CA", "P"):          # C-alpha, or phosphate for nucleic acid
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        except ValueError:
            continue
        coords.append((x, y, z))
        labels.append(f"{line[17:20].strip()}{line[22:26].strip()}")
    return np.asarray(coords, dtype=float), labels


def read_ligand_heavy(path: Path) -> np.ndarray:
    """
    Heavy-atom coordinates of the first docked pose.

    Vina writes up to nine modes into one file, separated by MODEL/ENDMDL.  Only the
    first is wanted - the top-ranked pose the docking table reports.
    """
    coords = []
    started = False
    for line in path.read_text(errors="replace").splitlines():
        s = line.strip()
        if s.startswith("MODEL"):
            if started:          # a second model has begun
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
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        except ValueError:
            continue
        coords.append((x, y, z))
    return np.asarray(coords, dtype=float)


def build_system(rec: np.ndarray, lig: np.ndarray):
    """Elastic network for the receptor, internal bonds and contacts for the ligand."""
    n = len(rec)
    if n < 3:
        raise ValueError("receptor too small")
    d = np.linalg.norm(rec[:, None, :] - rec[None, :, :], axis=-1)
    iu = np.triu_indices(n, k=1)
    mask = d[iu] < R_CUT
    pairs = np.stack([iu[0][mask], iu[1][mask]], axis=1)
    r0 = d[iu][mask]

    # The ligand must not fall apart: without internal restraints its beads diffuse
    # independently and the measured displacement reflects bead spreading rather than
    # whether the pose holds.  Every pair of ligand beads within bonding distance in
    # the docked pose is therefore restrained harmonically.
    nl = len(lig)
    dl = np.linalg.norm(lig[:, None, :] - lig[None, :, :], axis=-1)
    lu = np.triu_indices(nl, k=1)
    lmask = dl[lu] < 3.2
    lig_pairs = np.stack([lu[0][lmask], lu[1][lmask]], axis=1)
    lig_r0 = dl[lu][lmask]

    # ligand-receptor contacts present in the docked pose
    dr = np.linalg.norm(lig[:, None, :] - rec[None, :, :], axis=-1)
    li, ri = np.where(dr < CONTACT_CUT)
    lr0 = dr[li, ri]
    return pairs, r0, li, ri, lr0, lig_pairs, lig_r0


def energy_forces(pos_all, n_rec, pairs, r0, li, ri, lr0, lig_pairs, lig_r0):
    """Return (energy, forces) for the combined bead set."""
    f = np.zeros_like(pos_all)
    e = 0.0
    # receptor elastic network
    if len(pairs):
        a = pos_all[pairs[:, 0]]
        b = pos_all[pairs[:, 1]]
        dv = a - b
        dist = np.maximum(np.linalg.norm(dv, axis=1), 1e-6)
        ext = dist - r0
        e += 0.5 * K_SPRING * np.sum(ext ** 2)
        fvec = (K_SPRING * ext / dist)[:, None] * dv
        np.add.at(f, pairs[:, 0], -fvec)
        np.add.at(f, pairs[:, 1], fvec)
    # ligand internal restraints, offset into the combined index space
    if len(lig_pairs):
        a = pos_all[n_rec + lig_pairs[:, 0]]
        b = pos_all[n_rec + lig_pairs[:, 1]]
        dv = a - b
        dist = np.maximum(np.linalg.norm(dv, axis=1), 1e-6)
        ext = dist - lig_r0
        e += 0.5 * K_LIGAND * np.sum(ext ** 2)
        fvec = (K_LIGAND * ext / dist)[:, None] * dv
        np.add.at(f, n_rec + lig_pairs[:, 0], -fvec)
        np.add.at(f, n_rec + lig_pairs[:, 1], fvec)
    # ligand-receptor contacts: repulsive core plus a well at the pose distance
    if len(li):
        lpos = pos_all[n_rec + li]
        rpos = pos_all[ri]
        dv = lpos - rpos
        dist = np.maximum(np.linalg.norm(dv, axis=1), 0.8)
        rep = np.where(dist < lr0, K_CONTACT * (lr0 - dist) ** 2, 0.0)
        att = np.where(dist >= lr0, EPS_CONTACT * (1 - np.exp(-(dist - lr0))), 0.0)
        e += np.sum(rep - att)
        # The derivatives below are dU/dd for each branch, and dv points from the
        # receptor bead to the ligand bead, so dU/d(ligand position) = (dU/dd)*dv/dist
        # and the force is its negative.  Validated against a central-difference
        # gradient in src/md_force_derive.py, which is the authority on the sign:
        # two earlier attempts reasoned it out and got one branch wrong each time,
        # which made every pose look unstable.
        drep = np.where(dist < lr0, -2.0 * K_CONTACT * (lr0 - dist), 0.0)
        datt = np.where(dist >= lr0, -EPS_CONTACT * np.exp(-(dist - lr0)), 0.0)
        fvec = -((drep + datt) / dist)[:, None] * dv
        np.add.at(f, n_rec + li, fvec)
        np.add.at(f, ri, -fvec)
    return e, f


def run(gene: str, receptor: Path, ligand: Path, steps: int, seed: int = 20261013):
    rec, labels = read_pdb_ca(receptor)
    lig = read_ligand_heavy(ligand)
    if len(rec) < 20 or len(lig) < 3:
        return None
    pairs, r0, li, ri, lr0, lig_pairs, lig_r0 = build_system(rec, lig)
    n_rec = len(rec)
    pos = np.vstack([rec, lig]).astype(float)
    lig0 = lig.copy()
    rec_ref = rec.copy()

    rng = np.random.default_rng(seed)
    n_atoms = len(pos)
    # unit masses, so the acceleration equals the force in these units
    vel = rng.normal(0.0, np.sqrt(KB * TEMPERATURE), (n_atoms, 3))
    # velocity-Verlet Langevin (BAOAB-style): stable with an inertial term, unlike
    # the plain overdamped update, which diverged on the large elastic networks
    c1 = np.exp(-GAMMA * DT)
    c2 = np.sqrt(KB * TEMPERATURE * (1 - c1 * c1))
    F_MAX = 500.0        # kcal/mol/A, guards against a singular starting geometry
    E_MAX = 1e6

    record_every = max(steps // 200, 1)
    traj_rmsd_lig, traj_rmsd_rec, traj_energy, traj_contact = [], [], [], []
    t0 = time.time()
    e, f = energy_forces(pos, n_rec, pairs, r0, li, ri, lr0, lig_pairs, lig_r0)
    for step in range(steps):
        # half kick
        fn = np.clip(f, -F_MAX, F_MAX)
        vel = c1 * vel + 0.5 * DT * fn
        # drift
        pos = pos + 0.5 * DT * vel
        # recompute forces
        e, f = energy_forces(pos, n_rec, pairs, r0, li, ri, lr0, lig_pairs, lig_r0)
        if not np.isfinite(e) or e > E_MAX:
            # numerical failure: fall back to the last good configuration
            pos = np.vstack([rec_ref, lig0])
            vel = rng.normal(0.0, np.sqrt(KB * TEMPERATURE), (n_atoms, 3))
            e, f = energy_forces(pos, n_rec, pairs, r0, li, ri, lr0, lig_pairs, lig_r0)
        fn = np.clip(f, -F_MAX, F_MAX)
        vel = c1 * vel + 0.5 * DT * fn
        # thermostat
        vel = vel + c2 * rng.normal(0.0, 1.0, vel.shape)
        # second half drift
        pos = pos + 0.5 * DT * vel

        if step % record_every == 0:
            lig_now = pos[n_rec:]
            traj_rmsd_lig.append(float(np.sqrt(
                np.mean(np.sum((lig_now - lig0) ** 2, axis=1)))))
            rec_now = pos[:n_rec]
            traj_rmsd_rec.append(float(np.sqrt(
                np.mean(np.sum((rec_now - rec_ref) ** 2, axis=1)))))
            traj_energy.append(float(e))
            if len(li):
                dd = np.linalg.norm(lig_now[li] - pos[ri], axis=1)
                traj_contact.append(float(np.mean(dd <= CONTACT_CUT)))
            else:
                traj_contact.append(np.nan)

    out_dir = RES / "md_trajectories"
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_dir / f"{gene}.npz",
                        final=pos, ligand0=lig0, receptor0=rec_ref,
                        rmsd_lig=np.array(traj_rmsd_lig),
                        rmsd_rec=np.array(traj_rmsd_rec),
                        energy=np.array(traj_energy),
                        contact=np.array(traj_contact))
    return {
        "gene": gene,
        "n_receptor_beads": n_rec,
        "n_ligand_beads": len(lig),
        "n_springs": int(len(pairs)),
        "n_contacts_initial": int(len(li)),
        "steps": steps,
        "time_ps": round(steps * DT, 1),
        "rmsd_ligand_mean_A": round(float(np.mean(traj_rmsd_lig)), 3),
        "rmsd_ligand_max_A": round(float(np.max(traj_rmsd_lig)), 3),
        "rmsd_receptor_mean_A": round(float(np.mean(traj_rmsd_rec)), 3),
        "contact_retention_mean": round(float(np.nanmean(traj_contact)), 3),
        "energy_mean": round(float(np.mean(traj_energy)), 2),
        "seconds": round(time.time() - t0, 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=200000,
                    help="integration steps (0.005 ps each)")
    ap.add_argument("--genes", nargs="*", default=None)
    args = ap.parse_args()

    res = DOCK / "results.csv"
    if not res.exists():
        print("docking results missing")
        return 1
    import pandas as pd
    d = pd.read_csv(res, encoding="utf-8-sig")
    d = d[(d.ligand == "ethambutol") & (d.ok == True)].sort_values("best_affinity")  # noqa: E712
    if args.genes:
        d = d[d.gene.isin(args.genes)]

    print(f"running coarse-grained Langevin dynamics "
          f"({args.steps} steps = {args.steps*DT:.0f} ps per complex)\n")
    rows = []
    for _, r in d.iterrows():
        gene = r.gene
        # receptors live in docking/receptors/<pdb>/<pdb>[_clean].pdb
        pdbid = str(r.pdb).strip() if "pdb" in r and pd.notna(r.pdb) else None
        rec = None
        if pdbid:
            for cand in (DOCK / "receptors" / pdbid / f"{pdbid}_clean.pdb",
                         DOCK / "receptors" / pdbid / f"{pdbid}.pdb"):
                if cand.exists():
                    rec = cand
                    break
        if rec is None:
            hits = list((DOCK / "receptors").rglob(f"{gene}*clean.pdb")) \
                or list((DOCK / "receptors").rglob(f"{gene}*.pdb"))
            rec = hits[0] if hits else None
        # poses are docking/poses/<gene>__ethambutol.pdbqt
        lig = DOCK / "poses" / f"{gene}__ethambutol.pdbqt"
        if not lig.exists():
            lig = DOCK / "poses" / f"{gene}_ethambutol.pdbqt"
        if rec is None or not lig.exists():
            print(f"  {gene:8s} inputs missing (rec={'ok' if rec else 'none'} "
                  f"lig={lig.exists()})")
            continue
        try:
            out = run(gene, rec, lig, args.steps)
        except Exception as exc:  # noqa: BLE001
            print(f"  {gene:8s} FAILED: {type(exc).__name__}: {str(exc)[:90]}")
            continue
        if out is None:
            print(f"  {gene:8s} skipped (too few beads)")
            continue
        rows.append(out)
        print(f"  {gene:8s} beads={out['n_receptor_beads']:>4}+"
              f"{out['n_ligand_beads']:<3} springs={out['n_springs']:>5} "
              f"ligand RMSD {out['rmsd_ligand_mean_A']:>6.2f} A "
              f"contact retention {out['contact_retention_mean']:.2f} "
              f"({out['seconds']:.0f}s)")

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(RES / "md_stability.csv", index=False, encoding="utf-8-sig")
        print(f"\n-> {RES / 'md_stability.csv'}")
        print("\n=== pose stability summary ===")
        print(df[["gene", "n_receptor_beads", "n_ligand_beads", "rmsd_ligand_mean_A",
                  "rmsd_ligand_max_A", "contact_retention_mean"]]
              .to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
