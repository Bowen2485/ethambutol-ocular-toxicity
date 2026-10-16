# -*- coding: utf-8 -*-
"""
Close a gap in the Chinese section numbering that predates this work.

The file jumps from 3.7 to 3.11.  Nothing is missing - 3.8, 3.9 and 3.10 have no
counterpart in the Chinese version, because that version consolidated several of the English
subsections into its 3.4b-3.4e block - but a reader sees a jump and looks for the sections
that are not there.  The section is renumbered 3.8, which is what its position implies.

Any cross-reference to it is updated in the same pass, and the search covers both the
halfwidth and fullwidth forms of the numeral in case the text is inconsistent about which it
uses.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

t = CN.read_text(encoding="utf-8")

OLD = "### 3.11 网络节点在视网膜中表达，而铁死亡的类别层面检验未能提供信息"
NEW = "### 3.8 网络节点在视网膜中表达，而铁死亡的类别层面检验未能提供信息"

print("=" * 90)
print("1. Before")
print("=" * 90)
heads = re.findall(r"^### (3\.[0-9a-z]+)", t, re.M)
print(f"  section numbers: {heads}")
nums = [h for h in heads if h.count(".") == 1 and h[2:].isdigit()]
print(f"  plain-numbered: {nums}")

if OLD in t:
    t = t.replace(OLD, NEW)
    print("\n  renumbered 3.11 -> 3.8")
elif NEW in t:
    print("\n  already renumbered")
else:
    print("\n  heading not found verbatim")

# references to it elsewhere
refs_before = len(re.findall(r"3\.11(?=\s*节|节)", t))
t = re.sub(r"3\.11(?=\s*节)", "3.8", t)
print(f"  cross-references to 3.11节 rewritten: {refs_before}")

# a cross-reference may also be written as "见 3.11" without 节
loose = len(re.findall(r"见\s*3\.11", t))
t = re.sub(r"(见\s*)3\.11", r"\g<1>3.8", t)
print(f"  references of the form 见 3.11 rewritten: {loose}")

CN.write_text(t, encoding="utf-8")

print()
print("=" * 90)
print("2. After")
print("=" * 90)
for m in re.finditer(r"^### (3\.[0-9a-z]+) (.{0,46})", t, re.M):
    print(f"  {m.group(1):8s} {m.group(2)}")

heads = re.findall(r"^### (3\.[0-9a-z]+)", t, re.M)
dupes = {h for h in heads if heads.count(h) > 1}
plain = sorted(int(h.split(".")[1]) for h in heads
               if h.count(".") == 1 and h[2:].isdigit())
print()
print(f"  duplicate numbers: {sorted(dupes) if dupes else 'none'}")
print(f"  plain numbers in order: {plain}")
gaps = [b for a, b in zip(plain, plain[1:]) if b != a + 1]
print(f"  gaps in the plain numbering: {gaps if gaps else 'none'}")
print(f"  lines: {len(t.splitlines())}")
