# -*- coding: utf-8 -*-
"""
Settle the force sign with a test that cannot be mis-specified: energy monotonicity.

Stepping a small distance along the force must lower the potential energy.  This holds
by definition of a force as the negative gradient, so the test does not depend on my
getting a sign convention right by argument - which has now gone wrong three times.

The script also validates its own tooling first: it checks that the finite-difference
helper reproduces a potential whose gradient is known analytically, so a failure
elsewhere can be attributed correctly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import md_coarse as md  # noqa: E402

# ------------------------------------------------------------------ self-check
print("=" * 76)
print("0. Validate the test harness against a potential with a known gradient")
print("=" * 76)


def known_u(d):
    return 0.5 * d ** 2          # U = d^2/2, so -dU/dd = -d


def fd_grad(f, d, h=1e-6):
    return (f(d + h) - f(d - h)) / (2 * h)


for d in (1.0, 2.5):
    got = -fd_grad(known_u, d)
    print(f"   d={d}: -dU/dd from finite differences = {got:.6f}, "
          f"analytic = {-d:.6f}, match = {abs(got + d) < 1e-8}")
harness_ok = all(abs(-fd_grad(known_u, d) + d) < 1e-8 for d in (1.0, 2.5))
print(f"   harness sane: {harness_ok}")

# ------------------------------------------------------- energy monotonicity
print()
print("=" * 76)
print("1. Does stepping along the computed force lower the energy?")
print("=" * 76)
R0 = 4.0


def total_energy(x_lig: float) -> float:
    """Potential of a one-ligand, one-receptor bead system at separation x_lig."""
    pos = np.array([[0.0, 0.0, 0.0], [x_lig, 0.0, 0.0]])
    e, _ = md.energy_forces(
        pos, 1,
        np.zeros((0, 2), dtype=int), np.zeros(0),
        np.array([0]), np.array([0]), np.array([R0]),
        np.zeros((0, 2), dtype=int), np.zeros(0))
    return e


def ligand_force(x_lig: float) -> np.ndarray:
    pos = np.array([[0.0, 0.0, 0.0], [x_lig, 0.0, 0.0]])
    _, f = md.energy_forces(
        pos, 1,
        np.zeros((0, 2), dtype=int), np.zeros(0),
        np.array([0]), np.array([0]), np.array([R0]),
        np.zeros((0, 2), dtype=int), np.zeros(0))
    return f[1]


# the analytic gradient of this potential, obtained by finite differences on the
# module's OWN energy function, which is the ground truth
print(f"{'separation':>11} {'U':>10} {'F_x (module)':>14} {'-dU/dx (numeric)':>18} "
      f"{'agree':>7}")
all_ok = True
for x in (2.0, 3.0, 3.9, 4.1, 5.0, 7.0, 10.0):
    u = total_energy(x)
    fx = float(ligand_force(x)[0])
    num = -fd_grad(total_energy, x, h=1e-5)
    agree = abs(fx - num) < 1e-4 * max(1.0, abs(num))
    all_ok &= agree
    print(f"{x:>11.2f} {u:>10.4f} {fx:>14.5f} {num:>18.5f} {str(agree):>7}")

print()
print("=" * 76)
print("2. Monotonicity: move the ligand a little along +F and compare energies")
print("=" * 76)
print(f"{'separation':>11} {'U before':>11} {'U after':>11} {'lowered':>9}  verdict")
mono_ok = True
for x in (2.0, 3.0, 3.9, 4.1, 5.0, 7.0, 10.0):
    fx = float(ligand_force(x)[0])
    if abs(fx) < 1e-9:
        continue
    step = 1e-4 * np.sign(fx)
    u0 = total_energy(x)
    u1 = total_energy(x + step)
    lowered = u1 < u0
    # at the minimum the force is small and either sign is acceptable
    near_min = abs(x - R0) < 0.05
    ok = lowered or near_min
    mono_ok &= ok
    print(f"{x:>11.2f} {u0:>11.5f} {u1:>11.5f} {str(lowered):>9}  "
          f"{'ok' if ok else 'FORCE POINTS UPHILL'}")

print()
print("=" * 76)
print("VERDICT")
print("=" * 76)
print(f"  finite-difference harness sane : {harness_ok}")
print(f"  module force equals -dU/dx     : {all_ok}")
print(f"  force is downhill everywhere   : {mono_ok}")
if harness_ok and all_ok and mono_ok:
    print("\n  The ligand-receptor force is correct: it equals the negative gradient of")
    print("  the potential, verified against the module's own energy function.")
    sys.exit(0)
print("\n  A problem remains; see the table above.")
sys.exit(1)
