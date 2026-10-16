# -*- coding: utf-8 -*-
"""
Extract the quantitative findings from the five supplied papers and check them against this
manuscript's claims.

What is being looked for
    Not a summary of each paper, but the specific numbers that bear on statements this
    manuscript makes.  Three of the manuscript's claims are the ones at risk:

        that daily dose does not predict the optic-nerve outcome once exposure duration is
            accounted for (LR P = 0.55) - if a human study reports a dose effect, the two have
            to be reconciled;
        that incidence estimates range from 0.28% to 6.5% according to ascertainment - if a
            study reports a figure outside that range, the range is wrong;
        that renal impairment acts by raising exposure rather than independently - if a study
            reports renal disease as an independent risk factor, that needs addressing.

    Each paper is therefore searched for its incidence figure, its pooled or adjusted odds
    ratios, and any dose or reversibility finding, and the results are printed with the
    sentence they came from so the number can be checked rather than trusted.

The fontTools warnings that flooded the last run are suppressed: they concern glyph widths in
embedded fonts and do not affect the extracted text.
"""
from __future__ import annotations

import json
import re
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
try:
    from pypdf import PdfReader
except ImportError:
    raise SystemExit("pypdf needed")

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "docs" / "literature_peers" / "text"

PAPERS = {
    "haitanuwong": ("10.3389/fopht.2023.1152215",
                    "Incidence, risk factors and clinical characteristics, Thailand"),
    "au2022": ("10.1136/bjophthalmol-2020-317742",
               "Macular superficial vessel density in preclinical EON"),
    "au2008": ("(Korean cohort)", "Incidence and clinical features, Korea"),
    "41905405": ("10.1016/j.jcjo.2026.03.004",
                 "Systematic review and meta-analysis of risk factors"),
    "42251932": ("10.1016/j.pnpbp.2026.111773",
                 "Fluoxetine sexual dysfunction: pharmacovigilance + network toxicology"),
}

EN = (ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")


def sentences(text: str, pat: str, limit: int = 4) -> list[str]:
    out = []
    for m in re.finditer(pat, text, re.I):
        s = max(0, m.start() - 260)
        e = min(len(text), m.end() + 260)
        seg = re.sub(r"\s+", " ", text[s:e]).strip()
        if seg[:60] not in {o[:60] for o in out}:
            out.append(seg)
        if len(out) >= limit:
            break
    return out


print("=" * 104)
print("Incidence figures reported")
print("=" * 104)
for key, (doi, label) in PAPERS.items():
    p = TEXT / f"{key}_text.txt"
    if not p.exists():
        print(f"\n  {key}: text not found")
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    print(f"\n  {key}  [{label}]")
    hits = sentences(t, r"(?:incidence|occurred in|developed ON|% of patients)", 3)
    for h in hits:
        print(f"      - {h[:230]}")

print()
print("=" * 104)
print("Dose findings, which bear on the P = 0.55 claim")
print("=" * 104)
for key in PAPERS:
    p = TEXT / f"{key}_text.txt"
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    hits = sentences(t, r"(?:daily dose|dose[- ]dependent|cumulative dose|mg/kg/day)", 3)
    if hits:
        print(f"\n  {key}")
        for h in hits:
            print(f"      - {h[:230]}")

print()
print("=" * 104)
print("Renal findings, which bear on the Mendelian randomisation interpretation")
print("=" * 104)
for key in PAPERS:
    p = TEXT / f"{key}_text.txt"
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    hits = sentences(t, r"(?:renal|kidney).{0,80}(?:risk|factor|odds|OR\b|independent)", 3)
    if hits:
        print(f"\n  {key}")
        for h in hits:
            print(f"      - {h[:230]}")

print()
print("=" * 104)
print("Reversibility and outcome")
print("=" * 104)
for key in PAPERS:
    p = TEXT / f"{key}_text.txt"
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    hits = sentences(t, r"(?:recover|reversib|visual outcome|prognos)", 2)
    if hits:
        print(f"\n  {key}")
        for h in hits:
            print(f"      - {h[:230]}")

print()
print("=" * 104)
print("Manuscript claims at risk")
print("=" * 104)
CLAIMS = {
    "incidence range 0.28-6.5%": r"0\.28|6\.5\s*%",
    "daily dose not predictive": r"did not predict|likelihood-ratio P\s*=\s*0\.55|P = 0\.55",
    "renal acts via exposure": r"raising drug exposure|raising exposure",
    "regimen rate ratio 3.28": r"3\.28",
    "ascertainment drives spread": r"ascertain",
}
for label, pat in CLAIMS.items():
    n = len(re.findall(pat, EN, re.I))
    print(f"  {label:32s} present in manuscript: {n} time(s)")

print()
print("=" * 104)
print("Citation status")
print("=" * 104)
BIB = (ROOT / "submission" / "references.bib").read_text(encoding="utf-8")
for key, (doi, label) in PAPERS.items():
    cited = doi.startswith("10.") and doi.lower() in BIB.lower()
    print(f"  {key:14s} {'CITED' if cited else 'NOT CITED':10s}  {label[:60]}")
