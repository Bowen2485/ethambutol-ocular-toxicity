# -*- coding: utf-8 -*-
"""Verify that Mao & Ou 2026 is cited in both manuscripts and the reference list."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

print("=" * 84)
print("Citation markers")
print("=" * 84)
for label, name in (("EN", "Ethambutol_EyeTox_EN_full.md"),
                    ("CN", "Ethambutol_EyeTox_CN_full.md")):
    t = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
    n28 = t.count("[28]") + t.count("〔28〕")
    print(f"  {label}: reference 28 cited {n28} time(s)")
    for idx in ([i + 1 for i, ln in enumerate(t.splitlines())
                 if "28" in ln and ("Mao" in ln or "Mao 与 Ou" in ln
                                    or "Mao and Ou" in ln)]):
        line = t.splitlines()[idx - 1].strip()
        print(f"      line {idx}: {line[:110]}")

print()
print("=" * 84)
print("Reference list")
print("=" * 84)
refs = (ROOT / "manuscript" / "references_en.md").read_text(encoding="utf-8")
has28 = "28. Mao Q" in refs
print(f"  reference 28 present in references_en.md: {has28}")
for ln in refs.splitlines():
    if ln.startswith("28."):
        print(f"      {ln[:150]}")

print()
print("=" * 84)
print("The old gap statement should be gone")
print("=" * 84)
old_en = "no analysis has yet placed EON's full ocular"
old_cn = "尚无研究在 FAERS 全库范围内、以术语级"
for label, name, old in (("EN", "Ethambutol_EyeTox_EN_full.md", old_en),
                         ("CN", "Ethambutol_EyeTox_CN_full.md", old_cn)):
    t = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
    print(f"  {label}: {'STILL PRESENT' if old in t else 'replaced'}")

print()
print("=" * 84)
print("New content checks")
print("=" * 84)
EN = ["Mao and Ou applied five signal-detection methods",
      "978 ethambutol reports from 2021Q1 to 2025Q3",
      "The one directly comparable FAERS analysis",
      "blurred vision (41.3% of ocular cases"]
CN = ["Mao 与 Ou 对四种一线抗结核药应用五种信号检测方法",
      "2021Q1–2025Q3 的 978 份乙胺丁醇报告",
      "唯一直接可比的 FAERS 分析",
      "视力模糊"]
for label, name, checks in (("EN", "Ethambutol_EyeTox_EN_full.md", EN),
                            ("CN", "Ethambutol_EyeTox_CN_full.md", CN)):
    t = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
    print(f"  {label}:")
    for k in checks:
        print(f"      {'OK ' if k in t else 'MISSING'}  {k[:66]}")
