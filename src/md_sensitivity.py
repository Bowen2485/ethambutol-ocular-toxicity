# -*- coding: utf-8 -*-
"""
Sensitivity test: are the docked poses unstable because they are weak, or because the
reduced model cannot hold a ligand?

The coarse-grained run placed one bead per residue at the C-alpha position, so side
chains - which form most of a real binding site - are absent and the ligand-receptor
well is shallow.  A ligand that leaves in that model may be an artefact of the model
rather than a property of the pose.

The test therefore repeats each run with the ligand-receptor interaction scaled up by
factors of 10 and 50, which is far stronger than any realistic protein-ligand
interaction.  The outcome is interpreted as follows:

  * if the ligand escapes even at 50x, the pose is not a stable binding mode under any
    reasonable interaction strength, and the docking result should be reported as a
    weak, non-committal prediction
  * if the ligand is retained at 10-50x, the escape at 1x reflects the model's missing
    side chains, and the docking result stands

Run with: python src/md_sensitivity.py --steps 40000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import md_coarse as md  # noqa: E402

DOCK = ROOT / "docking"
RES = ROOT / "results"


def run_scaled(gene: str, receptor: Path, ligand: Path, steps: int, scale: float,
               seed: int = 20261013) -> dict | None:
    rec, _ = md.read_pdb_ca(receptor)
    lig = md.read_ligand_heavy(ligand)
    if len(rec) < 20 or len(lig) < 3:
        return None
    pairs, r0, li, ri, lr0, lig_pairs, lig_r0 = md.build_system(rec, lig)
    n_rec = len(rec)
    pos = np.vstack([rec, lig]).astype(float)
    rec_ref, lig0 = rec.copy(), lig.copy()

    rng = np.random.default_rng(seed)
    vel = rng.normal(0.0, np.sqrt(md.KB * md.TEMPERATURE), pos.shape)
    c1 = np.exp(-md.GAMMA * md.DT)
    c2 = np.sqrt(md.KB * md.TEMPERATURE * (1 - c1 * c1))
    F_MAX, E_MAX = 500.0, 1e6

    def ef(p):
        e, f = md.energy_forces(p, n_rec, pairs, r0, li, ri, lr0,
                                lig_pairs, lig_r0)
        return e, f

    # scale only the ligand-receptor term by re-running the whole force with a
    # weighted contact contribution
    def ef_scaled(p):
        """
        Total force with the ligand-receptor contact term scaled.

        The scaled part is obtained by calling the module's own energy_forces twice:
        once with the contacts included and once with them removed.  An earlier
        version duplicated the contact force expression here, which meant the sign
        fix applied to md_coarse.py never reached this script and every run,
        including the 50x one, used the broken force.
        """
        e_full, f_full = md.energy_forces(p, n_rec, pairs, r0, li, ri, lr0,
                                          lig_pairs, lig_r0)
        if scale == 1.0 or len(li) == 0:
            return e_full, f_full
        empty = np.zeros(0, dtype=int)
        e_nc, f_nc = md.energy_forces(p, n_rec, pairs, r0,
                                      empty, empty, np.zeros(0),
                                      lig_pairs, lig_r0)
        e_c, f_c = e_full - e_nc, f_full - f_nc
        return e_nc + scale * e_c, f_nc + scale * f_c

    e, f = ef_scaled(pos)
    for step in range(steps):
        fn = np.clip(f, -F_MAX, F_MAX)
        vel = c1 * vel + 0.5 * md.DT * fn
        pos = pos + 0.5 * md.DT * vel
        e, f = ef_scaled(pos)
        if not np.isfinite(e) or e > E_MAX:
            pos = np.vstack([rec_ref, lig0])
            vel = rng.normal(0.0, np.sqrt(md.KB * md.TEMPERATURE), pos.shape)
            e, f = ef_scaled(pos)
        fn = np.clip(f, -F_MAX, F_MAX)
        vel = c1 * vel + 0.5 * md.DT * fn
        vel = vel + c2 * rng.normal(0.0, 1.0, vel.shape)
        pos = pos + 0.5 * md.DT * vel

    lig1 = pos[n_rec:]
    dr0 = np.linalg.norm(lig0[:, None, :] - rec[None, :, :], axis=-1)
    li0, ri0 = np.where(dr0 < md.CONTACT_CUT)
    dr1 = np.linalg.norm(lig1[li0] - pos[ri0], axis=1)
    return {
        "gene": gene,
        "scale": scale,
        "centroid_shift_A": round(float(np.linalg.norm(
            lig1.mean(axis=0) - lig0.mean(axis=0))), 2),
        "contact_retention_pct": round(100 * float(np.mean(dr1 <= md.CONTACT_CUT)), 1),
        "mean_contact_dist_A": round(float(np.mean(dr1)), 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=40000)
    ap.add_argument("--genes", nargs="*", default=["TNF", "MFN2", "HMOX1"])
    ap.add_argument("--scales", nargs="*", type=float, default=[1.0, 10.0, 50.0])
    args = ap.parse_args()

    d = pd.read_csv(DOCK / "results.csv", encoding="utf-8-sig")
    d = d[(d.ligand == "ethambutol") & (d.ok == True)]  # noqa: E712

    rows = []
    for gene in args.genes:
        row = d[d.gene == gene]
        if row.empty:
            continue
        pdbid = str(row.iloc[0].pdb).strip()
        rec = DOCK / "receptors" / pdbid / f"{pdbid}_clean.pdb"
        if not rec.exists():
            rec = DOCK / "receptors" / pdbid / f"{pdbid}.pdb"
        lig = DOCK / "poses" / f"{gene}__ethambutol.pdbqt"
        if not (rec.exists() and lig.exists()):
            print(f"  {gene}: inputs missing")
            continue
        print(f"\n{gene}  (receptor {rec.name}, {args.steps} steps = "
              f"{args.steps*md.DT:.0f} ps)")
        for scale in args.scales:
            try:
                out = run_scaled(gene, rec, lig, args.steps, scale)
            except Exception as exc:  # noqa: BLE001
                print(f"    x{scale:<5g} FAILED {type(exc).__name__}: "
                      f"{str(exc)[:70]}")
                continue
            if out is None:
                continue
            rows.append(out)
            print(f"    x{scale:<5g} centroid shift {out['centroid_shift_A']:>6.2f} A   "
                  f"contacts retained {out['contact_retention_pct']:>5.1f}%   "
                  f"mean contact {out['mean_contact_dist_A']:>5.2f} A")

    if not rows:
        print("no results")
        return 1
    df = pd.DataFrame(rows)
    df.to_csv(RES / "md_sensitivity.csv", index=False, encoding="utf-8-sig")

    print("\n" + "=" * 74)
    print("READING")
    print("=" * 74)
    for gene, g in df.groupby("gene"):
        g = g.sort_values("scale")
        weak = g[g.scale == g.scale.min()].iloc[0]
        strong = g[g.scale == g.scale.max()].iloc[0]
        if strong.contact_retention_pct > 50:
            verdict = ("retained once the interaction is strong, so the escape at 1x "
                       "reflects the reduced model's missing side chains")
        else:
            verdict = ("escapes even at the strongest interaction tested, so the pose "
                       "is not a stable binding mode")
        print(f"  {gene:8s} 1x retention {weak.contact_retention_pct:>5.1f}%  ->  "
              f"x{strong.scale:g} retention {strong.contact_retention_pct:>5.1f}%")
        print(f"           {verdict}")
    print(f"\n-> {RES / 'md_sensitivity.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
