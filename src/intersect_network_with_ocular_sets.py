# -*- coding: utf-8 -*-
"""
Build the disease-gene sets in full and intersect them with the network, which is the step
the comparator papers report and this manuscript had never done.

What the comparators do with these sets
    They take the drug's targets, take the disease's genes, and analyse the intersection only.
    The intersection is the object of study: a PPI network is built from it, its hubs are
    taken, and its pathways are enriched.  The number reported is the size of the intersection,
    which is why their disease sets are large - 2,835 genes for SJS/TEN - and their
    intersections are small - 30.

    This manuscript instead built its network from literature co-mention, so its genes are
    already restricted to ones discussed alongside ethambutol and eye disease.  Intersecting
    them with an ocular gene set therefore asks a different question: not "which genes are
    both drug targets and disease genes", but "how much of this literature-derived network is
    independently supported by disease annotation".  That is worth reporting, and it is what
    the comparator method yields when applied here.

Two comparisons are made
    The intersection with the optic-nerve and ocular sets, counted as genes and as a share of
    the network.
    The same intersection for the 33 control genes, because a share is only interpretable
    against a baseline.  The controls are the exocrine pancreatic genes used elsewhere in this
    analysis, chosen for having no ocular role.

The sets are drawn from DisGeNET, which under an academic plan serves curated sources only.
The counts are therefore lower bounds and the restriction is carried into the reporting.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

KEY = (ROOT / "credential" / "disgenet_key.txt").read_text(
    encoding="utf-8", errors="replace").strip().split()[-1].strip(chr(34)).strip(chr(39))
BASE = "https://api.disgenet.com/api/v1/gda/summary"
HEADERS = {"Authorization": KEY, "accept": "*/*",
           "User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)"}

#: the identifiers that returned data, with what each covers
SETS = {
    "UMLS_C0029134": "Optic Nerve Diseases",
    "UMLS_C0271084": "Optic Neuropathy",
    "UMLS_C0015397": "Eye Diseases",
    "UMLS_C0035309": "Retinal Diseases",
}

HUBS = ["TP53", "NFE2L2", "AKT1", "BCL2", "HMOX1", "CASP3", "SOD2", "TNF", "GPX4",
        "MFN2", "SLC7A11", "ACSL4", "SDHB", "OPA1", "SLC25A4", "KEAP1", "MAPK1",
        "IL6", "STAT3", "CAT", "GPX1", "TXN", "NQO1", "HIF1A", "PPARGC1A", "DNM1L",
        "VDAC1", "CYCS", "APAF1", "BAX", "BCL2L1", "FTH1", "FTL"]
CONTROL = ["HBB", "HBA1", "ALB", "APOA1", "APOB", "FGA", "FGB", "FGG", "SERPINA1",
           "ORM1", "HP", "TF", "CP", "AMY1A", "AMY2A", "PRSS1", "CELA1", "CTRB1",
           "CPA1", "PNLIP", "CLPS", "CELA3A", "SYCN", "PNLIPRP1", "CTRB2", "CEL",
           "CPA2", "PRSS2", "CTRC", "CELP", "PNLIPRP2", "CLPSL1", "CELA2A"]


def query(params: dict, retries: int = 4) -> dict:
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=HEADERS), timeout=90) as fh:
                return json.loads(fh.read(4_000_000).decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": f"HTTP {e.code}"}
        except Exception as e:  # noqa: BLE001
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": f"{type(e).__name__}: {str(e)[:90]}"}
    return {"__error__": "exhausted"}


def gene_set(cui: str, page_size: int = 500, max_pages: int = 6) -> tuple[set[str], int, str]:
    """All gene symbols associated with a disorder, paginated."""
    genes: set[str] = set()
    page, total = 0, None
    while page < max_pages:
        r = query({"disease": cui, "page_size": page_size, "page_number": page,
                   "order_by": "score", "order": "DESC"})
        if r.get("__error__"):
            return genes, total or 0, r["__error__"]
        pay = r.get("payload") or []
        if total is None:
            total = (r.get("paging") or {}).get("totalElements", len(pay))
        if not pay:
            break
        for x in pay:
            sym = (x.get("symbolOfGene") or x.get("geneSymbol") or "").strip().upper()
            if sym:
                genes.add(sym)
        page += 1
        if total and len(genes) >= total:
            break
        time.sleep(0.2)
    return genes, (total or len(genes)), ""


sets: dict[str, set[str]] = {}
meta: dict[str, dict] = {}
for cui, label in SETS.items():
    genes, total, err = gene_set(cui)
    sets[cui] = genes
    meta[cui] = {"label": label, "total_reported": total, "genes_retrieved": len(genes),
                 "error": err}
    print(f"  {label:24s} reported {total:>5}   retrieved {len(genes):>5} unique symbols"
          f"{'   ' + err if err else ''}")

#: the union of the optic-nerve sets, which is the comparison this paper is about
OPTIC = sets["UMLS_C0029134"] | sets["UMLS_C0271084"]
ALL_EYE = OPTIC | sets["UMLS_C0015397"] | sets["UMLS_C0035309"]

print()
print("=" * 100)
print("1. The intersection with the network")
print("=" * 100)
print(f"  {'set':26s} {'size':>6s} {'hubs in it':>11s} {'controls in it':>15s}")
rows = []
for name, s in (("Optic-nerve union", OPTIC), ("All ocular sets", ALL_EYE)):
    h = sorted(set(HUBS) & s)
    c = sorted(set(CONTROL) & s)
    rows.append((name, len(s), h, c))
    print(f"  {name:26s} {len(s):>6d} {len(h):>11d} {len(c):>15d}")
for cui, label in SETS.items():
    h = sorted(set(HUBS) & sets[cui])
    c = sorted(set(CONTROL) & sets[cui])
    print(f"  {label:26s} {len(sets[cui]):>6d} {len(h):>11d} {len(c):>15d}")

print()
print("  hub genes present in the ocular sets:")
for name, size, h, c in rows:
    print(f"      {name}: {', '.join(h) if h else 'none'}")
print("  control genes present in the ocular sets:")
for name, size, h, c in rows:
    print(f"      {name}: {', '.join(c) if c else 'none'}")

print()
print("=" * 100)
print("2. Is the network enriched for ocular disease genes?")
print("=" * 100)
print("""  The shares have to be compared against the same shares for the control set, because a
  gene in a curated database is more likely to appear in any disease set simply by being
  well studied, and the hub genes are chosen from the literature.""")
print()
print(f"  {'set':26s} {'hubs':>12s} {'controls':>12s} {'Fisher P':>11s}")
fisher_rows = []
for name, size, h, c in rows:
    a, b = len(h), len(HUBS) - len(h)
    cc, d = len(c), len(CONTROL) - len(c)
    p = sum(comb(a + cc, k) * comb(b + d, (a + b) - k) / comb(a + b + cc + d, a + b)
            for k in range(a, min(a + b, a + cc) + 1))
    fisher_rows.append({"set": name, "hubs": a, "controls": cc, "p": p,
                        "hub_genes": h, "control_genes": c})
    print(f"  {name:26s} {a:>5d}/{len(HUBS):<6d} {cc:>5d}/{len(CONTROL):<6d} {p:>11.3e}")

print()
print("=" * 100)
print("3. What this says, and what it does not")
print("=" * 100)
best = min(fisher_rows, key=lambda r: r["p"])
print(f"""  The strongest comparison is {best['set']}: {best['hubs']} of {len(HUBS)} hub genes
  against {best['controls']} of {len(CONTROL)} controls, Fisher P = {best['p']:.2e}.

  This is the comparator papers' step applied to this manuscript's network, and it answers a
  question the earlier per-gene check could not: not whether an individual gene is annotated
  for eye disease, which every well-studied gene will be somewhere, but whether the set as a
  whole overlaps the ocular gene sets more than a control set does.

  Two limits are carried forward.  The sets come from DisGeNET's curated sources only, so both
  counts are lower bounds; and the hub genes were derived from literature that discusses
  ethambutol and eye disease together, so an overlap is partly expected and the control
  comparison is what gives the number meaning.""")

(OUT / "ocular_gene_sets.json").write_text(json.dumps(
    {"sets": {k: sorted(v) for k, v in sets.items()}, "meta": meta,
     "optic_union_size": len(OPTIC), "all_eye_size": len(ALL_EYE),
     "comparisons": fisher_rows}, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  -> results/ocular_gene_sets.json")
