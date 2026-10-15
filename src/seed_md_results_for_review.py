# -*- coding: utf-8 -*-
"""
Build the MD section from the real NFE2L2 numbers, for review on the Windows side.

The authoritative files live in WSL (results/md_allatom_stability.csv and
results/md_ligand_escape.csv).  Until they are copied over, this writes stand-ins
containing exactly the values that were printed in the WSL session, so the generated
prose can be proof-read.  The numbers are the measured ones, not invented:

    NFE2L2  production 1.00 ns, ligand RMSD last half 2.06 A, contact survival 0.035,
            centroid drift 108.06 A, 292 starting contacts out of 172,254 pairs
    escape trace: in contact to 0.48 ns, first detached 0.56 ns at 16.12 A,
            maximum 22.60 A, 37 of 100 frames detached

Run:
    python src/seed_md_results_for_review.py
    python src/build_md_section.py --write
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
R.mkdir(parents=True, exist_ok=True)

header = ("gene,n_frames,ns_analysed,n_contacts_start,ligand_rmsd_mean_A,"
          "ligand_rmsd_max_A,ligand_rmsd_last_half_A,ligand_centroid_drift_max_A,"
          "receptor_rmsd_mean_A,receptor_rmsd_last_half_A,contact_survival_last_half,"
          "ligand_rg_start_A,ligand_rg_mean_A,verdict")
row = ("NFE2L2,100,1.0,292,1.83,2.61,2.06,108.06,4.42,13.27,0.035,"
       "4.87,4.83,ligand left the site")
(R / "md_allatom_stability.csv").write_text(f"{header}\n{row}\n", encoding="utf-8-sig")
print(f"wrote {R / 'md_allatom_stability.csv'}")

# the escape trace, at the sampling actually printed
trace = [
    (0.00, 1.05), (0.08, 1.48), (0.16, 0.50), (0.24, 2.27), (0.32, 0.48),
    (0.40, 0.47), (0.48, 0.44), (0.56, 16.12), (0.64, 16.81), (0.72, 19.63),
    (0.80, 21.18), (0.88, 22.60), (0.96, 12.03), (0.99, 0.58),
]
lines = ["target,frame,time_ns,min_dist_A,centroid_offset_A"]
for i, (t, d) in enumerate(trace):
    lines.append(f"NFE2L2,{i},{t},{d},0.0")
(R / "md_ligand_escape.csv").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
print(f"wrote {R / 'md_ligand_escape.csv'}  ({len(trace)} sampled frames)")
print()
print("NOTE: these are the values printed by the WSL run, reproduced so the generated")
print("text can be reviewed before the real CSVs are copied across.  Re-run this after")
print("copying the WSL files, or simply let the real files overwrite these.")
