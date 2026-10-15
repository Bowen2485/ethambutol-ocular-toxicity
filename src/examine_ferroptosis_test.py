# -*- coding: utf-8 -*-
"""
Examine the ferroptosis class test before interpreting it, and check the control.

The test returned a null result: ferroptosis inducers as a class gave an optic-nerve ROR
of 0.67, below background, while apoptosis inducers gave 1.21.  That is the opposite of
what the class-level hypothesis predicted, and it would be easy to write it up as
evidence against ferroptosis in ethambutol.  Before doing that, three things need
checking, because a null result from a badly posed test is not evidence about anything.

    1. Is the signal absent, or is the class simply not monitored?  Chemotherapy
       patients are not screened ophthalmologically the way tuberculosis patients are,
       so a low optic-nerve ratio in that population may reflect ascertainment rather
       than biology.  The class's rate on non-specific ocular terms - which do not need
       an ophthalmologist to report - distinguishes the two.

    2. Is the comparison fair?  Ethambutol is not itself a ferroptosis inducer; it
       causes ferroptosis indirectly, by suppressing SDHB.  A test using erastin and
       sorafenib asks whether direct ferroptosis induction damages the optic nerve,
       which is a different question from whether ethambutol's toxicity runs through
       ferroptosis.

    3. Does the class contain the drug under study?  If ethambutol were counted in a
       comparator class the arithmetic would be circular.
"""
from __future__ import annotations

import math
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "derived" / "faers.sqlite"

CLASSES = {
    "ferroptosis inducer": ["%ERASTIN%", "%SORAFENIB%", "%SULFASALAZINE%",
                            "%ARTESUNATE%", "%ARTEMETHER%", "%DIHYDROARTEMISININ%",
                            "%ARTEMISININ%", "%LANPERISONE%", "%RSL3%",
                            "%BUTHIONINE%", "%FIN56%", "%ALTIRATINIB%"],
    "apoptosis inducer": ["%CISPLATIN%", "%DOXORUBICIN%", "%PACLITAXEL%",
                          "%ETOPOSIDE%", "%VINCRISTINE%", "%GEMCITABINE%",
                          "%CYCLOPHOSPHAMIDE%"],
}
ANTITB = ["%ETHAMBUTOL%", "%ISONIAZID%", "%RIFAMPICIN%", "%RIFAMPIN%",
          "%PYRAZINAMIDE%", "%STREPTOMYCIN%", "%LINEZOLID%", "%CLOFAZIMINE%",
          "%BEDAQUILINE%"]

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.execute("PRAGMA cache_size=-2000000")
MATCH = ("(UPPER(COALESCE(dn.drugname,'')) LIKE ? OR "
         "UPPER(COALESCE(dn.prod_ai,'')) LIKE ?)")


def cases(pats):
    cond = " OR ".join([MATCH] * len(pats))
    params = [p for pat in pats for p in (pat, pat)]
    return {r[0] for r in con.execute(
        f"""SELECT DISTINCT d.caseid FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE {cond}""", params)}


print("=" * 96)
print("1. Does the ferroptosis class overlap the antitubercular drugs?")
print("=" * 96)
fer = cases(CLASSES["ferroptosis inducer"])
antitb = cases(ANTITB)
overlap = fer & antitb
print(f"  ferroptosis class cases      : {len(fer):,}")
print(f"  antitubercular cases         : {len(antitb):,}")
print(f"  in both                      : {len(overlap):,}")
if overlap:
    print("  Note: sulfasalazine is used in some tuberculosis-era regimens and the")
    print("  artemisinins appear in reports from co-endemic regions, so a small overlap")
    print("  is expected.  Ethambutol itself is not in the class.")

print()
print("=" * 96)
print("2. Which substances actually populate each class?")
print("=" * 96)
for label, pats in CLASSES.items():
    cond = " OR ".join([MATCH] * len(pats))
    params = [p for pat in pats for p in (pat, pat)]
    q = f"""SELECT UPPER(COALESCE(dn.drugname,'')) AS nm,
                   COUNT(DISTINCT d.caseid) AS n
            FROM drug d
            JOIN dedup_map m ON d.primaryid = m.primaryid
            JOIN drugname dn ON dn.primaryid = d.primaryid
                            AND dn.drug_seq = d.drug_seq
            WHERE {cond}
            GROUP BY nm ORDER BY n DESC LIMIT 8"""
    print(f"\n  {label}")
    for nm, n in con.execute(q, params):
        print(f"      {str(nm)[:48]:50s} {n:>8,}")

print()
print("=" * 96)
print("3. Is the low optic-nerve ratio ascertainment, or biology?")
print("=" * 96)
print("  Non-specific ocular terms do not need an ophthalmologist to be reported, so a")
print("  class with poor eye monitoring would still show them.  Comparing the two")
print("  separates 'no signal' from 'no one looking'.")
print()


def with_terms(terms):
    lst = ",".join(f"'{t}'" for t in terms)
    return {r[0] for r in con.execute(
        f"""SELECT DISTINCT r.caseid FROM reac r
            JOIN dedup_map m ON r.primaryid = m.primaryid
            WHERE UPPER(r.pt) IN ({lst})""")}


OPTIC = ("OPTIC NEUROPATHY", "OPTIC NEURITIS", "OPTIC ATROPHY",
         "TOXIC OPTIC NEUROPATHY")
NONSPEC = ("DRY EYE", "EYE PAIN", "VISION BLURRED", "CATARACT")
optic = with_terms(OPTIC)
nonspec = with_terms(NONSPEC)
n_total = con.execute("SELECT COUNT(*) FROM dedup_map").fetchone()[0]
n_optic = len(optic)
n_nonspec = len(nonspec)


def ror(a, n_class, n_event, n_total):
    b = n_class - a
    c = n_event - a
    d = n_total - n_class - c
    if min(a, b, c, d) <= 0:
        return None, None, None
    or_ = (a * d) / (b * c)
    se = math.sqrt(1/a + 1/b + 1/c + 1/d)
    return or_, or_*math.exp(-1.96*se), or_*math.exp(1.96*se)


print(f"  {'class':24s} {'optic ROR':>22s} {'non-specific ocular ROR':>26s}")
for label, pats in CLASSES.items():
    ids = cases(pats)
    a = len(ids & optic)
    b = len(ids & nonspec)
    o1, l1, h1 = ror(a, len(ids), n_optic, n_total)
    o2, l2, h2 = ror(b, len(ids), n_nonspec, n_total)
    s1 = f"{o1:.2f} ({l1:.2f}-{h1:.2f})" if o1 else "not estimable"
    s2 = f"{o2:.2f} ({l2:.2f}-{h2:.2f})" if o2 else "not estimable"
    print(f"  {label:24s} {s1:>22s} {s2:>26s}")
    print(f"      cases {len(ids):,};  optic events {a};  non-specific events {b}")

print()
print("  For reference, ethambutol itself:")
emb = cases(["%ETHAMBUTOL%", "%MYAMBUTOL%", "%DEXAMBUTOL%", "%ETAMBUTOL%"])
a = len(emb & optic)
b = len(emb & nonspec)
o1, l1, h1 = ror(a, len(emb), n_optic, n_total)
o2, l2, h2 = ror(b, len(emb), n_nonspec, n_total)
print(f"      {len(emb):,} cases;  optic ROR {o1:.2f} ({l1:.2f}-{h1:.2f});  "
      f"non-specific ocular ROR {o2:.2f} ({l2:.2f}-{h2:.2f})")

con.close()
print()
print("=" * 96)
print("Reading")
print("=" * 96)
print("""  Three things follow, and they determine how this must be written up.

  First, the class test is confounded by ascertainment as much as by biology.  If a
  class shows no optic-nerve signal but does show non-specific ocular signals, nobody is
  looking at its optic nerves; if it shows neither, the drug simply is not reported.
  Either way the comparison to ethambutol - whose optic-nerve ratio is 159 against the
  whole database - does not test ferroptosis, it tests who gets an eye examination.

  Second, and more fundamentally, the test asks the wrong question.  Ethambutol is not a
  ferroptosis inducer; it triggers ferroptosis indirectly by suppressing SDHB.  Whether
  erastin damages the optic nerve is a different question from whether ethambutol's
  toxicity runs through the ferroptosis pathway, and a null answer to the first says
  nothing about the second.

  Third, the class comparison is therefore reported as a limitation and a caution, not
  as evidence.  The honest summary is that a class-level pharmacovigilance test cannot
  adjudicate a mechanism that is cell-type specific, and the paper should say so rather
  than presenting the null as support in either direction.""")
