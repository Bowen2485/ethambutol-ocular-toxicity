# -*- coding: utf-8 -*-
"""
Confirm the exact name of the GAFF force field accepted by SystemGenerator.

Validating this statically matters: three runs have already been lost to assumed API
details, and an invalid force-field name would fail at generator construction with a
confusing message.  The names are defined in template_generators.py.
"""
from __future__ import annotations

import re
import ssl
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
BASE = ("https://raw.githubusercontent.com/openmm/openmmforcefields/0.16.0/"
        "openmmforcefields/generators/")


def get(name: str) -> str:
    req = urllib.request.Request(BASE + name, headers={"User-Agent": "x"})
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        return r.read().decode("utf-8", "replace")


src = get("template_generators.py")
print(f"fetched template_generators.py: {len(src)} characters\n")

print("=" * 76)
print("INSTALLED_FORCEFIELDS entries")
print("=" * 76)
for m in re.finditer(r"INSTALLED_FORCEFIELDS\s*=\s*\[([^\]]*)\]", src, re.S):
    names = re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))
    print("  " + ", ".join(names))

print()
print("=" * 76)
print("classes defining INSTALLED_FORCEFIELDS")
print("=" * 76)
for m in re.finditer(r"class (\w+)\(([^)]*)\)", src):
    print(f"  {m.group(1)}  ({' '.join(m.group(2).split())[:70]})")

print()
print("=" * 76)
print("every quoted string that looks like a force-field name")
print("=" * 76)
cands = sorted(set(re.findall(r"['\"]((?:gaff|smirnoff|espaloma|openff)[^'\"]*)['\"]",
                              src, re.I)))
for c in cands:
    print("  " + c)

print()
print("=" * 76)
print("VERDICT")
print("=" * 76)
has_gaff211 = any(c == "gaff-2.11" for c in cands)
print(f"  'gaff-2.11' defined in template_generators.py: {has_gaff211}")
print(f"  'espaloma' available as an alternative      : "
      f"{any('espaloma' in c.lower() for c in cands)}")
print(f"  'openff-2*' (SMIRNOFF) available            : "
      f"{any(c.lower().startswith('openff-2') for c in cands)}")
