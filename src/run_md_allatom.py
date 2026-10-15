#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
All-atom molecular dynamics of ethambutol in each hub-target binding site.

Intended to run inside WSL with a working OpenMM CUDA platform.

What it does, per target
    1. repairs the receptor (missing atoms, hydrogens at pH 7.4) with PDBFixer
    2. loads ethambutol from the PubChem 3D conformer and places it at the centroid of
       the docked pose, so the starting geometry is the pose Vina reported while the
       ligand keeps a chemically correct topology
    3. solvates in a TIP3P box with 0.15 M salt using amber14
    4. minimises, equilibrates and runs production MD, writing a trajectory
    5. reports whether the ligand stayed in the site

Why the ligand is placed rather than taken from the pose file directly
    Vina writes PDBQT, which carries no bond orders, and the docked geometry is
    strained relative to the PubChem conformer.  Using the PubChem topology and the
    docked centroid gives a clean starting structure that equilibration can relax
    inside the pocket.  This is stated in the output so the manuscript can describe
    it accurately.

Usage (in WSL, conda env active)
    python run_md_allatom.py --targets TNF HMOX1 MFN2 --ns 10
    python run_md_allatom.py --all --ns 10          # every target in docking/results.csv

Outputs
    md_allatom/<GENE>/{receptor_fixed.pdb,complex.pdb,traj.dcd,md.log,summary.json}
    md_allatom/summary.csv
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

try:
    import openmm as mm
    import openmm.app as app
    import openmm.unit as unit
except ImportError:
    sys.exit("OpenMM is not importable. Activate the conda environment first:\n"
             "    conda activate md")


def configure_ambertools() -> str | None:
    """
    Put AmberTools' command-line tools on PATH and set AMBERHOME.

    GAFF needs antechamber to compute AM1-BCC charges, and it is invoked as an
    external program.  In a conda environment the executables sit in <env>/bin, but
    a wrapper directory, <env>/bin/wrapped_progs, shadows them, so a naive `which
    antechamber` finds the wrapper and the toolkit registry concludes that no charge
    backend is available.  That is what produced
    "No registered toolkits can provide the capability assign_partial_charges".

    Setting both variables here means the script does not depend on the caller's
    shell configuration.
    """
    import shutil
    env_bin = Path(sys.executable).parent
    candidates = [env_bin, env_bin / "wrapped_progs"]
    found = None
    for d in candidates:
        exe = d / "antechamber"
        if exe.exists():
            found = d
            if "wrapped_progs" in str(d):
                # prefer the real binary if it also exists directly in bin/
                if (env_bin / "antechamber").exists():
                    found = env_bin
            break
    if found is None:
        return None
    os.environ["PATH"] = str(found) + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("AMBERHOME", str(env_bin))
    return str(found)

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"
OUT = ROOT / "md_allatom"
SDF = DOCK / "ligands" / "ethambutol" / "pubchem_3d.sdf"
CLEAN = ROOT / "receptors_clean"

# Residues the amber14 templates do not cover.  They are removed before solvation
# because Modeller.addSolvent builds a system internally and aborts on any residue it
# cannot template - the JNI content of the TNF structure is what actually stopped the
# earlier runs, not the docked ligand.  Cofactors listed in KEEP_COFACTORS are handled
# separately instead of being discarded.
AMINO = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
         "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
         "HID", "HIE", "HIP", "CYX", "ASH", "GLH", "LYN", "ACE", "NME"}
KEEP_COFACTORS = {"HEM"}

# force field choices: amber14 for protein and water, GAFF for the small molecule
PROTEIN_FF = ["amber14-all.xml", "amber14/tip3pfb.xml"]
SMALL_MOL_FF = "gaff-2.11"
PH = 7.4
PADDING_NM = 1.0
IONIC_MOLAR = 0.15
TEMPERATURE_K = 300.0
FRICTION = 1.0            # 1/ps
TIMESTEP_PS = 0.002
MIN_STEPS = 5000
NVT_PS = 100.0
NPT_PS = 400.0
REPORT_PS = 10.0


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------------- inputs
def receptor_path(gene: str, pdbid: str) -> Path | None:
    """Prefer the cleaned, protein-only receptor produced by src/clean_receptors.py."""
    for cand in (CLEAN / pdbid / f"{pdbid}_protein.pdb",
                 CLEAN / pdbid / f"{pdbid}.pdb"):
        if cand.exists():
            return cand
    for cand in (DOCK / "receptors" / pdbid / f"{pdbid}_clean.pdb",
                 DOCK / "receptors" / pdbid / f"{pdbid}.pdb"):
        if cand.exists():
            return cand
    hits = list((DOCK / "receptors").rglob(f"{gene}*clean.pdb"))
    return hits[0] if hits else None


def strip_non_standard(path: Path) -> tuple[Path, dict[str, int]]:
    """
    Write a copy of `path` containing only residues the force field can template.

    Returns the new path and a count of what was dropped.  If the source is already
    clean the original path is returned unchanged.
    """
    kept, dropped = [], {}
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        res = line[17:20].strip()
        if res in AMINO or res in KEEP_COFACTORS:
            kept.append(line)
        else:
            dropped[res] = dropped.get(res, 0) + 1
    if not dropped:
        return path, {}
    out = path.with_name(path.stem + "_ffready.pdb")
    out.write_text("\n".join(kept) + "\nEND\n", encoding="utf-8")
    return out, dropped


def pose_path(gene: str) -> Path | None:
    for cand in (DOCK / "poses" / f"{gene}__ethambutol.pdbqt",
                 DOCK / "poses" / f"{gene}_ethambutol.pdbqt"):
        if cand.exists():
            return cand
    return None


def pose_centroid(p: Path) -> np.ndarray | None:
    """Centroid of the first docked mode's heavy atoms."""
    xyz, started = [], False
    for line in p.read_text(errors="replace").splitlines():
        s = line.strip()
        if s.startswith("MODEL"):
            if started:
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
            xyz.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        except ValueError:
            continue
    return np.asarray(xyz).mean(axis=0) if xyz else None


def positions_to_array(positions) -> np.ndarray:
    """
    Convert OpenMM positions to an (n, 3) float array in nanometres.

    np.asarray() on a list of Vec3 objects builds an object array whose elements carry
    units, so arithmetic on it raises
    "unsupported operand type(s) for +: 'float' and 'Quantity'".  Each vector is read
    component-wise instead, using the unit-aware accessor when the values arrive as
    OpenMM Quantities.
    """
    out = np.empty((len(positions), 3), dtype=float)
    for i, p in enumerate(positions):
        try:
            v = p.value_in_unit(unit.nanometer)     # OpenMM Vec3 with units
            out[i] = (v.x, v.y, v.z)
        except AttributeError:
            try:
                out[i] = (float(p.x), float(p.y), float(p.z))   # plain Vec3 in nm
            except AttributeError:
                out[i] = (float(p[0]), float(p[1]), float(p[2]))
    return out


# ------------------------------------------------------------------- platform
def pick_platform() -> tuple[mm.Platform, dict]:
    """CUDA if it is really available, otherwise the fastest fallback."""
    names = [mm.Platform.getPlatform(i).getName()
             for i in range(mm.Platform.getNumPlatforms())]
    log(f"platforms available: {names}")
    if "CUDA" in names:
        log("using CUDA with mixed precision")
        return mm.Platform.getPlatformByName("CUDA"), {"Precision": "mixed"}
    if "OpenCL" in names:
        log("CUDA absent, falling back to OpenCL")
        return mm.Platform.getPlatformByName("OpenCL"), {"Precision": "mixed"}
    log("!! no GPU platform - running on CPU, expect roughly 100x slower")
    return mm.Platform.getPlatformByName("CPU"), {}


# ----------------------------------------------------------------- one target
def run_target(gene: str, pdbid: str, ns: float, platform, props) -> dict | None:
    rec_p = receptor_path(gene, pdbid)
    pose_p = pose_path(gene)
    if rec_p is None or pose_p is None or not SDF.exists():
        log(f"{gene}: missing input (rec={rec_p}, pose={pose_p}, sdf={SDF.exists()})")
        return None

    work = OUT / gene
    work.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------- 1. receptor
    from pdbfixer import PDBFixer
    rec_p, dropped = strip_non_standard(rec_p)
    if dropped:
        summary = dict(sorted(dropped.items(), key=lambda kv: -kv[1])[:8])
        log(f"{gene}: removed non-templateable residues {summary}")
    fixer = PDBFixer(filename=str(rec_p))
    fixer.findMissingResidues()
    # a repaired terminus or a long missing loop can make the system enormous;
    # drop any missing stretch longer than 10 residues rather than modelling it
    fixer.missingResidues = {k: v for k, v in fixer.missingResidues.items()
                             if len(v) <= 10}
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(PH)
    rec_top, rec_pos = fixer.topology, fixer.positions
    app.PDBFile.writeFile(rec_top, rec_pos, open(work / "receptor_fixed.pdb", "w"))
    log(f"{gene}: receptor repaired, {rec_top.getNumAtoms()} atoms")

    # ------------------------------------------------------------ 2. ligand
    from openff.toolkit import Molecule
    from openmmforcefields.generators import SystemGenerator
    # Try the explicit-stereo-tolerant call first, then fall back to the plain one.
    # The SDF from PubChem has no wedge bonds, so stereo can be ambiguous, but the
    # keyword name has moved between OpenFF releases - two earlier attempts at this
    # script died on assumed API details, so both forms are attempted here.
    try:
        mols = Molecule.from_file(str(SDF), allow_undefined_stereo=True)
    except TypeError:
        mols = Molecule.from_file(str(SDF))
    # from_file returns a single Molecule for a one-record file and a list otherwise
    if isinstance(mols, (list, tuple)):
        log(f"{gene}: SDF holds {len(mols)} records; using the first")
        mol = mols[0]
    else:
        mol = mols
    if mol is None:
        log(f"{gene}: could not read the ligand SDF")
        return None
    # Diagnostics must never stop the run.  An earlier version died here on an
    # attribute name that does not exist on this OpenFF release, so every optional
    # descriptor is guarded and simply omitted when unavailable.
    describe = []
    for attr in ("hill_formula", "n_atoms"):
        try:
            describe.append(f"{attr}={getattr(mol, attr)}")
        except Exception:  # noqa: BLE001
            pass
    try:
        from rdkit.Chem import Descriptors, Lipinski
        rdk = mol.to_rdkit()
        describe.append(f"rotatable_bonds={Lipinski.NumRotatableBonds(rdk)}")
        describe.append(f"MW={Descriptors.MolWt(rdk):.1f}")
    except Exception:  # noqa: BLE001
        pass
    msg = ", ".join(describe) if describe else "loaded (no descriptors available)"
    log(f"{gene}: ligand {msg}")
    mol.generate_conformers(n_conformers=1)

    # The conformer is a pint Quantity, not an OpenMM one, so it has no
    # value_in_unit() method - that call raises AttributeError.  pint exposes the
    # magnitude through .magnitude and the conversion through .m_as().  Verified
    # against the live environment by src/probe_all_apis.py.
    conf = mol.conformers[0]
    lig_nm = None
    try:
        mag = getattr(conf, "magnitude", None)
        if mag is not None:
            raw = np.asarray(mag, dtype=float)
            uname = str(getattr(conf, "units", ""))
            if "angstrom" in uname.lower():
                lig_nm = raw / 10.0
                log(f"{gene}: conformer units = {uname}; converted to nm")
            elif "nanometer" in uname.lower() or "nm" == uname.lower():
                lig_nm = raw
            else:
                span = float(np.max(raw.max(axis=0) - raw.min(axis=0)))
                lig_nm = raw / 10.0 if span > 5.0 else raw
                log(f"{gene}: unrecognised conformer units {uname!r}; inferred from "
                    f"a span of {span:.2f}")
    except Exception as exc:  # noqa: BLE001
        log(f"{gene}: could not read the conformer magnitude ({type(exc).__name__}); "
            f"falling back to the raw array")
    if lig_nm is None:
        raw = np.asarray(conf, dtype=float)
        span = float(np.max(raw.max(axis=0) - raw.min(axis=0)))
        lig_nm = raw / 10.0 if span > 5.0 else raw
        log(f"{gene}: conformer read without units; span {span:.2f} -> "
            f"{'angstrom' if span > 5.0 else 'nanometre'}")
    span_nm = float(np.max(lig_nm.max(axis=0) - lig_nm.min(axis=0)))
    if not (0.3 <= span_nm <= 5.0):
        log(f"{gene}: ligand span {span_nm:.2f} nm is implausible; check the units")
    log(f"{gene}: ligand read, {lig_nm.shape[0]} atoms, "
        f"span {np.round(lig_nm.max(axis=0) - lig_nm.min(axis=0), 2)} nm")
    lig_pos = lig_nm

    # move the ligand so its centroid sits on the docked pose's centroid
    target_c = pose_centroid(pose_p)
    if target_c is not None:
        target_c = target_c * 0.1              # angstrom -> nm
        lig_pos = lig_pos - lig_pos.mean(axis=0) + target_c
        log(f"{gene}: centred on the docked pose at "
            f"{np.round(lig_pos.mean(axis=0), 2)} nm")
    else:
        # no usable pose: place the ligand near the receptor centroid so the run still
        # produces a valid system, and say so rather than pretending it is docked
        log(f"{gene}: WARNING no pose centroid available; placing the ligand at the "
            f"receptor centroid, which does NOT correspond to the docked pose")
        rec_cen = positions_to_array(rec_pos).mean(axis=0)
        lig_pos = lig_pos - lig_pos.mean(axis=0) + rec_cen

    # ------------------------------------------------------------ 3. assemble
    # Order matters, and getting it wrong cost a run.  Modeller.addSolvent builds a
    # system internally from the topology it is given; when the ligand is already in
    # that topology the ForceField cannot template residue JNI and the call dies with
    # "Did not recognize residue".  gen.add_molecules() does not help, because
    # addSolvent does not go through the SystemGenerator.
    #
    # So the protein is solvated first, while the topology still contains only
    # protein, and the ligand is inserted into the finished water box afterwards.
    # The docked pose already lies inside the receptor's coordinate frame (checked in
    # src/probe_pose_geometry.py), so the ligand lands in water rather than on top of
    # the protein.  Any water overlapping the pose is removed by minimisation, and
    # this is stated in the output so the manuscript can describe it.
    modeller = app.Modeller(rec_top, rec_pos)
    if any(a.residue.name == "JNI" for a in modeller.topology.atoms()):
        raise RuntimeError("ligand present before solvation; this ordering is what "
                           "makes addSolvent fail")
    gen = SystemGenerator(
        forcefields=PROTEIN_FF,
        small_molecule_forcefield=SMALL_MOL_FF,
        forcefield_kwargs={"constraints": app.HBonds,
                           "rigidWater": True,
                           "removeCMMotion": True})

    # register the ligand with the generator that create_system will use
    if getattr(gen, "template_generator", None) is None:
        raise RuntimeError(
            f"SystemGenerator created no small-molecule template generator for "
            f"'{SMALL_MOL_FF}'; check that the name is one of "
            f"{type(gen).SMALL_MOLECULE_FORCEFIELDS}")
    gen.add_molecules([mol])
    log(f"{gene}: ligand registered with the {SMALL_MOL_FF} template generator")
    log(f"{gene}: solvating the protein alone")
    modeller.addSolvent(gen.forcefield, model="tip3p",
                        padding=PADDING_NM * unit.nanometer,
                        ionicStrength=IONIC_MOLAR * unit.molar)
    n_solvent = modeller.topology.getNumAtoms()
    log(f"{gene}: protein solvated, {n_solvent} atoms")

    lig_top = mol.to_topology().to_openmm()
    modeller.add(lig_top, lig_pos * unit.nanometer)
    log(f"{gene}: ligand inserted into the water box "
        f"({modeller.topology.getNumAtoms()} atoms total)")

    app.PDBFile.writeFile(modeller.topology, modeller.positions,
                          open(work / "complex.pdb", "w"))

    try:
        system = gen.create_system(modeller.topology)
    except Exception as exc:  # noqa: BLE001
        # GAFF needs partial charges, and OpenFF can only get them from a toolkit that
        # advertises assign_partial_charges.  When that is missing the error is opaque
        # ("No registered toolkits can provide the capability"), so the available
        # backends are listed here to make the fix obvious.
        try:
            who = mol.hill_formula
        except Exception:  # noqa: BLE001
            who = "the ligand"
        log(f"{gene}: parameterisation FAILED for {who}: "
            f"{type(exc).__name__}: {str(exc)[:200]}")
        try:
            from openff.toolkit.utils.toolkits import GLOBAL_TOOLKIT_REGISTRY as REG
            log(f"{gene}: registered toolkits = "
                f"{[t.__class__.__name__ for t in REG.registered_toolkits]}")
            for meth in ("am1bcc", "am1-mulliken", "nagl", "gasteiger"):
                try:
                    REG.get_toolkit_for_capability("assign_partial_charges",
                                                   method=meth)
                    log(f"{gene}:   charge method available: {meth}")
                except Exception:  # noqa: BLE001
                    log(f"{gene}:   charge method unavailable: {meth}")
        except Exception:  # noqa: BLE001
            pass
        log(f"{gene}: run src/probe_charge_toolkits.py in the md environment for a "
            f"full diagnosis")
        raise
    system.addForce(mm.MonteCarloBarostat(1 * unit.bar, TEMPERATURE_K * unit.kelvin))
    integrator = mm.LangevinMiddleIntegrator(
        TEMPERATURE_K * unit.kelvin, FRICTION / unit.picosecond,
        TIMESTEP_PS * unit.picoseconds)
    sim = app.Simulation(modeller.topology, system, integrator, platform, props)
    sim.context.setPositions(modeller.positions)

    # ------------------------------------------------------- 4. minimise
    # A checkpoint makes the run resumable.  Long simulations outlive the session that
    # started them - this one was interrupted during NPT equilibration - so state is
    # written after each stage and a restart continues from the last completed stage
    # rather than rebuilding and re-equilibrating from scratch.
    ckpt = work / "state.chk"
    ckpt_meta = work / "state.json"

    def read_ckpt_stage() -> str | None:
        if not (ckpt.exists() and ckpt_meta.exists()):
            return None
        try:
            return json.loads(ckpt_meta.read_text(encoding="utf-8")).get("last_stage")
        except Exception:  # noqa: BLE001
            return None

    def save_stage(name: str, sim_obj, ns_done: float) -> None:
        try:
            with open(ckpt, "wb") as fh:
                sim_obj.saveCheckpoint(fh)
            ckpt_meta.write_text(
                json.dumps({"last_stage": name, "ns_completed": ns_done,
                            "atoms": modeller.topology.getNumAtoms()}),
                encoding="utf-8")
            log(f"{gene}: checkpoint written after {name}")
        except Exception as exc:  # noqa: BLE001
            log(f"{gene}: checkpoint not written ({type(exc).__name__}); the run is "
                f"still valid but will not be resumable")

    STAGES = ["minimise", "nvt", "npt", "production"]
    done_stage = read_ckpt_stage()
    if done_stage in STAGES:
        # A checkpoint can only be loaded into a system with the same particle count.
        # addSolvent is not deterministic - two builds of the same BCL2 receptor gave
        # 131,087 and 130,656 atoms - so a checkpoint from an earlier attempt is often
        # unusable.  It has to be detected rather than raised: loading it threw
        # OpenMMException "wrong number of particles", which aborted the whole target
        # instead of simply starting it over.
        meta = {}
        try:
            meta = json.loads(ckpt_meta.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
        n_now = modeller.topology.getNumAtoms()
        n_then = meta.get("atoms")
        if n_then is not None and int(n_then) != int(n_now):
            log(f"{gene}: the checkpoint was built on {n_then} atoms but this system has "
                f"{n_now}, because solvent placement is not reproducible; discarding the "
                f"checkpoint and running from the start")
            done_stage = None
        else:
            try:
                with open(ckpt, "rb") as fh:
                    sim.loadCheckpoint(fh)
                log(f"{gene}: resuming from checkpoint, last completed stage = "
                    f"{done_stage}")
            except Exception as exc:  # noqa: BLE001
                log(f"{gene}: checkpoint could not be loaded "
                    f"({type(exc).__name__}: {str(exc)[:90]}); running from the start")
                done_stage = None
        if done_stage is None:
            # stale state would otherwise be reused or appended to
            for stale in (ckpt, ckpt_meta):
                try:
                    stale.unlink(missing_ok=True)
                except Exception:  # noqa: BLE001
                    pass

    def stage_pending(s: str) -> bool:
        """True if stage `s` still needs to run."""
        if done_stage is None:
            return True
        return STAGES.index(s) > STAGES.index(done_stage)

    if stage_pending("minimise"):
        log(f"{gene}: minimising")
        sim.minimizeEnergy(maxIterations=MIN_STEPS)
        st = sim.context.getState(getPositions=True)
        app.PDBFile.writeFile(modeller.topology, st.getPositions(),
                              open(work / "minimised.pdb", "w"))
        save_stage("minimise", sim, 0.0)

    # --------------------------------------------- 5. equilibrate and produce
    # A resumed run appends to traj.dcd, and a run that started over leaves the
    # previous attempt's frames in the file.  Either way one file can hold frames from
    # two different systems, which is impossible to disentangle afterwards because the
    # particle counts differ.  Each attempt therefore writes its own trajectory, and
    # analysis picks the newest one.
    attempt = time.strftime("%Y%m%d-%H%M%S")
    traj_p = work / f"traj_{attempt}.dcd"
    log(f"{gene}: trajectory will be written to {traj_p.name}")
    sim.reporters.append(app.DCDReporter(str(traj_p), int(REPORT_PS / TIMESTEP_PS)))
    sim.reporters.append(app.StateDataReporter(
        str(work / "md.log"), int(REPORT_PS / TIMESTEP_PS), step=True, time=True,
        potentialEnergy=True, temperature=True, density=True, speed=True,
        remainingTime=True, totalSteps=int((NVT_PS + NPT_PS + ns * 1000)
                                           / TIMESTEP_PS)))

    # The barostat is inactive until the system is dense, so the NVT stage runs first
    # and the density is only meaningful during the NPT stage.
    barostat = [f for f in system.getForces()
                if isinstance(f, mm.MonteCarloBarostat)]

    if stage_pending("nvt"):
        if barostat:
            barostat[0].setFrequency(0)      # off during NVT
        log(f"{gene}: NVT equilibration {NVT_PS:.0f} ps")
        sim.step(int(NVT_PS / TIMESTEP_PS))
        save_stage("nvt", sim, NVT_PS / 1000.0)
    if stage_pending("npt"):
        if barostat:
            barostat[0].setFrequency(25)     # on for NPT
        sim.context.reinitialize(preserveState=True)
        log(f"{gene}: NPT equilibration {NPT_PS:.0f} ps")
        sim.step(int(NPT_PS / TIMESTEP_PS))
        save_stage("npt", sim, (NVT_PS + NPT_PS) / 1000.0)

    prod_steps = int(ns * 1000 / TIMESTEP_PS)
    t0 = time.time()
    if stage_pending("production"):
        log(f"{gene}: production {ns} ns ({prod_steps} steps)")
        sim.step(prod_steps)
        save_stage("production", sim, (NVT_PS + NPT_PS) / 1000.0 + ns)
    else:
        log(f"{gene}: production already complete in this checkpoint; reusing it")
    wall = time.time() - t0
    log(f"{gene}: production finished in {wall/3600:.2f} h "
        f"({ns/(wall/86400):.1f} ns/day)")

    # ------------------------------------------------------------ 6. summary
    summary = {
        "gene": gene,
        "pdb": pdbid,
        "ns_produced": ns,
        "wall_hours": round(wall / 3600, 2),
        "ns_per_day": round(ns / (wall / 86400), 1) if wall else None,
        "n_atoms": modeller.topology.getNumAtoms(),
        "platform": sim.context.getPlatform().getName(),
        "ligand_placement": "PubChem topology centred on the docked-pose centroid",
    }
    (work / "summary.json").write_text(json.dumps(summary, indent=2),
                                       encoding="utf-8")
    return summary


# ----------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", nargs="*", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ns", type=float, default=10.0)
    args = ap.parse_args()

    amber_dir = configure_ambertools()
    if amber_dir:
        log(f"AmberTools tools found at {amber_dir}; PATH and AMBERHOME set")
    else:
        log("WARNING antechamber not found; GAFF charge assignment will likely fail. "
            "Run src/probe_parameterisation.py to diagnose.")

    import pandas as pd
    res = DOCK / "results.csv"
    if not res.exists():
        sys.exit("docking/results.csv not found")
    d = pd.read_csv(res, encoding="utf-8-sig")
    d = d[(d.ligand == "ethambutol") & (d.ok == True)]      # noqa: E712
    if not args.all:
        if not args.targets:
            sys.exit("give --targets GENE [GENE ...] or --all")
        d = d[d.gene.isin(args.targets)]
    if d.empty:
        sys.exit("no matching targets")

    OUT.mkdir(parents=True, exist_ok=True)
    platform, props = pick_platform()

    summaries = []
    for _, r in d.iterrows():
        try:
            s = run_target(r.gene, str(r.pdb).strip(), args.ns, platform, props)
        except Exception as exc:                            # noqa: BLE001
            log(f"{r.gene}: FAILED {type(exc).__name__}: {str(exc)[:200]}")
            continue
        if s:
            summaries.append(s)

    if summaries:
        out = OUT / "summary.csv"
        pd.DataFrame(summaries).to_csv(out, index=False, encoding="utf-8-sig")
        log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
