#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Two experiments to get the ligand parameterised, now that the toolchain mismatch is
understood.

Diagnosis so far:
  * antechamber, sqm, parmchk2 and tleap are not on PATH and AMBERHOME is unset
  * the OpenFF toolkit registry raises AttributeError on
    list_available_toolkits_for_capability, which openmmforcefields 0.16.0 calls, so
    GAFF cannot reach any charge backend
  * the openff-nagl packages are installed and importable, but unusable through that
    broken path

Experiment A: is antechamber present anywhere in the environment?
    If it is, adding its directory to PATH restores AM1-BCC and GAFF works.

Experiment B: does the SMIRNOFF generator work?
    GAFFTemplateGenerator and SMIRNOFFTemplateGenerator derive from the same base but
    take different routes to parameters.  If the SMIRNOFF route survives, the ligand
    can be parameterised with openff-2.x and no external charge engine.

Run with:
    ~/miniconda3/envs/md/bin/python src/probe_parameterisation.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import openmm as mm

ENV = Path(sys.executable).parent.parent
print("=" * 84)
print("0. Which interpreter and environment")
print("=" * 84)
print(f"  python : {sys.executable}")
print(f"  env    : {ENV}")
print(f"  PATH entries containing 'amber': "
      f"{[p for p in os.environ.get('PATH', '').split(os.pathsep) if 'amber' in p.lower()]}")

print()
print("=" * 84)
print("A. Search the environment for the AmberTools command-line tools")
print("=" * 84)
found = {}
for exe in ("antechamber", "sqm", "parmchk2", "tleap"):
    hits = []
    for base in (ENV, Path("/usr"), Path("/opt"), Path.home()):
        if not base.exists():
            continue
        try:
            r = subprocess.run(["find", str(base), "-name", exe, "-type", "f",
                                "-maxdepth", "8"],
                               capture_output=True, text=True, timeout=180)
            hits += [h for h in r.stdout.split() if h]
        except Exception:  # noqa: BLE001
            pass
        if hits:
            break
    found[exe] = hits[:3]
    print(f"  {exe:12s} {hits[:3] if hits else 'NOT FOUND'}")

if found.get("antechamber"):
    # prefer the real binary in bin/ over the wrapper in bin/wrapped_progs/, which is
    # what the earlier search picked up and what made the tools look absent
    real = [h for h in found["antechamber"] if "wrapped_progs" not in h]
    d = str(Path(real[0] if real else found["antechamber"][0]).parent)
    amberhome = str(Path(d))
    os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
    os.environ["AMBERHOME"] = amberhome
    print(f"\n  -> antechamber exists at {d}")
    print(f"     PATH      now starts with {d}")
    print(f"     AMBERHOME set to {amberhome}")
    for exe in ("antechamber", "sqm", "parmchk2", "tleap"):
        print(f"     which {exe:12s} -> {shutil.which(exe)}")

print()
print("=" * 84)
print("B. Does any small-molecule force field work end to end?")
print("=" * 84)
from openff.toolkit import Molecule
from openmmforcefields.generators import SystemGenerator
import openmm.app as app
import openmm.unit as unit

SDF = Path(__file__).resolve().parents[1] / "docking" / "ligands" / \
    "ethambutol" / "pubchem_3d.sdf"
try:
    mol = Molecule.from_file(str(SDF), allow_undefined_stereo=True)
    if isinstance(mol, list):
        mol = mol[0]
    mol.generate_conformers(n_conformers=1)
    print(f"  ligand loaded: {mol.n_atoms} atoms")
except Exception as exc:  # noqa: BLE001
    print(f"  ligand load failed: {type(exc).__name__}: {exc}")
    sys.exit(1)

# a one-residue topology is enough to exercise the parameterisation path
top = mol.to_topology().to_openmm()
conf = mol.conformers[0]
# the conformer is a pint Quantity, which has .magnitude/.units but no
# value_in_unit(); that method belongs to OpenMM's unit system
mag = getattr(conf, "magnitude", None)
if mag is not None:
    raw = np.asarray(mag, dtype=float)
    uname = str(getattr(conf, "units", "")).lower()
    pos = raw if ("nanometer" in uname or uname == "nm") else raw / 10.0
else:
    raw = np.asarray(conf, dtype=float)
    span = float(np.max(raw.max(axis=0) - raw.min(axis=0)))
    pos = raw / 10.0 if span > 5.0 else raw
# Vec3 lives in the openmm module, not in openmm.app - an earlier version of this
# script used app.Vec3 and died before reaching the parameterisation tests
pos = [mm.Vec3(float(p[0]), float(p[1]), float(p[2])) for p in pos] * unit.nanometer

candidates = ["gaff-2.11", "gaff-2.2.20", "openff-2.1.0", "openff-2.2.0",
              "smirnoff", "espaloma"]
print(f"  force fields to try: {candidates}\n")
working = []
for ff in candidates:
    try:
        gen = SystemGenerator(forcefields=[], small_molecule_forcefield=ff,
                             forcefield_kwargs={"constraints": None})
        gen.add_molecules([mol])
        system = gen.create_system(top)
        n = system.getNumParticles()
        working.append(ff)
        print(f"  {ff:14s} WORKS   ({n} particles)")
    except Exception as exc:  # noqa: BLE001
        first = str(exc).split("\n")[0][:110]
        print(f"  {ff:14s} failed  {type(exc).__name__}: {first}")

print()
print("=" * 84)
print("VERDICT")
print("=" * 84)
if working:
    print(f"  usable force fields: {working}")
    print(f"  -> set SMALL_MOL_FF to '{working[0]}' in src/run_md_allatom.py")
else:
    print("  none of the small-molecule force fields could parameterise the ligand.")
    print("  Remaining options:")
    print("    1. install a matching pair of openmmforcefields and openff-toolkit")
    print("       (the registry API changed between releases)")
    print("    2. get antechamber onto PATH and use GAFF with AM1-BCC")
    print("    3. build the ligand's parameters directly from RDKit, bypassing OpenFF")
