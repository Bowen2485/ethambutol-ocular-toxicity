# -*- coding: utf-8 -*-
"""
Cross-check the two manuscripts against each other.

The English and Chinese versions have been edited in parallel for many rounds, and the
changes have not always been mirrored: an audit during this session found the English
version missing its figure-and-table list and the Chinese version carrying the reference
section twice.  Both were found by looking at structure, not by reading, so this script
does the same for the numbers.

Three checks:
    1. key quantities - every headline figure must appear in both versions, with the
       same value
    2. section coverage - sections present in one version and not the other
    3. analysis coverage - the named analyses must be described in both
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")

print("=" * 100)
print("1. Headline quantities that must agree between the versions")
print("=" * 100)
# (label, value as it should appear in each version)
KEY = [
    ("FAERS de-duplicated cases", "20,328,568", "20 328 568"),
    ("ethambutol cases", "13,804", "13 804"),
    ("ocular events", "971", "971"),
    ("ocular proportion", "7.03%", "7.03%"),
    ("optic-nerve proportion", "3.44%", "3.44%"),
    ("optic neuropathy a", "153", "153"),
    ("optic neuropathy ROR", "159.21", "159.21"),
    ("toxic optic neuropathy ROR", "277.14", "277.14"),
    ("within-class ROR", "6.47", "6.47"),
    ("regimen rate ratio", "3.28", "3.28"),
    ("regimen CI lower", "1.03", "1.03"),
    ("smaller group n", "845", "845"),
    ("co-prescription rifampicin", "71.1", "71.1"),
    ("co-prescription pyrazinamide", "73.3", "73.3"),
    ("temporal early ROR", "81.9", "81.9"),
    ("temporal late ROR", "86.9", "86.9"),
    ("JADER cases", "1,054,239", "1 054 239"),
    ("JADER optic neuropathy ROR", "571.0", "571.0"),
    ("JADER toxic optic ROR", "864.6", "864.6"),
    ("TB denominator rho", "0.14", "0.14"),
    ("US reports per burden", "834.5", "834.5"),
    ("South Africa multiplier", "229", "229"),
    ("heavy atoms", "fourteen heavy", "14 个重原子"),
    ("rotatable bonds", "nine rotatable", "9 个可旋转键"),
    ("redocking panel size", "9 to 36 heavy atoms", "9 至 36"),
]
bad = 0
for label, en_v, cn_v in KEY:
    in_en, in_cn = en_v in EN, cn_v in CN
    if in_en and in_cn:
        mark = "ok"
    else:
        mark = "MISMATCH"
        bad += 1
    print(f"  {label:32s} EN {'yes' if in_en else 'NO ':3s}  "
          f"CN {'yes' if in_cn else 'NO ':3s}  {mark}")
print()
print(f"  quantities failing in at least one version: {bad} of {len(KEY)}")

print()
print("=" * 100)
print("2. Section coverage")
print("=" * 100)
en_heads = {re.sub(r"^#+\s*", "", ln).strip()
            for ln in EN.splitlines() if ln.startswith("##")}
cn_heads = {re.sub(r"^#+\s*", "", ln).strip()
            for ln in CN.splitlines() if ln.startswith("##")}
print(f"  EN headings: {len(en_heads)}   CN headings: {len(cn_heads)}")
print()
print("  headings only in EN:")
for h in sorted(en_heads):
    print(f"      {h[:80]}")
print()
print("  headings only in CN:")
for h in sorted(cn_heads):
    print(f"      {h[:80]}")

print()
print("=" * 100)
print("3. Analyses that must be described in both")
print("=" * 100)
ANALYSES = [
    ("within-class comparison", "within the antitubercular class", "类内"),
    ("regimen stratification", "Regimen-stratified", "方案分层"),
    ("temporal split", "temporal", "时间切分"),
    ("JADER replication", "JADER", "JADER"),
    ("TB burden denominator", "Tuberculosis burden", "结核负担"),
    ("negative controls", "negative-control", "阴性对照"),
    ("docking validation panel", "redocking panel", "回对接面板"),
    ("molecular dynamics", "molecular dynamics", "分子动力学"),
    ("Mendelian randomisation", "Mendelian randomisation", "孟德尔随机化"),
    ("network toxicology", "network toxicolog", "网络毒理"),
    ("report adequacy", "adequacy", "充分性"),
    ("STROBE/RECORD", "STROBE", "STROBE"),
]
for label, en_k, cn_k in ANALYSES:
    e, c = en_k.lower() in EN.lower(), cn_k.lower() in CN.lower()
    print(f"  {label:30s} EN {'yes' if e else 'NO ':3s}  "
          f"CN {'yes' if c else 'NO ':3s}  "
          f"{'ok' if e and c else 'CHECK'}")

print()
print("=" * 100)
print("4. Length and structure")
print("=" * 100)
print(f"  EN: {len(EN.splitlines()):>5} lines, {len(EN.split()):>6} words")
cn_words = len(re.findall(r"[\u4e00-\u9fff]", CN))
print(f"  CN: {len(CN.splitlines()):>5} lines, {cn_words:>6} Chinese characters")
print(f"  EN figures referenced: {sorted({int(m) for m in re.findall(r'Figure (\\d+)', EN)})}")
print(f"  CN figures referenced: {sorted({int(m) for m in re.findall(r'图 ?(\\d+)', CN)})}")
