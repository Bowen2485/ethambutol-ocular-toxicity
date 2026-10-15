# -*- coding: utf-8 -*-
"""
Choose a redocking validation set by querying the structures, not by guessing PDB IDs.

Why a new set is needed
    The existing controls bracket ethambutol rather than covering it: acetazolamide has
    13 heavy atoms and passed at 1.795 A, methotrexate has 33 and failed at 5.863 A,
    while ethambutol has 10 heavy atoms and three rotatable bonds.  A protocol validated
    only at the two ends of a size range says nothing about the middle, and a reviewer is
    entitled to point that out.

    The set is therefore rebuilt around ligands matched to ethambutol: small (roughly
    8-20 heavy atoms), with few rotatable bonds, and - because ethambutol is a flexible
    polyol with ionisable amines - ideally also polar and hydrogen-bonding rather than
    purely aromatic.  That is where a docking protocol most plausibly fails.

What this does
    For each candidate structure it fetches the RCSB entry and reports every
    non-polymer, non-water component with its heavy-atom count and the chain it sits in.
    Nothing is assumed about which ligand is present or what it is called.  Only once
    these are known can the redocking set be defined, and a wrong ligand key would
    otherwise fail silently at the "no co-crystal ligand" branch of the pipeline.

Usage
    python src/probe_validation_candidates.py
"""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from collections import defaultdict

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 research/1.0"}

# candidates chosen so that the ligands span the relevant size and polarity range;
# the PDB IDs are hypotheses to be checked, not assertions
CANDIDATES = [
    ("CA2", "3HS4", "existing control - acetazolamide"),
    ("DHFR", "1RG7", "existing control - methotrexate"),
    ("CA2", "1AZM", "aromatic sulfonamide, small"),
    ("CA2", "3M04", "second CA2 ligand, small"),
    ("TRYPSIN", "3PTB", "benzamidine, very small and rigid"),
    ("TRYPSIN", "1DWD", "second trypsin ligand"),
    ("DHFR", "3DFR", "NADPH and folate analogue"),
    ("DHFR", "1DHF", "methotrexate, alternative entry"),
    ("HSP90", "1UYG", "resorcinol, small and polar"),
    ("PNP", "1B8O", "immucillin, polar"),
    ("FXA", "1MQ6", "small peptidomimetic"),
    ("THROMBIN", "1DWD", "checked above under trypsin"),
    ("HIVP", "1OHR", "cyclic urea inhibitor"),
    ("BACE1", "2OH4", "hydroxyethylamine, hydroxy-rich like ethambutol"),
    ("PDE5", "1UDT", "sildenafil analogue"),
    ("ALK", "2XP2", "small kinase inhibitor"),
    ("EGFR", "1M17", "erlotinib"),
    ("BRAF", "1UWH", "small kinase ligand"),
    ("AMPC", "1FSY", "boronic acid, very small"),
    ("CARB", "1CBY", "small ligand, polar"),
]


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def heavy_atoms(pdb_text: str, resname: str, chain: str, resseq: str) -> int:
    """Count non-hydrogen atoms of one residue, using the element column."""
    n = 0
    for ln in pdb_text.splitlines():
        if not ln.startswith(("ATOM", "HETATM")):
            continue
        if ln[17:20].strip() != resname or ln[21:22].strip() != chain:
            continue
        if ln[22:27].strip() != resseq:
            continue
        el = ln[76:78].strip().upper() if len(ln) >= 78 else ""
        if not el:
            name = ln[12:16].strip()
            el = name[0] if name else ""
        if el and el != "H":
            n += 1
    return n


print("=" * 92)
print("Evaluating candidate validation systems")
print("=" * 92)
print(f"  {'target':10s} {'pdb':6s} {'ligand':10s} {'chain':5s} {'heavy':>6s}  note")
print("  " + "-" * 86)

keep = []
for target, pdb, note in CANDIDATES:
    try:
        pdb_text = fetch(f"https://files.rcsb.org/download/{pdb}.pdb").decode(
            "utf-8", "replace")
    except urllib.error.HTTPError as exc:
        print(f"  {target:10s} {pdb:6s} {'-':10s} {'-':5s} {'-':>6s}  "
              f"HTTP {exc.code}")
        continue
    except Exception as exc:  # noqa: BLE001
        print(f"  {target:10s} {pdb:6s} {'-':10s} {'-':5s} {'-':6s}  "
              f"{type(exc).__name__}")
        continue

    # collect HETATM residues, excluding water and common cryoprotectants
    seen = defaultdict(lambda: {"chains": set(), "resseq": set()})
    for ln in pdb_text.splitlines():
        if not ln.startswith("HETATM"):
            continue
        rn = ln[17:20].strip()
        if rn in ("HOH", "DOD", "WAT"):
            continue
        seen[rn]["chains"].add(ln[21:22].strip())
        seen[rn]["resseq"].add(ln[22:27].strip())

    if not seen:
        print(f"  {target:10s} {pdb:6s} {'none':10s} {'-':5s} {'-':>6s}  "
              f"no non-water hetero residues")
        continue

    # report each component with its heavy-atom count
    rows = []
    for rn, info in seen.items():
        chain = sorted(info["chains"])[0]
        rs = sorted(info["resseq"])[0]
        n = heavy_atoms(pdb_text, rn, chain, rs)
        rows.append((n, rn, chain, rs, len(info["chains"])))
    rows.sort(reverse=True)

    for n, rn, chain, rs, nch in rows[:4]:
        tag = "  <-- candidate" if 8 <= n <= 22 else ""
        print(f"  {target:10s} {pdb:6s} {rn:10s} {chain:5s} {n:>6d}  "
              f"{note if n == rows[0][0] else ''}{tag}")
        if 8 <= n <= 22:
            keep.append({"target": f"{target}_{rn}", "pdb": pdb, "ligand": rn,
                         "chain": chain, "resseq": rs, "heavy": n, "note": note})
    if len(rows) > 4:
        print(f"  {'':10s} {'':6s} ... {len(rows) - 4} more components")

print()
print("=" * 92)
print("Ligands in the ethambutol size range (8-22 heavy atoms)")
print("=" * 92)
out = []
for k in keep:
    # the pipeline picks the largest ligand by default, so the resname must be given
    out.append(k)
    print(f"  {k['target']:22s} {k['pdb']}  {k['ligand']:8s} chain {k['chain']}  "
          f"{k['heavy']:>3d} heavy atoms   ({k['note']})")
print(f"\n  {len(out)} candidate systems")

here = __import__("pathlib").Path(__file__).resolve().parents[1]
res = here / "results"
res.mkdir(exist_ok=True)
(res / "validation_candidates.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8")
print(f"  -> {res / 'validation_candidates.json'}")
print()
print("  Build the validation set from these by taking several systems that bracket")
print("  ethambutol's 10 heavy atoms, then running the pipeline's own redocking check")
print("  so the new numbers are directly comparable with the existing ones.")
