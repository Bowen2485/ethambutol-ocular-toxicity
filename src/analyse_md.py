#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse the all-atom MD trajectories and report pose stability.

Rewritten after the first version segfaulted.  Two causes were identified:

  1. memory.  A 45,000-atom system at a 10 ps report interval gives about 9,000
     frames, roughly 10 GB as float32 and more as float64.  The first version called
     md.load() on the whole file; this one streams with md.iterload() in fixed-size
     blocks and accumulates running sums, so peak memory stays flat.

  2. ligand selection.  The first version fell back to a comprehension that produced a
     float array of atom indices, and mdtraj warned it was casting float64 to int.
     The ligand is now located by residue name and cast to int64 explicitly.

Metrics reported, which are the four a reviewer will ask for:
    ligand RMSD relative to its starting pose, after aligning on the receptor
    receptor backbone RMSD, showing whether the site held its shape
    fraction of the starting ligand-receptor contacts that survive
    ligand radius of gyration, catching a ligand that falls apart rather than leaves

A pose counts as stable only if the ligand RMSD plateaus below 3 A while the contact
fraction stays above 0.4.  Anything else is reported as unstable; a ligand that drifts
away is called that, not "flexible".

Usage
    python analyse_md.py
    python analyse_md.py --genes NFE2L2 --chunk 100
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

try:
    import mdtraj as md
except ImportError:
    sys.exit("mdtraj not installed. In WSL:  conda install -c conda-forge mdtraj")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "md_allatom"
CONTACT_NM = 0.45          # 4.5 A
# collects the per-frame time course from analyse() for the summary table
SERIES: dict[str, list] = {}
SOLVENT = {"HOH", "WAT", "DOD", "TIP", "SOL", "NA", "CL", "K", "MG", "ZN", "CA",
           "MN", "FE", "CU", "NI", "SO4", "PO4", "NO3", "ACT", "EDO", "GOL"}
# Standard residue names, used to decide protein membership explicitly.  This matters:
# mdtraj reports is_protein=True for the ligand residue UNK, because UNK is in its own
# list of known residues.  Selecting on is_protein therefore classified the ligand as
# protein and found no ligand at all - diagnosed by src/probe_ligand_detection.py.
AMINO = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
         "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
         "HID", "HIE", "HIP", "CYX", "ASH", "GLH", "LYN", "ACE", "NME", "SEC",
         "PYL", "MSE"}
REPORT_PS = 10.0
TIMESTEP_PS = 0.002
# Frames written during equilibration, which must be excluded from the production
# analysis.  DCDReporter is attached before the NVT stage, so the file holds
# (NVT_PS + NPT_PS) / REPORT_PS equilibration frames ahead of production.
EQUIL_PS = 500.0
EQUIL_FRAMES = int(EQUIL_PS / REPORT_PS)


def as_1d_per_frame(x, n_frames: int, label: str) -> np.ndarray:
    """
    Return a per-frame 1-D array from whatever mdtraj hands back.

    Six separate IndexError and ValueError failures in this script came from assuming
    the shape of a return value.  Rather than reason about each one, every result of
    this kind is normalised here: scalars broadcast, (n,1) and (1,n) squeeze to (n,),
    and an unexpected shape is reported with its actual dimensions instead of raising
    something opaque.
    """
    a = np.asarray(x, dtype=float)
    if a.ndim == 0:
        return np.full(n_frames, float(a))
    a = np.squeeze(a)
    if a.ndim == 0:
        return np.full(n_frames, float(a))
    if a.ndim != 1:
        raise RuntimeError(f"{label}: expected one value per frame, got shape "
                           f"{np.shape(x)} for {n_frames} frames")
    if a.size != n_frames:
        raise RuntimeError(f"{label}: got {a.size} values for {n_frames} frames "
                           f"(shape {np.shape(x)})")
    return a


def as_pair_matrix(x, label: str) -> np.ndarray:
    """
    Return an (n_pairs, 2) int array of atom index pairs.

    The same normalisation is applied here.  compute_neighbors in particular returned
    something with an odd number of elements, which cannot be a pair list at all, so
    that function is no longer used for the contact definition.
    """
    a = np.asarray(x, dtype=np.int64)
    if a.ndim == 1:
        if a.size % 2:
            raise RuntimeError(f"{label}: {a.size} elements, an odd number, so this "
                               f"cannot be a list of atom pairs")
        a = a.reshape(-1, 2)
    if a.ndim != 2 or a.shape[1] != 2:
        raise RuntimeError(f"{label}: expected an (n, 2) pair array, got shape "
                           f"{np.shape(x)}")
    return a


def radius_of_gyration(xyz: np.ndarray) -> np.ndarray:
    """
    Radius of gyration per frame, in the same units as the input, computed directly.

    mdtraj offers compute_rg, but obtaining the ligand subset required ref[:, lig], and
    for a single-frame trajectory that index form fails inside mdtraj:
        Time: self.time[key] -> IndexError: too many indices for array
    The coordinates are therefore taken with plain numpy indexing, which is
    unambiguous, and rg = sqrt(mean(|r - r_centroid|^2)).
    """
    a = np.asarray(xyz, dtype=float)
    if a.ndim == 2:
        a = a[None, ...]
    if a.ndim != 3:
        raise RuntimeError(f"radius_of_gyration: expected (frames, atoms, 3), "
                           f"got {a.shape}")
    cen = a.mean(axis=1, keepdims=True)
    return np.sqrt(((a - cen) ** 2).sum(axis=2).mean(axis=1))


def find_groups(top, gene: str = "?"):
    """
    Return (ligand, protein, backbone) index arrays as int64.

    Protein membership is decided by an explicit residue name list, never by mdtraj's
    is_protein flag: that flag is True for UNK, which is the name OpenFF gives a ligand
    without one, so an is_protein test silently turns the ligand into protein.

    Anything that is neither solvent nor a standard residue is the ligand.  On failure
    the complete residue inventory is printed - an earlier truncated listing hid UNK
    because it sorts after TYR, and the output was misread as "no ligand in the file".
    """
    import collections

    counts = collections.Counter()
    lig, prot, bb = [], [], []
    for atom in top.atoms:
        rn = atom.residue.name.upper()
        counts[rn] += 1
        if rn in SOLVENT:
            continue
        if rn in AMINO:
            prot.append(atom.index)
            if atom.name in ("CA", "C", "N", "O"):
                bb.append(atom.index)
        else:
            lig.append(atom.index)
    if not lig:
        print(f"  {gene}: no ligand identified; the complete residue inventory is:")
        for r, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            kind = ("solvent" if r in SOLVENT else
                    "standard residue" if r in AMINO else "UNKNOWN <-- ligand?")
            print(f"      {r:6s} {n:>7,}   {kind}")
    return (np.asarray(lig, dtype=np.int64),
            np.asarray(prot, dtype=np.int64),
            np.asarray(bb, dtype=np.int64))


def newest_traj(d: Path) -> Path | None:
    """
    The newest trajectory in a target directory.

    Runs now write traj_<timestamp>.dcd, because a restarted run would otherwise append
    to a file already holding frames from a system with a different particle count.
    Older files stay on disk for reference; the newest is the one to analyse.
    """
    cands = sorted(d.glob("traj*.dcd"), key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def trajectory_matches_topology(traj_p: Path, top_p: Path, gene: str) -> bool:
    """
    Whether a trajectory and a topology describe the same system.

    Two attempts to read the atom count out of the DCD header by fixed byte offset both
    failed: offset 8 returned the frame count, and offset 4 returned the ASCII value of
    the "CORD" magic.  In a CHARMM DCD the atom count (NBEGIN) sits after the title
    record, whose length varies, so no fixed offset is safe.  Rather than guess a third
    time, the question is put to mdtraj: it knows the topology's atom count and raises a
    ValueError naming the trajectory's count when the two disagree.  Reading a single
    frame is cheap, so this costs almost nothing.

    This matters because addSolvent is not reproducible - three builds of the HMOX1
    receptor gave 78,930, 78,837 and 79,191 atoms - so a trajectory left behind by an
    interrupted run routinely belongs to a differently sized system.  Without the check,
    mdtraj raises deep inside its reader and aborts the whole analysis run.
    """
    try:
        n_top = md.load_topology(str(top_p)).n_atoms
    except Exception as exc:  # noqa: BLE001
        print(f"  {gene:8s} topology unreadable: {type(exc).__name__}: {exc}")
        return False
    try:
        for block in md.iterload(str(traj_p), top=str(top_p), chunk=1):
            _ = block.xyz
            return True
        print(f"  {gene:8s} SKIPPED: {traj_p.name} contains no frames")
        return False
    except ValueError as exc:
        # mdtraj reports both counts: "xyz must be shape (Any, 79191, 3). You supplied
        # (1, 78930, 3)"
        print(f"  {gene:8s} SKIPPED: {traj_p.name} does not match complex.pdb "
              f"({n_top:,} atoms).")
        print(f"           {exc}")
        print(f"           This trajectory is from an interrupted attempt on a "
              f"differently solvated system; re-run the target to regenerate it.")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"  {gene:8s} SKIPPED: {traj_p.name} could not be opened: "
              f"{type(exc).__name__}: {str(exc)[:120]}")
        return False


def analyse(gene: str, chunk: int = 200) -> dict | None:
    d = OUT / gene
    traj_p = newest_traj(d)
    top_p = d / "complex.pdb"
    if traj_p is None or not top_p.exists():
        print(f"  {gene:8s} no trajectory")
        return None
    others = [p.name for p in d.glob("traj*.dcd") if p != traj_p]
    if others:
        print(f"  {gene:8s} analysing {traj_p.name}; older files present: {others}")
    if not trajectory_matches_topology(traj_p, top_p, gene):
        return None
    print(f"  {gene:8s} trajectory: {traj_p.name} "
          f"({traj_p.stat().st_size/1e6:.1f} MB)", flush=True)

    top = md.load_topology(str(top_p))
    lig, prot, bb = find_groups(top, gene)
    if len(lig) == 0:
        # find_groups has already printed the full residue inventory
        print(f"  {gene:8s} cannot analyse without identifying the ligand")
        return None
    align = bb if len(bb) else prot
    print(f"  {gene:8s} ligand {len(lig)} atoms, protein {len(prot)} atoms, "
          f"alignment on {len(align)} atoms", flush=True)

    # Two different reference structures are needed, and conflating them was a real
    # error in an earlier version of this analysis.
    #
    #   head  the first frame written, which is the start of equilibration.  Contacts
    #         are defined here, because it is the state closest to the docked pose and
    #         it is the frame the equilibration was launched from.
    #   ref   the first production frame, after 0.5 ns of equilibration.  Every
    #         production metric is measured against this, so that the reported ligand
    #         RMSD describes how the pose behaved during production and not how far
    #         equilibration had already carried it.  The previous version used the
    #         first frame for both and its output was labelled as if the reference were
    #         the docked pose, which it was not.
    #
    # The offset between the two is printed rather than hidden, so a reader can see how
    # much of the motion happened before production began.
    head = None
    for block in md.iterload(str(traj_p), top=str(top_p), chunk=1):
        head = block[0]
        break
    if head is None:
        print(f"  {gene:8s} trajectory is empty")
        return None
    if len(align):
        head.superpose(head, 0, atom_indices=align)

    # Contact definition, built explicitly rather than taken from compute_neighbors.
    #
    # Three different assumptions about that function have now been wrong: that it
    # returns a list of per-frame arrays, that indexing [0] gives the pair array, and
    # that its output holds atom pairs at all.  The last error was decisive -
    # "flattened contact array has odd size 67", and a ligand-protein pair list must
    # have an even number of elements.  Its return value is therefore not relied on.
    #
    # Instead every ligand-protein atom pair is enumerated and the distances are
    # computed directly, which is unambiguous.  38 ligand atoms against 4,533 protein
    # atoms is about 172,000 pairs, roughly 1.4 MB of indices, and the distance matrix
    # per frame is 172,000 floats.
    all_pairs = np.array([(l, p) for l in lig for p in prot], dtype=np.int64)
    d0 = md.compute_distances(head, all_pairs)[0]
    contacts = all_pairs[d0 <= CONTACT_NM]
    n_contacts = len(contacts)
    print(f"  {gene:8s} contacts defined from the first written frame: {n_contacts} "
          f"(out of {len(all_pairs):,} ligand-protein atom pairs within "
          f"{CONTACT_NM} nm)", flush=True)

    # Frame count, skipping the equilibration frames.  DCDReporter is attached before
    # the NVT stage, so the file contains (NVT_PS + NPT_PS) / REPORT_PS equilibration
    # frames ahead of production; analysing them would report a longer run than was
    # performed and would include a stage that is not equilibrated.
    total_all = 0
    for block in md.iterload(str(traj_p), top=str(top_p), chunk=chunk):
        total_all += block.n_frames
    if total_all == 0:
        print(f"  {gene:8s} no frames")
        return None
    skip = min(EQUIL_FRAMES, max(total_all - 1, 0))
    total = total_all - skip
    # REPORT_PS is in picoseconds, so the frame span is frames * 10 ps; an earlier
    # version multiplied by the timestep instead and reported 1.5 ns as 3.0 ns.
    ns_all = total_all * REPORT_PS / 1000.0
    ns_prod = total * REPORT_PS / 1000.0
    print(f"  {gene:8s} frames in file: {total_all} ({ns_all:.2f} ns); "
          f"skipping {skip} equilibration frames; "
          f"analysing {total} ({ns_prod:.2f} ns)", flush=True)
    if total == 0:
        print(f"  {gene:8s} no production frames after skipping equilibration")
        return None
    half = total // 2

    # The production reference: the first frame after the equilibration frames.
    ref = None
    for block in md.iterload(str(traj_p), top=str(top_p), chunk=1, skip=skip):
        ref = block[0]
        break
    if ref is None:
        print(f"  {gene:8s} no frame at the start of production")
        return None
    if len(align):
        ref.superpose(head, 0, atom_indices=align)

    # How far equilibration carried the system before production began.  Reported, not
    # buried: it bounds what the production metrics can be said to describe.  A ligand
    # RMSD measured from `ref` covers only the production window, so the user of these
    # numbers needs this offset to combine it with anything said about the docked pose.
    eq_lig = float(np.sqrt(((ref.xyz[0, lig, :] - head.xyz[0, lig, :]) ** 2).sum(axis=1).mean())) * 10.0
    eq_rec = float(np.sqrt(((ref.xyz[0, align, :] - head.xyz[0, align, :]) ** 2).sum(axis=1).mean())) * 10.0
    print(f"  {gene:8s} equilibration carried the ligand {eq_lig:.2f} A and the "
          f"aligned backbone {eq_rec:.2f} A away from the first written frame "
          f"({skip * REPORT_PS / 1000.0:.2f} ns of NVT + NPT)", flush=True)

    lig0_centroid = ref.xyz[0, lig, :].mean(axis=0)
    # plain numpy indexing: ref[:, lig] fails inside mdtraj for a single-frame
    # trajectory, because Trajectory.slice() does self.time[key] and time is 1-D there
    rg0 = float(radius_of_gyration(ref.xyz[:, lig, :])[0]) * 10.0
    acc = {"lig": 0.0, "rec": 0.0, "drift": 0.0, "surv": 0.0, "rg": 0.0}
    tail = {"lig": 0.0, "rec": 0.0, "surv": 0.0}
    mx = {"lig": 0.0, "drift": 0.0}
    n_tail = 0
    seen = 0

    for block in md.iterload(str(traj_p), top=str(top_p), chunk=chunk, skip=skip):
        nb = block.n_frames
        if len(align):
            block.superpose(ref, 0, atom_indices=align)
        # every per-frame quantity goes through as_1d_per_frame: seven earlier failures
        # came from assuming what these functions return.  Each call is also guarded so
        # that a shape surprise names the operation that produced it instead of raising
        # an IndexError somewhere downstream.
        try:
            _r = md.rmsd(block, ref, 0, atom_indices=lig)
            lig_rmsd = as_1d_per_frame(_r, nb, "ligand RMSD") * 10.0
        except RuntimeError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"ligand RMSD failed on a block of {nb} frames: "
                               f"{type(exc).__name__}: {exc}") from exc
        try:
            _r = md.rmsd(block, ref, 0, atom_indices=align)
            rec_rmsd = as_1d_per_frame(_r, nb, "receptor RMSD") * 10.0
        except RuntimeError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"receptor RMSD failed on a block of {nb} frames: "
                               f"{type(exc).__name__}: {exc}") from exc
        cent = block.xyz[:, lig, :].mean(axis=1)
        drift = np.linalg.norm(cent - lig0_centroid, axis=1) * 10.0
        # computed directly from the coordinate array, avoiding mdtraj's indexing
        rg = as_1d_per_frame(radius_of_gyration(block.xyz[:, lig, :]), nb,
                             "radius of gyration") * 10.0
        if n_contacts:
            try:
                dist = np.asarray(md.compute_distances(block, contacts), dtype=float)
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(
                    f"compute_distances failed: block has {nb} frames, contacts has "
                    f"shape {np.shape(contacts)}, block.xyz shape "
                    f"{np.shape(block.xyz)}: {type(exc).__name__}: {exc}") from exc
            # compute_distances returns (frames, pairs); a single-frame block can
            # collapse to one dimension, so the shape is normalised explicitly
            if dist.ndim == 1:
                dist = dist.reshape(1, -1) if nb == 1 else dist.reshape(nb, -1)
            if dist.shape[0] != nb:
                raise RuntimeError(
                    f"compute_distances gave {dist.shape[0]} rows for a block of "
                    f"{nb} frames (raw shape {np.shape(dist)}, "
                    f"contacts {np.shape(contacts)})")
            surv = as_1d_per_frame((dist <= CONTACT_NM).mean(axis=1), nb,
                                   "contact survival")
        else:
            surv = np.zeros(nb)

        acc["lig"] += float(lig_rmsd.sum())
        acc["rec"] += float(rec_rmsd.sum())
        acc["drift"] += float(drift.sum())
        acc["surv"] += float(surv.sum())
        acc["rg"] += float(rg.sum())
        mx["lig"] = max(mx["lig"], float(lig_rmsd.max()))
        mx["drift"] = max(mx["drift"], float(drift.max()))

        idx = np.arange(seen, seen + nb)
        sel = idx >= half
        if sel.any():
            tail["lig"] += float(lig_rmsd[sel].sum())
            tail["rec"] += float(rec_rmsd[sel].sum())
            tail["surv"] += float(surv[sel].sum())
            n_tail += int(sel.sum())

        # record the time course so the motion can be inspected rather than summarised
        rows_series = SERIES.setdefault(gene, [])
        for j in range(nb):
            rows_series.append([
                gene, int(idx[j]),
                round(float((seen + j) * REPORT_PS / 1000.0), 3),
                round(float(lig_rmsd[j]), 3),
                round(float(drift[j]), 3),
                round(float(rec_rmsd[j]), 3),
                round(float(surv[j]), 4),
            ])
        seen += nb
        print(f"    {gene}: {seen}/{total} frames", end="\r", flush=True)

    print(" " * 60, end="\r")
    out = {
        "gene": gene,
        "n_frames": int(total),
        # frames times the reporting interval, in ps, converted to ns.  Also
        # multiplying by TIMESTEP_PS was a unit error that reported a 1 ns run as 2 ns;
        # the reporting interval is already in picoseconds.
        "ns_analysed": round(total * REPORT_PS / 1000.0, 2),
        "n_contacts_start": int(n_contacts),
        "ligand_rmsd_mean_A": round(acc["lig"] / total, 2),
        "ligand_rmsd_max_A": round(mx["lig"], 2),
        "ligand_rmsd_last_half_A": round(tail["lig"] / max(n_tail, 1), 2),
        "ligand_centroid_drift_max_A": round(mx["drift"], 2),
        "receptor_rmsd_mean_A": round(acc["rec"] / total, 2),
        "receptor_rmsd_last_half_A": round(tail["rec"] / max(n_tail, 1), 2),
        "contact_survival_last_half": round(tail["surv"] / max(n_tail, 1), 3),
        "ligand_rg_start_A": round(rg0, 2),
        "ligand_rg_mean_A": round(acc["rg"] / total, 2),
    }
    if out["ligand_rmsd_last_half_A"] < 3.0 and out["contact_survival_last_half"] > 0.4:
        out["verdict"] = "stable pose"
    elif out["ligand_centroid_drift_max_A"] > 5.0:
        out["verdict"] = "ligand left the site"
    else:
        out["verdict"] = "partially displaced / unstable"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genes", nargs="*", default=None)
    ap.add_argument("--chunk", type=int, default=200,
                    help="frames per block; lower it if memory is tight")
    args = ap.parse_args()

    if not OUT.is_dir():
        sys.exit(f"{OUT} does not exist; run run_md_allatom.py first")
    genes = args.genes or sorted(p.name for p in OUT.iterdir()
                                 if p.is_dir() and newest_traj(p) is not None)
    if not genes:
        sys.exit("no target directories with a trajectory found")

    print(f"analysing {len(genes)} trajectory(ies), {args.chunk} frames per block\n")
    rows = []
    for g in genes:
        try:
            r = analyse(g, args.chunk)
        except Exception as exc:  # noqa: BLE001
            # Print the whole stack plus the local variables of every frame.  Seven
            # failures in this script were caused by an assumed return shape, and a
            # bare one-line message left the offending line unidentified each time.
            import traceback
            print(f"\n{'=' * 84}\n{g}: analysis failed - full traceback follows\n"
                  f"{'=' * 84}")
            tb = traceback.format_exc()
            print(tb)
            print("Local variables per frame (types and shapes only):")
            e = exc.__traceback__
            depth = 0
            while e is not None:
                fr = e.tb_frame
                print(f"  frame {depth}: {fr.f_code.co_name} at line {e.tb_lineno}")
                for k, v in list(fr.f_locals.items())[:14]:
                    if k.startswith("__"):
                        continue
                    shape = getattr(v, "shape", None)
                    desc = (f"{type(v).__name__} shape={shape}" if shape is not None
                            else repr(v)[:70])
                    print(f"      {k:22s} {desc}")
                depth += 1
                e = e.tb_next
            print(f"{'=' * 84}\n")
            continue
        if r:
            rows.append(r)
            print(f"    -> {r['verdict']}: ligand RMSD last half "
                  f"{r['ligand_rmsd_last_half_A']} A, contact survival "
                  f"{r['contact_survival_last_half']:.2f}", flush=True)

    if not rows:
        return 1
    out_p = ROOT / "results" / "md_allatom_stability.csv"
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # A time course is written alongside the summary.  The first run reported a ligand
    # RMSD of 1.8 A together with a centroid drift of 108 A, which cannot both describe
    # the same motion; the trajectory has to be inspected over time to say which of the
    # two is meaningful before either is quoted.
    series = [r for k in sorted(SERIES) for r in SERIES[k]]
    if series:
        ser_p = ROOT / "results" / "md_ligand_timeseries.csv"
        with open(ser_p, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["target", "frame", "time_ns", "ligand_rmsd_A",
                        "ligand_centroid_drift_A", "receptor_rmsd_A",
                        "contact_survival"])
            w.writerows(series)
        print(f"-> {ser_p}")

        # print the course in coarse steps so the trajectory can be read at a glance
        print("\n=== ligand motion over time ===")
        for r in rows:
            g = r["gene"]
            mine = [x for x in series if x[0] == g]
            if not mine:
                continue
            step = max(len(mine) // 10, 1)
            print(f"  {g}:")
            print(f"    {'time(ns)':>9} {'ligRMSD':>9} {'centroid':>9} "
                  f"{'recRMSD':>8} {'contacts':>9}")
            for x in mine[::step]:
                print(f"    {x[2]:>9.2f} {x[3]:>9.2f} {x[4]:>9.2f} "
                      f"{x[5]:>8.2f} {x[6]:>9.2f}")
            last = mine[-1]
            print(f"    {last[2]:>9.2f} {last[3]:>9.2f} {last[4]:>9.2f} "
                  f"{last[5]:>8.2f} {last[6]:>9.2f}")

    print("\n=== pose stability ===")
    print(f"  {'gene':8s} {'frames':>7} {'ns':>6} {'ligRMSD':>8} {'max':>7} "
          f"{'drift':>7} {'contacts':>9}  verdict")
    for r in rows:
        print(f"  {r['gene']:8s} {r['n_frames']:>7} {r['ns_analysed']:>6} "
              f"{r['ligand_rmsd_mean_A']:>8} {r['ligand_rmsd_max_A']:>7} "
              f"{r['ligand_centroid_drift_max_A']:>7} "
              f"{r['contact_survival_last_half']:>9}  {r['verdict']}")
    print(f"\n-> {out_p}")
    print("\nReport in the manuscript: the criteria, every target including unstable")
    print("ones, the production length, the platform used, and the ns/day achieved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
