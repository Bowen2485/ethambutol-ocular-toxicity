# -*- coding: utf-8 -*-
"""
Audit what the manuscript promises against what exists on disk.

Several rounds of revision have added sections, tables and figures, and nothing has
checked that the artefacts those sections refer to are actually present or that the
figure and table lists still describe them.  A manuscript that cites Figure 9 when nine
figures exist is not a writing problem, it is a submission blocker, and it is the kind
of thing that goes unnoticed when the text is edited repeatedly without looking at the
directory.

This checks:
    * how many figures and tables exist as files, and what they are
    * how many the manuscript refers to
    * whether the declared lists in the manuscript match
    * whether every declared figure is actually cited in the body, which is what the Word and
      LaTeX builds use to decide where to place it
    * whether sections the text announces are present
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
EN = (MS / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
CN = (MS / "Ethambutol_EyeTox_CN_full.md").read_text(encoding="utf-8")

print("=" * 96)
print("1. Figure and table files on disk")
print("=" * 96)
FIGDIRS = [ROOT / "figures", ROOT / "results" / "figures", MS / "figures",
           ROOT / "output" / "figures"]
seen = False
for d in FIGDIRS:
    if d.exists():
        seen = True
        files = sorted(p for p in d.iterdir() if p.is_file())
        print(f"  {d.relative_to(ROOT)}: {len(files)} files")
        for p in files[:40]:
            print(f"      {p.name}  ({p.stat().st_size/1024:.0f} KB)")
if not seen:
    print("  no figure directory found in any of:")
    for d in FIGDIRS:
        print(f"      {d.relative_to(ROOT)}")

# any image anywhere in the project
imgs = [p for ext in ("*.png", "*.pdf", "*.svg", "*.tif", "*.tiff", "*.jpg")
        for p in ROOT.rglob(ext)
        if "node_modules" not in str(p) and ".git" not in str(p)]
print(f"\n  images anywhere in the project: {len(imgs)}")
bydir: dict[str, int] = {}
for p in imgs:
    bydir.setdefault(str(p.parent.relative_to(ROOT)), 0)
    bydir[str(p.parent.relative_to(ROOT))] += 1
for d, n in sorted(bydir.items(), key=lambda x: -x[1])[:12]:
    print(f"      {d}: {n}")

print()
print("=" * 96)
print("2. What the manuscript refers to")
print("=" * 96)
fig_refs = sorted({int(m) for m in re.findall(r"Figure\s+(\d+)", EN)})
# table labels carry letter suffixes (2b, 2c, 2d), so they stay strings
tab_refs = sorted({m for m in re.findall(r"Table\s+(\d+[a-z]?)", EN)})
fig_refs_cn = sorted({int(m) for m in re.findall(r"图\s*(\d+)", CN)})
tab_refs_cn = sorted({m for m in re.findall(r"表\s*(\d+[a-z]?)", CN)})
print(f"  EN refers to Figures: {fig_refs}")
print(f"  EN refers to Tables : {tab_refs}")
print(f"  CN refers to 图     : {fig_refs_cn}")
print(f"  CN refers to 表     : {tab_refs_cn}")

print()
print("=" * 96)
print("3. The declared lists at the end of each manuscript")
print("=" * 96)
for label, text in (("EN", EN), ("CN", CN)):
    m = re.search(r"##\s*(Figures and Tables|图表清单|Figure and Table)[^\n]*\n(.*?)(?=\n##|\Z)",
                  text, re.S)
    if m:
        body = m.group(2)
        figs = re.findall(r"(?:Figure|\*\*图)\s*(\d+)", body)
        tabs = re.findall(r"(?:Table|表)\s*(\d+[a-z]?)", body)
        print(f"  {label} declared: figures {sorted({int(x) for x in figs})}")
        print(f"  {label} declared: tables  {sorted(set(tabs))}")
    else:
        print(f"  {label}: no declared list found")

print()
print("=" * 96)
print("4. Sections the text announces")
print("=" * 96)
for label, text in (("EN", EN), ("CN", CN)):
    heads = [ln.strip() for ln in text.splitlines() if ln.startswith("###")
             or ln.startswith("##")]
    print(f"  {label}: {len(heads)} headings")
    for h in heads[-10:]:
        print(f"      {h[:88]}")

print()
print("=" * 96)
print("5. Statements about data availability and reporting standards")
print("=" * 96)
for key in ("Data availability", "data availability", "Data Availability",
            "STROBE", "RECORD", "reporting guideline", "Code availability",
            "数据可用性", "报告规范"):
    print(f"  EN contains {key!r}: {key in EN}")

print()
print("=" * 96)
print("6. Every declared figure is also cited in the body")
print("=" * 96)
#: A figure that appears only in the caption list is a figure no reader is ever sent to, and
#: both builders embed a figure at its first mention in the body.  Two instances of this went
#: unnoticed until they were looked for directly: the Venn diagram existed in the repository
#: cited nowhere at all, and the Chinese docking figure was listed but never mentioned, so the
#: Chinese Word file shipped without it.  Counting references does not catch either.
for label, text, pat, list_head in (
        ("EN", EN, r"Figure\s*(\d{1,2})", r"\*\*Figure 1\*\*"),
        ("CN", CN, r"图\s*(\d{1,2})", r"\*\*图1\*\*")):
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if re.match(list_head, ln.strip())),
                 len(lines))
    in_body = {int(n) for n in re.findall(pat, "\n".join(lines[:start]))}
    in_list = {int(n) for n in re.findall(pat, "\n".join(lines[start:]))}
    only_listed = sorted(in_list - in_body)
    print(f"  {'OK' if not only_listed else 'PROBLEM':8s} {label}: {len(in_list)} declared, "
          f"{len(in_body)} cited in the body"
          + (f"; listed but never cited: {only_listed}" if only_listed else ""))
