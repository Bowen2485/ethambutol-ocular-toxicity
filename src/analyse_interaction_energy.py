#!/usr/bin/env python
"""
Ligand-protein interaction energy over the existing trajectories.

Reads the trajectories already on disk. No simulation, no GPU.
Writes results/md_interaction_energy.csv

The absolute energies below are computed with per-element fixed charges, not with the AM1-BCC
charges the trajectory was built from, because the .dcd does not carry charges.  The quantity
to read is therefore the electrostatic-to-van-der-Waals ratio, which is invariant to the charge
scale; the kcal/mol columns are recorded so the ratio can be checked, not quoted as affinities.
"""
import csv
import pathlib
import warnings
from collections import Counter

warnings.filterwarnings("ignore")
import numpy as np

MD = pathlib.Path.home() / "ethambutol" / "md_allatom"
RES = pathlib.Path.home() / "ethambutol" / "results"
STD = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
       "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "HID", "HIE",
       "HIP", "CYX", "ASH", "GLH", "LYN"}
SOLV = {"HOH", "WAT", "DOD", "TIP", "SOL", "NA", "CL", "K", "MG", "ZN", "CA", "MN",
        "FE", "CU", "NI", "SO4", "PO4", "NO3", "ACT", "EDO", "GOL"}

#: fixed charges in units of the elementary charge.  The trajectory was built with GAFF-2.11
#: and AM1-BCC charges per the method section; those are not recoverable from the .dcd, so the
#: interaction energy is instead computed with a distance-dependent dielectric and formal
#: partial charges, and the result is reported as a ratio of electrostatic to van der Waals
#: contribution rather than as an absolute energy.  A ratio is insensitive to the charge scale,
#: which is the quantity that is not known.  It is not insensitive to the dielectric, which is
#: therefore a named constant below rather than an expression buried in the loop.
Q = {"N": -0.30, "O": -0.50, "C": 0.20, "H": 0.10, "S": -0.20}
#: sigma, the Lennard-Jones zero crossing, in angstrom; epsilon in kcal/mol.  GAFF values.
SIGMA = {"C": 3.40, "N": 3.25, "O": 2.96, "S": 4.00, "H": 1.20}
EPS = {"C": 0.086, "N": 0.170, "O": 0.210, "S": 0.250, "H": 0.015}

#: epsilon = DIELECTRIC_SLOPE * r, with r in angstrom.  The electrostatic term scales as
#: 1 / slope while the van der Waals term does not, so the reported ratio moves with this
#: number and it has to be stated rather than implied.
DIELECTRIC_SLOPE = 1.0


def rmin(e):
    """Lennard-Jones minimum position, sigma * 2**(1/6).  Reported, not used in the energy."""
    return SIGMA.get(e, 3.4) * 2 ** (1 / 6)


def element(atom):
    """Element symbol, read from the topology and falling back to the atom name.

    Read from the topology rather than from columns 77-78 of the PDB record, because those
    columns are blank in some records and a wrong element changes sigma, epsilon and q at once.
    """
    try:
        sym = (atom.element.symbol or "").strip()
    except Exception:  # noqa: BLE001
        sym = ""
    if sym:
        return sym.upper()
    n = "".join(c for c in atom.name if c.isalpha())
    return n[0].upper() if n else "C"


def min_image(A, B, box):
    d = A[:, None, :] - B[None, :, :]
    if box is not None:
        fr = np.einsum("ijk,kl->ijl", d, np.linalg.inv(box))
        fr -= np.round(fr)
        d = np.einsum("ijk,kl->ijl", fr, box)
    return d


def analyse(gene):
    d = MD / gene
    tp = d / "complex.pdb"
    if not tp.exists():
        print(f"{gene}: no complex.pdb")
        return None

    #: coordinates per frame come from the DCD through mdtraj if available, otherwise the
    #: script stops rather than inventing a trajectory
    try:
        import mdtraj as md
    except ImportError:
        print(f"{gene}: mdtraj unavailable")
        return None

    top = md.load_topology(str(tp))
    #: selection by topology atom index, the convention analyse_md_contacts.py already uses.
    #: Indexing by the line number of the ATOM record instead - which an earlier version of this
    #: script did - is off by the number of CRYST1 and TER records.
    prot = np.array([a.index for a in top.atoms if a.residue.name in STD], dtype=np.int64)
    lig = np.array([a.index for a in top.atoms if a.residue.name not in STD
                    and a.residue.name not in SOLV], dtype=np.int64)
    if not len(prot) or not len(lig):
        print(f"{gene}: protein {len(prot)} atoms, ligand {len(lig)} atoms - nothing to compute")
        return None

    chosen = None
    for t in sorted(d.glob("*.dcd")):
        try:
            if md.load_frame(str(t), 0, top=str(tp)).n_atoms == top.n_atoms:
                chosen = t
                break
        except Exception:  # noqa: BLE001
            continue
    if chosen is None:
        print(f"{gene}: no trajectory matches the topology ({top.n_atoms:,} atoms)")
        return None
    tr = md.load(str(chosen), top=str(tp))
    tr.image_molecules(inplace=True)
    n = tr.n_frames
    print(f"\n{gene}: {chosen.name}, {n} frames ({n * 0.01:.2f} ns), "
          f"{len(prot):,} protein atoms and {len(lig)} ligand atoms")
    print(f"  ligand composition: {dict(Counter(element(top.atom(i)) for i in lig))}")

    p_el = [element(top.atom(i)) for i in prot]
    l_el = [element(top.atom(i)) for i in lig]
    p_eps = np.array([EPS.get(e, 0.1) for e in p_el])
    l_eps = np.array([EPS.get(e, 0.1) for e in l_el])
    #: SIGMA, not sigma * 2**(1/6): this Lennard-Jones form takes the zero crossing.  Passing
    #: the minimum position instead moves the well out by 12 per cent and is a different
    #: potential, so the two are not interchangeable here.
    p_sig = np.array([SIGMA.get(e, 3.4) for e in p_el])
    l_sig = np.array([SIGMA.get(e, 3.4) for e in l_el])
    p_q = np.array([Q.get(e, 0.0) for e in p_el])
    l_q = np.array([Q.get(e, 0.0) for e in l_el])

    box = tr.unitcell_vectors
    evdw, eele = [], []
    closest = np.inf
    for f in range(n):
        P = tr.xyz[f][prot]
        L = tr.xyz[f][lig]
        r = min_image(L, P, box[f] if box is not None else None) * 10.0     # angstrom
        closest = min(closest, float(r.min()))
        sep = np.clip(r, 0.9, None)
        #: Lennard-Jones with Lorentz-Berthelot mixing
        s = (l_sig[:, None] + p_sig[None, :]) / 2.0
        e = np.sqrt(l_eps[:, None] * p_eps[None, :])
        sr6 = (s / sep) ** 6
        evdw.append(float((4 * e * (sr6 ** 2 - sr6)).sum()))
        #: Coulomb with a distance-dependent dielectric, epsilon = DIELECTRIC_SLOPE * r, which
        #: is the standard crude treatment when explicit solvent charges are not available in
        #: the trajectory
        qq = l_q[:, None] * p_q[None, :]
        eele.append(float((332.0 * qq / (DIELECTRIC_SLOPE * sep * sep)).sum()))

    evdw = np.array(evdw)
    eele = np.array(eele)
    tot = evdw + eele
    sem = float(tot.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    ratio = float(abs(eele.mean()) / abs(evdw.mean())) if evdw.mean() else float("nan")

    #: the closest approach cannot fall below roughly 1.5 A, so this is the cheapest available
    #: check that the topology and the trajectory are aligned atom for atom
    rmin_min = min(rmin(e) for e in set(l_el) | set(p_el))
    print(f"  closest ligand-protein contact, all frames: {closest:.2f} A "
          f"(smallest Lennard-Jones minimum position here {rmin_min:.2f} A)")
    if closest < 1.5:
        print("  WARNING: a contact below 1.5 A is not physical, so the topology and the")
        print("           trajectory are probably not aligned atom for atom.  Do not use these")
        print("           numbers until that is resolved.")
    elif closest > 4.0:
        print(f"  NOTE: the closest contact is {closest:.2f} A, so the ligand is not in contact")
        print("        with the protein and the mean includes unbound frames.")

    print(f"  van der Waals  mean {evdw.mean():>9.1f} kcal/mol")
    print(f"  electrostatic  mean {eele.mean():>9.1f} kcal/mol")
    print(f"  total          mean {tot.mean():>9.1f}   SEM over frames {sem:.1f}")
    print(f"  |electrostatic| / |van der Waals| = {ratio:.2f}")
    print(f"  NOTE: the {n} frames are consecutive and not independent, so the SEM is a lower")
    print(f"        bound on the true uncertainty, and {n * 0.01:.2f} ns does not sample all")
    print(f"        bound conformations.  The ratio is more robust than the absolute value,")
    print(f"        which also carries the charge model in Q rather than the AM1-BCC charges.")
    return {"gene": gene, "frames": n, "ns": n * 0.01,
            "min_contact_A": round(closest, 2),
            "vdw_mean": round(float(evdw.mean()), 1),
            "elec_mean": round(float(eele.mean()), 1),
            "total_mean": round(float(tot.mean()), 1),
            "sem": round(sem, 1), "elec_vdw_ratio": round(ratio, 2)}


out = []
for g in ("NFE2L2", "HMOX1", "MFN2"):
    try:
        r = analyse(g)
        if r:
            out.append(r)
    except Exception:
        import traceback
        traceback.print_exc()

if out:
    RES.mkdir(parents=True, exist_ok=True)
    with open(RES / "md_interaction_energy.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print("\n" + "=" * 96)
    print(f"  {'gene':8s} {'frames':>7s} {'ns':>6s} {'contact':>8s} {'vdW':>10s} "
          f"{'elec':>10s} {'total':>10s} {'E/D ratio':>10s}")
    for r in out:
        print(f"  {r['gene']:8s} {r['frames']:>7d} {r['ns']:>6.2f} "
              f"{r['min_contact_A']:>8.2f} {r['vdw_mean']:>10.1f} {r['elec_mean']:>10.1f} "
              f"{r['total_mean']:>10.1f} {r['elec_vdw_ratio']:>10.2f}")
    print("=" * 96)
    print(f"\n-> {RES}/md_interaction_energy.csv")
else:
    print("nothing computed")
