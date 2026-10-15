# -*- coding: utf-8 -*-
"""
Stage the new work and commit it, after checking that nothing private goes in.

The repository is public, so the safety check is not a formality.  Two things must never
be committed and neither is caught by a careless "git add -A":

    data/raw/opengwas/token.txt holds a live OpenGWAS API token; publishing it hands over
        the account and git retains it in history after deletion
    data/derived/faers.sqlite is 37.5 GB and is excluded on size as well as by policy

.gitignore already covers both, but the check is repeated here against the staged paths, so
a mistake in the ignore file cannot silently publish a credential.

Which new scripts are kept, and which are not
    Kept: the ones that produce or verify something in the manuscript - the bibliography
    builder, the LaTeX converter and its verifier, the archive builder, the HPA retinal
    analysis, the label cross-check, the ferroptosis class test, and the strict-count
    diagnostics.
    Left out: the throwaway probes written while locating the PDF parser's behaviour.
    They answered a question that is now settled and would only add noise.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\20200\Downloads\论文\投稿\ethambutol-ocular-toxicity")
PROJ = Path(r"C:\Users\20200\Downloads\论文\投稿\Ethambutol_EyeTox")

ADD = [
    "manuscript/Ethambutol_EyeTox_EN_full.md",
    "manuscript/Ethambutol_EyeTox_CN_full.md",
    # LaTeX submission package.  In the project the manuscript is named after the paper;
    # in the repository it is main.tex, which is what the field expects and what the
    # archive contains.  The earlier version of this script looked for main.tex in the
    # project folder, where it does not exist.
    ("submission/Ethambutol_EyeTox_Frontiers.tex", "submission/main.tex"),
    "submission/references.bib",
    "submission/README_Overleaf.md",
    "submission/Ethambutol_Frontiers_Overleaf.zip",
    "results/md_allatom_stability_pbc.csv",
    "src/build_bib.py",
    "src/build_latex.py",
    "src/verify_latex.py",
    "src/build_overleaf_zip.py",
    "src/analyse_hpa_retina.py",
    "src/crosscheck_labels.py",
    "src/examine_ferroptosis_test.py",
    "src/analyse_md_pbc.py",
    "src/write_pbc_table_windows.py",
    "src/reconcile_numbers.py",
    "src/verify_strict_count.py",
    "src/read_signal_thresholds.py",
    "src/fix_strict_count.py",
    "src/verify_four_part_definition.py",
    "src/check_refetch_live.py",
    "src/check_unicode.py",
    "src/check_specials.py",
    "src/commit_repo.py",
    "docs/投稿方案_Frontiers_in_Pharmacology.md",
    "docs/目标期刊推荐_20261015.md",
    "docs/投稿信与投稿材料_20261015.md",
]

# the overleaf folder, whole, including the official class and the nine figures
OVERLEAF = PROJ / "submission" / "overleaf"
for p in sorted(OVERLEAF.iterdir()):
    if p.is_file():
        ADD.append((f"submission/overleaf/{p.name}", f"submission/overleaf/{p.name}"))


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


print("=" * 90)
print("1. Copy the new files into the repository")
print("=" * 90)
targets: list[str] = []
copied = missing = 0
for item in ADD:
    src_rel, dst_rel = item if isinstance(item, tuple) else (item, item)
    src, dst = PROJ / src_rel, REPO / dst_rel
    if not src.exists():
        print(f"  MISSING SOURCE  {src_rel}")
        missing += 1
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    targets.append(dst_rel)
    copied += 1
print(f"  copied {copied}, missing {missing}")

print()
print("=" * 90)
print("2. Stage")
print("=" * 90)
rc, out = run("add", "--", *targets)
print(f"  git add exit {rc}")
if out.strip():
    print(f"  {out.strip()[:400]}")

rc, staged = run("diff", "--cached", "--name-only")
paths = [p for p in staged.splitlines() if p.strip()]
print(f"  staged files: {len(paths)}")

print()
print("=" * 90)
print("3. Safety check on the staged paths")
print("=" * 90)
FORBIDDEN = ("token", ".env", ".key", ".pem", "credential", "secret", ".sqlite", ".db")
bad = [p for p in paths if any(f in p.lower() for f in FORBIDDEN)]
data = [p for p in paths if p.startswith("data/")]
print(f"  matching a forbidden pattern : {len(bad)}")
for p in bad:
    print(f"      {p}")
print(f"  under data/                  : {len(data)}")
for p in data:
    print(f"      {p}")

sizes = sorted(((REPO / p).stat().st_size, p) for p in paths if (REPO / p).exists())
print("  largest staged files:")
for s, p in sizes[-5:]:
    print(f"      {s/1024:>9,.1f} KB  {p}")
big = [(s, p) for s, p in sizes if s > 5 * 1024 * 1024]
print(f"  over 5 MB: {len(big)}")

print()
print("=" * 90)
print("4. Commit")
print("=" * 90)
if bad or data or big:
    print("  REFUSING to commit: the safety check found something that should not be")
    print("  published.  Resolve it before running this script again.")
else:
    MSG = (
        "Add LaTeX submission package, corrected MD, and panel corrections\n"
        "\n"
        "LaTeX package for Frontiers in Pharmacology, built from the official\n"
        "Frontiers class (FrontiersinVancouver, numbered references):\n"
        "  submission/main.tex     structured abstract, 28 references, 9 figures\n"
        "  submission/references.bib   28 entries, keys mapped from [n] citations\n"
        "  submission/Ethambutol_Frontiers_Overleaf.zip   upload-ready archive\n"
        "Compilation confirmed on Overleaf.\n"
        "\n"
        "Molecular dynamics, corrected.  The earlier analysis differenced raw\n"
        "coordinates after superposition, so periodic-boundary wrapping produced\n"
        "apparent displacements of up to 97 A and inverted the conclusion.  With the\n"
        "trajectory imaged first, the docked pose is retained in all three targets\n"
        "(minimum ligand-protein distance 1.76-2.18 A, contacts maintained or\n"
        "increased, receptor backbone RMSD 1.18-1.34 A).\n"
        "\n"
        "Ocular panel corrections.  The strict-signal count is 45, not 58, which\n"
        "belonged to the 177-term source panel; and the criteria now state all four\n"
        "conditions applied, including IC025 > 0 and a Benjamini-Hochberg q < 0.05\n"
        "that the text had omitted.\n"
        "\n"
        "Three analyses added: retinal expression of the network hubs (31 of 33 in\n"
        "retinal clusters, P = 0.0067), a class-level test of ferroptosis that could\n"
        "not adjudicate the mechanism and is reported as a limitation, and a\n"
        "cross-check of the signals against regulatory labelling."
    )
    rc, out = run("commit", "-m", MSG)
    print(f"  git commit exit {rc}")
    print(out.strip()[:900])

print()
print("=" * 90)
print("5. Push")
print("=" * 90)
rc, out = run("push", "origin", "main")
print(f"  git push exit {rc}")
print(out.strip()[:600])
if rc != 0:
    print()
    print("  The commit is local.  The push can be completed from Git Bash or GitHub")
    print("  Desktop, both of which have working credentials.")
