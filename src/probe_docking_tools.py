# -*- coding: utf-8 -*-
"""
Report the docking toolchain available, so a new validation set can be built on fact.

The existing validation has two controls: carbonic anhydrase II with acetazolamide
(13 heavy atoms), which reproduced its crystal pose at 1.795 A and passed, and
dihydrofolate reductase with methotrexate (33 heavy atoms, flexible), which gave
5.863 A and failed.

That pair does not establish where the protocol's limit lies.  Acetazolamide is smaller
than ethambutol and methotrexate is far larger, so ethambutol - 10 heavy atoms and three
rotatable bonds - sits in an untested gap.  The fix is a validation set of ligands
matched to ethambutol in size and flexibility, which is what this script prepares for by
reporting exactly which tools are present and which paths the pipeline already uses.
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"

print("=" * 84)
print("1. External executables")
print("=" * 84)
for exe in ("vina", "obabel", "reduce", "prepare_receptor4.py", "prepare_ligand4.py"):
    found = shutil.which(exe)
    print(f"  {exe:24s} {found or 'not on PATH'}")

print()
print("=" * 84)
print("2. Python modules")
print("=" * 84)
for m in ("rdkit", "openbabel", "meeko", "vina", "numpy", "pandas", "scipy"):
    try:
        mod = importlib.import_module(m)
        v = getattr(mod, "__version__", "?")
        print(f"  {m:12s} {v}")
    except ImportError as exc:
        print(f"  {m:12s} NOT INSTALLED ({type(exc).__name__})")

print()
print("=" * 84)
print("3. Where the existing pipeline looks for its tools")
print("=" * 84)
for f in ("docking_tools_fetch.py", "docking_run.py", "docking_prep.py"):
    p = ROOT / "src" / f
    if not p.exists():
        continue
    txt = p.read_text(encoding="utf-8", errors="replace")
    hits = [ln.strip() for ln in txt.splitlines()
            if any(k in ln for k in ("which(", "TOOLS", "BIN", "vina", "obabel",
                                     "reduce", "exe"))][:6]
    print(f"  {f}:")
    for h in hits:
        print(f"      {h[:96]}")

print()
print("=" * 84)
print("4. What the docking directory already contains")
print("=" * 84)
for sub in ("receptors", "ligands", "boxes", "poses", "validation"):
    d = DOCK / sub
    if d.is_dir():
        n = sum(1 for _ in d.rglob("*") if _.is_file())
        print(f"  {sub:12s} {n:>5} files")
    else:
        print(f"  {sub:12s} absent")

print()
print("  Ligands already prepared:")
lig = DOCK / "ligands"
if lig.is_dir():
    for p in sorted(lig.iterdir())[:20]:
        n = sum(1 for _ in p.rglob("*") if _.is_file()) if p.is_dir() else 0
        print(f"      {p.name:22s} {'dir, ' + str(n) + ' files' if p.is_dir() else ''}")

print()
print("=" * 84)
print("5. Vina version, if runnable")
print("=" * 84)
vina = shutil.which("vina")
if vina:
    try:
        r = subprocess.run([vina, "--version"], capture_output=True, text=True,
                           timeout=60)
        print(f"  {' '.join((r.stdout or r.stderr).split())[:100]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  could not run: {type(exc).__name__}")
else:
    print("  vina not on PATH; the pipeline must reference it by absolute path")
