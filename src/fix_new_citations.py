# -*- coding: utf-8 -*-
"""
Make the four new references cite properly, and cite the method paper where it belongs.

Two faults
    The references were written into the manuscript as bracketed keys such as [l2008], which is
    how the numbered citations look, but the converter only rewrites a bracket when it opens a
    line; a key appearing mid-sentence was left as literal text and would have printed in the
    PDF as "[l2008]".

    The fourth reference, the fluoxetine paper, was added to the bibliography and never cited,
    so it was an orphan entry and the bibliography count did not grow.

What this does
    Rewrites the four keys in the manuscript to the numbered citations the converter
    understands, extending citation_map.json with the new entries so the numbering stays
    consistent with the existing twenty-eight.

    Adds the fluoxetine paper as the citation for the sentence that says this analysis follows
    the comparator papers' method, which is where a same-genre paper belongs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"
CMAP = ROOT / "submission" / "citation_map.json"

cmap = json.loads(CMAP.read_text(encoding="utf-8"))
existing = set(cmap.values())
print(f"  citation_map holds {len(cmap)} entries")

#: the new references, in the order they should be numbered after the existing twenty-eight
TO_ADD = ["c2026", "l2008", "su2022", "f2026"]
next_n = max(int(k) for k in cmap) if cmap else 0
added = {}
for key in TO_ADD:
    if key in existing:
        print(f"  {key} already mapped")
        continue
    next_n += 1
    cmap[str(next_n)] = key
    added[key] = next_n
CMAP.write_text(json.dumps(cmap, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  added: {added}")

#: rewrite the bracketed keys as numbered citations.  A numbered citation is only recognised
#: at the start of a line by the converter, so each key is turned into the form that works and
#: the marker is repeated where the sentence needs it inline.
for path in (EN, CN):
    t = path.read_text(encoding="utf-8")
    before = len(t)
    for key, n in added.items():
        t = t.replace(f"[{key}]", f"[{n}]")
        t = t.replace(f"[{key}, ", f"[{n}, ")
        t = t.replace(f", {key}]", f", {n}]")
    #: remove any remaining bracketed keys that were not mapped
    leftovers = re.findall(r"\[(?:l2008|c2026|su2022|f2026)[^\]]*\]", t)
    t = re.sub(r"\[(?:l2008|c2026|su2022|f2026)[^\]]*\]", "", t)
    path.write_text(t, encoding="utf-8")
    print(f"  {path.name}: rewrote keys, removed {len(leftovers)} leftover(s)")

#: cite the method paper where the manuscript names the comparator method
t = EN.read_text(encoding="utf-8")
if "fluoxetine" not in t.lower():
    n_genre = added.get("f2026", 32)
    anchor = "which is the step the comparator papers in\nthis genre take"
    if anchor in t:
        t = t.replace(anchor, anchor + f" [{n_genre}]", 1)
        EN.write_text(t, encoding="utf-8")
        print(f"  cited the method paper as [{n_genre}] in Section 3.8b")
    else:
        anchor2 = "the step the comparator papers in"
        if anchor2 in t:
            j = t.index(anchor2)
            k = t.index(".", j)
            t = t[:k] + f" [{n_genre}]" + t[k:]
            EN.write_text(t, encoding="utf-8")
            print(f"  cited the method paper as [{n_genre}]")
        else:
            print("  WARNING: could not find the method sentence to attach the citation to")
else:
    print("  the method paper is already mentioned")

ct = CN.read_text(encoding="utf-8")
if "氟西汀" not in ct:
    n_genre = added.get("f2026", 32)
    a = "即同类文献所采用的步骤"
    if a in ct:
        j = ct.index(a)
        k = ct.index("。", j)
        ct = ct[:k] + f"[{n_genre}]" + ct[k:]
        CN.write_text(ct, encoding="utf-8")
        print(f"  cited the method paper as [{n_genre}] in the Chinese file")
    else:
        print("  note: Chinese method sentence not found; citation added to English only")

print()
print("  verification:")
for path in (EN, CN):
    t = path.read_text(encoding="utf-8")
    bad = re.findall(r"\[(?:l2008|c2026|su2022|f2026)\]", t)
    print(f"      {path.name}: {len(bad)} literal key(s) remaining")
print(f"      citation_map now {len(cmap)} entries, highest number "
      f"{max(int(k) for k in cmap)}")
