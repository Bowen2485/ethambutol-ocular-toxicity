# -*- coding: utf-8 -*-
"""
Rewrite the per-residue contact part of the trajectory analysis, correctly this time.

What was wrong
    The residue-to-atom mapping used np.searchsorted and a bounds test that did not hold:

        pos = np.searchsorted(prot, idx)
        pos = pos[(pos < len(prot)) & (prot[np.clip(pos, 0, len(prot) - 1)] == idx)]

    When the test failed for an atom the index was dropped, and when it passed for the wrong
    reason the atom was paired with the wrong protein position.  The output gave the number
    of contacting residues as equal to the total number of residues in every target - 301 of
    301, 428 of 428, 841 of 841 - and listed the first residues of each sequence as the
    most persistent contacts, which is the signature of a mapping that selects from the
    start of the array rather than at the residue.

    The polar-contact census and the RMSF do not use that mapping, and their values stand:
    the ligand's polar contacts are maintained or increase while the initial pairs largely
    exchange, which supports the conclusion that the ligand rearranges within the site.

The fix
    A direct lookup table from absolute atom index to row within the protein subset, built
    once.  The same construction is used in analyse_md_pbc.py, where it replaced
    np.searchsorted for the same reason.  No bounds test is needed because every index in
    the residue is by definition present in the protein subset.

A guard
    The script now checks its own output: if the number of contacting residues equals the
    number of residues, it says so and refuses to write the file, because that cannot happen
    for a site of the size the docking found.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = r'''#!/usr/bin/env python
"""
Per-residue contact persistence for the MD trajectories, with a corrected atom mapping.

Only the contact part is recomputed; the polar-contact census and RMSF already produced are
unaffected.  Writes results/md_contact_residues.csv.
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
        return []
    top = md.load_topology(str(tp))
    prot = np.array([a.index for a in top.atoms if a.residue.name in STD], dtype=np.int64)
    lig = np.array([a.index for a in top.atoms if a.residue.name not in STD
                    and a.residue.name not in SOLV], dtype=np.int64)
    if not len(prot) or not len(lig):
        print(f"{gene}: ligand {len(lig)}, protein {len(prot)}")
        return []

    # direct lookup: absolute atom index -> row within the protein subset.  Every residue
    # atom is by construction in the subset, so no membership test is required, and that is
    # the difference from the searchsorted version that produced nonsense.
    row_of = np.full(top.n_atoms, -1, dtype=np.int64)
    row_of[prot] = np.arange(len(prot), dtype=np.int64)

    chosen = None
    for t in sorted(d.glob("*.dcd")):
        try:
            if md.load_frame(str(t), 0, top=str(tp)).n_atoms == top.n_atoms:
                chosen = t
                break
        except Exception:
            continue
    if chosen is None:
        print(f"{gene}: no trajectory matches the topology")
        return []

    tr = md.load(str(chosen), top=str(tp))
    tr.image_molecules(inplace=True)
    n = tr.n_frames
    box = tr.unitcell_vectors
    print(f"\n=== {gene}: {chosen.name}  {n} frames  {tr.n_atoms:,} atoms ===")

    residues = [r for r in top.residues if r.name in STD]
    rows = []
    for r in residues:
        idx = np.array([a.index for a in r.atoms], dtype=np.int64)
        pos = row_of[idx]
        pos = pos[pos >= 0]               # a non-protein atom would map to -1
        if not len(pos):
            continue
        n_contact = 0
        min_dist = 999.0
        for i in range(n):
            dd = min_image(tr.xyz[i][lig], tr.xyz[i][prot][pos],
                           box[i] if box is not None else None)
            m = float(dd.min())
            min_dist = min(min_dist, m)
            if m <= CUT_NM:
                n_contact += 1
        rows.append({"gene": gene, "residue": f"{r.name}{r.resSeq}",
                     "resSeq": int(r.resSeq), "frames_in_contact": n_contact,
                     "n_frames": n, "occupancy": round(n_contact / n, 3),
                     "min_distance_nm": round(min_dist, 3)})

    rows.sort(key=lambda x: -x["occupancy"])
    n_any = sum(1 for x in rows if x["frames_in_contact"] > 0)
    print(f"  residues examined          : {len(rows)}")
    print(f"  residues in contact at all : {n_any}")
    print(f"  residues in contact >=50%  : {sum(1 for x in rows if x['occupancy'] >= 0.5)}")
    for x in rows[:8]:
        print(f"      {x['residue']:10s} occupancy {x['occupancy']:.2f}  "
              f"closest {x['min_distance_nm']:.2f} nm")

    if n_any == len(rows) and len(rows) > 50:
        print(f"  GUARD TRIPPED: every one of the {len(rows)} residues is reported as "
              f"contacting the ligand, which cannot be true for a single binding site. "
              f"The mapping is still wrong; the file was not written.")
        return []
    return rows


all_rows = []
for g in ("NFE2L2", "HMOX1", "MFN2"):
    try:
        all_rows.extend(analyse(g))
    except Exception:
        import traceback
        traceback.print_exc()

if all_rows:
    RES.mkdir(parents=True, exist_ok=True)
    out = RES / "md_contact_residues.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["gene", "residue", "resSeq",
                                           "frames_in_contact", "n_frames",
                                           "occupancy", "min_distance_nm"])
        w.writeheader()
        w.writerows(all_rows)
    print(f"\n-> {out}")
    print(f"   {len(all_rows)} rows")
else:
    print("\nnothing written")
'''

out_p = ROOT / "src" / "analyse_md_contacts.py"
out_p.write_text(SCRIPT, encoding="utf-8")
print(f"  written: {out_p.relative_to(ROOT)}  ({len(SCRIPT.splitlines())} lines)")
print()
print("  Run in WSL with:")
print("      $HOME/miniconda3/envs/md/bin/python ~/ethambutol/src/analyse_md_contacts.py")
