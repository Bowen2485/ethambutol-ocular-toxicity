# -*- coding: utf-8 -*-
"""Verify the heavy-atom correction landed everywhere, in both manuscripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STALE = ["ten heavy atoms", "10 个重原子", "ten heavy", "three rotatable bonds",
         "3 个可旋转键", "sits inside the validated range", "位于已验证区间之内"]
FRESH_EN = ["fourteen heavy", "nine rotatable bonds",
            "brackets but does not", "falls in the gap the panel brackets",
            "one atom above the largest ligand that passed"]
FRESH_CN = ["14 个重原子", "9 个可旋转键", "括住但未填充"]

for label, name, fresh in (
        ("EN", "Ethambutol_EyeTox_EN_full.md", FRESH_EN),
        ("CN", "Ethambutol_EyeTox_CN_full.md", FRESH_CN)):
    t = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
    print(f"=== {label} ({len(t.splitlines())} lines) ===")
    print("  stale claims that must be gone:")
    for k in STALE:
        print(f"      {'STILL PRESENT' if k in t else 'removed      '}  {k}")
    print("  corrected claims that must be present:")
    for k in fresh:
        print(f"      {'OK     ' if k in t else 'MISSING'}  {k}")
    print()

print("=== reference values, for the record ===")
print("  ethambutol  C10H24N2O2 -> 14 heavy atoms, 9 rotatable bonds")
print("  panel       passing: 9 and 13 heavy atoms")
print("              failing: 19, 22, 33, 36 heavy atoms")
print("              ethambutol at 14 sits between 13 and 19")
