# -*- coding: utf-8 -*-
"""Add the author ORCID and record the acknowledgements and APC position.

Bowen Shi: ORCID 0009-0001-6900-1779. Jing Yan has none. Acknowledgements: none (already stated).
APC: none applies, so nothing is added to the manuscript; the submission-system field is recorded
in the package README instead.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

# ------------------------------------------------------------ markdown front matter
p = MAN / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
old = "**Authors:** Bowen Shi¹, Jing Yan¹*, Zhengzheng Wu¹, Siyuan Yang¹, Yaqin Tan¹, Xuan Wang¹"
new = ("**Authors:** Bowen Shi¹ (ORCID 0009-0001-6900-1779), Jing Yan¹*, Zhengzheng Wu¹, "
       "Siyuan Yang¹, Yaqin Tan¹, Xuan Wang¹")
assert old in text, "author line not found"
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("front matter: ORCID added")

# ------------------------------------------------------------------- PDF title page
p = ROOT / "src" / "build_tads_pdf.py"
s = p.read_text(encoding="utf-8")
old = ('.replace("__AUTHORS__", inline("Bowen Shi, Jing Yan, Zhengzheng Wu, Siyuan Yang, "\n'
       '                                         "Yaqin Tan, Xuan Wang"))')
new = ('.replace("__AUTHORS__", inline("Bowen Shi (ORCID 0009-0001-6900-1779), Jing Yan, "\n'
       '                                         "Zhengzheng Wu, Siyuan Yang, Yaqin Tan, "\n'
       '                                         "Xuan Wang"))')
assert old in s, "pdf author line not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("PDF title page: ORCID added")

# --------------------------------------------------------------- statements note
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
old = "**Acknowledgements.** None.\n"
new = ("**Acknowledgements.** None.\n\n"
       "**ORCID.** Bowen Shi, 0009-0001-6900-1779.\n")
assert old in s, "acknowledgements line not found"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("statements: ORCID entry added")
