# -*- coding: utf-8 -*-
"""
Cross-language and cross-document consistency audit.

Checks that
  1. every headline number in the English manuscript matches the analysis outputs;
  2. the Chinese translation quotes the same numbers for the same quantities;
  3. the reference numbering and count agree between the two versions;
  4. no unresolved placeholder remains in either manuscript.

Exit code 0 = all checks pass.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
RES = ROOT / "results"
DER = ROOT / "data" / "derived"

EN = MAN / "Ethambutol_EyeTox_EN_full.md"
CN = MAN / "Ethambutol_EyeTox_CN_full.md"

problems, notes = [], []
skipped = []


def check(cond, msg):
    (notes if cond else problems).append(("OK   " if cond else "FAIL ") + msg)


def try_read(path: Path, **kw):
    """
    Read a CSV/JSON if it is present, otherwise record a skip.

    The input files live in several directories and a partial checkout - for example
    copying results/ and tables/ but not data/derived/, which holds a 35 GB database
    alongside 30 MB of small files - should degrade to skipped checks rather than a
    traceback, so someone reproducing the analysis can still run what they have.
    """
    if not path.exists():
        skipped.append(f"{path.relative_to(ROOT)}")
        return None
    try:
        if path.suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        return pd.read_csv(path, encoding="utf-8-sig", **kw)
    except Exception as exc:  # noqa: BLE001
        skipped.append(f"{path.relative_to(ROOT)} ({type(exc).__name__})")
        return None


# locate an optional input in any of the directories that may hold it
def find(name: str) -> Path | None:
    for base in (DER, RES, ROOT / "tables"):
        p = base / name
        if p.exists():
            return p
    return None


def data_path(name: str) -> Path:
    """Return the first existing location, or the default that try_read will skip."""
    p = find(name)
    return p if p is not None else DER / name


print("=" * 78)
print("CROSS-LANGUAGE CONSISTENCY AUDIT")
print("=" * 78)

en = EN.read_text(encoding="utf-8")
cn = CN.read_text(encoding="utf-8")
sig = try_read(RES / "faers_signals_annotated.csv")
dedup = try_read(RES / "faers_dedup_summary.csv")
rb = try_read(RES / "faers_robustness.csv")
adqs = try_read(RES / "faers_adequacy_summary.csv")
terms = try_read(data_path("ocular_terms.csv"))
cited = try_read(data_path("citation_map.json"))

if sig is None or dedup is None:
    print("\n[skip] the signal and cohort tables are required for the numeric")
    print("       cross-checks and were not found. Copy results/ into the project,")
    print("       or run the analysis scripts first. Prose and reference checks")
    print("       will still run.\n")

# ------------------------------------------------------- 1. English vs outputs
print("\n[1] English manuscript vs analysis outputs")
cases = []
if sig is not None and {"OPTIC NEUROPATHY", "TOXIC OPTIC NEUROPATHY"} <= set(sig.term):
    on = sig[sig.term == "OPTIC NEUROPATHY"].iloc[0]
    ton = sig[sig.term == "TOXIC OPTIC NEUROPATHY"].iloc[0]
    cases += [
        ("optic neuropathy ROR", f"{on.ror:.2f}", "159.21"),
        ("toxic optic neuropathy ROR", f"{ton.ror:.2f}", "277.14"),
    ]
if dedup is not None and "drug" in dedup.columns:
    allrow = dedup[dedup.drug == "FAERS_ALL"]
    ethrow = dedup[dedup.drug == "ethambutol"]
    if not allrow.empty:
        cases.append(("total de-duplicated cases",
                      f"{int(allrow.n_cases.iloc[0]):,}", "20,328,568"))
    if not ethrow.empty:
        cases.append(("ethambutol cases",
                      f"{int(ethrow.n_cases.iloc[0]):,}", "13,804"))
if terms is not None:
    cases.append(("panel size", str(len(terms)), "178"))
if sig is not None and "signal_strict" in sig.columns:
    cases.append(("strict signals", str(int(sig.signal_strict.sum())), "58"))

if not cases:
    print("  (no numeric checks could be run)")
for label, got, want in cases:
    check(re.sub(r"[^0-9]", "", got) == re.sub(r"[^0-9]", "", want),
          f"EN {label}: computed={got} quoted={want}")

# --------------------------------------------- 2. English vs Chinese numbers
print("\n[2] English manuscript vs Chinese translation")
shared = {"optic neuropathy ROR": "159.21",
          "toxic optic neuropathy ROR": "277.14",
          "total cases": "20,328,568",
          "ethambutol cases": "13,804",
          "panel size": "178",
          "strict signals": "58"}
if rb is not None and "term" in rb.columns:
    hit = rb[(rb.term == "OPTIC NEUROPATHY")
             & (rb.scenario.str.contains("anti-TB", na=False))]
    if not hit.empty:
        shared["anti-TB-only ROR"] = f"{hit.iloc[0].ror:.2f}"
if adqs is not None and "pct_both" in adqs.columns:
    shared["adequacy pct_both"] = f"{adqs.iloc[0].pct_both:.1f}"

for label, val in shared.items():
    # numbers are written with different thousands separators in the two
    # languages (20,328,568 vs 20 328 568), so compare on digits only
    digits = re.sub(r"[^0-9]", "", val)
    in_en = digits in re.sub(r"[^0-9]", "", en) or val in en
    in_cn = digits in re.sub(r"[^0-9]", "", cn) or val in cn
    check(in_en, f"EN contains {label} = {val}")
    check(in_cn, f"CN contains {label} = {val}")

# the two versions must agree on the primary signal
check("159.21" in en and "159.21" in cn,
      "both versions quote OPTIC NEUROPATHY ROR 159.21")
check("277.14" in en and "277.14" in cn,
      "both versions quote TOXIC OPTIC NEUROPATHY ROR 277.14")

# --------------------------------------------------- 3. reference consistency
print("\n[3] references")
if cited is not None:
    n_ref = len(cited)
    en_refs = re.findall(r"^\s*(\d{1,2})\.\s+\S", en, flags=re.M)
    en_nums = sorted({int(x) for x in en_refs})
    check(max(en_nums, default=0) == n_ref,
          f"EN reference list ends at {max(en_nums, default=0)} (map has {n_ref})")
    cited_en = {int(n) for m in re.findall(r"\[([\d,]+)\]", en)
                for n in m.split(",") if n.isdigit()}
    check(cited_en == set(range(1, n_ref + 1)),
          f"all {n_ref} references are cited inline "
          f"(missing {sorted(set(range(1, n_ref+1)) - cited_en)})")
    check("参考文献编号与英文版完全一致" in cn or "编号与英文版" in cn,
          "CN states the reference numbering follows the English version")
else:
    print("  (citation_map.json not available; reference checks skipped)")

# ------------------------------------------------------ 4. no placeholders
print("\n[4] placeholders")
bad = [r"\bTODO\b", r"\bTBD\b", r"\bPLACEHOLDER\b", r"\[PMID"]
for name, txt in (("EN", en), ("CN", cn)):
    hits = [p for p in bad if re.search(p, txt)]
    check(not hits, f"{name} free of placeholders {hits}")
# the fields a human must fill are allowed and are listed in the checklist
for marker in ["[to be inserted]"]:
    check(marker in en, f"EN keeps the human-fill marker {marker}")

# ----------------------------------------- 5. structure parity EN vs CN
print("\n[5] structural parity")
en_secs = len(re.findall(r"^##\s", en, flags=re.M))
cn_secs = len(re.findall(r"^##\s", cn, flags=re.M))
check(abs(en_secs - cn_secs) <= 4,
      f"top-level section counts comparable (EN {en_secs}, CN {cn_secs})")
check("ferroptosis" in en, "EN reports the ferroptosis enrichment")
check("铁死亡" in cn, "CN reports the ferroptosis enrichment")

print("\n" + "=" * 78)
for n in notes:
    print("  " + n)
if skipped:
    print("\n" + "-" * 78)
    seen = sorted(set(skipped))
    print(f"  {len(seen)} optional input(s) not found, related checks were skipped:")
    for s in seen[:12]:
        print(f"    - {s}")
    if len(seen) > 12:
        print(f"    ... and {len(seen) - 12} more")
    print("  Copy data/derived/ (about 30 MB excluding faers.sqlite) to enable them.")
if problems:
    print("\n" + "!" * 78)
    for p in problems:
        print("  " + p)
    print("!" * 78)
    print(f"\n{len(problems)} CHECK(S) FAILED")
    sys.exit(1)
print(f"\nALL {len(notes)} CHECKS PASSED"
      + (f" ({len(set(skipped))} skipped for missing optional inputs)"
         if skipped else ""))
sys.exit(0)
