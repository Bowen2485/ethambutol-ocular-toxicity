# -*- coding: utf-8 -*-
"""
Consolidate the redocking panel into one table, keeping only box-verified systems.

Results accumulated across several runs, and one run produced two entries whose boxes
did not enclose their own ligands.  Those are excluded here, together with duplicates
created when the directory key was changed, so that what remains is one row per
system with a docking box confirmed to contain the ligand it scored.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "docking" / "validation"
OUT = ROOT / "results" / "redocking_validation_final.csv"

# friendly names for the systems that enter the manuscript
LABELS = {
    "TRYPSIN_3PTB": "Trypsin",
    "CA2_3HS4": "Carbonic anhydrase II (3HS4)",
    "CA2_1AZM": "Carbonic anhydrase II (1AZM)",
    "PNP": "Purine nucleoside phosphorylase",
    "HSP90": "HSP90",
    "DHFR": "Dihydrofolate reductase",
    "BACE1_2OH4": "BACE1",
}
# directories superseded by a corrected re-run, or discarded on the box check
SKIP = {"CA2", "BACE1", "AMPC", "TRYPSIN", "CA2_3M04"}


def centroid(p: Path) -> np.ndarray | None:
    xs = []
    for ln in p.read_text(errors="replace").splitlines():
        if ln.startswith(("ATOM", "HETATM")):
            try:
                xs.append([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])
            except ValueError:
                continue
    return np.asarray(xs).mean(axis=0) if xs else None


def box_files(p: Path) -> tuple[np.ndarray | None, float]:
    vals = {}
    for ln in p.read_text(errors="replace").splitlines():
        for k in ("center_x", "center_y", "center_z", "size_x"):
            if ln.strip().startswith(k):
                try:
                    vals[k] = float(ln.split("=")[1])
                except (IndexError, ValueError):
                    pass
    c = (np.asarray([vals["center_x"], vals["center_y"], vals["center_z"]])
         if {"center_x", "center_y", "center_z"} <= vals.keys() else None)
    return c, vals.get("size_x", 24.0)


rows = []
for d in sorted(VAL.iterdir()):
    if not d.is_dir() or d.name in SKIP:
        continue
    jp = d / "validation.json"
    if not jp.exists():
        continue
    rec = json.loads(jp.read_text(encoding="utf-8"))
    rms = rec.get("top_pose_rmsd_A")
    heavy = rec.get("ligand_heavy_atoms")
    if rms is None or heavy is None:
        continue
    bp, lp = d / "redock.box.txt", d / "crystal_ligand.pdb"
    box_ok, offset = "no box/ligand file", None
    if bp.exists() and lp.exists():
        c, size = box_files(bp)
        lc = centroid(lp)
        if c is not None and lc is not None:
            offset = float(np.linalg.norm(c - lc))
            box_ok = "OK" if offset <= size / 2.0 else "MISSED"
    rows.append({
        "system": LABELS.get(d.name, d.name),
        "dir": d.name,
        "pdb": rec.get("pdb"),
        "ligand": str(rec.get("ligand", "")).split("_")[0],
        "heavy_atoms": heavy,
        "affinity": rec.get("best_affinity_kcal_mol"),
        "rmsd_A": round(float(rms), 3),
        "passed": bool(float(rms) <= 2.0),
        "box_offset_A": round(offset, 1) if offset is not None else "",
        "box_ok": box_ok,
    })

rows.sort(key=lambda r: r["heavy_atoms"])
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"-> {OUT}")
print()
print(f"  {'system':30s} {'lig':6s} {'heavy':>5s} {'aff':>7s} {'RMSD':>8s} {'box':>5s}")
for r in rows:
    aff = r["affinity"]
    aff_s = f"{float(aff):.2f}" if isinstance(aff, (int, float)) else "-"
    print(f"  {r['system']:30s} {r['ligand']:6s} {r['heavy_atoms']:>5} "
          f"{aff_s:>7s} {r['rmsd_A']:>8.3f} {r['box_ok']:>5s}")
print()
print(f"  {sum(1 for r in rows if r['passed'])} passed, "
      f"{sum(1 for r in rows if not r['passed'])} failed")
