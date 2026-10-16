# -*- coding: utf-8 -*-
"""
Analyse the GeneCards export once it is filled in, mirroring the DisGeNET analysis exactly.

The point of asking for a second database
    The DisGeNET check found 18 of 33 hub genes with an eye-disease annotation against 4 of 33
    controls, odds ratio 7.82, Fisher P = 2.6e-4, after removing matches that were artefacts
    of keyword matching.  A second database either reproduces that or contradicts it, and
    either is worth having: a reproduction strengthens the claim that the network's nodes are
    ocular, and a contradiction would mean the DisGeNET result is a property of that database's
    disease vocabulary rather than of the network.

Why the disease names are requested and not only a yes/no
    On the DisGeNET data, "keratosis" and "dyskeratosis congenita" matched an ocular keyword
    while being skin diseases, and "cataract and cardiomyopathy" is a syndrome classified
    under its cardiac feature.  Removing those matches moved the result from 61% to 55%.  If
    only a yes/no were recorded, that audit could not be repeated here and the two databases
    would not be comparable - the DisGeNET figure would have been corrected and the GeneCards
    one would not.

Refusal to run on an unfilled file
    The template ships with the three genecards_ columns empty.  An analysis run against it
    would report zero eye associations for every gene and would look like a null result.  The
    script therefore stops and says so rather than producing that number.
"""
from __future__ import annotations

import csv
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "results" / "genecards_search_list.csv"
DISGENET = ROOT / "results" / "disgenet_hub_annotation.json"

#: the same ocular stems the DisGeNET analysis used, so the two are comparable
EYE_RE = ("retin", "optic", "macula", "ocular", "eye", "glaucom", "uveit", "choroid",
          "conjunctiv", "cornea", "leber", "stargardt", "cone-rod", "photoreceptor",
          "visual", "cataract", "kerat", "amblyop", "nyctalop", "colour blind",
          "color blind", "achromatops")
#: names that match a stem while being something else.  Carried over from the DisGeNET audit,
#: where removing them changed the count, and listed here so the same correction is applied.
SUSPECT = ("keratosis", "dyskeratosis", "cataract and cardiomyopathy")


def fisher_one_sided(a: int, b: int, c: int, d: int) -> float:
    return sum(comb(a + c, k) * comb(b + d, (a + b) - k) / comb(a + b + c + d, a + b)
               for k in range(a, min(a + b, a + c) + 1))


def main() -> None:
    if not WORK.exists():
        raise SystemExit(f"worklist not found: {WORK}")
    rows = list(csv.DictReader(WORK.open(encoding="utf-8-sig")))

    filled = [r for r in rows if (r.get("genecards_eye_related") or "").strip()]
    if not filled:
        print("=" * 96)
        print("The worklist has not been filled in yet")
        print("=" * 96)
        print(f"  file: {WORK.relative_to(ROOT)}")
        print(f"  rows: {len(rows)}, of which filled: 0")
        print()
        print("  Stopping rather than analysing it.  Every gene would count as having no eye")
        print("  association and the output would read as a null result, which is the one")
        print("  number this run must not produce.")
        print()
        print("  Fill genecards_eye_related with yes or no for each gene - and")
        print("  genecards_diseases with the eye-related disease names, which is what allows")
        print("  the keyword audit to be repeated here.")
        return
    if len(filled) < len(rows):
        print(f"  note: {len(filled)} of {len(rows)} rows are filled; the rest are excluded")

    print("=" * 96)
    print("1. Eye associations in the GeneCards export")
    print("=" * 96)

    for group in ("hub", "control"):
        sub = [r for r in filled if r["group"] == group]
        flagged = []
        for r in sub:
            names = [n.strip() for n in (r.get("genecards_diseases") or "").split(";")
                     if n.strip()]
            # the flag is derived from the recorded names when they are present, so a
            # disagreement between the yes/no and the names is caught rather than averaged
            by_name = any(any(k in n.lower() for k in EYE_RE) for n in names)
            stated = (r.get("genecards_eye_related") or "").strip().lower().startswith("y")
            if names and by_name != stated:
                print(f"  DISAGREEMENT {r['symbol']}: marked "
                      f"{'yes' if stated else 'no'}, names suggest "
                      f"{'yes' if by_name else 'no'}  -> {names[:3]}")
            if stated or by_name:
                flagged.append((r["symbol"], names, stated, by_name))
        print(f"\n  {group}: {len(flagged)} of {len(sub)} with an eye association")
        for sym, names, stated, by_name in flagged:
            clean = [n for n in names if not any(s in n.lower() for s in SUSPECT)]
            tag = "" if len(clean) == len(names) else "   (some matches questionable)"
            print(f"      {sym:10s} {', '.join(names[:3])[:66]}{tag}")

    hub_rows = [r for r in filled if r["group"] == "hub"]
    ctrl_rows = [r for r in filled if r["group"] == "control"]

    def count(rs, strict: bool) -> int:
        n = 0
        for r in rs:
            names = [x.strip() for x in (r.get("genecards_diseases") or "").split(";")
                     if x.strip()]
            if strict:
                names = [x for x in names
                         if not any(s in x.lower() for s in SUSPECT)]
            if (r.get("genecards_eye_related") or "").strip().lower().startswith("y") \
                    or any(any(k in x.lower() for k in EYE_RE) for x in names):
                n += 1
        return n

    a_any, c_any = count(hub_rows, False), count(ctrl_rows, False)
    a_str, c_str = count(hub_rows, True), count(ctrl_rows, True)
    p_any = fisher_one_sided(a_any, len(hub_rows) - a_any,
                             c_any, len(ctrl_rows) - c_any)
    p_str = fisher_one_sided(a_str, len(hub_rows) - a_str,
                             c_str, len(ctrl_rows) - c_str)

    print()
    print("=" * 96)
    print("2. Against the DisGeNET result")
    print("=" * 96)
    print(f"  {'source':32s} {'hubs':>10s} {'controls':>10s} {'Fisher P':>12s}")
    print(f"  {'GeneCards, any match':32s} "
          f"{a_any}/{len(hub_rows):<8d} {c_any}/{len(ctrl_rows):<8d} {p_any:>12.3e}")
    print(f"  {'GeneCards, questionable removed':32s} "
          f"{a_str}/{len(hub_rows):<8d} {c_str}/{len(ctrl_rows):<8d} {p_str:>12.3e}")
    if DISGENET.exists():
        d = json.loads(DISGENET.read_text(encoding="utf-8"))
        print(f"  {'DisGeNET, any match':32s} "
              f"{d['n_hub_eye']}/33{'':<5d} {d['n_ctrl_eye']}/33{'':<5d} "
              f"{d['fisher_any']:>12.3e}")
        print(f"  {'DisGeNET, questionable removed':32s} "
              f"{d['n_hub_strong'] if False else d.get('n_hub_strong', 0)}"
              f"/33{'':<5d} "
              f"{d.get('n_ctrl_strong', 0)}/33{'':<5d} "
              f"{d.get('fisher_strong', 0):>12.3e}")

    print()
    print("=" * 96)
    print("3. What the two databases together say")
    print("=" * 96)
    out = {"genecards_any": {"hubs": a_any, "controls": c_any, "p": p_any},
           "genecards_strict": {"hubs": a_str, "controls": c_str, "p": p_str},
           "n_hub_rows": len(hub_rows), "n_control_rows": len(ctrl_rows)}
    (ROOT / "results" / "genecards_analysis.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    if a_str > c_str and p_str < 0.05:
        print("  GeneCards reproduces the direction and significance of the DisGeNET result.")
        print("  Two independent disease vocabularies agreeing is stronger than either alone,")
        print("  and the manuscript can state the check without qualification.")
    elif a_str > c_str:
        print("  GeneCards shows the same direction without reaching significance.  That is a")
        print("  weaker reproduction and should be reported as such, with both intervals.")
    else:
        print("  GeneCards does not reproduce the result.  That would mean the DisGeNET")
        print("  finding is a property of that database's disease vocabulary rather than of")
        print("  the network, and the manuscript's claim would have to be narrowed to say so.")
    print()
    print(f"  -> results/genecards_analysis.json")


if __name__ == "__main__":
    main()
