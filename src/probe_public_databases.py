# -*- coding: utf-8 -*-
"""
Test which public databases offering country-level denominators are actually usable.

The paper's structural weakness is that FAERS and JADER have no denominator: every
figure is a proportion of reports, never an incidence, because nobody knows how many
people took ethambutol.  That is why the analysis is a disproportionality study and not
a risk study.

A tuberculosis burden database can supply the missing term, at least in approximate
form.  Ethambutol is part of the standard first-line regimen, so the number of people
treated with it is a fairly stable fraction of the number of people treated for
tuberculosis, and that number is published annually by country.  Dividing reports by an
estimated treated population converts a report proportion into a report rate.

Candidates:
    WHO Global Health Observatory   official API, tuberculosis indicators by country
                                    and year, including incidence and treatment
                                    coverage
    IHME GBD                        cause-specific vision-loss estimates by country
    Human Protein Atlas             retina cell-type expression, for checking whether
                                    the hub genes are expressed in the relevant tissue

This probe checks reachability and, where an API exists, whether it returns real
records.  Nothing is downloaded for storage.
"""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (research)"}


def get(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


print("=" * 96)
print("1. WHO Global Health Observatory - is the API reachable?")
print("=" * 96)
WHO_INDICATORS = "https://ghoapi.azureedge.net/api/Indicator"
try:
    st, ct, body = get(WHO_INDICATORS, timeout=90)
    print(f"  {st}  {ct}  {len(body):,} bytes")
    j = json.loads(body)
    rows = j.get("value", [])
    print(f"  indicators returned: {len(rows):,}")
    tb = [r for r in rows
          if any(k in (r.get("IndicatorName") or "").lower()
                 for k in ("tuberculosis", "tb "))]
    print(f"  indicators mentioning tuberculosis: {len(tb)}")
    for r in tb[:14]:
        print(f"      {r.get('IndicatorCode','?'):24s} "
              f"{(r.get('IndicatorName') or '')[:74]}")
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED {type(exc).__name__}: {str(exc)[:140]}")

print()
print("=" * 96)
print("2. Can it return country-level values for one tuberculosis indicator?")
print("=" * 96)
for code in ("MDG_0000000020", "TB_incidence", "TB_c_newinc", "TB_epi_inc_100k"):
    url = f"https://ghoapi.azureedge.net/api/{code}?$top=5"
    try:
        st, ct, body = get(url, timeout=60)
        j = json.loads(body)
        rows = j.get("value", [])
        note = j.get("message", "")
        print(f"  {code:22s} {st}  rows={len(rows)}  {str(note)[:60]}")
        if rows:
            r = rows[0]
            keys = [k for k in r if k in ("SpatialDim", "TimeDim", "NumericValue",
                                          "Dim1", "Value")]
            print(f"      sample: { {k: r[k] for k in keys} }")
            break
    except urllib.error.HTTPError as exc:
        print(f"  {code:22s} HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {code:22s} {type(exc).__name__}")

print()
print("=" * 96)
print("3. Human Protein Atlas - retina expression data")
print("=" * 96)
HPA_URLS = [
    ("HPA download index", "https://www.proteinatlas.org/about/download"),
    ("HPA single cell (rna_single_cell_type.tsv.zip)",
     "https://www.proteinatlas.org/download/tsv/rna_single_cell_type.tsv.zip"),
    ("HPA tissue (rna_tissue_consensus.tsv.zip)",
     "https://www.proteinatlas.org/download/tsv/rna_tissue_consensus.tsv.zip"),
]
for label, url in HPA_URLS:
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            size = r.headers.get("Content-Length")
            mb = int(size) / 1e6 if size else 0
            print(f"  {label:46s} {r.status}  {mb:>8.1f} MB")
    except urllib.error.HTTPError as exc:
        print(f"  {label:46s} HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label:46s} {type(exc).__name__}")

print()
print("=" * 96)
print("4. IHME GBD / GHDx")
print("=" * 96)
for label, url in (
        ("GHDx results (GBD vision loss)",
         "https://ghdx.healthdata.org/gbd-results-tool"),
        ("IHME data catalogue", "https://ghdx.healthdata.org/"),
        ("GBD API (gbd-results)", "https://vizhub.healthdata.org/gbd-results/")):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            print(f"  {label:40s} {r.status}")
    except urllib.error.HTTPError as exc:
        print(f"  {label:40s} HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label:40s} {type(exc).__name__}")

print()
print("=" * 96)
print("Reading")
print("=" * 96)
print("""  What matters is not that a portal loads, but that it exposes machine-readable
  values by country and year.  The WHO GHO API does, and tuberculosis indicators are
  what would let an ethambutol-treated population be estimated: ethambutol is a
  standard component of first-line therapy, so treated patients scale with notified
  tuberculosis cases, which are published annually for every country.  Dividing FAERS
  reports by that estimate gives a report rate per treated patient - the quantity
  every disproportionality study lacks.""")
