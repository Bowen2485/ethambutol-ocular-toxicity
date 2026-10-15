# -*- coding: utf-8 -*-
"""
Inspect the cell-type labels, then test hub-gene expression in retinal cells.

The Human Protein Atlas single-cell table is in long form - one row per gene per cell
type - with 3.09 million rows and 248 distinct cell types across all tissues.  The
retinal clusters have to be identified from the labels rather than assumed, since the
naming does not follow an obvious pattern (`Rod photoreceptor cells` rather than
`retina_rod`).

Once the retinal clusters are known, two things are computed:

    expression   which of the 33 hub genes are detected in retinal ganglion cells and
                 Müller glia, the two cell types the mechanism implicates

    enrichment   whether that is more than expected.  The control is 10,000 random gene
                 sets of the same size drawn from the genes measured in the same
                 clusters, because any list of well-studied genes would be expressed
                 somewhere in retina and only the comparison makes it evidence.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "data" / "raw" / "hpa"
TSV = WORK / "rna_single_cell_type.tsv"

print("=" * 96)
print("1. Loading the expression table")
print("=" * 96)
expr = pd.read_csv(TSV, sep="\t")
expr.columns = [c.strip() for c in expr.columns]
print(f"  rows    : {len(expr):,}")
print(f"  columns : {list(expr.columns)}")

gene_col, cell_col, val_col = "Gene name", "Cell type", "nCPM"
expr[gene_col] = expr[gene_col].astype(str).str.strip().str.upper()
expr[cell_col] = expr[cell_col].astype(str).str.strip()

print()
print("=" * 96)
print("2. Cell types that belong to the retina")
print("=" * 96)
cells = sorted(expr[cell_col].unique())
print(f"  total distinct cell types: {len(cells)}")
KEY = ("retina", "ganglion", "muller", "müller", "photoreceptor", "rod",
       "cone", "bipolar", "amacrine", "horizontal")
retinal = [c for c in cells if any(k in c.lower() for k in KEY)]
print(f"  matching a retinal keyword: {len(retinal)}")
for c in retinal:
    n = int((expr[cell_col] == c).sum())
    print(f"      {c:44s} {n:>7,} genes measured")

if not retinal:
    print("  none matched; labels containing 'eye' or 'optic':")
    for c in cells:
        if any(k in c.lower() for k in ("eye", "optic", "ocular", "cornea")):
            print(f"      {c}")

print()
print("=" * 96)
print("3. Hub genes")
print("=" * 96)
hubs = pd.read_csv(ROOT / "results" / "mechanism_consensus_hubs.csv")
hub_genes = sorted({str(g).strip().upper() for g in hubs["gene"]})
print(f"  {len(hub_genes)} hubs: {hub_genes}")

if not retinal:
    raise SystemExit("no retinal clusters identified; stopping here")

sub = expr[expr[cell_col].isin(retinal)].copy()
print()
print("=" * 96)
print("4. Detection of hub genes in retinal cells")
print("=" * 96)
DETECT = 1.0        # nCPM above 1 counts as detected
det = sub[sub[gene_col].isin(hub_genes)]
wide = det.pivot_table(index=gene_col, columns=cell_col, values=val_col,
                       aggfunc="max")
wide = wide.reindex(hub_genes)
detected_any = (wide.fillna(0) > DETECT).any(axis=1)
print(f"  {'gene':10s} " + " ".join(f"{c[:16]:>16s}" for c in wide.columns[:6]))
for g in hub_genes:
    if g not in wide.index:
        print(f"  {g:10s} not measured in any retinal cluster")
        continue
    row = wide.loc[g]
    cells_hit = [c for c in wide.columns if pd.notna(row[c]) and row[c] > DETECT]
    best = row.max()
    print(f"  {g:10s} max nCPM {best:>8.1f}   detected in "
          f"{len(cells_hit)}/{len(wide.columns)} retinal clusters"
          + (f"   e.g. {cells_hit[0][:30]}" if cells_hit else ""))

n_detected = int(detected_any.sum())
print()
print(f"  hubs detected in at least one retinal cluster: {n_detected} "
      f"of {len(hub_genes)} "
      f"({100*n_detected/len(hub_genes):.0f}%)")

print()
print("=" * 96)
print("5. Is that more than chance?  10,000 random gene sets of the same size")
print("=" * 96)
universe = sorted(sub[gene_col].unique())
print(f"  genes measured in retinal clusters: {len(universe):,}")
presence = (sub.groupby(gene_col)[val_col].max() > DETECT)
universe_detected = set(presence[presence].index)
print(f"  of which detected (nCPM > {DETECT}): {len(universe_detected):,} "
      f"({100*len(universe_detected)/len(universe):.1f}%)")

measurable = [g for g in hub_genes if g in presence.index]
obs = sum(1 for g in measurable if bool(presence.get(g, False)))
print(f"  hubs measurable in this table: {len(measurable)}")
print(f"  hubs detected               : {obs}")
print(f"  expected if hubs were average genes: "
      f"{len(measurable)*len(universe_detected)/len(universe):.1f}")

rng = np.random.default_rng(20261015)
# np.random.Generator.choice with replace=False applies the restriction to the whole
# array, so for many independent draws the indices are generated directly instead.
n_meas = len(measurable)
flags = presence.reindex(universe).fillna(False).to_numpy().astype(np.int8)
n_univ = len(universe)
null = np.empty(10_000, dtype=int)
chunk = 500
for start in range(0, 10_000, chunk):
    stop = min(start + chunk, 10_000)
    idx = rng.random((stop - start, n_univ)).argpartition(n_meas, axis=1)[:, :n_meas]
    null[start:stop] = flags[idx].sum(axis=1)
p_ge = float((null >= obs).mean())
print()
print(f"  null distribution: mean {null.mean():.1f}, sd {null.std():.1f}, "
      f"range {null.min()}-{null.max()}")
print(f"  P(random set >= observed) = {p_ge:.4f}")
print(f"  fold enrichment           = "
      f"{obs/max(null.mean(), 1e-9):.2f}x")

out = ROOT / "results" / "hpa_retina_hub_expression.csv"
wide.to_csv(out, encoding="utf-8-sig")
print()
print(f"-> {out.relative_to(ROOT)}")
print()
print("=" * 96)
print("Reading")
print("=" * 96)
if p_ge < 0.05:
    print("""  The hubs are expressed in retinal cells more often than random gene sets of the
  same size, so the network is grounded in the tissue whose toxicity it is invoked to
  explain.  This answers the reviewer question rather than leaving it open.""")
else:
    print("""  The hubs are not expressed in retina more often than chance.  That is a negative
  result and it has to be reported: it means the network describes processes the drug
  perturbs in general rather than processes specific to the retina, and the mechanism
  section must say so.""")
