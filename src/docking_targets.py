# -*- coding: utf-8 -*-
"""
Step 4d - Dock ethambutol and the candidate TCM actives against the hub targets.

Target panel
    The focused-tier hubs from step 3 (TP53, NFE2L2, AKT1, BCL2, HMOX1, CASP3,
    SOD2, TNF, GPX4, MFN2, SDHB, BDNF, TFEB, SMAD4).  For each target the best
    human experimental structure is chosen from RCSB (lowest resolution, human
    gene-name match); if the structure carries a drug-like co-crystal ligand the
    search box is centred on that ligand, otherwise the LIGSITE pocket detector
    supplies the box.

Ligands
    ethambutol (the toxicant) plus the TCM actives nominated in
    docs/tcm_optic_neuropathy_background.md.

Outputs -> docking/results.csv, docking/poses/*
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
ROOT = SRC.parent

import docking_prep as dp          # noqa: E402
import docking_run as dr           # noqa: E402
import pocket_detect as pkd        # noqa: E402

DERIVED = ROOT / "data" / "derived"
DOCK = ROOT / "docking"
RESULTS = ROOT / "results"

# gene -> (uniprot, preferred PDB if curated, ligand to keep)
TARGETS = {
    "TP53":   {"uniprot": "P04637"},
    "NFE2L2": {"uniprot": "Q16236"},
    "AKT1":   {"uniprot": "P31749"},
    "BCL2":   {"uniprot": "P10415"},
    "HMOX1":  {"uniprot": "P09601"},
    "CASP3":  {"uniprot": "P42574"},
    "SOD2":   {"uniprot": "P04179"},
    "TNF":    {"uniprot": "P01375"},
    "GPX4":   {"uniprot": "P36969"},
    "MFN2":   {"uniprot": "O95140"},
    "SDHB":   {"uniprot": "P21912"},
    "BDNF":   {"uniprot": "P23560"},
    "TFEB":   {"uniprot": "P19484"},
    "SMAD4":  {"uniprot": "Q13485"},
}

TCM_LIGANDS = [
    "quercetin", "luteolin", "kaempferol", "chlorogenic acid", "puerarin",
    "crocin", "ginkgolide B", "ferulic acid", "salvianolic acid B",
    "astragaloside IV", "betaine",
]
CORE_LIGANDS = ["ethambutol"]


def pick_structure(gene: str, preferred: str = "") -> dict | None:
    cache = DERIVED / f"rcsb_choice_{gene}.json"
    if cache.exists():
        d = json.loads(cache.read_text(encoding="utf-8"))
        return d or None
    cands = dp.rcsb_best(gene)
    if preferred:
        cands = [c for c in cands if c["pdb"] == preferred.upper()] or cands
    if not cands:
        choice = None
    else:
        # prefer an entry that carries a drug-like co-crystal ligand for box definition
        def rank(c):
            ligs = [l for l in (c["ligands"] or "").split("|") if l and len(l) >= 3]
            return (not ligs, c["resolution"] if c["resolution"] is not None else 99)
        cands.sort(key=rank)
        choice = cands[0]
    cache.write_text(json.dumps(choice or {}, indent=2), encoding="utf-8")
    return choice


def prepare_target(gene: str, info: dict) -> dict | None:
    ch = pick_structure(gene, info.get("pdb", ""))
    if not ch:
        print(f"[{gene}] no experimental structure found -> AlphaFold")
        url = dp.alphafold_model(info["uniprot"])
        if not url:
            return None
        work = DOCK / "receptors" / f"{gene}_AF"
        work.mkdir(parents=True, exist_ok=True)
        pdb = work / f"{gene}_AF.pdb"
        if not pdb.exists():
            import ssl
            import urllib.request
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=300, context=ctx) as r:
                pdb.write_bytes(r.read())
        pdbqt = dp.prep_receptor(str(pdb)) if False else None
        # AlphaFold models: no ligand, box from LIGSITE
        import subprocess
        r = subprocess.run(
            [str(dp.OBABEL), str(pdb), "-O", str(work / "receptor.pdbqt"), "-xr"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        return {"gene": gene, "pdb": "AlphaFold", "receptor": work / "receptor.pdbqt",
                "source_pdb": pdb, "resolution": None, "ligand": None}

    pdb_id = ch["pdb"]
    print(f"[{gene}] structure {pdb_id} res={ch['resolution']} "
          f"ligands={ch['ligands'][:50]}")
    receptor = dp.prep_receptor(pdb_id, keep_het=[])
    if receptor is None:
        return None
    src_pdb = DOCK / "receptors" / pdb_id.upper() / f"{pdb_id.upper()}.pdb"
    return {"gene": gene, "pdb": pdb_id, "receptor": receptor, "source_pdb": src_pdb,
            "resolution": ch["resolution"], "ligand": ch["ligands"]}


def define_box(target: dict) -> tuple[dict, str]:
    """Box from the co-crystal ligand centroid, else from the top LIGSITE pocket."""
    src = target.get("source_pdb")
    ligs = dr.crystal_ligands(src) if src and src.exists() else {}
    if ligs:
        key = max(ligs, key=lambda k: ligs[k]["n_heavy"])
        # a drug-like ligand is the best possible box definition
        if ligs[key]["n_heavy"] >= 10:
            c = dr.centroid(ligs[key]["atoms"])
            return dr.make_box(c, size=24.0), f"co-crystal {key} ({ligs[key]['n_heavy']} ha)"
    pockets = pkd.detect_pockets(src) if src and src.exists() else []
    if pockets:
        top = pockets[0]
        return pkd.pocket_box(top), (f"LIGSITE pocket #{top['label']} "
                                     f"({top['n_grid_points']} pts, "
                                     f"meanPSP {top['mean_psp']:.1f})")
    return dr.make_box(np.array([0.0, 0.0, 0.0]), 30.0), "origin (fallback)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", nargs="+", default=list(TARGETS))
    ap.add_argument("--ligands", nargs="+", default=CORE_LIGANDS)
    ap.add_argument("--tcm", action="store_true", help="also dock the TCM actives")
    ap.add_argument("--exhaustiveness", type=int, default=32)
    ap.add_argument("--modes", type=int, default=9)
    ap.add_argument("--box-size", type=float, default=0.0,
                    help="override the box edge length (A); 0 = automatic")
    args = ap.parse_args()

    ligands = list(args.ligands)
    if args.tcm:
        ligands += [l for l in TCM_LIGANDS if l not in ligands]

    lig_paths = {}
    for name in ligands:
        try:
            p = dp.prep_ligand(name)
            if p:
                lig_paths[name] = p
        except Exception as exc:  # noqa: BLE001
            print(f"[ligand] {name}: FAILED {type(exc).__name__} {str(exc)[:100]}")
    print(f"[ligands] prepared {len(lig_paths)}: {list(lig_paths)}")

    rows = []
    for gene in args.targets:
        info = TARGETS.get(gene, {"uniprot": ""})
        try:
            target = prepare_target(gene, info)
        except Exception as exc:  # noqa: BLE001
            print(f"[{gene}] preparation FAILED {type(exc).__name__} {str(exc)[:130]}")
            continue
        if not target:
            continue
        box, box_note = define_box(target)
        if args.box_size > 0:
            box = {**box, "size_x": args.box_size, "size_y": args.box_size,
                   "size_z": args.box_size}
            box_note += f" | box forced to {args.box_size} A"
        print(f"[{gene}] box: {box_note} centre=("
              f"{box['center_x']:.1f},{box['center_y']:.1f},{box['center_z']:.1f}) "
              f"size={box['size_x']:.0f}")
        for lname, lpath in lig_paths.items():
            out = DOCK / "poses" / f"{gene}__{lname}.pdbqt"
            try:
                ok, msg = dr.dock(target["receptor"], lpath, box, out,
                                  exhaustiveness=args.exhaustiveness,
                                  n_modes=args.modes)
            except Exception as exc:  # noqa: BLE001
                ok, msg = False, f"{type(exc).__name__} {str(exc)[:120]}"
            scores = dr.vina_scores(out) if out.exists() else []
            rows.append({
                "gene": gene, "pdb": target["pdb"], "resolution": target["resolution"],
                "box_source": box_note,
                "box_center": f"{box['center_x']:.1f},{box['center_y']:.1f},"
                              f"{box['center_z']:.1f}",
                "box_size": box["size_x"],
                "ligand": lname, "ok": bool(ok),
                "best_affinity": scores[0] if scores else None,
                "affinity_2": scores[1] if len(scores) > 1 else None,
                "affinity_3": scores[2] if len(scores) > 2 else None,
                "n_modes": len(scores), "note": "" if ok else str(msg)[-160:],
            })
            print(f"   {gene:7s} + {lname:22s} -> "
                  f"{rows[-1]['best_affinity']} kcal/mol  ok={ok}")
            pd.DataFrame(rows).to_csv(DOCK / "results.csv", index=False,
                                      encoding="utf-8-sig")
    print(f"\n[done] {len(rows)} docking runs -> {DOCK / 'results.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
