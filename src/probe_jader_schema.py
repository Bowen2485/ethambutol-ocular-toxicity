# -*- coding: utf-8 -*-
"""
Establish the real structure of the JADER tables before any analysis is written.

JADER is distributed as Shift-JIS CSV files, so the column names are Japanese and the
byte encoding has to be handled explicitly or every read will fail or mis-decode.  The
sizes are also very different from FAERS: drug202609.csv alone is 501 MB, which is
small enough to process with pandas in chunks rather than needing a database.

This reports, for each table: the encoding that decodes it, the header row, the number
of rows, and a few sample records.  Nothing is assumed - the earlier FAERS work was
held up repeatedly by guessing at schemas, and the same mistake here would cost the same
time again.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JADER = ROOT / "data" / "raw" / "jader"

TABLES = ["demo202609.csv", "drug202609.csv", "reac202609.csv", "hist202609.csv"]
ENCODINGS = ["shift_jis", "cp932", "utf-8", "utf-8-sig", "euc_jp"]


def sniff(path: Path) -> str | None:
    """The first encoding that decodes the first 200 kB without error."""
    raw = path.open("rb").read(200_000)
    for enc in ENCODINGS:
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return None


def head_rows(path: Path, enc: str, n: int = 4) -> list[list[str]]:
    import csv
    out = []
    with path.open(encoding=enc, errors="replace", newline="") as fh:
        for i, row in enumerate(csv.reader(fh)):
            out.append(row)
            if i >= n:
                break
    return out


def count_rows(path: Path) -> int:
    """Count lines fast; the last line may lack a terminator."""
    n = 0
    with path.open("rb") as fh:
        while True:
            block = fh.read(1 << 22)
            if not block:
                break
            n += block.count(b"\n")
    return n


print("=" * 100)
print("File inventory")
print("=" * 100)
for name in (*TABLES, "弶傔偵偍撉傒偔偩偝偄.txt", "棙梡婯栺.txt"):
    p = JADER / name
    if p.exists():
        print(f"  {name:26s} {p.stat().st_size/1e6:>8.1f} MB")
for p in sorted(JADER.iterdir()):
    if p.suffix == ".txt" and p.name not in ("弶傔偵偍撉傒偔偩偝偄.txt", "棙梡婯栺.txt"):
        print(f"  {p.name:26s} {p.stat().st_size/1e6:>8.1f} MB")

print()
print("=" * 100)
print("Encoding and header for each table")
print("=" * 100)
for name in TABLES:
    p = JADER / name
    if not p.exists():
        print(f"  {name}: absent")
        continue
    enc = sniff(p)
    print(f"\n  --- {name}  (encoding: {enc}) ---")
    if enc is None:
        print("      could not decode with any tried encoding")
        continue
    rows = head_rows(p, enc, 3)
    if not rows:
        print("      empty")
        continue
    hdr = rows[0]
    print(f"      columns ({len(hdr)}):")
    for i, c in enumerate(hdr):
        print(f"          [{i:>2}] {c}")
    print(f"      sample rows:")
    for r in rows[1:]:
        cells = [f"{c[:34]}" for c in r[:8]]
        print(f"          {cells}{' ...' if len(r) > 8 else ''}")

print()
print("=" * 100)
print("Row counts")
print("=" * 100)
for name in TABLES:
    p = JADER / name
    if p.exists():
        print(f"  {name:26s} {count_rows(p):>12,} lines")

print()
print("=" * 100)
print("Readme files, decoded")
print("=" * 100)
for p in sorted(JADER.glob("*.txt")):
    enc = sniff(p) or "cp932"
    try:
        text = p.read_text(encoding=enc, errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"  {p.name}: {type(exc).__name__}")
        continue
    print(f"\n  --- {p.name} ({enc}, {len(text)} chars) ---")
    for ln in text.splitlines()[:40]:
        print(f"      {ln[:110]}")
