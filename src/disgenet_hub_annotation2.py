# -*- coding: utf-8 -*-
"""
Read the DisGeNET payload with the field names it actually uses.

The interface now works - status OK, 100 rows in the first page - but the previous script
read nothing useful because it asked for "disease_name" and the payload calls it
"diseaseName".  Every gene therefore appeared to have no eye association, which is false and
would have been reported as a finding if the count had not been checked against the raw
payload first.

The lesson is the one that has recurred in this project: inspect the response before
writing code against it.  So this prints the real field names and a sample row before doing
anything with them, and the analysis only starts once the names are confirmed.
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
HEADERS = {"Authorization": KEY, "accept": "*/*",
           "User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)"}


def query(symbol: str, page: int = 0, page_size: int = 100, retries: int = 3) -> dict:
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
            return {"__error__": f"HTTP {e.code}"}
        except Exception as e:  # noqa: BLE001
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": f"{type(e).__name__}: {str(e)[:80]}"}
    return {"__error__": "exhausted"}


print("=" * 100)
print("1. The payload's real fields, printed before anything is written against them")
print("=" * 100)
r = query("APOE", page_size=3)
if r.get("__error__"):
    raise SystemExit(f"interface failed: {r['__error__']}")
pay = r.get("payload") or []
print(f"  status {r.get('status')}   rows {len(pay)}   paging {r.get('paging')}")
if pay:
    row = pay[0]
    print(f"\n  fields ({len(row)}):")
    for k in sorted(row):
        v = row[k]
        s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
        print(f"      {k:44s} {str(s)[:78]}")
    # the two fields the analysis needs
    name_field = "diseaseName" if "diseaseName" in row else None
    gene_field = next((k for k in row if k.lower() in ("gene_symbol", "genesymbol",
                                                       "gene", "symbol")), None)
    score_field = next((k for k in row if k.lower() == "score"), None)
    ei_field = next((k for k in row if k.lower() in ("ei", "evidence_index",
                                                     "evidencelevel",
                                                     "evidence_level")), None)
    print(f"\n  resolved: disease={name_field!r} gene={gene_field!r} "
          f"score={score_field!r} evidence={ei_field!r}")
else:
    raise SystemExit("empty payload")

if not name_field:
    raise SystemExit("could not identify the disease-name field; stopping")

HUBS = ["TP53", "NFE2L2", "AKT1", "BCL2", "HMOX1", "CASP3", "SOD2", "TNF", "GPX4",
        "MFN2", "SLC7A11", "ACSL4", "SDHB", "OPA1", "SLC25A4", "KEAP1", "MAPK1",
        "IL6", "STAT3", "CAT", "GPX1", "TXN", "NQO1", "HIF1A", "PPARGC1A", "DNM1L",
        "VDAC1", "CYCS", "APAF1", "BAX", "BCL2L1", "FTH1", "FTL"]
CONTROL = ["HBB", "HBA1", "ALB", "APOA1", "APOB", "FGA", "FGB", "FGG", "SERPINA1",
           "ORM1", "HP", "TF", "CP", "AMY1A", "AMY2A", "PRSS1", "CELA1", "CTRB1",
           "CPA1", "PNLIP", "CLPS", "CELA3A", "SYCN", "PNLIPRP1", "CTRB2", "CEL",
           "CPA2", "PRSS2", "CTRC", "CELP", "PNLIPRP2", "CLPSL1", "CELA2A"]

EYE_RE = ("retin", "optic", "macula", "ocular", "eye", "glaucom", "uveit", "choroid",
          "conjunctiv", "cornea", "leber", "stargardt", "cone-rod", "photoreceptor",
          "visual", "cataract", "kerat", "amblyop", "nyctalop", "colour blind",
          "color blind", "achromatops")


def diseases(symbol: str) -> list[dict]:
    rows: list[dict] = []
    r0 = query(symbol, page=0)
    rows.extend(r0.get("payload") or [])
    total = (r0.get("paging") or {}).get("totalElements", 0)
    page = 1
    while len(rows) < min(total, 500) and page <= 5:
        rn = query(symbol, page=page)
        got = rn.get("payload") or []
        if not got:
            break
        rows.extend(got)
        page += 1
    return rows


def analyse(genes: list[str], label: str) -> dict[str, dict]:
    out = {}
    for i, g in enumerate(genes, 1):
        rows = diseases(g)
        eye = [x for x in rows
               if any(k in str(x.get(name_field) or "").lower() for k in EYE_RE)]
        strong = []
        for x in eye:
            try:
                sc = float(x.get(score_field)) if score_field else 0.0
            except (TypeError, ValueError):
                sc = 0.0
            lvl = str(x.get(ei_field) or "").lower() if ei_field else ""
            if sc >= 0.3 or "definitive" in lvl or "strong" in lvl:
                strong.append(x)
        out[g] = {
            "n_diseases": len(rows),
            "n_eye": len(eye),
            "eye_diseases": sorted({str(x.get(name_field)) for x in eye})[:10],
            "strong_eye": sorted({str(x.get(name_field)) for x in strong})[:10],
            "max_score": (round(max((float(x.get(score_field) or 0)
                                     for x in rows), default=0), 3)
                          if score_field else None),
        }
        if i % 10 == 0:
            print(f"    {label}: {i}/{len(genes)}")
        time.sleep(0.2)
    return out


print()
print("=" * 100)
print("2. Eye associations across the two gene sets")
print("=" * 100)
hub = analyse(HUBS, "hubs")
ctrl = analyse(CONTROL, "controls")

n_hub_eye = sum(1 for v in hub.values() if v["n_eye"])
n_ctrl_eye = sum(1 for v in ctrl.values() if v["n_eye"])
n_hub_strong = sum(1 for v in hub.values() if v["strong_eye"])
n_ctrl_strong = sum(1 for v in ctrl.values() if v["strong_eye"])

print()
print(f"  hub genes with any eye association     : {n_hub_eye}/{len(HUBS)} "
      f"({100*n_hub_eye/len(HUBS):.0f}%)")
print(f"  control genes with any eye association : {n_ctrl_eye}/{len(CONTROL)} "
      f"({100*n_ctrl_eye/len(CONTROL):.0f}%)")
print()
print("  hub genes with eye associations:")
for g, v in sorted(hub.items(), key=lambda kv: -kv[1]["n_eye"]):
    if v["n_eye"]:
        print(f"      {g:10s} {v['n_eye']:>3d} of {v['n_diseases']:>4d}   "
              f"{', '.join(v['eye_diseases'][:2])[:76]}")
if n_ctrl_eye:
    print()
    print("  control genes with eye associations (the comparison set):")
    for g, v in sorted(ctrl.items(), key=lambda kv: -kv[1]["n_eye"]):
        if v["n_eye"]:
            print(f"      {g:10s} {v['n_eye']:>3d} of {v['n_diseases']:>4d}   "
                  f"{', '.join(v['eye_diseases'][:2])[:76]}")

from math import comb


def fisher(a: int, b: int, c: int, d: int) -> float:
    n = a + b + c + d
    r1, c1 = a + b, a + c
    return sum(comb(c1, k) * comb(n - c1, r1 - k) / comb(n, r1)
               for k in range(a, min(r1, c1) + 1))


p_any = fisher(n_hub_eye, len(HUBS) - n_hub_eye, n_ctrl_eye, len(CONTROL) - n_ctrl_eye)
p_strong = fisher(n_hub_strong, len(HUBS) - n_hub_strong,
                  n_ctrl_strong, len(CONTROL) - n_ctrl_strong)
print()
print(f"  Fisher exact, any eye association  : p = {p_any:.4f}")
print(f"  hub with a strong eye association  : {n_hub_strong}/{len(HUBS)}   "
      f"control {n_ctrl_strong}/{len(CONTROL)}   Fisher p = {p_strong:.4f}")

(RES / "disgenet_hub_annotation.json").write_text(json.dumps(
    {"hubs": hub, "controls": ctrl, "fisher_any": p_any, "fisher_strong": p_strong,
     "n_hub_eye": n_hub_eye, "n_ctrl_eye": n_ctrl_eye,
     "n_hub_strong": n_hub_strong, "n_ctrl_strong": n_ctrl_strong,
     "fields_used": {"disease": name_field, "score": score_field,
                     "evidence": ei_field},
     "restriction": "academic plan: CURATED sources only"},
    indent=2, ensure_ascii=False), encoding="utf-8")

import csv as _csv
with open(RES / "disgenet_hub_annotation.csv", "w", newline="",
          encoding="utf-8-sig") as fh:
    w = _csv.writer(fh)
    w.writerow(["gene", "set", "n_diseases", "n_eye", "n_strong_eye", "max_score",
                "eye_diseases"])
    for g, v in hub.items():
        w.writerow([g, "hub", v["n_diseases"], v["n_eye"], len(v["strong_eye"]),
                    v["max_score"], "; ".join(v["eye_diseases"])])
    for g, v in ctrl.items():
        w.writerow([g, "control", v["n_diseases"], v["n_eye"], len(v["strong_eye"]),
                    v["max_score"], "; ".join(v["eye_diseases"])])
print()
print(f"  -> {RES / 'disgenet_hub_annotation.csv'}")
print(f"  -> {RES / 'disgenet_hub_annotation.json'}")
