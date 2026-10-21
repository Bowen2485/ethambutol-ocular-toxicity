# -*- coding: utf-8 -*-
"""Archive the supplied SDUD annual releases and the GNINA binary.

Why this is a script rather than a copy command
    Six and a half gigabytes moved across two naming conventions, and an archive whose files
    cannot be matched to their source is not an archive.  Each file is copied, hashed on both
    sides and recorded in a manifest with its year, size, SHA-256 and the URL it came from.

Layout
    data/raw/sdud/<original name>          the eleven annual Medicaid releases, 2016-2026
    tools/gnina.cuda12.8.static            docking binary, alongside the existing vina.exe
    data/raw/sdud/MANIFEST.csv             provenance for every file

Nothing is deleted from ~/Downloads; the copies are verified before this script reports success.
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "Downloads"

SDUD = {
    2016: "StateDrugUtilizationData-2016.csv",
    2017: "StateDrugUtilizationData-2017.csv",
    2018: "StateDrugUtilizationData-2018.csv",
    2019: "StateDrugUtilizationData-2019.csv",
    2020: "sdud2020_updatedJuly2026.csv",
    2021: "sdud2021_updatedJuly2026.csv",
    2022: "sdud2022_updatedJuly2026.csv",
    2023: "sdud2023_updatedJuly2026.csv",
    2024: "sdud2024_updatedJuly2026.csv",
    2025: "sdud2025_updatedjuly2026.csv",
    2026: "sdud2026_updated072026.csv",
}
URL_OLD = "https://download.medicaid.gov/data/StateDrugUtilizationData-{y}.csv"
URL_NEW = "https://download.medicaid.gov/data/{name}"

DEST_SDUD = ROOT / "data" / "raw" / "sdud"
DEST_TOOLS = ROOT / "tools"
DEST_SDUD.mkdir(parents=True, exist_ok=True)


def sha256(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


rows = []
failures = []
for year, name in SDUD.items():
    src = DOWNLOADS / name
    if not src.exists():
        failures.append(f"missing source: {name}")
        continue
    dst = DEST_SDUD / name
    print(f"[{year}] {name} ({src.stat().st_size/1e9:.2f} GB) ...", end=" ", flush=True)
    shutil.copy2(src, dst)
    src_hash, dst_hash = sha256(src), sha256(dst)
    ok = src_hash == dst_hash and src.stat().st_size == dst.stat().st_size
    print("ok" if ok else "HASH MISMATCH")
    if not ok:
        failures.append(f"hash mismatch: {name}")
    rows.append({
        "year": year, "file": name, "bytes": dst.stat().st_size, "sha256": dst_hash,
        "source_url": (URL_OLD.format(y=year) if year <= 2019 else URL_NEW.format(name=name)),
        "retrieved": "2026-10-22", "local_path": str(dst.relative_to(ROOT)),
    })

manifest = pd.DataFrame(rows).sort_values("year")
manifest.to_csv(DEST_SDUD / "MANIFEST.csv", index=False, encoding="utf-8-sig")

GNINA = DOWNLOADS / "gnina.cuda12.8.static"
if GNINA.exists():
    dst = DEST_TOOLS / GNINA.name
    print(f"[tool] {GNINA.name} ({GNINA.stat().st_size/1e9:.2f} GB) ...", end=" ", flush=True)
    shutil.copy2(GNINA, dst)
    same = sha256(GNINA) == sha256(dst)
    print("ok" if same else "HASH MISMATCH")
    if not same:
        failures.append("hash mismatch: gnina")
    (DEST_TOOLS / "gnina_README.md").write_text(
        "# GNINA docking binary\n\n"
        "`gnina.cuda12.8.static`, supplied 2026-10-22, archived alongside `vina.exe`.\n\n"
        "- SHA-256: `" + sha256(dst) + "`\n"
        "- Size: " + f"{dst.stat().st_size:,} bytes\n\n"
        "**Not used by the current manuscript.** The docking analyses were removed from the\n"
        "paper in the 2026-10-21 restructuring; this binary is retained for provenance only.\n",
        encoding="utf-8")
else:
    failures.append("missing source: gnina.cuda12.8.static")

print("\nmanifest:")
print(manifest[["year", "file", "bytes"]].to_string(index=False))
print(f"\narchive total: {manifest.bytes.sum()/1e9:.2f} GB in {DEST_SDUD.relative_to(ROOT)}")
if failures:
    print("\nFAILURES:")
    for f in failures:
        print("  " + f)
    raise SystemExit(1)
print("\nall files copied and verified")
