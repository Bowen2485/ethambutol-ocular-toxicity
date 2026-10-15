# -*- coding: utf-8 -*-
"""
Step 8 - Publication figures.

Every figure is written to both PDF (vector, for submission) and PNG (300 dpi,
for the manuscript file and for slides).

    Figure 1  FAERS case-selection flow diagram
    Figure 2  disproportionality volcano (ethambutol ocular terms)
    Figure 3  signal heat map, ethambutol vs comparator anti-TB drugs
    Figure 4  forest plot of the primary ocular signals
    Figure 5  PPI network of the focused mechanism tier
    Figure 6  enrichment dot plot (GO / KEGG / Reactome / WikiPathways)
    Figure 7  docking affinity heat map (ethambutol vs TCM actives)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
FIGS = ROOT / "figures"
DOCK = ROOT / "docking"
for p in (FIGS,):
    p.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 9, "axes.linewidth": 0.8, "axes.labelsize": 9.5,
    "axes.titlesize": 10, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "legend.fontsize": 8, "figure.dpi": 120, "savefig.bbox": "tight",
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "axes.unicode_minus": False,
})
PALETTE = {"ethambutol": "#B2182B", "isoniazid": "#2166AC",
           "rifampicin": "#4393C3", "pyrazinamide": "#92C5DE",
           "linezolid": "#D6604D", "streptomycin": "#F4A582"}


def save(fig, name: str) -> None:
    for ext in ("pdf", "png"):
        out = FIGS / f"{name}.{ext}"
        fig.savefig(out, dpi=300 if ext == "png" else None)
    plt.close(fig)
    print(f"[fig] {name}.pdf / .png")


def _dodge_overlaps(xs, ys, dx=0.0, dy=0.0):
    return xs, ys


# ----------------------------------------------------------------- Figure 1
def fig1_flow() -> None:
    manifest_path = DERIVED / "faers_manifest.json"
    dedup_path = RESULTS / "faers_dedup_summary.csv"
    n_total = n_dedup = n_drug = None
    if dedup_path.exists():
        d = pd.read_csv(dedup_path, encoding="utf-8-sig")
        allrow = d[d.drug == "FAERS_ALL"]
        eth = d[d.drug == "ethambutol"]
        if len(allrow):
            n_dedup = int(allrow.iloc[0].n_cases)
        if len(eth):
            n_drug = int(eth.iloc[0].n_cases)
    if manifest_path.exists() and n_dedup is None:
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        n_total = m.get("faers_total_reports")
        n_drug = m.get("index_reports_raw")

    n_quarters = len(list((ROOT / "data" / "raw" / "faers_ascii").glob("*.zip")))
    boxes = [
        ("FDA FAERS quarterly ASCII releases\n2004Q1-2026Q2 "
         f"({n_quarters} quarters)", "#EFF3FF"),
        (f"All submitted reports\nN = {n_dedup:,}" if n_dedup else
         "All submitted reports", "#DEEBF7"),
        ("Case-version de-duplication\nkeep latest FDA_DT per CASEID", "#C6DBEF"),
        (f"Reports naming ethambutol\nn = {n_drug:,}" if n_drug else
         "Reports naming ethambutol", "#FDDBC7"),
        ("Ocular MedDRA preferred terms\n(2x2 contingency table per term)", "#F4A582"),
        ("Signal metrics\nROR / PRR / IC025 / EBGM05", "#D6604D"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    ax.set_axis_off()
    y = 1.0
    step = 0.155
    for i, (txt, colour) in enumerate(boxes):
        box = FancyBboxPatch((0.18, y - 0.105), 0.64, 0.105,
                             boxstyle="round,pad=0.012,rounding_size=0.02",
                             linewidth=0.9, edgecolor="#333333", facecolor=colour)
        ax.add_patch(box)
        ax.text(0.5, y - 0.052, txt, ha="center", va="center", fontsize=8.6)
        if i < len(boxes) - 1:
            ax.add_patch(FancyArrowPatch((0.5, y - 0.108), (0.5, y - step + 0.052),
                                         arrowstyle="-|>", mutation_scale=12,
                                         linewidth=0.9, color="#333333"))
        y -= step
    ax.set_xlim(0, 1)
    ax.set_ylim(y + 0.02, 1.06)
    save(fig, "Figure1_flow")


# ----------------------------------------------------------------- Figure 2
def fig2_volcano() -> None:
    p = RESULTS / "faers_signals_ethambutol.csv"
    if not p.exists():
        print("[fig2] missing faers_signals_ethambutol.csv")
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    d = d[d.a > 0].copy()
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    sig = d[d.signal_strict]
    ns = d[~d.signal_strict]
    ax.scatter(np.log2(ns.ror.clip(lower=1e-3)), -np.log10(ns.q_bh.clip(lower=1e-12)),
               s=14, c="#BDBDBD", edgecolors="none", label="Not a signal")
    ax.scatter(np.log2(sig.ror.clip(lower=1e-3)), -np.log10(sig.q_bh.clip(lower=1e-12)),
               s=26, c="#B2182B", edgecolors="black", linewidths=0.4,
               label="Signal (ROR LCL>1, PRR≥2, IC025>0, FDR<0.05)")
    ax.axhline(-math.log10(0.05), color="#555555", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="#555555", linestyle="--", linewidth=0.8)
    # label the leading signals with vertical staggering so the text does not collide
    top = sig.nlargest(10, "ror").reset_index(drop=True)
    for i, r in top.iterrows():
        ax.annotate(str(r["term"]).title(),
                    (math.log2(max(r.ror, 1e-3)),
                     -math.log10(max(r.q_bh, 1e-12))),
                    fontsize=6.2, xytext=(6, 4 - 7 * (i % 5)),
                    textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", linewidth=0.4,
                                    color="#888888", shrinkA=0, shrinkB=2))
    ax.set_ylim(-0.8, 13.8)
    ax.set_xlabel("log$_2$ reporting odds ratio")
    ax.set_ylabel("$-\\log_{10}$ (Benjamini-Hochberg $q$)")
    ax.set_title("Ethambutol-associated ocular terms in FAERS")
    ax.legend(loc="lower right", frameon=False, fontsize=7.6)
    save(fig, "Figure2_volcano")


# ----------------------------------------------------------------- Figure 3
def fig3_heatmap() -> None:
    """
    Ocular reporting odds ratios for ethambutol, within the antitubercular class.

    The earlier version used the whole database as the denominator for every drug,
    which for antitubercular agents mostly contrasts tuberculosis patients with
    everyone else rather than comparing drugs with each other.  This version uses
    the within-class denominator produced by src/faers_withinclass.py, and adds the
    ethambutol rank on each term so the reader can see where the drug sits among
    its comparators rather than only its own ratio.
    """
    p = RESULTS / "faers_withinclass_signals.csv"
    if not p.exists():
        print("[fig3] missing faers_withinclass_signals.csv")
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    eth = d[(d.drug == "ethambutol") & (d.a >= 5)].copy()
    if eth.empty:
        print("[fig3] no ethambutol terms with a>=5")
        return
    eth = eth.sort_values("ror", ascending=False).head(18)
    terms = eth.term.tolist()

    # rank of ethambutol on each term within the class
    ranks = {}
    for t in terms:
        sub = d[d.term == t].sort_values("ror", ascending=False).reset_index(drop=True)
        hit = sub[sub.drug == "ethambutol"]
        ranks[t] = (int(hit.index[0]) + 1, len(sub)) if len(hit) else (None, len(sub))

    fig, axes = plt.subplots(1, 2, figsize=(11.6, 6.2),
                             gridspec_kw={"width_ratios": [1, 1.25]})
    # ---- left: ethambutol's own within-class ROR per term
    ax = axes[0]
    y = np.arange(len(terms))[::-1]
    colours = ["#08519C" if d[(d.drug == "ethambutol") &
                              (d.term == t)].iloc[0].signal else "#B0B0B0"
               for t in terms]
    vals = [float(eth[eth.term == t].iloc[0].ror) for t in terms]
    lcls = [float(eth[eth.term == t].iloc[0].ror_lcl) for t in terms]
    ucls = [float(eth[eth.term == t].iloc[0].ror_ucl) for t in terms]
    ax.barh(y, vals, color=colours, edgecolor="#333333", linewidth=0.4, height=0.68)
    ax.errorbar(vals, y, xerr=[np.array(vals) - np.array(lcls),
                               np.array(ucls) - np.array(vals)],
                fmt="none", ecolor="#333333", elinewidth=0.8, capsize=1.8)
    ax.axvline(1, color="#888888", linestyle="--", linewidth=0.8)
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels([t.title() for t in terms], fontsize=7.6)
    ax.set_xlabel("ROR within the antitubercular class (log scale)")
    ax.set_title("(A) Ethambutol, within-class ROR", fontsize=10)
    for yi, t in zip(y, terms):
        rk = ranks[t][0]
        if rk:
            ax.text(max(ucls[terms.index(t)], 1.2), yi, f"rank {rk}/{ranks[t][1]}",
                    va="center", fontsize=6.2, color="#555555")

    # ---- right: term-by-drug grid
    ax2 = axes[1]
    drugs = (d[d.term.isin(terms)].groupby("drug")
             .apply(lambda g: g[g.term == "OPTIC NEUROPATHY"].ror.iloc[0]
                    if (g.term == "OPTIC NEUROPATHY").any() else np.nan,
                    include_groups=False)
             .sort_values(ascending=False))
    mat = (d[d.term.isin(terms)].pivot_table(index="drug", columns="term",
                                             values="ror", aggfunc="max")
           .reindex(index=drugs.index, columns=terms))
    im = ax2.imshow(np.log2(mat.fillna(1).clip(lower=0.05)).values,
                    cmap="RdBu_r", aspect="auto", vmin=-2.5, vmax=3.5)
    ax2.set_xticks(range(len(terms)))
    ax2.set_xticklabels([t.title() for t in terms], rotation=40, ha="right",
                        fontsize=6.6)
    ax2.set_yticks(range(mat.shape[0]))
    ax2.set_yticklabels([str(i).title() for i in mat.index], fontsize=7)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.values[i, j]
            if np.isfinite(v):
                # label with the ROR itself, not the log2 value that is plotted, so
                # the printed numbers match what a reader would quote
                ax2.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=5.2,
                         color="black" if abs(math.log2(max(v, 0.05))) < 2.2
                         else "white")
    ax2.set_title("(B) All antitubercular drugs, same terms", fontsize=10)
    cb = fig.colorbar(im, ax=ax2, fraction=0.035, pad=0.02)
    cb.set_label("log$_2$ ROR")
    fig.suptitle("Ocular reporting odds ratios within the antitubercular class",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, "Figure3_heatmap")


# ----------------------------------------------------------------- Figure 4
def fig4_forest() -> None:
    p = RESULTS / "faers_signals_ethambutol.csv"
    if not p.exists():
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    d = d[(d.a >= 3) & d.signal_ror].nlargest(18, "ror").sort_values("ror")
    if d.empty:
        print("[fig4] no signals to plot")
        return
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    y = np.arange(len(d))
    ax.errorbar(d.ror, y,
                xerr=[d.ror - d.ror_lcl, d.ror_ucl - d.ror],
                fmt="o", ms=4, lw=0.9, color="#B2182B", ecolor="#666666",
                capsize=2)
    ax.axvline(1, color="#333333", linestyle="--", linewidth=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{t.title()} (n={int(a)})"
                        for t, a in zip(d.term, d.a)], fontsize=7.4)
    ax.set_xscale("log")
    ax.set_xlabel("Reporting odds ratio (95% CI)")
    ax.set_title("Ocular disproportionality signals for ethambutol")
    save(fig, "Figure4_forest")


# ----------------------------------------------------------------- Figure 5
def fig5_network() -> None:
    hub_p = RESULTS / "mechanism_hub_A_focused.csv"
    net_p = DERIVED / "string_network_A_focused_400.tsv"
    if not hub_p.exists() or not net_p.exists():
        print("[fig5] missing network inputs")
        return
    import networkx as nx
    hub = pd.read_csv(hub_p, encoding="utf-8-sig")
    edges = pd.read_csv(net_p, sep="\t")
    G = nx.Graph()
    for _, e in edges.iterrows():
        a, b = e.get("preferredName_A"), e.get("preferredName_B")
        if a and b:
            G.add_edge(a, b, weight=float(e.get("score", 0.4)))
    if G.number_of_nodes() == 0:
        return
    core = set(hub[hub.in_core_panel == True].gene) if "in_core_panel" in hub else set()
    lit = set(hub[hub.n_lit_papers > 0].gene) if "n_lit_papers" in hub else set()
    deg = dict(G.degree())
    pos = nx.spring_layout(G, seed=11, k=0.55 / math.sqrt(max(G.number_of_nodes(), 2)),
                           iterations=260)
    fig, ax = plt.subplots(figsize=(7.4, 6.6))
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.25, width=0.5,
                           edge_color="#888888")
    sizes = [40 + 22 * deg.get(n, 1) for n in G.nodes()]
    colours = ["#B2182B" if n in core else ("#F4A582" if n in lit else "#9ECAE1")
               for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=sizes, node_color=colours,
                           edgecolors="black", linewidths=0.4)
    top = sorted(G.nodes(), key=lambda n: -deg.get(n, 0))[:26]
    nx.draw_networkx_labels(G, pos, ax=ax, labels={n: n for n in top}, font_size=6.8)
    ax.set_axis_off()
    ax.set_title("STRING PPI network, focused mechanism tier\n"
                 "red = curated core panel, orange = literature-supported, "
                 "blue = optic-nerve phenotype genes")
    save(fig, "Figure5_network")


# ----------------------------------------------------------------- Figure 6
def fig6_enrichment() -> None:
    p = RESULTS / "mechanism_enrichment_A_focused.csv"
    if not p.exists():
        print("[fig6] missing enrichment file")
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    d = d[(d.significant == True) & d.source.isin(  # noqa: E712
        ["GO:BP", "GO:CC", "GO:MF", "KEGG", "REAC", "WP"])]
    if d.empty:
        return
    keep = []
    for src, g in d.groupby("source"):
        keep.append(g.nsmallest(8, "p_value"))
    d = pd.concat(keep).drop_duplicates("term_id").sort_values("p_value").head(34)
    d["logq"] = -np.log10(d.p_value.clip(lower=1e-30))
    src_order = ["GO:BP", "GO:CC", "GO:MF", "KEGG", "REAC", "WP"]
    src_colour = dict(zip(src_order, ["#B2182B", "#EF8A62", "#FDDBC7",
                                      "#2166AC", "#67A9CF", "#92C5DE"]))
    d = d.sort_values("logq")
    fig, ax = plt.subplots(figsize=(7.6, 8.0))
    y = np.arange(len(d))
    ax.scatter(d.logq, y, s=18 + 8 * d.intersection_size,
               c=[src_colour.get(s, "#999999") for s in d.source],
               edgecolors="black", linewidths=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{t[:64]}" for t in d.term_name], fontsize=6.9)
    ax.set_xlabel("$-\\log_{10}$ (FDR-adjusted $P$)")
    ax.set_title("Functional enrichment of the focused mechanism panel")
    handles = [plt.Line2D([], [], marker="o", linestyle="none", markersize=6,
                          markerfacecolor=src_colour[s], markeredgecolor="black",
                          label=s) for s in src_order if s in set(d.source)]
    ax.legend(handles=handles, loc="lower right", frameon=False, title="Source")
    save(fig, "Figure6_enrichment")


# ----------------------------------------------------------------- Figure 7
def fig7_docking() -> None:
    """
    Docking of ethambutol against the hub panel.

    The earlier version was a ligand-by-target heat map that included a
    phytochemical panel; with that panel removed the figure becomes a ranked bar
    chart of the ethambutol-only results, which is what the mechanism section now
    needs: the ordering of targets by predicted occupancy.
    """
    p = DOCK / "results.csv"
    if not p.exists():
        print("[fig7] missing docking results")
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    d = d[(d.ligand == "ethambutol") & (d.ok == True)]  # noqa: E712
    if d.empty:
        print("[fig7] no ethambutol docking runs")
        return
    d = d[["gene", "best_affinity", "resolution", "box_source"]].copy()
    d["is_experimental"] = d.resolution.notna()
    d = d.sort_values("best_affinity")

    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    y = np.arange(len(d))
    colours = ["#08519C" if e else "#9ECAE1" for e in d.is_experimental]
    ax.barh(y, d.best_affinity, color=colours, edgecolor="#333333", linewidth=0.5,
            height=0.68)
    ax.set_yticks(y)
    ax.set_yticklabels(d.gene, fontsize=8.6)
    ax.set_xlabel("AutoDock Vina score (kcal/mol)")
    ax.set_title("Docking of ethambutol against the hub targets\n"
                 "dark = experimental human structure, light = AlphaFold model")
    ax.axvline(0, color="#333333", linewidth=0.6)
    ax.set_xlim(min(d.best_affinity) - 1.1, 0.35)
    # the axis is inverted (0 at the right), so labels sit to the LEFT of each bar
    for yi, v in zip(y, d.best_affinity):
        ax.text(v - 0.10, yi, f"{v:.2f}", va="center", ha="right", fontsize=7.4,
                color="#333333")
    save(fig, "Figure7_docking")


def fig8_tto() -> None:
    """Time from ethambutol start to the reported event, by event class."""
    p = DERIVED / "faers_tto_cases.csv"
    if not p.exists():
        print("[fig8] missing faers_tto_cases.csv")
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    d = d[d.tto_days.notna()]
    if d.empty:
        return
    optic = d[d.any_optic == 1].tto_days.values
    ocular = d[(d.any_ocular == 1) & (d.any_optic == 0)].tto_days.values
    other = d[d.any_ocular == 0].tto_days.values

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0),
                             gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axes[0]
    bins = np.logspace(0, np.log10(3300), 34)
    for arr, lab, col in ((other, f"Non-ocular (n={len(other)})", "#9ECAE1"),
                          (ocular, f"Ocular (n={len(ocular)})", "#F4A582"),
                          (optic, f"Optic nerve (n={len(optic)})", "#B2182B")):
        if len(arr) == 0:
            continue
        w = np.ones_like(arr, dtype=float) / len(arr)
        ax.hist(np.clip(arr, 1, None), bins=bins, weights=w, alpha=0.62,
                label=lab, color=col, edgecolor="white", linewidth=0.3)
    ax.set_xscale("log")
    ax.set_xlabel("Days from ethambutol start to reported event (log scale)")
    ax.set_ylabel("Proportion of cases")
    ax.set_title("Time to onset")
    ax.legend(frameon=False, fontsize=7.4)
    if len(optic):
        ax.axvline(np.median(optic), color="#B2182B", linestyle=":", linewidth=1.0)

    ax2 = axes[1]
    pairs = [(other, "Non-\nocular", "#9ECAE1"), (ocular, "Ocular", "#F4A582"),
             (optic, "Optic\nnerve", "#B2182B")]
    data = [np.clip(a, 1, None) for a, _, _ in pairs if len(a)]
    labels = [l for a, l, _ in pairs if len(a)]
    cols = [c for a, _, c in pairs if len(a)]
    bp = ax2.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55,
                     medianprops=dict(color="black", linewidth=1.1),
                     flierprops=dict(marker=".", markersize=2, alpha=0.4))
    for patch, col in zip(bp["boxes"], cols):
        patch.set_facecolor(col)
        patch.set_alpha(0.75)
    ax2.set_yscale("log")
    ax2.set_ylabel("Days to onset (log scale)")
    ax2.set_title("Median time to onset")
    for i, a in enumerate(data, 1):
        ax2.text(i, float(np.median(a)), f" {np.median(a):.0f} d", fontsize=7,
                 va="bottom", ha="left")
    save(fig, "Figure8_tto")


def fig9_trend() -> None:
    """Annual ethambutol reporting volume and the ocular share."""
    p = RESULTS / "faers_trend.csv"
    if not p.exists():
        print("[fig9] missing faers_trend.csv")
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    d = d[d.year >= 2013]          # before 2013 the annual counts are negligible
    if d.empty:
        return
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.bar(d.year, d.n_reports, color="#CFD8DC", edgecolor="#90A4AE",
           linewidth=0.4, label="All ethambutol reports")
    ax.bar(d.year, d.n_optic, color="#B2182B", edgecolor="none",
           label="With an optic-nerve term")
    ax.set_xlabel("Report year")
    ax.set_ylabel("Number of FAERS reports")
    ax.set_title("Ethambutol ocular reporting over time")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax2 = ax.twinx()
    ax2.plot(d.year, d.pct_optic, color="#0B5394", marker="o", markersize=3.4,
             linewidth=1.1, label="Optic-nerve share (%)")
    ax2.set_ylabel("Share of reports (%)", color="#0B5394")
    ax2.tick_params(axis="y", colors="#0B5394")
    ax2.set_ylim(0, max(8.0, float(d.pct_optic.max()) * 1.35))
    ax2.legend(frameon=False, fontsize=8, loc="upper center")
    save(fig, "Figure9_trend")


def main() -> int:
    which = sys.argv[1:] or ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    todo = {"1": fig1_flow, "2": fig2_volcano, "3": fig3_heatmap, "4": fig4_forest,
            "5": fig5_network, "6": fig6_enrichment, "7": fig7_docking,
            "8": fig8_tto, "9": fig9_trend}
    for k in which:
        fn = todo.get(k)
        if not fn:
            continue
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            print(f"[fig{k}] FAILED {type(exc).__name__}: {str(exc)[:160]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
