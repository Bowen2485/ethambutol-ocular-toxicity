# -*- coding: utf-8 -*-
"""Round thirteen: README entry for the layout pass."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8").rstrip()
block = """

## Thirteenth review round: layout (2026-10-23)

1. **Word manuscript: references fixed.** The nineteen entries had been merged into one
   4,400-character paragraph; each is now its own paragraph with a hanging indent.
2. **Word manuscript: field names.** Backticks around `CASEID`, `drugname` and `prod_ai` were
   printed literally; they are now set in a monospace run without the ticks.
3. **Figure pages carry their captions.** The PDF figures had no caption under the image, and the
   Word file only had a bare "Figure N". Both now print the legend beneath the figure.
4. **Caption truncation fixed.** In the PDF, "95% confidence intervals" was cut at the percent
   sign, which LaTeX read as a comment; specials are escaped now.
5. **Figure placement.** The [p] float centred each figure vertically and left most of the page
   blank; figures are placed inline at the top of a fresh page with the caption directly below.
6. **Reference block tightened** (`\\parskip` 1 pt, `\\linespread` 0.94) so the list no longer
   leaves a page holding one line: the PDF has 24 pages with no page under 39% full, and those are
   the figure pages.
7. New audit script `src/audit_layout_pdf.py` reports heading-at-foot, near-empty pages and figure
   extents; it is the check that found items 5 and 6.
"""
if "Thirteenth review round" not in text:
    p.write_text(text + block, encoding="utf-8")
    print("README updated")
