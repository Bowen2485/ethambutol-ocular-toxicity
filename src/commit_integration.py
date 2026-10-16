# -*- coding: utf-8 -*-
"""
Stage and commit the integration work, having first proved the API key cannot go with it.

The repository is public.  A DisGeNET key now lives in credential/disgenet_key.txt, and the
.gitignore added earlier lists credential/ and *.key.  Trusting that listing is not enough:
the check below asks git itself, with `git check-ignore`, whether the path is ignored, and
then scans everything staged for a key-shaped string or a filename that could carry one.  If
either test fails the script refuses to commit rather than reporting a problem afterwards,
because a key pushed to a public repository has to be rotated, not deleted.

The same refusal covers the other things that must never be published: the OpenGWAS token,
the 37 GB FAERS database, and any file over 5 MB.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\20200\Downloads\论文\投稿\ethambutol-ocular-toxicity")
PROJ = Path(r"C:\Users\20200\Downloads\论文\投稿\Ethambutol_EyeTox")


def run(*args: str, cwd: Path = REPO) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


print("=" * 92)
print("1. Is the credential path ignored by git?")
print("=" * 92)
rc, out = run("check-ignore", "-v", "credential/disgenet_key.txt")
print(f"  git check-ignore exit {rc}")
print(f"  {out.strip() if out.strip() else 'NOT IGNORED - the key would be committable'}")
key_ignored = rc == 0

# also confirm the project copy would be ignored if the repository shared the rule
rc2, out2 = run("check-ignore", "-v", "credential/")
print(f"  credential/ dir: {'ignored' if rc2 == 0 else 'NOT IGNORED'}")

print()
print("=" * 92)
print("2. Copy the new artefacts into the repository")
print("=" * 92)
FILES = [
    "manuscript/Ethambutol_EyeTox_EN_full.md",
    "manuscript/Ethambutol_EyeTox_CN_full.md",
    "submission/main.tex",
    "submission/references.bib",
    "submission/README_Overleaf.md",
    "submission/Ethambutol_Frontiers_Overleaf.zip",
    "results/faers_subgroups.csv",
    "results/faers_subgroup_contrasts.csv",
    "results/disgenet_hub_annotation.csv",
    "results/disgenet_hub_annotation.json",
    "results/disgenet_false_positive_check.json",
    "results/hub_disease_annotation.csv",
    "results/geo_series_candidates.json",
    "results/md_rmsf.csv",
    "results/md_hbonds.csv",
    "results/md_contact_residues.csv",
    "results/data_source_probe.json",
    "results/gene_annotation_probe.json",
    "src/analyse_md_extra.py",
    "src/analyse_md_contacts.py",
    "src/faers_subgroups.py",
    "src/disgenet_hub_annotation2.py",
    "src/check_disgenet_false_positives.py",
    "src/hub_disease_and_geo.py",
    "src/compare_techniques.py",
    "src/compare_abstract_vocabulary.py",
    "src/rewrite_abstract.py",
    "src/final_audit.py",
    "src/verify_latex.py",
    "src/build_latex.py",
]
copied, missing = 0, []
for rel in FILES:
    s = PROJ / rel
    if not s.exists():
        # the file may exist only in the repository already, or may be new
        if (REPO / rel).exists():
            continue
        missing.append(rel)
        continue
    d = REPO / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_bytes(s.read_bytes())
    copied += 1
print(f"  copied {copied}")
if missing:
    print(f"  not found (listed, not copied): {len(missing)}")
    for m in missing[:8]:
        print(f"      {m}")

# the overleaf folder, whole
ov = PROJ / "submission" / "overleaf"
if ov.is_dir():
    for p in sorted(ov.iterdir()):
        if p.is_file():
            d = REPO / "submission" / "overleaf" / p.name
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(p.read_bytes())
            copied += 1
    print(f"  overleaf folder copied; running total {copied}")

print()
print("=" * 92)
print("3. Stage")
print("=" * 92)
rc, out = run("add", "-A")
print(f"  git add -A exit {rc} {out.strip()[:160]}")
rc, staged = run("diff", "--cached", "--name-only")
paths = [p for p in staged.splitlines() if p.strip()]
print(f"  staged files: {len(paths)}")

print()
print("=" * 92)
print("4. Safety scan of everything staged")
print("=" * 92)
FORBIDDEN = ("token", ".env", ".key", ".pem", "credential", "disgenet_key",
             "secret", ".sqlite", ".db")
bad = [p for p in paths if any(f in p.lower() for f in FORBIDDEN)]
data = [p for p in paths if p.startswith("data/")]
sizes = sorted(((REPO / p).stat().st_size, p) for p in paths if (REPO / p).exists())
big = [(s, p) for s, p in sizes if s > 5 * 1024 * 1024]

# a key-shaped string in the staged content: a UUID, or the OpenGWAS JWT prefix
UUID = re.compile(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
JWT = re.compile(rb"eyJ[A-Za-z0-9_-]{10,}\.")
hits = []
for p in paths:
    f = REPO / p
    if not f.exists() or f.stat().st_size > 2_000_000:
        continue
    try:
        blob = f.read_bytes()
    except Exception:
        continue
    if UUID.search(blob) or JWT.search(blob):
        hits.append(p)

print(f"  filenames matching a forbidden pattern : {len(bad)}")
for p in bad[:6]:
    print(f"      {p}")
print(f"  paths under data/                      : {len(data)}")
print(f"  files over 5 MB                        : {len(big)}")
for s, p in big[:4]:
    print(f"      {s/1e6:.1f} MB  {p}")
print(f"  staged files containing a key-shaped string: {len(hits)}")
for p in hits[:6]:
    print(f"      {p}")

print()
print("=" * 92)
print("5. Commit")
print("=" * 92)
blocked = (not key_ignored) or bad or data or big or hits
if blocked:
    print("  REFUSING TO COMMIT.  Unstage the items listed above.  A key pushed to a")
    print("  public repository must be rotated, not merely removed.")
else:
    MSG = (
        "Add subgroup, disease-annotation and trajectory analyses\n"
        "\n"
        "Four analyses the peer literature in this genre carries and the manuscript\n"
        "lacked, with the negative results reported as they stand.\n"
        "\n"
        "Subgroup analysis (Section 3.7b).  The optic-nerve signal is present in every\n"
        "stratum of sex, age, reporting region and era.  Five contrasts exclude unity;\n"
        "three are not effects - unknown sex and unknown age mark a sparsely completed\n"
        "report, and region is uninterpretable for the reason Section 3.2c already gives.\n"
        "The age gradient is the one worth reading (65+ against 0-17, ratio 5.40,\n"
        "2.58-11.32), and it agrees with the continuous age effect already reported\n"
        "without being independent of it.\n"
        "\n"
        "Disease-annotation cross-check (Section 3.8b).  Against Open Targets and HPO,\n"
        "30% of hubs and 24% of controls carry an eye annotation (P = 0.39); against\n"
        "DisGeNET, 61% and 12% do.  The narrow sources, not the network, appear to have\n"
        "caused the null.  Auditing the keyword match for false positives - keratosis and\n"
        "dyskeratosis congenita are skin diseases - leaves 55% against 12%, odds ratio\n"
        "7.82, P = 2.6e-4.  The positive control holds: OPA1, DNM1L and MFN2 are annotated\n"
        "for optic atrophy.  GPX4, SLC7A11 and ACSL4 have no eye annotation at all, which\n"
        "bounds the mechanism to its mitochondrial and inflammatory arm.\n"
        "\n"
        "Trajectory measures independent of displacement (Section 3.9b).  Mean C-alpha\n"
        "RMSF is 0.65-0.68 A across three proteins of very different size, so the site is\n"
        "not disintegrating.  Ligand-protein polar contacts are maintained or increase\n"
        "(63 to 80, 175 to 189) while only 11-21% of the initial atom pairs survive, which\n"
        "is the signature of a ligand that stays and re-forms its interactions.\n"
        "\n"
        "Positive control reported.  Body mass index, carried as a positive control, is\n"
        "the only pair of 60 surviving FDR (OR 1.680, 1.265-2.231, q = 0.020).  This is\n"
        "what makes the renal nulls readable: the panel does recover an effect where one\n"
        "exists.\n"
        "\n"
        "Two audits repaired rather than deleted.  The MR section of final_audit.py was\n"
        "querying exposure names that no longer exist, so every check inside it was\n"
        "silently skipped; and verify_latex.py held counts from before the new sections.\n"
        "A check that has stopped checking is worse than one that fails.  72 checks pass."
    )
    rc, out = run("commit", "-m", MSG)
    print(f"  git commit exit {rc}")
    print(out.strip()[:700])

print()
print("=" * 92)
print("6. Push")
print("=" * 92)
rc, out = run("push", "origin", "main")
print(f"  git push exit {rc}")
print(out.strip()[:400])
