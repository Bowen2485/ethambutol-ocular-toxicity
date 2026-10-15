# -*- coding: utf-8 -*-
"""Inspect the BGZF block structure of a FinnGen summary-statistics file."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bgzf_tabix as bt  # noqa: E402

GZ = ("https://storage.googleapis.com/finngen-public-data-r12/"
      "summary_stats/release/finngen_R12_H7_OPTNEURITIS.gz")
f = bt.HttpFile(GZ, block=1 << 20)
print("file size:", f.size)

# walk the first 4 MB and record every gzip member offset / BSIZE
f.seek(0)
blob = f.read(4 << 20)
print("fetched", len(blob), "bytes")
offs = []
i = 0
while i < len(blob) - 18:
    if blob[i:i + 4] == b"\x1f\x8b\x08\x04":
        xlen = struct.unpack("<H", blob[i + 10:i + 12])[0]
        extra = blob[i + 12:i + 12 + xlen]
        bsize = None
        j = 0
        while j + 4 <= len(extra):
            si1, si2, slen = extra[j], extra[j + 1], struct.unpack("<H", extra[j + 2:j + 4])[0]
            if si1 == 66 and si2 == 67:
                bsize = struct.unpack("<H", extra[j + 4:j + 6])[0]
            j += 4 + slen
        if bsize is None:
            i += 1
            continue
        total = bsize + 1
        offs.append((i, total, xlen))
        i += total
    else:
        i += 1

print(f"gzip members found in the first 4 MB: {len(offs)}")
for o, t, x in offs[:8]:
    print(f"   offset={o:>8}  total={t:>7}  xlen={x}")
if offs:
    sizes = [t for _, t, _ in offs]
    print(f"   member size: min={min(sizes)} max={max(sizes)} mean={sum(sizes)/len(sizes):.0f}")

# probe a mid-file range for a gzip header (is 402 MB a member boundary?)
for probe in (402_424_348, 402_424_348 - 4096, 200_000_000):
    try:
        f2 = bt.HttpFile(GZ, block=1 << 16)
        f2.seek(probe)
        head = f2.read(64)
        print(f"\n  bytes at {probe}: {head[:24].hex(' ')}")
        print(f"    is BGZF header: {head[:4] == b'\\x1f\\x8b\\x08\\x04'}")
    except Exception as e:  # noqa: BLE001
        print(f"  probe {probe} failed: {type(e).__name__} {str(e)[:90]}")

# consistency: chunk voffset -> coffset
vo = 8349150017544
print(f"\n  chunk voffset {vo}: coffset={vo >> 16} uoffset={vo & 0xFFFF}")
print(f"  coffset within file size: {0 <= (vo >> 16) < f.size}")
