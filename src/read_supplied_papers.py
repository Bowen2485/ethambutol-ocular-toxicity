# -*- coding: utf-8 -*-
"""
Extract and identify the five papers supplied, then compare each against this manuscript.

Why identify before analysing
    The file names are first-author surnames, so one of them cannot be matched to a title from
    the metadata alone.  Each file is therefore read, its title and abstract recovered from the
    text, and the identifier taken from that rather than from the file name.

What the comparison looks for
    For each paper: the incidence or risk figures it reports, which of this manuscript's claims
    they bear on, whether the manuscript already cites it, and whether anything it reports
    contradicts a statement in the manuscript.  A contradiction is the outcome that matters,
    because it is the one that would draw a reviewer's question.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = Path(r"C:\Users\20200\Downloads\Documents")
TEXT = ROOT / "docs" / "literature_peers" / "text"
TEXT.mkdir(parents=True, exist_ok=True)

FILES = ["haitanuwong.pdf", "au2022.pdf", "au2008.pdf", "41905405.pdf", "42251932.pdf"]

EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
BIB = (ROOT / "submission" / "references.bib").read_text(encoding="utf-8")

try:
    import pypdf
except ImportError:
    raise SystemExit("pypdf is needed to read these")

records = []
for name in FILES:
    p = DOCS / name
    if not p.exists():
        print(f"  missing: {name}")
        continue
    txt_path = TEXT / (p.stem + "_text.txt")
    if txt_path.exists():
        text = txt_path.read_text(encoding="utf-8", errors="replace")
        src = "cached"
    else:
        try:
            r = pypdf.PdfReader(str(p))
            text = "\n".join((pg.extract_text() or "") for pg in r.pages)
            txt_path.write_text(text, encoding="utf-8")
            src = f"{len(r.pages)} pages"
        except Exception as e:  # noqa: BLE001
            print(f"  {name}: read failed, {type(e).__name__}: {str(e)[:70]}")
            continue
    text = re.sub(r"[ \t]+", " ", text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    #: title: the first substantial line, or the one before an abstract marker
    title = ""
    for l in lines[:40]:
        if 25 < len(l) < 190 and not re.match(r"^(doi|http|www|received|accepted|published)",
                                               l, re.I):
            title = l
            break
    doi = ""
    m = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)
    if m:
        doi = m.group(0).rstrip(".")
    pmid = ""
    m = re.search(r"PMID[:\s]*(\d{6,9})", text)
    if m:
        pmid = m.group(1)

    #: incidence and risk figures
    inc = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
    records.append({"file": name, "title": title, "doi": doi, "pmid": pmid,
                    "chars": len(text), "source": src,
                    "percents": sorted({x for x in inc}, key=lambda s: -float(s))[:12],
                    "text_path": str(txt_path.relative_to(ROOT))})
    print(f"\n  {name}  ({src}, {len(text):,} chars)")
    print(f"      title : {title[:108]}")
    print(f"      doi   : {doi or '(not found)'}   pmid: {pmid or '-'}")

print()
print("=" * 104)
print("Comparison with this manuscript")
print("=" * 104)
for r in records:
    text = Path(ROOT / r["text_path"]).read_text(encoding="utf-8", errors="replace")
    cited = bool(r["doi"]) and r["doi"].lower() in BIB.lower()
    print(f"\n  {r['file']}")
    print(f"      cited in references.bib : {'yes' if cited else 'NO'}")
    print(f"      incidence figures seen  : {', '.join(r['percents'][:8])}")

    #: statements that bear on claims this manuscript makes
    PROBES = {
        "regimen / co-prescription": r"isoniazid|rifampicin|combination|concomitant",
        "renal function": r"renal|kidney|creatinine|haemodialysis|hemodialysis",
        "daily dose": r"daily dose|mg/kg|dosage",
        "cumulative dose / duration": r"cumulative dose|duration of (?:therapy|treatment)",
        "age and sex": r"\bage\b.{0,40}\bsex\b|\bsex\b.{0,40}\bage\b|female|male",
        "diabetes": r"diabet",
        "reversibility / outcome": r"recover|reversib|visual outcome|prognos",
        "MRC / reporting quality": r"under-?report|reporting|spontaneous",
    }
    for label, pat in PROBES.items():
        n = len(re.findall(pat, text, re.I))
        if n:
            print(f"          {label:28s} {n:>4d} mentions")

    #: a numeric value the manuscript states, to check for contradiction
    for key, stated in (("0.28", r"0\.28"), ("6.5", r"6\.5\s*%"), ("7.03", r"7\.03"),
                        ("2.6%", r"2\.6\s*%")):
        if re.search(stated, text):
            print(f"          reports {key}")

(ROOT / "results" / "supplied_papers.json").write_text(
    json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  {len(records)} papers read -> results/supplied_papers.json")
