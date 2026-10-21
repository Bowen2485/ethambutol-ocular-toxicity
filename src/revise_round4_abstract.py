# -*- coding: utf-8 -*-
"""Abstract and declarations for the fourth round (the earlier edits are already applied)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"

p = MAN / "TADS_EN.md"
text = p.read_text(encoding="utf-8")
old = ("Control terms were mostly at or below background, but vision blurred showed a modest excess "
       "(1.50, 1.28–1.76). The pattern replicated in JADER (optic neuropathy 570.96, 413.50–788.37) "
       "and Canada Vigilance (21.85, 14.13–33.79). Median onset was 125 days, against 33 days for "
       "non-ocular events.")
assert old in text, "abstract results sentence not found"
new = ("The four negative controls showed no positive signal, but vision blurred did (1.50, "
       "1.28–1.76). An optic-nerve-related signal was also observed in JADER (optic neuropathy "
       "570.96, 413.50–788.37) and Canada Vigilance (composite outcome 21.85, 14.13–33.79); the "
       "non-specific comparison was assessable in FAERS and, for mapped terms, JADER, but not in "
       "Canada. Median onset was 125 days against 33 for non-ocular events. In the exploratory "
       "transcriptomic analysis, selected ferroptosis-related predictions were not reproduced, and "
       "their clinical relevance remains uncertain.")
text = text.replace(old, new, 1)

if "**Plain Language Title.**" not in text:
    marker = "**Keywords.**"
    plt_ = ("**Plain Language Title.** How side-effect reports describe eye problems with the "
            "tuberculosis drug ethambutol\n\n")
    text = text.replace(marker, plt_ + marker, 1)
p.write_text(text, encoding="utf-8")

abs_block = text[text.find("## Abstract"):text.find("**Keywords")]
words = len([w for w in re.sub(r"[#*]", " ", abs_block).split() if re.search(r"\w", w)])
print(f"abstract now {words} words")

# --------------------------------------------------------------- declarations
p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
start = s.index('STATEMENTS = """')
end = s.index('"""', start + len('STATEMENTS = """')) + 3
NEW = '''STATEMENTS = """
## Statements and Declarations

**Ethics approval and consent to participate.** Not applicable. The study used publicly available,
de-identified aggregate data from pharmacovigilance databases and public gene-expression series. No
human participants were recruited, no identifiable information was accessed, and no ethics
approval was therefore required.

**Consent for publication.** Not applicable. No individual person's data are reported.

**Availability of data and materials.** FAERS quarterly ASCII releases are available from the U.S.
Food and Drug Administration
(https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html); JADER from the Pharmaceuticals
and Medical Devices Agency of Japan; Canada Vigilance from Health Canada (cvponline); GSE294687 and
GSE318912 from NCBI GEO. The derived tables that support the findings — the de-duplication map, the
2×2 tables, `results/main_results.json` and the code that generates every table and figure — are
available at https://github.com/Bowen2485/ethambutol-ocular-toxicity/tree/v2.0-tads-2026-10-21
(release tag `v2.0-tads-2026-10-21`) under an MIT licence.

**Code availability.** All analysis scripts, the data dictionary and the results file are in the
repository named above, under the same release tag. The scripts record the software versions and
random seeds used.

**Funding.** This research received no specific grant from any funding agency in the public,
commercial, or not-for-profit sectors.

**Declaration of conflicting interests.** The authors declare no competing interests.

**Author contributions.** Bowen Shi: conceptualisation, methodology, software, formal analysis,
writing — original draft. Jing Yan: conceptualisation, supervision, writing — review and editing.
Zhengzheng Wu: supervision. Siyuan Yang: writing — review and editing. Yaqin Tan: investigation.
Xuan Wang: visualisation. All authors read and approved the final manuscript.

**Acknowledgements.** None.
"""'''
s = s[:start] + NEW + s[end:]
p.write_text(s, encoding="utf-8")
print("statements reformatted")
