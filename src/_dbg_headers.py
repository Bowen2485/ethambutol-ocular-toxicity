# -*- coding: utf-8 -*-
"""Dump the real column headers of the FAERS quarterly ASCII tables."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "faers_ascii"

for q in ("2004q1", "2012q4", "2020q1", "2026q1"):
    z = CACHE / f"{q}.zip"
    if not z.exists():
        print(f"{q}: archive missing")
        continue
    print(f"\n=== {q} ===")
    with zipfile.ZipFile(z) as zf:
        for name in sorted(zf.namelist()):
            low = name.lower()
            if not low.endswith(".txt"):
                continue
            with zf.open(name) as fh:
                head = fh.read(4000).decode("latin-1")
            first = head.splitlines()[0] if head else ""
            cols = [c.strip().lower() for c in first.split("$")]
            print(f"  {Path(name).name:22s} ({len(cols):2d} cols): {cols}")
