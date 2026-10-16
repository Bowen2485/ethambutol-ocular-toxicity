# -*- coding: utf-8 -*-
"""
Check that the published repository mirrors the working tree.

Written because results/mr_opengwas_results.csv was found to be three days stale in the
repository while the working tree had moved on, and a stale copy of a result file is invisible:
it is the same file name, the same columns, and plausible numbers.  The publishable set is
defined by src/build_repository.py, so the same rules are used here.

Reports, for every publishable file: missing from the repository, different, or identical.
Exit code is 1 when anything differs, so this can be a gate.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

WORK = Path(r"C:\Users\20200\Downloads\论文\投稿\Ethambutol_EyeTox")
REPO = Path(r"C:\Users\20200\Downloads\论文\投稿\ethambutol-ocular-toxicity")

PLAN = [("src", "*.py"), ("src", "*.sh"), ("docs", "*.md"), ("tables", "*.csv"),
        ("figures", "*"), ("manuscript", "*"),
        ("results", "*.csv"), ("results", "*.json"), ("results", "*.md")]


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


#: src/build_repository.py rewrites the local user directory to a placeholder and the
#: corresponding author's address to another in .md, .py and .sh files, and .gitattributes
#: normalises line endings to LF on commit.  A byte comparison would therefore report every
#: document that mentions a path as drifted, which is noise, so the same two transforms are
#: applied here before comparing text files.
WINPATH = re.compile(r"[A-Za-z]:\\+Users\\+[\w\u4e00-\u9fff]+")
EMAIL_SELF = "<corresponding author email>"
TEXTUAL = {".md", ".py", ".sh"}


def normalised(p: Path) -> bytes:
    raw = p.read_bytes()
    if p.suffix not in TEXTUAL:
        return raw
    try:
        t = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    t = WINPATH.sub("<user directory>", t)
    if p.suffix == ".md" and "投稿前待办" not in p.name:
        t = t.replace(EMAIL_SELF, "<corresponding author email>")
    return t.replace("\r\n", "\n").encode("utf-8")


def same_text(a: Path, b: Path) -> bool:
    return normalised(a) == normalised(b)


pairs = []
for sub, pattern in PLAN:
    for p in sorted((WORK / sub).glob(pattern)):
        if p.is_file():
            pairs.append((f"{sub}/{p.name}", p, REPO / sub / p.name))
for p in sorted(WORK.glob("*.sh")):
    pairs.append((p.name, p, REPO / p.name))

same, diff, missing = [], [], []
for label, src, dst in pairs:
    if not dst.exists():
        missing.append((label, src.stat().st_size))
    elif same_text(src, dst):
        same.append(label)
    else:
        diff.append((label, src.stat().st_size, dst.stat().st_size))

#: files in the repository that no longer have a source in the working tree
orphans = []
declared_sources = {label for label, _, _ in pairs}
for p in REPO.rglob("*"):
    if not p.is_file() or ".git" in p.parts:
        continue
    rel = p.relative_to(REPO).as_posix()
    if rel in {"README.md", "LICENSE", ".gitignore", ".gitattributes"}:
        continue
    if rel not in declared_sources:
        orphans.append(rel)

print("=" * 94)
print(f"publishable files checked: {len(pairs)}")
print(f"  identical : {len(same)}")
print(f"  different : {len(diff)}")
print(f"  missing   : {len(missing)}")
print("=" * 94)

if diff:
    print("\nDIFFERENT (working tree -> repository):")
    print(f"  {'file':<52} {'work':>12} {'repo':>12}")
    for label, a, b in diff:
        print(f"  {label:<52} {a:>12,} {b:>12,}")

if missing:
    print("\nMISSING FROM REPOSITORY:")
    for label, a in missing:
        print(f"  {label:<52} {a:>12,}")

if orphans:
    print("\nIN THE REPOSITORY BUT NOT PUBLISHED FROM THE WORKING TREE:")
    for rel in sorted(orphans):
        print(f"  {rel}")

print()
print("VERDICT:", "in sync" if not (diff or missing) else "OUT OF SYNC")
if orphans:
    print(f"         ({len(orphans)} repository-only file(s) reported above; those may be")
    print("          deliberate, but each one should be a decision rather than a leftover)")
sys.exit(1 if (diff or missing) else 0)
