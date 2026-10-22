# -*- coding: utf-8 -*-
"""Append the ninth-round change log to the submission README."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8").rstrip()
block = """

## Ninth review round (2026-10-22)

1. **Table 2 footnote names the tests actually used**: Pearson chi-square for ten queries and
   Fisher exact for Scleral disorders (smallest expected count 3.4), instead of pointing at S1,
   which only covers the 15 preferred terms.
2. **The GSE294687 source study is cited** (Cheng et al., Cell Commun Signal 2025;23(1):474, now
   reference 19), the reanalysis is described as using a different method from the original
   count-based analysis, and the TPEN comparator is named as the AC16 cardiomyocyte line analysed
   unpaired.
3. **Abstract**: the eleven queries are classified by statistical support (four positive signals,
   three significantly below 1, four intervals spanning 1), and the onset result is marked as
   restricted to reports with usable dates. 298 words.
4. **Ocular infections** is now attributed to confounding by indication and channelling rather
   than to a confirmed mechanism, in both Results 3.2 and Discussion 4.3.
5. PDF: 24 pages, 0 overfull; 19 references.
"""
if "Ninth review round" not in text:
    p.write_text(text + block, encoding="utf-8")
    print("README updated")
else:
    print("README already updated")
