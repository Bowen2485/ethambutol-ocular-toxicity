# -*- coding: utf-8 -*-
"""Produce the consolidated figure set: six main figures and two supplementary ones.

Why this exists
    The paper carried ten main figures, which is over what most journals allow.  Two
    pairs draw the same thing twice and two others carry a single sentence each, so the
    set is consolidated rather than trimmed:

        main   Figure 1  flow                       (unchanged)
               Figure 2  disproportionality          <- old Figure 2 (volcano) + Figure 4 (forest)
               Figure 3  network                     <- old Figure 5
               Figure 4  enrichment                  <- old Figure 6
               Figure 5  docking                     <- old Figure 7
               Figure 6  temporal                    <- old Figure 8 (time to onset) + Figure 9 (trend)
        supp   Figure S1 heatmap                     <- old Figure 3
               Figure S2 Venn overlap                <- old Figure 10

    The panels that are only renumbered are copied rather than redrawn: matplotlib
    output is not guaranteed to be byte-identical across runs, so redrawing a figure
    that already exists would replace a reviewed artefact for no reason.  Only the two
    composites are drawn here.

    Superseded files are moved to archive/figures_superseded/ rather than deleted, and
    the move matters for correctness rather than tidiness: the builders pick the figure
    file by matching "Figure<n>_*" against the caption, so leaving Figure2_volcano.pdf
    beside Figure2_disproportionality.pdf would make the choice ambiguous.
"""
from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import make_figures as mf  # noqa: E402  (applies the shared rcParams on import)

FIGS = mf.FIGS
RESULTS = mf.RESULTS
DERIVED = mf.DERIVED
ARCHIVE = ROOT / "archive" / "figures_superseded"

#: same stem -> same stem, new name (both .pdf and .png are copied)
RENAMES = {
    "Figure5_network": "Figure3_network",
    "Figure6_enrichment": "Figure4_enrichment",
    "Figure7_docking": "Figure5_docking",
    "Figure3_heatmap": "FigureS1_heatmap",
    "Figure10_venn_hubs_ocular": "FigureS2_venn",
}
SUPERSEDED = ("Figure2_volcano", "Figure4_forest", "Figure8_tto", "Figure9_trend")
EXTS = ("pdf", "png")


def rename_unchanged() -> None:
    """Copy the renumbered panels under their new names."""
    for old, new in RENAMES.items():
        for ext in EXTS:
            src, dst = FIGS / f"{old}.{ext}", FIGS / f"{new}.{ext}"
            if not src.exists():
                print(f"  [rename] MISSING {src.name}")
                continue
            shutil.copy2(src, dst)
            print(f"  [rename] {src.name} -> {dst.name}")


def archive_superseded() -> None:
    """Move the files the new set replaces out of figures/."""
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for stem in SUPERSEDED + tuple(RENAMES):
        for ext in EXTS:
            src = FIGS / f"{stem}.{ext}"
            if src.exists():
                shutil.move(str(src), str(ARCHIVE / src.name))
                print(f"  [archive] {src.name}")


def figure2_disproportionality() -> None:
    """Volcano and forest side by side, because they plot the same estimates."""
    p = RESULTS / "faers_signals_ethambutol.csv"
    if not p.exists():
        print("[fig2] missing faers_signals_ethambutol.csv")
        return
    d = pd.read_csv(p, encoding="utf-8-sig")

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 10.6))
    fig.subplots_adjust(hspace=0.34, top=0.94, bottom=0.06, left=0.13, right=0.97)

    # ---- panel A: volcano (the panel code of the original Figure 2)
    ax = axes[0]
    v = d[d.a > 0].copy()
    sig, ns = v[v.signal_strict], v[~v.signal_strict]
    ax.scatter(np.log2(ns.ror.clip(lower=1e-3)), -np.log10(ns.q_bh.clip(lower=1e-12)),
               s=13, c="#BDBDBD", edgecolors="none", label="Not a signal")
    ax.scatter(np.log2(sig.ror.clip(lower=1e-3)), -np.log10(sig.q_bh.clip(lower=1e-12)),
               s=24, c="#B2182B", edgecolors="black", linewidths=0.4,
               label="Signal (ROR LCL>1, PRR\u22652, IC025>0, FDR<0.05)")
    ax.axhline(-math.log10(0.05), color="#555555", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="#555555", linestyle="--", linewidth=0.8)
    # The leading signals all sit at the q clamp, so offsetting each label from its own
    # point piles them on top of one another.  They go in a column in the right margin
    # instead, which cannot collide and is joined to its point by a leader line.
    top = sig.nlargest(10, "ror").reset_index(drop=True)
    x_hi = float(np.log2(max(sig.ror.max(), 1.0)))
    ax.set_xlim(-5.4, x_hi + 5.6)
    for i, r in top.iterrows():
        ax.annotate(str(r["term"]).title(),
                    (math.log2(max(r.ror, 1e-3)), -math.log10(max(r.q_bh, 1e-12))),
                    xytext=(x_hi + 1.0, 13.0 - 0.62 * i),
                    fontsize=6.0, va="center", ha="left",
                    arrowprops=dict(arrowstyle="-", linewidth=0.35, color="#999999",
                                    shrinkA=0, shrinkB=2))
    ax.set_ylim(-0.8, 13.8)
    ax.set_xlabel("log$_2$ reporting odds ratio")
    ax.set_ylabel("$-\\log_{10}$ (Benjamini-Hochberg $q$)")
    ax.set_title("A  Ethambutol-associated ocular terms in FAERS", loc="left")
    ax.legend(loc="lower right", frameon=False, fontsize=7.6)

    # ---- panel B: forest (the panel code of the original Figure 4)
    ax2 = axes[1]
    f = d[(d.a >= 3) & d.signal_ror].nlargest(18, "ror").sort_values("ror")
    if not f.empty:
        y = np.arange(len(f))
        ax2.errorbar(f.ror, y, xerr=[f.ror - f.ror_lcl, f.ror_ucl - f.ror],
                     fmt="o", ms=4, lw=0.9, color="#B2182B", ecolor="#666666", capsize=2)
        ax2.axvline(1, color="#333333", linestyle="--", linewidth=0.9)
        ax2.set_yticks(y)
        ax2.set_yticklabels([f"{t.title()} (n={int(a)})"
                             for t, a in zip(f.term, f.a)], fontsize=7.4)
        ax2.set_xscale("log")
        ax2.set_xlabel("Reporting odds ratio (95% CI)")
    ax2.set_title("B  Ocular disproportionality signals for ethambutol", loc="left")

    mf.save(fig, "Figure2_disproportionality")


def figure6_temporal() -> None:
    """Time to onset and the annual trend, which are both time-axis descriptions."""
    tto_p = DERIVED / "faers_tto_cases.csv"
    trend_p = RESULTS / "faers_trend.csv"
    if not tto_p.exists() or not trend_p.exists():
        print(f"[fig6] missing input ({tto_p.name} / {trend_p.name})")
        return

    d = pd.read_csv(tto_p, encoding="utf-8-sig")
    d = d[d.tto_days.notna()]
    optic = d[d.any_optic == 1].tto_days.values
    ocular = d[(d.any_ocular == 1) & (d.any_optic == 0)].tto_days.values
    other = d[d.any_ocular == 0].tto_days.values

    t = pd.read_csv(trend_p, encoding="utf-8-sig")
    t = t[t.year >= 2013]

    fig = plt.figure(figsize=(9.8, 8.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.82], hspace=0.40, wspace=0.26)
    fig.subplots_adjust(top=0.94, bottom=0.07, left=0.09, right=0.91)

    # ---- panel A: distribution (the left panel of the original Figure 8)
    ax = fig.add_subplot(gs[0, 0])
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
    ax.set_title("A  Time to onset", loc="left")
    ax.legend(frameon=False, fontsize=7.4)
    if len(optic):
        ax.axvline(np.median(optic), color="#B2182B", linestyle=":", linewidth=1.0)

    # ---- panel B: medians (the right panel of the original Figure 8)
    ax2 = fig.add_subplot(gs[0, 1])
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
    ax2.set_title("B  Median time to onset", loc="left")
    for i, a in enumerate(data, 1):
        ax2.text(i, float(np.median(a)), f" {np.median(a):.0f} d", fontsize=7,
                 va="bottom", ha="left")

    # ---- panel C: annual trend (the original Figure 9)
    ax3 = fig.add_subplot(gs[1, :])
    ax3.bar(t.year, t.n_reports, color="#CFD8DC", edgecolor="#90A4AE",
            linewidth=0.4, label="All ethambutol reports")
    ax3.bar(t.year, t.n_optic, color="#B2182B", edgecolor="none",
            label="With an optic-nerve term")
    ax3.set_xlabel("Report year")
    ax3.set_ylabel("Number of FAERS reports")
    ax3.set_title("C  Ethambutol ocular reporting over time", loc="left")
    ax3.legend(frameon=False, fontsize=8, loc="upper left")
    ax3b = ax3.twinx()
    ax3b.plot(t.year, t.pct_optic, color="#0B5394", marker="o", markersize=3.4,
              linewidth=1.1, label="Optic-nerve share (%)")
    ax3b.set_ylabel("Share of reports (%)", color="#0B5394")
    ax3b.tick_params(axis="y", colors="#0B5394")
    ax3b.set_ylim(0, max(8.0, float(t.pct_optic.max()) * 1.35))
    ax3b.legend(frameon=False, fontsize=8, loc="upper center")

    mf.save(fig, "Figure6_temporal")


def main() -> int:
    print("Consolidating the figure set")
    print("\n1. merged composites")
    figure2_disproportionality()
    figure6_temporal()
    print("\n2. renumbered panels (copied, not redrawn)")
    rename_unchanged()
    print("\n3. superseded files moved out of figures/")
    archive_superseded()

    print("\nMain figures now in figures/:")
    for p in sorted(FIGS.glob("Figure[0-9]*.pdf")):
        print(f"  {p.name}")
    print("Supplementary figures:")
    for p in sorted(FIGS.glob("FigureS*.pdf")):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
