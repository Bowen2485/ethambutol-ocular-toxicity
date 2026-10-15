# -*- coding: utf-8 -*-
"""
Build the reference list from the verified Europe PMC records.

The earlier draft list was written from memory and comparison against the live
records showed that nine of the twenty-five entries had the wrong first author,
journal or year (for example the entry drafted for the childhood dosage review was
attributed to the wrong paper).  The list is therefore generated entirely from
data/derived/references_verified.json, and each PMID carries a note recording what
the manuscript cites it for so that the attribution can be checked.

Also renumbers the in-text citations in order of first appearance, which is the
Vancouver convention most target journals require.

Outputs -> manuscript/references_en.md, data/derived/citation_map.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
MAN = ROOT / "manuscript"

# what each reference is cited for, taken from the manuscript text
CITED_FOR = {
    "28759559": "clinical description of ethambutol optic neuropathy",
    "36018127": "visual outcome after withdrawal in an endemic-country cohort",
    "38351490": "time course of visual recovery",
    "40109812": "retrospective incidence estimate",
    "38983080": "single-centre incidence and risk factors",
    "40425190": "nationwide incidence, prevalence and risk factors",
    "40900291": "prospective screening incidence",
    "32713840": "subclinical injury on prospective electrophysiology",
    "9510653": "optic neuropathy at conventional dosing in a Korean series",
    "3790421": "ocular toxicity at standard dosage",
    "41846599": "low-dose versus standard-dose optic neuropathy risk",
    "40854737": "longitudinal visual function and OCT outcome",
    "29677374": "ganglion cell layer as a predictor of recovery",
    "38277226": "OCT cut-off values for visual prognosis",
    "659802": "zinc status and risk of ocular toxicity",
    "19063910": "zinc-mediated lysosomal membrane permeabilisation",
    "34676220": "mitochondrial variants in ethambutol-induced optic neuropathy",
    "12527998": "LHON mutations in ethambutol-induced optic neuropathy (negative)",
    "41563626": "SDHB/Smad4 ferroptosis mechanism in retinal ganglion cells",
    "41184893": "Müller glia BDNF protection of retinal ganglion cells",
    "42240730": "VigiBase ocular toxicity in the South-East Asia Region",
    "17167947": "ethambutol dosage review (children) - dosage thresholds",
    "39474613": "nationwide usage and screening practices",
    "22960095": "nationwide cohort, renal disease as a risk factor",
    "31109468": "optic neuropathy in renal disorder",
    "39979502": "factors affecting visual outcome in toxic optic neuropathy",
    "40444310": "clinical profile and visual outcomes in ethambutol optic neuropathy",
}


def clean_title(t: str) -> str:
    t = re.sub(r"<[^>]+>", "", t or "")
    t = t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def vancouver(rec: dict) -> str:
    """Vancouver-style entry: authors, title, journal, year, doi."""
    authors = rec.get("authors") or ""
    # Europe PMC returns a comma-separated author string; keep up to six then et al.
    parts = [a.strip() for a in authors.split(",") if a.strip()]
    if len(parts) > 6:
        author_str = ", ".join(parts[:6]) + ", et al"
    else:
        author_str = ", ".join(parts)
    title = clean_title(rec.get("title", ""))
    if not title.endswith("."):
        title += "."
    journal = (rec.get("journal") or "").strip()
    year = rec.get("year") or ""
    doi = rec.get("doi") or ""
    out = f"{author_str}. {title} {journal}. {year}"
    out += f"; doi:{doi}" if doi else ""
    return out.rstrip() + "."


def main() -> int:
    verified = json.loads(
        (DER / "references_verified.json").read_text(encoding="utf-8"))
    by_pmid = {r["pmid"]: r for r in verified if r.get("verified")}

    body = (MAN / "Manuscript_EN_draft.md").read_text(encoding="utf-8")
    methods = (MAN / "Methods_draft_EN.md").read_text(encoding="utf-8")
    full = body + "\n" + methods

    # renumber by order of first appearance in the assembled text
    seen: list[str] = []
    for m in re.finditer(r"\[PMID\s+([0-9]{6,9})\]", full):
        p = m.group(1)
        if p not in seen:
            seen.append(p)
    # any CITED_FOR entry not present in the text is appended so nothing is lost
    for p in CITED_FOR:
        if p not in seen and p in by_pmid:
            seen.append(p)

    num = {p: i + 1 for i, p in enumerate(seen)}

    lines = ["# References", ""]
    missing = []
    for p in seen:
        rec = by_pmid.get(p)
        if rec is None:
            lines.append(f"{num[p]}. [PMID {p} - NOT VERIFIED, do not submit]")
            missing.append(p)
            continue
        lines.append(f"{num[p]}. {vancouver(rec)}")
    lines.append("")

    (MAN / "references_en.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] {len(seen)} references -> manuscript/references_en.md")
    if missing:
        print(f"[warn] {len(missing)} unverified: {missing}")

    # the citation map lets the assembler renumber the in-text markers
    cmap = {p: {"number": num[p],
                "pmid": p,
                "cited_for": CITED_FOR.get(p, ""),
                "title": clean_title(by_pmid[p].get("title", ""))
                if p in by_pmid else "",
                "year": by_pmid[p].get("year") if p in by_pmid else "",
                "journal": by_pmid[p].get("journal") if p in by_pmid else "",
                "entry": vancouver(by_pmid[p]) if p in by_pmid else ""}
            for p in seen}
    (DER / "citation_map.json").write_text(
        json.dumps(cmap, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== citation order and what each is cited for ===")
    for p in seen:
        c = cmap[p]
        print(f"  [{c['number']:>2}] PMID {p}  {str(c['year']):4s}  "
              f"{c['cited_for'][:56]}")
        print(f"        {c['title'][:96]}")
    print(f"\n-> {DER / 'citation_map.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
