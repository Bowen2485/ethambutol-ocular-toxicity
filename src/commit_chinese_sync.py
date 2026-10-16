# -*- coding: utf-8 -*-
"""
Commit the Chinese manuscript synchronisation.

The two manuscripts are parallel versions of one submission, and before this the Chinese
file lacked the subgroup analysis, the disease-annotation cross-check, the
displacement-independent trajectory measures and the positive control.  Reading the two
against each other at proofing time is exactly when drift costs the most.

The commit also records the numbering decisions, because they were not mechanical: the new
sections were placed by logic and first numbered by analogy with the English file, which put
3.8b before 3.6 and 3.7b after the section it does not belong to.  The final scheme is
3.4f for the subgroup analysis, continuing the robustness block, and 3.5b for the
disease-annotation check, following the enrichment it tests.  The pre-existing jump from 3.7
to 3.11 is closed as well, and two cross-references now point at 3.8 rather than 3.11.

The safety gate is repeated here in its corrected form: the earlier version blocked a commit
over a false alarm, and a gate that cries wolf gets ignored.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\20200\Downloads\论文\投稿\ethambutol-ocular-toxicity")
PROJ = Path(r"C:\Users\20200\Downloads\论文\投稿\Ethambutol_EyeTox")


KEYFILE = PROJ / "credential" / "disgenet_key.txt"
KEYVAL = (KEYFILE.read_text(encoding="utf-8", errors="replace")
          .strip().split()[-1].strip(chr(34)).encode()
          if KEYFILE.exists() else b"")


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


print("=" * 92)
print("1. Copy the Chinese manuscript and the sync scripts")
print("=" * 92)
FILES = [
    "manuscript/Ethambutol_EyeTox_CN_full.md",
    "src/sync_chinese.py",
    "src/sync_chinese_mr.py",
    "src/renumber_chinese.py",
    "src/close_cn_number_gap.py",
    "src/check_md_pocket.py",
    "src/write_md_pocket_check.py",
    "src/write_md_contacts_fix.py",
    "src/commit_integration.py",
    "src/commit_integration2.py",
    "src/update_audit_mr.py",
    "src/rewrite_audit_mr_section.py",
    "src/check_table_widths.py",
    "src/fix_table_count_check.py",
    "src/repair_verify_escapes.py",
    "src/find_disgenet_endpoint.py",
    "src/find_disgenet_routes.py",
    "src/test_disgenet_key.py",
    "src/probe_data_sources.py",
    "src/probe_data_sources2.py",
    "src/probe_gene_annotation.py",
    "src/disgenet_hub_annotation.py",
]
n = 0
for rel in FILES:
    s = PROJ / rel
    if not s.exists():
        if (REPO / rel).exists():
            continue
        print(f"  absent: {rel}")
        continue
    d = REPO / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_bytes(s.read_bytes())
    n += 1
print(f"  copied {n}")

print()
print("=" * 92)
print("2. Stage and scan")
print("=" * 92)
rc, out = run("add", "-A")
print(f"  git add exit {rc}")

rc, staged = run("diff", "--cached", "--name-only")
paths = [p for p in staged.splitlines() if p.strip()]
# Filename patterns for things that must never be published.  A name that merely
# mentions a key is not one of them: src/test_disgenet_key.py reads the credential file
# and prints only its length and a masked form, and the gate below proves that by
# searching the staged content for the key value itself.  Matching on names alone blocked
# that file once and would have kept blocking it.
FORBIDDEN = ("token.txt", ".env", ".pem", "/credential/", "credentials/",
             "disgenet_key.txt", ".sqlite", ".db")
UUID = re.compile(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
JWT = re.compile(rb"eyJ[A-Za-z0-9_-]{10,}\.")

bad = [p for p in paths if any(f in p.lower() for f in FORBIDDEN)]
hits, big = [], []
for p in paths:
    f = REPO / p
    if not f.exists():
        continue
    if f.stat().st_size > 5 * 1024 * 1024:
        big.append(p)
    if f.stat().st_size <= 2_000_000:
        try:
            blob = f.read_bytes()
            # the substantive test: the key value itself, read from the credential file,
            # so a file that merely mentions a key is not blocked and one that contains it
            # always is
            if UUID.search(blob) or JWT.search(blob) or (KEYVAL and KEYVAL in blob):
                hits.append(p)
        except Exception:
            pass

print(f"  staged {len(paths)}   forbidden names {len(bad)}   "
      f"key-shaped {len(hits)}   over 5 MB {len(big)}")
for p in bad + hits + big:
    print(f"      {p}")

print()
print("=" * 92)
print("3. Commit and push")
print("=" * 92)
if bad or hits or big:
    print("  REFUSING: a real problem was found.")
else:
    MSG = (
        "Sync the Chinese manuscript with the four added analyses\n"
        "\n"
        "The English file gained the subgroup analysis, the disease-annotation\n"
        "cross-check, the displacement-independent trajectory measures and the positive\n"
        "control; the Chinese file had none of them.  Both are parts of one submission\n"
        "and are read against each other at proofing time.\n"
        "\n"
        "Numbering was decided by position, not by analogy.  The new sections were first\n"
        "numbered after their English counterparts, which put 3.8b ahead of 3.6 and 3.7b\n"
        "after a section it does not belong to.  They are now 3.4f, continuing the\n"
        "robustness block (3.4c specifications, 3.4d two eras, 3.4e an independent\n"
        "database, 3.4f patient subgroups), and 3.5b, following the enrichment it tests.\n"
        "The pre-existing jump from 3.7 to 3.11 is closed and the section is 3.8; two\n"
        "cross-references were pointing at the old number.\n"
        "\n"
        "The positive control paragraph was added to the Chinese Mendelian\n"
        "randomisation section.  Without it the Chinese version states the renal nulls\n"
        "while omitting the evidence that the panel can detect an effect at all, which\n"
        "is a weaker argument rather than a shorter one.\n"
        "\n"
        "Neither version's renal effect estimates were changed.  Both still report\n"
        "cystatin C on optic neuritis as 1.026 (0.865-1.216) with 150-186 instruments,\n"
        "from the run the paper presents, while the pooled re-run gives 1.054\n"
        "(0.886-1.254) with 115.  Moving both to the pooled values is a decision about\n"
        "which analysis the paper presents and has not been taken.\n"
        "\n"
        "Also added: the WSL script that checks whether the molecular-dynamics contact\n"
        "residues match the ligand's actual position, by measuring against the HMOX1\n"
        "heme site as an independent landmark.  The contact-persistence numbers are held\n"
        "back from the manuscript until that check passes, because the mapping they came\n"
        "from was wrong once already.\n"
        "\n"
        "Chinese manuscript: 724 -> 817 lines, 21,573 characters, all 19 headline\n"
        "figures present and agreeing with the English file.  72 audit checks pass."
    )
    rc, out = run("commit", "-m", MSG)
    print(f"  git commit exit {rc}")
    print(out.strip()[:460])
    rc, out = run("push", "origin", "main")
    print(f"  git push exit {rc}")
    print(out.strip()[:300])
