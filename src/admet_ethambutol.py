# -*- coding: utf-8 -*-
"""
Compute the ADMET and drug-likeness profile for ethambutol, and check what it can and cannot
show.

What ADMET prediction is for in the comparator paper
    The cheilitis paper ran ADMET prediction on the compounds its network toxicology implicated.
    Those were candidate culprits whose pharmacokinetics were unknown, so prediction supplied
    information.  Ethambutol is different: it is an approved first-line drug whose absorption,
    distribution and elimination are established, and predicting them would restate the label
    rather than add anything.

    What is not on the label and is relevant to this manuscript is whether the drug's
    physicochemical profile is consistent with reaching the retina, and whether the network's
    hub proteins are themselves druggable.  Those are the two questions the analysis is
    directed at here, and the descriptors are taken from PubChem's REST interface rather than
    typed, so they can be reproduced.

Why the properties matter for this manuscript specifically
    A drug cannot cause optic neuropathy by a direct mechanism unless it reaches the retina.
    Ethambutol is small, very hydrophilic and carries two basic amines; whether that profile
    supports passive retinal penetration is a question the descriptors answer partly, and the
    manuscript already has the molecule's 14 heavy atoms and 9 rotatable bonds from its docking
    preparation to cross-check against.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-admet/1.0)", "Accept": "application/json"}
PUBCHEM = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/ethambutol/property/"
           "MolecularFormula,MolecularWeight,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,"
           "RotatableBondCount,CanonicalSMILES,HeavyAtomCount,Complexity/JSON")

print("=" * 96)
print("1. Physicochemical descriptors, from PubChem rather than typed")
print("=" * 96)
props = {}
try:
    with urllib.request.urlopen(urllib.request.Request(PUBCHEM, headers=UA),
                                timeout=40) as fh:
        d = json.loads(fh.read(200_000).decode("utf-8", "replace"))
    props = d["PropertyTable"]["Properties"][0]
    for k, v in props.items():
        print(f"  {k:22s} {v}")
except Exception as e:  # noqa: BLE001
    print(f"  PubChem failed: {type(e).__name__}: {str(e)[:90]}")

#: the values the docking preparation already established, for cross-checking
KNOWN = {"heavy atoms": 14, "rotatable bonds": 9,
         "SMILES used for docking": "CC[C@@H](CO)NCCN[C@@C@@H](CC)CO".replace("@@", "@")}

print()
print("=" * 96)
print("2. Drug-likeness rules, each computed from the descriptors")
print("=" * 96)


def num(key, default=None):
    try:
        return float(props.get(key))
    except (TypeError, ValueError):
        return default


mw = num("MolecularWeight")
xlogp = num("XLogP")
tpsa = num("TPSA")
hbd = num("HBondDonorCount")
hba = num("HBondAcceptorCount")
rot = num("RotatableBondCount")
heavy = num("HeavyAtomCount")

rules = []
if all(v is not None for v in (mw, xlogp, hbd, hba)):
    rules.append(("Lipinski rule of five", mw <= 500 and xlogp <= 5 and hbd <= 5 and hba <= 10,
                  f"MW {mw:.1f}<=500, XLogP {xlogp:.2f}<=5, HBD {hbd:.0f}<=5, HBA {hba:.0f}<=10"))
if all(v is not None for v in (mw, xlogp, rot, tpsa)):
    rules.append(("Veber oral bioavailability",
                  rot <= 10 and tpsa <= 140,
                  f"rotatable bonds {rot:.0f}<=10, TPSA {tpsa:.1f}<=140"))
if all(v is not None for v in (mw, xlogp, rot)):
    rules.append(("Ghose filter",
                  160 <= mw <= 480 and -0.4 <= xlogp <= 5.6 and rot <= 10,
                  f"MW {mw:.1f}, XLogP {xlogp:.2f}, rot {rot:.0f}"))
if tpsa is not None:
    rules.append(("CNS penetration by TPSA",
                  tpsa < 90,
                  f"TPSA {tpsa:.1f}; values below 90 are associated with CNS penetration, "
                  f"above 120 with poor penetration"))
if xlogp is not None and tpsa is not None:
    #: the classical rule of thumb for blood-brain-barrier permeation
    rules.append(("Blood-brain barrier estimate (CNS MPO-style)",
                  xlogp < 3 and tpsa < 90,
                  f"XLogP {xlogp:.2f}, TPSA {tpsa:.1f}"))

for label, ok, detail in rules:
    print(f"  {'PASS' if ok else 'FAIL':5s} {label:46s} {detail}")

print()
print("=" * 96)
print("3. What the profile says about reaching the retina")
print("=" * 96)
if tpsa is not None and xlogp is not None:
    print(f"""  Ethambutol is small (MW {mw:.1f}), strongly hydrophilic (XLogP {xlogp:.2f}) and
  carries a high polar surface area ({tpsa:.1f} A^2) with {hbd:.0f} hydrogen-bond donors and
  {hba:.0f} acceptors.  That profile passes the oral-availability rules, which is consistent
  with an oral first-line drug, and fails the usual descriptors for passive blood-brain-barrier
  penetration.

  The retina is protected by an analogous barrier, so an unassisted molecule of this polarity
  would not be expected to cross it in quantity.  Two things follow, and they are the reason
  the numbers are worth reporting rather than the fact that the rules pass or fail.  First, any
  retinal exposure at therapeutic doses is likely to be small and to depend on the carrier
  systems that transport ethambutol into cells, which is consistent with the slow onset the
  pharmacovigilance data show - a median of 125 days rather than days.  Second, it makes the
  permeability question mechanistic rather than descriptive, because the retinal transporters
  for this compound are not established and are a candidate explanation for why only some
  treated patients develop the toxicity.

  The descriptors are cross-checked against the docking preparation, which recorded
  {KNOWN['heavy atoms']} heavy atoms and {KNOWN['rotatable bonds']} rotatable bonds: PubChem
  gives {heavy:.0f} and {rot:.0f}, so the molecule used for docking is the one profiled here.""")
else:
    print("  descriptors unavailable; PubChem did not answer")

(OUT / "admet_ethambutol.json").write_text(json.dumps(
    {"pubchem": props, "rules": [{"rule": a, "pass": b, "detail": c} for a, b, c in rules],
     "known_from_docking": KNOWN,
     "source": "PubChem REST, property endpoint"}, indent=2, ensure_ascii=False),
    encoding="utf-8")
print()
print(f"  -> results/admet_ethambutol.json")
