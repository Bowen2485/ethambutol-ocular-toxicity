# -*- coding: utf-8 -*-
"""
Do the immune-cell part of the infiltration analysis with the data already on disk.

Why this and not CIBERSORTx
    The comparator paper that ran immune infiltration did so on bulk tissue expression, where
    the fraction of each immune cell type has to be inferred by deconvolution.  That needs an
    expression matrix this project does not have, and the tools that do it - CIBERSORTx,
    TIMER2.0 - either require registration or run as web services on data that would have to be
    uploaded.

    The Human Protein Atlas single-cell table, 141.9 MB of which is already in data/raw/hpa,
    sidesteps the deconvolution entirely for the question that matters here.  Bulk tissue has to
    have its composition inferred; single-cell data measure it.  The table holds 154 cell types
    including the ones that constitute immune presence in the retina - microglia, which are its
    resident macrophages, and the vascular and stromal cells that carry the rest - so the
    question "are this network's genes expressed in the cells that mediate immune signalling in
    the retina" can be asked directly rather than estimated.

Why it matters for this manuscript
    Section 3.11 reports that 31 of the 33 hubs are detected in retinal clusters, with TNF among
    the two that are not.  TNF is the archetypal microglial cytokine and a hub of this network,
    so its absence from the eight retinal clusters is either a fact about the retina or an
    artefact of which clusters the HPA table names.  Reading the microglial column settles it,
    and the answer changes how the inflammatory arm of the network should be described.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HPA = ROOT / "data" / "raw" / "hpa" / "rna_single_cell_type.tsv"
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

if not HPA.exists():
    raise SystemExit(f"HPA table not found at {HPA}")

HUBS = ["TP53", "NFE2L2", "AKT1", "BCL2", "HMOX1", "CASP3", "SOD2", "TNF", "GPX4",
        "MFN2", "SLC7A11", "ACSL4", "SDHB", "OPA1", "SLC25A4", "KEAP1", "MAPK1",
        "IL6", "STAT3", "CAT", "GPX1", "TXN", "NQO1", "HIF1A", "PPARGC1A", "DNM1L",
        "VDAC1", "CYCS", "APAF1", "BAX", "BCL2L1", "FTH1", "FTL"]
CONTROL = ["HBB", "HBA1", "ALB", "APOA1", "APOB", "FGA", "FGB", "FGG", "SERPINA1",
           "ORM1", "HP", "TF", "CP", "AMY1A", "AMY2A", "PRSS1", "CELA1", "CTRB1",
           "CPA1", "PNLIP", "CLPS", "CELA3A", "SYCN", "PNLIPRP1", "CTRB2", "CEL",
           "CPA2", "PRSS2", "CTRC", "CELP", "PNLIPRP2", "CLPSL1", "CELA2A"]

#: cell types whose expression constitutes immune presence in the retina.  Microglia are its
#: resident macrophages; the others are the vascular and stromal cells that carry the rest of
#: the retinal immune signalling.  The names are matched loosely because the HPA labels vary
#: in capitalisation and punctuation.
IMMUNE = {
    "microglial cells": r"microgli",
    "macrophages": r"macrophage",
    "endothelial cells": r"endothelial",
    "fibroblasts": r"fibroblast",
    "pericytes": r"pericyte",
    "T-cells": r"\bT-cells?\b",
    "NK-cells": r"NK-cell",
    "B-cells": r"B-cell",
    "monocytes": r"monocyte",
    "neutrophils": r"neutrophil",
    "dendritic cells": r"dendritic",
    "plasma cells": r"plasma cell",
    "mast cells": r"mast cell",
    "retinal ganglion cells": r"retinal ganglion",
    "müller glia": r"m[üu]ller glia",
    "retinal pigment epithelial cells": r"pigment epithelial",
}

#: the layout is Cluster, Cell type, Gene name, nCPM in most HPA releases; the header is
#: inspected rather than assumed because the column names have changed between versions.
with HPA.open(encoding="utf-8", errors="replace") as fh:
    head = fh.readline().rstrip("\n").split("\t")
print(f"  HPA columns: {head}")
idx = {name.lower(): i for i, name in enumerate(head)}


def col(*names: str) -> int | None:
    for n in names:
        if n.lower() in idx:
            return idx[n.lower()]
    return None


i_cell = col("Cell type", "Cell_type", "celltype")
i_gene = col("Gene name", "Gene", "gene")
i_cpm = col("nCPM", "nCPM ", "Expression", "TPM", "nTPM")
if i_cell is None or i_gene is None or i_cpm is None:
    raise SystemExit(f"could not identify the columns in {head}")

print(f"  using cell type column {i_cell}, gene column {i_gene}, value column {i_cpm}")

want = {g.upper() for g in HUBS + CONTROL}
cells: dict[str, dict[str, float]] = {}
n_rows = 0
with HPA.open(encoding="utf-8", errors="replace") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        if len(parts) <= max(i_cell, i_gene, i_cpm):
            continue
        n_rows += 1
        sym = parts[i_gene].strip().upper()
        if sym not in want:
            continue
        try:
            v = float(parts[i_cpm])
        except ValueError:
            continue
        cells.setdefault(parts[i_cell].strip(), {})[sym] = v

print(f"  rows scanned: {n_rows:,}   cell types seen: {len(cells)}")

print()
print("=" * 100)
print("1. The immune and retinal cell types present in the table")
print("=" * 100)
matched: dict[str, str] = {}
for label, pat in IMMUNE.items():
    hit = [c for c in cells if re.search(pat, c, re.I)]
    if hit:
        matched[label] = hit[0]
        print(f"  {label:30s} -> {hit[0]}")

print()
print("=" * 100)
print("2. Are the hub genes expressed in retinal microglia?")
print("=" * 100)
micro = matched.get("microglial cells")
if micro:
    vals = cells[micro]
    hubs_seen = [g for g in HUBS if vals.get(g, 0) > 1]
    ctrl_seen = [g for g in CONTROL if vals.get(g, 0) > 1]
    print(f"  cell type: {micro}   ({len(vals)} of the genes of interest measured)")
    print(f"  hub genes detected at nCPM > 1   : {len(hubs_seen)} of {len(HUBS)}")
    print(f"  control genes detected           : {len(ctrl_seen)} of {len(CONTROL)}")
    print()
    print("  the network hubs in microglia, by expression:")
    for g in sorted(HUBS, key=lambda x: -vals.get(x, 0)):
        v = vals.get(g)
        if v is None:
            continue
        tag = "  <- named in the manuscript as not detected in retina" if g == "TNF" else ""
        print(f"      {g:10s} {v:>9.1f} nCPM{tag}")

print()
print("=" * 100)
print("3. TNF specifically, since the manuscript reports it absent from retina")
print("=" * 100)
if "TNF" in {g for c in cells.values() for g in c}:
    per_cell = {c: v.get("TNF") for c, v in cells.items() if "TNF" in v}
    top = sorted(per_cell.items(), key=lambda x: -(x[1] or 0))[:10]
    print("  highest TNF expression across all cell types:")
    for c, v in top:
        print(f"      {v:>9.1f} nCPM   {c}")
    retinal = {c: v for c, v in per_cell.items() if re.search(r"retinal|m[üu]ller|photorecept", c, re.I)}
    print()
    print("  within retinal cell types:")
    for c, v in sorted(retinal.items(), key=lambda x: -(x[1] or 0)):
        print(f"      {v if v is not None else 0:>9.1f} nCPM   {c}")

(OUT / "immune_cell_expression.json").write_text(json.dumps(
    {"cells_matched": matched,
     "microglia": {g: cells.get(micro, {}).get(g) for g in HUBS} if micro else {},
     "tnf_by_cell": {c: v.get("TNF") for c, v in cells.items() if "TNF" in v},
     "source": "HPA rna_single_cell_type.tsv, already on disk"},
    indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  -> results/immune_cell_expression.json")
