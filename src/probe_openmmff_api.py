# -*- coding: utf-8 -*-
"""
Read the openmmforcefields source to get the SystemGenerator API right.

Three attempts at the MD script have now failed on assumed API details, so the
signature of add_molecules and the way create_system picks up small-molecule
parameters are read from the released source rather than guessed.
"""
from __future__ import annotations

import re
import ssl
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
URL = ("https://raw.githubusercontent.com/openmm/openmmforcefields/0.16.0/"
       "openmmforcefields/generators/system_generators.py")


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "x"})
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        return r.read().decode("utf-8", "replace")


src = get(URL)
print(f"fetched {len(src)} characters\n")

print("=" * 76)
print("SystemGenerator methods")
print("=" * 76)
for m in re.finditer(r"\n    def (\w+)\(([^)]*)\)", src):
    sig = " ".join(m.group(2).split())
    print(f"  {m.group(1)}({sig[:150]})")

print()
print("=" * 76)
print("add_molecules implementation")
print("=" * 76)
i = src.find("def add_molecules")
print(src[i:i + 1500] if i > 0 else "  not found")

print()
print("=" * 76)
print("__init__ implementation body (docstring skipped)")
print("=" * 76)
i = src.find("def __init__")
if i > 0:
    head = src[i:i + 8000]
    # skip the docstring: find the closing triple quote after the opening one
    first = head.find('"""')
    second = head.find('"""', first + 3)
    impl = head[second + 3:] if second > 0 else head
    for line in impl.splitlines()[:70]:
        print("  " + line.rstrip()[:120])
else:
    print("  __init__ not found")

print()
print("=" * 76)
print("how create_system obtains small-molecule parameters")
print("=" * 76)
i = src.find("def create_system")
block = src[i:i + 3000] if i > 0 else ""
for line in block.splitlines():
    if any(k in line for k in ("_sm_template_generator", "add_molecules",
                               "molecules", "cache", "template")):
        print("  " + line.strip()[:120])
