# -*- coding: utf-8 -*-
"""Record the Word-formatting repair in the submission README."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "submission" / "tads" / "README.md"
text = p.read_text(encoding="utf-8").rstrip()
block = """

## Fourteenth round: Word formatting (2026-10-23)

Opening the Word file showed three converter faults that the PDF never had:

1. **Third-level headings leaked as text.** The converter handled `#` and `##` only, so 24 lines
   such as `### 2.4 Exposure` were printed literally. Headings one to four levels deep are now
   converted, giving 35 headings (1 + 9 + 25).
2. **Horizontal rules printed.** Three `---` separators appeared as dashes; they are skipped.
3. **Heading bullets.** Each heading now carries `numId=0`, so the word processor does not draw a
   bullet before it.

A scan of the final file finds no backticks, `**`, `###`, `---`, pipes or `__`: the Word document is
plain text and real tables. It was rebuilt to a staging path because the submission copy was open
in a word processor, then copied over once the file was released.
"""
if "Fourteenth round" not in text:
    p.write_text(text + block, encoding="utf-8")
    print("README updated")
