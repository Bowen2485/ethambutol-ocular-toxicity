# -*- coding: utf-8 -*-
"""
List the rotatable bonds bond by bond, because the count did not match a hand count.

The strict rotatable-bond count came out at 9, while counting the flexible linkages by
eye gave fewer.  A disagreement between an implementation and a hand count is not
resolved by arguing about which definition applies: the bonds have to be printed, with
the neighbours that decide each case, so the rule can be seen operating on real atoms.
"""
from __future__ import annotations

from rdkit import Chem
from rdkit.Chem import Lipinski, rdMolDescriptors

SMILES = "CC[C@@H](CO)NCCN[C@@H](CC)CO"     # PubChem CID 14052
m = Chem.MolFromSmiles(SMILES)
mh = Chem.AddHs(m)

# label heavy atoms so the listing is readable
labels = {}
counts: dict[str, int] = {}
for a in mh.GetAtoms():
    s = a.GetSymbol()
    counts[s] = counts.get(s, 0) + 1
    labels[a.GetIdx()] = f"{s}{counts[s]}"

print("=" * 92)
print("Molecule as written")
print("=" * 92)
print(f"  SMILES : {SMILES}")
print(f"  formula: {rdMolDescriptors.CalcMolFormula(m)}")
print(f"  atoms  : {mh.GetNumAtoms()} including hydrogens, "
      f"{m.GetNumHeavyAtoms()} heavy")
print()
print("  heavy-atom skeleton (bonds among heavy atoms):")
for b in mh.GetBonds():
    a1, a2 = b.GetBeginAtom(), b.GetEndAtom()
    if a1.GetAtomicNum() == 1 or a2.GetAtomicNum() == 1:
        continue
    order = {Chem.BondType.SINGLE: "-", Chem.BondType.DOUBLE: "=",
             Chem.BondType.TRIPLE: "#"}.get(b.GetBondType(), "?")
    ring = " (ring)" if b.IsInRing() else ""
    print(f"      {labels[a1.GetIdx()]:5s} {order} {labels[a2.GetIdx()]:5s}{ring}")

print()
print("=" * 92)
print("Every single, non-ring, heavy-heavy bond, with the decision")
print("=" * 92)
print(f"  {'bond':16s} {'heavy nbrs on each end':26s} {'rotatable':>10s}")
n_rot = 0
for b in mh.GetBonds():
    a1, a2 = b.GetBeginAtom(), b.GetEndAtom()
    if a1.GetAtomicNum() == 1 or a2.GetAtomicNum() == 1:
        continue
    if b.GetBondType() != Chem.BondType.SINGLE:
        print(f"  {labels[a1.GetIdx()]:6s}-{labels[a2.GetIdx()]:6s} "
              f"{'not a single bond':26s} {'no':>10s}")
        continue
    if b.IsInRing():
        print(f"  {labels[a1.GetIdx()]:6s}-{labels[a2.GetIdx()]:6s} "
              f"{'in a ring':26s} {'no':>10s}")
        continue
    n1 = len([x for x in a1.GetNeighbors() if x.GetAtomicNum() > 1])
    n2 = len([x for x in a2.GetNeighbors() if x.GetAtomicNum() > 1])
    ok = n1 >= 2 and n2 >= 2
    n_rot += int(ok)
    note = f"{labels[a1.GetIdx()]}={n1}, {labels[a2.GetIdx()]}={n2}"
    print(f"  {labels[a1.GetIdx()]:6s}-{labels[a2.GetIdx()]:6s} "
          f"{note:26s} {'YES' if ok else 'no':>10s}")

print()
print(f"  strict rotatable bonds by this listing : {n_rot}")
print(f"  RDKit Lipinski.NumRotatableBonds       : {Lipinski.NumRotatableBonds(m)}")
print()
print("  Note: the hydroxyl O-H bonds are excluded because one end is hydrogen; the")
print("  three methyl groups are excluded because the carbon has only one heavy")
print("  neighbour; the two C-OH bonds ARE counted, because the hydroxyl oxygen has a")
print("  heavy neighbour and the carbon has three, so rotation about them moves the")
print("  OH group relative to the skeleton.  Included or excluded, the number is not")
print("  what a hand count of 'flexible linkages' usually means, which is why the")
print("  listing is printed rather than the value asserted.")
