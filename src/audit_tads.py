# -*- coding: utf-8 -*-
"""Check the assembled manuscript for the errors that matter before submission.

    every in-text citation has a reference-list entry and every entry is cited
    the abstract is within the journal limit
    the main text is within the journal limit
    no placeholder text survives
    the numbers quoted in the Results agree with results/main_results.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "manuscript" / "TADS_manuscript.md").read_text(encoding="utf-8")
d = json.loads((ROOT / "results" / "main_results.json").read_text(encoding="utf-8"))

problems: list[str] = []
ok: list[str] = []


def check(cond: bool, msg: str) -> None:
    (ok if cond else problems).append(msg)


# ---------------------------------------------------------------- citations
body = text[:text.find("## References")]
refs_block = text[text.find("## References"):]
listed = {int(m.group(1)) for m in re.finditer(r"^(\d{1,2})\.\s+\S", refs_block, re.M)}
cited: set[int] = set()
for m in re.finditer(r"\[(\d+(?:,\d+)*)\]", body):
    cited.update(int(x) for x in m.group(1).split(","))
check(not (cited - listed), f"cited but not listed: {sorted(cited - listed)}")
check(not (listed - cited), f"listed but not cited: {sorted(listed - cited)}")
check(len(listed) == 18, f"reference count: {len(listed)}")

# ------------------------------------------------------------------ lengths
abs_block = text[text.find("## Abstract"):text.find("**Keywords")]
abs_words = len([w for w in re.sub(r"[#*]", " ", abs_block).split() if re.search(r"\w", w)])
check(abs_words <= 300, f"abstract words: {abs_words} (limit 300)")

main = text[text.find("## 1. Introduction"):text.find("## Statements")]
main_words = len([w for w in re.sub(r"[#*|]", " ", main).split() if re.search(r"\w", w)])
check(main_words <= 6000, f"main text words: {main_words:,} (limit 6,000)")

# --------------------------------------------------------------- placeholders
for pat in (r"\bTODO\b", r"\bTBD\b", r"PLACEHOLDER", r"待补", r"XXX"):
    check(not re.search(pat, text), f"no {pat} marker")

# ------------------------------------------------------------ key numbers
smq = next(r for r in d["smq"] if r["smq"].startswith("Optic nerve"))
on = next(r for r in d["pt"] if r["term"] == "Optic neuropathy")
checks = {
    "23.51": f"{smq['ror']:.2f}",
    "21.35": f"{smq['ror_lcl']:.2f}",
    "116.58": f"{on['ror']:.2f}",
    "99.36": f"{on['ror_lcl']:.2f}",
}
for quoted, computed in checks.items():
    check(quoted in text and quoted == computed,
          f"{quoted} quoted and computed ({computed})")

for k in ("n_ethambutol", "N"):
    pass
check("15,510" in text and d["n_ethambutol"] == 15_510, "cohort 15,510")
check("20,692,683" in text and d["N"] == 20_692_683, "de-duplicated cases 20,692,683")

print(f"abstract {abs_words} words; main text {main_words:,} words; {len(listed)} references")
for m in ok:
    print(f"  OK   {m}")
if problems:
    print("\nFAILURES:")
    for p in problems:
        print(f"  FAIL {p}")
    raise SystemExit(1)
print(f"\nALL {len(ok)} CHECKS PASSED")
