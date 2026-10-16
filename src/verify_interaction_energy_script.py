# -*- coding: utf-8 -*-
"""
Verify the three faults found by reading src/analyse_interaction_energy.py against the scripts
that already work, without needing mdtraj or the trajectories (neither exists on this side).

Each fault is reproduced as a computation rather than asserted, so the repair can be checked
rather than believed:

  1. Atom selection by PDB line number.  complex.pdb as OpenMM's PDBFile.writeFile writes it
     begins with CRYST1 and carries TER records, so the line number of an ATOM record is not
     its atom index.  A synthetic file with that exact layout is built here and the old
     expression is evaluated against it.

  2. The Lennard-Jones term used sigma * 2**(1/6) where the form takes sigma.  The two
     potentials are evaluated side by side at contact distances.

  3. The Coulomb term carried a 4.0 factor that cancelled itself.  That one is a
     documentation fault, not a numerical one, and is shown to be exact rather than argued.

Writes results/interaction_script_verification.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "interaction_script_verification.json"

STD = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
       "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"}
SOLV = {"HOH", "WAT", "DOD", "TIP", "SOL", "NA", "CL", "K", "MG", "ZN", "CA", "MN"}
SIGMA = {"C": 3.40, "N": 3.25, "O": 2.96, "S": 4.00, "H": 1.20}
EPS = {"C": 0.086, "N": 0.170, "O": 0.210, "S": 0.250, "H": 0.015}

findings = {}

print("=" * 92)
print("1. Atom selection by PDB line number")
print("=" * 92)

N_PROT, N_LIG, N_WATER = 12, 38, 6


def build_pdb(order):
    """A complex.pdb laid out the way OpenMM's PDBFile.writeFile writes one.

    order is the block order.  It matters, and the two orders here are not hypothetical:
    run_md_allatom.py solvates the protein first and inserts the ligand afterwards
    (`modeller.addSolvent(...)` then `modeller.add(lig_top, ...)`), so the ligand is the last
    block.  The other order is included because a file written in a different order fails
    differently, and one of the two failure modes is silent.
    """
    lines = ["CRYST1   78.500   78.500   78.500  90.00  90.00  90.00 P 1           1"]
    blocks = {
        "protein": [f"ATOM  {i + 1:5d}  N   ALA A{i // 3 + 1:4d}      "
                    f"{1.0 + i * 0.1:8.3f}{2.0:8.3f}{3.0:8.3f}  1.00  0.00           N"
                    for i in range(N_PROT)],
        "water": [f"HETATM{i + 1:5d}  O   HOH B{i + 1:4d}      "
                  f"{9.0:8.3f}{9.0:8.3f}{9.0:8.3f}  1.00  0.00           O"
                  for i in range(N_WATER)],
        "ligand": [f"HETATM{i + 1:5d}  C{i + 1:<3d}UNK C{i // 4 + 1:4d}      "
                   f"{5.0 + i * 0.1:8.3f}{6.0:8.3f}{7.0:8.3f}  1.00  0.00           C"
                   for i in range(N_LIG)],
    }
    for name in order:
        lines.extend(blocks[name])
        lines.append("TER")
    return lines


def old_selection(lines):
    """The expression the first version used: the line number of the record is the index."""
    prot, lig = [], []
    for i, ln in enumerate(lines):
        if not ln.startswith(("ATOM", "HETATM")):
            continue
        resn = ln[17:20].strip()
        if resn in STD:
            prot.append(i)
        elif resn not in SOLV:
            lig.append(i)
    return prot, lig


def new_selection(lines):
    """The repaired expression: a counter over atom records, which is the atom index."""
    prot, lig, k = [], [], 0
    for ln in lines:
        if not ln.startswith(("ATOM", "HETATM")):
            continue
        resn = ln[17:20].strip()
        if resn in STD:
            prot.append(k)
        elif resn not in SOLV:
            lig.append(k)
        k += 1
    return prot, lig


def kind_of(lines, idx):
    """Which block the coordinate at this index actually belongs to."""
    kinds = []
    for ln in lines:
        if not ln.startswith(("ATOM", "HETATM")):
            continue
        resn = ln[17:20].strip()
        kinds.append("protein" if resn in STD else ("water" if resn in SOLV else "ligand"))
    return kinds[idx] if idx < len(kinds) else "OFF THE END"


cases = {}
for order in (["protein", "water", "ligand"], ["protein", "ligand", "water"]):
    label = " ".join(order)
    lines = build_pdb(order)
    n_atoms = N_PROT + N_LIG + N_WATER
    n_nonatom = sum(1 for ln in lines if not ln.startswith(("ATOM", "HETATM")))
    old_prot, old_lig = old_selection(lines)
    new_prot, new_lig = new_selection(lines)

    print()
    print(f"  --- blocks in the order: {label} ---")
    print(f"  {len(lines)} lines, {n_atoms} atom records, {n_nonatom} non-atom records "
          f"(CRYST1 and {len(order)} TER)")
    print(f"  old selection: {len(old_prot)} protein indices, {len(old_lig)} ligand indices")

    # what the old indices actually point at
    confusion = {}
    for name, sel in (("protein", old_prot), ("ligand", old_lig)):
        got = [kind_of(lines, i) for i in sel]
        counts = {k: got.count(k) for k in
                  ("protein", "water", "ligand", "OFF THE END") if got.count(k)}
        confusion[name] = counts
        print(f"    the {len(sel)} indices selected as {name} point at: {counts}")

    xyz = np.zeros((n_atoms, 3))
    raised = None
    try:
        _ = xyz[old_lig]
        _ = xyz[old_prot]
    except IndexError as exc:
        raised = str(exc) or "IndexError"
        print(f"    indexing the {n_atoms}-atom coordinate array raises: IndexError: {raised}")
    if raised is None:
        print(f"    no exception is raised, and the misassignment above is silent")

    print(f"  new selection: protein {len(new_prot)}, ligand {len(new_lig)}, "
          f"max index {max(new_prot + new_lig)} of {n_atoms - 1}, "
          f"ligand atoms {len(new_lig)} (true {N_LIG})")
    good = (max(new_prot + new_lig) < n_atoms and len(new_lig) == N_LIG
            and all(kind_of(lines, i) == "ligand" for i in new_lig))
    print(f"    every ligand index points at a ligand atom: {good}")

    cases[label] = {
        "n_atoms": n_atoms,
        "old_selection_size": [len(old_prot), len(old_lig)],
        "what_the_old_indices_point_at": confusion,
        "old_runtime_error": raised,
        "new_ligand_atoms": len(new_lig),
        "new_selection_correct": good,
    }

print()
print("  The order run_md_allatom.py writes is protein, water, ligand - the ligand is last.  So")
print("  the first version does not merely misassign: it indexes past the end of the array.")

findings["selection"] = cases

print()
print("=" * 92)
print("2. Lennard-Jones: sigma against sigma * 2**(1/6)")
print("=" * 92)

sigma = SIGMA["C"]
eps = EPS["C"]
sigma_wrong = sigma * 2 ** (1 / 6)
print(f"  carbon: sigma {sigma} A, epsilon {eps} kcal/mol, minimum position "
      f"{sigma * 2 ** (1 / 6):.3f} A")
print(f"  the wrong form passes {sigma_wrong:.3f} A where sigma is required, so its minimum")
print(f"  sits at {sigma_wrong * 2 ** (1 / 6):.3f} A instead")
print()
print(f"  {'r (A)':>8s} {'correct (kcal/mol)':>20s} {'sigma*2^(1/6)':>16s} {'difference':>12s}")
rows = []
for r in (3.4, 3.6, 3.8, 4.0, 4.28, 4.6, 5.0):
    good = 4 * eps * ((sigma / r) ** 12 - (sigma / r) ** 6)
    bad = 4 * eps * ((sigma_wrong / r) ** 12 - (sigma_wrong / r) ** 6)
    rows.append({"r": r, "correct": round(float(good), 3),
                 "sigma_rmin": round(float(bad), 3), "diff": round(float(good - bad), 3)})
    print(f"  {r:>8.2f} {good:>20.3f} {bad:>16.3f} {good - bad:>12.3f}")

r_at_correct_min = sigma * 2 ** (1 / 6)
at_min = 4 * eps * ((sigma_wrong / r_at_correct_min) ** 12 - (sigma_wrong / r_at_correct_min) ** 6)
print()
print(f"  at the true minimum {r_at_correct_min:.3f} A the correct form gives {-eps:.3f} and the")
print(f"  wrong form gives {at_min:.3f}, i.e. it is not the same potential")

findings["lennard_jones"] = {
    "sigma_C": sigma, "epsilon_C": eps,
    "well_position_correct": round(float(r_at_correct_min), 3),
    "well_position_wrong": round(float(sigma_wrong * 2 ** (1 / 6)), 3),
    "energy_at_true_minimum_wrong_form": round(float(at_min), 3),
    "table": rows,
    "verdict": "quantitative",
}

print()
print("=" * 92)
print("3. The Coulomb dielectric: was 4.0 * r * 4.0 / 4.0 a no-op?")
print("=" * 92)

r_test = np.array([1.0, 2.5, 3.75, 8.0, 12.25])
old_form = r_test * 4.0 * r_test / 4.0
new_form = 1.0 * r_test * r_test
same = bool(np.array_equal(old_form, new_form))
print(f"  r values        : {r_test.tolist()}")
print(f"  old d*4.0*d/4.0 : {old_form.tolist()}")
print(f"  new slope*r*r   : {new_form.tolist()}")
print(f"  bit-for-bit identical: {same}")
print()
print("  So the original dielectric was already epsilon = r; the 4.0 cancelled.  The repair is a")
print("  edit to what the code says, not to what it computes, and the ratio it reports is")
print("  unchanged by it.  It is still worth naming, because the ratio is not invariant to the")
print("  slope: epsilon = 4r would divide the electrostatic term by four and move the ratio by")
print("  the same factor.")

findings["dielectric"] = {
    "identical": same,
    "old_expression": "d * 4.0 * d / 4.0",
    "new_expression": "DIELECTRIC_SLOPE * r * r with slope 1.0",
    "verdict": "documentation only, numerically a no-op",
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(findings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print()
print("=" * 92)
print(f"-> {OUT}")
print("=" * 92)
