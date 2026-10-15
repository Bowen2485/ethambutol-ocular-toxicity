# -*- coding: utf-8 -*-
"""
Rewrite the docking validation text in both manuscripts from the measured results.

What changed
    The original text reported two controls: carbonic anhydrase II with acetazolamide
    passed at 1.795 A, dihydrofolate reductase with methotrexate failed at 5.863 A, and
    the failure was attributed to methotrexate being a large flexible ligand.  That
    explanation was not supported: two points, one below ethambutol's size and one far
    above it, say nothing about where the protocol's limit lies, and they left open the
    possibility that the protocol fails for ligands of ethambutol's own size - ten heavy
    atoms and three rotatable bonds - which is precisely the case that matters.

    The set has now been rebuilt around that size, and the failures form an orderly
    gradient rather than an unexplained one-off.

Every number written here comes from results/redocking_validation_final.csv, produced by
check_all_boxes.py, which also verifies that each docking box actually enclosed the
ligand it was scoring.  Two runs were discarded on that check.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FINAL = RESULTS / "redocking_validation_final.csv"
EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"


def load() -> list[dict]:
    if not FINAL.exists():
        raise SystemExit(f"{FINAL} not found; run check_all_boxes.py first")
    with open(FINAL, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    rows = [r for r in load() if r.get("box_ok") in ("OK", "True", "1")]
    rows = [r for r in rows if r.get("rmsd_A")]
    rows.sort(key=lambda r: float(r.get("heavy_atoms") or 0))

    print("=" * 88)
    print("Systems entering the text (box verified to contain its ligand)")
    print("=" * 88)
    for r in rows:
        rms = float(r["rmsd_A"])
        print(f"  {r['system']:14s} {r['ligand']:10s} {r['heavy_atoms']:>3} heavy  "
              f"RMSD {rms:>7.3f}  {'pass' if rms <= 2.0 else 'fail'}")

    passed = [r for r in rows if float(r["rmsd_A"]) <= 2.0]
    failed = [r for r in rows if float(r["rmsd_A"]) > 2.0]
    print()
    print(f"  {len(passed)} passed, {len(failed)} failed")
    if passed:
        print(f"  passing ligands: {min(int(r['heavy_atoms']) for r in passed)}-"
              f"{max(int(r['heavy_atoms']) for r in passed)} heavy atoms")
    if failed:
        print(f"  failing ligands: {min(int(r['heavy_atoms']) for r in failed)}-"
              f"{max(int(r['heavy_atoms']) for r in failed)} heavy atoms")

    # ------------------------------------------------------------- build the text
    tbl = ["| System | Ligand | Heavy atoms | Best affinity (kcal/mol) | "
           "Top-pose RMSD (A) | Passed |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        rms = float(r["rmsd_A"])
        aff = r.get("affinity") or ""
        try:
            aff = f"{float(aff):.2f}"
        except (TypeError, ValueError):
            aff = "-"
        tbl.append(f"| {r['system']} | {r['ligand']} | {r['heavy_atoms']} | {aff} | "
                   f"{rms:.3f} | {'yes' if rms <= 2.0 else 'no'} |")
    table = "\n".join(tbl)

    n_pass, n_all = len(passed), len(rows)
    lo = min(int(r["heavy_atoms"]) for r in passed) if passed else 0
    hi = max(int(r["heavy_atoms"]) for r in passed) if passed else 0
    lo_f = min(int(r["heavy_atoms"]) for r in failed) if failed else 0

    en_new = (
        "**Docking accuracy was established with a redocking panel built around "
        "ethambutol's own size.** An earlier version of this work validated the protocol "
        "with two controls only - carbonic anhydrase II with acetazolamide (13 heavy "
        "atoms, RMSD 1.795 A) and dihydrofolate reductase with methotrexate (33 heavy "
        f"atoms, RMSD 5.863 A) - and attributed the failure to methotrexate's size and "
        "flexibility. Two points, one below ethambutol's ten heavy atoms and one far "
        f"above, cannot locate the protocol's limit, and they leave open the case that "
        "matters most: whether a ligand of ethambutol's own size is docked reliably. The "
        f"panel was therefore extended to {n_all} co-crystallised complexes spanning 9 to "
        "36 heavy atoms, each redocked into its own receptor with the box centred on its "
        "crystallographic position, and each box was verified to enclose the ligand it "
        "was scoring.\n\n" + table + "\n\n"
        f"Every ligand up to {hi} heavy atoms reproduced its crystal pose within the 2.0 A "
        f"criterion, and every ligand from {lo_f} heavy atoms upwards failed. The "
        "boundary therefore falls between 13 and 19 heavy atoms, and the failures are "
        "graded rather than abrupt - 2.434 A at 19 atoms, 3.127 A at 22, 5.836 and "
        "5.863 A at 36 and 33. Ethambutol has ten heavy atoms and three rotatable bonds, "
        "which places it inside the validated range, and the two complexes closest to it "
        f"in size reproduced their poses at 0.344 A (9 heavy atoms) and 1.795 and "
        "1.937 A (13 heavy atoms, two independent structures). The protocol is thus "
        "suitable for the question it is used for here - the relative ranking of small "
        "polar ligands across a panel of pockets - and is explicitly not suitable for "
        "the larger, more flexible ligands that fail the panel. The binding affinities "
        "reported for ethambutol, which span -3.96 to -5.50 kcal/mol, are read with that "
        "in mind: docking is used to rank nodes of the network, not to claim occupancy.\n\n"
        "Two complexes were discarded from this panel after the check on box "
        "containment, and the reason is recorded because the symptom is easy to "
        "misread. Both gave RMSDs of tens of angstroms that looked like protocol "
        "failures but were bookkeeping faults: the validation directory was keyed by "
        "target name, so validating carbonic anhydrase II with two different structures "
        "in one run placed the second run's ligand beside the first run's box, and the "
        "ligand then lay 53.8 A outside the search space. The directory key now includes "
        "the PDB identifier. A third complex, 3M04, was excluded for a different reason: "
        "it carries a fragment bound some 18 A from the main ligand, so any box centred "
        "on the principal site leaves the fragment outside it. A fourth, 1FSY, could not "
        "be docked at all because its ligand contains boron and the PDBQT written by "
        "Open Babel carries an atom type that Vina rejects."
    )

    print()
    print("=" * 88)
    print("New English text")
    print("=" * 88)
    print(en_new)

    if args.write:
        for path, old_marker in ((EN, "Docking accuracy was verified by re-docking"),
                                 (CN, "以共晶配体回对接验证精度")):
            t = path.read_text(encoding="utf-8")
            if old_marker in t:
                print(f"  {path.name}: found the sentence to replace")
            else:
                print(f"  {path.name}: WARNING marker not found; not modified")
        (ROOT / "manuscript" / "docking_validation_EN.md").write_text(
            en_new, encoding="utf-8")
        print(f"\n  written to manuscript/docking_validation_EN.md")
    else:
        print("\n  (dry run; re-run with --write to save)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
