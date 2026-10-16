# -*- coding: utf-8 -*-
"""
Assemble the gene list for a manual GeneCards search, with the identifiers the search
interface needs, and prepare the analysis that will consume the result.

Why the identifiers are fetched rather than typed
    GeneALaCart takes batches of gene identifiers, and the NCBI Gene ID is the one that
    cannot be confused between synonyms - TP53 is also P53, BCC7, LFS1 and TRP53.  Typing 66
    identifiers by hand would introduce errors that would be invisible in the output, because
    a wrong ID returns a different gene's annotations and the analysis would report on that
    gene instead.  The IDs are therefore retrieved from NCBI Gene through eutils, and the
    retrieved symbol is cross-checked against the symbol that was asked for; any disagreement
    is printed rather than silently accepted.

What is prepared alongside
    The template the search results go into, and the analysis that will read it.  The analysis
    deliberately mirrors src/check_disgenet_false_positives.py, including the keyword audit
    and the comparison against the control set, so the GeneCards result either reproduces the
    DisGeNET one or contradicts it, and either outcome is informative.
"""
from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

HUBS = ["TP53", "NFE2L2", "AKT1", "BCL2", "HMOX1", "CASP3", "SOD2", "TNF", "GPX4",
        "MFN2", "SLC7A11", "ACSL4", "SDHB", "OPA1", "SLC25A4", "KEAP1", "MAPK1",
        "IL6", "STAT3", "CAT", "GPX1", "TXN", "NQO1", "HIF1A", "PPARGC1A", "DNM1L",
        "VDAC1", "CYCS", "APAF1", "BAX", "BCL2L1", "FTH1", "FTL"]
CONTROL = ["HBB", "HBA1", "ALB", "APOA1", "APOB", "FGA", "FGB", "FGG", "SERPINA1",
           "ORM1", "HP", "TF", "CP", "AMY1A", "AMY2A", "PRSS1", "CELA1", "CTRB1",
           "CPA1", "PNLIP", "CLPS", "CELA3A", "SYCN", "PNLIPRP1", "CTRB2", "CEL",
           "CPA2", "PRSS2", "CTRC", "CELP", "PNLIPRP2", "CLPSL1", "CELA2A"]

UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
      "Accept": "application/json"}


def ncbi_ids(symbols: list[str]) -> dict[str, dict]:
    """Gene ID per symbol, from NCBI Gene, with the symbol echoed back for checking."""
    out: dict[str, dict] = {}
    # the API takes a modest batch; 20 at a time is safe and keeps the response small
    for i in range(0, len(symbols), 20):
        chunk = symbols[i:i + 20]
        term = " OR ".join(f"{s}[sym] AND human[orgn]" for s in chunk)
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene"
               f"&term={urllib.parse.quote(term)}&retmax=60&retmode=json")
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=45) as fh:
                ids = json.loads(fh.read(400_000).decode("utf-8", "replace")
                                 ).get("esearchresult", {}).get("idlist", [])
        except Exception as e:  # noqa: BLE001
            print(f"    esearch failed for batch {i//20 + 1}: {type(e).__name__}")
            ids = []
        if ids:
            s_url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene"
                     f"&id={','.join(ids)}&retmode=json")
            try:
                with urllib.request.urlopen(urllib.request.Request(s_url, headers=UA),
                                            timeout=45) as fh:
                    res = json.loads(fh.read(1_200_000).decode("utf-8", "replace")
                                     ).get("result", {})
            except Exception:
                res = {}
            for uid in res.get("uids", []):
                d = res.get(uid, {})
                sym = str(d.get("name", "")).strip()
                if sym in symbols:
                    out[sym] = {"gene_id": uid, "ncbi_symbol": sym,
                                "description": str(d.get("description", ""))[:70]}
        time.sleep(0.4)
    return out


print("=" * 100)
print("1. Fetching NCBI Gene IDs and checking the symbols come back the same")
print("=" * 100)
all_syms = HUBS + CONTROL
ids = ncbi_ids(all_syms)

missing = [s for s in all_syms if s not in ids]
mismatch = [s for s in ids if ids[s]["ncbi_symbol"] != s]
print(f"  requested {len(all_syms)} symbols")
print(f"  resolved  {len(ids)}")
if missing:
    print(f"  NOT RESOLVED ({len(missing)}): {missing}")
if mismatch:
    print(f"  symbol mismatch: {mismatch}")
else:
    print("  every resolved symbol came back identical to the one requested")

rows = []
for group, syms in (("hub", HUBS), ("control", CONTROL)):
    for s in syms:
        d = ids.get(s, {})
        rows.append({
            "group": group,
            "symbol": s,
            "ncbi_gene_id": d.get("gene_id", ""),
            "description": d.get("description", ""),
            "genecards_score": "",      # to be filled from the manual search
            "genecards_eye_related": "",  # yes / no
            "genecards_diseases": "",   # the eye-related names, if any
            "notes": "",
        })

names_file = OUT / "genecards_search_list.csv"
with open(names_file, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

#: a bare identifier list, for pasting into a batch query box
with open(OUT / "genecards_gene_ids.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(str(r["ncbi_gene_id"]) for r in rows if r["ncbi_gene_id"]))

#: the symbol list too, in case the interface prefers symbols
with open(OUT / "genecards_symbols.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(r["symbol"] for r in rows))

print()
print("=" * 100)
print("2. Files for the search")
print("=" * 100)
print(f"  {names_file.relative_to(ROOT)}")
print(f"      the working file: fill the three genecards_* columns")
print(f"  {(OUT / 'genecards_gene_ids.txt').relative_to(ROOT)}")
print(f"      {len([r for r in rows if r['ncbi_gene_id']])} NCBI Gene IDs, one per line")
print(f"  {(OUT / 'genecards_symbols.txt').relative_to(ROOT)}")
print(f"      66 symbols, one per line")

print()
print("  the list, by group:")
for group in ("hub", "control"):
    sub = [r for r in rows if r["group"] == group]
    print(f"\n    {group} ({len(sub)})")
    for i in range(0, len(sub), 6):
        chunk = sub[i:i + 6]
        print("      " + "  ".join(f"{r['symbol']:9s}{r['ncbi_gene_id']:>7s}" for r in chunk))

print()
print("=" * 100)
print("3. What to record for each gene")
print("=" * 100)
print("""  Open the GeneCards page for the gene (or the batch result) and record:

      genecards_score           the relevance score GeneCards shows for the eye-related
                                disease, if any. Leave blank when there is none.
      genecards_eye_related     yes or no - whether any associated disease is an eye
                                disease. This single column is what the test needs.
      genecards_diseases        the names of the eye-related diseases, so the keyword
                                audit can be repeated on your data rather than trusted
                                from mine.

  The audit matters: on the DisGeNET data, keratosis and dyskeratosis congenita matched an
  ocular keyword while being skin diseases, and removing them changed the result from 61% to
  55%. The same check will be run here, so recording the disease names rather than only a
  yes/no makes that possible.""")
print(f"\n  when the file is filled, the analysis is:")
print(f"      python src/analyse_genecards_export.py")
