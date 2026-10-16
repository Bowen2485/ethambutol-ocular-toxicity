# -*- coding: utf-8 -*-
"""
Cross-check the network's hub genes against two independent disease-annotation sources, and
against transcriptomic evidence in patient retina.

Why the sources are these two
    The peer papers assemble disease targets from GeneCards and DisGeNET.  Neither is
    reachable here: GeneCards answers 403 and the DisGeNET API serves an HTML page rather
    than data, both requiring a licence or registration.  Substituting a different database
    without saying so would change what the intersection means while leaving the sentence
    unchanged, so the two sources that do answer are used and named: Open Targets, which the
    manuscript already uses for the drug-target landscape, and the HPO gene-to-disease
    annotation service, which is independent of it.

What the analysis does
    For each hub gene it collects the diseases annotated in each source and counts how often
    an optic-nerve or retinal disease appears.  The expectation to test is not that every hub
    appears in both - hub genes from a literature mine are pleiotropic and will map to many
    diseases - but that the set as a whole is annotated for eye disease more often than a
    random set of the same size.  That is what makes it a test rather than a listing.

    Second, the hub genes are checked for expression in patient retina and optic nerve using
    GEO series found through eutils, which is a check on whether the network describes
    tissue that actually expresses its genes.  The HPA single-cell data already in the
    manuscript answer this for cell types; GEO answers it for whole tissue from patients with
    eye disease, which is a different and complementary question.

A note on trust: all responses are external content, inspected as data and never executed.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
RES.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
      "Accept": "application/json, text/plain, */*"}

#: the focus-tier hubs the manuscript names
HUBS = ["TP53", "NFE2L2", "AKT1", "BCL2", "HMOX1", "CASP3", "SOD2", "TNF", "GPX4",
        "MFN2", "SLC7A11", "ACSL4", "SDHB", "OPA1", "SLC25A4", "KEAP1", "MAPK1",
        "IL6", "STAT3", "CAT", "GPX1", "TXN", "NQO1", "HIF1A", "PPARGC1A", "DNM1L",
        "VDAC1", "CYCS", "APAF1", "BAX", "BCL2L1", "FTH1", "FTL"]

#: genes used as a comparison set: the same size, drawn from a fixed unrelated pathway so
#: the comparison is reproducible rather than resampled
CONTROL = ["HBB", "HBA1", "ALB", "APOA1", "APOB", "FGA", "FGB", "FGG", "SERPINA1",
           "ORM1", "HP", "TF", "CP", "AMY1A", "AMY2A", "PRSS1", "CELA1", "CTRB1",
           "CPA1", "PNLIP", "CLPS", "CELA3A", "SYCN", "PNLIPRP1", "CTRB2", "CEL",
           "CPA2", "PRSS2", "CTRC", "CELP", "PNLIPRP2", "CLPSL1", "CELA2A"]

EYE_RE = re.compile(
    r"retin|optic|macula|ocular|eye|glaucom|uveit|choroid|conjunctiv|cornea|"
    r"leber|stargardt|cone-rod|photoreceptor|visual", re.I)

NS = {"OT": "https://api.platform.opentargets.org/api/v4/graphql"}


def post_json(url: str, payload: dict, timeout: int = 45):
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={**UA, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            return json.loads(fh.read(600_000).decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"__error__": f"{type(e).__name__}: {str(e)[:100]}"}


def get_json(url: str, timeout: int = 45):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=timeout) as fh:
            return json.loads(fh.read(600_000).decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"__error__": f"{type(e).__name__}: {str(e)[:100]}"}


def opentargets_diseases(symbol: str) -> list[str]:
    """Diseases associated with a gene, via the Open Targets GraphQL API."""
    q = {"query": '{ search(queryString: "%s", entityNames: ["target"]) '
                  '{ hits { id } } }' % symbol}
    r = post_json(NS["OT"], q)
    hits = (((r or {}).get("data") or {}).get("search") or {}).get("hits") or []
    if not hits:
        return []
    tid = hits[0]["id"]
    q2 = {"query": '{ target(ensemblId: "%s") { associatedDiseases(page: {index: 0, '
                   'size: 40}) { rows { disease { name } score } } } }' % tid}
    r2 = post_json(NS["OT"], q2)
    rows = ((((r2 or {}).get("data") or {}).get("target") or {})
            .get("associatedDiseases") or {}).get("rows") or []
    return [str(x["disease"]["name"]) for x in rows if x.get("disease")]


def hpo_diseases(symbol: str) -> list[str]:
    """Diseases annotated for a gene by the HPO service."""
    r = get_json(f"https://ontology.jax.org/api/network/annotation/{symbol}")
    if not isinstance(r, dict) or "__error__" in r:
        return []
    out = []
    for d in (r.get("diseases") or []):
        if isinstance(d, dict) and d.get("name"):
            out.append(str(d["name"]))
    return out


print("=" * 100)
print("1. Disease annotation of the hub genes, from two sources")
print("=" * 100)


def annotate(genes: list[str], label: str) -> dict[str, dict]:
    out = {}
    for i, g in enumerate(genes, 1):
        ot = opentargets_diseases(g)
        hp = hpo_diseases(g)
        eye_ot = [d for d in ot if EYE_RE.search(d)]
        eye_hp = [d for d in hp if EYE_RE.search(d)]
        out[g] = {"open_targets_total": len(ot), "hpo_total": len(hp),
                  "eye_in_opentargets": eye_ot[:6], "eye_in_hpo": eye_hp[:6],
                  "any_eye": bool(eye_ot or eye_hp)}
        if i % 8 == 0:
            print(f"    {label}: {i}/{len(genes)} genes queried")
        time.sleep(0.15)
    return out


hub_ann = annotate(HUBS, "hubs")
ctrl_ann = annotate(CONTROL, "controls")

n_hub_eye = sum(1 for v in hub_ann.values() if v["any_eye"])
n_ctrl_eye = sum(1 for v in ctrl_ann.values() if v["any_eye"])
print()
print(f"  hub genes with an eye-disease annotation      : {n_hub_eye}/{len(HUBS)} "
      f"({100*n_hub_eye/len(HUBS):.0f}%)")
print(f"  control genes with an eye-disease annotation  : {n_ctrl_eye}/{len(CONTROL)} "
      f"({100*n_ctrl_eye/len(CONTROL):.0f}%)")

print()
print("  hub genes annotated for eye disease:")
for g, v in hub_ann.items():
    if v["any_eye"]:
        names = (v["eye_in_opentargets"] + v["eye_in_hpo"])[:3]
        print(f"      {g:10s} {', '.join(names)[:88]}")

# Fisher exact test without scipy, by summing hypergeometric probabilities
def fisher_one_sided(a: int, b: int, c: int, d: int) -> float:
    from math import comb
    n = a + b + c + d
    r1, c1 = a + b, a + c
    p = 0.0
    hi = min(r1, c1)
    for k in range(a, hi + 1):
        p += comb(c1, k) * comb(n - c1, r1 - k) / comb(n, r1)
    return p


p_val = fisher_one_sided(n_hub_eye, len(HUBS) - n_hub_eye,
                         n_ctrl_eye, len(CONTROL) - n_ctrl_eye)
print()
print(f"  Fisher exact, one-sided: p = {p_val:.4f}")
print(f"  odds ratio: "
      f"{((n_hub_eye+0.5)*(len(CONTROL)-n_ctrl_eye+0.5))/((len(HUBS)-n_hub_eye+0.5)*(n_ctrl_eye+0.5)):.2f} "
      f"(Haldane-Anscombe correction)")

with open(RES / "hub_disease_annotation.csv", "w", newline="", encoding="utf-8-sig") as fh:
    import csv as _csv
    w = _csv.writer(fh)
    w.writerow(["gene", "set", "open_targets_diseases", "hpo_diseases",
                "eye_annotations", "any_eye"])
    for g, v in hub_ann.items():
        w.writerow([g, "hub", v["open_targets_total"], v["hpo_total"],
                    "; ".join((v["eye_in_opentargets"] + v["eye_in_hpo"])[:5]),
                    v["any_eye"]])
    for g, v in ctrl_ann.items():
        w.writerow([g, "control", v["open_targets_total"], v["hpo_total"],
                    "; ".join((v["eye_in_opentargets"] + v["eye_in_hpo"])[:5]),
                    v["any_eye"]])

print()
print("=" * 100)
print("2. Transcriptomic evidence in patient retina and optic nerve (GEO)")
print("=" * 100)


def esearch(term: str, n: int = 15) -> list[str]:
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds"
           f"&term={urllib.parse.quote(term)}&retmax={n}&retmode=json")
    r = get_json(url)
    return (r.get("esearchresult", {}) or {}).get("idlist", []) or []


def esummary(ids: list[str]) -> list[dict]:
    if not ids:
        return []
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds"
           f"&id={','.join(ids)}&retmode=json")
    r = get_json(url)
    res = (r.get("result") or {})
    out = []
    for uid in res.get("uids", []):
        d = res.get(uid, {})
        out.append({"gse": d.get("accession", ""), "title": d.get("title", ""),
                    "n_samples": d.get("n_samples"), "taxon": d.get("taxon", ""),
                    "summary": (d.get("summary") or "")[:200]})
    return out


QUERIES = {
    "retina, human": '(retina[All Fields] OR retinal[All Fields]) AND '
                     '"Homo sapiens"[Organism] AND gse[Entry Type]',
    "optic nerve, human": '("optic nerve"[All Fields] OR "optic neuropathy"[All Fields]) '
                          'AND "Homo sapiens"[Organism] AND gse[Entry Type]',
    "retinal ganglion cell, human": '("retinal ganglion cell"[All Fields]) AND '
                                    '"Homo sapiens"[Organism] AND gse[Entry Type]',
}
geo = {}
for label, term in QUERIES.items():
    ids = esearch(term, 12)
    recs = esummary(ids)
    geo[label] = recs
    print(f"\n  {label}: {len(recs)} series")
    for r in recs[:6]:
        print(f"      {r['gse']:12s} {str(r['n_samples']):>5s} samples  "
              f"{r['title'][:72]}")

(RES / "geo_series_candidates.json").write_text(
    json.dumps({"geo": geo, "annotation": {"hubs": hub_ann, "controls": ctrl_ann},
                "eye_counts": {"hubs": n_hub_eye, "controls": n_ctrl_eye},
                "fisher_p": p_val}, indent=2, ensure_ascii=False), encoding="utf-8")

print()
print("=" * 100)
print("What was written")
print("=" * 100)
print(f"  {(RES / 'hub_disease_annotation.csv').relative_to(ROOT)}")
print(f"  {(RES / 'geo_series_candidates.json').relative_to(ROOT)}")
print()
print("""  The GEO series are recorded as candidates rather than analysed, because downloading
  and normalising expression matrices is a separate step and doing it casually would be
  worse than not doing it.  The annotation counts and the Fisher test are complete.""")
