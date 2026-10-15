# -*- coding: utf-8 -*-
"""Fetch the AutoDock Vina Windows binary and probe the docking toolchain."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOOLS.mkdir(exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

ASSETS = {
    "vina.exe": "https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/"
                "v1.2.7/vina_1.2.7_win.exe",
    "vina_split.exe": "https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/"
                      "v1.2.7/vina_split_1.2.7_win.exe",
}


def download(url: str, dest: Path, chunk: int = 1 << 20, tries: int = 8) -> bool:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=300, context=CTX) as r, \
                    dest.open("wb") as fh:
                while True:
                    b = r.read(chunk)
                    if not b:
                        break
                    fh.write(b)
            if dest.stat().st_size > 0:
                print(f"[ok] {dest.name}: {dest.stat().st_size/1e6:.2f} MB")
                return True
        except Exception as exc:  # noqa: BLE001
            print(f"[retry {attempt+1}] {dest.name}: {type(exc).__name__} {str(exc)[:70]}")
    return False


def main() -> None:
    for name, url in ASSETS.items():
        dest = TOOLS / name
        if dest.exists() and dest.stat().st_size > 0:
            print(f"[cache] {name}: {dest.stat().st_size/1e6:.2f} MB")
            continue
        download(url, dest)

    # probe docking-related services
    probes = {
        "PDBe_files": "https://www.ebi.ac.uk/pdbe/entry-files/download/1bna.cif",
        "RCSB_pdb": "https://files.rcsb.org/download/1BNA.pdb",
        "RCSB_search": "https://search.rcsb.org/rcsbsearch/v2/query",
        "AlphaFold_api": "https://alphafold.ebi.ac.uk/api/prediction/P00330",
        "DiffDock_api": "https://health.api.nvidia.com/v1/biology/mit/diffdock",
        "PLIP_api": "https://plip-tool.biotec.tu-dresden.de/plip-web/plip/index",
        "ProteinsPlus": "https://proteins.plus/api/",
        "P2Rank_dl": "https://github.com/rdk/p2rank/releases/latest",
    }
    for name, url in probes.items():
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
                print(f"[{r.status}] probe {name:16s} len={len(r.read())}")
        except urllib.error.HTTPError as e:
            print(f"[HTTP{e.code}] probe {name:16s}")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] probe {name:16s} {type(e).__name__} {str(e)[:60]}")


if __name__ == "__main__":
    main()
