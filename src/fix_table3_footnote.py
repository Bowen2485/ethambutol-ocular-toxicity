# -*- coding: utf-8 -*-
"""Replace the Table 3 footnote: the Canadian outcome is an exploratory composite, and 1,308 is a
database-wide count of reports carrying the term, not a count of exposed reports."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
can = json.loads((ROOT / "results" / "canada_vigilance_ethambutol.json").read_text(encoding="utf-8"))
n_terms = len(can["optic_terms"])
n_event = can["n_optic"]
n_exposed = can["cells"][0]["a"]

p = ROOT / "src" / "build_tads_manuscript.py"
s = p.read_text(encoding="utf-8")
start = s.index("ROR, reporting odds ratio.")
end_marker = "across systems: the proportion of reports naming the drug as suspect differs by system."
end = s.index("\n", s.index(end_marker, start))
new = (
    "ROR, reporting odds ratio. The Canadian outcome is an exploratory composite of every preferred\n"
    f"term containing the string OPTIC ({n_terms} such terms appear in the extract); it is not the\n"
    "45-term query and includes terms of different clinical meaning. A total of\n"
    f"{n_event:,} reports in the full Canada Vigilance database carried at least one of these\n"
    f"terms, and {n_exposed} of those reports named ethambutol. The JADER rows report the "
    "term-specific\n"
    "estimate; cataract, glaucoma and dry eye were null or below unity in the same analysis. The two\n"
    "FAERS period rows use that period's own de-duplicated case count as the reference population.\n"
    "Estimates are not compared across systems: the proportion of reports naming the drug as suspect\n"
    "differs by system."
)
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("table 3 footnote replaced")
print(new)
