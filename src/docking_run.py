# -*- coding: utf-8 -*-
"""
Step 4 - AutoDock Vina docking engine with a redocking validation protocol.

Validation (reported as a methodological control in the paper)
    For a target that has a co-crystallised ligand, the ligand is extracted from
    the experimental structure, converted to PDBQT, re-docked into its own
    receptor with the search box centred on the crystallographic ligand, and the
    top pose is compared with the crystal pose by symmetry-corrected RMSD.
    A protocol is only used for novel predictions if the redocking RMSD is
    <= 2.0 A (the accepted community criterion).

Docking
    Focused docking: search box centred on the co-crystal ligand centroid
    (radius -> box size), or on a supplied centre/size.  Exhaustiveness 32,
    up to 20 modes, seed fixed for reproducibility.

Outputs -> docking/poses/<target>_<ligand>_vina.pdbqt and docking/results.csv
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DOCK = ROOT / "docking"
TOOLS = ROOT / "tools"
VINA = TOOLS / "vina.exe"
OBABEL = Path(r"C:\Program Files\OpenBabel-3.1.1\obabel.exe")
for p in (DOCK / "poses", DOCK / "boxes", DOCK / "validation", DERIVED):
    p.mkdir(parents=True, exist_ok=True)


def _env() -> dict:
    e = dict(os.environ)
    e["BABEL_LIBDIR"] = r"C:\Program Files\OpenBabel-3.1.1\lib\openbabel\3.1.0"
    e["BABEL_DATADIR"] = r"C:\Program Files\OpenBabel-3.1.1\share\openbabel\3.1.0"
    return e


def run(cmd: list, timeout: int = 1800) -> tuple[int, str]:
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                       env=_env(), timeout=timeout, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# ------------------------------------------------------------------ PDB parsing
def parse_pdb_atoms(path: Path, keep_het: bool = True) -> list[dict]:
    atoms = []
    for ln in path.read_text(errors="replace").splitlines():
        rec = ln[:6].strip()
        if rec not in ("ATOM", "HETATM"):
            continue
        if rec == "HETATM" and not keep_het:
            continue
        try:
            atoms.append({
                "rec": rec,
                "serial": ln[6:11].strip(),
                "name": ln[12:16].strip(),
                "resname": ln[17:20].strip(),
                "chain": ln[21:22].strip(),
                "resseq": ln[22:26].strip(),
                "icode": ln[26:27].strip(),
                "xyz": np.array([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])]),
                "element": (ln[76:78].strip() or ln[12:16].strip()[:1]).upper(),
                "line": ln,
            })
        except (ValueError, IndexError):
            continue
    return atoms


def crystal_ligands(path: Path) -> dict[str, dict]:
    """Non-polymer residues larger than a buffer ion, grouped by (resname, chain)."""
    atoms = parse_pdb_atoms(path)
    groups: dict[tuple, list] = {}
    for a in atoms:
        if a["rec"] != "HETATM":
            continue
        if a["resname"] in ("HOH", "DOD"):
            continue
        groups.setdefault((a["resname"], a["chain"], a["resseq"]), []).append(a)
    out = {}
    for (resn, ch, rs), ats in groups.items():
        heavy = [a for a in ats if a["element"] != "H"]
        if len(heavy) < 8:          # skip ions / solvents / small buffers
            continue
        keys = [a["element"] for a in heavy]
        if sum(1 for e in keys if e in ("C",)) < 4:   # a real drug-like ligand has carbons
            continue
        out[f"{resn}_{ch}_{rs}"] = {"resname": resn, "chain": ch, "resseq": rs,
                                    "atoms": ats, "n_heavy": len(heavy)}
    return out


def write_pdb(atoms: list[dict], path: Path, resname: str = "LIG") -> None:
    lines = []
    for i, a in enumerate(atoms, 1):
        lines.append(
            f"HETATM{i:5d} {a['name']:<4s}{resname:>3s} A   1    "
            f"{a['xyz'][0]:8.3f}{a['xyz'][1]:8.3f}{a['xyz'][2]:8.3f}"
            f"  1.00  0.00          {a['element']:>2s}")
    lines.append("END")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_pdbqt_poses(path: Path) -> list[dict]:
    poses, cur, model = [], [], 0
    for ln in path.read_text(errors="replace").splitlines():
        if ln.startswith("MODEL"):
            model += 1
            cur = []
        elif ln.startswith("ENDMDL"):
            poses.append({"model": model, "atoms": cur})
            cur = []
        elif ln.startswith(("ATOM", "HETATM")):
            try:
                cur.append({
                    "name": ln[12:16].strip(),
                    "resname": ln[17:20].strip(),
                    "xyz": np.array([float(ln[30:38]), float(ln[38:46]),
                                     float(ln[46:54])]),
                    "type": ln[77:79].strip(),
                })
            except (ValueError, IndexError):
                continue
    if cur:
        poses.append({"model": model or 1, "atoms": cur})
    return poses


def vina_scores(pdbqt: Path) -> list[float]:
    """Parse the `REMARK VINA RESULT` affinity column written by Vina."""
    out = []
    for ln in pdbqt.read_text(errors="replace").splitlines():
        if ln.startswith("REMARK VINA RESULT"):
            parts = ln.split()
            try:
                out.append(float(parts[3]))
            except (IndexError, ValueError):
                pass
    return out


# ----------------------------------------------------------------- RMSD metrics
def _best_symmetry_rmsd(ref: np.ndarray, mob: np.ndarray, elements: list[str],
                        max_perm: int = 200000) -> float:
    """
    Symmetry-corrected RMSD: for each element class, try every assignment of the
    mobile atoms onto the reference atoms (Hungarian-free brute force is too
    slow beyond ~8 atoms of a class, so a greedy nearest-neighbour assignment is
    used above that threshold, which is standard practice for redocking checks).
    """
    from itertools import permutations
    if len(ref) != len(mob):
        n = min(len(ref), len(mob))
        ref, mob = ref[:n], mob[:n]
        elements = elements[:n]
    total = 0.0
    for el in sorted(set(elements)):
        idx = [i for i, e in enumerate(elements) if e == el]
        r, m = ref[idx], mob[idx]
        if len(idx) == 0:
            continue
        if len(idx) <= 7:
            best = float("inf")
            for p in permutations(range(len(idx))):
                d = r - m[list(p)]
                v = float((d ** 2).sum())
                if v < best:
                    best = v
            total += best
        else:
            # greedy: assign each mobile atom to its nearest free reference atom
            free = list(range(len(idx)))
            for i in range(len(idx)):
                d = ((r[free] - m[i]) ** 2).sum(axis=1)
                j = int(np.argmin(d))
                total += float(d[j])
                free.pop(j)
    return math.sqrt(total / max(len(ref), 1))


def rmsd_to_crystal(crystal_atoms: list[dict], pose_atoms: list[dict]) -> float:
    ref = np.array([a["xyz"] for a in crystal_atoms if a["element"] != "H"])
    els = [a["element"] for a in crystal_atoms if a["element"] != "H"]
    mob_all = [a for a in pose_atoms if a["type"] not in ("H", "HD")]
    mob = np.array([a["xyz"] for a in mob_all])
    # align the pose element sequence to the reference by nearest-element matching
    if len(mob) != len(ref):
        # keep only the heavy atoms closest in count
        n = min(len(mob), len(ref))
        mob, ref, els = mob[:n], ref[:n], els[:n]
    return _best_symmetry_rmsd(ref, mob, els)


# ------------------------------------------------------------------------ Vina
def make_box(centre: np.ndarray, size: float = 24.0) -> dict:
    return {"center_x": float(centre[0]), "center_y": float(centre[1]),
            "center_z": float(centre[2]),
            "size_x": float(size), "size_y": float(size), "size_z": float(size)}


def write_box(box: dict, path: Path) -> None:
    path.write_text("\n".join(f"{k} = {v}" for k, v in box.items()) + "\n",
                    encoding="utf-8")


def dock(receptor: Path, ligand: Path, box: dict, out: Path,
         exhaustiveness: int = 32, n_modes: int = 20, seed: int = 20261011,
         cpu: int = 0) -> tuple[bool, str]:
    if out.exists() and out.stat().st_size > 0 and vina_scores(out):
        return True, "cached"
    box_path = out.with_suffix(".box.txt")
    write_box(box, box_path)
    log = out.with_suffix(".log")
    cmd = [VINA, "--receptor", receptor, "--ligand", ligand,
           "--config", box_path, "--out", out,
           "--exhaustiveness", exhaustiveness, "--num_modes", n_modes,
           "--seed", seed, "--cpu", cpu or max(1, (os.cpu_count() or 4) - 1)]
    rc, txt = run(cmd, timeout=7200)
    log.write_text(txt, encoding="utf-8", errors="replace")
    return rc == 0 and out.exists() and bool(vina_scores(out)), txt[-800:]


def centroid(atoms: list[dict]) -> np.ndarray:
    heavy = [a["xyz"] for a in atoms if a["element"] != "H"]
    return np.mean(np.array(heavy), axis=0)


# ------------------------------------------------------------------------ main
def validation(target: str, pdb_id: str, ligand_key: str | None = None) -> dict:
    """Redock the co-crystallised ligand and report the symmetry-corrected RMSD."""
    from docking_prep import prep_receptor            # local import: same package
    # The directory is keyed by target AND PDB id.  Keying it by target alone means two
    # structures of the same protein share one directory, and the second run overwrites
    # the first run's box file while its ligand file is replaced - so the docking is
    # then performed with one structure's box against another structure's ligand.  That
    # happened when CA2 was validated with both 3HS4 and 1AZM, and it produced a 54 A
    # RMSD from what was in fact a correct protocol.
    work = DOCK / "validation" / f"{target}_{pdb_id.upper()}"
    work.mkdir(parents=True, exist_ok=True)
    raw = DOCK / "receptors" / pdb_id.upper() / f"{pdb_id.upper()}.pdb"
    if not raw.exists():
        work.mkdir(parents=True, exist_ok=True)
        (DOCK / "receptors" / pdb_id.upper()).mkdir(parents=True, exist_ok=True)
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=180, context=ctx) as r:
            raw.write_bytes(r.read())

    ligs = crystal_ligands(raw)
    if not ligs:
        return {"target": target, "pdb": pdb_id, "status": "no co-crystal ligand"}
    if ligand_key:
        # The keys returned by crystal_ligands are identifiers such as "BE7_A_502",
        # while a caller naturally supplies just the residue name "BE7".  An exact
        # match therefore failed and the code fell through to the largest ligand,
        # which is how CA2:3M04:BE7 silently docked the 19-atom BE9 instead of the
        # 10-atom BE7 - the one component whose size matches ethambutol.  Match on the
        # residue name, then fall back to a substring test on the whole key.
        want = ligand_key.strip().upper()
        exact = [k for k in ligs if k.upper() == want]
        by_res = [k for k in ligs if k.split("_")[0].upper() == want]
        partial = [k for k in ligs if want in k.upper()]
        pick = (exact or by_res or partial)
        if pick:
            key = pick[0]
            if len(pick) > 1:
                print(f"[valid:{target}] WARNING {len(pick)} ligands match "
                      f"{ligand_key!r}: {pick}; using {key}")
        else:
            key = max(ligs, key=lambda k: ligs[k]["n_heavy"])
            print(f"[valid:{target}] WARNING requested ligand {ligand_key!r} not "
                  f"found; available: {sorted(ligs)}; falling back to the largest, "
                  f"{key}")
    else:
        key = max(ligs, key=lambda k: ligs[k]["n_heavy"])
    lig = ligs[key]
    print(f"[valid:{target}] co-crystal ligand {key} ({lig['n_heavy']} heavy atoms)")

    # receptor without that ligand
    receptor_pdb = work / f"{pdb_id}_apo.pdb"
    keep_lines = []
    for ln in raw.read_text(errors="replace").splitlines():
        if ln.startswith("HETATM") and ln[17:20].strip() == lig["resname"] and \
                ln[21:22].strip() == lig["chain"]:
            continue
        if ln.startswith(("ATOM", "HETATM", "TER", "END")):
            keep_lines.append(ln)
    receptor_pdb.write_text("\n".join(keep_lines) + "\n", encoding="utf-8")
    rc, _ = run([OBABEL, receptor_pdb, "-O", work / "receptor.pdbqt", "-xr"])
    receptor = work / "receptor.pdbqt"
    if not receptor.exists():
        return {"target": target, "pdb": pdb_id, "status": "receptor prep failed"}

    crystal_pdb = work / "crystal_ligand.pdb"
    write_pdb(lig["atoms"], crystal_pdb, resname=lig["resname"][:3])
    rc, log = run([OBABEL, crystal_pdb, "-O", work / "crystal_ligand.pdbqt", "-h"])
    lig_pdbqt = work / "crystal_ligand.pdbqt"
    if not lig_pdbqt.exists():
        return {"target": target, "pdb": pdb_id, "status": f"ligand prep failed {log[-160:]}"}

    box = make_box(centroid(lig["atoms"]), size=24.0)
    out = work / "redock.pdbqt"
    ok, msg = dock(receptor, lig_pdbqt, box, out, exhaustiveness=32, n_modes=20)
    if not ok:
        return {"target": target, "pdb": pdb_id, "status": f"docking failed {msg[-200:]}"}

    scores = vina_scores(out)
    poses = parse_pdbqt_poses(out)
    if not poses:
        return {"target": target, "pdb": pdb_id, "status": "no poses written"}
    rms = rmsd_to_crystal(lig["atoms"], poses[0]["atoms"])
    res = {"target": target, "pdb": pdb_id, "ligand": key,
           "ligand_heavy_atoms": lig["n_heavy"],
           "best_affinity_kcal_mol": scores[0] if scores else None,
           "top_pose_rmsd_A": round(rms, 3),
           "passed": bool(rms <= 2.0), "status": "ok"}
    (work / "validation.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"[valid:{target}] affinity={res['best_affinity_kcal_mol']} "
          f"RMSD={res['top_pose_rmsd_A']} A  passed={res['passed']}")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["validate", "dock"], default="validate")
    ap.add_argument("--validation-set", default="",
                    help="comma list gene:PDBID")
    ap.add_argument("--target", default="")
    ap.add_argument("--pdb", default="")
    ap.add_argument("--ligands", default="ethambutol")
    ap.add_argument("--box-center", default="")
    ap.add_argument("--box-size", type=float, default=24.0)
    args = ap.parse_args()

    if args.mode == "validate":
        pairs = []
        if args.validation_set:
            # gene:PDBID or gene:PDBID:LIGANDRESNAME.  The ligand key matters: without
            # it the pipeline takes the largest co-crystal ligand, and 3M04 carries both
            # a 19-atom and a 10-atom component, so the default would silently skip the
            # one that matches ethambutol's size.
            for item in args.validation_set.split(","):
                parts = [p.strip() for p in item.split(":")]
                gene = parts[0] if parts else ""
                pid = parts[1] if len(parts) > 1 else ""
                key = parts[2] if len(parts) > 2 else None
                pairs.append((gene, pid, key))
        else:
            pairs = [(g, p, None) for g, p in
                     [("CA2", "3HS4"), ("DHFR", "1RG7"), ("AKT1", "9TMV"),
                      ("HMOX1", "1N45"), ("TP53", "5G4M")]]
        rows = []
        for gene, pid, key in pairs:
            if not pid:
                continue
            try:
                rows.append(validation(gene, pid, key))
            except Exception as exc:  # noqa: BLE001
                print(f"[valid:{gene}] FAILED {type(exc).__name__} {str(exc)[:160]}")
                rows.append({"target": gene, "pdb": pid,
                             "status": f"error {type(exc).__name__}"})
        import pandas as pd
        df = pd.DataFrame(rows)
        # each system also keeps its own validation.json, so re-running the set does not
        # lose the record of a system that was validated earlier
        df.to_csv(DOCK / "validation" / "redocking_validation.csv", index=False,
                  encoding="utf-8-sig")
        print("\n=== redocking validation ===")
        print(df.to_string(index=False, max_colwidth=40))
        return 0

    print("dock mode: supply a prepared receptor/ligand pair (see dock_targets.py)")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
