# -*- coding: utf-8 -*-
"""
Find the correct byte offset of the atom count in a DCD header, by measurement.

Why measurement rather than another guess
    Two offsets have now been tried and both were wrong.  The first read offset 8 and
    returned 26 for HMOX1 and 150 for NFE2L2, which are frame counts.  The second read
    offset 4 and returned 1146244931, which is the integer formed by the ASCII bytes
    "CORD" - so the magic number sits at offset 4, not the atom count.  Guessing a third
    time would be the same mistake again.

The method
    A DCD describes a system whose atom count is known independently, from the
    complex.pdb written alongside it.  Reading every 4-byte-aligned offset out of the
    first 128 bytes and comparing each against that known value identifies the field
    unambiguously, and the same offset should hold for every target.  Whatever this
    prints is the answer; nothing is assumed.

Run in WSL:
    ~/miniconda3/envs/md/bin/python src/probe_dcd_header.py
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np

try:
    import mdtraj as md
except ImportError:
    sys.exit("mdtraj not installed; run this inside the md environment")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "md_allatom"

print("=" * 88)
print("1. Atom counts known independently, from each complex.pdb")
print("=" * 88)
known: dict[str, int] = {}
for d in sorted(OUT.iterdir()):
    if not d.is_dir():
        continue
    pdb = d / "complex.pdb"
    if not pdb.exists():
        continue
    try:
        n = md.load_topology(str(pdb)).n_atoms
    except Exception as exc:  # noqa: BLE001
        print(f"  {d.name:8s} topology unreadable: {type(exc).__name__}")
        continue
    known[d.name] = n
    print(f"  {d.name:8s} {n:>8,} atoms in complex.pdb")
if not known:
    sys.exit("no complex.pdb files found")

print()
print("=" * 88)
print("2. Every 4-byte offset in the first 128 bytes of each trajectory")
print("=" * 88)
trajs: list[tuple[str, Path, int]] = []
for d in sorted(OUT.iterdir()):
    if not d.is_dir() or d.name not in known:
        continue
    for t in sorted(d.glob("traj*.dcd")):
        trajs.append((d.name, t, known[d.name]))
if not trajs:
    sys.exit("no trajectories found")

for gene, path, expect in trajs:
    with open(path, "rb") as fh:
        head = fh.read(128)
    print(f"\n  {gene}  {path.name}  (expect {expect:,} atoms, "
          f"{path.stat().st_size/1e6:.1f} MB)")
    print(f"    first 32 bytes: {head[:32]!r}")
    hits = []
    for off in range(0, min(len(head), 128) - 3, 4):
        v = int(np.frombuffer(head[off:off + 4], dtype="<i4")[0])
        mark = ""
        if v == expect:
            mark = "   <== MATCHES the atom count"
            hits.append(off)
        # a plausible frame count would be the trajectory length in frames
        print(f"    offset {off:>3}: {v:>14,}{mark}")
    if hits:
        print(f"    -> atom count found at offset(s): {hits}")
    else:
        print(f"    -> no offset in the first 128 bytes equals {expect:,}; the count "
              f"may live beyond 128 bytes")

print()
print("=" * 88)
print("3. Offset consistent across all targets")
print("=" * 88)
common: set[int] | None = None
for gene, path, expect in trajs:
    with open(path, "rb") as fh:
        head = fh.read(128)
    found = {off for off in range(0, min(len(head), 128) - 3, 4)
             if int(np.frombuffer(head[off:off + 4], dtype="<i4")[0]) == expect}
    print(f"  {gene:8s} offsets matching: {sorted(found) if found else 'none'}")
    common = found if common is None else (common & found)
print()
if common:
    off = sorted(common)[0]
    print(f"  A single offset matches every target: {off}")
    print(f"  Use head[{off}:{off + 4}] as the atom count.")
    for gene, path, expect in trajs:
        with open(path, "rb") as fh:
            head = fh.read(128)
        print(f"    {gene:8s} -> {int(np.frombuffer(head[off:off + 4], dtype='<i4')[0]):,}"
              f"  (expected {expect:,})")
else:
    print("  No offset matches every target, so the field position is not shared.")
    print("  Report this output and the reader will be built from what is shown.")
