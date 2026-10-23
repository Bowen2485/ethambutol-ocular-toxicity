# -*- coding: utf-8 -*-
"""README entry for the sixteenth round."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8").rstrip()
block = """

## Sixteenth round: compression and closing wording (2026-10-24)

1. **Main text 5,993 -> 5,796 words.** The cuts are limited to repeated statements that a reporting
   pattern is not a risk estimate (four restatements), one duplicated three-database summary, one
   duplicated 17-term clause, and two shortened sentences in the transcriptomic paragraph. No bias
   explanation, case count, statistical definition or limitation was removed.
2. **Plain Language Summary ending rewritten.** It no longer says to watch patients "especially in
   the first months of treatment"; it asks for vigilance, existing clinical guidance on monitoring,
   and states that no follow-up interval was tested and that the 125-day median comes from reports
   with complete dates.
3. **Verified**: figures 2 and 3 carry the same case counts and odds ratios as
   results/main_results.json; table 3 keeps the three systems' exposure definitions and outcome
   labels distinct; S11 marks the Canadian rule as a study-specific composite while S4b lists its
   29 terms.
4. Banned phrasings checked and absent: "statistically greater", "anatomically specific",
   "selective toxicity", "preferential optic".
"""
if "Sixteenth round" not in text:
    p.write_text(text + block, encoding="utf-8")
    print("README updated")
