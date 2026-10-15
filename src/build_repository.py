# -*- coding: utf-8 -*-
"""
Build a clean, publishable repository directory from the project.

Why a copy rather than a repository in place
    The project holds 42 GB of data, including a 37 GB SQLite database and a live
    OpenGWAS credential.  A git repository created in place would be a hazard: one
    careless `git add .` would commit the database, and the credential in
    data/raw/opengwas/token.txt would be published permanently, remaining in the
    history even after deletion.  Building a separate directory means the published
    set is defined by what is copied into it, not by what someone remembers to exclude.

What goes in
    source scripts, documentation, result tables and figures, the manuscript, and the
    files a reader needs to understand and rerun the work.

What stays out
    all data, the credential, the tools directory, and anything holding a local
    absolute path or a third party's email address.

Sanitisation
    Documents that mention the local user directory have those paths rewritten to a
    placeholder, because a published repository should not record where the work was
    done on someone's machine.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent / "Ethambutol_EyeTox_repo"

if REPO.exists():
    shutil.rmtree(REPO)
REPO.mkdir(parents=True)

print("=" * 90)
print("1. Copying the publishable material")
print("=" * 90)
PLAN = [
    ("src", "src", "*.py"),
    ("src", "src", "*.sh"),
    ("docs", "docs", "*.md"),
    ("tables", "tables", "*.csv"),
    ("figures", "figures", "*"),
    ("manuscript", "manuscript", "*"),
    ("results", "results", "*.csv"),
    ("results", "results", "*.json"),
    ("results", "results", "*.md"),
]
copied = 0
for src_dir, dst_dir, pattern in PLAN:
    d = ROOT / src_dir
    if not d.is_dir():
        continue
    (REPO / dst_dir).mkdir(parents=True, exist_ok=True)
    for p in d.glob(pattern):
        if not p.is_file():
            continue
        # never carry a credential, whatever it is named
        if "token" in p.name.lower() and p.suffix == ".txt":
            print(f"  skipped (credential-looking): {p.name}")
            continue
        shutil.copy2(p, REPO / dst_dir / p.name)
        copied += 1
print(f"  files copied: {copied}")

# the shell helpers in the project root
for p in list(ROOT.glob("*.sh")):
    shutil.copy2(p, REPO / p.name)
    copied += 1

print()
print("=" * 90)
print("2. Sanitising local paths and personal addresses in documents")
print("=" * 90)
WINPATH = re.compile(r"[A-Za-z]:\\+Users\\+[\w\u4e00-\u9fff]+")
EMAIL_SELF = "20200121047@bucm.edu.cn"
changed = 0
for p in list(REPO.rglob("*.md")) + list(REPO.rglob("*.py")) + \
        list(REPO.rglob("*.sh")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    orig = t
    t = WINPATH.sub("<user directory>", t)
    if EMAIL_SELF in t and p.suffix == ".md" and "投稿前待办" not in p.name:
        t = t.replace(EMAIL_SELF, "<corresponding author email>")
    if t != orig:
        p.write_text(t, encoding="utf-8")
        changed += 1
        print(f"  sanitised: {p.relative_to(REPO)}")
print(f"  documents changed: {changed}")

print()
print("=" * 90)
print("3. Writing .gitignore")
print("=" * 90)
GITIGNORE = """\
# ---------------------------------------------------------------------------
# Data - must never be committed
# ---------------------------------------------------------------------------
# The analysis reads 42 GB of source data: FAERS quarterly ASCII releases, a 37 GB
# SQLite database, JADER CSVs, FinnGen summary-statistic scans and OpenGWAS files.
# None of it belongs in a repository.  It is all publicly downloadable and the
# scripts describe how to obtain it.
data/
*.sqlite
*.sqlite3
*.db
*.gz
*.tbi
*.bgz
*.dcd
*.nc
*.xtc
*.prmtop
*.frcmod
*.mol2

# ---------------------------------------------------------------------------
# Credentials - must never be committed
# ---------------------------------------------------------------------------
# data/raw/opengwas/token.txt holds a live OpenGWAS API token.  Publishing it would
# hand over the account, and git keeps it in the history even after deletion.
token.txt
*token*.txt
.env
.env.*
*.key
*.pem
credentials*
secrets*

# ---------------------------------------------------------------------------
# Environment and build products
# ---------------------------------------------------------------------------
tools/
.wheels/
.piptarget/
__pycache__/
*.pyc
*.pyo
.venv/
venv/
env/
.tmp/
archive/
receptors_clean/

# ---------------------------------------------------------------------------
# Large intermediate output
# ---------------------------------------------------------------------------
docking/poses/
docking/validation/*/docked*.pdbqt

# ---------------------------------------------------------------------------
# Editor and OS
# ---------------------------------------------------------------------------
.vscode/
.idea/
Thumbs.db
Desktop.ini
"""
(REPO / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
print(f"  written, {len(GITIGNORE.splitlines())} lines")

# a second guard: .gitattributes marks generated files so diffs stay readable
(REPO / ".gitattributes").write_text(
    "* text=auto eol=lf\n"
    "*.csv text\n"
    "*.md text\n"
    "*.py text\n"
    "*.png binary\n"
    "*.pdf binary\n", encoding="utf-8")
print("  .gitattributes written")

print()
print("=" * 90)
print("4. Result")
print("=" * 90)
total = sum(p.stat().st_size for p in REPO.rglob("*") if p.is_file())
n = sum(1 for p in REPO.rglob("*") if p.is_file())
print(f"  repository directory : {REPO}")
print(f"  files                : {n:,}")
print(f"  size                 : {total/1e6:.1f} MB")
print()
for d in sorted(p for p in REPO.iterdir() if p.is_dir()):
    sub = sum(q.stat().st_size for q in d.rglob("*") if q.is_file())
    cnt = sum(1 for q in d.rglob("*") if q.is_file())
    print(f"      {d.name:16s} {cnt:>5} files  {sub/1e6:>7.2f} MB")
for f in sorted(p for p in REPO.iterdir() if p.is_file()):
    print(f"      {f.name:16s} {1:>5} file   {f.stat().st_size/1e6:>7.2f} MB")
print()
print("  Next: add README.md and LICENSE, then push.  See the setup guide.")
