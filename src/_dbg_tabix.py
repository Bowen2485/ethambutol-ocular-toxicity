# -*- coding: utf-8 -*-
"""Debug the tabix reader against FinnGen: inspect raw records and bin structure."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bgzf_tabix as bt  # noqa: E402

GZ = ("https://storage.googleapis.com/finngen-public-data-r12/"
      "summary_stats/release/finngen_R12_H7_OPTNEURITIS.gz")
TBI = GZ + ".tbi"

tb = bt.Tabix(GZ, TBI)
print(f"refs: {tb.names}")
print(f"chr3 bins: {sorted(tb.bins[2].keys())[:20]} ... n={len(tb.bins[2])}")
print(f"chr3 linear index length: {len(tb.linear[2])}")
print(f"chr3 linear[:5]: {tb.linear[2][:5]}")

print("\n--- read the first records straight from the data file ---")
f = tb.data
f.seek(0)
out = bytearray()
for _ in range(40):
    payload, start = bt.read_bgzf_block(f)
    if not payload:
        print(f"  block at {start} failed to decompress")
        break
    out += payload
    if len(out) > 200000:
        break
lines = bytes(out).split(b"\n")
print(f"  decompressed {len(out)} bytes, {len(lines)} lines")
for ln in lines[:8]:
    print("   ", ln.decode("utf-8", "replace")[:180])

print("\n--- bins actually present for chr1 and the range they cover ---")
for ci in (0, 2):
    bins = tb.bins[ci]
    offs = [c for chunks in bins.values() for c in chunks]
    if offs:
        print(f"  ref {tb.names[ci]}: {len(bins)} bins, "
              f"voffset min={min(o[0] for o in offs)} max={max(o[1] for o in offs)}")
    print(f"  bin ids: {sorted(bins.keys())[:25]}")

print("\n--- try a whole-chromosome query on chr3 via the first chunk ---")
ci = 2
chunks = sorted(c for cl in tb.bins[ci].values() for c in cl)
print(f"  {len(chunks)} chunks on chr3; first 3: {chunks[:3]}")
if chunks:
    data = bt.read_from_voffset(tb.data, chunks[0][0], max_bytes=200000)
    ls = data.split(b"\n")
    print(f"  decompressed {len(data)} bytes, {len(ls)} lines")
    for ln in ls[:5]:
        print("   ", ln.decode("utf-8", "replace")[:180])
