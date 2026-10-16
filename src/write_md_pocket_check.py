# -*- coding: utf-8 -*-
"""
Write the WSL check that decides whether the reported contact residues are the real pocket.

Why this check is needed
    The corrected contact analysis reports sensible pocket sizes, but in all three targets the
    contacting residues begin near the N-terminus: TYR10, ARG12, PHE15 for NFE2L2; PHE24,
    MET25, PHE28 for HMOX1; TRP95 for MFN2.  A ligand sitting at the N-terminal end of three
    unrelated constructs is unlikely, so either the mapping is still offset - bounded now
    rather than total - or each docked pose genuinely lies there.

    The two possibilities are separated by measuring against an independent landmark.  Each
    run kept receptor_fixed.pdb, and for HMOX1 the heme was extracted separately when the
    1N45 receptor was cleaned.  Heme is the catalytic centre of a heme oxygenase, so if the
    ligand's contact residues are the heme-adjacent ones, the ligand is in the active site
    and the mapping is right.  If the two sets do not overlap, the mapping is still wrong.

    The ligand's own position is also reported, taken from complex.pdb, so the distance from
    the ligand centroid to the first residue of the chain can be compared with the distances
    to the residues reported as contacting.  A ligand near the N-terminus would make those
    distances similar; a mapping error would make them disagree.

The result decides whether the contact-persistence numbers go into the manuscript at all.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = r'''#!/usr/bin/env python
"""
Verify that the MD contact residues match the ligand's actual position.

Runs in WSL, reads only files already on disk, no simulation and no GPU.
"""
import pathlib
import warnings

warnings.filterwarnings("ignore")
import numpy as np
import mdtraj as md

MD = pathlib.Path.home() / "ethambutol" / "md_allatom"
REC = pathlib.Path.home() / "ethambutol" / "receptors_clean"
STD = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
       "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "HID", "HIE",
       "HIP", "CYX", "ASH", "GLH", "LYN"}
SOLV = {"HOH", "WAT", "DOD", "TIP", "SOL", "NA", "CL", "K", "MG", "ZN", "CA", "MN",
        "FE", "CU", "NI", "SO4", "PO4", "NO3", "ACT", "EDO", "GOL"}

# residues the contact analysis reported, in occupancy order
REPORTED = {
    "NFE2L2": ["TYR10", "ARG12", "PHE15", "ASN58", "SER59", "GLN13", "PRO60", "LEU8"],
    "HMOX1": ["PHE24", "MET25", "PHE28", "PHE38", "VAL41", "LEU45", "ARG127", "ASP131"],
    "MFN2": ["TRP95", "LEU166", "ARG289", "GLU313", "GLU317", "SER4", "PRO165", "GLN310"],
}

print("=" * 96)
print("1. Is the ligand where those residues are?  Measured from complex.pdb")
print("=" * 96)
for g, reported in REPORTED.items():
    tp = MD / g / "complex.pdb"
    if not tp.exists():
        print(f"\n{g}: complex.pdb absent")
        continue
    top = md.load_topology(str(tp))
    lig = np.array([a.index for a in top.atoms
                    if a.residue.name not in STD and a.residue.name not in SOLV])
    if not len(lig):
        print(f"\n{g}: no ligand atoms identified")
        continue
    tr = md.load_frame(str(tp), 0, top=str(tp)) if False else md.load(str(tp), top=str(tp))
    lig_c = tr.xyz[0][lig].mean(axis=0) * 10.0

    print(f"\n{g}: ligand centroid {np.round(lig_c, 1)}")
    print(f"     {'residue':10s} {'distance to ligand centroid (A)':>34s}")
    dists = {}
    for name in reported:
        m = None
        for r in top.residues:
            if f"{r.name}{r.resSeq}" == name:
                m = r
                break
        if m is None:
            print(f"     {name:10s} {'residue not found in the topology':>34s}")
            continue
        idx = np.array([a.index for a in m.atoms])
        c = tr.xyz[0][idx].mean(axis=0) * 10.0
        d = float(np.linalg.norm(c - lig_c))
        dists[name] = d
        inside = "  <- close contact" if d < 6.0 else ""
        print(f"     {name:10s} {d:>34.1f}{inside}")

    # the first residue of the chain, as the reference the reported names suggest
    first_prot = next((r for r in top.residues if r.name in STD), None)
    if first_prot is not None and dists:
        idx = np.array([a.index for a in first_prot.atoms])
        c = tr.xyz[0][idx].mean(axis=0) * 10.0
        d_first = float(np.linalg.norm(c - lig_c))
        med = float(np.median(list(dists.values())))
        print()
        print(f"     first residue of the chain: {first_prot.name}{first_prot.resSeq} "
              f"at {d_first:.1f} A from the ligand")
        print(f"     median distance of the reported contacts: {med:.1f} A")
        verdict = ("consistent - the ligand IS near the N-terminus of this construct"
                   if abs(d_first - med) < 12 else
                   "INCONSISTENT - the reported contacts are closer to the ligand than "
                   "the first residue is, so the residue numbering is offset")
        print(f"     -> {verdict}")

print()
print("=" * 96)
print("2. HMOX1: do the contacts overlap the heme site?")
print("=" * 96)
heme = None
for cand in (REC / "1N45" / "HEM.pdb", REC / "1N45" / "HEME.pdb",
             REC / "1N45" / "hem.pdb"):
    if cand.exists():
        heme = cand
        break
print(f"  heme file: {heme if heme else 'not found in receptors_clean/1N45/'}")
if heme:
    heme_xyz = []
    for ln in heme.read_text(errors="replace").splitlines():
        if ln.startswith(("ATOM", "HETATM")):
            try:
                heme_xyz.append([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])
            except ValueError:
                continue
    H = np.array(heme_xyz)
    print(f"  heme atoms: {len(H)}")
    prot = MD / "HMOX1" / "receptor_fixed.pdb"
    if prot.exists() and len(H):
        near = {}
        rec_xyz = []
        names = []
        for ln in prot.read_text(errors="replace").splitlines():
            if not ln.startswith("ATOM"):
                continue
            try:
                rec_xyz.append([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])
                names.append(ln[17:20].strip() + ln[22:27].strip())
            except ValueError:
                continue
        R = np.array(rec_xyz)
        d = np.sqrt(((R[:, None, :] - H[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
        for nm, dd in zip(names, d):
            if dd < 5.0:
                near[nm] = min(near.get(nm, 99.0), float(dd))
        print(f"  receptor residues within 5 A of the heme: {len(near)}")
        print(f"      {sorted(near, key=lambda k: near[k])[:22]}")
        rep = REPORTED["HMOX1"]
        ov = [r for r in rep if r in near]
        print()
        print(f"  reported contact residues that are heme-adjacent: {len(ov)} of {len(rep)}")
        for r in rep:
            print(f"      {r:10s} "
                  f"{'heme-adjacent at %.2f A' % near[r] if r in near else 'not heme-adjacent'}")
        print()
        if len(ov) >= 4:
            print("  -> the ligand contacts include the heme-binding residues, so the")
            print("     pose is in the active site and the residue mapping is sound")
        else:
            print("  -> little or no overlap with the heme site, so the reported contacts")
            print("     are probably not the ligand's real partners")
'''

out = ROOT / "src" / "check_md_pocket.py"
out.write_text(SCRIPT, encoding="utf-8")
print(f"  written: {out.relative_to(ROOT)}  ({len(SCRIPT.splitlines())} lines)")
print()
print("  Run in WSL with:")
print("      $HOME/miniconda3/envs/md/bin/python ~/ethambutol/src/check_md_pocket.py")
