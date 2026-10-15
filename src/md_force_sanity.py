# -*- coding: utf-8 -*-
"""
Minimal sanity test of the ligand-receptor force.

A ligand held by contacts that are scaled 50x should be pulled back towards the
pocket; instead it drifts away, which is physically wrong and points at a sign or
reference error in the force rather than at the pose.  This test removes everything
else: a single ligand bead is placed near a single receptor bead, displaced from the
well minimum, and the resulting force is inspected.

A correct implementation must pull the ligand towards the minimum when it is beyond
it, and push it away when it is inside it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import md_coarse as md  # noqa: E402


def probe(dist: float, r0: float):
    """One ligand bead at `dist` from one receptor bead; well minimum at r0."""
    pos = np.array([[0.0, 0.0, 0.0],       # receptor bead
                    [dist, 0.0, 0.0]])     # ligand bead
    pairs = np.zeros((0, 2), dtype=int)
    r0s = np.zeros(0)
    lig_pairs = np.zeros((0, 2), dtype=int)
    lig_r0 = np.zeros(0)
    li = np.array([0])
    ri = np.array([0])
    lr0 = np.array([r0])
    e, f = md.energy_forces(pos, 1, pairs, r0s, li, ri, lr0, lig_pairs, lig_r0)
    # force on the ligand bead along +x
    return e, f[1, 0]


print("=" * 76)
print("Ligand-receptor force sign test")
print("=" * 76)
r0 = 4.0
print(f"well minimum at r0 = {r0} A; ligand bead placed at various distances")
print(f"{'distance':>10} {'energy':>12} {'force_on_ligand_x':>20}   expectation")
print("(the receptor sits at x = 0, so inside the minimum the ligand is pushed")
print(" outwards, +x, and beyond it it is pulled back, -x)")
ok = True
for dist in (2.0, 3.0, 3.9, 4.0, 4.1, 5.0, 7.0, 10.0):
    e, fx = probe(dist, r0)
    if dist < r0 - 1e-9:
        want = "push outwards (+x)"
        good = fx > 0
    elif dist > r0 + 1e-9:
        want = "pull back (-x)"
        good = fx < 0
    else:
        # the two branches meet at the minimum; the well is continuous but not
        # smooth there, so only finiteness is required
        want = "finite"
        good = np.isfinite(fx)
    ok &= good
    print(f"{dist:>10.2f} {e:>12.4f} {fx:>20.4f}   {want}"
          f"{'' if good else '   <-- WRONG SIGN'}")

print()
print("=" * 76)
print("VERDICT")
print("=" * 76)
print("  force field behaves correctly" if ok else
      "  the ligand-receptor force has the wrong sign, which would invalidate any\n"
      "  pose-stability result computed from it")
sys.exit(0 if ok else 1)
