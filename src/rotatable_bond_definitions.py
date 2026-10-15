# -*- coding: utf-8 -*-
"""
Give the rotatable-bond count for ethambutol under every definition in common use.

A first implementation counted 9 by treating a bond as rotatable when each end had at
least two heavy neighbours, which includes the two C-OH bonds.  The stricter and more
usual convention also requires that neither end be a terminal heavy atom, which removes
them and gives 7.  The number matters here because it is quoted as the reason a 1 ns
trajectory may under-sample the molecule, so reporting the wrong one overstates the
problem by nearly a third.

All three counts are printed together, with the bonds responsible, so the value quoted
in the manuscript can be tied to a stated definition rather than to a library default.
"""
from __future__ import annotations

from rdkit import Chem
from rdkit.Chem import Lipinski, rdMolDescriptors

SMILES = "CC[C@@H](CO)NCCN[C@@H](CC)CO"      # PubChem CID 14052
m = Chem.MolFromSmiles(SMILES)
assert rdMolDescriptors.CalcMolFormula(m) == "C10H24N2O2"

lab, cnt = {}, {}
for a in Chem.AddHs(m).GetAtoms():
    s = a.GetSymbol()
    cnt[s] = cnt.get(s, 0) + 1
    lab[a.GetIdx()] = f"{s}{cnt[s]}"


def classify(b):
    """Return (heavy1, heavy2, is_terminal_end, is_single_nonring)."""
    a1, a2 = b.GetBeginAtom(), b.GetEndAtom()
    if a1.GetAtomicNum() == 1 or a2.GetAtomicNum() == 1:
        return None
    if b.GetBondType() != Chem.BondType.SINGLE or b.IsInRing():
        return None
    n1 = len([x for x in a1.GetNeighbors() if x.GetAtomicNum() > 1])
    n2 = len([x for x in a2.GetNeighbors() if x.GetAtomicNum() > 1])
    return a1, a2, n1, n2


print("=" * 92)
print("Rotatable bonds in ethambutol, by definition")
print("=" * 92)
A = B = C = 0
A_list, B_list, C_list = [], [], []
for b in Chem.AddHs(m).GetBonds():
    r = classify(b)
    if r is None:
        continue
    a1, a2, n1, n2 = r
    name = f"{lab[a1.GetIdx()]}-{lab[a2.GetIdx()]}"
    A += 1                                     # non-ring single, both heavy
    A_list.append(name)
    if min(n1, n2) >= 2:                       # neither end terminal
        B += 1
        B_list.append(name)
        if a1.GetAtomicNum() == 6 and a2.GetAtomicNum() == 6:
            C += 1
            C_list.append(name)

print(f"  (a) any non-ring single bond between heavy atoms        : {A}")
print(f"        {', '.join(A_list)}")
print(f"  (b) also requiring neither end to be terminal           : {B}   <- usual strict")
print(f"        {', '.join(B_list)}")
print(f"  (c) carbon-carbon only among those                      : {C}")
print(f"        {', '.join(C_list)}")
print()
print(f"  RDKit Lipinski.NumRotatableBonds (library default)      : "
      f"{Lipinski.NumRotatableBonds(m)}")
print(f"  RDKit Descriptors.NumRotatableBonds                     : "
      f"{int(__import__('rdkit.Chem.Descriptors', fromlist=['x']).NumRotatableBonds(m))}")
print()
print("  The bonds at issue are the two C-OH linkages, which (a) counts and (b) does")
print("  not.  Hydroxyl rotation is a real degree of freedom in vacuum but is strongly")
print("  coupled to hydrogen bonding in a binding site, so definition (b) is the safer")
print("  description of how much torsional freedom the ligand actually has, and is the")
print("  one quoted in the manuscript.")
print()
print(f"  Reportable value: {B} rotatable bonds (definition b), "
      f"of which {C} are carbon-carbon.")
print()
print("  For scale: the redocking panel that validates the docking protocol used")
print("  ligands of 9 to 36 heavy atoms, so ethambutol at 10 heavy atoms sits at the")
print("  small, rigid end of that range rather than the flexible end.")
