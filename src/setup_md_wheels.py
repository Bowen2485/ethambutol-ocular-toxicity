# -*- coding: utf-8 -*-
"""
Install OpenMM and its dependencies into the portable Python 3.13.

The Python 3.13 runtime already exists at tools/py313 (installed by setup_md_env.py).
This script only handles the wheels, with explicit messages for every decision so a
silent skip is impossible.

Usage
    python src/setup_md_wheels.py
    python src/setup_md_wheels.py --check
"""
from __future__ import annotations

import io
import json
import ssl
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / "tools" / "py313" / "python.exe"
SITE = ROOT / "tools" / "py313" / "Lib" / "site-packages"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 research/1.0"}

PKGS = ["numpy", "scipy", "openmm"]


def fetch(url: str, timeout: int = 900) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def resolve(pkg: str) -> tuple[str, str] | None:
    """Return (filename, url) for the best win_amd64 CPython 3.13 wheel."""
    d = json.loads(fetch(f"https://pypi.org/pypi/{pkg}/json", timeout=180))
    ver = d["info"]["version"]
    files = [f for f in d["releases"][ver]
             if f["filename"].endswith(".whl")
             and "win_amd64" in f["filename"]]
    print(f"    {pkg} {ver}: {len(files)} win_amd64 wheel(s)")
    if not files:
        return None
    # exact CPython 3.13 tag first, then any cp313, then pure-python fallbacks
    def score(fn: str) -> int:
        n = fn.lower()
        if "cp313" in n and "win_amd64" in n:
            return 0
        if "cp313" in n:
            return 1
        if "abi3" in n:
            return 2
        if "py3-none-any" in n:
            return 3
        return 9
    files.sort(key=lambda f: score(f["filename"]))
    best = files[0]
    print(f"      chosen: {best['filename']}")
    return best["filename"], best["url"]


def check() -> int:
    if not PY.exists():
        print(f"  portable python missing: {PY}")
        return 1
    code = ("import sys;print('python',sys.version.split()[0]);"
            "import numpy;print('numpy',numpy.__version__);"
            "import openmm;print('openmm',openmm.version.version);"
            "print('platforms',[openmm.Platform.getPlatform(i).getName() "
            "for i in range(openmm.Platform.getNumPlatforms())])")
    r = subprocess.run([str(PY), "-c", code], capture_output=True, text=True,
                       timeout=600)
    print(r.stdout.strip() or r.stderr.strip()[-3000:])
    return 0 if "openmm" in r.stdout else 1


def main() -> int:
    if "--check" in sys.argv:
        return check()
    if not PY.exists():
        print(f"[fail] {PY} not found; run src/setup_md_env.py first")
        return 1
    SITE.mkdir(parents=True, exist_ok=True)

    for pkg in PKGS:
        print(f"[pkg] {pkg}")
        got = resolve(pkg)
        if got is None:
            print(f"      [skip] no suitable wheel found for {pkg}")
            continue
        name, url = got
        print(f"      downloading ...")
        blob = fetch(url)
        print(f"      {len(blob)/1e6:.1f} MB; unpacking into site-packages")
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            zf.extractall(SITE)
        print(f"      done")

    print("\n[verify]")
    rc = check()
    if rc != 0:
        print("\n[warn] OpenMM did not import; see the message above")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
