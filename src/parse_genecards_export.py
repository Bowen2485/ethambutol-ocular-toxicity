# -*- coding: utf-8 -*-
"""
Parse the GeneCards disorder exports and see what the two available criteria say.

The export has six columns - Disorder, Short Description, Categories, Inheritance, Evidence,
References - with four lines of copyright notice above the header.  Two fields can carry an
eye signal and they are not the same measure:

    the Disorder name, matched against ocular stems, which is the criterion already applied
    to the DisGeNET data and is therefore the one that makes the two comparable;

    the Categories column, which lists classes such as "Eye diseases" and is assigned by
    GeneCards rather than by me.

Checking both matters because the Categories column produces false positives.  In the
screenshots the BCL2 page tags Lymphoma as "Eye diseases", and the SDHB page tags
Dyskeratosis Congenita and Familial Adenomatous Polyposis 1 the same way; none of those is an
eye disease.  If the category were trusted, the hub set would look more ocular than it is.
The disorder-name criterion is reported as primary for that reason, and the category is
reported alongside so the divergence is visible rather than hidden.
"""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path(r"C:\Users\20200\Downloads")
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

#: the same stems used on the DisGeNET data
EYE_RE = ("retin", "optic", "macula", "ocular", "eye", "glaucom", "uveit", "choroid",
          "conjunctiv", "cornea", "leber", "stargardt", "cone-rod", "photoreceptor",
          "visual", "cataract", "kerat", "amblyop", "nyctalop", "colour blind",
          "color blind", "achromatops", "blind")
#: names that match a stem while naming something else, carried from the DisGeNET audit
SUSPECT = ("keratosis", "dyskeratosis", "adenomatous polyposis")

FILES = {"AKT1": None, "TP53": None, "NFE2L2": None}
for sym in FILES:
    cand = DOWNLOADS / f"GeneCards - disorders for the gene {sym}.csv"
    if cand.exists():
        FILES[sym] = cand


def parse(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    hdr = next((i for i, l in enumerate(lines) if l.startswith("Disorder,")), None)
    if hdr is None:
        return []
    rows = list(csv.DictReader(io.StringIO("\n".join(lines[hdr:]))))
    return [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in rows]


print("=" * 100)
print("1. What was parsed")
print("=" * 100)
parsed: dict[str, list[dict]] = {}
for sym, path in FILES.items():
    if path is None:
        print(f"  {sym}: file not found")
        continue
    rows = parse(path)
    parsed[sym] = rows
    print(f"  {sym:8s} {len(rows):>4d} disorders   columns: "
          f"{list(rows[0].keys()) if rows else '[]'}")

print()
print("=" * 100)
print("2. Eye signal by the two criteria")
print("=" * 100)
print(f"  {'gene':8s} {'n':>5s} {'by disorder name':>18s} {'by Categories column':>22s}")
summary = {}
for sym, rows in parsed.items():
    by_name = [r for r in rows if any(k in r.get("Disorder", "").lower()
                                      for k in EYE_RE)]
    clean = [r for r in by_name
             if not any(s in r.get("Disorder", "").lower() for s in SUSPECT)]
    by_cat = [r for r in rows if "eye disease" in r.get("Categories", "").lower()]
    summary[sym] = {
        "n_disorders": len(rows),
        "by_name": [r["Disorder"] for r in by_name],
        "by_name_clean": [r["Disorder"] for r in clean],
        "by_category": [r["Disorder"] for r in by_cat],
    }
    print(f"  {sym:8s} {len(rows):>5d} {len(by_name):>18d} {len(by_cat):>22d}")

print()
for sym, s in summary.items():
    print(f"  {sym}:")
    if s["by_name_clean"]:
        print(f"      by name, after removing artefacts : "
              f"{', '.join(s['by_name_clean'][:6])}")
    else:
        print(f"      by name, after removing artefacts : none")
    removed = [d for d in s["by_name"] if d not in s["by_name_clean"]]
    if removed:
        print(f"      removed as artefacts              : {', '.join(removed)}")
    if s["by_category"]:
        print(f"      tagged 'Eye diseases' by GeneCards : "
              f"{', '.join(s['by_category'][:6])}")
    else:
        print(f"      tagged 'Eye diseases' by GeneCards : none")

print()
print("=" * 100)
print("3. Where the two criteria disagree, which is the reason both are reported")
print("=" * 100)
for sym, s in summary.items():
    a, b = set(s["by_name_clean"]), set(s["by_category"])
    only_name = a - b
    only_cat = b - a
    if only_name or only_cat:
        print(f"\n  {sym}")
        if only_name:
            print(f"      named as ocular but not tagged : {', '.join(sorted(only_name))}")
        if only_cat:
            print(f"      tagged but not named as ocular : {', '.join(sorted(only_cat))}")
if not any((set(s["by_name_clean"]) ^ set(s["by_category"]))
           for s in summary.values()):
    print("  the two criteria agree on every gene parsed")

(OUT / "genecards_parsed.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

print()
print("=" * 100)
print("4. What is still needed for a test")
print("=" * 100)
print(f"""  Parsed so far: {', '.join(parsed) if parsed else 'none'} - three hub genes.
  A test needs both groups: hub genes and the control set.  Twelve hub genes have been seen
  in screenshots, but screenshots capture what is on screen and the export is complete, so
  the export is what should be used.

  Requesting the export for the remaining genes is the reliable route: the same CSV download
  from each gene's Disorders page, which is the file that was already produced three times
  here.  With hub and control exports alike, the Fisher test follows immediately.""")

print(f"\n  written: {(OUT / 'genecards_parsed.json').relative_to(ROOT)}")
