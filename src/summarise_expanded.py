# -*- coding: utf-8 -*-
"""Summarise the expanded-panel run: what changed relative to the curated panel."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived"
RES = ROOT / "results"

sig = pd.read_csv(RES / "faers_signals_ethambutol.csv", encoding="utf-8-sig")
cur = {r["term"] for r in json.loads(
    (DER / "ocular_terms_curated_backup.json").read_text(encoding="utf-8"))}
panel = pd.read_csv(DER / "ocular_terms.csv", encoding="utf-8-sig")

print(f"panel tested with a >= 3 : {len(sig)}")
print(f"strict signals           : {int(sig.signal_strict.sum())}")
on = sig[sig.term == "OPTIC NEUROPATHY"].iloc[0]
print(f"OPTIC NEUROPATHY         : a={int(on.a)} "
      f"ROR={on.ror:.2f} ({on.ror_lcl:.2f}-{on.ror_ucl:.2f}) "
      f"PRR={on.prr:.2f} IC025={on.ic025:.2f} EBGM05={on.ebgm05:.2f}")

print(f"\nsignals in the curated 73-term panel : "
      f"{int(sig[sig.term.isin(cur)].signal_strict.sum())}")
print(f"signals only in the data-driven terms: "
      f"{int(sig[~sig.term.isin(cur)].signal_strict.sum())}")

new = sig[(~sig.term.isin(cur)) & (sig.signal_strict == True)]  # noqa: E712
print("\n=== new strict signals contributed by the data-driven terms ===")
print(new.nlargest(20, "ror")[["term", "group", "a", "ror", "ror_lcl",
                               "ic025", "ebgm05"]]
      .to_string(index=False, max_colwidth=32))

print("\n=== interpretation check on the new terms ===")
for t in ["OCULAR ICTERUS", "MACULE", "CATARACT SUBCAPSULAR", "CORNEAL OPACITY",
          "OPHTHALMOPLEGIA", "VITREOUS DETACHMENT", "CONJUNCTIVAL HYPERAEMIA",
          "RASH MACULAR"]:
    row = sig[sig.term == t]
    if row.empty:
        print(f"  {t:24s} not tested")
        continue
    r = row.iloc[0]
    print(f"  {t:24s} a={int(r.a):>4} ROR={r.ror:>8.2f} "
          f"IC025={r.ic025:>5.2f} signal={bool(r.signal_strict)}")

# specificity controls unchanged?
print("\n=== non-signal controls (must stay null) ===")
for t in ["CATARACT", "DRY EYE", "GLAUCOMA", "EYE PAIN", "CONJUNCTIVITIS",
          "VISION BLURRED", "PHOTOPHOBIA", "EYE IRRITATION"]:
    row = sig[sig.term == t]
    if row.empty:
        continue
    r = row.iloc[0]
    print(f"  {t:20s} a={int(r.a):>4} ROR={r.ror:>6.2f} signal={bool(r.signal_strict)}")

# save the focused table used in the manuscript
keep = ["term", "group", "a", "n_drug", "n_event", "ror", "ror_lcl", "ror_ucl",
        "prr", "chi2_yates", "ic025", "ebgm05", "q_bh", "signal_ror",
        "signal_prr", "signal_ic", "signal_strict"]
sig[[c for c in keep if c in sig.columns]].to_csv(
    ROOT / "tables" / "Table2_signals_full_panel.csv", index=False,
    encoding="utf-8-sig")
sig[sig.signal_strict == True].nlargest(30, "ror")[  # noqa: E712
    [c for c in keep if c in sig.columns]].to_csv(
    ROOT / "tables" / "Table2b_signals_strict.csv", index=False,
    encoding="utf-8-sig")
print(f"\n-> tables/Table2_signals_full_panel.csv ({len(sig)} rows)")
print(f"-> tables/Table2b_signals_strict.csv "
      f"({int(sig.signal_strict.sum())} rows)")
