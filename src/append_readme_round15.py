# -*- coding: utf-8 -*-
"""Record the fifteenth-round consistency check and wording changes."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8").rstrip()
block = """

## Fifteenth round: consistency check and five wording points (2026-10-24)

1. **Numbers verified end to end.** `src/verify_consistency.py` compares results/main_results.json
   with the PDF, the Word tables and supplementary S1: 11 queries and 15 preferred terms agree, and
   the release tag is present in the PDF. No mismatches.
2. **What the eleven-query comparison supports is now stated explicitly** in §4.3: the queries are
   not independent, terms belong to more than one, background frequencies and disease mix differ,
   and an ordering of odds ratios is not a test that one ocular structure is affected more than
   another.
3. **Exposure identification limits moved into the discussion**, with both consequences: brand-only
   reports are missed, and because the three systems identify exposure differently the
   cross-database results are agreement in direction and pattern rather than comparable ratios.
4. **Onset medians tied to their subset**: missing date pairs are unlikely to be random, and the
   medians come from the 17-term definition rather than the 45-term query.
5. **The fixed-regimen analysis is named a within-class reporting contrast**, not a cohort, and the
   things it does not hold constant are listed.
6. **Ferroptosis verdict aligned** in abstract, results and discussion: no consistent transcriptional
   support, not exclusion.
7. Main text 5,993 words after the additions, abstract 298, 19 references, PDF 24 pages, 0 overfull.
8. Also corrected: Results 3.7 still called GSE318912 "a TPEN-treated human cell line"; it now says
   the AC16 cardiomyocyte line, matching Methods.
"""
if "Fifteenth round" not in text:
    p.write_text(text + block, encoding="utf-8")
    print("README updated")
