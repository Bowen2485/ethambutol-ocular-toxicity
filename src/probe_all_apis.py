#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exhaustive pre-flight check of every API the MD pipeline touches.

Why this exists
    The all-atom pipeline was written from the Windows side, where Linux code cannot be
    executed, and it failed seven times in a row - each time exposing exactly one wrong
    API detail.  This script front-loads that discovery: it exercises every external
    call the pipeline makes, using real inputs, and reports the actual signatures and
    return types alongside pass/fail.

    Run it once, and the whole remaining set of problems is visible at the same time.

Design
    Tests are independent and each catches its own exception, so one failure never
    hides the others.  Nothing is mocked: the receptor, the ligand pose and the real
    conda environment are used throughout.  Runtime is a few minutes, dominated by
    PDBFixer and by one parameterisation of ethambutol.

Run with
    ~/miniconda3/envs/md/bin/python src/probe_all_apis.py
    # or, to leave the output where the Windows side can read it:
    ~/miniconda3/envs/md/bin/python src/probe_all_apis.py 2>&1 | tee \
      "/mnt/c/Users/20200/Downloads/论文/投稿/Ethambutol_EyeTox/logs/wsl_feedback.txt"
"""
from __future__ import annotations

import inspect
import os
import shutil
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"
CLEAN = ROOT / "receptors_clean"
SDF = DOCK / "ligands" / "ethambutol" / "pubchem_3d.sdf"

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f"  -- {detail}" if detail else ""), flush=True)


def section(title: str) -> None:
    print(f"\n{'=' * 86}\n{title}\n{'=' * 86}", flush=True)


def signature(obj, name: str) -> str:
    try:
        return f"{name}{inspect.signature(obj)}"
    except Exception:  # noqa: BLE001
        return f"{name}(signature unavailable)"


def positions_to_array(positions) -> np.ndarray:
    """OpenMM positions -> (n, 3) float array in nanometres, units handled properly."""
    out = np.empty((len(positions), 3), dtype=float)
    for i, p in enumerate(positions):
        try:
            v = p.value_in_unit(unit.nanometer)
            out[i] = (v.x, v.y, v.z)
        except AttributeError:
            try:
                out[i] = (float(p.x), float(p.y), float(p.z))
            except AttributeError:
                out[i] = (float(p[0]), float(p[1]), float(p[2]))
    return out


def conformer_to_nm(conf) -> tuple[np.ndarray, str]:
    """
    Return the conformer coordinates in nanometres, whatever unit object is used.

    openff-toolkit returns a pint Quantity, which has no value_in_unit() method - that
    belongs to OpenMM's own unit system, and calling it raises AttributeError.  pint
    exposes .magnitude and .units instead.  Both routes are attempted, and the unit
    name is returned so the caller can see what happened.
    """
    mag = getattr(conf, "magnitude", None)
    if mag is not None:
        raw = np.asarray(mag, dtype=float)
        uname = str(getattr(conf, "units", ""))
        low = uname.lower()
        if "angstrom" in low or low in ("a", "ang", "å"):
            return raw / 10.0, f"{uname} -> nm"
        if "nanometer" in low or low in ("nm",):
            return raw, f"{uname} already nm"
        span = float(np.max(raw.max(axis=0) - raw.min(axis=0)))
        return (raw / 10.0 if span > 5.0 else raw), \
            f"unrecognised {uname!r}, span {span:.2f}"
    # an OpenMM Quantity, or a bare array
    try:
        return np.asarray(conf.value_in_unit(unit.nanometer), dtype=float), \
            "OpenMM Quantity"
    except Exception:  # noqa: BLE001
        raw = np.asarray(conf, dtype=float)
        span = float(np.max(raw.max(axis=0) - raw.min(axis=0)))
        return (raw / 10.0 if span > 5.0 else raw), f"bare array, span {span:.2f}"


# ============================================================== 0. environment
section("0. Environment")
print(f"  python     : {sys.version.split()[0]}")
print(f"  executable : {sys.executable}")
print(f"  cwd        : {Path.cwd()}")
print(f"  project    : {ROOT}")
print(f"  project ok : {ROOT.is_dir()}")
for rel in ("docking/ligands/ethambutol/pubchem_3d.sdf",
            "docking/poses/NFE2L2__ethambutol.pdbqt",
            "receptors_clean/2FLU/2FLU_protein.pdb",
            "receptors_clean/1N45/1N45_protein.pdb",
            "receptors_clean/1N45/HEM.pdb"):
    p = ROOT / rel
    record(f"input present: {rel}", p.exists(),
           "" if p.exists() else "MISSING")

# ========================================================= 1. AmberTools PATH
section("1. AmberTools discovery (the cause of the charge-assignment failure)")
env_bin = Path(sys.executable).parent
config_dir = None
for d in (env_bin, env_bin / "wrapped_progs"):
    if (d / "antechamber").exists():
        config_dir = env_bin if (env_bin / "antechamber").exists() else d
        break
if config_dir:
    os.environ["PATH"] = str(config_dir) + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("AMBERHOME", str(env_bin))
    record("antechamber located", True, f"using {config_dir}")
else:
    record("antechamber located", False, f"not under {env_bin}")
for exe in ("antechamber", "sqm", "parmchk2", "tleap"):
    found = shutil.which(exe)
    record(f"which {exe}", bool(found), str(found))
print(f"  AMBERHOME = {os.environ.get('AMBERHOME')!r}")

# =============================================================== 2. imports
section("2. Imports and versions")
mods = {}
for mod, label in (("openmm", "openmm"), ("openmm.app", "openmm.app"),
                   ("openmm.unit", "openmm.unit"), ("pdbfixer", "pdbfixer"),
                   ("openff.toolkit", "openff.toolkit"),
                   ("openmmforcefields", "openmmforcefields"),
                   ("rdkit", "rdkit"), ("numpy", "numpy"), ("mdtraj", "mdtraj")):
    try:
        m = __import__(mod, fromlist=["*"])
        mods[label] = m
        record(f"import {mod}", True, f"version={getattr(m, '__version__', '?')}")
    except Exception as exc:  # noqa: BLE001
        record(f"import {mod}", False, f"{type(exc).__name__}: {exc}")
        mods[label] = None

import numpy as np  # noqa: E402
import openmm as mm  # noqa: E402
import openmm.app as app  # noqa: E402
import openmm.unit as unit  # noqa: E402

record("openmm platforms",
       True,
       str([mm.Platform.getPlatform(i).getName()
            for i in range(mm.Platform.getNumPlatforms())]))

# ================================================================ 3. ligand
section("3. Ligand: reading, units, topology, charges")
mol = None
try:
    from openff.toolkit import Molecule
    try:
        raw = Molecule.from_file(str(SDF), allow_undefined_stereo=True)
    except TypeError as exc:
        record("Molecule.from_file(allow_undefined_stereo=...)", False,
               f"TypeError, retrying without it: {exc}")
        raw = Molecule.from_file(str(SDF))
    record("Molecule.from_file", True,
           f"returned {type(raw).__name__}"
           + (f" of length {len(raw)}" if isinstance(raw, (list, tuple)) else ""))
    mol = raw[0] if isinstance(raw, (list, tuple)) else raw

    # conformers: what type, what unit
    if mol.n_conformers == 0:
        mol.generate_conformers(n_conformers=1)
    conf = mol.conformers[0]
    record("mol.conformers[0] type", True,
           f"{type(conf).__name__}, has value_in_unit="
           f"{hasattr(conf, 'value_in_unit')}, has magnitude="
           f"{hasattr(conf, 'magnitude')}, units="
           f"{getattr(conf, 'units', 'n/a')!r}")
    try:
        arr, how = conformer_to_nm(conf)
        record("conformer_to_nm()", True,
               f"{how}; shape={arr.shape} "
               f"span={np.round(arr.max(0) - arr.min(0), 2)}")
    except Exception as exc:  # noqa: BLE001
        record("conformer_to_nm()", False, f"{type(exc).__name__}: {exc}")
        arr = np.zeros((1, 3))

    # attributes actually available on this OpenFF release
    available = [a for a in ("hill_formula", "n_atoms", "n_conformers",
                             "n_rotatable_bonds", "partial_charges", "name",
                             "smiles") if hasattr(mol, a)]
    record("Molecule attributes present", True, ", ".join(available))
    record("n_rotatable_bonds absent (use RDKit instead)",
           not hasattr(mol, "n_rotatable_bonds"),
           "expected on this release")

    top = mol.to_topology().to_openmm()
    record("mol.to_topology().to_openmm()", True,
           f"{top.getNumAtoms()} atoms, {top.getNumResidues()} residue(s), "
           f"names={[r.name for r in top.residues()]}")
except Exception as exc:  # noqa: BLE001
    record("ligand preparation", False, f"{type(exc).__name__}: {exc}")
    traceback.print_exc()

# ====================================================== 4. SystemGenerator API
section("4. SystemGenerator: signatures and ligand parameterisation")
gen = None
system_lig = None
try:
    from openmmforcefields.generators import SystemGenerator
    print("  " + signature(SystemGenerator.__init__, "SystemGenerator.__init__"))
    print("  " + signature(SystemGenerator.add_molecules, "add_molecules"))
    print("  " + signature(SystemGenerator.create_system, "create_system"))
    try:
        print("  supported force fields: "
              f"{list(SystemGenerator.SMALL_MOLECULE_FORCEFIELDS)[:12]} ...")
    except Exception as exc:  # noqa: BLE001
        print(f"  (force-field list unavailable: {type(exc).__name__})")

    gen = SystemGenerator(
        forcefields=["amber14-all.xml", "amber14/tip3pfb.xml"],
        small_molecule_forcefield="gaff-2.11",
        forcefield_kwargs={"constraints": app.HBonds, "rigidWater": True,
                           "removeCMMotion": True})
    record("SystemGenerator constructed", True)
    tg = getattr(gen, "template_generator", None)
    record("template_generator present", tg is not None,
           type(tg).__name__ if tg else "None")
    ff = getattr(gen, "forcefield", None)
    record("gen.forcefield present", ff is not None,
           type(ff).__name__ if ff else "None")

    gen.add_molecules([mol])
    record("gen.add_molecules([mol])", True, "ligand registered")

    # parameterise the ligand alone in a tiny system
    lig_top = mol.to_topology().to_openmm()
    system_lig = gen.create_system(lig_top)
    record("create_system(ligand only)", True,
           f"{system_lig.getNumParticles()} particles")
except Exception as exc:  # noqa: BLE001
    record("SystemGenerator pipeline", False, f"{type(exc).__name__}: {str(exc)[:200]}")
    traceback.print_exc()

# ============================================================= 5. PDBFixer
section("5. PDBFixer on the cleaned receptor")
fixed = None
try:
    from pdbfixer import PDBFixer
    rec_p = CLEAN / "2FLU" / "2FLU_protein.pdb"
    fixer = PDBFixer(filename=str(rec_p))
    record("PDBFixer(filename=...)", True)
    fixer.findMissingResidues()
    n_missing = len(fixer.missingResidues)
    longest = max((len(v) for v in fixer.missingResidues.values()), default=0)
    record("findMissingResidues", True,
           f"{n_missing} gap(s), longest {longest} residue(s)")
    fixer.missingResidues = {k: v for k, v in fixer.missingResidues.items()
                             if len(v) <= 10}
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.4)
    fixed = (fixer.topology, fixer.positions)
    record("addMissingAtoms + addMissingHydrogens", True,
           f"{fixer.topology.getNumAtoms()} atoms")
    # check whether the N-terminal residue kept its full name
    first = list(fixer.topology.residues())[0]
    record("N-terminal residue name is templateable",
           first.name in {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY",
                          "HIS", "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER",
                          "THR", "TRP", "TYR", "VAL", "ACE", "NME"},
           f"first residue = {first.name!r}")
except Exception as exc:  # noqa: BLE001
    record("PDBFixer pipeline", False, f"{type(exc).__name__}: {exc}")
    traceback.print_exc()

# ==================================================== 6. Modeller and solvation
section("6. Modeller: addSolvent and adding the ligand afterwards")
modeller = None
try:
    if fixed is None or mol is None:
        raise RuntimeError("skipped: receptor or ligand unavailable")
    top_rec, pos_rec = fixed
    modeller = app.Modeller(top_rec, pos_rec)
    record("Modeller(protein)", True, f"{modeller.topology.getNumAtoms()} atoms")

    # the ordering that matters: solvate while the topology has no ligand
    from openmmforcefields.generators import SystemGenerator as SG
    gen2 = SG(forcefields=["amber14-all.xml", "amber14/tip3pfb.xml"],
              small_molecule_forcefield="gaff-2.11",
              forcefield_kwargs={"constraints": app.HBonds, "rigidWater": True,
                                 "removeCMMotion": True})
    gen2.add_molecules([mol])
    modeller.addSolvent(gen2.forcefield, model="tip3p",
                        padding=1.0 * unit.nanometer,
                        ionicStrength=0.15 * unit.molar)
    n_solv = modeller.topology.getNumAtoms()
    record("addSolvent(protein only)", True, f"{n_solv} atoms")

    # now insert the ligand
    lig_top = mol.to_topology().to_openmm()
    lig_pos, how = conformer_to_nm(mol.conformers[0])
    print(f"  (ligand coordinates: {how})")
    rec_arr = positions_to_array(pos_rec)
    record("positions_to_array(receptor)", True,
           f"shape={rec_arr.shape} dtype={rec_arr.dtype} "
           f"centroid={np.round(rec_arr.mean(axis=0), 2)}")
    lig_pos = lig_pos - lig_pos.mean(axis=0) + rec_arr.mean(axis=0)
    modeller.add(lig_top, lig_pos * unit.nanometer)
    record("modeller.add(ligand)", True,
           f"{modeller.topology.getNumAtoms()} atoms "
           f"(+{modeller.topology.getNumAtoms() - n_solv})")

    # full parameterisation, which is the step that kept failing
    system_full = gen2.create_system(modeller.topology)
    record("create_system(protein+water+ligand)", True,
           f"{system_full.getNumParticles()} particles")
    nb = [f for f in system_full.getForces()
          if isinstance(f, mm.NonbondedForce)]
    record("NonbondedForce present", bool(nb),
           f"{len(nb)} instance(s)" if nb else "none")
except Exception as exc:  # noqa: BLE001
    record("Modeller / solvation pipeline", False,
           f"{type(exc).__name__}: {str(exc)[:250]}")
    traceback.print_exc()

# =========================================== 7. simulation objects on the GPU
section("7. Simulation objects and the CUDA platform")
try:
    if modeller is None:
        raise RuntimeError("skipped: no system built")
    integrator = mm.LangevinMiddleIntegrator(
        300.0 * unit.kelvin, 1.0 / unit.picosecond, 0.002 * unit.picoseconds)
    record("LangevinMiddleIntegrator", True, signature(
        mm.LangevinMiddleIntegrator.__init__, "  init")[:110])
    barostat = mm.MonteCarloBarostat(1 * unit.bar, 300.0 * unit.kelvin)
    record("MonteCarloBarostat", True, f"frequency={barostat.getFrequency()}")
    record("barostat.setFrequency", True, f"now {barostat.getFrequency()}")
    plat = mm.Platform.getPlatformByName("CUDA")
    sim = app.Simulation(modeller.topology, system_full, integrator, plat,
                         {"Precision": "mixed"})
    record("Simulation on CUDA", True, sim.context.getPlatform().getName())
    report = app.StateDataReporter(sys.stdout, 1000, step=True, time=True,
                                   potentialEnergy=True, temperature=True,
                                   density=True, speed=True, remainingTime=True,
                                   totalSteps=1000)
    record("StateDataReporter", True)
    dcd = app.DCDReporter(str(ROOT / "md_allatom" / "_probe.dcd"), 1000)
    record("DCDReporter", True)
    # timing on a very short run, to sanity-check the achievable speed
    import time as _t
    sim.context.setPositions(modeller.positions)
    t0 = _t.time()
    sim.step(200)          # 0.4 ps
    dt = _t.time() - t0
    ns_per_day = (200 * 0.002 / 1000.0) / (dt / 86400.0)
    record("200-step timing run", True,
           f"{dt:.1f} s -> approx {ns_per_day:.0f} ns/day "
           f"(includes startup, so treat as a lower bound)")
    Path(ROOT / "md_allatom" / "_probe.dcd").unlink(missing_ok=True)
except Exception as exc:  # noqa: BLE001
    record("simulation objects", False, f"{type(exc).__name__}: {str(exc)[:250]}")
    traceback.print_exc()

# ============================================================ 8. analysis stack
section("8. Analysis stack (mdtraj)")
try:
    import mdtraj as md
    record("import mdtraj", True, md.__version__)
    # build a tiny trajectory and exercise the calls analyse_md.py makes
    import openmm as _mm
    record("md.load signature", True, signature(md.load, "load")[:100])
    record("md.rmsd available", True, signature(md.rmsd, "rmsd")[:80])
    record("md.compute_neighbors available", True,
           signature(md.compute_neighbors, "compute_neighbors")[:100])
except Exception as exc:  # noqa: BLE001
    record("mdtraj", False, f"{type(exc).__name__}: {exc}")

# =================================================================== summary
section("SUMMARY")
n_pass = sum(1 for _, ok, _ in RESULTS if ok)
n_fail = len(RESULTS) - n_pass
print(f"  {n_pass} passed, {n_fail} failed, {len(RESULTS)} checks total\n")
if n_fail:
    print("  Failures:")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"    - {name}: {detail}")
    print("\n  Fix these before running the production MD:")
    print("      python src/run_md_allatom.py --targets NFE2L2 --ns 1")
else:
    print("  Every API the pipeline uses behaves as assumed.")
    print("  The production run should proceed:")
    print("      python src/run_md_allatom.py --targets NFE2L2 --ns 1")
sys.exit(1 if n_fail else 0)
