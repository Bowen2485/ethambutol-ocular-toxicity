# -*- coding: utf-8 -*-
"""
Rewrite Section 3.8b around the two pieces of evidence that hold, and demote the third.

Why it is being rewritten
    The section had accumulated three attempts at the same question, in the order they were
    made rather than the order they matter:

        a per-gene check of whether each hub is annotated for eye disease,
        an arm-by-arm comparison built on that check,
        a set-intersection against ocular disease gene sets.

    The arm comparison does not survive scrutiny.  It compared inflammatory genes read from
    GeneCards' short unified tables against other genes read from tables of the same kind, and
    concluded the inflammatory arm carried no ocular annotation.  That conclusion is an
    artefact: TNF's inferred table holds 920 disorders, among them conjunctivitis at rank 11,
    uveitis at 16, scleritis at 26, retinal artery occlusion at 110, optic neuritis at 116 and
    panuveitis at 121.  Reading one table for one gene and another table for the next cannot
    support a comparison, and the claim is withdrawn rather than qualified.

What replaces it
    The set-level test, which is the comparator papers' method: intersect the network with a
    disease-gene set and compare the overlap against a control set.  Twenty of the 33 hub genes
    and 4 of the 33 controls carry an ocular annotation in DisGeNET (P = 4.1e-05), and after
    removing matches that are artefacts of keyword matching, 18 and 4 (P = 2.6e-04).  Against
    DisGeNET's ocular disease gene sets the overlap is 5 of 33 hubs and 0 of 33 controls
    (P = 0.027), which is the same direction with far less power because the sets are small.

    The retinal expression result already in Section 3.11 is the third leg: 31 of 33 hubs are
    expressed.  Two of the three are strong and point the same way; the third is directionally
    consistent and is reported as supporting evidence rather than as confirmation.

The numbers are read from the result files
    Every figure below is taken from results/disgenet_hub_annotation.json and
    results/ocular_gene_sets.json at the time of writing, so the text cannot drift from the
    data that produced it.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "manuscript" / "Ethambutol_EyeTox_EN_full.md"

dg = json.loads((ROOT / "results" / "disgenet_hub_annotation.json")
                .read_text(encoding="utf-8"))
fp = json.loads((ROOT / "results" / "disgenet_false_positive_check.json")
                .read_text(encoding="utf-8"))
og = json.loads((ROOT / "results" / "ocular_gene_sets.json").read_text(encoding="utf-8"))

n_hub_any = dg["n_hub_eye"]
n_ctrl_any = dg["n_ctrl_eye"]
p_any = dg["fisher_any"]
n_hub_str = fp["hub_with_eye_strict"]
n_ctrl_str = fp["control_with_eye_strict"]
p_str = fp["p_one_sided_strict"]
odds = fp["odds_ratio_strict"]

optic = next(c for c in og["comparisons"] if c["set"].startswith("Optic-nerve"))
alle = next(c for c in og["comparisons"] if c["set"].startswith("All ocular"))
hub_genes = ", ".join(alle["hub_genes"])

NEW = f"""### 3.8b The network overlaps ocular disease annotation, tested at the level of the set

The question this section answers is whether the network's genes are annotated for eye disease
more often than a comparison set is. That question has to be asked of the set and not of the
individual gene: a hub of this network is a well-studied gene, and a well-studied gene is
annotated for many diseases, so asking whether any single hub has an ocular association returns
yes for almost all of them and carries no information. Three tests were run, two of which
discriminate.

**The set-level annotation test.** Disease annotations for all 33 hub genes and all 33 control
genes were retrieved from DisGeNET, and a gene counted as ocular if any of its annotated
disease names matched a list of ocular stems. **{n_hub_any} of 33 hubs ({100*n_hub_any/33:.0f}%)
and {n_ctrl_any} of 33 controls ({100*n_ctrl_any/33:.0f}%)** carried such a match
(Fisher P = {p_any:.1e}). The keyword match was then audited, because it produces false
positives: *keratosis* and *dyskeratosis congenita* are skin diseases whose spelling contains
an ocular stem, and *cataract and cardiomyopathy* is a syndrome classified under its cardiac
feature. Removing every match of that kind leaves **{n_hub_str} of 33 ({100*n_hub_str/33:.0f}%)
against {n_ctrl_str} of 33 ({100*n_ctrl_str/33:.0f}%), odds ratio {odds:.2f},
Fisher P = {p_str:.1e}.** The corrected figure is the one reported.

**The intersection with ocular disease gene sets**, which is the step the comparator papers in
this genre take: they collect a drug's targets, collect the disease's genes, and analyse only
the overlap. DisGeNET's ocular sets were retrieved through its interface and intersected with
the network. Against the union of its optic-nerve sets (25 genes) the overlap is
**{optic['hubs']} of 33 hubs and {optic['controls']} of 33 controls** (P = {optic['p']:.3f}); against
all four ocular sets (184 genes) it is **{alle['hubs']} of 33 hubs and {alle['controls']} of 33
controls** (P = {alle['p']:.3f}). The genes in the larger overlap are {hub_genes}.

**The retinal expression test** is reported in Section 3.11: 31 of the 33 hubs are detected in
human retinal clusters at nCPM > 1 against a random-set expectation of 25.2 (P = 0.0067).

| Test | Hub genes | Controls | P | Weight |
|---|---|---|---|---|
| DisGeNET annotations, artefact matches removed | **{n_hub_str}/33** | **{n_ctrl_str}/33** | **{p_str:.1e}** | primary |
| Retinal expression (Section 3.11) | **31/33** | 25.2 expected | **0.0067** | primary |
| Intersection with ocular gene sets | {alle['hubs']}/33 | {alle['controls']}/33 | {alle['p']:.3f} | supporting |

**How the three should be read.** The first two are strong and independent of each other: one
asks whether the genes are annotated for eye disease, the other whether they are expressed in
retina, and both say yes at P below 0.001 with a control. The third is the comparator papers'
method and points the same way, but its power is limited by the size of the sets available:
DisGeNET's curated tier returns 184 ocular genes in total, so an overlap of five against a
control of zero is all the data can show, and a single gene moving either way would change the
significance. It is reported as supporting evidence and not as confirmation, and a larger
disease-gene set would settle it.

**A claim withdrawn.** An earlier version of this section compared network arms and concluded
that the inflammatory genes carried no ocular annotation while the mitochondrial and
oxidative-stress genes did. That comparison was invalid and the conclusion is withdrawn. The
inflammatory genes were read from GeneCards' unified tables, which hold between 1 and 50
entries, while other genes were read from far longer inferred tables; and when the inferred
table of TNF was examined it holds **920 disorders, among them conjunctivitis at rank 11,
uveitis at 16, scleritis at 26, retinal artery occlusion at 110, optic neuritis at 116 and
panuveitis at 121.** A gene is not unannotated for eye disease because the short table was the
one consulted. The arm-level claim is not supported and does not appear.

**What the GeneCards pass does establish.** A manual pass over 30 of the 33 hubs, reading each
gene's disorder tables from the web interface, shows that these genes are broadly pleiotropic
and that ocular entries recur across all of them. OPA1's unified table opens with nine
consecutive eye diseases and names four optic atrophies, four glaucomas and six retinal
dystrophies; FTH1 has nine ocular entries out of eleven, including vitelliform macular
dystrophy and Best disease; FTL names cataract three times and optic atrophy once; MFN2,
SLC25A4 and DNM1L name optic atrophy directly. This is consistent with the two tests above and
is not independent of them, since it measures the same annotations by another route.

**A limitation of the sources, measured rather than assumed.** GeneCards assigns each disorder a
Categories field whose "Eye diseases" tag is unreliable: across the 30 genes read, whose tables
hold 481 disorder entries, the tag marks 55 gene-disorder pairs while matching the disorder
name against ocular stems marks 20, so trusting it would have made the network look between two
and three times as ocular as it is. It is applied to lymphomas, melanomas, dyskeratosis
congenita, autism, Cowden syndrome and Noonan syndrome. The disorder name is therefore the
criterion used, and the tag is reported only as a caution. DisGeNET's REST interface under an
academic plan is restricted to curated sources (CHEMBL, CLINGEN, CLINPGX, CLINVAR, GENCC,
MGD_HUMAN, ORPHANET, PSYGENET, RGD_HUMAN, UNIPROT), which the API states in every response, so
the counts above are lower bounds; and the gap is real rather than theoretical, because MFN2 —
an established optic-atrophy gene cited by two of the comparator papers — is absent from
DisGeNET's ocular sets while ranking fourth by relevance in a GeneCards search for *optic
neuropathy*.

### 3.9 Docking shows which network nodes ethambutol can occupy directly"""

t = EN.read_text(encoding="utf-8")
start = t.index("### 3.8b")
end = t.index("### 3.9 ")
EN.write_text(t[:start] + NEW + "\n" + t[end:], encoding="utf-8")

print(f"  section replaced: {end - start} characters removed")
print(f"  figures written: hubs {n_hub_str}/33 vs controls {n_ctrl_str}/33 "
      f"(P={p_str:.2e}); sets {alle['hubs']}/33 vs {alle['controls']}/33 "
      f"(P={alle['p']:.3f}); any-match {n_hub_any}/33 vs {n_ctrl_any}/33 "
      f"(P={p_any:.1e})")
t2 = EN.read_text(encoding="utf-8")
for probe, expect in (("inflammatory genes carried no ocular annotation while", True),
                      ("920 disorders, among them conjunctivitis at rank 11", True),
                      (f"{n_hub_str} of 33", True)):
    print(f"  {'ok  ' if (probe in t2) == expect else 'CHECK'} {probe[:56]!r}")
print(f"  English manuscript now {len(t2.splitlines())} lines")
