# -*- coding: utf-8 -*-
"""
Build the Overleaf upload archive with a specification-compliant structure.

PowerShell's Compress-Archive writes entry names with backslashes - "ethambutol\\main.tex"
rather than "ethambutol/main.tex".  The ZIP specification requires forward slashes, and
readers that take the name literally see one file whose name contains a backslash instead
of a folder containing a file, so nothing resolves and the document class is reported as
missing.  Python's zipfile writes the separator correctly.

The archive carries a single top-level folder.  Overleaf's "New Project / Upload Project"
expects either that or a flat set of files; a flat archive dragged onto an existing project
lands wherever the pointer was, which is how a class file ends up in a subfolder and stops
being found.

Every entry is checked after writing, because the whole point of this script is that the
archive was wrong before in a way that is invisible until it is opened.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "submission" / "overleaf"
OUT = ROOT / "submission" / "Ethambutol_Frontiers_Overleaf.zip"
TOP = "ethambutol"

if not SRC.is_dir():
    raise SystemExit(f"source folder missing: {SRC}")

files = sorted(p for p in SRC.iterdir() if p.is_file())
print(f"  source files: {len(files)}")

if OUT.exists():
    OUT.unlink()

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in files:
        # forward slashes, enforced by using a POSIX-style arcname
        z.write(p, arcname=f"{TOP}/{p.name}")

print(f"  written: {OUT.relative_to(ROOT)}  ({OUT.stat().st_size/1024:.0f} KB)")

print()
print("=" * 88)
print("Verification of the archive as a reader will see it")
print("=" * 88)
with zipfile.ZipFile(OUT) as z:
    names = z.namelist()
    bad_sep = [n for n in names if "\\" in n]
    bad_abs = [n for n in names if n.startswith("/") or ".." in n]
    print(f"  entries                       : {len(names)}")
    print(f"  entries containing a backslash: {len(bad_sep)}"
          f"{'   <-- would break resolution' if bad_sep else ''}")
    print(f"  absolute or traversing paths  : {len(bad_abs)}")
    print(f"  integral (testzip)            : "
          f"{'ok' if z.testzip() is None else 'CORRUPT'}")
    print()
    print("  contents:")
    for i in z.infolist():
        print(f"      {i.file_size:>9,}  {i.filename}")

print()
print("=" * 88)
print("What Overleaf needs to find")
print("=" * 88)
with zipfile.ZipFile(OUT) as z:
    names = z.namelist()
    for req, why in ((f"{TOP}/main.tex", "the manuscript"),
                     (f"{TOP}/FrontiersinVancouver.cls", "the document class"),
                     (f"{TOP}/references.bib", "the bibliography"),
                     (f"{TOP}/Frontiers-Vancouver.bst", "the reference style")):
        print(f"  {'present' if req in names else 'MISSING':8s} {req:44s} {why}")
    figs = sorted(n.rsplit("/", 1)[-1] for n in names if n.startswith(f"{TOP}/Figure"))
    #: the exact set the consolidated paper needs: six main plus two supplementary.  A
    #: bare count would not notice the wrong figure being shipped under a right-looking
    #: name, which is how the package came to hold a superseded manuscript last time.
    expected_figs = {
        "Figure1_flow.pdf", "Figure2_disproportionality.pdf", "Figure3_network.pdf",
        "Figure4_enrichment.pdf", "Figure5_docking.pdf", "Figure6_temporal.pdf",
        "FigureS1_heatmap.pdf", "FigureS2_venn.pdf",
    }
    missing_figs = sorted(expected_figs - set(figs))
    extra_figs = sorted(set(figs) - expected_figs)
    print(f"  {'present' if not missing_figs and not extra_figs else 'MISSING':8s} "
          f"{'eight figure files':44s} found {len(figs)}"
          + (f"  missing {missing_figs}" if missing_figs else "")
          + (f"  unexpected {extra_figs}" if extra_figs else ""))
