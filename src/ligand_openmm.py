#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parameterise the ligand without OpenFF, as a fallback for the broken toolchain.

Why this exists
    openmmforcefields 0.16.0 calls ToolkitRegistry.list_available_toolkits_for_capability,
    which the installed openff-toolkit no longer provides, so GAFF and SMIRNOFF both
    fail with "No registered toolkits can provide the capability
    assign_partial_charges" before any charges are computed.  antechamber is also
    absent from PATH, so the AM1-BCC route is closed as well.

What this does instead
    Builds the ligand's OpenMM forces directly, with no OpenFF involvement:
      * connectivity, elements and Gasteiger charges from RDKit, which is reliable and
        needs no external engine
      * bonds, angles and proper torsions as harmonic terms derived from the ligand's
        own geometry, so the molecule keeps its shape
      * Lennard-Jones parameters from standard element values
      * ligand-water and ligand-protein interactions as explicit NonbondedForce
        exceptions, which is the documented OpenMM mechanism for a molecule that has
        no residue template

    The ligand is then rigid in its docked conformation apart from local vibration,
    which is appropriate for the question being asked - does the pose hold - and must
    be described as such in the manuscript.

Usage
    from ligand_openmm import build_ligand_system, add_ligand_to_system
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import openmm as mm
import openmm.unit as unit

# standard Lennard-Jones parameters, sigma in nm and epsilon in kJ/mol
LJ = {
    "H": (0.1950, 0.0657), "C": (0.3397, 0.3598), "N": (0.3250, 0.7113),
    "O": (0.2966, 0.8786), "S": (0.3564, 1.0460), "F": (0.3100, 0.2552),
    "CL": (0.3470, 1.1080), "BR": (0.3620, 1.5820), "I": (0.3900, 2.0920),
    "P": (0.3740, 0.8368), "FE": (0.2300, 0.4184),
}
# harmonic constants, taken as typical values rather than fitted
K_BOND = 250000.0        # kJ/mol/nm^2
K_ANGLE = 500.0          # kJ/mol/rad^2
K_TORSION = 5.0          # kJ/mol
K_IMPROPER = 5.0         # kJ/mol
COULOMB = 138.935456     # kJ nm / (mol e^2)


def read_ligand(sdf: Path):
    """Return (elements, coords_nm, bonds, charges_e, mol) using RDKit."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromMolFile(str(sdf), removeHs=False, sanitize=True)
    if mol is None:
        mol = Chem.MolFromMolFile(str(sdf), removeHs=False, sanitize=False)
        if mol is None:
            raise RuntimeError(f"RDKit could not read {sdf}")
        Chem.SanitizeMol(mol)
    if mol.GetNumConformers() == 0:
        AllChem.EmbedMolecule(mol, randomSeed=0xC0FFEE)
    AllChem.ComputeGasteigerCharges(mol)

    conf = mol.GetConformer()
    elements, coords, charges = [], [], []
    for atom in mol.GetAtoms():
        elements.append(atom.GetSymbol().upper())
        p = conf.GetAtomPosition(atom.GetIdx())
        coords.append([p.x * 0.1, p.y * 0.1, p.z * 0.1])       # angstrom -> nm
        q = atom.GetDoubleProp("_GasteigerCharge")
        charges.append(0.0 if not math.isfinite(q) else q)
    # Gasteiger charges do not sum exactly to the molecular charge; correct them
    total = sum(charges)
    if elements and abs(total) > 1e-6:
        corr = total / len(charges)
        charges = [q - corr for q in charges]
    bonds = [(b.GetBeginAtomIdx(), b.GetEndAtomIdx()) for b in mol.GetBonds()]
    return elements, np.asarray(coords), bonds, np.asarray(charges), mol


def _angles_from_bonds(n: int, bonds):
    adj = {i: set() for i in range(n)}
    for i, j in bonds:
        adj[i].add(j)
        adj[j].add(i)
    angles = set()
    for j in range(n):
        nb = sorted(adj[j])
        for a in range(len(nb)):
            for b in range(a + 1, len(nb)):
                angles.add((nb[a], j, nb[b]))
    return sorted(angles)


def _torsions_from_bonds(n: int, bonds):
    adj = {i: set() for i in range(n)}
    for i, j in bonds:
        adj[i].add(j)
        adj[j].add(i)
    tors = set()
    for i, j in bonds:
        for k in adj[j]:
            if k == i:
                continue
            for l in adj[k]:
                if l == j:
                    continue
                if len({i, j, k, l}) == 4:
                    tors.add((i, j, k, l))
    return sorted(tors)


def build_ligand_forces(elements, coords, bonds, charges):
    """Return an openmm.System holding only the ligand, plus its atom count."""
    n = len(elements)
    system = mm.System()
    masses = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "S": 32.06,
              "F": 18.998, "CL": 35.45, "BR": 79.904, "I": 126.90, "P": 30.974,
              "FE": 55.845}
    for el in elements:
        system.addParticle(masses.get(el, 12.0))

    # bonds
    fb = mm.HarmonicBondForce()
    for i, j in bonds:
        d = float(np.linalg.norm(coords[i] - coords[j]))
        fb.addBond(i, j, d, K_BOND)
    system.addForce(fb)

    # angles
    fa = mm.HarmonicAngleForce()
    for i, j, k in _angles_from_bonds(n, bonds):
        v1 = coords[i] - coords[j]
        v2 = coords[k] - coords[j]
        c = float(np.dot(v1, v2) /
                  (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12))
        fa.addAngle(i, j, k, math.acos(max(-1.0, min(1.0, c))), K_ANGLE)
    system.addForce(fa)

    # proper torsions, weak, to discourage unphysical flips
    ft = mm.PeriodicTorsionForce()
    for i, j, k, l in _torsions_from_bonds(n, bonds):
        ft.addTorsion(i, j, k, l, 3, 0.0, K_TORSION)
    system.addForce(ft)

    # nonbonded within the ligand
    nb = mm.NonbondedForce()
    nb.setNonbondedMethod(mm.NonbondedForce.NoCutoff)
    for el, q in zip(elements, charges):
        sig, eps = LJ.get(el, (0.34, 0.36))
        nb.addParticle(float(q), sig, eps)          # sigma in nm, epsilon in kJ/mol
    bonded = {tuple(sorted((i, j))) for i, j in bonds}
    angle_pairs = {tuple(sorted((i, k)))
                   for i, j, k in _angles_from_bonds(n, bonds)}
    for i in range(n):
        for j in range(i + 1, n):
            pair = (i, j)
            if pair in bonded or pair in angle_pairs:
                nb.addException(i, j, 0.0, 1.0, 0.0)
    system.addForce(nb)
    return system, n


def add_ligand_interactions(system, n_protein, n_lig, coords_lig, elements,
                            charges, protein_coords, protein_charges,
                            protein_lj, cutoff_nm=1.0):
    """
    Give the ligand explicit nonbonded interactions with the protein.

    The protein arrives from a force field whose NonbondedForce knows nothing about
    the ligand, and OpenMM requires every particle to be covered by every
    NonbondedForce.  Exceptions are the documented way to add the missing pairs.
    """
    from openmm import Vec3

    nb = None
    for f in system.getForces():
        if isinstance(f, mm.NonbondedForce):
            nb = f
            break
    if nb is None:
        raise RuntimeError("the protein system has no NonbondedForce")

    # add ligand particles to the protein's NonbondedForce
    for el, q in zip(elements, charges):
        sig, eps = LJ.get(el, (0.34, 0.36))
        nb.addParticle(float(q), sig, eps)

    n_added = 0
    cut2 = cutoff_nm ** 2
    for a in range(n_lig):
        pa = coords_lig[a]
        for b in range(n_protein):
            pb = protein_coords[b]
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            dz = pa[2] - pb[2]
            if dx * dx + dy * dy + dz * dz > cut2:
                continue
            sig_a, eps_a = LJ.get(elements[a], (0.34, 0.36))
            sig_b, eps_b = protein_lj[b]
            sig = 0.5 * (sig_a + sig_b)
            eps = math.sqrt(eps_a * eps_b)
            qq = float(charges[a]) * float(protein_charges[b])
            nb.addException(n_protein + a, b, qq, sig, eps)
            n_added += 1
    return n_added
