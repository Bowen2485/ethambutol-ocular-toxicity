# -*- coding: utf-8 -*-
"""Table 2: drop the narrow-term count so the eight-column table becomes seven and fits.

The count is in Supplementary Table S1 anyway, the Methods promise was to report P with q, and
the eight-column version overflowed by 1.5 pt.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")

old = ('         "| Query | Narrow terms | Exposed cases | Cases in database | ROR | 95% CI | P | q |",\n'
       '         "|---|---|---|---|---|---|---|---|"]')
new = ('         "| Query | Exposed cases | Cases in database | ROR | 95% CI | P | q |",\n'
       '         "|---|---|---|---|---|---|---|"]')
assert old in s, "header not found"
s = s.replace(old, new, 1)

old = ('    lines.append(f"| {r[\'smq\']} | {r[\'narrow_terms\']} | {r[\'a\']} | {r[\'n_event\']:,} | "')
new = ('    lines.append(f"| {r[\'smq\']} | {r[\'a\']} | {r[\'n_event\']:,} | "')
assert old in s, "row not found"
s = s.replace(old, new, 1)

old = ('    "\\n\\nP, two-sided p value from the test named in Supplementary Table S1; q, "\n'
       '    "Benjamini–Hochberg adjusted across the eleven queries.")')
new = ('    "\\n\\nP, two-sided p value from the test named in Supplementary Table S1, which also gives "\n'
       '    "the narrow-term counts; q, Benjamini–Hochberg adjusted across the eleven queries.")')
assert old in s, "note not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("Table 2 reduced to seven columns")
