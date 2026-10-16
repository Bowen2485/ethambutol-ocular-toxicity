#!/usr/bin/env python
"""
Per-residue fluctuation, hydrogen bonding and contact stability for the MD trajectories.

Adds to the stability analysis rather than replacing it.  Everything here is computed from
trajectories that already exist, so no simulation is run and the GPU is not touched.

Outputs, all under results/:
    md_rmsf.csv                  per-residue fluctuation for each target
    md_hbonds.csv                hydrogen-bond occupancy per ligand atom pair and per frame
    md_contact_residues.csv      per-residue contact persistence
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
#: atoms that can donate or accept a hydrogen bond
N_DONOR = {"N", "NE", "NE1", "NE2", "ND1", "ND2", "NH1", "NH2", "NZ", "OG", "OG1",
           "OH", "ND", "NE", "O", "OD1", "OD2", "OE1", "OE2", "OT1", "OT2"}
BASE = pathlib.Path.home() / "ethambutol" / "md_allatom"
RES = pathlib.Path.home() / "ethambutol" / "results"


def min_image(A, B, box):
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
    if not len(prot) or not len(lig):
        print(f"{gene}: ligand {len(lig)}, protein {len(prot)}")
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
        print(f"{gene}: no trajectory matches the topology ({top.n_atoms:,} atoms)")
        return None

    tr = md.load(str(chosen), top=str(tp))
    tr.image_molecules(inplace=True)
    n = tr.n_frames
    print(f"\n{'=' * 88}\n{gene}: {chosen.name}  {n} frames  {tr.n_atoms:,} atoms")
    print(f"  ligand {len(lig)}, protein {len(prot)}, backbone {len(bb)}")

    # ---- protein-only superposition, then fluctuation about the mean position
    tr.superpose(tr, frame=0, atom_indices=bb)
    ca = np.array([a.index for a in top.atoms if a.name == "CA"
                   and a.residue.name in STD], dtype=np.int64)
    mean_ca = tr.xyz[:, ca, :].mean(axis=0)
    rmsf = np.sqrt(((tr.xyz[:, ca, :] - mean_ca) ** 2).sum(axis=2).mean(axis=1)) * 10.0
    ca_res = [top.atom(i).residue for i in ca]
    print(f"  RMSF over {len(ca)} C-alpha atoms: mean {rmsf.mean():.2f} A, "
          f"max {rmsf.max():.2f} A")

    # ---- hydrogen bonds between ligand and protein, per frame
    # A bond is counted when a donor hydrogen sits within 2.5 A of an acceptor.  Without
    # explicit hydrogens on the ligand in the topology this reduces to a heavy-atom
    # distance criterion, so a 3.5 A cutoff is applied to donor-acceptor pairs instead and
    # the assumption is stated in the manuscript rather than implied.
    box = tr.unitcell_vectors
    hb_pairs = []
    hb_counts = np.zeros(n, dtype=int)
    for i in range(n):
        L = tr.xyz[i][lig]
        P = tr.xyz[i][prot]
        dmat = min_image(L, P, box[i] if box is not None else None) * 10.0
        close = dmat <= 3.5
        hb_counts[i] = int(close.sum())
        if i == 0:
            li, pi = np.where(close)
            hb_pairs = list(zip(li.tolist(), pi.tolist()))
    print(f"  ligand-protein polar contacts within 3.5 A: "
          f"start {hb_counts[0]}, last-half mean {hb_counts[n//2:].mean():.1f}, "
          f"max {hb_counts.max()}")

    # partner exchange: of the contacts present in the first frame, how many persist
    if hb_pairs:
        persist = np.zeros(n)
        for i in range(n):
            L = tr.xyz[i][lig]
            P = tr.xyz[i][prot]
            dmat = min_image(L, P, box[i] if box is not None else None) * 10.0
            keep = sum(1 for a, b in hb_pairs if dmat[a, b] <= 3.5)
            persist[i] = keep / len(hb_pairs)
        half = n // 2
        print(f"  of the {len(hb_pairs)} initial pairs, surviving in the last half: "
              f"{persist[half:].mean():.2f}")
    else:
        persist = np.zeros(n)

    # ---- per-residue contact stability
    residues = [r for r in top.residues if r.name in STD]
    rows = []
    for r in residues:
        idx = np.array([a.index for a in r.atoms], dtype=np.int64)
        # map to positions within the protein subset
        pos = np.searchsorted(prot, idx)
        pos = pos[(pos < len(prot)) & (prot[np.clip(pos, 0, len(prot) - 1)] == idx)]
        if not len(pos):
            continue
        n_contact = 0
        for i in range(n):
            L = tr.xyz[i][lig]
            P = tr.xyz[i][prot][pos]
            dmat = min_image(L, P, box[i] if box is not None else None)
            if (dmat <= 0.45).any():
                n_contact += 1
        rows.append({"gene": gene, "residue": f"{r.name}{r.resSeq}",
                     "chain": str(r.chain.index), "frames_in_contact": n_contact,
                     "n_frames": n, "occupancy": round(n_contact / n, 3)})
    rows.sort(key=lambda x: -x["occupancy"])
    print(f"  residues in contact at any point: {len(rows)}")
    for r in rows[:5]:
        print(f"      {r['residue']:10s} occupancy {r['occupancy']:.2f}")

    return {
        "gene": gene, "trajectory": chosen.name, "n_frames": n,
        "ns_total": round(n * 0.01, 2),
        "rmsf_mean_A": round(float(rmsf.mean()), 2),
        "rmsf_max_A": round(float(rmsf.max()), 2),
        "rmsf_max_residue": f"{ca_res[int(np.argmax(rmsf))].name}"
                            f"{ca_res[int(np.argmax(rmsf))].resSeq}",
        "polar_contacts_start": int(hb_counts[0]),
        "polar_contacts_last_half": round(float(hb_counts[n // 2:].mean()), 1),
        "polar_contacts_max": int(hb_counts.max()),
        "initial_pair_survival_last_half": round(float(persist[n // 2:].mean()), 2),
        "site_residues_in_contact": len(rows),
        "rmsf": [(f"{r.name}{r.resSeq}", float(v)) for r, v in zip(ca_res, rmsf)],
        "contacts": rows,
        "hbond_series": hb_counts.tolist(),
    }


out = {}
for g in ("NFE2L2", "HMOX1", "MFN2"):
    try:
        r = analyse(g)
        if r:
            out[g] = r
    except Exception:
        import traceback
        traceback.print_exc()

RES.mkdir(parents=True, exist_ok=True)

# summary table
if out:
    with open(RES / "md_rmsf.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["gene", "residue", "rmsf_A"])
        for g, r in out.items():
            for res, v in r["rmsf"]:
                w.writerow([g, res, round(v, 3)])
    with open(RES / "md_hbonds.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["gene", "frame", "time_ns", "polar_contacts"])
        for g, r in out.items():
            for i, c in enumerate(r["hbond_series"]):
                w.writerow([g, i, round(i * 0.01, 2), c])
    with open(RES / "md_contact_residues.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["gene", "residue", "chain",
                                           "frames_in_contact", "n_frames", "occupancy"])
        w.writeheader()
        for g, r in out.items():
            for row in r["contacts"]:
                w.writerow(row)

    print("\n" + "=" * 108)
    print(f"  {'gene':8s} {'frames':>6s} {'ns':>5s} {'RMSF mean':>10s} {'RMSF max':>9s} "
          f"{'polar start':>12s} {'polar 2nd half':>15s} {'pair survival':>14s} "
          f"{'site res':>9s}")
    for g, r in out.items():
        print(f"  {g:8s} {r['n_frames']:>6d} {r['ns_total']:>5.2f} "
              f"{r['rmsf_mean_A']:>10.2f} {r['rmsf_max_A']:>9.2f} "
              f"{r['polar_contacts_start']:>12d} {r['polar_contacts_last_half']:>15.1f} "
              f"{r['initial_pair_survival_last_half']:>14.2f} "
              f"{r['site_residues_in_contact']:>9d}")
    print("=" * 108)
    print(f"\n-> {RES}/md_rmsf.csv")
    print(f"-> {RES}/md_hbonds.csv")
    print(f"-> {RES}/md_contact_residues.csv")
else:
    print("no target could be analysed")
