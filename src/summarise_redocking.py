# -*- coding: utf-8 -*-
"""
Summarise the redocking validation directory as it stands.

Each system writes its own validation.json, and the per-system files survive a re-run
of the whole set, so this reads them directly rather than relying on the aggregate CSV,
which is only written when the job finishes.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "docking" / "validation"

rows = []
pending = []
for d in sorted(VAL.iterdir()):
    if not d.is_dir():
        continue
    j = d / "validation.json"
    if j.exists():
        rows.append(json.loads(j.read_text(encoding="utf-8")))
    else:
        files = [f.name for f in d.iterdir() if f.is_file()]
        pending.append((d.name, files))

print("=" * 88)
print("Completed systems")
print("=" * 88)
print(f"  {'target':10s} {'pdb':6s} {'ligand':14s} {'heavy':>6s} {'RMSD(A)':>9s}  pass")
print("  " + "-" * 84)
for r in sorted(rows, key=lambda r: r.get("ligand_heavy_atoms") or 0):
    rms = r.get("top_pose_rmsd_A")
    print(f"  {str(r.get('target')):10s} {str(r.get('pdb')):6s} "
          f"{str(r.get('ligand')):14s} {r.get('ligand_heavy_atoms'):>6} "
          f"{(f'{rms:.3f}' if isinstance(rms, (int, float)) else str(rms)):>9s}  "
          f"{r.get('passed')}   {r.get('status')}")

print()
print("=" * 88)
print("Still running")
print("=" * 88)
if pending:
    for name, files in pending:
        print(f"  {name:14s} {len(files)} files so far: {files[:4]}")
else:
    print("  none")

if rows:
    n_pass = sum(1 for r in rows if r.get("passed") is True)
    n = len([r for r in rows if r.get("passed") is not None])
    print()
    print("=" * 88)
    print(f"{n_pass} of {n} systems passed the 2.0 A criterion")
    print("=" * 88)

    ok = [r for r in rows if r.get("passed") is True]
    bad = [r for r in rows if r.get("passed") is False]
    if ok:
        print(f"  passed:      heavy atoms "
              f"{min(r['ligand_heavy_atoms'] for r in ok)}-"
              f"{max(r['ligand_heavy_atoms'] for r in ok)}")
    if bad:
        print(f"  failed:      heavy atoms "
              f"{min(r['ligand_heavy_atoms'] for r in bad)}-"
              f"{max(r['ligand_heavy_atoms'] for r in bad)}")
        print("  failures:")
        for r in bad:
            print(f"      {r.get('target')} / {r.get('ligand')} "
                  f"({r.get('ligand_heavy_atoms')} heavy atoms): "
                  f"{r.get('top_pose_rmsd_A')} A")
    print()
    print("  ethambutol has 10 heavy atoms and three rotatable bonds, so the question")
    print("  is whether systems of that size pass; a failure confined to much larger")
    print("  ligands bounds the protocol's applicability instead of undermining it.")
