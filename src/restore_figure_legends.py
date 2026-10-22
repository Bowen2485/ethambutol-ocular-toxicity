# -*- coding: utf-8 -*-
"""Restore the four figure legends, which a previous edit to the declarations block deleted.

The round-four rewrite of the STATEMENTS string replaced the whole block and did not carry the
legends that followed the acknowledgements, so the assembled manuscript and the PDF have had no
legend text since.  The text is re-inserted after the declarations.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = Path(__file__).resolve().parents[1] / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")

LEGENDS = """

## Figure legends

**Figure 1.** Case flow in the three spontaneous-reporting systems. FAERS releases were
de-duplicated by case version; the ethambutol cohort was defined by any drug record naming the
drug, and split by drug role. JADER and Canada Vigilance were analysed independently with the
exposure definitions given in Table 1.

**Figure 2.** The eleven ocular Standardised MedDRA Queries (narrow sets) in FAERS, ethambutol
against all other de-duplicated reports. Points are reporting odds ratios with 95% confidence
intervals on a logarithmic axis; the dashed line marks unity. Red, interval above unity; blue,
interval below unity; grey, interval includes unity. The number of exposed cases is given at the
right.

**Figure 3.** Preferred terms within the optic-nerve query, alongside the pre-specified negative
controls and the non-specific ocular comparators. Terms with fewer than three exposed cases are
not plotted. Conventions as in Figure 2.

**Figure 4.** Sensitivity of the optic-nerve estimate to exposure role and reporting period. The
upper four rows compare the preferred term and the query under all-role and suspect-only exposure;
the lower two split the cohort by receipt year at 2016. Conventions as in Figure 2.
"""

anchor = '**Acknowledgements.** None.\n"""'
assert anchor in s, "statements end not found"
if "## Figure legends" in s:
    print("legends already present")
else:
    s = s.replace(anchor, '**Acknowledgements.** None.\n' + LEGENDS + '"""', 1)
    p.write_text(s, encoding="utf-8")
    print("figure legends restored")
