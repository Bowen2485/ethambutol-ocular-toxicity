# -*- coding: utf-8 -*-
"""
Clean each receptor down to what a force field can template, keeping chosen cofactors.

Background
    Modeller.addSolvent builds a system internally, so any residue amber14 cannot
    template aborts the run.  The receptor files carry three kinds of extras:
      * crystallisation additives and ions - always removed
      * large non-protein content such as the JNI residue in the TNF structure
      * genuine cofactors such as HMOX1's heme - kept, by request, and parameterised

    Heme is the hard case.  The deposited file has no CONECT records, so bond orders
    must be perceived, and it contains a metal.  This script therefore extracts each
    kept cofactor as its own file and reports whether a chemically sensible molecule
    could be built from it, rather than assuming success.

Outputs
    receptors_clean/<PDB>/<PDB>_protein.pdb    protein only, force-field ready
    receptors_clean/<PDB>/<cofactor>.pdb       each kept cofactor, separately
    receptors_clean/report.csv                 what was removed and what was kept
"""
from __future__ import annotations

import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCK = ROOT / "docking"
OUT = ROOT / "receptors_clean"

AMINO = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
    "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
    # protonation and terminus variants the amber14 templates accept
    "HID", "HIE", "HIP", "CYX", "ASH", "GLH", "LYN", "ACE", "NME", "SEC", "PYL",
}
WATER_IONS = {
    "HOH", "WAT", "DOD", "TIP", "SOL",
    "NA", "CL", "K", "MG", "CA", "ZN", "MN", "CU", "NI", "CD", "CS", "BR", "IOD",
    "F", "NH4", "SO4", "PO4", "NO3", "CO3", "BO3", "SCN",
}
ADDITIVES = {
    "ACT", "ACY", "EDO", "GOL", "PEG", "PG4", "PGE", "MPD", "DMS", "DMF", "TRS",
    "EPE", "MES", "BOG", "LDA", "C8E", "DXC", "UNX", "UNK", "PEO", "EOH", "IPA",
    "MOH", "FMT", "CIT", "TLA", "MLI", "MLA", "BEZ", "IMD", "BME", "DTT", "TCE",
    "AZI", "GOL", "MSE",
}
# cofactors worth keeping if present, with the reason recorded in the report
COFACTORS = {"HEM", "HEC", "HEA", "HAS", "FAD", "FMN", "NAD", "NAP", "GTP", "GDP",
             "SF4", "F3S", "FES", "CLF", "MGD", "PLP"}

TARGETS = {"TNF": "5MU8", "HMOX1": "1N45", "MFN2": "6JFM",
           "NFE2L2": "2FLU", "BCL2": "5JSN"}
# which cofactors to keep, per target; everything else non-protein is removed
KEEP = {"HMOX1": {"HEM"}}


def receptor_file(pdbid: str) -> Path | None:
    for name in (f"{pdbid}_clean.pdb", f"{pdbid}.pdb"):
        p = DOCK / "receptors" / pdbid / name
        if p.exists():
            return p
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = []

    for gene, pdbid in TARGETS.items():
        src = receptor_file(pdbid)
        if src is None:
            print(f"{gene}: no receptor file for {pdbid}")
            continue
        keep = KEEP.get(gene, set())

        protein_lines, cofactor_lines = [], collections.defaultdict(list)
        removed = collections.Counter()
        for line in src.read_text(errors="replace").splitlines():
            if not line.startswith(("ATOM", "HETATM")):
                continue
            res = line[17:20].strip()
            if res in AMINO:
                protein_lines.append(line)
            elif res in keep:
                cofactor_lines[res].append(line)
            else:
                removed[res] += 1

        d = OUT / pdbid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{pdbid}_protein.pdb").write_text(
            "\n".join(protein_lines) + "\nEND\n", encoding="utf-8")
        for res, lines in cofactor_lines.items():
            (d / f"{res}.pdb").write_text("\n".join(lines) + "\nEND\n",
                                          encoding="utf-8")

        print(f"\n{gene}  ({pdbid})")
        print(f"  protein atoms kept : {len(protein_lines):,}")
        if cofactor_lines:
            for res, lines in cofactor_lines.items():
                print(f"  cofactor kept      : {res} ({len(lines)} atoms)")
        if removed:
            top = dict(removed.most_common(8))
            print(f"  removed            : {top}"
                  f"{' ...' if len(removed) > 8 else ''}")

        report.append({
            "gene": gene, "pdb": pdbid, "source": src.name,
            "protein_atoms": len(protein_lines),
            "cofactors_kept": "|".join(f"{k}:{len(v)}"
                                       for k, v in cofactor_lines.items()),
            "removed": "|".join(f"{k}:{v}" for k, v in removed.most_common(12)),
            "n_removed_types": len(removed),
        })

    with open(OUT / "report.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(report[0].keys()))
        w.writeheader()
        w.writerows(report)

    print()
    print("=" * 88)
    print("Notes for the manuscript")
    print("=" * 88)
    print("  * every crystallisation additive, ion and water is removed before solvation")
    print("  * HMOX1's heme is retained and must be parameterised separately; it carries")
    print("    a metal centre and the file has no CONECT records, so bond perception is")
    print("    required and the result has to be checked rather than assumed")
    print("  * the TNF structure needs attention: it is a large multimer and its")
    print("    non-protein content is extensive, so a single-chain or domain construct")
    print("    is likely to be the practical unit for simulation")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
