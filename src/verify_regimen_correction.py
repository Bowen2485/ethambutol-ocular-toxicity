# -*- coding: utf-8 -*-
"""Verify the regimen-stratified correction landed in both manuscripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EN = [
    "once co-prescription is accounted for",
    "71.1% also name\nrifampicin",
    "73.3% of pyrazinamide cases",
    "A drug cannot be compared with another drug when most reports contain",
    "3.28 (1.03–10.40)",
    "The first row is the interpretable comparison",
    "845",
    "not evidence and are shown to be discounted",
    "Regimen-stratified comparison",
    "the first-line one",
]
CN = [
    "控制共用药之后",
    "71.1% 同时提及利福平",
    "73.3% 提及乙胺丁醇",
    "当多数报告同时含有两种药时",
    "3.28（1.03–10.40）",
    "第一行是唯一可解读的比较",
    "845",
    "其余各行不是证据",
    "方案分层比较",
    "一线药对照受共用药混杂",
]

for label, name, checks in (("EN", "Ethambutol_EyeTox_EN_full.md", EN),
                            ("CN", "Ethambutol_EyeTox_CN_full.md", CN)):
    t = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
    print(f"=== {label} ({len(t.splitlines())} lines, "
          f"{len(t.split())} words) ===")
    for k in checks:
        print(f"  {'OK ' if k in t else 'MISSING'}  {k[:70]}")
    print()

print("=== claims that should no longer stand alone ===")
for label, name, bad in (
    ("EN", "Ethambutol_EyeTox_EN_full.md",
     "Within the antitubercular class ethambutol is high but not the highest"),
    ("EN", "Ethambutol_EyeTox_EN_full.md",
     "ethambutol's optic-neuropathy ratio exceeds isoniazid"),
    ("CN", "Ethambutol_EyeTox_CN_full.md",
     "**高于同方案一线药**——异烟肼 1.47"),
    ("CN", "Ethambutol_EyeTox_CN_full.md",
     "但低于部分用于耐药结核的二线药，不能据此断言其毒性最强"),
):
    t = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
    print(f"  {label}: {'STILL PRESENT' if bad in t else 'removed'}  -- {bad[:56]}")
