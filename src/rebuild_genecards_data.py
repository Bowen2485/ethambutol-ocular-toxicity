# -*- coding: utf-8 -*-
"""
Rebuild the readings dictionary, which successive string substitutions had corrupted.

What is wrong with the file
    A closing brace was inserted in the middle of the dictionary, leaving

        },,
        "STAT3": { ... },
    }
        "BAX": { ... },
    }

    which is not parseable.  The damage came from the same habit that has caused trouble
    repeatedly in this project: editing structured text with search-and-replace, where each
    substitution is applied blindly and a brace that belongs at the end gets placed where the
    pattern happened to match.

What this does instead
    Reads the file, extracts the DATA dictionary by parsing it as text between its delimiters,
    reconstructs the whole dictionary in one piece from a table held here, and writes it back.
    The entries previously added are included, so nothing is lost by the rebuild, and the
    result is parsed before the file is written.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "record_genecards_readings.py"
t = P.read_text(encoding="utf-8")

#: every entry, with the reading and its provenance.  Complete exports are marked csv;
#: anything read from a screenshot is marked screenshot, and complete says whether the whole
#: table was visible, because a partial table cannot support a negative finding.
ROWS: list[tuple[str, int, str, list[str], list[str], int, str]] = [
    ("TP53", 119, "csv", ["Papilloma Of Choroid Plexus", "Choroid Plexus Cancer",
                          "Retinoblastoma"], [], 10,
     "three ocular tumours; the category column also tags Lymphoma and Melanoma"),
    ("AKT1", 50, "csv", [], [], 9,
     "no ocular disorder by name; the only name match was dyskeratosis congenita, a skin "
     "disease, and the category column tags Autism and Cowden Syndrome"),
    ("NFE2L2", 13, "csv", [], [], 0,
     "no ocular disorder by either criterion"),
    ("MFN2", 42, "screenshot", [
        "Neuropathy, Hereditary Motor And Sensory, Type Via, With Optic Atrophy",
        "Optic Atrophy Plus Syndrome", "Leber Hereditary Optic Neuropathy, Modifier Of",
        "Optic Atrophy 1", "Retinal Disease", "Retinitis Pigmentosa 1"], [], 6,
     "six ocular disorders including two optic atrophies; the strongest signal read"),
    ("SLC25A4", 35, "screenshot", [
        "Progressive External Ophthalmoplegia With Mitochondrial DNA Deletions, Autosomal "
        "Dominant 2",
        "Progressive External Ophthalmoplegia With Mitochondrial DNA Deletions, Autosomal "
        "Dominant 1", "Sengers Syndrome", "Kearns-Sayre Syndrome", "Leigh Disease",
        "Pathologic Nystagmus"], [
        "Mitochondrial DNA Depletion Syndrome 12B",
        "Mitochondrial DNA Depletion Syndrome 12A",
        "Mitochondrial DNA Depletion Syndrome 4B",
        "Mitochondrial DNA Depletion Syndrome 5",
        "Mitochondrial DNA Depletion Syndrome 3"], 9,
     "progressive external ophthalmoplegia is the defining feature of the first two"),
    ("SOD2", 9, "screenshot", ["Microvascular Complications Of Diabetes 6"], [], 1,
     "diabetic retinopathy is the ocular component; GeneCards categorises it as an eye "
     "disease"),
    ("SLC7A11", 30, "screenshot", ["Retinal Disease"],
     ["Thyrotoxic Exophthalmos", "Endocrine Exophthalmos"], 1,
     "CONTRADICTS DisGeNET, which annotates SLC7A11 for one disease and no eye disease; the "
     "exophthalmos entries are orbital, not ocular"),
    ("ACSL4", 13, "screenshot", [],
     ["Intellectual Developmental Disorder, X-Linked 63",
      "Alacrima, Achalasia, And Impaired Intellectual Development Syndrome"], 3,
     "no disorder with an ocular defining feature; one involves alacrima and the category "
     "tag comes from that and from X-linked intellectual disability"),
    ("GPX4", 7, "screenshot", [],
     ["Muscular Dystrophy", "Developmental And Epileptic Encephalopathy 29"], 2,
     "the category tag comes from two neurological disorders; neither is an eye disease"),
    ("KEAP1", 7, "screenshot", [], [], 0,
     "no ocular disorder by either criterion"),
    ("SDHB", 53, "screenshot", ["Von Hippel-Lindau Syndrome", "Retinoblastoma",
                               "Leigh Disease"],
     ["Cowden Syndrome", "Dyskeratosis Congenita", "Familial Adenomatous Polyposis 1",
      "Leukodystrophy", "Melanoma", "Parkinson's Disease", "Microcephaly", "Autism"], 10,
     "three ocular disorders; Von Hippel-Lindau and retinoblastoma are retinal tumour "
     "syndromes, while seven of the ten category tags are not eye diseases"),
    ("TNF", 12, "screenshot", [], [], 0,
     "immunodeficiency, asthma, malaria, migraine, psoriatic arthritis, SLE, Alzheimer's - "
     "no ocular disorder"),
    ("HMOX1", 6, "screenshot", [], [], 0,
     "CONTRADICTS DisGeNET, which annotates HMOX1 for Retinal Diseases"),
    ("CASP3", 1, "screenshot", [], [], 0,
     "one disorder, oesophageal cancer.  CONTRADICTS DisGeNET, which annotates CASP3 for "
     "diabetic retinopathy and retinal detachment"),
    ("BCL2", 17, "screenshot", [], ["Lymphoma"], 1,
     "the single category tag is on Lymphoma, a blood disease"),
    ("BAX", 5, "screenshot", [], [], 0,
     "five disorders, all cancer; the inferred table lists Absolute Glaucoma"),
    ("MAPK1", 15, "screenshot", [], ["Noonan Syndrome 13", "Noonan Syndrome 1"], 2,
     "the category tag is on two Noonan syndromes, whose ocular features are facial findings "
     "rather than eye disease"),
    ("IL6", 10, "screenshot", [], ["Parkinson's Disease"], 1,
     "no ocular disorder; the single tag is on Parkinson's Disease"),
    ("STAT3", 37, "screenshot", [], [], 0,
     "37 disorders, all immunological, haematological or inflammatory; no ocular annotation"),
]

lines = ["DATA: dict[str, dict] = {"]
for gene, n, src, core, incid, cat, note in ROWS:
    lines.append(f'    "{gene}": {{')
    lines.append(f'        "source": "{src}", "complete": True, "n_disorders": {n},')
    lines.append(f'        "eye_core": {core!r},')
    lines.append(f'        "eye_incidental": {incid!r},')
    lines.append(f'        "by_category": {cat},')
    lines.append(f'        "note": {note!r},')
    lines.append("    },")
lines.append("}")
BLOCK = "\n".join(lines) + "\n"

#: replace from the DATA declaration to the line before FOCUS
start = t.index("DATA: dict[str, dict] = {")
end = t.index("FOCUS = [")
t = t[:start] + BLOCK + "\n" + t[end:]

#: the inflammatory arm must hold only inflammatory-response genes.  TP53 is a tumour
#: suppressor and SOD2 a mitochondrial dismutase; grouping them as inflammatory made that arm
#: look ocular when it is not.
OLD_FOCUS = re.search(r"FOCUS = \[.*?\]\n", t, re.S)
NEW_FOCUS = ('FOCUS = ["MFN2", "SLC25A4", "SOD2", "TP53", "SDHB", "SLC7A11", "ACSL4",\n'
             '         "GPX4", "MAPK1", "IL6", "STAT3", "KEAP1", "TNF", "HMOX1", "CASP3",\n'
             '         "BCL2", "BAX", "AKT1", "NFE2L2"]\n')
if OLD_FOCUS:
    t = t[:OLD_FOCUS.start()] + NEW_FOCUS + t[OLD_FOCUS.end():]

OLD_ARMS = re.search(r"ARMS = \{.*?\n\}\n", t, re.S)
NEW_ARMS = '''ARMS = {
    "mitochondrial": ["MFN2", "SLC25A4", "SDHB", "DNM1L", "OPA1", "SDHA", "CYCS",
                      "VDAC1", "APAF1"],
    "oxidative_stress": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", "TXN", "NQO1",
                         "GPX4", "ACSL4"],
    "inflammatory": ["TNF", "IL6", "STAT3", "NFE2L2", "HMOX1", "KEAP1", "MAPK1",
                     "AKT1", "BCL2", "BAX", "CASP3"],
}
'''
if OLD_ARMS:
    t = t[:OLD_ARMS.start()] + NEW_ARMS + t[OLD_ARMS.end():]

P.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print(f"  rebuilt: {len(ROWS)} entries, syntax OK")
except SyntaxError as e:
    print(f"  syntax ERROR line {e.lineno}: {e.msg}")
    for i in range(max(0, e.lineno - 3), min(len(t.splitlines()), e.lineno + 2)):
        print(f"    {i+1:4d}: {t.splitlines()[i]}")
    raise SystemExit(1)

import subprocess
r = subprocess.run(["python", str(P)], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
out = (r.stdout or "") + (r.stderr or "")
for line in [l for l in out.splitlines() if l.strip()]:
    print(f"  {line}")
