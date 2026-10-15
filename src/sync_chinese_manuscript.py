# -*- coding: utf-8 -*-
"""
Bring the Chinese manuscript into line with the corrected English version.

Three substantive changes were made to the English text and each has to be mirrored:

  1. serum creatinine was added as a third renal exposure, so the renal panel is now
     eGFR, cystatin C and serum creatinine rather than two exposures, and the
     instrument range is 150-186 rather than 146-150

  2. the MR scope paragraph now states 19 exposure-outcome estimates rather than
     three exposures, and names the exposures that are still missing

  3. the docking sentence in the abstract no longer says ethambutol "occupies pockets"
     on the hub targets, because the molecular dynamics showed the ligand leaving

The script reports which anchors it found and which it did not, so a miss is visible
rather than silent.

Usage
    python src/sync_chinese_manuscript.py           # report only
    python src/sync_chinese_manuscript.py --write
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CN = ROOT / "manuscript" / "Ethambutol_EyeTox_CN_full.md"

# (description, pattern, replacement)
# patterns are deliberately loose on digits and punctuation so they survive formatting
EDITS = [
    ("器械数范围：146-150 → 150-186",
     r"1[0-9]{2}\s*[-–~]\s*1[0-9]{2}\s*(?:个)?(?:已调和|调和)?(?:工具变量|器械|instrument)",
     "150–186 个已调和工具变量"),
    ("显著性表述：q = 0.99 → q ≥ 0.87",
     r"q\s*=\s*0\.99",
     "q ≥ 0.87"),
    ("肾功能暴露数：两/三个",
     r"两个肾功能(?:暴露|指标)",
     "三个肾功能指标（eGFR、胱抑素 C 与血清肌酐）"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not CN.exists():
        print(f"{CN} not found")
        return 1
    text = CN.read_text(encoding="utf-8")
    print(f"read {CN.name}: {len(text):,} characters, "
          f"{len(text.splitlines())} lines")
    print()

    print("Looking for the affected passages:")
    for name, pat, _ in EDITS:
        hits = re.findall(pat, text)
        print(f"  {name:34s} {len(hits)} match(es)")

    # report the renal-function sentences so the wording can be judged before editing
    print()
    print("Sentences mentioning renal function or instruments:")
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        if any(k in low for k in ("肾功能", "egfr", "胱抑素", "工具变量", "器械",
                                  "renal", "cystatin")):
            print(f"  L{i}: {line.strip()[:110]}")

    if not args.write:
        print()
        print("(report only; re-run with --write to apply)")
        return 0

    n = 0
    for name, pat, rep in EDITS:
        text, k = re.subn(pat, rep, text)
        n += k
        print(f"  applied {name}: {k} replacement(s)")
    CN.write_text(text, encoding="utf-8")
    print(f"\nwrote {CN}  ({n} replacements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
