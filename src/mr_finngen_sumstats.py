# -*- coding: utf-8 -*-
"""
Step 6b - Can FinnGen summary statistics actually be downloaded and queried?

A two-sample MR needs per-SNP effect sizes, not the phenotype manifest.  FinnGen
publishes tabix-indexed per-phenotype summary statistics; this script checks the
public bucket, downloads one endpoint, and reports whether the columns required
for MR (beta, se, effect allele, other allele, EAF) are present.
"""
from __future__ import annotations

import gzip
import io
import json
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RAW = ROOT / "data" / "raw" / "finngen"
RAW.mkdir(parents=True, exist_ok=True)
DERIVED.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

CANDIDATE_BUCKETS = [
    "https://storage.googleapis.com/finngen-public-data-r12",
    "https://storage.googleapis.com/finngen-public-data-r11",
    "https://finngen-public-data-r12.s3.amazonaws.com",
    "https://r12.finngen.fi",
]

GB = "https://storage.googleapis.com"


def get(url: str, timeout: int = 90, tries: int = 3, head: bool = False):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA, method="HEAD" if head else "GET")
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                return r.status, dict(r.headers), (b"" if head else r.read())
        except urllib.error.HTTPError as exc:
            return exc.code, {}, b""
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (a + 1))
    return None, {}, str(last).encode()


def main() -> None:
    print("=" * 78)
    print("STEP 6b  FinnGen summary-statistics availability")
    print("=" * 78)

    # 1. does the bucket list objects?
    for base in CANDIDATE_BUCKETS[:3]:
        url = f"{base}?list-type=2&max-keys=5"
        st, hdr, body = get(url, timeout=60)
        ok = st == 200 and b"<ListBucketResult" in body
        print(f"[{st}] list {base}: {'OK' if ok else 'no'}"
              f"{' :: ' + body[:160].decode('utf-8', 'replace') if not ok else ''}")
        if ok:
            print("     keys:", [l for l in body.decode("utf-8", "replace").split("<Key>")[1:6]])

    # 2. resolve a manifest for one endpoint from the phenotype API
    man = DERIVED / "finngen_R12_phenos.json"
    if not man.exists():
        st, hdr, body = get("https://r12.finngen.fi/api/phenos", timeout=240)
        man.write_bytes(body)
    phenos = json.loads(man.read_text(encoding="utf-8"))
    print(f"\n[manifest] {len(phenos)} R12 endpoints")
    sample = None
    for p in phenos:
        af = p.get("assoc_files") or []
        if af and p.get("phenocode") in ("H7_OPTNEURITIS", "H7_OPTATROPHY",
                                         "H7_OPTNERVE", "H7_BLINDANDVISIMPAIRMENT"):
            sample = p
            break
    if not sample:
        for p in phenos:
            if p.get("assoc_files"):
                sample = p
                break
    print(f"[manifest] sample endpoint: {sample['phenocode']} "
          f"({sample.get('phenostring')}) cases={sample.get('num_cases')}")
    print(f"[manifest] assoc_files: {sample['assoc_files'][:3]}")

    # 3. try to download the summary statistics for that endpoint
    target = None
    for af in sample["assoc_files"]:
        for base in ["https://storage.googleapis.com/finngen-public-data-r12",
                     "https://finngen-public-data-r12.s3.amazonaws.com"]:
            for cand in (af, af.replace("/cromwell_root/pheweb/generated-by-pheweb/", ""),
                         af.lstrip("/")):
                if not cand:
                    continue
                url = f"{base}/{cand.lstrip('/')}"
                st, hdr, body = get(url, timeout=120, head=True)
                if st == 200:
                    target = url
                    print(f"\n[sumstat] HEAD 200 -> {url}")
                    print(f"          content-length={hdr.get('Content-Length')}")
                    break
            if target:
                break
        if target:
            break

    if not target:
        print("\n[sumstat] no downloadable object found with the probed URL patterns")
        print("          -> MR will need either an OpenGWAS token or a user-supplied")
        print("             summary-statistics file")
        return

    # 4. download the first few MB and inspect the schema
    print("[sumstat] downloading the first ~4 MB to inspect columns ...")
    req = urllib.request.Request(target, headers={**UA, "Range": "bytes=0-4194303"})
    with urllib.request.urlopen(req, timeout=300, context=CTX) as r:
        blob = r.read()
    local = RAW / f"{sample['phenocode']}.head.tsv.gz"
    local.write_bytes(blob)
    text = gzip.decompress(blob).decode("utf-8", "replace")
    lines = text.splitlines()
    lines = [l for l in lines if l and not l.startswith("##")]
    print(f"[sumstat] header: {lines[0]}")
    print(f"[sumstat] first data row: {lines[1] if len(lines) > 1 else 'n/a'}")
    df = pd.read_csv(io.StringIO("\n".join(lines[:5000])), sep="\t")
    print(f"[sumstat] parsed {len(df)} variants x {len(df.columns)} columns")
    need = ["beta", "sebeta", "alt", "ref", "af_alt", "pval"]
    print(f"[sumstat] MR-ready columns present: "
          f"{[c for c in need if c in df.columns]} "
          f"missing={[c for c in need if c not in df.columns]}")
    (DERIVED / "finngen_sumstat_schema.json").write_text(json.dumps({
        "url": target, "phenocode": sample["phenocode"],
        "columns": list(df.columns), "n_rows_probe": len(df),
        "mr_ready": all(c in df.columns for c in ("beta", "sebeta", "alt", "ref")),
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
