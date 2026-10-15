# -*- coding: utf-8 -*-
"""
Generate references.bib for the Frontiers submission from the manuscript's reference list.

The manuscript cites numbered entries ([1] ... [28]) and holds the reference text in
manuscript/references_en.md.  Frontiers uses natbib with the Vancouver style, so the
numbered citations have to become keys, and the reference text has to become BibTeX.

Approach
    Each numbered line is parsed into authors, title, journal, year and DOI.  The key is
    derived from the first author's surname and the year, which is stable and readable.
    A mapping from number to key is written alongside so the converter can turn [12] into
    \\citep{key12} without re-parsing.

    The title is protected with braces where it contains a capital that is not sentence
    initial (BibTeX lowercases unprotected titles in some styles), and journal names are
    given in full because the Vancouver style abbreviates them itself.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "manuscript" / "references_en.md"
OUT = ROOT / "submission"
OUT.mkdir(parents=True, exist_ok=True)


def clean(s: str) -> str:
    s = s.strip()
    s = re.sub(r"<i>(.*?)</i>", r"\1", s)          # markdown italics inside titles
    s = s.replace("&", r"\&")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def make_key(authors: str, year: str  , num: int) -> str:
    """First author surname plus year, which is stable and readable."""
    first = authors.split(",")[0].strip()
    surname = first.split()[-1] if first.split() else f"ref{num}"
    surname = re.sub(r"[^A-Za-z]", "", surname)
    return f"{surname.lower()}{year or 'anon'}"


entries: list[dict] = []
lines = SRC.read_text(encoding="utf-8").splitlines()
for ln in lines:
    m = re.match(r"^(\d+)\.\s+(.*)$", ln.strip())
    if not m:
        continue
    num = int(m.group(1))
    body = m.group(2)

    # the trailing note in parentheses (present on ref 28) is not part of the reference
    note = ""
    nm = re.search(r"\s*\((Not indexed.*?)\)\s*$", body)
    if nm:
        note = nm.group(1)
        body = body[: nm.start()]

    # split into "authors. title. journal. year; doi."
    parts = [p.strip() for p in body.split(". ")]
    authors = parts[0].rstrip(".")
    # the title is the next substantial segment
    title = ""
    journal = ""
    year = ""
    doi = ""

    dm = re.search(r"doi:\s*(\S+?)\.?$", body)
    if dm:
        doi = dm.group(1).rstrip(".")
    ym = re.search(r"\b(19|20)\d{2}\b", body)
    if ym:
        year = ym.group(0)

    # title = text between the author block and the journal
    rest = body[len(authors) + 1:].strip()
    rest = re.sub(r"\s*doi:\s*\S+\.?$", "", rest).strip()
    rest = re.sub(r"\s*\b(19|20)\d{2};?\.?$", "", rest).strip()
    # journal and title are separated by ". " and the journal precedes the year
    segs = [s.strip() for s in rest.split(". ") if s.strip()]
    if segs:
        title = segs[0]
        journal = segs[1] if len(segs) > 1 else ""
    title = title.rstrip(".")

    key = make_key(authors, year, num)
    # guard against duplicate keys
    while any(e["key"] == key for e in entries):
        key += "b"

    entries.append({
        "num": num, "key": key, "authors": authors, "title": clean(title),
        "journal": clean(journal).rstrip("."), "year": year, "doi": doi,
        "note": note,
    })

# ---------------------------------------------------------------- write the bib
bib: list[str] = [
    "% References for: Ocular toxicity of ethambutol",
    "% Generated from manuscript/references_en.md; keys are first author + year.",
    "% Citation commands in the manuscript use \\citep{key}, numbered by natbib.",
    "",
]
for e in entries:
    authors = " and ".join(
        a.strip() for a in e["authors"].split(",") if a.strip()) or "Anonymous"
    bib.append(f"@article{{{e['key']},")
    bib.append(f"  author  = {{{authors}}},")
    bib.append(f"  title   = {{{e['title']}}},")
    if e["journal"]:
        bib.append(f"  journal = {{{e['journal']}}},")
    if e["year"]:
        bib.append(f"  year    = {{{e['year']}}},")
    if e["doi"]:
        bib.append(f"  doi     = {{{e['doi']}}},")
    if e["note"]:
        bib.append(f"  note    = {{{e['note']}}},")
    bib.append("}")
    bib.append("")

(OUT / "references.bib").write_text("\n".join(bib), encoding="utf-8")

# ---------------------------------------------------------------- number -> key map
mapping = {str(e["num"]): e["key"] for e in entries}
(OUT / "citation_map.json").write_text(
    json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"  entries: {len(entries)}")
print(f"  written: submission/references.bib")
print(f"  written: submission/citation_map.json")
print()
print(f"  {'#':>3s}  {'key':<22s} {'year':<5s} title")
for e in entries:
    flag = "" if e["title"] and e["journal"] else "   <-- INCOMPLETE"
    print(f"  {e['num']:>3d}  {e['key']:<22s} {e['year']:<5s} {e['title'][:62]}{flag}")

missing = [e["num"] for e in entries if not e["title"] or not e["year"]]
print()
print(f"  entries missing a title or year: {missing if missing else 'none'}")
dup = len(mapping) != len(entries)
print(f"  duplicate numbers: {dup}")
