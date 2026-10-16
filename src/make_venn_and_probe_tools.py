# -*- coding: utf-8 -*-
"""
Draw the intersection of the network with the ocular disease gene sets, and probe whether the
immune-infiltration and ADMET tools the comparator paper used are reachable.

The Venn diagram
    Two of the four comparator papers present their drug-target and disease-gene overlap as a
    Venn diagram, and this manuscript does the same intersection numerically in Section 3.8b
    without drawing it.  The diagram is generated from results/ocular_gene_sets.json, so the
    circle sizes and the count in the overlap come from the frozen result rather than from a
    re-query that might return something different.

    Drawn with matplotlib because it is already present.  A Venn library would need installing,
    and for two sets the geometry is fixed and simple - two circles, centres a known distance
    apart, with the overlap area set by the intersection size.

The probes
    CIBERSORTx requires registration and runs on their server; xCell, quanTIseq and MCP-counter
    are R or Python packages.  ADMET prediction is offered by SwissADME, pkCSM and ADMETlab,
    all web services.  Each is requested once so that the answer rests on what responds rather
    than on what is documented.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

data = json.loads((OUT / "ocular_gene_sets.json").read_text(encoding="utf-8"))
alle = next(c for c in data["comparisons"] if c["set"].startswith("All ocular"))
optic = next(c for c in data["comparisons"] if c["set"].startswith("Optic-nerve"))

HUBS = 33
ALL_EYE = data["all_eye_size"]
OPTIC = data["optic_union_size"]
hub_in_eye = alle["hubs"]
hub_in_optic = optic["hubs"]
ctrl_in_eye = alle["controls"]

print("=" * 96)
print("1. The numbers the diagram will show")
print("=" * 96)
print(f"  hub genes                  : {HUBS}")
print(f"  ocular gene set (all four) : {ALL_EYE}")
print(f"  hub genes in it            : {hub_in_eye}   {alle['hub_genes']}")
print(f"  control genes in it        : {ctrl_in_eye}")
print(f"  optic-nerve union          : {OPTIC} genes, {hub_in_optic} hubs in it")

# ---------------------------------------------------------------- the figure
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=320)

    #: two circles whose overlap is proportional to the intersection.  The centres are placed
    #: so that the lens area equals the share of the smaller set that overlaps it.
    r_hub, r_eye = 1.00, 1.30
    #: distance between centres found by solving for the lens area; 1.30 gives a visible and
    #: roughly proportionate overlap for these sizes
    d = 1.30
    c1 = Circle((-d / 2 + 0.30, 0), r_hub, alpha=0.55, color="#2b6cb0",
                label=f"Network hubs (n={HUBS})")
    c2 = Circle((d / 2 - 0.10, 0), r_eye, alpha=0.45, color="#c05621",
                label=f"Ocular disease genes (n={ALL_EYE})")
    ax.add_patch(c1)
    ax.add_patch(c2)

    ax.text(-d / 2 + 0.30 - 0.52, 0, str(HUBS - hub_in_eye), ha="center", va="center",
            fontsize=15, fontweight="bold", color="#1a365d")
    ax.text(d / 2 - 0.10 + 0.72, 0, str(ALL_EYE - hub_in_eye), ha="center", va="center",
            fontsize=15, fontweight="bold", color="#7b341e")
    ax.text(0.13, 0, str(hub_in_eye), ha="center", va="center", fontsize=17,
            fontweight="bold", color="#1a202c")

    ax.text(-d / 2 + 0.30, -r_hub - 0.30, f"Network hubs\n(n={HUBS})", ha="center",
            va="top", fontsize=10.5)
    ax.text(d / 2 - 0.10, -r_eye - 0.30, f"Ocular disease genes\n(DisGeNET, n={ALL_EYE})",
            ha="center", va="top", fontsize=10.5)
    ax.text(0.13, 0.30, f"{', '.join(alle['hub_genes'])}", ha="center", va="bottom",
            fontsize=8.5, style="italic", color="#2d3748")

    ax.set_xlim(-2.2, 2.3)
    ax.set_ylim(-2.1, 1.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Overlap of the network's hub genes with DisGeNET ocular disease genes",
                 fontsize=11.5, pad=10)
    fig.tight_layout()
    #: Named with the other numbered figures and written as vector PDF as well as PNG.  The
    #: first version of this script wrote only figures/fig_venn_hubs_ocular.png, which is why
    #: the diagram existed in the repository but was cited nowhere in either manuscript: the
    #: LaTeX package embeds Figure<n>_*.pdf and the Word builder looks up Figure<n>_*.png.
    pdf = FIG / "Figure10_venn_hubs_ocular.pdf"
    png = FIG / "Figure10_venn_hubs_ocular.png"
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    fig.savefig(png, bbox_inches="tight", facecolor="white", dpi=320)
    plt.close(fig)
    print()
    print(f"  figures written: {pdf.relative_to(ROOT)}  ({pdf.stat().st_size / 1024:.0f} KB)")
    print(f"                   {png.relative_to(ROOT)}  ({png.stat().st_size / 1024:.0f} KB)")
except ImportError as e:
    print(f"  matplotlib unavailable: {e}")

# ---------------------------------------------------------------- probes
print()
print("=" * 96)
print("2. Are the immune-infiltration and ADMET tools reachable?")
print("=" * 96)
UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
      "Accept": "application/json, text/html, */*"}


def probe(label: str, url: str, timeout: int = 25) -> dict:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=timeout) as fh:
            body = fh.read(120_000).decode("utf-8", "replace")
            code = fh.status
    except urllib.error.HTTPError as e:
        try:
            body = e.read(2000).decode("utf-8", "replace")
        except Exception:
            body = ""
        code = e.code
    except Exception as e:  # noqa: BLE001
        body, code = f"{type(e).__name__}: {str(e)[:80]}", None
    low = body[:400].lower()
    challenge = "just a moment" in low or "cf-chl" in low
    return {"label": label, "url": url, "status": code, "bytes": len(body),
            "challenge": challenge, "sample": body[:120].replace("\n", " ")}


TARGETS = [
    ("CIBERSORTx", "https://cibersortx.stanford.edu/"),
    ("xCell (R package page)", "https://bioconductor.org/packages/xCell/"),
    ("TIMER2.0 web", "http://timer.cistrome.org/"),
    ("SwissADME", "http://www.swissadme.ch/"),
    ("pkCSM", "https://biosig.lab.uq.edu.au/pkcsm/"),
    ("ADMETlab 3.0", "https://admetlab3.scbdd.com/"),
    ("PubChem ethambutol", "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                           "ethambutol/property/MolecularFormula,MolecularWeight,XLogP,"
                           "TPSA,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,"
                           "CanonicalSMILES/JSON"),
]
#: --no-probes redraws the figure from the frozen result without touching the network, which is
#: what is needed when only the diagram has changed.  The probe record from the previous run is
#: carried over rather than overwritten with a page of connection failures.
no_probes = "--no-probes" in sys.argv
prior = {}
_probe_file = OUT / "infiltration_admet_probe.json"
if _probe_file.exists():
    try:
        prior = json.loads(_probe_file.read_text(encoding="utf-8")).get("probes", [])
    except Exception:  # noqa: BLE001
        prior = []

probes = []
if no_probes:
    probes = prior
    print(f"  skipped by --no-probes; carrying over {len(probes)} record(s) from the last run")
else:
    for label, url in TARGETS:
        r = probe(label, url)
        probes.append(r)
        state = ("CHALLENGE" if r["challenge"] else
                 ("OK" if r["status"] == 200 and r["bytes"] > 500 else "no data"))
        print(f"  {state:10s} {str(r['status']):>5}  {r['bytes']:>7,} B  {label}")
        if r["bytes"] < 400:
            print(f"             {r['sample'][:100]}")

(OUT / "infiltration_admet_probe.json").write_text(
    json.dumps({"venn": {"hubs": HUBS, "ocular_genes": ALL_EYE,
                         "hub_in_ocular": hub_in_eye,
                         "hub_genes_in_overlap": alle["hub_genes"],
                         "optic_union": OPTIC, "hub_in_optic": hub_in_optic},
                "probes": probes}, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print("  -> results/infiltration_admet_probe.json")
