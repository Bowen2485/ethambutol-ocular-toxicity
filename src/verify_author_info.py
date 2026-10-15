# -*- coding: utf-8 -*-
"""Verify the author information landed correctly in both manuscripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")

print("=" * 90)
print("1. Author block")
print("=" * 90)
AUTHORS = ["Bowen Shi", "Jing Yan", "Zhengzheng Wu", "Siyuan Yang", "Yaqin Tan",
           "Xuan Wang"]
for a in AUTHORS:
    print(f"  {a:16s} EN {'ok' if a in EN else 'MISSING'}")
print()
CN_NAMES = ["史博文", "严京", "吴正正", "杨思远", "谭雅琴", "王萱"]
for n in CN_NAMES:
    print(f"  {n:16s} CN {'ok' if n in CN else 'MISSING'}")

print()
print("=" * 90)
print("2. Affiliation and corresponding author")
print("=" * 90)
CHECKS_EN = [
    "Eye Hospital, China Academy of Chinese Medical Sciences",
    "33 Lugu Road, Shijingshan District, Beijing 100040",
    "20200121047@bucm.edu.cn",
    "Corresponding author",
    "Bowen Shi¹, Jing Yan¹*, Zhengzheng Wu¹, Siyuan Yang¹, Yaqin Tan¹, Xuan Wang¹",
]
CHECKS_CN = [
    "中国中医科学院眼科医院",
    "鲁谷路 33 号",
    "100040",
    "20200121047@bucm.edu.cn",
    "通讯作者",
    "史博文¹，严京¹*，吴正正¹，杨思远¹，谭雅琴¹，王萱¹",
]
# the earlier address must be gone from both
STALE = ["<old address removed>"]
for k in CHECKS_EN:
    print(f"  EN {'ok     ' if k in EN else 'MISSING'}  {k}")
for k in CHECKS_CN:
    print(f"  CN {'ok     ' if k in CN else 'MISSING'}  {k}")

print()
print("  the earlier address must no longer appear:")
for k in STALE:
    print(f"      EN {'STILL PRESENT' if k in EN else 'removed'}   "
          f"CN {'STILL PRESENT' if k in CN else 'removed'}   {k}")

print()
print("=" * 90)
print("3. CRediT statement")
print("=" * 90)
CREDIT = ["Conceptualization", "Methodology", "Software", "Validation",
          "Formal analysis", "Investigation", "Resources", "Data curation",
          "Writing – original draft", "Writing – review & editing",
          "Visualization", "Supervision", "Project administration",
          "Funding acquisition"]
for c in CREDIT:
    print(f"  {c:28s} EN {'ok' if c in EN else 'MISSING'}   "
          f"CN {'ok' if c in CN else 'MISSING'}")

print()
print("=" * 90)
print("4. What is still pending")
print("=" * 90)
for label, text in (("EN", EN), ("CN", CN)):
    for k in ("[to be inserted]", "[待填入]", "repository URL",
              "[待填入仓库地址]"):
        if k in text:
            print(f"  {label}: still contains {k!r}")

print()
print("=" * 90)
print("5. Size")
print("=" * 90)
print(f"  EN: {len(EN.splitlines()):>5} lines, {len(EN.split()):>6} words")
print(f"  CN: {len(CN.splitlines()):>5} lines")
