# -*- coding: utf-8 -*-
"""Verify the reporting-intensity edits landed in both manuscripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EN_CHECKS = [
    "Tuberculosis burden denominator",
    "Spearman rho = -0.14",
    "834.5",
    "229 times higher",
    "reporting artefact and is not given a clinical",
    "not interpreted",
    "reporting intensity cancels",
    "no result here is interpreted geographically",
    "MDG_0000000020",
]
CN_CHECKS = [
    "结核负担分母",
    "834.5",
    "0.14",
    "229",
    "报告假象",
    "不予解读",
    "报告强度自然约掉",
    "WHO 结核通报",
]

for label, path, checks in (
        ("EN", ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md", EN_CHECKS),
        ("CN", ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md", CN_CHECKS)):
    t = path.read_text(encoding="utf-8")
    print(f"=== {label} ({len(t.splitlines())} lines) ===")
    for k in checks:
        print(f"  {'OK ' if k in t else 'MISSING'}  {k}")
    print()

# the old unqualified Europe claim must be gone from both
print("=== the unqualified regional claim should be gone ===")
for label, path, bad in (
        ("EN", ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md",
         "and reporting from Europe (1.358, 1.151-1.601)"),
        ("CN", ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md",
         "欧洲报告者（1.358）")):
    t = path.read_text(encoding="utf-8")
    print(f"  {label}: {'STILL PRESENT' if bad in t else 'removed'}")
