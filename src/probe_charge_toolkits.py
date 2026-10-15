#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnose why partial charges cannot be assigned for the ligand.

The error was:
    No registered toolkits can provide the capability "assign_partial_charges"

GAFFTemplateGenerator needs partial charges.  OpenFF can get them from several
backends - AmberTools' antechamber, OpenEye, or the openff-nagl model - and the
environment has both ambertools and openff-nagl installed, so the question is which
ones the toolkit registry actually exposes.

Run with the md environment:
    ~/miniconda3/envs/md/bin/python src/probe_charge_toolkits.py
"""
from __future__ import annotations

import traceback

print("=" * 84)
print("1. OpenFF toolkit registry: what is registered")
print("=" * 84)
try:
    from openff.toolkit.utils.toolkits import GLOBAL_TOOLKIT_REGISTRY as REG
    print(f"  registered toolkits: {[t.__class__.__name__ for t in REG.registered_toolkits]}")
    for tk in REG.registered_toolkits:
        name = tk.__class__.__name__
        try:
            ok = tk.check_for_toolkit()
        except Exception as exc:  # noqa: BLE001
            ok = f"check raised {type(exc).__name__}"
        print(f"    {name:22s} available={ok}")
except Exception as exc:  # noqa: BLE001
    print(f"  registry unavailable: {type(exc).__name__}: {exc}")

print()
print("=" * 84)
print("2. Which toolkits advertise assign_partial_charges")
print("=" * 84)
try:
    from openff.toolkit.utils.toolkits import GLOBAL_TOOLKIT_REGISTRY as REG
    try:
        providers = REG.list_available_toolkits_for_capability("assign_partial_charges")
        print(f"  providers: {providers}")
    except Exception as exc:  # noqa: BLE001
        print(f"  query failed: {type(exc).__name__}: {exc}")
    for meth in ("am1bcc", "am1-mulliken", "nagl", "gasteiger", "mmff94"):
        try:
            tk = REG.get_toolkit_for_capability("assign_partial_charges", method=meth)
            print(f"  method {meth:14s} -> {tk.__class__.__name__}")
        except Exception as exc:  # noqa: BLE001
            print(f"  method {meth:14s} -> unavailable ({type(exc).__name__})")
except Exception:  # noqa: BLE001
    traceback.print_exc()

print()
print("=" * 84)
print("3. Is openff-nagl importable, and does it register itself?")
print("=" * 84)
for mod in ("openff.nagl", "openff.nagl_models", "openff.nagl.toolkits.openff"):
    try:
        m = __import__(mod, fromlist=["*"])
        print(f"  {mod:32s} OK  {getattr(m, '__version__', '')}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {mod:32s} MISSING ({type(exc).__name__})")

print()
print("=" * 84)
print("4. AmberTools: is antechamber on PATH for this interpreter?")
print("=" * 84)
import os
import shutil
for exe in ("antechamber", "sqm", "parmchk2", "tleap"):
    p = shutil.which(exe)
    print(f"  {exe:12s} {p if p else 'NOT FOUND'}")
print(f"  AMBERHOME={os.environ.get('AMBERHOME')!r}")

print()
print("=" * 84)
print("5. Direct test: ask for AM1-BCC charges on ethanol")
print("=" * 84)
try:
    from openff.toolkit import Molecule
    m = Molecule.from_smiles("CCO")
    m.assign_partial_charges("am1bcc")
    print(f"  am1bcc worked: {[round(float(q), 3) for q in m.partial_charges[:4]]} ...")
except Exception as exc:  # noqa: BLE001
    print(f"  am1bcc failed: {type(exc).__name__}: {str(exc)[:200]}")

print()
print("=" * 84)
print("6. Fallback that needs no external charge engine: Gasteiger via RDKit")
print("=" * 84)
try:
    from openff.toolkit import Molecule
    m = Molecule.from_smiles("CCO")
    m.assign_partial_charges("gasteiger")
    print(f"  gasteiger worked: {[round(float(q), 3) for q in m.partial_charges[:4]]} ...")
except Exception as exc:  # noqa: BLE001
    print(f"  gasteiger failed: {type(exc).__name__}: {str(exc)[:200]}")

print()
print("=" * 84)
print("VERDICT")
print("=" * 84)
print("""  If section 5 works, the failure is specific to how GAFFTemplateGenerator asks
  for charges and can be sidestepped by pre-assigning them on the Molecule before
  it is handed to the generator.
  If only section 6 works, the ligand can still be parameterised, with Gasteiger
  charges instead of AM1-BCC; that must be reported in the manuscript as a
  limitation of the ligand parameterisation.""")
