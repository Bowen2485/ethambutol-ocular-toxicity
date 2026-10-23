# -*- coding: utf-8 -*-
"""Figures for the restructured (Therapeutic Advances in Drug Safety) manuscript.

Every value is read from results/main_results.json, so a figure cannot disagree with the text.

    Figure 1  three independent data sources and the FAERS case flow
    Figure 2  the eleven ocular queries, ROR and 95% CI
    Figure 3  preferred terms inside the optic-nerve query and the pre-specified controls
    Figure 4  sensitivity: exposure role and reporting period

Figure 1 draws the three systems as separate modules.  Earlier versions put JADER and Canada
Vigilance beside the FAERS flow with dashed arrows, which read as if they were branches of that
flow; they are independent databases analysed separately.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import FixedLocator, NullFormatter, ScalarFormatter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
FIG = ROOT / "figures"
OUT = ROOT / "results" / "tads_figures"
OUT.mkdir(parents=True, exist_ok=True)

d = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
can = json.loads((RES / "canada_vigilance_ethambutol.json").read_text(encoding="utf-8"))
plt.rcParams.update({
    "font.size": 9.5, "axes.linewidth": 0.8, "axes.labelsize": 10, "axes.titlesize": 10.5,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9,
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "axes.unicode_minus": False, "savefig.bbox": "tight",
})


def save(fig, name: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=300)
    plt.close(fig)
    print(f"  {name}.pdf / .png")


def forest(rows, title, xlabel, name, xlim=None, figsize=(6.6, 4.4), tick_labelsize=9.5,
           value_size=8.5):
    """rows: (label, est, lo, hi, n) drawn on a log axis, reference line at 1."""
    fig, ax = plt.subplots(figsize=figsize)
    ys = np.arange(len(rows))[::-1]
    for y, (label, est, lo, hi, n) in zip(ys, rows):
        colour = "#B2182B" if lo > 1 else ("#4393C3" if hi < 1 else "#777777")
        ax.plot([lo, hi], [y, y], color=colour, lw=1.5, solid_capstyle="butt")
        ax.plot(est, y, "o", color=colour, ms=6)
        ax.text(1.02, y, f"{est:.2f}", transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=value_size)
        ax.text(1.20, y, f"{int(n):,}", transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=value_size, color="#444444")
    ax.axvline(1, color="#444444", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=tick_labelsize)
    ax.set_ylim(-0.85, len(rows) - 0.15)
    if xlim:
        ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontsize=10)
    ax.text(1.02, len(rows) - 0.62, "ROR", transform=ax.get_yaxis_transform(),
            fontsize=value_size, ha="left", color="#444444", weight="bold")
    ax.text(1.20, len(rows) - 0.62, "cases", transform=ax.get_yaxis_transform(),
            fontsize=value_size, ha="left", color="#444444", weight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, name)


# ------------------------------------------------------------------ Figure 1
def figure1() -> None:
    flow = d["case_flow"]
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    ax.set_axis_off()

    def box(x, y, w, h, text, colour, size=9.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.012,rounding_size=0.02",
                                    linewidth=0.9, edgecolor="#333333", facecolor=colour))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size)

    def arrow(x, y0, y1):
        ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>", mutation_scale=12,
                                     lw=1.0, color="#333333"))

    # ---- FAERS: the only module with a flow
    ax.text(0.03, 0.97, "A  FAERS (primary analysis)", fontsize=10.5, weight="bold",
            ha="left", va="top", color="#08519C")
    x, w = 0.03, 0.46
    box(x, 0.84, w, 0.09,
        f"Quarterly ASCII releases 2004Q1-2026Q2 (90 quarters)\n"
        f"submitted reports: {flow['submitted_reports']:,}", "#EFF3FF")
    box(0.55, 0.84, 0.42, 0.09,
        f"Duplicate records removed: {flow['submitted_reports'] - flow['de_duplicated_cases']:,}\n"
        f"keep latest FDA_DT per CASEID", "#F7F7F7", size=8.6)
    arrow(x + w / 2, 0.83, 0.76)
    ax.add_patch(FancyArrowPatch((x + w, 0.885), (0.55, 0.885), arrowstyle="-|>",
                                 mutation_scale=10, lw=0.9, color="#777777"))
    box(x, 0.65, w, 0.10, f"De-duplicated cases\n{flow['de_duplicated_cases']:,}", "#9ECAE1")
    arrow(x + w / 2, 0.64, 0.57)
    box(x, 0.45, w, 0.11,
        f"Cases naming ethambutol: {flow['ethambutol_any_role']:,}\n"
        f"suspect (PS/SS) {flow['ethambutol_suspect_ps_ss']:,}  ·  "
        f"concomitant only {flow['ethambutol_concomitant_only']:,}", "#FDDBC7")
    arrow(x + w / 2, 0.44, 0.36)
    box(x, 0.24, w, 0.11,
        "Eleven ocular MedDRA 29.0 queries (narrow sets)\n"
        "2x2 table per query; optic-nerve terms by PT", "#F4A582", size=8.3)
    ax.text(x, 0.19, "Main analysis: any drug role.  Sensitivity: suspect only.", fontsize=8.4,
            ha="left", va="top", color="#333333")

    # ---- JADER: independent database
    ax.plot([0.52, 0.52], [0.06, 0.60], color="#BBBBBB", lw=0.8, ls=(0, (3, 3)))
    ax.text(0.55, 0.58, "Independent database — separate analysis", fontsize=8.6,
            ha="left", va="top", color="#555555", style="italic")
    box(0.55, 0.36, 0.42, 0.18,
        "B  JADER (external, term level)\n"
        "September 2026 release: 1,054,239 cases\n"
        "ethambutol: 3,483 (1,798 as suspect)\n"
        "exposure from the suspect-drug code\n"
        "optic-nerve terms mapped to MedDRA/J", "#E5F5E0", size=8.7)

    # ---- Canada: independent database
    ax.plot([0.52, 0.52], [0.06, 0.30], color="#BBBBBB", lw=0.8, ls=(0, (3, 3)))
    box(0.55, 0.06, 0.42, 0.18,
        "C  Canada Vigilance (external, exploratory)\n"
        f"31 May 2026 extract: {can['N_reports']:,} reports\n"
        f"ethambutol: {can['n_ethambutol_any']:,} "
        f"({can['n_ethambutol_suspect']:,} as suspect)\n"
        "exposure from the ingredient table\n"
        "outcome: any preferred term containing OPTIC", "#E5F5E0", size=8.7)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save(fig, "Figure1_flow")


# ------------------------------------------------------------------ Figure 2
def figure2() -> None:
    rows = []
    for r in sorted(d["smq"], key=lambda x: x["ror"]):
        rows.append((r["smq"], r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"]))
    forest(rows, "Eleven ocular MedDRA queries, ethambutol vs all other reports",
           "Reporting odds ratio (log scale, 95% CI)", "Figure2_smq_forest",
           xlim=(0.1, 40), figsize=(7.4, 6.4), tick_labelsize=10.5, value_size=9.5)


# ------------------------------------------------------------------ Figure 3
def figure3() -> None:
    pts = [r for r in d["pt"] if r["group"] == "optic nerve" and r["a"] >= 3]
    ctl = [r for r in d["pt"] if r["group"] == "control"]
    pts.sort(key=lambda r: -r["ror"])
    ctl.sort(key=lambda r: -r["ror"])
    rows = [(r["term"].capitalize(), r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"]) for r in pts]
    negative = {"Cataract", "Dry eye", "Glaucoma", "Conjunctivitis"}
    rows += [(r["term"].capitalize()
              + (" (negative control)" if r["term"] in negative else " (non-specific comparator)"),
              r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"]) for r in ctl]
    forest(rows, "Optic-nerve preferred terms (top); pre-specified negative controls and "
                 "non-specific comparators (bottom)",
           "Reporting odds ratio (log scale, 95% CI)", "Figure3_pt_forest",
           xlim=(0.05, 400), figsize=(7.6, 9.2), tick_labelsize=10.5, value_size=9.5)


# ------------------------------------------------------------------ Figure 4
def suspect_ci(a: int, n_event: int, n_drug: int) -> tuple[float, float, float]:
    """ROR and Woolf CI for the suspect-only cohort, from the stored cells."""
    import math
    N = d["N"]
    n_eth_ps = d["n_ethambutol_suspect"]
    b, c, dd = n_eth_ps - a, n_event - a, N - n_eth_ps - n_event + a
    est = (a * dd) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / dd)
    return est, math.exp(math.log(est) - 1.959964 * se), math.exp(math.log(est) + 1.959964 * se)


def figure4() -> None:
    on = next(r for r in d["pt"] if r["term"] == "Optic neuropathy")
    smq = next(r for r in d["smq"] if r["smq"].startswith("Optic nerve"))
    t1, t2 = d["temporal"]["2004-2016"], d["temporal"]["2017-2026"]
    on_ps = suspect_ci(on["a_suspect"], on["n_event"], d["n_ethambutol_suspect"])
    smq_ps = suspect_ci(smq["a_suspect"], smq["n_event"], d["n_ethambutol_suspect"])

    #: a blank row separates the exposure-role block from the period block, so the two questions
    #: are not read as one series
    rows = [
        ("Term, all roles (main)", on["ror"], on["ror_lcl"], on["ror_ucl"], on["a"]),
        ("Term, suspect only", on_ps[0], on_ps[1], on_ps[2], on["a_suspect"]),
        ("Query, all roles (main)", smq["ror"], smq["ror_lcl"], smq["ror_ucl"], smq["a"]),
        ("Query, suspect only", smq_ps[0], smq_ps[1], smq_ps[2], smq["a_suspect"]),
        None,
        ("Term, 2004-2016", t1["ror"], t1["ror_lcl"], t1["ror_ucl"], t1["a"]),
        ("Term, 2017-2026", t2["ror"], t2["ror_lcl"], t2["ror_ucl"], t2["a"]),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ys, labels = [], []
    y = len(rows) - 1
    for row in rows:
        if row is None:
            y -= 1
            continue
        ys.append(y)
        labels.append(row[0])
        colour = "#B2182B"
        ax.plot([row[2], row[3]], [y, y], color=colour, lw=1.5, solid_capstyle="butt")
        ax.plot(row[1], y, "o", color=colour, ms=6)
        ax.text(1.02, y, f"{row[1]:.2f}", transform=ax.get_yaxis_transform(), va="center",
                fontsize=9)
        ax.text(1.18, y, f"{int(row[4]):,}", transform=ax.get_yaxis_transform(), va="center",
                fontsize=9, color="#444444")
        y -= 1

    ax.axvline(1, color="#444444", ls="--", lw=0.8)
    ax.set_xscale("log")
    ticks = [20, 50, 100, 200, 500]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_ylim(-0.9, len(rows) - 0.1)
    ax.set_xlim(20, 900)
    ax.set_xlabel("Reporting odds ratio for the optic-nerve outcome (log scale, 95% CI)")
    ax.set_title("Sensitivity: exposure role and reporting period", loc="left", fontsize=10)
    ax.text(1.02, len(rows) - 0.75, "ROR", transform=ax.get_yaxis_transform(), fontsize=9,
            weight="bold", color="#444444")
    ax.text(1.18, len(rows) - 0.75, "cases", transform=ax.get_yaxis_transform(), fontsize=9,
            weight="bold", color="#444444")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "Figure4_sensitivity")


figure1()
figure2()
figure3()
figure4()
print(f"\nwritten to {OUT.relative_to(ROOT)}")
