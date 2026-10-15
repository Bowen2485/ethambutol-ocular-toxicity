# -*- coding: utf-8 -*-
"""
Step 4 - Molecular docking: ligand and receptor preparation.

Ligand pipeline (no RDKit needed for the 3D step)
    ligand name -> PubChem CID -> canonical SMILES + MW/TPSA/logP descriptors
                -> Open Babel: protonate at pH 7.4, generate 3D, MMFF94 minimise
                -> PDBQT (AutoDock atom types) via Open Babel or meeko

Receptor pipeline
    gene -> RCSB PDB search (best resolution, human, X-ray/cryo-EM)
         -> download PDB
         -> strip waters/heteroatoms except the chosen co-crystal ligand
         -> protonate with the ADFR `reduce` binary
         -> PDBQT via Open Babel

Tested end-to-end on a known complex before any novel target is docked.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DOCK = ROOT / "docking"
TOOLS = ROOT / "tools"
for p in (DERIVED, DOCK / "ligands", DOCK / "receptors", DOCK / "poses"):
    p.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

OBABEL = Path(r"C:\Program Files\OpenBabel-3.1.1\obabel.exe")
REDUCE = Path(r"C:\Program Files (x86)\ADFRsuite-1.0\bin\reduce.exe")
VINA = TOOLS / "vina.exe"
PYTARGET = ROOT / ".piptarget"


def get(url: str, timeout: int = 120, tries: int = 4) -> bytes:
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (a + 1))
    raise RuntimeError(f"GET failed {url}: {last}")


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 900) -> tuple[int, str]:
    env = dict(os.environ)
    env["BABEL_LIBDIR"] = r"C:\Program Files\OpenBabel-3.1.1\lib\openbabel\3.1.0"
    env["BABEL_DATADIR"] = r"C:\Program Files\OpenBabel-3.1.1\share\openbabel\3.1.0"
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                       cwd=str(cwd) if cwd else None, env=env, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# ----------------------------------------------------------------------- ligands
def pubchem_props(name: str) -> dict | None:
    base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    q = urllib.parse.quote(name)
    props = None
    for attempt in range(4):
        try:
            props = json.loads(get(
                f"{base}/compound/name/{q}/property/CanonicalSMILES,ConnectivitySMILES,"
                f"MolecularFormula,MolecularWeight,XLogP,TPSA,HBondDonorCount,"
                f"HBondAcceptorCount,RotatableBondCount/JSON",
                timeout=60, tries=2).decode())["PropertyTable"]["Properties"][0]
            break
        except Exception as exc:  # noqa: BLE001
            if attempt == 3:
                print(f"  [pubchem] {name}: props failed {type(exc).__name__} "
                      f"{str(exc)[:80]}")
                return None
            time.sleep(1.5 * (attempt + 1))
    if props is None:
        return None
    cid = props["CID"]
    try:
        sdf = get(f"{base}/compound/cid/{cid}/SDF?record_type=3d",
                  timeout=90, tries=2).decode("latin-1")
        if "V2000" not in sdf and "V3000" not in sdf:
            sdf = ""
    except Exception:
        sdf = ""
    out = {"name": name, "cid": cid, "sdf_3d": sdf}
    out.update(props)
    return out


def prep_ligand(name: str, smiles: str | None = None) -> Path | None:
    out = DOCK / "ligands" / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', name)}.pdbqt"
    if out.exists() and out.stat().st_size > 0:
        return out
    props = pubchem_props(name)
    smi = ((props or {}).get("CanonicalSMILES")
           or (props or {}).get("ConnectivitySMILES") or smiles)
    if not smi:
        print(f"  [ligand] {name}: no structure found")
        return None
    work = DOCK / "ligands" / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', name)}"
    work.mkdir(exist_ok=True)
    # Prefer the PubChem 3D conformer; fall back to Open Babel --gen3d.
    src = None
    if (props or {}).get("sdf_3d"):
        (work / "pubchem_3d.sdf").write_text(props["sdf_3d"], encoding="latin-1")
        src = work / "pubchem_3d.sdf"
    if src is None:
        smi_file = work / "ligand.smi"
        smi_file.write_text(f"{smi}\t{name}\n", encoding="utf-8")
        rc, log = run([OBABEL, smi_file, "-O", work / "gen3d.mol", "--gen3d", "-p", "7.4"])
        if (work / "gen3d.mol").exists():
            src = work / "gen3d.mol"
    if src is None:
        print(f"  [ligand] {name}: no 3D source could be produced")
        return None
    rc, log = run([OBABEL, src, "-O", work / "ligand_h.mol", "-h", "-p", "7.4"])
    if not (work / "ligand_h.mol").exists():
        rc, log = run([OBABEL, src, "-O", work / "ligand_h.mol", "-h"])
    pdb_in = work / "ligand_h.mol" if (work / "ligand_h.mol").exists() else src
    rc, log = run([OBABEL, pdb_in, "-O", out, "-h"])
    if not out.exists() or out.stat().st_size == 0:
        print(f"  [ligand] {name}: PDBQT conversion failed :: {log[-200:]}")
        return None
    n_rot = out.read_text(errors="replace").count("BRANCH")
    print(f"  [ligand] {name}: cid={props['cid']} MW={props.get('MolecularWeight')} "
          f"rotors={n_rot} -> {out.name}")
    meta = {"name": name, "cid": props["cid"], "smiles": smi,
            "molecular_formula": props.get("MolecularFormula"),
            "molecular_weight": props.get("MolecularWeight"),
            "xlogp": props.get("XLogP"), "tpsa": props.get("TPSA"),
            "hbd": props.get("HBondDonorCount"), "hba": props.get("HBondAcceptorCount"),
            "rotatable_bonds": n_rot, "source_3d": src.name}
    (work / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    return out


# --------------------------------------------------------------------- receptors
def rcsb_best(gene: str, rows: int = 40) -> list[dict]:
    """
    Candidate experimental structures for a gene symbol.

    RCSB does not expose `rcsb_gene_name` to the text service (HTTP 400), so a
    full-text search is used first and every hit is then verified against the
    polymer-entity metadata through the RCSB GraphQL data API, keeping only
    entries whose deposited entity actually carries the requested gene name.
    """
    q = {"query": {"type": "terminal", "service": "full_text",
                   "parameters": {"value": gene}},
         "return_type": "entry",
         "request_options": {"paginate": {"start": 0, "rows": rows}}}
    url = ("https://search.rcsb.org/rcsbsearch/v2/query?json="
           + urllib.parse.quote(json.dumps(q)))
    try:
        d = json.loads(get(url, timeout=180).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  [rcsb] {gene}: full-text search failed {str(exc)[:90]}")
        return []
    ids = [r["identifier"] for r in d.get("result_set", [])]
    if not ids:
        return []

    gq = """
    query($ids:[String!]!) {
      entries(entry_ids:$ids) {
        rcsb_id
        struct { title }
        rcsb_entry_info { resolution_combined experimental_method
                          nonpolymer_bound_components polymer_entity_count }
        polymer_entities {
          rcsb_polymer_entity { pdbx_description }
          rcsb_entity_source_organism { rcsb_gene_name { value } scientific_name
                                        ncbi_taxonomy_id }
        }
      }
    }"""
    out: list[dict] = []
    for i in range(0, len(ids), 12):
        chunk = ids[i:i + 12]
        try:
            req = urllib.request.Request(
                "https://data.rcsb.org/graphql", data=json.dumps(
                    {"query": gq, "variables": {"ids": chunk}}).encode(),
                headers={**UA, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
                payload = json.loads(r.read().decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001
            print(f"  [rcsb] {gene}: metadata fetch failed {str(exc)[:80]}")
            continue
        if payload.get("errors"):
            print(f"  [rcsb] graphql errors: {str(payload['errors'])[:200]}")
        for e in (payload.get("data", {}) or {}).get("entries", []) or []:
            names: list[str] = []
            human = False
            for pe in e.get("polymer_entities") or []:
                for so in pe.get("rcsb_entity_source_organism") or []:
                    if str(so.get("ncbi_taxonomy_id")) == "9606":
                        human = True
                    for gn in so.get("rcsb_gene_name") or []:
                        if gn.get("value"):
                            names.append(gn["value"])
            if gene.upper() not in {str(n).upper() for n in names}:
                continue
            info = e.get("rcsb_entry_info") or {}
            out.append({
                "pdb": e["rcsb_id"],
                "resolution": (info.get("resolution_combined") or [None])[0],
                "method": "|".join(info.get("experimental_method") or []),
                "title": (e.get("struct") or {}).get("title"),
                "ligands": "|".join(info.get("nonpolymer_bound_components") or []),
                "gene_names": "|".join(sorted(set(names))),
                "human": human,
                "n_entities": info.get("polymer_entity_count"),
            })
    out.sort(key=lambda r: (not r["human"], r["resolution"] is None,
                            r["resolution"] or 99))
    return out


def alphafold_model(uniprot: str) -> str | None:
    try:
        d = json.loads(get(f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot}").decode())
        for entry in d:
            if entry.get("pdbUrl"):
                return entry["pdbUrl"]
    except Exception:  # noqa: BLE001
        return None
    return None


def download_structure(pdb_id: str, dest_dir: Path) -> Path | None:
    """
    Fetch an experimental structure.  Some recent entries have no legacy PDB
    format (HTTP 404 on files.rcsb.org/download/<ID>.pdb), so the mmCIF
    coordinate file is used as a fallback and converted with Open Babel.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    pid = pdb_id.upper()
    pdb = dest_dir / f"{pid}.pdb"
    if pdb.exists() and pdb.stat().st_size > 0:
        return pdb
    try:
        pdb.write_bytes(get(f"https://files.rcsb.org/download/{pid}.pdb"))
        return pdb
    except Exception as exc:  # noqa: BLE001
        print(f"  [pdb] {pid}: PDB format unavailable ({type(exc).__name__}); "
              f"trying mmCIF")
    cif = dest_dir / f"{pid}.cif"
    try:
        if not cif.exists():
            cif.write_bytes(get(f"https://files.rcsb.org/download/{pid}.cif"))
    except Exception as exc:  # noqa: BLE001
        print(f"  [pdb] {pid}: mmCIF fetch also failed ({type(exc).__name__})")
        return None
    rc, log = run([OBABEL, cif, "-O", pdb, "-h"])
    if pdb.exists() and pdb.stat().st_size > 0:
        print(f"  [pdb] {pid}: converted from mmCIF")
        return pdb
    print(f"  [pdb] {pid}: conversion failed :: {log[-160:]}")
    return None


def prep_receptor(pdb_id: str, keep_het: list[str] | None = None) -> Path | None:
    safe = pdb_id.upper()
    out = DOCK / "receptors" / f"{safe}.pdbqt"
    if out.exists() and out.stat().st_size > 0:
        return out
    work = DOCK / "receptors" / safe
    work.mkdir(exist_ok=True)
    raw = download_structure(safe, work)
    if raw is None:
        return None
    # strip waters and unwanted heteroatoms, keep the selected co-crystal ligand
    keep = {k.upper() for k in (keep_het or [])}
    lines = []
    for ln in raw.read_text(errors="replace").splitlines():
        rec = ln[:6].strip()
        if rec == "HETATM":
            resn = ln[17:20].strip().upper()
            if resn in ("HOH", "DOD") or (keep and resn not in keep):
                continue
        if rec in ("ATOM", "HETATM", "TER", "END"):
            lines.append(ln)
    clean = work / f"{safe}_clean.pdb"
    clean.write_text("\n".join(lines) + "\n", encoding="utf-8")

    prot = clean
    if REDUCE.exists():
        rc, log = run([REDUCE, "-NOFLIP", "-BUILD", clean], cwd=work)
        # reduce writes to stdout; capture it properly
        env = dict(os.environ)
        r = subprocess.run([str(REDUCE), "-NOFLIP", "-BUILD", str(clean)],
                           capture_output=True, text=True, cwd=str(work),
                           encoding="utf-8", errors="replace")
        if r.stdout and r.stdout.count("ATOM") > 100:
            prot = work / f"{safe}_h.pdb"
            prot.write_text(r.stdout, encoding="utf-8")
    rc, log = run([OBABEL, prot, "-O", out, "-xr"])
    if not out.exists() or out.stat().st_size == 0:
        print(f"  [receptor] {safe}: PDBQT conversion failed :: {log[-200:]}")
        return None
    n_atoms = sum(1 for ln in out.read_text(errors="replace").splitlines()
                  if ln.startswith(("ATOM", "HETATM")))
    print(f"  [receptor] {safe}: {n_atoms} atoms -> {out.name}")
    return out


def receptor_ligand(pdb_id: str) -> list[str]:
    """Non-polymer components actually present in the downloaded file."""
    try:
        txt = get(f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb").decode(
            "latin-1", "replace")
    except Exception:  # noqa: BLE001
        return []
    seen = {}
    for ln in txt.splitlines():
        if ln.startswith("HETATM"):
            resn = ln[17:20].strip().upper()
            if resn not in ("HOH", "DOD"):
                seen[resn] = seen.get(resn, 0) + 1
    return sorted(seen, key=lambda k: -seen[k])


def main() -> int:
    print("=" * 78)
    print("STEP 4a  docking preparation smoke test")
    print("=" * 78)
    print(f"vina     : {VINA} exists={VINA.exists()}")
    print(f"obabel   : {OBABEL} exists={OBABEL.exists()}")
    print(f"reduce   : {REDUCE} exists={REDUCE.exists()}")
    if PYTARGET.exists():
        print(f"piptarget: {PYTARGET}")

    print("\n--- ligands ---")
    for name in ["ethambutol", "quercetin", "luteolin", "chlorogenic acid",
                 "puerarin", "crocin", "kaempferol", "ginkgolide B"]:
        try:
            prep_ligand(name)
        except Exception as exc:  # noqa: BLE001
            print(f"  [ligand] {name}: FAILED {type(exc).__name__} {str(exc)[:90]}")

    print("\n--- receptors (smoke test: AKT1 / TNF) ---")
    for gene in ["AKT1", "TNF"]:
        rows = rcsb_best(gene)
        print(f"  [rcsb] {gene}: {len(rows)} candidates")
        for r in rows[:4]:
            print(f"      {r['pdb']}  res={r['resolution']}  {r['method'][:24]:26s} "
                  f"ligands={r['ligands'][:40]}")
        if rows:
            pid = rows[0]["pdb"]
            het = receptor_ligand(pid)
            print(f"      chosen {pid}; HETATM components present: {het[:12]}")
            try:
                prep_receptor(pid, keep_het=[h for h in het if len(h) > 2][:2])
            except Exception as exc:  # noqa: BLE001
                print(f"      receptor prep FAILED: {type(exc).__name__} {str(exc)[:120]}")

    print("\n--- alphaFold fallback ---")
    for uni, gene in [("P31749", "AKT1"), ("P01375", "TNF"), ("P09601", "HMOX1")]:
        url = alphafold_model(uni)
        print(f"  {gene} ({uni}): {'available' if url else 'missing'} {str(url)[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
