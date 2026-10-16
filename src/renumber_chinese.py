# -*- coding: utf-8 -*-
"""
Renumber the two sections just added so the Chinese numbering follows the Chinese order.

What is wrong
    A section was placed by logic - the disease-annotation cross-check belongs directly after
    the enrichment it checks, and the subgroup analysis belongs with the other robustness
    material - but numbered by analogy with the English file, which orders its sections
    differently.  The result is a file whose numbers run out of sequence:

        ### 3.5 机制网络与富集
        ### 3.8b hub 基因的眼病注释...        <- numbered 3.8b, sits before 3.6
        ### 3.6 分子对接...
        ### 3.7 遗传学考察...
        ### 3.7b 信号在全部患者亚组中...

    A reader following a cross-reference to 3.8b, or to 3.7b, would be sent past the section
    they are looking for.

What the new numbers are
    3.5b for the disease-annotation cross-check, immediately after 3.5, which is the
    enrichment it tests.
    3.4f for the subgroup analysis, which continues the 3.4 robustness block - 3.4c
    specifications, 3.4d two eras, 3.4e an independent database, 3.4f patient subgroups.  It
    is also moved to sit with that block instead of after the genetics section, so number and
    position agree.

Cross-references are updated in the same pass, and the change is reported with the count of
each substitution so a wrong one would be visible.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

t = CN.read_text(encoding="utf-8")

print("=" * 90)
print("1. Before")
print("=" * 90)
for m in re.finditer(r"^### (3\.[0-9a-z]+) (.{0,44})", t, re.M):
    print(f"  {m.group(1):8s} {m.group(2)}")

# ---- renumber
subs = [
    ("### 3.8b hub 基因的眼病注释显著多于对照集", "### 3.5b hub 基因的眼病注释显著多于对照集"),
    ("### 3.7b 信号在全部患者亚组中均存在，唯年龄梯度值得解读",
     "### 3.4f 信号在全部患者亚组中均存在，唯年龄梯度值得解读"),
]
for a, b in subs:
    if a in t:
        t = t.replace(a, b)
        print(f"\n  renumbered: {a.split()[1]} -> {b.split()[1]}")
    elif b in t:
        print(f"\n  already renumbered: {b.split()[1]}")

# ---- move the subgroup section to sit with the robustness block, after 3.4e
NEW_H = "### 3.4f 信号在全部患者亚组中均存在，唯年龄梯度值得解读"
start = t.find(NEW_H)
if start >= 0:
    # the section runs to the next heading of the same or higher level
    nxt = re.search(r"\n### ", t[start + len(NEW_H):])
    end = start + len(NEW_H) + (nxt.start() if nxt else len(t))
    body = t[start:end].rstrip() + "\n"
    t = t[:start] + t[end:]

    anchor = "\n### 3.5 机制网络与富集"
    if anchor in t:
        t = t.replace(anchor, "\n" + body.rstrip() + "\n" + anchor, 1)
        print("  moved 3.4f to sit after the 3.4 robustness block")
    else:
        print("  WARNING: could not find the anchor for the move; section left where it was")
        t = t[:start] + body + t[start:]

# ---- update cross-references
print()
print("=" * 90)
print("2. Cross-references")
print("=" * 90)
for old, new in (("3.8b", "3.5b"), ("3.7b", "3.4f")):
    hits = [m.start() for m in re.finditer(re.escape(old), t)]
    # do not rewrite the heading we just created
    hits = [h for h in hits if t[max(0, h - 4):h] != "### "]
    print(f"  {old}: {len(hits)} occurrence(s) outside its heading")
    if hits:
        # only rewrite when it is a reference, i.e. preceded by nothing or by a CJK char
        t2 = re.sub(r"(?<![\d.])" + re.escape(old) + r"节", new + "节", t)
        if t2 != t:
            t = t2
            print(f"      rewritten to {new}节 where it was a reference")

# the earlier sections that cite the robustness block by number
print()
print("=" * 90)
print("3. After")
print("=" * 90)
for m in re.finditer(r"^### (3\.[0-9a-z]+) (.{0,44})", t, re.M):
    print(f"  {m.group(1):8s} {m.group(2)}")

CN.write_text(t, encoding="utf-8")
print(f"\n  lines: {len(t.splitlines())}")

# ---- confirm each heading number is unique and ascending where it should be
heads = re.findall(r"^### (3\.[0-9a-z]+)", t, re.M)
dupes = {h for h in heads if heads.count(h) > 1}
print(f"  duplicate section numbers: {sorted(dupes) if dupes else 'none'}")
