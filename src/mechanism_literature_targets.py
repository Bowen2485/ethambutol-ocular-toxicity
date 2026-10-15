# -*- coding: utf-8 -*-
"""
Step 3b - Identify human genes with real experimental evidence of interacting with
or being affected by ethambutol, by mining the Europe PMC full-text corpus.

Rationale: Open Targets records no human mechanism for ethambutol (the drug
inhibits mycobacterial arabinosyltransferases), so the human gene set must be
built from experimental literature rather than from a target database.

Output: data/derived/literature_human_targets.csv  (gene, n_papers, example_pmid)
        results/mechanism_literature_targets.csv
"""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
RAW = ROOT / "data" / "raw"
for p in (DERIVED, RESULTS, RAW):
    p.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

QUERIES = [
    "ethambutol AND (retinal ganglion cell OR optic nerve OR retina)",
    "ethambutol AND (mitochondrial OR oxidative stress OR ferroptosis OR apoptosis)",
    "ethambutol AND (zinc OR copper OR chelation OR lysosome)",
    "ethambutol AND (autophagy OR mTOR OR AMPK OR Nrf2)",
    "ethambutol AND (BDNF OR neurotrophin OR AKT OR MAPK OR PI3K)",
    "ethambutol AND (glutamate OR excitotoxicity OR NMDA)",
    "ethambutol AND (OPA1 OR LHON OR mitochondrial DNA)",
    "ethambutol toxicity mechanism",
]

# Human gene symbols are extracted only from a curated, unambiguous whitelist of
# HGNC symbols that repeatedly appear in this literature, so that acronym noise
# (e.g. "ROS", "TB", "MOUSE") can never enter the network.
GENE_WHITELIST = """
OPA1 MFN1 MFN2 OPA3 DNM1L FIS1 YME1L1 SPG7 AFG3L2 IMMT CHCHD3 SLC25A4 SLC25A5
POLG POLG2 TWNK SSBP1 MTERF1 TFAM NRF1 NFE2L2 KEAP1 HMOX1 NQO1 GCLM GCLC TXN TXN2
TXNIP PRDX1 PRDX2 PRDX3 PRDX4 PRDX5 PRDX6 CAT SOD1 SOD2 SOD3 GPX1 GPX3 GPX4 GPX7
GSS GSR NOS1 NOS2 NOS3 NOX1 NOX2 NOX4 CYBB DUOX1 MPO XDH
SDHA SDHB SDHC SDHD SDHAF2 FH IDH1 IDH2 IDH3A OGDH DLD DLST PDHA1 PDHB PDHX CS
ACO2 ACO1 ISCU FECH FXN ABCB7 GLRX5 NFS1 LYRM4
CASP3 CASP7 CASP8 CASP9 CASP12 BAX BAK1 BAD BID BBC3 PMAIP1 BCL2 BCL2L1 BCL2L11
MCL1 XIAP BIRC2 BIRC3 APAF1 CYCS DIABLO AIFM1 ENDOG PARP1 TP53 TP53BP2 MDM2 CDKN1A
AKT1 AKT2 AKT3 PIK3CA PIK3CB PIK3CD PIK3R1 PTEN MTOR MLST8 RPTOR RICTOR TSC1 TSC2
RHEB RPS6KB1 RPS6 EIF4EBP1 PRKAA1 PRKAA2 PRKAB1 STK11 CAB39 ULK1 ULK2 ATG3 ATG4B
ATG5 ATG7 ATG9A ATG10 ATG12 ATG13 ATG14 ATG16L1 BECN1 PIK3C3 UVRAG AMBRA1 RB1CC1
MAP1LC3A MAP1LC3B GABARAP GABARAPL1 SQSTM1 NBR1 CALCOCO2 OPTN TBK1 NDP52
MAPK1 MAPK3 MAPK8 MAPK9 MAPK10 MAPK14 MAP2K1 MAP2K2 MAP2K3 MAP2K4 MAP3K5 MAP3K7
MAPKAPK2 JUN FOS MYC EGR1 ATF2 ATF4 ATF6 HSPA5 HSPA8 HSPB1 HSP90AA1 HSP90AB1
HSPD1 HSPE1 DNAJB1 DDIT3 XBP1 ERN1 EIF2AK3
BDNF NGF NGFR NTRK1 NTRK2 NTRK3 GDNF ARTN PSPN NTF3 NTF4 SORT1
GRIN1 GRIN2A GRIN2B GRIN2C GRIN2D GRIA1 GRIA2 GRIA3 GRIA4 GRM1 GRM5
SLC1A1 SLC1A2 SLC1A3 SLC1A6 SLC17A6 SLC17A7 SLC17A8 GAD1 GAD2 GLS GLS2 GLUL
SLC7A11 SLC3A2 SLC6A9 SLC38A1 SLC38A2 SLC38A3 SLC38A5
ACSL1 ACSL3 ACSL4 ACSL5 LPCAT3 ALOX15 ALOX12 ALOX5 ALOXE3 FSP1 AIFM2
ATP7A ATP7B SLC31A1 SLC31A2 SLC30A1 SLC30A2 SLC30A3 SLC30A4 SLC30A5 SLC30A6 SLC30A7
SLC30A8 SLC30A9 SLC30A10 SLC39A1 SLC39A2 SLC39A3 SLC39A4 SLC39A5 SLC39A6 SLC39A7
SLC39A8 SLC39A9 SLC39A10 SLC39A11 SLC39A12 SLC39A13 SLC39A14 MT1A MT1B MT1E MT1F
MT1G MT1H MT1M MT1X MT2A MT3 MT4 ATOX1 CCS COX17 COX11 SCO1 SCO2 COMMD1 CP
MCOLN1 MCOLN2 MCOLN3 TPCN1 TPCN2 LAMP1 LAMP2 LAMP3 CTNS CTSD CTSB CTSL MAP1S
TFEB TFE3 MITF ZKSCAN3 ATP6V0A1 ATP6V1A
SLC22A1 SLC22A2 SLC22A3 SLC22A4 SLC22A5 SLC22A6 SLC22A8 SLC22A11 ABCB1 ABCG2 ABCC1
ABCC2 ABCC3 ABCC4 ABCC5 SLC15A1 SLC15A2 SLC47A1 SLC47A2
BAX BCL2 CASP3 NFE2L2 HMOX1 RBPMS POU4F2 POU4F3 ATOH7 SNCG SNCB
THY1 CDKN1B SOX2 PAX6 OTX2 SIX3 RAX VSX2 CRX NRL NR2E3 RHO
MYOC OPTN WDR36 ASB10 TBK1 CYP1B1 LTBP2 FOXC1 PITX2
VEGFA VEGFB VEGFC KDR FLT1 FLT4 HIF1A EPAS1 ARNT EGLN1 EGLN2 EGLN3
TNF IL1B IL6 IL10 CXCL8 CCL2 NFKB1 NFKB2 RELA RELB NFKBIA TLR4 MYD88
STAT1 STAT3 JAK1 JAK2 TYK2 IFNG IFNGR1 IFNGR2
SIRT1 SIRT2 SIRT3 SIRT4 SIRT5 SIRT6 SIRT7 PPARGC1A PPARA PPARD PPARG
ACHE BCHE MAOA MAOB CYP1A2 CYP2E1 CYP3A4 CYP2D6 CYP2C9 CYP2C19 NAT1 NAT2 GSTM1
GSTT1 GSTP1 NQO2 EPHX1 UGT1A1 UGT2B7
"""

GENES = sorted(set(GENE_WHITELIST.split()))


def fetch_epmc(query: str, pages: int = 6, pagesize: int = 100) -> list[dict]:
    out: list[dict] = []
    cursor = "*"
    for _ in range(pages):
        url = (f"{EPMC}/search?query={urllib.parse.quote(query)}"
               f"&format=json&pageSize={pagesize}&resultType=core&cursorMark={cursor}")
        last = None
        for a in range(5):
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
                    d = json.loads(r.read().decode("utf-8", "replace"))
                break
            except Exception as exc:  # noqa: BLE001
                last = exc
                time.sleep(2 * (a + 1))
        else:
            print(f"  [fail] {query[:60]}: {last}")
            break
        res = d.get("resultList", {}).get("result", [])
        out.extend(res)
        cursor = d.get("nextCursorMark")
        if not cursor or not res:
            break
        time.sleep(0.34)
    return out


def main() -> None:
    print(f"[setup] gene whitelist size = {len(GENES)}")
    seen: dict[str, dict] = {}
    for q in QUERIES:
        recs = fetch_epmc(q)
        print(f"[epmc] {q[:62]:64s} -> {len(recs)} records")
        for r in recs:
            pid = r.get("pmid") or r.get("id")
            if pid and pid not in seen:
                seen[pid] = r
        time.sleep(0.34)
    print(f"[epmc] unique records: {len(seen)}")

    gene_hits: Counter = Counter()
    gene_pmids: dict[str, list[str]] = defaultdict(list)
    gene_ctx: dict[str, str] = {}
    pat = {g: re.compile(rf"(?<![A-Za-z0-9-]){re.escape(g)}(?![A-Za-z0-9-])")
           for g in GENES}

    for pid, rec in seen.items():
        text_parts = [rec.get("title") or "", rec.get("abstractText") or "",
                      " ".join(k.get("keyword", "") for k in
                               (rec.get("keywordList", {}) or {}).get("keyword", [])
                               if isinstance(k, dict))]
        text = " ".join(text_parts)
        if not text.strip():
            continue
        for g, rx in pat.items():
            if rx.search(text):
                gene_hits[g] += 1
                if len(gene_pmids[g]) < 25:
                    gene_pmids[g].append(str(pid))
                    if g not in gene_ctx:
                        gene_ctx[g] = (rec.get("title") or "")[:180]

    rows = [{"gene": g, "n_papers": n, "n_pmids": len(gene_pmids[g]),
             "example_pmids": ";".join(gene_pmids[g][:8]),
             "example_title": gene_ctx.get(g, "")}
            for g, n in gene_hits.most_common()]
    df = pd.DataFrame(rows)
    df.to_csv(DERIVED / "literature_human_targets.csv", index=False,
              encoding="utf-8-sig")
    df.to_csv(RESULTS / "mechanism_literature_targets.csv", index=False,
              encoding="utf-8-sig")
    print(f"\n[result] genes with >=1 co-mention: {len(df)}")
    print("\ntop 50 by paper count:")
    print(df.head(50)[["gene", "n_papers", "example_title"]]
          .to_string(index=False, max_colwidth=70))
    print(f"\n-> {DERIVED / 'literature_human_targets.csv'}")


if __name__ == "__main__":
    main()
