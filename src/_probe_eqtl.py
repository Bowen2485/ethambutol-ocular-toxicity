# -*- coding: utf-8 -*-
"""Check availability of cis-eQTL / pQTL resources for instrument construction."""
from __future__ import annotations

import ssl
import urllib.error
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

URLS = [
    ("eQTLGen probe-level",
     "https://molgenis26.gcc.rug.nl/downloads/eqtlgen/cis-eqtl/"
     "2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz"),
    ("eQTLGen significant",
     "https://molgenis26.gcc.rug.nl/downloads/eqtlgen/cis-eqtl/"
     "2019-12-11-cis-eQTLsFDR-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz"),
    ("eQTLGen site", "https://eqtlgen.org/"),
    ("EBI eQTL Catalogue datasets", "https://www.ebi.ac.uk/eqtl/api/v2/datasets/"),
    ("EBI eQTL Catalogue studies", "https://www.ebi.ac.uk/eqtl/api/v2/studies/"),
    ("GTEx portal api", "https://gtexportal.org/api/v2/dataset/variant"),
    ("OpenGWAS api root", "https://api.opengwas.io/api/"),
    ("MR-Base IEU", "https://gwas-api.mrcieu.ac.uk/"),
    ("FinnGen R12 pheno", "https://r12.finngen.fi/api/pheno/H7_OPTNEURITIS"),
]

for name, url in URLS:
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            length = r.headers.get("Content-Length")
            ctype = r.headers.get("Content-Type", "")[:40]
            print(f"[{r.status}] {name:28s} len={length} ct={ctype}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {name:28s} {url[:80]}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name:28s} {type(e).__name__} {str(e)[:70]}")
