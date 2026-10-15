# -*- coding: utf-8 -*-
"""
Check what would actually be published if this project were pushed to a repository.

Before advising on how to create a repository, the contents have to be looked at.  A
research repository is public and permanent, and this project has accumulated data
directories measured in gigabytes, absolute paths, and possibly credentials or notes
that were never meant to be read by anyone else.

What is checked here:
    * total size and what dominates it
    * whether a git repository already exists, and what it would stage
    * files that commonly carry secrets (env files, keys, tokens, notebooks)
    * how much of the size is source code as opposed to data
    * whether any file contains an email address, a key-looking string or a local
      absolute path that would be committed
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {"tools", ".piptarget", "__pycache__", ".git", "node_modules"}


def walk():
    for p in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file():
            yield p


print("=" * 94)
print("1. Size by top-level directory")
print("=" * 94)
bydir: dict[str, int] = {}
for p in walk():
    rel = p.relative_to(ROOT)
    top = rel.parts[0] if len(rel.parts) > 1 else "(root files)"
    bydir[top] = bydir.get(top, 0) + p.stat().st_size
total = sum(bydir.values())
for d, n in sorted(bydir.items(), key=lambda x: -x[1]):
    print(f"  {d:26s} {n/1e6:>12,.1f} MB   {100*n/total:>5.1f}%")
print(f"  {'TOTAL':26s} {total/1e9:>12,.2f} GB")

print()
print("=" * 94)
print("2. Source code versus data")
print("=" * 94)
src = [p for p in walk() if p.suffix in (".py", ".sh", ".md", ".json", ".toml",
                                         ".cfg", ".txt", ".yml", ".yaml")]
code = [p for p in src if p.suffix in (".py", ".sh")]
src_size = sum(p.stat().st_size for p in src)
code_size = sum(p.stat().st_size for p in code)
print(f"  python and shell scripts : {len(code):>6,} files, "
      f"{code_size/1e6:>8.2f} MB")
print(f"  all text-like files      : {len(src):>6,} files, "
      f"{src_size/1e6:>8.2f} MB")
print(f"  everything else          : {(total-src_size)/1e6:>15,.2f} MB")
print()
print(f"  A repository of the scripts and documentation alone would be about "
      f"{src_size/1e6:.1f} MB.")
print(f"  The data must NOT be committed: {total/1e9:.2f} GB.")

print()
print("=" * 94)
print("3. Is there already a git repository?")
print("=" * 94)
g = ROOT / ".git"
print(f"  .git directory present: {g.is_dir()}")
if g.is_dir():
    head = (g / "HEAD").read_text(errors="replace").strip() if (g / "HEAD").exists() \
        else "?"
    print(f"  HEAD: {head}")
    cfg = g / "config"
    if cfg.exists():
        for ln in cfg.read_text(errors="replace").splitlines():
            if "url" in ln or "remote" in ln:
                print(f"  {ln.strip()}")
gi = ROOT / ".gitignore"
print(f"  .gitignore present: {gi.is_file()}")
if gi.is_file():
    print("  current .gitignore contents:")
    for ln in gi.read_text(errors="replace").splitlines()[:30]:
        print(f"      {ln}")

print()
print("=" * 94)
print("4. Files that commonly carry secrets")
print("=" * 94)
RISKY = [".env", ".env.local", "credentials", "secret", "token", "id_rsa",
         ".netrc", ".pypirc", "api_key", "apikey"]
hits = [p for p in walk()
        if any(k in p.name.lower() for k in RISKY)]
print(f"  files with a risky name: {len(hits)}")
for p in hits[:20]:
    print(f"      {p.relative_to(ROOT)}")
nb = [p for p in walk() if p.suffix == ".ipynb"]
print(f"  notebooks (may embed outputs and paths): {len(nb)}")
for p in nb[:10]:
    print(f"      {p.relative_to(ROOT)}")

print()
print("=" * 94)
print("5. Content scan of the files that would be published")
print("=" * 94)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
KEYISH = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{12,}")
WINPATH = re.compile(r"[A-Za-z]:\\\\?Users\\\\?[\w\u4e00-\u9fff]+")

email_hits, key_hits, path_hits = [], [], []
for p in src:
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    for m in set(EMAIL.findall(t)):
        if not m.endswith((".png", ".jpg")):
            email_hits.append((str(p.relative_to(ROOT)), m))
    for m in KEYISH.findall(t):
        key_hits.append((str(p.relative_to(ROOT)), str(m)[:40]))
    if WINPATH.search(t):
        path_hits.append(str(p.relative_to(ROOT)))

print(f"  email addresses found : {len(email_hits)}")
for f, e in email_hits[:15]:
    print(f"      {f}: {e}")
print(f"  key-like strings found: {len(key_hits)}")
for f, k in key_hits[:10]:
    print(f"      {f}: {k}")
print(f"  files containing a local Windows user path: {len(path_hits)}")
for f in path_hits[:12]:
    print(f"      {f}")

print()
print("=" * 94)
print("Reading")
print("=" * 94)
print("""  The scripts are small enough to publish comfortably.  The data is not, and must be
  excluded.  Anything flagged above has to be dealt with before the repository is made
  public, because a public repository is permanent and searchable.""")
