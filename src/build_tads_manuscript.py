# -*- coding: utf-8 -*-
"""Assemble the restructured manuscript, with tables and references generated from data.

Inputs
    manuscript/TADS_EN.md          title page, abstract, plain-language summary, introduction
    manuscript/TADS_methods.md     methods
    manuscript/TADS_results.md     results
    manuscript/TADS_discussion.md  discussion

Output
    manuscript/TADS_manuscript.md

The tables are generated from results/main_results.json and the JADER/Canada files, and the
reference list is rebuilt in the new citation order from the previous manuscript's list, so no
number in the assembled paper is typed twice.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"

d = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
N = d["N"]
n_eth_ps = d["n_ethambutol_suspect"]


def ci(a: int, n_event: int, n_drug: int) -> tuple[float, float, float]:
    b, c, dd = n_drug - a, n_event - a, N - n_drug - n_event + a
    est = (a * dd) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / dd)
    return est, math.exp(math.log(est) - 1.959964 * se), math.exp(math.log(est) + 1.959964 * se)


# ------------------------------------------------------------------ Table 1
table1 = f"""Table 1. Data sources and exposed cohorts.

| Source | Period | Records | Records naming ethambutol | Exposure definition |
|---|---|---|---|---|
| FAERS quarterly ASCII releases | 2004Q1–2026Q2 (90 quarters) | {d['case_flow']['submitted_reports']:,} submitted; {d['case_flow']['de_duplicated_cases']:,} de-duplicated cases | {d['n_ethambutol']:,} ({d['n_ethambutol_suspect']:,} as primary or secondary suspect) | Any drug record, case-insensitive substring |
| JADER | September 2026 release | 1,054,239 cases | 3,483 ({1_798:,} as suspect) | Suspect drug code; all roles in sensitivity |
| Canada Vigilance | Extract of 31 May 2026 | 1,266,430 reports | 965 ({460:,} as suspect) | Ingredient table; all roles in main |
"""

# ------------------------------------------------------------------ Table 2
rows = sorted(d["smq"], key=lambda r: -r["ror"])
lines = ["Table 2. The eleven ocular Standardised MedDRA Queries (narrow sets, MedDRA 29.0), "
         "ethambutol against all other de-duplicated reports.", "",
         "| Query | Exposed cases | Cases in database | ROR | 95% CI | P | q |",
         "|---|---|---|---|---|---|---|"]
for r in rows:
    q = "<1e-300" if r["q_bh"] == 0 else f"{r['q_bh']:.2g}"
    lines.append(f"| {r['smq']} | {r['a']} | {r['n_event']:,} | "
                 f"{r['ror']:.2f} | {r['ror_lcl']:.2f}–{r['ror_ucl']:.2f} | "
                 f"{r['p_display']} | {q} |")
table2 = "\n".join(lines) + (
    "\n\nP, two-sided P value from Pearson’s χ² test without continuity correction, except for "
    "Scleral disorders, where Fisher’s exact test was used because the smallest expected cell "
    "count was below 5. Term-level estimates for the nine optic-nerve preferred terms with at "
    "least three exposed cases and the six pre-specified controls are in Supplementary Table "
    "S1. q, "
    "Benjamini–Hochberg adjusted across the eleven ocular queries.")

# ------------------------------------------------------------------ Table 3
on = next(r for r in d["pt"] if r["term"] == "Optic neuropathy")
smq = next(r for r in d["smq"] if r["smq"].startswith("Optic nerve"))
on_ps = ci(on["a_suspect"], on["n_event"], n_eth_ps)
smq_ps = ci(smq["a_suspect"], smq["n_event"], n_eth_ps)
t1, t2 = d["temporal"]["2004-2016"], d["temporal"]["2017-2026"]
jad = pd.read_csv(RES / "jader_validation.csv", encoding="utf-8-sig")
jad_s = jad[(jad.analysis == "suspect only")]
jad_a = jad[(jad.analysis == "any role")]
can = json.loads((RES / "canada_vigilance_ethambutol.json").read_text(encoding="utf-8"))
can_any = next(c for c in can["cells"] if c["exposure"].endswith("any role") and c["event"] == "optic term")
can_sus = next(c for c in can["cells"] if c["exposure"].endswith("suspect only") and c["event"] == "optic term")


def jrow(term: str, frame: pd.DataFrame) -> str:
    r = frame[frame.term == term].iloc[0]
    return (f"{int(r.a)} | {r.ror:.2f} ({r.ror_lcl:.2f}–{r.ror_ucl:.2f})")


table3 = f"""Table 3. The optic-nerve outcome in the three systems, by exposure definition.

| System | Exposure | Outcome | Exposed cases | ROR (95% CI) |
|---|---|---|---|---|
| FAERS | Any role (main) | Optic neuropathy | {on['a']} | {on['ror']:.2f} ({on['ror_lcl']:.2f}–{on['ror_ucl']:.2f}) |
| FAERS | Any role (main) | Optic-nerve query | {smq['a']} | {smq['ror']:.2f} ({smq['ror_lcl']:.2f}–{smq['ror_ucl']:.2f}) |
| FAERS | Suspect only | Optic neuropathy | {on['a_suspect']} | {on_ps[0]:.2f} ({on_ps[1]:.2f}–{on_ps[2]:.2f}) |
| FAERS | Suspect only | Optic-nerve query | {smq['a_suspect']} | {smq_ps[0]:.2f} ({smq_ps[1]:.2f}–{smq_ps[2]:.2f}) |
| FAERS | Any role, 2004–2016 | Optic neuropathy | {t1['a']} | {t1['ror']:.2f} ({t1['ror_lcl']:.2f}–{t1['ror_ucl']:.2f}) |
| FAERS | Any role, 2017–2026 | Optic neuropathy | {t2['a']} | {t2['ror']:.2f} ({t2['ror_lcl']:.2f}–{t2['ror_ucl']:.2f}) |
| JADER | Suspect only | Optic neuropathy | {jrow('optic neuropathy', jad_s)} |
| JADER | Any role | Optic neuropathy | {jrow('optic neuropathy', jad_a)} |
| Canada Vigilance | Any role | Any optic-nerve term | {can_any['a']} | {can_any['ror']:.2f} ({can_any['ror_lcl']:.2f}–{can_any['ror_ucl']:.2f}) |
| Canada Vigilance | Suspect only | Any optic-nerve term | {can_sus['a']} | {can_sus['ror']:.2f} ({can_sus['ror_lcl']:.2f}–{can_sus['ror_ucl']:.2f}) |

ROR, reporting odds ratio. The Canadian outcome is an exploratory composite of every preferred
term containing the string OPTIC (29 such terms appear in the extract); it is not the
45-term query and includes terms of different clinical meaning. A total of
1,308 reports in the full Canada Vigilance database carried at least one of these
terms, and 21 of those reports named ethambutol. The JADER rows report the term-specific
estimate; cataract, glaucoma and dry eye were null or below unity in the same analysis. The two
FAERS period rows use that period's own de-duplicated case count as the reference population.
Estimates are not compared across systems: the proportion of reports naming the drug as suspect
differs by system.

Table 4. Pre-specified negative controls (cataract, dry eye, glaucoma, conjunctivitis) and
non-specific comparators (eye pain, vision blurred) in FAERS.

| Term | Exposed cases | Cases in database | ROR | 95% CI | q |
|---|---|---|---|---|---|
"""
for r in [x for x in d["pt"] if x["group"] == "control"]:
    q = "<1e-300" if r["q_bh"] == 0 else f"{r['q_bh']:.2g}"
    table3 += (f"| {r['term']} | {r['a']} | {r['n_event']:,} | {r['ror']:.2f} | "
               f"{r['ror_lcl']:.2f}–{r['ror_ucl']:.2f} | {q} |\n")

# ---------------------------------------------------------------- references
old = (MAN / "Ethambutol_EyeTox_EN_full.md").read_text(encoding="utf-8")
ref_block = old[old.find("## References"):old.find("## Figures and Tables")]
old_refs: dict[int, str] = {}
for m in re.finditer(r"^(\d{1,2})\.\s+(.+?)(?=\n\d{1,2}\.\s|\Z)", ref_block, re.M | re.S):
    old_refs[int(m.group(1))] = " ".join(m.group(2).split())

NEW_ORDER = [14, 15, 16, 17, 18, 1, 2, 3, 21, 22, 23, 26, 27, 28, 11]
EXTRA = {
    16: "Fusaroli M, Salvo F, Begaud B, AlShammari TM, Bate A, Battini V, et al. The Reporting "
        "of a Disproportionality Analysis for Drug Safety Signal Detection Using Individual Case "
        "Safety Reports in PharmacoVigilance (READUS-PV): development and statement. Drug Saf. "
        "2024;47(6):575-584. doi:10.1007/s40264-024-01421-9.",
    17: "Langan SM, Schmidt SA, Wing K, Ehrenstein V, Nicholls SG, Filion KB, et al. The "
        "reporting of studies conducted using observational routinely collected health data "
        "statement for pharmacoepidemiology (RECORD-PE). BMJ. 2018;363:k3532. "
        "doi:10.1136/bmj.k3532.",
}
refs = []
for i, old_no in enumerate(NEW_ORDER, start=1):
    refs.append(f"{i}. {old_refs[old_no]}")
refs.append(f"16. {EXTRA[16]}")
refs.append(f"17. {EXTRA[17]}")
refs.append(f"18. {old_refs[9]}")
#: READUS-PV and RECORD-PE were appended in order 16, 17 after the first fifteen entries
refs_text = "\n".join(refs)
#: if the reference list has been rebuilt from Europe PMC metadata, use that instead of the
#: carried-over list; the enriched file is generated by src/enrich_references.py
enriched = MAN / "TADS_references.md"
if enriched.exists():
    refs_text = enriched.read_text(encoding="utf-8").strip()
    print(f"  using enriched reference list ({len(refs_text.splitlines())} entries)")
#: the previous reference list carried doubled full stops ("Lee AG.."); a single full stop is
#: what Vancouver style expects, and the duplicate came from the author string, not from us
refs_text = re.sub(r"\.\.", ".", refs_text)

STATEMENTS = """
## Statements and Declarations

**Ethics approval and consent to participate.** Not applicable. The study used publicly available,
de-identified aggregate data from pharmacovigilance databases and public gene-expression series. No
human participants were recruited, no identifiable information was accessed, and no ethics
approval was therefore required.

**Consent for publication.** Not applicable. No individual person's data are reported.

**Availability of data and materials.** FAERS quarterly ASCII releases are available from the U.S.
Food and Drug Administration
(https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html); JADER from the Pharmaceuticals
and Medical Devices Agency of Japan; Canada Vigilance from Health Canada (cvponline); GSE294687 and
GSE318912 from NCBI GEO. The derived tables that support the findings — the de-duplication map, the
2×2 tables, `results/main_results.json` and the code that generates every table and figure — are
available at https://github.com/Bowen2485/ethambutol-ocular-toxicity/tree/v2.0-tads-2026-10-21
(release tag `v2.0-tads-2026-10-21`) under an MIT licence.

**Code availability.** All analysis scripts, the data dictionary and the results file are in the
repository named above, under the same release tag. The scripts record the software versions and
random seeds used.

**Funding.** This research received no specific grant from any funding agency in the public,
commercial, or not-for-profit sectors.

**Declaration of conflicting interests.** The authors declare no competing interests.

**Author contributions.** Bowen Shi: conceptualisation, methodology, software, formal analysis,
writing — original draft. Jing Yan: conceptualisation, supervision, writing — review and editing.
Zhengzheng Wu: supervision. Siyuan Yang: writing — review and editing. Yaqin Tan: investigation.
Xuan Wang: visualisation. All authors read and approved the final manuscript.

**Acknowledgements.** None.

**ORCID.** Bowen Shi, 0009-0001-6900-1779.


## Figure legends

**Figure 1.** Case flow in the three spontaneous-reporting systems. FAERS releases were
de-duplicated by case version; the ethambutol cohort was defined by any drug record naming the
drug, and split by drug role. JADER and Canada Vigilance were analysed independently with the
exposure definitions given in Table 1.

**Figure 2.** The eleven ocular Standardised MedDRA Queries (narrow sets) in FAERS, ethambutol
against all other de-duplicated reports. Points are reporting odds ratios with 95% confidence
intervals on a logarithmic axis; the dashed line marks unity. Red, interval above unity; blue,
interval below unity; grey, interval includes unity. The number of exposed cases is given at the
right.

**Figure 3.** Preferred terms within the optic-nerve query, alongside the pre-specified negative
controls and the non-specific ocular comparators. Terms with fewer than three exposed cases are
not plotted. Conventions as in Figure 2.

**Figure 4.** Sensitivity of the optic-nerve estimate to exposure role and reporting period. The
upper four rows compare the preferred term and the query under all-role and suspect-only exposure;
the lower two split the cohort by receipt year at 2016. Conventions as in Figure 2.
"""

parts = [
    (MAN / "TADS_EN.md").read_text(encoding="utf-8"),
    (MAN / "TADS_methods.md").read_text(encoding="utf-8"),
    (MAN / "TADS_results.md").read_text(encoding="utf-8"),
    (MAN / "TADS_discussion.md").read_text(encoding="utf-8"),
]
body = "\n".join(parts)
out = body.rstrip() + "\n" + STATEMENTS + "\n\n## Tables\n\n" + table1 + "\n" + table2 + "\n\n" \
      + table3 + "\n\n## References\n\n" + refs_text + "\n"

target = MAN / "TADS_manuscript.md"
target.write_text(out, encoding="utf-8")

# ------------------------------------------------------------ word accounting
main_start = out.find("## 1. Introduction")
main_end = out.find("## Statements")
main = out[main_start:main_end]
n_words = len([w for w in re.sub(r"[#*|]", " ", main).split() if re.search(r"\w", w)])
print(f"written {target.relative_to(ROOT)}")
print(f"main text (Introduction to Conclusion): {n_words:,} words")
print(f"abstract: {len(out[out.find('## Abstract'):out.find('**Keywords')].split())} tokens")
print(f"references: {len(refs)} entries")
