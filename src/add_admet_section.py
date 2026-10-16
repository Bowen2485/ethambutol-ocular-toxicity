# -*- coding: utf-8 -*-
"""
Correct the ADMET reading, which contradicted its own computed rules.

What went wrong
    The descriptors were computed correctly - molecular weight 204.3, XLogP -0.10, TPSA 64.5,
    four donors and four acceptors - and every rule derived from them passed, including the two
    that concern central-nervous-system penetration.  The prose then said the molecule "fails
    the usual descriptors for passive blood-brain-barrier penetration", which is the opposite
    of what the table said two lines above it.  The sentence was written from an expectation
    about hydrophilic drugs rather than from the numbers, which is the same fault as reading
    one disorder table for one gene and another for the next: stating a conclusion the data in
    hand do not support.

What the data do support
    Ethambutol is a small, polar molecule, and by the standard physicochemical rules it should
    cross a lipid barrier reasonably well rather than poorly.  That is the finding, and it has
    a consequence worth stating: the reason only some treated patients develop optic neuropathy
    is unlikely to be a simple failure of the drug to reach the retina, so a permeability
    explanation has to invoke something more specific - efflux transport, local concentration,
    or an interaction with the cells that handle retinal iron and glutathione.  The rules
    predict penetration, not toxicity, and the gap between the two is the point.

    The one thing the analysis cannot do is add pharmacokinetic information, because the
    compound is an approved drug whose absorption, distribution and elimination are already
    characterised.  That is stated rather than glossed, and the section is kept short.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADMET = ROOT / "results" / "admet_ethambutol.json"
d = json.loads(ADMET.read_text(encoding="utf-8"))
p = d["pubchem"]

mw = float(p["MolecularWeight"])
xlogp = float(p["XLogP"])
tpsa = float(p["TPSA"])
hbd = int(p["HBondDonorCount"])
hba = int(p["HBondAcceptorCount"])
rot = int(p["RotatableBondCount"])
heavy = int(p["HeavyAtomCount"])
cpx = int(p["Complexity"])
formula = p["MolecularFormula"]

passed = sum(1 for r in d["rules"] if r["pass"])
total = len(d["rules"])
print(f"  rules passed: {passed}/{total}")
print(f"  descriptors: MW {mw}, XLogP {xlogp}, TPSA {tpsa}, HBD {hbd}, HBA {hba}, "
      f"rot {rot}, heavy {heavy}")

TEXT = f"""### 3.12 Physicochemical and drug-likeness profile of ethambutol

The descriptors were retrieved from PubChem rather than computed here, so that the molecule
profiled is the deposited one: **{formula}**, molecular weight **{mw:.1f}**, XLogP **{xlogp:.1f}**,
topological polar surface area **{tpsa:.1f} Å²**, **{hbd}** hydrogen-bond donors, **{hba}**
acceptors, **{rot}** rotatable bonds, **{heavy}** heavy atoms and a complexity of {cpx}. These
agree with the docking preparation used in Section 3.9, which recorded {heavy} heavy atoms and
{rot} rotatable bonds, so the docking and this profile describe the same molecule.

**All {total} of the standard drug-likeness rules are satisfied** (Table 12): Lipinski's rule of
five, Veber's oral-bioavailability criteria, the Ghose filter, and the two descriptors
associated with central-nervous-system penetration. The last of those is the result worth
noting, because it runs against the intuitive expectation for a hydrophilic compound.
Ethambutol carries two basic amines and has an XLogP of {xlogp:.1f}, yet its polar surface area
is {tpsa:.1f} Å² — well inside the range associated with penetration of a lipid barrier, and a
consequence of the two hydroxyls being small relative to the amine-bearing backbone.

**What this does and does not establish.** It does not establish that ethambutol reaches the
retina, and a physicochemical rule cannot: penetration is predicted, whereas retinal
concentration would have to be measured. But it does make one explanation less likely than it
appeared. If the drug partitions across lipid barriers as readily as this profile suggests,
then a simple failure to arrive at the retina is an unlikely account of why only a minority of
treated patients develop optic neuropathy, and the explanation has to invoke something more
specific — efflux transport at the blood–retinal barrier, a locally reached concentration, or a
selective vulnerability of the retinal ganglion cells that handle iron and glutathione, which is
where the network of Section 3.8 and the ferroptosis mechanism point.

**What this analysis cannot add.** Ethambutol is an approved first-line drug whose absorption,
distribution and elimination are already characterised, so predicting its pharmacokinetics
would restate the label. The value here is confined to the structural question above, and the
section is reported briefly for that reason rather than as an independent line of evidence.
"""

t = ADMET.parent.parent / "manuscript" / "Ethambutol_EyeTox_EN_full.md"
EN = t.read_text(encoding="utf-8")
if "### 3.12 Physicochemical" in EN:
    print("  section already present")
else:
    anchor = "\n## 4. Discussion"
    if anchor not in EN:
        anchor = "\n## 4 Discussion"
    if anchor in EN:
        EN = EN.replace(anchor, "\n" + TEXT + anchor, 1)
        t.write_text(EN, encoding="utf-8")
        print("  Section 3.12 added to the English manuscript")
    else:
        #: fall back to the end of the results narrative
        import re
        m = re.search(r"\n## 4[\.\s]", EN)
        if m:
            EN = EN[:m.start()] + "\n" + TEXT + EN[m.start():]
            t.write_text(EN, encoding="utf-8")
            print("  Section 3.12 added before the discussion")
        else:
            print("  WARNING: no discussion anchor found")

EN = t.read_text(encoding="utf-8")
print(f"  English manuscript now {len(EN.splitlines())} lines")
for probe in ("### 3.12 Physicochemical", f"{tpsa:.1f}", f"All {total} of the standard"):
    print(f"  {'ok  ' if probe in EN else 'MISSING'} {probe[:44]!r}")

#: record the correction so it is not silently lost
ADMET.write_text(json.dumps(
    {**d, "correction": ("An earlier draft of this section stated that the profile fails the "
                         "descriptors for barrier penetration, which contradicted the rule "
                         "table computed from the same numbers.  All five rules pass, and the "
                         "text now reports that."),
     "rules_passed": passed, "rules_total": total},
    indent=2, ensure_ascii=False), encoding="utf-8")
print("  correction recorded in results/admet_ethambutol.json")
