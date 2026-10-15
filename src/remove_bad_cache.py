# -*- coding: utf-8 -*-
"""
Delete the scan files written with copied phenotype data, and nothing else.

Every path is resolved to an absolute form and checked to be inside
data/raw/opengwas before removal, and the names must carry one of the seven affected
exposure identifiers.  The three sound exposures are named explicitly as protected, so a
mistake in the selector cannot reach them.

The count of files removed and the count left behind are both reported, and the
post-condition is checked rather than assumed: the affected exposures must be gone and
the sound ones must be intact.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = (ROOT / "data" / "raw" / "opengwas").resolve()

BAD = ["ukb-b-13891", "ieu-b-25", "ieu-b-73", "ieu-b-4877",
       "ebi-a-GCST006867", "ebi-a-GCST90014006", "ieu-b-40"]
PROTECTED = ["ebi-a-GCST90103634", "ebi-a-GCST90025945", "ebi-a-GCST90025946"]

print("=" * 94)
print("Preconditions")
print("=" * 94)
print(f"  target directory : {RAW}")
print(f"  exists           : {RAW.is_dir()}")
if not RAW.is_dir():
    raise SystemExit("target directory not found; refusing to proceed")

bads, goods = [], []
for p in RAW.glob("mr_*.tsv"):
    rp = p.resolve()
    if rp.parent != RAW:                       # never touch anything outside the cache
        print(f"  skipping {rp} - outside the cache directory")
        continue
    name = p.name
    if any(f"mr_{gid}_" in name for gid in BAD):
        if any(f"mr_{gid}_" in name for gid in PROTECTED):
            print(f"  skipping {name} - matches a protected exposure")
            continue
        bads.append(rp)
    elif any(f"mr_{gid}_" in name for gid in PROTECTED):
        goods.append(rp)

print(f"  files selected for removal : {len(bads):,}")
print(f"  files protected            : {len(goods):,}")
print()
print("  every selected path resolves inside the cache directory: "
      f"{all(p.parent == RAW for p in bads)}")
print("  every selected path carries an affected exposure id : "
      f"{all(any(f'mr_{g}_' in p.name for g in BAD) for p in bads)}")
print("  no selected path carries a protected exposure id    : "
      f"{not any(any(f'mr_{g}_' in p.name for g in PROTECTED) for p in bads)}")

# record what the protected files look like, so the post-condition can be checked
before_good = {p.name: hashlib.md5(p.read_bytes()).hexdigest()[:10] for p in goods}

print()
print("=" * 94)
print("Removing")
print("=" * 94)
removed = 0
for p in bads:
    try:
        p.unlink()
        removed += 1
    except OSError as exc:
        print(f"  could not remove {p.name}: {exc}")
print(f"  removed {removed:,} of {len(bads):,}")

print()
print("=" * 94)
print("Post-conditions")
print("=" * 94)
left_bad = [p for p in RAW.glob("mr_*.tsv")
            if any(f"mr_{g}_" in p.name for g in BAD)]
left_good = [p for p in RAW.glob("mr_*.tsv")
             if any(f"mr_{g}_" in p.name for g in PROTECTED)]
print(f"  affected-exposure files remaining : {len(left_bad):,}  "
      f"(expected 0)")
print(f"  protected files remaining         : {len(left_good):,}  "
      f"(expected {len(before_good):,})")
print(f"  total scan files now              : "
      f"{len(list(RAW.glob('mr_*.tsv'))):,}")

same = all(hashlib.md5(p.read_bytes()).hexdigest()[:10] == h
           for p in left_good for h in [before_good.get(p.name)])
print(f"  protected files unchanged         : {same}")

print()
print("=" * 94)
print("Result")
print("=" * 94)
ok = not left_bad and len(left_good) == len(before_good) and same
print("  cache now holds only the three sound exposures"
      if ok else "  CHECK FAILED - inspect before fetching")
