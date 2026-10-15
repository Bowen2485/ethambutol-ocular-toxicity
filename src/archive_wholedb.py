# -*- coding: utf-8 -*-
"""
Archive the superseded whole-database comparison products.

These files use the whole FAERS database as the denominator.  For an antitubercular
drug that denominator is dominated by non-tuberculosis reports, so the resulting
ratios contrast tuberculosis patients with everyone else rather than comparing drugs
with each other.  They are kept for traceability but moved out of results/ and
tables/ so they cannot be cited by mistake.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "archive" / "superseded_wholedb"

MOVES = [
    "results/faers_signals_all_drugs.csv",
    "tables/Table12_drug_ranking.csv",
    "results/faers_drug_ranking_optic.csv",
    "results/faers_drug_ranking_ocular_nonspecific.csv",
]

README = """# Superseded whole-database comparison products

These files use the whole FAERS database as the denominator. For an antitubercular
drug that denominator is dominated by non-tuberculosis reports, so the resulting
ratios measure the contrast between tuberculosis patients and everyone else rather
than the contrast between drugs. They were removed from the manuscript.

What replaced them:

* `results/faers_withinclass_signals.csv` - denominator restricted to reports
  mentioning any antitubercular drug, with Benjamini-Hochberg control per drug
* `results/faers_headtohead_pairs.csv` - pairwise Fisher comparisons
  (ethambutol versus each comparator)
* `tables/Table2_withinclass.csv`, `tables/Table14_headtohead.csv`

Retained because a reviewer asking about the whole-database figures should be able
to see exactly what changed and why.

| file | what it was | why superseded |
|---|---|---|
| faers_signals_all_drugs.csv | six drugs against the whole database | whole-database denominator is not a drug-versus-drug comparison |
| Table12_drug_ranking.csv | all drugs ranked on ocular risk | same, and drug names were not merged across salt and brand forms, which split one molecule across several entries |
| faers_drug_ranking_optic.csv | optic-nerve phenotype, whole database | same denominator problem |
| faers_drug_ranking_ocular_nonspecific.csv | non-specific ocular phenotype | dominated by topical ophthalmic products, for which the ocular event is the indication, not an adverse effect |
"""


def main() -> int:
    ARCH.mkdir(parents=True, exist_ok=True)
    moved = []
    for rel in MOVES:
        p = ROOT / rel
        if p.exists():
            p.rename(ARCH / p.name)
            moved.append(rel)
    (ARCH / "README.md").write_text(README, encoding="utf-8")
    print(f"archived {len(moved)} file(s) to archive/superseded_wholedb/")
    for m in moved:
        print("  -", m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
