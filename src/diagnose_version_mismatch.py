# -*- coding: utf-8 -*-
"""
Pin down the three mismatches the cross-check reported.

    1. the JADER case count appears in the English version but not the Chinese one
    2. the Chinese version does not mention STROBE or RECORD anywhere
    3. figure references came back empty from both, which is more likely a bad regular
       expression than two manuscripts without figures

Each is checked directly here so the fix is aimed at the real cause.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")

print("=" * 96)
print("1. Where the JADER case count appears")
print("=" * 96)
for label, text, pats in (
        ("EN", EN, [r"1,054,239", r"1054239", r"1\.05 million", r"1,054"]),
        ("CN", CN, [r"1\s*054\s*239", r"1054239", r"105 万", r"1,054,239"])):
    print(f"  {label}:")
    for p in pats:
        hits = [m.start() for m in re.finditer(p, text)]
        if hits:
            for h in hits[:3]:
                line = text[:h].count("\n") + 1
                snippet = text[max(0, h - 70):h + 60].replace("\n", " ")
                print(f"      {p!r:16s} line {line}: ...{snippet}...")
        else:
            print(f"      {p!r:16s} not found")

print()
print("=" * 96)
print("2. Reporting guidelines mentioned in each version")
print("=" * 96)
for label, text in (("EN", EN), ("CN", CN)):
    print(f"  {label}:")
    for k in ("STROBE", "RECORD", "STROBE-MR", "checklist", "报告规范",
              "清单", "声明"):
        n = text.count(k)
        print(f"      {k:14s} {n} occurrence(s)")

print()
print("=" * 96)
print("3. Figure and table references, with several patterns")
print("=" * 96)
PATTERNS = {
    "EN 'Figure N'": (EN, r"Figure\s+(\d+)"),
    "EN 'Figure' any": (EN, r"Figure"),
    "EN 'Fig. N'": (EN, r"Fig\.\s*(\d+)"),
    "CN '图N'": (CN, r"图\s*(\d+)"),
    "CN '**图N**'": (CN, r"\*\*图\s*(\d+)\*\*"),
    "CN '图' any": (CN, r"图"),
}
for label, (text, pat) in PATTERNS.items():
    hits = re.findall(pat, text)
    if hits and hits[0].isdigit():
        print(f"  {label:18s} {len(hits):>4} -> {sorted({int(x) for x in hits})}")
    else:
        print(f"  {label:18s} {len(hits):>4} occurrences")

print()
print("  sample lines containing a figure reference in each:")
for label, text, pat in (("EN", EN, r"Figure\s*\d"), ("CN", CN, r"图\s*\d")):
    print(f"    {label}:")
    shown = 0
    for ln in text.splitlines():
        if re.search(pat, ln):
            print(f"        {ln.strip()[:104]}")
            shown += 1
            if shown >= 4:
                break

print()
print("=" * 96)
print("4. Does the Chinese version have the analyses the English one reports?")
print("=" * 96)
# markers that must be present if the analysis is described
MARKERS = [
    ("JADER sample size", "1 054 239", "1,054,239"),
    ("JADER suspect coding", "被疑薬", "被疑薬"),
    ("temporal split point", "2016", "2016"),
    ("negative control list", "dry eye", "干眼"),
    ("regimen strata table", "5,757", "5 757"),
    ("force field naming", "GAFF", "GAFF"),
    ("dynamics duration", "1 ns", "1 ns"),
    ("MR instrument count", "186", "186"),
]
for label, en_k, cn_k in MARKERS:
    print(f"  {label:24s} EN {'yes' if en_k in EN else 'NO ':3s}   "
          f"CN {'yes' if cn_k in CN else 'NO ':3s}   (looking for {en_k!r} / {cn_k!r})")
