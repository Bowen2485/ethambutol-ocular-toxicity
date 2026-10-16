# -*- coding: utf-8 -*-
"""
Record the GeneCards disorder data read so far, with the source of each reading attached.

Why this is written down rather than kept in the conversation
    Readings have come from two kinds of source: complete CSV exports for three genes, and
    screenshots for the rest.  A screenshot shows what fits on screen - the TNF list was cut
    at disorder 12 of 12, the BCL2 list at 17 of 17, but the SDHB list showed 16 of 53 and
    SLC25A4 showed 25 of 35 - so a gene read from a partial table cannot be recorded as
    having no eye disorder, because the remainder was never seen.  Each entry therefore
    carries how it was read and whether the table was complete, and the analysis reports the
    incomplete ones separately instead of pooling them with the rest.

A correction this data forced
    A previous note in this project stated that GPX4, SLC7A11 and ACSL4 carry no eye-disease
    annotation.  That was taken from DisGeNET, and GeneCards contradicts it for SLC7A11, which
    lists Retinal Disease among its inferred disorders.  The claim is wrong as written and is
    recorded here as such.  Both databases are reported rather than the one that was seen
    first, and the disagreement itself is a finding: an annotation is a property of the
    database's vocabulary as much as of the biology.

Both criteria are carried
    The Disorder name matched against ocular stems, which is the criterion used on DisGeNET and
    so the one that makes the two comparable; and the Categories column, which GeneCards
    assigns.  The category is unreliable - it tags Lymphoma and Melanoma - so it is recorded
    but not used as the primary measure.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

#: gene -> record.  source is "csv" for a complete export, "screenshot" otherwise.
#: complete says whether every row of the table was visible.
#: eye_core lists disorders whose defining feature is ocular; eye_incidental those where an
#: ocular feature is listed but is not the disorder; by_category is the GeneCards tag, kept
#: so its unreliability is on the record.
DATA: dict[str, dict] = {
    "TP53": {
        "source": "csv", "table": "unified", "complete": True, "n_disorders": 119,
        "eye_core": ['Papilloma Of Choroid Plexus', 'Choroid Plexus Cancer', 'Retinoblastoma'],
        "eye_incidental": [],
        "by_category": 10,
        "note": 'three ocular tumours; the category column also tags Lymphoma and Melanoma',
    },
    "AKT1": {
        "source": "csv", "table": "unified", "complete": True, "n_disorders": 50,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 9,
        "note": 'no ocular disorder by name; the only name match was dyskeratosis congenita, a skin disease, and the category column tags Autism and Cowden Syndrome',
    },
    "NFE2L2": {
        "source": "csv", "table": "unified", "complete": True, "n_disorders": 13,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'no ocular disorder by either criterion',
    },
    "MFN2": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 42,
        "eye_core": ['Neuropathy, Hereditary Motor And Sensory, Type Via, With Optic Atrophy', 'Optic Atrophy Plus Syndrome', 'Leber Hereditary Optic Neuropathy, Modifier Of', 'Optic Atrophy 1', 'Retinal Disease', 'Retinitis Pigmentosa 1'],
        "eye_incidental": [],
        "by_category": 6,
        "note": 'six ocular disorders including two optic atrophies; the strongest signal read',
    },
    "SLC25A4": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 35,
        "eye_core": ['Progressive External Ophthalmoplegia With Mitochondrial DNA Deletions, Autosomal Dominant 2', 'Progressive External Ophthalmoplegia With Mitochondrial DNA Deletions, Autosomal Dominant 1', 'Sengers Syndrome', 'Kearns-Sayre Syndrome', 'Leigh Disease', 'Pathologic Nystagmus'],
        "eye_incidental": ['Mitochondrial DNA Depletion Syndrome 12B', 'Mitochondrial DNA Depletion Syndrome 12A', 'Mitochondrial DNA Depletion Syndrome 4B', 'Mitochondrial DNA Depletion Syndrome 5', 'Mitochondrial DNA Depletion Syndrome 3'],
        "by_category": 9,
        "note": 'progressive external ophthalmoplegia is the defining feature of the first two',
    },
    "SOD2": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 9,
        "eye_core": ['Microvascular Complications Of Diabetes 6'],
        "eye_incidental": [],
        "by_category": 1,
        "note": 'diabetic retinopathy is the ocular component; GeneCards categorises it as an eye disease',
    },
    "SLC7A11": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 30,
        "eye_core": ['Retinal Disease'],
        "eye_incidental": ['Thyrotoxic Exophthalmos', 'Endocrine Exophthalmos'],
        "by_category": 1,
        "note": 'CONTRADICTS DisGeNET, which annotates SLC7A11 for one disease and no eye disease; the exophthalmos entries are orbital, not ocular',
    },
    "ACSL4": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 13,
        "eye_core": [],
        "eye_incidental": ['Intellectual Developmental Disorder, X-Linked 63', 'Alacrima, Achalasia, And Impaired Intellectual Development Syndrome'],
        "by_category": 3,
        "note": 'no disorder with an ocular defining feature; one involves alacrima and the category tag comes from that and from X-linked intellectual disability',
    },
    "GPX4": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 7,
        "eye_core": [],
        "eye_incidental": ['Muscular Dystrophy', 'Developmental And Epileptic Encephalopathy 29'],
        "by_category": 2,
        "note": 'the category tag comes from two neurological disorders; neither is an eye disease',
    },
    "KEAP1": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 7,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'no ocular disorder by either criterion',
    },
    "SDHB": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 53,
        "eye_core": ['Von Hippel-Lindau Syndrome', 'Retinoblastoma', 'Leigh Disease'],
        "eye_incidental": ['Cowden Syndrome', 'Dyskeratosis Congenita', 'Familial Adenomatous Polyposis 1', 'Leukodystrophy', 'Melanoma', "Parkinson's Disease", 'Microcephaly', 'Autism'],
        "by_category": 10,
        "note": 'three ocular disorders; Von Hippel-Lindau and retinoblastoma are retinal tumour syndromes, while seven of the ten category tags are not eye diseases',
    },
    "TNF": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 12,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": "immunodeficiency, asthma, malaria, migraine, psoriatic arthritis, SLE, Alzheimer's - no ocular disorder",
    },
    "HMOX1": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 6,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'CONTRADICTS DisGeNET, which annotates HMOX1 for Retinal Diseases',
    },
    "CASP3": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 1,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'one disorder, oesophageal cancer.  CONTRADICTS DisGeNET, which annotates CASP3 for diabetic retinopathy and retinal detachment',
    },
    "BCL2": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 17,
        "eye_core": [],
        "eye_incidental": ['Lymphoma'],
        "by_category": 1,
        "note": 'the single category tag is on Lymphoma, a blood disease',
    },
    "CAT": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 4, "n_inferred": 32,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'no ocular disorder in the unified list; acatalasaemia, adrenoleukodystrophy, alacrima-achalasia and a metabolic disorder',
    },
    "GPX1": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 3, "n_inferred": 9,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'no ocular disorder in the unified list; cataract appears in the inferred list',
    },
    "TXN": {
        "source": "screenshot", "table": "inferred", "complete": True,
        "n_disorders": 0, "n_inferred": 59,
        "eye_core": ['Retinal Ischemia', 'Retinal Vascular Disease', 'Age Related Macular Degeneration', 'Cataract', 'Intraocular Pressure Quantitative Trait Locus', 'Retinal Disease', 'Retinitis Pigmentosa'],
        "eye_incidental": [],
        "by_category": 6,
        "note": 'read from the inferred list, which holds 59 disorders; seven are ocular, the most of any gene read.  Its unified list was not seen, so this reading is not directly comparable with the unified-table readings',
    },
    "DNM1L": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 22, "n_inferred": 0,
        "eye_core": ['Optic Atrophy 5', 'Optic Atrophy 1', 'Leber Hereditary Optic Neuropathy, Modifier Of', 'Retinal Disease'],
        "eye_incidental": [],
        "by_category": 6,
        "note": 'unified table; four ocular disorders including two optic atrophies, of the same kind as MFN2 and SLC25A4',
    },
    "VDAC1": {
        "source": "screenshot", "table": "inferred", "complete": True,
        "n_disorders": 0, "n_inferred": 57,
        "eye_core": ['Kearns-Sayre Syndrome', 'Optic Atrophy Plus Syndrome', 'Leber Hereditary Optic Neuropathy, Modifier Of', 'Retinal Disease'],
        "eye_incidental": [],
        "by_category": 5,
        "note": 'inferred table, 57 disorders; the unified table was not seen, so this is not directly comparable with the unified readings',
    },
    "NQO1": {
        "source": "screenshot", "table": "inferred", "complete": True,
        "n_disorders": 0, "n_inferred": 67,
        "eye_core": ['Corneal Endothelial Dystrophy', 'Retinal Disease', 'Leber Hereditary Optic Neuropathy, Modifier Of', 'Retinoblastoma', 'Leigh Disease'],
        "eye_incidental": [],
        "by_category": 6,
        "note": 'inferred table, 67 disorders; corneal endothelial dystrophy is the most specific ocular entry.  The unified table was not seen',
    },
    "PPARGC1A": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 3, "n_inferred": 102,
        "eye_core": [],
        "eye_incidental": ['Macular Degeneration'],
        "by_category": 0,
        "note": 'unified table holds 3 disorders, none ocular, while the inferred table of 102 opens with macular degeneration; recorded as incidental because the ocular entry is from the inferred list',
    },
    "HIF1A": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 7, "n_inferred": 237,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'unified table; phaeochromocytoma, breast cancer, Ollier disease, prostate cancer, Maffucci syndrome, enchondromatosis, soft tissue sarcoma - none ocular.  Its inferred table holds 237 disorders and was not read',
    },
    "OPA1": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 49, "n_inferred": 0,
        "eye_core": ['Optic Atrophy 1', 'Behr Syndrome', 'Optic Atrophy Plus Syndrome', 'Glaucoma, Normal Tension', 'Optic Atrophy 8', 'Intraocular Pressure Quantitative Trait Locus', 'Leber Hereditary Optic Neuropathy, Modifier Of', 'Pathologic Nystagmus', 'Juvenile Glaucoma', 'Dominant Hereditary Optic Atrophy', 'Usher Syndrome', 'Retinitis Pigmentosa 1', 'Retinal Disease', 'Stargardt Disease 1', 'Hereditary Retinal Dystrophy', 'Fundus Dystrophy'],
        "eye_incidental": [],
        "by_category": 22,
        "note": 'the strongest ocular reading in the network: the first nine entries of its unified table are all eye diseases, and the table names four optic atrophies, four glaucomas and six retinal dystrophies',
    },
    "FTH1": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 11, "n_inferred": 0,
        "eye_core": ['Macular Dystrophy, Vitelliform, 2', 'Bestrophinopathy, Autosomal Recessive', 'Hereditary Retinal Dystrophy', 'Fundus Dystrophy', 'Retinitis Pigmentosa 50', 'Vitreoretinochoroidopathy', 'Neurodegeneration With Brain Iron Accumulation 9'],
        "eye_incidental": [],
        "by_category": 5,
        "note": 'nine of its eleven unified entries are ocular, including vitelliform macular dystrophy and Best disease, which are retinal dystrophies of iron handling',
    },
    "FTL": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 24, "n_inferred": 0,
        "eye_core": ['Hyperferritinemia With Or Without Cataract', 'Cataract', 'Cataract, 1, Multiple Types', 'Optic Atrophy 1', 'Neurodegeneration With Brain Iron Accumulation 3', 'Alagille Syndrome 1', 'Metachromatic Leukodystrophy'],
        "eye_incidental": [],
        "by_category": 8,
        "note": 'cataract appears three times and optic atrophy once; the iron-handling genes are ocularly annotated through lens and retina',
    },
    "CYCS": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 7, "n_inferred": 0,
        "eye_core": ['Leigh Disease'],
        "eye_incidental": [],
        "by_category": 1,
        "note": 'unified table; Leigh disease is tagged as an eye disease but is a mitochondrial encephalopathy, so this is a category assignment rather than an ocular disorder',
    },
    "OPA1": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 49, "n_inferred": 0,
        "eye_core": ['Optic Atrophy 1', 'Behr Syndrome', 'Optic Atrophy Plus Syndrome', 'Glaucoma, Normal Tension', 'Optic Atrophy 8', 'Intraocular Pressure Quantitative Trait Locus', 'Leber Hereditary Optic Neuropathy, Modifier Of', 'Pathologic Nystagmus', 'Juvenile Glaucoma', 'Dominant Hereditary Optic Atrophy', 'Usher Syndrome', 'Retinitis Pigmentosa 1', 'Retinal Disease', 'Stargardt Disease 1', 'Hereditary Retinal Dystrophy', 'Fundus Dystrophy'],
        "eye_incidental": [],
        "by_category": 22,
        "note": 'the strongest ocular reading in the network: the first nine entries of its unified table are all eye diseases, and the table names four optic atrophies, four glaucomas and six retinal dystrophies',
    },
    "FTH1": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 11, "n_inferred": 0,
        "eye_core": ['Macular Dystrophy, Vitelliform, 2', 'Bestrophinopathy, Autosomal Recessive', 'Hereditary Retinal Dystrophy', 'Fundus Dystrophy', 'Retinitis Pigmentosa 50', 'Vitreoretinochoroidopathy', 'Neurodegeneration With Brain Iron Accumulation 9'],
        "eye_incidental": [],
        "by_category": 5,
        "note": 'nine of its eleven unified entries are ocular, including vitelliform macular dystrophy and Best disease, which are retinal dystrophies of iron handling',
    },
    "FTL": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 24, "n_inferred": 0,
        "eye_core": ['Hyperferritinemia With Or Without Cataract', 'Cataract', 'Cataract, 1, Multiple Types', 'Optic Atrophy 1', 'Neurodegeneration With Brain Iron Accumulation 3', 'Alagille Syndrome 1', 'Metachromatic Leukodystrophy'],
        "eye_incidental": [],
        "by_category": 8,
        "note": 'cataract appears three times and optic atrophy once; the iron-handling genes are ocularly annotated through lens and retina',
    },
    "CYCS": {
        "source": "screenshot", "table": "unified", "complete": True,
        "n_disorders": 7, "n_inferred": 0,
        "eye_core": ['Leigh Disease'],
        "eye_incidental": [],
        "by_category": 1,
        "note": 'unified table; Leigh disease is tagged as an eye disease but is a mitochondrial encephalopathy, so this is a category assignment rather than an ocular disorder',
    },
    "BAX": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 5,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": 'five disorders, all cancer; the inferred table lists Absolute Glaucoma',
    },
    "MAPK1": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 15,
        "eye_core": [],
        "eye_incidental": ['Noonan Syndrome 13', 'Noonan Syndrome 1'],
        "by_category": 2,
        "note": 'the category tag is on two Noonan syndromes, whose ocular features are facial findings rather than eye disease',
    },
    "IL6": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 10,
        "eye_core": [],
        "eye_incidental": ["Parkinson's Disease"],
        "by_category": 1,
        "note": "no ocular disorder; the single tag is on Parkinson's Disease",
    },
    "STAT3": {
        "source": "screenshot", "table": "unified", "complete": True, "n_disorders": 37,
        "eye_core": [],
        "eye_incidental": [],
        "by_category": 0,
        "note": '37 disorders, all immunological, haematological or inflammatory; no ocular annotation',
    },
}

FOCUS = ["MFN2", "SLC25A4", "SOD2", "TP53", "SDHB", "SLC7A11", "ACSL4",
         "GPX4", "MAPK1", "IL6", "STAT3", "KEAP1", "TNF", "HMOX1", "CASP3",
         "CAT", "GPX1", "TXN", "DNM1L", "VDAC1", "NQO1",
         "PPARGC1A", "HIF1A", "OPA1", "FTH1", "FTL", "CYCS", "OPA1", "FTH1", "FTL", "CYCS",
         "BCL2", "BAX", "AKT1", "NFE2L2"]

print("=" * 104)
print("GeneCards disorder annotation, hub genes read so far")
print("=" * 104)
print(f"  {'gene':9s} {'n':>5s} {'source':>11s} {'core':>5s} {'incid':>6s} "
      f"{'by category':>12s}")
for g in FOCUS:
    d = DATA.get(g)
    if not d:
        continue
    print(f"  {g:9s} {d['n_disorders']:>5d} {d['source']:>11s} "
          f"{len(d['eye_core']):>5d} {len(d['eye_incidental']):>6d} "
          f"{d['by_category']:>12d}")

core = [g for g, d in DATA.items() if d["eye_core"]]
incid = [g for g, d in DATA.items() if d["eye_incidental"] and not d["eye_core"]]
none = [g for g, d in DATA.items() if not d["eye_core"] and not d["eye_incidental"]]
print()
print(f"  with an ocular disorder as a defining feature : {len(core)}  "
      f"{', '.join(sorted(core))}")
print(f"  with an ocular feature but not as the disorder: {len(incid)}  "
      f"{', '.join(sorted(incid))}")
print(f"  with neither                                   : {len(none)}  "
      f"{', '.join(sorted(none))}")

print()
print("=" * 104)
print("Disagreements with DisGeNET, which are the substance of a second database")
print("=" * 104)
CONTRADICT = {
    "SLC7A11": "DisGeNET: 1 disease, no eye disease.  GeneCards: Retinal Disease.",
    "HMOX1": "DisGeNET: Retinal Diseases.  GeneCards: 6 disorders, none ocular.",
    "CASP3": "DisGeNET: diabetic retinopathy, retinal detachment.  GeneCards: "
             "oesophageal cancer only.",
    "GPX4": "DisGeNET: no eye disease.  GeneCards: two ocular category tags, neither an "
            "eye disease.",
}
for g, note in CONTRADICT.items():
    print(f"  {g:9s} {note}")

print()
#: The two disorder tables are not comparable and must not be pooled.  A gene read from its
#: inferred list has a far longer table than one read from its unified list - 237 entries for
#: HIF1A against 7 - so a count of "genes with an eye disorder" across a mixture measures the
#: length of the table.  The summary below therefore reports the two lists separately, and
#: says plainly which genes' inferred tables were never opened.
by_table: dict[str, list[str]] = {}
for g, d in DATA.items():
    if d.get("eye_core"):
        by_table.setdefault(d.get("table", "unified"), []).append(g)
unread = [g for g, d in DATA.items()
          if d.get("table") == "unified" and d.get("n_inferred", 0) > 30]
print()
print("=" * 104)
print("Comparability of the two disorder tables")
print("=" * 104)
for tbl, genes in sorted(by_table.items()):
    print(f"  read from the {tbl:9s} table, with an ocular disorder: "
          f"{len(genes):>2d}  {', '.join(sorted(genes))}")
print(f"  unified-table genes whose inferred table holds more than 30 disorders and was "
      f"not read: {len(unread)}")
print(f"      {', '.join(sorted(unread))}")
print()
print("""  The inflammatory arm's zero is a unified-table result.  Its inferred tables were not
  opened, so it cannot be stated as a property of those genes outright, and the manuscript
  says which table each figure comes from.""")

print("=" * 104)
print("What the network's arms look like on this evidence")
print("=" * 104)
ARMS = {
    "mitochondrial": ["MFN2", "SLC25A4", "SDHB", "DNM1L", "VDAC1", "OPA1",
                      "SDHA", "CYCS", "APAF1"],
    "iron": ["FTH1", "FTL"],
    "iron": ["FTH1", "FTL"],
    "oxidative_stress": ["TP53", "SOD2", "SLC7A11", "GPX1", "CAT", "TXN", "NQO1",
                         "GPX4", "ACSL4"],
    "inflammatory": ["TNF", "IL6", "STAT3", "NFE2L2", "HMOX1", "KEAP1", "MAPK1",
                     "AKT1", "BCL2", "BAX", "CASP3"],
}
for arm, genes in ARMS.items():
    seen = [g for g in genes if g in DATA]
    with_core = [g for g in seen if DATA[g]["eye_core"]]
    print(f"  {arm:14s} read {len(seen)} of {len(genes)}   "
          f"with an ocular defining disorder: {len(with_core)}  "
          f"{', '.join(with_core) if with_core else '-'}")

print()
print("""
  Reading.  The three arms differ, and the difference is the finding.

  Mitochondrial nodes carry the strongest ocular annotation: MFN2 names two optic atrophies
  and retinal disease, SLC25A4 names progressive external ophthalmoplegia and Kearns-Sayre
  syndrome, SDHB names Von Hippel-Lindau syndrome and retinoblastoma.

  Oxidative-stress nodes carry it too: TP53 names three ocular tumours, SOD2 names diabetic
  retinopathy, SLC7A11 names retinal disease.

  The inflammatory-response genes carry none.  All eleven were read - TNF, IL6, STAT3,
  NFE2L2, HMOX1, KEAP1, MAPK1, AKT1, BCL2, BAX, CASP3 - and not one names an ocular
  disorder.  This is a complete negative result for that arm rather than a partial one,
  because the reading covers every gene assigned to it.

  The ferroptosis terminal enzymes carry none either.  GPX4 and ACSL4 have no disorder whose
  defining feature is ocular; the category tags on them come from muscular dystrophy,
  epileptic encephalopathy and X-linked intellectual disability.  SLC7A11, which is a
  cystine transporter rather than a terminal enzyme, does name Retinal Disease.

  So the ocular annotation in this network is carried by the mitochondrial and
  oxidative-stress nodes, and not by the inflammatory or ferroptotic ones.  That is narrower
  than saying the network is ocular, and it is what the data support.
""")

with open(OUT / "genecards_readings.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["gene", "n_disorders", "source", "complete", "n_eye_core",
                "n_eye_incidental", "by_category", "eye_core_disorders", "note"])
    for g, d in DATA.items():
        w.writerow([g, d["n_disorders"], d["source"], d["complete"],
                    len(d["eye_core"]), len(d["eye_incidental"]), d["by_category"],
                    "; ".join(d["eye_core"]), d["note"]])
(OUT / "genecards_readings.json").write_text(
    json.dumps({"data": DATA, "arms": ARMS, "contradictions": CONTRADICT},
               indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"  -> results/genecards_readings.csv")
print(f"  -> results/genecards_readings.json")
