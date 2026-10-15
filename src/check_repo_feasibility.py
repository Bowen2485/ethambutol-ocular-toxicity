# -*- coding: utf-8 -*-
"""
Check disk space and the size of the material a repository would contain.

Git is not installed on this machine, and WMI access is refused in this sandbox, so the
free space is read through shutil instead.  This matters because the project's data
directory is 42 GB and the C: drive was reported as having nothing free - if that is
accurate, creating any copy of anything needs care, and it also affects whether the
FinnGen refetch can finish writing its files.

The second purpose is to size the repository: it should hold scripts, documentation,
result tables and the manuscript, and none of the data.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

print("=" * 88)
print("1. Disk space")
print("=" * 88)
for drive in ("C:\\", "D:\\", "E:\\", "F:\\"):
    try:
        total, used, free = shutil.disk_usage(drive)
    except OSError:
        continue
    print(f"  {drive:5s} total {total/1e9:>8.1f} GB   used {used/1e9:>8.1f} GB   "
          f"free {free/1e9:>8.1f} GB   ({100*free/total:.1f}% free)")

print()
print("=" * 88)
print("2. What a repository would contain")
print("=" * 88)
GROUPS = [
    ("src/*.py", "src", "*.py"),
    ("src/*.sh", "src", "*.sh"),
    ("docs/*.md", "docs", "*.md"),
    ("results/*.csv", "results", "*.csv"),
    ("results/*.json", "results", "*.json"),
    ("tables/*.csv", "tables", "*.csv"),
    ("figures/*.png", "figures", "*.png"),
    ("figures/*.pdf", "figures", "*.pdf"),
    ("manuscript/*", "manuscript", "*"),
]
grand = 0
for label, sub, pat in GROUPS:
    d = ROOT / sub
    if not d.is_dir():
        print(f"  {label:20s} directory absent")
        continue
    files = [p for p in d.glob(pat) if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    grand += size
    print(f"  {label:20s} {len(files):>5} files   {size/1e6:>8.2f} MB")

# scripts in the project root
rootfiles = [p for p in ROOT.glob("*.sh")] + [p for p in ROOT.glob("*.md")]
rsize = sum(p.stat().st_size for p in rootfiles)
grand += rsize
print(f"  {'root *.sh and *.md':20s} {len(rootfiles):>5} files   "
      f"{rsize/1e6:>8.2f} MB")

print()
print(f"  repository total      : {grand/1e6:.1f} MB")
print(f"  project data excluded : 42,060 MB")

print()
print("=" * 88)
print("3. The material that must never be committed")
print("=" * 88)
SENSITIVE = [
    "data/raw/opengwas/token.txt",
    "data/derived/faers.sqlite",
    "data/raw/jader",
]
for s in SENSITIVE:
    p = ROOT / s
    if p.exists():
        size = p.stat().st_size if p.is_file() else \
            sum(q.stat().st_size for q in p.rglob("*") if q.is_file())
        print(f"  {s:34s} {size/1e6:>10,.1f} MB")
    else:
        print(f"  {s:34s} absent")

print()
print("  token.txt is a 556-character JWT: a live OpenGWAS credential.  Publishing it")
print("  would hand the account to anyone who reads the repository, and it would remain")
print("  in the history even if deleted later.")

print()
print("=" * 88)
print("4. Files whose content would leak local detail")
print("=" * 88)
import re
WINPATH = re.compile(r"[A-Za-z]:\\+Users\\+[\w\u4e00-\u9fff]+")
for p in list((ROOT / "docs").glob("*.md")) + [ROOT / "PROGRESS.md"]:
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    hits = WINPATH.findall(t)
    if hits or "20200121047@bucm.edu.cn" in t:
        print(f"  {p.relative_to(ROOT)}")
        for h in dict.fromkeys(hits):
            print(f"      local path: {h}")
        if "20200121047@bucm.edu.cn" in t:
            print("      contains the corresponding author's email address")
