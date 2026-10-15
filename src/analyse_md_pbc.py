#!/usr/bin/env python
"""
PBC-corrected stability analysis of the all-atom trajectories.

The original analysis superposed each frame and then differenced raw coordinates, which
breaks whenever a molecule crosses the periodic boundary: the stored coordinates jump by
a box vector.  For NFE2L2 that produced a receptor backbone RMSD of 13.0 A against a true
1.18 A, apparent N-terminal displacements of 60-66 A, a contact survival of 0.035 where
contacts in fact rise from 292 to 312, and - because the verdict tested a centroid drift
and never consulted the ligand RMSD - the conclusion that the ligand had left the site.

The trajectory is therefore imaged before anything is measured, contacts are evaluated
under the minimum-image convention, and the verdict rests on the minimum ligand-protein
distance, which no imaging choice can manufacture.
"""
import csv
import pathlib
import warnings

warnings.filterwarnings("ignore")
import numpy as np
import mdtraj as md

STD = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
       "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "HID", "HIE",
       "HIP", "CYX", "ASH", "GLH", "LYN"}
SOLV = {"HOH", "WAT", "DOD", "TIP", "SOL", "NA", "CL", "K", "MG", "ZN", "CA", "MN",
        "FE", "CU", "NI", "SO4", "PO4", "NO3", "ACT", "EDO", "GOL"}
CUT_NM = 0.45
BASE = pathlib.Path.home() / "ethambutol" / "md_allatom"


def min_image_dists(A, B, box):
    """Pairwise A-B distances under the minimum-image convention."""
    d = A[:, None, :] - B[None, :, :]
    if box is not None:
        fr = np.einsum("ijk,kl->ijl", d, np.linalg.inv(box))
        fr -= np.round(fr)
        d = np.einsum("ijk,kl->ijl", fr, box)
    return np.linalg.norm(d, axis=2)


def analyse(gene):
    d = BASE / gene
    tp = d / "complex.pdb"
    if not tp.exists():
        print(f"{gene}: no complex.pdb")
        return None
    top = md.load_topology(str(tp))
    prot = np.array([a.index for a in top.atoms if a.residue.name in STD], dtype=np.int64)
    bb = np.array([a.index for a in top.atoms if a.name in ("CA", "C", "N", "O")
                   and a.residue.name in STD], dtype=np.int64)
    lig = np.array([a.index for a in top.atoms if a.residue.name not in STD
                    and a.residue.name not in SOLV], dtype=np.int64)
    if not len(lig) or not len(prot) or not len(bb):
        print(f"{gene}: ligand {len(lig)}, protein {len(prot)}, backbone {len(bb)}")
        return None

    chosen = None
    for t in sorted(d.glob("*.dcd")):
        try:
            if md.load_frame(str(t), 0, top=str(tp)).n_atoms == top.n_atoms:
                chosen = t
                break
        except Exception:
            continue
    if chosen is None:
        got = []
        for t in sorted(d.glob("*.dcd")):
            try:
                got.append((t.name, md.load_frame(str(t), 0).n_atoms))
            except Exception:
                got.append((t.name, "unreadable"))
        print(f"{gene}: no trajectory matches {tp.name} ({top.n_atoms:,} atoms). "
              f"Trajectories present: {got}")
        return None

    tr = md.load(str(chosen), top=str(tp))
    n = tr.n_frames
    print(f"\n{'=' * 88}\n{gene}: {chosen.name}  {n} frames  {tr.n_atoms:,} atoms  "
          f"ligand {len(lig)}  protein {len(prot)}")
    if tr.unitcell_lengths is not None:
        L = tr.unitcell_lengths[0] * 10.0
        print(f"  box {L[0]:.1f} x {L[1]:.1f} x {L[2]:.1f} A")

    # ---- 1. image, so a molecule split across the boundary is made whole
    raw = tr.xyz.copy()
    imaging_ok = True
    try:
        tr.image_molecules(inplace=True)
    except Exception as exc:
        imaging_ok = False
        print(f"  image_molecules failed ({type(exc).__name__}); distances still use "
              f"the minimum image per pair, but the RMSDs are unreliable")
    shift = float(np.linalg.norm(tr.xyz - raw, axis=2).max()) * 10.0
    print(f"  imaging applied: {imaging_ok}; largest coordinate change {shift:.1f} A "
          f"(near the box length means atoms were crossing it)")

    # ---- 2. superpose on the receptor backbone, now safe
    tr.superpose(tr, frame=0, atom_indices=bb)
    rec_rms = np.sqrt(((tr.xyz[:, bb, :] - tr.xyz[0, bb, :]) ** 2)
                      .sum(axis=2).mean(axis=1)) * 10.0
    lig_rms = np.sqrt(((tr.xyz[:, lig, :] - tr.xyz[0, lig, :]) ** 2)
                      .sum(axis=2).mean(axis=1)) * 10.0

    # ---- 3. contacts and minimum distance, both under the minimum image
    box = tr.unitcell_vectors if tr.unitcell_lengths is not None else None
    d0 = min_image_dists(tr.xyz[0][lig], tr.xyz[0][prot],
                         box[0] if box is not None else None)
    pairs = np.array([(l, p) for l in range(len(lig)) for p in range(len(prot))],
                     dtype=np.int64)
    start = pairs[(d0 <= CUT_NM).ravel()]
    n_start = len(start)

    ct = np.zeros(n, dtype=int)
    mdist = np.zeros(n)
    surv = np.zeros(n)
    for i in range(n):
        dd = min_image_dists(tr.xyz[i][lig], tr.xyz[i][prot],
                             box[i] if box is not None else None)
        ct[i] = int((dd <= CUT_NM).sum())
        mdist[i] = float(dd.min()) * 10.0
        if n_start:
            surv[i] = float((dd[start[:, 0], start[:, 1]] <= CUT_NM).mean())

    print(f"\n  {'frame':>6s} {'t(ns)':>7s} {'ligRMSD':>9s} {'recRMSD':>9s} "
          f"{'contacts':>9s} {'minDist':>9s}")
    for i in range(0, n, max(n // 15, 1)):
        print(f"  {i:>6d} {i * 0.01:>7.2f} {lig_rms[i]:>9.2f} {rec_rms[i]:>9.2f} "
              f"{ct[i]:>9d} {mdist[i]:>9.2f}")

    h = n // 2
    out = {
        "gene": gene,
        "trajectory": chosen.name,
        "n_frames": n,
        "ns_analysed": round(n * 0.01, 2),
        "imaging_applied": imaging_ok,
        "largest_imaging_shift_A": round(shift, 1),
        "receptor_backbone_rmsd_last_half_A": round(float(rec_rms[h:].mean()), 2),
        "receptor_backbone_rmsd_max_A": round(float(rec_rms.max()), 2),
        "ligand_rmsd_last_half_A": round(float(lig_rms[h:].mean()), 2),
        "ligand_rmsd_max_A": round(float(lig_rms.max()), 2),
        "contacts_start": int(n_start),
        "contacts_last_half_mean": round(float(ct[h:].mean()), 1),
        "contacts_min": int(ct.min()),
        "min_lig_prot_dist_start_A": round(float(mdist[0]), 2),
        "min_lig_prot_dist_last_half_A": round(float(mdist[h:].mean()), 2),
        "min_lig_prot_dist_max_A": round(float(mdist.max()), 2),
    }
    # the verdict rests on contact with the protein, which imaging cannot manufacture
    kept_contact = out["min_lig_prot_dist_last_half_A"] < 4.5
    if kept_contact and out["contacts_last_half_mean"] >= 0.5 * n_start:
        out["verdict"] = "docked pose retained"
    elif kept_contact:
        out["verdict"] = "bound, but the pose shifted within the site"
    elif out["min_lig_prot_dist_last_half_A"] < 10.0:
        out["verdict"] = "partially detached"
    else:
        out["verdict"] = "ligand left the protein"
    print(f"\n  ligRMSD {out['ligand_rmsd_last_half_A']} A   "
          f"recRMSD {out['receptor_backbone_rmsd_last_half_A']} A   "
          f"contacts {out['contacts_start']} -> {out['contacts_last_half_mean']}   "
          f"minDist {out['min_lig_prot_dist_last_half_A']} A")
    print(f"  VERDICT: {out['verdict']}")
    return out


rows = []
for g in ("NFE2L2", "HMOX1", "MFN2", "TNF", "BCL2"):
    try:
        r = analyse(g)
        if r:
            rows.append(r)
    except Exception:
        import traceback
        traceback.print_exc()

if rows:
    outp = pathlib.Path.home() / "ethambutol" / "results" / "md_allatom_stability_pbc.csv"
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n-> {outp}")
    print("\n" + "=" * 96)
    print(f"  {'gene':8s} {'ns':>5s} {'ligRMSD':>8s} {'recRMSD':>8s} "
          f"{'contacts':>16s} {'minD':>6s}  verdict")
    for r in rows:
        c = f"{r['contacts_start']}->{r['contacts_last_half_mean']:.0f}"
        print(f"  {r['gene']:8s} {r['ns_analysed']:>5.2f} "
              f"{r['ligand_rmsd_last_half_A']:>8.2f} "
              f"{r['receptor_backbone_rmsd_last_half_A']:>8.2f} {c:>16s} "
              f"{r['min_lig_prot_dist_last_half_A']:>6.2f}  {r['verdict']}")
    print("=" * 96)
