# -*- coding: utf-8 -*-
"""
Derive the correct force sign empirically instead of by argument.

Two attempts at reasoning about the sign have produced inconsistent results, so the
implementation is validated against the definition of force: F = -dU/dx, evaluated by
finite differences.  Whatever sign convention makes the analytic force agree with the
numerical gradient is the correct one, and it is then written into the module.
"""
from __future__ import annotations

import numpy as np

K_CONTACT = 1.0
EPS_CONTACT = 0.35
R0 = 4.0


def energy(d: float) -> float:
    """Contact potential between one ligand bead and one receptor bead."""
    if d < R0:
        return K_CONTACT * (R0 - d) ** 2
    return -EPS_CONTACT * (1.0 - np.exp(-(d - R0)))


print("=" * 76)
print("Definition check: is the potential sane?")
print("=" * 76)
print(f"{'d':>6} {'U(d)':>12}   note")
for d in (2.0, 3.0, 4.0, 5.0, 7.0, 10.0):
    note = "repulsive core" if d < R0 else ("minimum" if d == R0 else "attractive well")
    print(f"{d:>6.1f} {energy(d):>12.4f}   {note}")

print()
print("=" * 76)
print("Numeric force on the ligand: F_x = -dU/dx, with the receptor at the origin")
print("=" * 76)


def numeric_force(d: float, h: float = 1e-5) -> float:
    """Central difference of U with respect to the ligand's x coordinate."""
    return -(energy(d + h) - energy(d - h)) / (2 * h)


print(f"{'d':>6} {'-dU/dx':>12}   direction the ligand should be pushed")
for d in (2.0, 3.0, 3.9, 4.1, 5.0, 7.0, 10.0):
    fx = numeric_force(d)
    if d < R0:
        want = "outwards, i.e. +x (away from the receptor)"
    elif d > R0:
        want = "inwards, i.e. -x (towards the receptor)"
    else:
        want = "zero"
    print(f"{d:>6.1f} {fx:>12.4f}   {want}")

print()
print("=" * 76)
print("So the ligand force is:")
print("  d < R0 :  +2*K*(R0 - d) * (dv/dist)   [positive along +x]")
print("  d > R0 :  -EPS*exp(-(d-R0)) * (dv/dist)  [negative along +x]")
print("  Combining:  F_ligand = -(drep + datt) / dist * dv")
print("  where drep and datt are the derivatives of U, and the whole expression")
print("  carries a leading minus sign.  The receptor takes the opposite force.")
print()
print("  A second error is visible in the previous code: datt was written as")
print("  -EPS*exp(...), i.e. already the force rather than the derivative, while")
print("  drep was written as the derivative.  The two branches therefore needed")
print("  opposite signs and no single sign could satisfy both.  The fix is to use")
print("  the derivative consistently and negate once.")
print()


def analytic_ligand_force(d: float) -> float:
    dv = np.array([[d, 0.0, 0.0]])       # ligand - receptor
    dist = np.array([d])
    # derivatives of the potential with respect to distance
    if d < R0:
        dU = -2.0 * K_CONTACT * (R0 - d)
    else:
        dU = -EPS_CONTACT * np.exp(-(d - R0))
    # F = -dU/dx  with  dU/dx = dU/dd * dv/dist
    fvec = (dU / dist)[:, None] * dv
    return float(-fvec[0, 0])


print("=" * 76)
print("Verification of the corrected analytic expression")
print("=" * 76)
ok = True
print(f"{'d':>6} {'numeric':>12} {'analytic':>12} {'agree':>8}")
for d in (2.0, 3.0, 3.9, 4.1, 5.0, 7.0, 10.0):
    fn, fa = numeric_force(d), analytic_ligand_force(d)
    agree = abs(fn - fa) < 1e-6
    ok &= agree
    print(f"{d:>6.1f} {fn:>12.6f} {fa:>12.6f} {str(agree):>8}")

print()
print("VERDICT:", "the corrected expression matches the numerical gradient everywhere"
      if ok else "still inconsistent")
raise SystemExit(0 if ok else 1)
