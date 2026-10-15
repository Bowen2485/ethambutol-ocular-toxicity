# -*- coding: utf-8 -*-
"""Check whether the partially downloaded eQTLGen file is in fact complete."""
import gzip
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "data" / "raw" / "eqtlgen" / "cis-eQTLsFDR0.05-ProbeLevel.txt.gz.part"
print("exists:", p.exists(), "size:", p.stat().st_size if p.exists() else "-")

if p.exists():
    # 1. can the whole file be decompressed?
    try:
        d = zlib.decompressobj(31)
        n_in = n_out = 0
        with p.open("rb") as fh:
            while True:
                b = fh.read(1 << 22)
                if not b:
                    break
                n_in += len(b)
                out = d.decompress(b)
                n_out += len(out)
        tail = d.flush()
        n_out += len(tail)
        print(f"decompress OK: in={n_in} out={n_out} "
              f"unused={len(d.unused_data)} eof={d.eof}")
    except Exception as exc:  # noqa: BLE001
        print(f"decompress FAILED: {type(exc).__name__} {str(exc)[:160]}")
        print(f"  consumed {n_in} bytes, produced {n_out}")

    # 2. how many lines, and does the last one look complete?
    try:
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as fh:
            n = 0
            last = ""
            header = ""
            for line in fh:
                if n == 0:
                    header = line.rstrip("\n")
                n += 1
                last = line.rstrip("\n")
        print(f"lines: {n}")
        print(f"header: {header[:200]}")
        print(f"last  : {last[:200]}")
    except Exception as exc:  # noqa: BLE001
        print(f"line scan truncated at {n} lines: {type(exc).__name__} {str(exc)[:120]}")
        print(f"last complete line: {last[:180]}")
