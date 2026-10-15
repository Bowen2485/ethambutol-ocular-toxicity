# -*- coding: utf-8 -*-
"""Smoke-test the vectorised LIGSITE pocket detector on a prepared receptor."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pocket_detect as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

for rel in ["docking/receptors/7NH5/7NH5.pdb",
            "docking/receptors/5MU8/5MU8.pdb"]:
    p = ROOT / rel
    if not p.exists():
        print(f"{rel}: missing")
        continue
    t0 = time.time()
    pks = pd.detect_pockets(p)
    dt = time.time() - t0
    print(f"\n{p.name}: {len(pks)} pockets in {dt:.1f}s")
    for k in pks[:6]:
        b = pd.pocket_box(k)
        c = k["centre"]
        print(f"  #{k['label']:>2} pts={k['n_grid_points']:>6} "
              f"vol={k['volume_A3']:>8.0f} meanPSP={k['mean_psp']:5.2f} "
              f"centre=({c[0]:7.1f},{c[1]:7.1f},{c[2]:7.1f}) box={b['size_x']:.0f}")
