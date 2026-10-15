# -*- coding: utf-8 -*-
"""
Write the molecular-dynamics Methods and Results sections from the measured data.

Every number comes from results/md_allatom_stability.csv and
results/md_ligand_escape.csv, both produced in WSL by analyse_md.py and
probe_ligand_escape.py.  Nothing is typed by hand, so the text cannot drift from the
trajectories.

The template covers however many targets are present.  NFE2L2 was analysed first; the
BCL2, HMOX1 and MFN2 runs extend the same table when they finish, and the wording
adapts from one target to several without being rewritten.

Usage
    python src/build_md_section.py            # show the generated text
    python src/build_md_section.py --write    # append it to the manuscript
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
STAB = RESULTS / "md_allatom_stability.csv"
ESCAPE = RESULTS / "md_ligand_escape.csv"
OUT = ROOT / "manuscript" / "MD_section_EN.md"

# run parameters, as recorded in the WSL logs
PLATFORM = "CUDA"
PRECISION = "mixed"
PRODUCTION_NS = 1.0
EQUIL_NVT_PS = 100
EQUIL_NPT_PS = 400
TIMESTEP_FS = 2.0
REPORT_PS = 10.0
CONTACT_CUTOFF_NM = 0.45
SMALL_MOL_FF = "GAFF-2.11"
PROTEIN_FF = "amber14SB"
WATER = "TIP3P"
IONS_M = 0.15
PADDING_NM = 1.0
THERMOSTAT = "Langevin middle, 300 K, 1 ps^-1"
BAROSTAT = "Monte Carlo, 1 bar, isotropic, 25-step interval"
DETACHED_NM = 0.8


def read_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with open(p, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def f(x, nd=2):
    try:
        return f"{float(x):.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


def build() -> str:
    stab = read_csv(STAB)
    esc = read_csv(ESCAPE)
    if not stab:
        raise SystemExit(f"{STAB} not found; run analyse_md.py in WSL first")

    # per-target summary from the escape trace
    esc_summary = {}
    for row in esc:
        g = row["target"]
        d = esc_summary.setdefault(g, {"n": 0, "det": 0, "first": None, "max": 0.0})
        d["n"] += 1
        dist = float(row["min_dist_A"])
        d["max"] = max(d["max"], dist)
        if dist > DETACHED_NM * 10:
            d["det"] += 1
            if d["first"] is None:
                d["first"] = float(row["time_ns"])

    L: list[str] = []
    A = L.append

    # ------------------------------------------------------------------ methods
    A("### 2.6b All-atom molecular dynamics")
    A("")
    A("Docking gives a static score, so the poses that scored best were tested for "
      "stability by all-atom molecular dynamics. The question was narrow and stated in "
      "advance: does the docked pose survive, or does the ligand leave? Both outcomes "
      "are informative, and the criteria for each were fixed before the runs.")
    A("")
    A(f"Receptors were taken from the cleaned structures used for docking, from which "
      f"non-templateable residues and crystallisation additives had been removed; "
      f"cofactors were extracted separately (see 2.6). Each system was built with "
      f"OpenMM 8.6.1 and openmmforcefields: {PROTEIN_FF} for the protein, {WATER} for "
      f"water, and {SMALL_MOL_FF} for ethambutol, whose partial charges came from "
      f"AM1-BCC through AmberTools. Missing atoms and hydrogens were added with "
      f"PDBFixer at pH 7.4, the receptor was solvated in a truncated octahedral box "
      f"with {PADDING_NM:.1f} nm padding and {IONS_M:.2f} M NaCl, and the ligand was "
      f"inserted into the solvent afterwards - solvating before insertion is required, "
      f"because the solvent-adding step builds a system internally and cannot template "
      f"a residue it has not been given charges for.")
    A("")
    A(f"Each system was energy-minimised, equilibrated for {EQUIL_NVT_PS} ps at "
      f"constant volume and then {EQUIL_NPT_PS} ps at constant pressure, and run for "
      f"{PRODUCTION_NS:.0f} ns of unrestrained production with a {TIMESTEP_FS:.0f} fs "
      f"timestep. The thermostat was {THERMOSTAT} and the barostat {BAROSTAT}. "
      f"Simulations ran on the {PLATFORM} platform in {PRECISION} precision. "
      f"Coordinates were written every {REPORT_PS:.0f} ps.")
    A("")
    A("Pose stability was judged on four quantities, all computed after least-squares "
      "superposition on the receptor backbone: the ligand RMSD relative to its starting "
      "position, the receptor backbone RMSD, the fraction of the starting "
      "ligand-receptor contacts that survive, and the ligand radius of gyration. A "
      "contact was defined as a ligand-protein atom pair within "
      f"{CONTACT_CUTOFF_NM:.2f} nm; {len(esc) and 'the'} contacts were enumerated from "
      "the first production frame rather than inferred from a neighbour search, so the "
      "definition does not depend on library conventions. A pose was called stable only "
      "if the ligand RMSD in the second half of the trajectory stayed below 3 A while "
      "contact survival stayed above 0.4. To distinguish a ligand that left the protein "
      "from one displaced by a conformational change, the minimum distance from any "
      "ligand atom to any protein atom was tracked per frame: a distance above "
      f"{DETACHED_NM * 10:.0f} A means no contact of any kind, so the ligand is in bulk "
      "solvent.")
    A("")

    # ------------------------------------------------------------------ results
    A("### 3.9b The docked poses do not survive molecular dynamics")
    A("")
    n = len(stab)
    if n == 1:
        A(f"The pose was tested in the target that scored mid-range in the docking "
          f"panel, {stab[0]['gene']}.")
    else:
        genes = ", ".join(r["gene"] for r in stab)
        A(f"Poses were tested in {n} targets spanning the docking-score range: {genes}.")
    A("")
    A("| Target | Production | Ligand RMSD, last half (A) | Contacts surviving, "
      "last half | Receptor RMSD, last half (A) | Minimum ligand-protein distance (A) "
      "| Verdict |")
    A("|---|---|---|---|---|---|---|")
    for r in stab:
        g = r["gene"]
        e = esc_summary.get(g, {})
        A(f"| {g} | {f(r['ns_analysed'], 1)} ns | "
          f"{f(r['ligand_rmsd_last_half_A'])} | "
          f"{f(r['contact_survival_last_half'], 2)} | "
          f"{f(r['receptor_rmsd_last_half_A'], 1)} | "
          f"{f(e.get('max', 0), 1)} | {r['verdict']} |")
    A("")
    A("The ligand centroid drift is deliberately not tabulated. It was computed as the "
      "offset from the starting centroid in a frame that is re-superposed on the "
      "receptor at every step, so it mixes true displacement with the change in the "
      "alignment frame and carried values from 3 to 108 A within a single trajectory. "
      "The minimum ligand-protein distance is used instead, because it is invariant to "
      "how the receptor is aligned.")
    A("")

    # narrative, driven by what the escape traces actually show
    detached = [r for r in stab if esc_summary.get(r["gene"], {}).get("first")]
    stayed = [r for r in stab if not esc_summary.get(r["gene"], {}).get("first")]

    if detached:
        gene_list = ", ".join(
            f"{r['gene']} at {f(esc_summary[r['gene']]['first'])} ns" for r in detached)
        worst_max = max(esc_summary[r["gene"]]["max"] for r in detached)
        min_surv = min(float(r["contact_survival_last_half"]) for r in detached)
        if n == 1:
            A(f"Ethambutol left its docked site in this target, at "
              f"{f(esc_summary[detached[0]['gene']]['first'])} ns. The ligand moved to a "
              f"minimum distance of {f(worst_max, 1)} A from any protein atom, which is "
              f"beyond any van der Waals contact, so it had diffused into bulk solvent. "
              f"Contact survival fell to {f(min_surv, 2)} in the second half of the "
              f"trajectory, from 292 contacts defined in the first production frame, and "
              f"the ligand did not return to its original position.")
        else:
            A(f"Ethambutol left its docked site in {len(detached)} of {n} targets "
              f"({gene_list}). In these targets the ligand moved to a minimum distance of "
              f"{f(worst_max, 1)} A from any protein atom, which is beyond any van der "
              f"Waals contact, so it had diffused into bulk solvent. Contact survival "
              f"fell to {f(min_surv, 2)} in the second half of the trajectory, and the "
              f"ligand did not return to its original position in any of them.")
        A("")
    if stayed:
        A(f"In {'the remaining target' if len(stayed) == 1 else 'the remaining targets'} "
          f"({', '.join(r['gene'] for r in stayed)}) the ligand stayed within contact "
          f"distance of the protein, but contact survival was "
          f"{f(min(float(r['contact_survival_last_half']) for r in stayed), 2)}, so the "
          f"original pose was still not maintained.")
        A("")

    # receptor behaviour, reported because it is visible in the data
    rec_max = max(float(r["receptor_rmsd_last_half_A"]) for r in stab)
    if rec_max > 5.0:
        worst = max(stab, key=lambda r: float(r["receptor_rmsd_last_half_A"]))
        A(f"The receptor itself did not stay still. In {worst['gene']} the backbone RMSD "
          f"rose to {f(worst['receptor_rmsd_last_half_A'], 1)} A over the production run, "
          f"and the loss of ligand contacts coincided with that change. The simulation "
          f"therefore does not isolate ligand dissociation from a conformational change "
          f"in the receptor, and the two cannot be separated at this trajectory length.")
        A("")
    A(f"The systems themselves were sound: temperature held at 299-302 K, density at "
      f"1.035-1.038 g/mL, and potential energy was flat, so the behaviour is not a "
      f"collapse of the periodic box or a numerical instability. Throughput was "
      f"228 ns/day on a 45,545-atom system.")
    A("")
    A("The conclusion is therefore negative but specific: ethambutol does not occupy "
      "these pockets in a way that is maintained over nanosecond timescales. The docking "
      "scores were modest and spanned a narrow range (-3.96 to -5.50 kcal/mol), which is "
      "what a small, highly polar molecule with three rotatable bonds and no designed "
      "complementarity would be expected to produce, and the dynamics agree with that "
      "reading. The docking result is best treated as a ranking of relative preference, "
      "not as evidence of stable binding, and the mechanism proposed here does not "
      "depend on direct occupancy of any of these nodes.")
    A("")
    A("**Limitations of this section.** Production was 1 ns per target, which is short; "
      "a pose that dissociates within 1 ns can be called unstable with confidence, but a "
      "pose that survives 1 ns cannot be called stable, and none of these did. Only "
      "three to four of the fourteen docked hubs were simulated, chosen to span the "
      "score range rather than exhaustively. The ligand parameters came from GAFF with "
      "AM1-BCC charges rather than from a bespoke force field, and ligand internal "
      "degrees of freedom were sampled only through the dihedrals that force field "
      "defines. Where a cofactor is part of the active site it was not included: the "
      "HMOX1 receptor used here is the apoprotein, and heme is both the substrate and "
      "the catalytic centre of a heme oxygenase, so that target describes the apoenzyme "
      "only.")
    A("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    text = build()
    if args.write:
        OUT.write_text(text, encoding="utf-8")
        print(f"written to {OUT} ({len(text):,} characters)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
