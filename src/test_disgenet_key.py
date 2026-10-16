# -*- coding: utf-8 -*-
"""
Test the DisGeNET API with the supplied key, and prepare the credential for safe use.

The key is read from credential/disgenet_key.txt and never printed.  Only its length and a
masked form appear in the output, because a log is as public as a repository once it is
shared and the point of storing the key in a file is to keep it out of everything else.

What is established here
    whether the key is accepted at all,
    which endpoints answer and in what shape,
    and therefore whether the hub-gene disease annotation can be redone against DisGeNET
    instead of the two narrow curated sources that produced a null result.

A 401 or 403 means the key is wrong or the account is not activated; that is reported
plainly rather than retried with variations, since guessing at an authentication failure is
how accounts get locked.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = ROOT / "credential" / "disgenet_key.txt"

if not KEY_FILE.exists():
    raise SystemExit(f"key file not found: {KEY_FILE}")

raw = KEY_FILE.read_text(encoding="utf-8", errors="replace").strip()
# tolerate a key pasted with a label such as "key: xxxx" or surrounding quotes
key = raw.split()[-1].strip().strip('"').strip("'")
print(f"  key file      : {KEY_FILE.relative_to(ROOT)}")
print(f"  key length    : {len(key)} characters")
print(f"  masked        : {key[:4]}...{key[-4:]}" if len(key) > 8 else "  (too short)")

UA = {"User-Agent": "Mozilla/5.0 (compatible; manuscript-data-check/1.0)",
      "Accept": "application/json",
      "Authorization": f"Bearer {key}"}


def get(url: str, timeout: int = 45):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=timeout) as fh:
            body = fh.read(400_000).decode("utf-8", "replace")
            return fh.status, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read(2000).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {str(e)[:120]}"


print()
print("=" * 96)
print("Endpoint tests")
print("=" * 96)
TESTS = [
    ("gene disease associations (summary)", "https://www.disgenet.org/api/gda/summary/TP53"),
    ("gene disease associations (full)", "https://www.disgenet.org/api/gda/gene/TP53"),
    ("disease by UMLS", "https://www.disgenet.org/api/disease/C0029463"),
    ("gene info", "https://www.disgenet.org/api/gene/7157"),
    ("vocabulary: disease types", "https://www.disgenet.org/api/vda/summary/TP53"),
]
working = []
for label, url in TESTS:
    status, body = get(url)
    is_json = False
    n_items = 0
    if body and body.lstrip().startswith(("[", "{")):
        try:
            parsed = json.loads(body)
            is_json = True
            n_items = len(parsed) if isinstance(parsed, list) else 1
        except Exception:
            pass
    verdict = "DATA" if is_json else "no data"
    print(f"  {verdict:8s} {label:38s} status {status}  {len(body):>8,} B")
    print(f"           {body[:170]}")
    if is_json and n_items:
        working.append((label, url, n_items))
    print()

print("=" * 96)
print("Result")
print("=" * 96)
if working:
    print(f"  endpoints returning data: {len(working)}")
    for label, url, n in working:
        print(f"      {label:38s} {n} record(s)")
    print()
    print("  The key works.  The hub-gene disease annotation can be redone against")
    print("  DisGeNET, which is a far wider source than the two curated ones that gave a")
    print("  null result, and is one of the sources the peer papers actually use.")
else:
    print("  No endpoint returned data.  A 401 or 403 means the key was rejected.")
    print("  The exact status is printed above; the fix is at the DisGeNET end, not here.")

# ---- make sure the credential cannot be committed
gi = ROOT / ".gitignore"
if gi.exists():
    t = gi.read_text(encoding="utf-8")
    needed = [p for p in ("credential/", "credentials/") if p not in t]
    if needed:
        with open(gi, "a", encoding="utf-8") as fh:
            fh.write("\n# Credentials directory holding API keys\n")
            for p in needed:
                fh.write(f"{p}\n")
        print()
        print(f"  .gitignore updated with: {', '.join(needed)}")
    else:
        print()
        print("  .gitignore already excludes the credential directory")
else:
    print()
    print("  WARNING: no .gitignore found; the key could be committed")
