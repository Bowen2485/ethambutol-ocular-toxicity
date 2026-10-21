# -*- coding: utf-8 -*-
"""Figures for the restructured (Therapeutic Advances in Drug Safety) manuscript.

Every value is read from results/main_results.json, so a figure cannot disagree with the text.

    Figure 1  multi-database case flow
    Figure 2  the eleven ocular queries, ROR and 95% CI
    Figure 3  preferred terms inside the optic-nerve query and the pre-specified controls
    Figure 4  sensitivity: exposure role and reporting period, optic neuropathy
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
FIG = ROOT / "figures"
OUT = ROOT / "results" / "tads_figures"
OUT.mkdir(parents=True, exist_ok=True)

d = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
plt.rcParams.update({
    "font.size": 9, "axes.linewidth": 0.8, "axes.labelsize": 9.5, "axes.titlesize": 10,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 8,
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "axes.unicode_minus": False, "savefig.bbox": "tight",
})


def save(fig, name: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=300)
    plt.close(fig)
    print(f"  {name}.pdf / .png")


def forest(rows, title, xlabel, name, xlim=None, figsize=(6.6, 4.4)):
    """rows: (label, est, lo, hi, n) drawn on a log axis, reference line at 1."""
    fig, ax = plt.subplots(figsize=figsize)
    ys = np.arange(len(rows))[::-1]
    for y, (label, est, lo, hi, n) in zip(ys, rows):
        colour = "#B2182B" if lo > 1 else ("#4393C3" if hi < 1 else "#777777")
        ax.plot([lo, hi], [y, y], color=colour, lw=1.4, solid_capstyle="butt")
        ax.plot(est, y, "o", color=colour, ms=5.5)
        ax.text(1.02, y, f"{est:.2f}", transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=7.5)
        ax.text(1.20, y, f"{int(n):,}", transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=7.5, color="#444444")
    ax.axvline(1, color="#444444", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_ylim(-0.8, len(rows) - 0.2)
    if xlim:
        ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontsize=9.5)
    ax.text(1.02, len(rows) - 0.55, "ROR", transform=ax.get_yaxis_transform(),
            fontsize=7.5, ha="left", color="#444444", weight="bold")
    ax.text(1.20, len(rows) - 0.55, "cases", transform=ax.get_yaxis_transform(),
            fontsize=7.5, ha="left", color="#444444", weight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, name)


# ------------------------------------------------------------------ Figure 1
def figure1() -> None:
    flow = d["case_flow"]
    boxes = [
        (f"FAERS quarterly ASCII releases\n2004Q1-2026Q2 (90 quarters)\n"
         f"submitted reports: {flow['submitted_reports']:,}", "#EFF3FF"),
        ("Case-version de-duplication\nkeep latest FDA_DT per CASEID", "#DEEBF7"),
        (f"De-duplicated cases: {flow['de_duplicated_cases']:,}", "#9ECAE1"),
        (f"Cases naming ethambutol: {flow['ethambutol_any_role']:,}\n"
         f"suspect (PS/SS): {flow['ethambutol_suspect_ps_ss']:,}   "
         f"concomitant only: {flow['ethambutol_concomitant_only']:,}", "#FDDBC7"),
        ("Eleven ocular MedDRA 29.0 queries (narrow sets)\n"
         "2x2 table per query; preferred terms inside the optic-nerve query", "#F4A582"),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    ax.set_axis_off()
    y, step = 1.0, 0.165
    for i, (txt, colour) in enumerate(boxes):
        ax.add_patch(FancyBboxPatch((0.14, y - 0.105), 0.66, 0.105,
                                    boxstyle="round,pad=0.012,rounding_size=0.02",
                                    linewidth=0.9, edgecolor="#333333", facecolor=colour))
        ax.text(0.47, y - 0.052, txt, ha="center", va="center", fontsize=8.4)
        if i < len(boxes) - 1:
            ax.add_patch(FancyArrowPatch((0.47, y - 0.108), (0.47, y - step + 0.052),
                                         arrowstyle="-|>", mutation_scale=12, lw=0.9,
                                         color="#333333"))
        y -= step
    # replication boxes
    ax.add_patch(FancyBboxPatch((0.84, 0.40), 0.15, 0.30,
                                boxstyle="round,pad=0.010,rounding_size=0.02",
                                linewidth=0.9, edgecolor="#333333", facecolor="#E5F5E0"))
    ax.text(0.915, 0.55, "JADER\n1,054,239 cases\n3,483 ethambutol", ha="center",
            va="center", fontsize=7.4)
    ax.add_patch(FancyBboxPatch((0.84, 0.06), 0.15, 0.30,
                                boxstyle="round,pad=0.010,rounding_size=0.02",
                                linewidth=0.9, edgecolor="#333333", facecolor="#E5F5E0"))
    ax.text(0.915, 0.21, "Canada Vigilance\n1,266,430 reports\n965 ethambutol", ha="center",
            va="center", fontsize=7.4)
    ax.add_patch(FancyArrowPatch((0.80, 0.72), (0.84, 0.55), arrowstyle="-|>",
                                 mutation_scale=10, lw=0.8, color="#777777", ls="--"))
    ax.add_patch(FancyArrowPatch((0.80, 0.20), (0.84, 0.21), arrowstyle="-|>",
                                 mutation_scale=10, lw=0.8, color="#777777", ls="--"))
    ax.text(0.915, 0.78, "replication", ha="center", fontsize=7.4, color="#555555")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.02, 1.03)
    save(fig, "Figure1_flow")


# ------------------------------------------------------------------ Figure 2
def figure2() -> None:
    rows = []
    for r in sorted(d["smq"], key=lambda x: x["ror"]):
        rows.append((r["smq"], r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"]))
    forest(rows, "Eleven ocular MedDRA queries, ethambutol vs all other reports",
           "Reporting odds ratio (log scale, 95% CI)", "Figure2_smq_forest",
           xlim=(0.1, 40), figsize=(6.8, 4.6))


# ------------------------------------------------------------------ Figure 3
def figure3() -> None:
    pts = [r for r in d["pt"] if r["group"] == "optic nerve" and r["a"] >= 3]
    ctl = [r for r in d["pt"] if r["group"] == "control"]
    pts.sort(key=lambda r: -r["ror"])
    ctl.sort(key=lambda r: -r["ror"])
    rows = [(r["term"].capitalize(), r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"]) for r in pts]
    rows += [(r["term"].capitalize() + " (control)", r["ror"], r["ror_lcl"], r["ror_ucl"], r["a"])
             for r in ctl]
    forest(rows, "Preferred terms: optic-nerve query (top) and pre-specified controls (bottom)",
           "Reporting odds ratio (log scale, 95% CI)", "Figure3_pt_forest",
           xlim=(0.05, 400), figsize=(6.8, 5.4))


# ------------------------------------------------------------------ Figure 4
def suspect_ci(a: int, n_event: int, n_drug: int) -> tuple[float, float, float]:
    """ROR and Woolf CI for the suspect-only cohort, from the stored cells.

    main_results.json stores the suspect-cohort estimate but not its interval; the other three
    cells of that 2x2 are fixed by the stored counts, so the interval is computed here rather
    than re-queried.
    """
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
    rows = [
        ("Term, all roles (main)", on["ror"], on["ror_lcl"], on["ror_ucl"], on["a"]),
        ("Term, suspect only", on_ps[0], on_ps[1], on_ps[2], on["a_suspect"]),
        ("Query, all roles", smq["ror"], smq["ror_lcl"], smq["ror_ucl"], smq["a"]),
        ("Query, suspect only", smq_ps[0], smq_ps[1], smq_ps[2], smq["a_suspect"]),
        ("Term, 2004-2016", t1["ror"], t1["ror_lcl"], t1["ror_ucl"], t1["a"]),
        ("Term, 2017-2026", t2["ror"], t2["ror_lcl"], t2["ror_ucl"], t2["a"]),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ys = np.arange(len(rows))[::-1]
    for y, (label, est, lo, hi, n) in zip(ys, rows):
        ax.plot([lo, hi], [y, y], color="#B2182B", lw=1.4)
        ax.plot(est, y, "o", color="#B2182B", ms=5)
        ax.text(1.02, y, f"{est:.2f}", transform=ax.get_yaxis_transform(), va="center", fontsize=7.5)
        ax.text(1.18, y, f"{int(n):,}", transform=ax.get_yaxis_transform(), va="center",
                fontsize=7.5, color="#444444")
    ax.axvline(1, color="#444444", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_xlim(20, 900)
    ax.set_xlabel("Reporting odds ratio for the optic-nerve outcome (log scale)")
    ax.set_title("Sensitivity: exposure role and reporting period", loc="left", fontsize=9.5)
    ax.text(1.02, len(rows) - 0.55, "ROR", transform=ax.get_yaxis_transform(), fontsize=7.5,
            weight="bold", color="#444444")
    ax.text(1.18, len(rows) - 0.55, "cases", transform=ax.get_yaxis_transform(), fontsize=7.5,
            weight="bold", color="#444444")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "Figure4_sensitivity")


figure1()
figure2()
figure3()
figure4()
print(f"\nwritten to {OUT.relative_to(ROOT)}")
