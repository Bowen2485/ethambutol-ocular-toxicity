# -*- coding: utf-8 -*-
"""
Retrieve hub-gene disease associations from DisGeNET using the documented interface.

The endpoint and its authentication were taken from the platform's own API console rather
than inferred:

    GET https://api.disgenet.com/api/v1/gda/summary
    Authorization: <the UUID>            no "Bearer" prefix
    parameters: gene_symbol, gene_ncbi_id, uniprot_id, source, order_by, page_number ...
    response:   {"status","paging","payload","warnings"}

Two earlier attempts failed for reasons worth recording, because both were faults of
assumption rather than of the service: the host was www.disgenet.org, which serves its web
page for every path, and the header was written as "Bearer <uuid>", which the API does not
use.

An academic plan is restricted to CURATED sources - CHEMBL, CLINGEN, CLINPGX, CLINVAR,
GENCC, MGD_HUMAN, ORPHANET, PSYGENET, RGD_HUMAN, UNIPROT - which the response states in its
warnings.  That restriction is carried into the reporting rather than hidden: it is a real
limit on coverage and it explains part of why the count differs from the full database.

The stored evidence is filed by DisGeNET's own evidence index, so associations are ranked by
score and the strong ones can be separated from the weak.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
RES.mkdir(parents=True, exist_ok=True)
KEY = (ROOT / "credential" / "disgenet_key.txt").read_text(
    encoding="utf-8", errors="replace").strip().split()[-1].strip('"').strip("'")

BASE = "https://api.disgenet.com/api/v1/gda/summary"

HUBS = ["TP53", "NFE2L2", "AKT1", "BCL2", "HMOX1", "CASP3", "SOD2", "TNF", "GPX4",
        "MFN2", "SLC7A11", "ACSL4", "SDHB", "OPA1", "SLC25A4", "KEAP1", "MAPK1",
        "IL6", "STAT3", "CAT", "GPX1", "TXN", "NQO1", "HIF1A", "PPARGC1A", "DNM1L",
        "VDAC1", "CYCS", "APAF1", "BAX", "BCL2L1", "FTH1", "FTL"]
CONTROL = ["HBB", "HBA1", "ALB", "APOA1", "APOB", "FGA", "FGB", "FGG", "SERPINA1",
           "ORM1", "HP", "TF", "CP", "AMY1A", "AMY2A", "PRSS1", "CELA1", "CTRB1",
           "CPA1", "PNLIP", "CLPS", "CELA3A", "SYCN", "PNLIPRP1", "CTRB2", "CEL",
           "CPA2", "PRSS2", "CTRC", "CELP", "PNLIPRP2", "CLPSL1", "CELA2A"]

EYE_RE = ("retin", "optic", "macula", "ocular", "eye", "glaucom", "uveit", "choroid",
          "conjunctiv", "cornea", "leber", "stargardt", "cone-rod",
          "photoreceptor", "visual", "cataract", "kerat")

HEADERS = {"Authorization": KEY, "accept": "*/*",
           "User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)"}


def query(symbol: str, page: int = 0, page_size: int = 100, retries: int = 3):
    params = {"gene_symbol": symbol, "order_by": "score", "order": "DESC",
              "page_number": page, "page_size": page_size}
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=HEADERS), timeout=45) as fh:
                return json.loads(fh.read(1_500_000).decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": f"HTTP {e.code}", "status": None}
        except Exception as e:  # noqa: BLE001
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": f"{type(e).__name__}: {str(e)[:90]}", "status": None}
    return {"__error__": "exhausted", "status": None}


print("=" * 100)
print("1. Verify the documented call works")
print("=" * 100)
probe = query("APOE", page=0, page_size=5)
if probe.get("__error__"):
    print(f"  FAILED: {probe['__error__']}")
else:
    pay = probe.get("payload") or probe.get("data") or []
    print(f"  status  : {probe.get('status')}")
    print(f"  paging  : {probe.get('paging')}")
    print(f"  payload : {len(pay)} row(s)")
    if pay:
        row = pay[0]
        print(f"  first row keys: {sorted(row)[:14]}")
        print(f"    gene    : {row.get('gene_symbol')}")
        print(f"    disease : {row.get('disease_name')}")
        print(f"    score   : {row.get('score')}   source: {row.get('source')}")
    warn = probe.get("warnings") or []
    for w in warn[:3]:
        print(f"  warning : {str(w)[:110]}")

if probe.get("__error__"):
    raise SystemExit("the interface did not answer; stopping rather than guessing further")


def _is_strong(row: dict) -> bool:
    """A conservative "strong" call: high score, or a definitive evidence level."""
    try:
        sc = float(row.get("score"))
    except (TypeError, ValueError):
        sc = 0.0
    lvl = str(row.get("ei") or row.get("evidence_level") or "").lower()
    return sc >= 0.5 or "definitive" in lvl or "strong" in lvl


def annotate(genes: list[str]) -> dict[str, dict]:
    out = {}
    for i, g in enumerate(genes, 1):
        rows: list[dict] = []
        r = query(g, page=0, page_size=100)
        pay = r.get("payload") or r.get("data") or []
        rows.extend(pay)
        # follow one page further if the API says there is more
        paging = r.get("paging") or {}
        if paging.get("totalPages", 1) > 1 and not r.get("__error__"):
            r2 = query(g, page=1, page_size=100)
            rows.extend(r2.get("payload") or r2.get("data") or [])
        # names and strong calls are derived from the same row objects, so they cannot
        # get out of step; an earlier version built the names list separately and zipped
        # it back to the rows, which would have mis-paired them if any name were missing
        names = [str(x.get("disease_name") or "") for x in rows]
        scored = [x for x in rows if x.get("score") is not None]
        scores = []
        for x in scored:
            try:
                scores.append(float(x.get("score")))
            except (TypeError, ValueError):
                continue
        eye = [x for x in rows
               if any(k in str(x.get("disease_name") or "").lower() for k in EYE_RE)]
        strong = [x for x in eye if _is_strong(x)]
        out[g] = {
            "n_diseases": len(rows),
            "n_eye": len(eye),
            "eye_diseases": [str(x.get("disease_name")) for x in eye[:8]],
            "strong_eye": [str(x.get("disease_name")) for x in strong[:8]],
            "max_score": round(max(scores), 3) if scores else None,
            "sources": sorted({str(x.get("source") or "") for x in rows}),
        }
        if i % 10 == 0:
            print(f"    queried {i}/{len(genes)}")
        time.sleep(0.25)
    return out


print()
print("=" * 100)
print("2. Hub genes and control genes")
print("=" * 100)
hub = annotate(HUBS)
ctrl = annotate(CONTROL)

n_hub_eye = sum(1 for v in hub.values() if v["n_eye"] > 0)
n_ctrl_eye = sum(1 for v in ctrl.values() if v["n_eye"] > 0)
print()
print(f"  hub genes with an eye association      : {n_hub_eye}/{len(HUBS)} "
      f"({100*n_hub_eye/len(HUBS):.0f}%)")
print(f"  control genes with an eye association  : {n_ctrl_eye}/{len(CONTROL)} "
      f"({100*n_ctrl_eye/len(CONTROL):.0f}%)")
print()
print("  hub genes with eye associations:")
for g, v in sorted(hub.items(), key=lambda kv: -kv[1]["n_eye"]):
    if v["n_eye"]:
        print(f"      {g:10s} {v['n_eye']:>3d} eye of {v['n_diseases']:>3d} total   "
              f"e.g. {', '.join(v['eye_diseases'][:2])[:70]}")

# Fisher exact, one-sided, computed by summing hypergeometric terms
from math import comb


def fisher(a: int, b: int, c: int, d: int) -> float:
    n = a + b + c + d
    r1, c1 = a + b, a + c
    return sum(comb(c1, k) * comb(n - c1, r1 - k) / comb(n, r1)
               for k in range(a, min(r1, c1) + 1))


p_all = fisher(n_hub_eye, len(HUBS) - n_hub_eye, n_ctrl_eye, len(CONTROL) - n_ctrl_eye)
print()
print(f"  Fisher exact, any eye association, one-sided p = {p_all:.4f}")

# the same test restricted to stronger evidence
n_hub_strong = sum(1 for v in hub.values() if v["strong_eye"])
n_ctrl_strong = sum(1 for v in ctrl.values() if v["strong_eye"])
p_strong = fisher(n_hub_strong, len(HUBS) - n_hub_strong,
                  n_ctrl_strong, len(CONTROL) - n_ctrl_strong)
print(f"  hub with a STRONG eye association      : {n_hub_strong}/{len(HUBS)}")
print(f"  control with a STRONG eye association  : {n_ctrl_strong}/{len(CONTROL)}")
print(f"  Fisher exact, strong only, one-sided p  = {p_strong:.4f}")

with open(RES / "disgenet_hub_annotation.csv", "w", newline="", encoding="utf-8-sig") as fh:
    import csv as _csv
    w = _csv.writer(fh)
    w.writerow(["gene", "set", "n_diseases", "n_eye", "n_strong_eye", "max_score",
                "sources", "eye_diseases"])
    for g, v in hub.items():
        w.writerow([g, "hub", v["n_diseases"], v["n_eye"],
                    len(v["strong_eye"]), v["max_score"],
                    ";".join(v["sources"]), "; ".join(v["eye_diseases"])])
    for g, v in ctrl.items():
        w.writerow([g, "control", v["n_diseases"], v["n_eye"],
                    len(v["strong_eye"]), v["max_score"],
                    ";".join(v["sources"]), "; ".join(v["eye_diseases"])])
(RES / "disgenet_hub_annotation.json").write_text(
    json.dumps({"hubs": hub, "controls": ctrl,
                "fisher_any": p_all, "fisher_strong": p_strong,
                "n_hub_eye": n_hub_eye, "n_ctrl_eye": n_ctrl_eye,
                "n_hub_strong": n_hub_strong, "n_ctrl_strong": n_ctrl_strong,
                "restriction": "academic plan: CURATED sources only"},
               indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  -> {RES / 'disgenet_hub_annotation.csv'}")
print(f"  -> {RES / 'disgenet_hub_annotation.json'}")
