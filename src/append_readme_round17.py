# -*- coding: utf-8 -*-
"""README entry for the figure revision."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8").rstrip()
block = """

## Seventeenth round: figures (2026-10-24)

1. **Figure 1 redrawn as three independent modules.** JADER (B) and Canada Vigilance (C) no longer
   hang off the FAERS flow by dashed arrows, which read as if they were branches of it. A vertical
   rule and the label "Independent database - separate analysis" separate the panels, and the word
   "replication" is gone from the figure. Each external module states its own cohort, exposure
   definition and outcome.
2. **Figure 2 enlarged**: query labels 10 pt, ROR and case counts 9 pt, taller canvas. All eleven
   queries remain, including those below unity and those with intervals crossing 1.
3. **Figure 3 made taller** (7.6 x 7.2 in) with 10 pt labels, so the fifteen terms are legible at
   journal width; the negative-control and non-specific-comparator labels stay in the term text.
4. **Figure 4**: a blank row separates the exposure-role block from the reporting-period block, and
   the log axis now carries explicit ticks at 20, 50, 100, 200 and 500, so intervals can be read.
5. All four regenerated from results/main_results.json and the Canada extract; the figure/table
   consistency check still reports no mismatches.
"""
if "Seventeenth round" not in text:
    p.write_text(text + block, encoding="utf-8")
    print("README updated")
