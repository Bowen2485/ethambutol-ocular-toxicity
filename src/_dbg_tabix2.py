# -*- coding: utf-8 -*-
"""Trace one tabix chunk end-to-end to find why no records are returned."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bgzf_tabix as bt  # noqa: E402

GZ = ("https://storage.googleapis.com/finngen-public-data-r12/"
      "summary_stats/release/finngen_R12_H7_OPTNEURITIS.gz")
tb = bt.Tabix(GZ, GZ + ".tbi")

chrom, start, end = "1", 155000000, 155300000
ci = tb.chrom_index(chrom)
print(f"chrom_index({chrom}) = {ci}")

want = tb._reg2bins(start - 1, end)
print(f"bins wanted: {want}")
present = [b for b in want if b in tb.bins[ci]]
print(f"bins present in the index: {present}")

li = (start - 1) >> 14
print(f"linear interval index {li}, in range: {li < len(tb.linear[ci])}")
min_off = tb.linear[ci][li] if li < len(tb.linear[ci]) else 0
print(f"min_off (voffset) = {min_off} -> coffset={min_off >> 16} uoffset={min_off & 0xFFFF}")

chunks = []
for b in want:
    for (cb, ce) in tb.bins[ci].get(b, []):
        chunks.append((cb, ce))
chunks = [c for c in chunks if c[1] > min_off]
print(f"raw chunks: {len(chunks)}; first 5: {chunks[:5]}")

merged = []
for cb, ce in sorted(chunks):
    if merged and cb <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], ce)
    else:
        merged.append([cb, ce])
print(f"merged chunks: {len(merged)}; first 3: {merged[:3]}")

for beg, en in merged[:2]:
    print(f"\n--- chunk voffset {beg} (coffset {beg >> 16}) ---")
    f = tb.data
    f.seek(beg >> 16)
    head = f.read(18)
    print(f"  header bytes: {head.hex(' ')}")
    print(f"  is BGZF: {head[:4] == bytes([0x1f,0x8b,8,4])}")
    payload, blk_start = bt.read_bgzf_block(f)
    print(f"  block at {blk_start}: {len(payload)} uncompressed bytes")
    if payload:
        lines = payload.split(b"\n")
        print(f"  first 3 lines (uoffset={beg & 0xFFFF}):")
        for ln in lines[:3]:
            print("     ", ln.decode("utf-8", "replace")[:140])
    data = bt.read_from_voffset(tb.data, beg, max_bytes=1 << 20)
    print(f"  read_from_voffset -> {len(data)} bytes")
    if data:
        ls = [l for l in data.split(b"\n") if l]
        print(f"  {len(ls)} non-empty lines; first 3:")
        for ln in ls[:3]:
            print("     ", ln.decode("utf-8", "replace")[:140])
