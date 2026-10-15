# -*- coding: utf-8 -*-
"""
Set up a portable Python 3.13 with OpenMM for molecular dynamics.

Why this is needed
    The project runs on Python 3.14.8, but OpenMM's newest release (8.6.1) ships
    Windows wheels only up to CPython 3.13.  Rather than downgrade the main
    environment, a self-contained Python 3.13 is unpacked under tools/, OpenMM and
    its dependencies are downloaded as wheels and unpacked into that interpreter,
    and nothing outside the workspace is touched.

Steps
    1. download the python-build-standalone CPython 3.13 Windows archive
    2. unpack it under tools/py313
    3. download openmm / numpy / scipy wheels and unpack into tools/py313/Lib/site-packages
    4. report whether OpenMM imports and whether the CUDA platform sees the GPU

Usage
    python src/setup_md_env.py            # set up
    python src/setup_md_env.py --check    # only report the current state
"""
from __future__ import annotations

import io
import json
import os
import ssl
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PY313 = TOOLS / "py313"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 research/1.0"}

PY_TAG = "3.13"
PKGS = ["openmm", "numpy", "scipy"]


def fetch(url: str, timeout: int = 600) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def pypi_wheel(pkg: str, py_tag: str = "cp313") -> str | None:
    """Return the win_amd64 wheel URL for the newest release of `pkg`."""
    d = json.loads(fetch(f"https://pypi.org/pypi/{pkg}/json", timeout=120))
    ver = d["info"]["version"]
    cands = [f for f in d["releases"][ver]
             if f["filename"].endswith(".whl") and "win_amd64" in f["filename"]]
    # prefer the exact CPython tag, then abi3 / py3-none fallbacks
    for tag in (py_tag, "py3-none", "abi3"):
        for f in cands:
            if tag in f["filename"]:
                return f["url"]
    return cands[0]["url"] if cands else None


def standalone_python_url() -> str | None:
    """Find a CPython 3.13 install_only archive for windows x86_64."""
    api = ("https://api.github.com/repos/astral-sh/python-build-standalone/"
           "releases?per_page=12")
    for attempt in range(4):
        try:
            raw = fetch(api, timeout=180)
            rels = json.loads(raw)
            break
        except Exception as exc:  # noqa: BLE001
            print(f"  github attempt {attempt+1} failed: {type(exc).__name__}")
            rels = None
    if not rels:
        return None
    for rel in rels:
        for a in rel.get("assets", []):
            n = a["name"]
            if (n.startswith("cpython-3.13") and "x86_64-pc-windows-msvc" in n
                    and "install_only" in n and n.endswith(".tar.gz")
                    and "freethreaded" not in n and "debug" not in n):
                return a["browser_download_url"]
    return None


def check() -> bool:
    print("=" * 70)
    print("MD environment status")
    print("=" * 70)
    exe = PY313 / "python" / "python.exe"
    if not exe.exists():
        exe = PY313 / "python.exe"
    print(f"  portable python 3.13 : {exe}  exists={exe.exists()}")
    if not exe.exists():
        return False
    import subprocess
    code = ("import sys;print('python',sys.version.split()[0]);"
            "import openmm;print('openmm',openmm.version.version);"
            "print('platforms',[openmm.Platform.getPlatform(i).getName() "
            "for i in range(openmm.Platform.getNumPlatforms())])")
    out = subprocess.run([str(exe), "-c", code], capture_output=True, text=True,
                         timeout=300)
    print(out.stdout.strip() or out.stderr.strip()[:2000])
    return "openmm" in out.stdout


def main() -> int:
    if "--check" in sys.argv:
        return 0 if check() else 1

    TOOLS.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------- 1. python 3.13
    exe = PY313 / "python" / "python.exe"
    if not exe.exists():
        url = standalone_python_url()
        if not url:
            print("[fail] could not locate a portable CPython 3.13 archive")
            return 1
        print(f"[1] downloading {url.rsplit('/', 1)[-1]} ...")
        blob = fetch(url, timeout=1200)
        print(f"    {len(blob)/1e6:.1f} MB downloaded; unpacking ...")
        PY313.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
            members = tf.getmembers()
            # the archive holds a top-level directory; strip it
            top = members[0].name.split("/")[0]
            for m in members:
                if not m.name.startswith(top):
                    continue
                rel = m.name[len(top):].lstrip("/")
                if not rel:
                    continue
                dest = PY313 / rel
                if m.isdir():
                    dest.mkdir(parents=True, exist_ok=True)
                elif m.isfile():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with tf.extractfile(m) as src, open(dest, "wb") as fh:
                        fh.write(src.read())
        print(f"    unpacked to {PY313}")
    else:
        print(f"[1] portable python already present: {exe}")

    if not exe.exists():
        print("[fail] python.exe not found after unpacking")
        return 1

    # ------------------------------------------------------------- 2. wheels
    site = PY313 / "Lib" / "site-packages"
    site.mkdir(parents=True, exist_ok=True)
    for pkg in PKGS:
        print(f"[2] {pkg}: resolving wheel ...")
        url = pypi_wheel(pkg)
        if not url:
            print(f"    no win_amd64 wheel for {pkg}; skipping")
            continue
        name = url.rsplit("/", 1)[-1]
        print(f"    {name}")
        blob = fetch(url, timeout=1200)
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            zf.extractall(site)
        print(f"    unpacked ({len(blob)/1e6:.1f} MB)")

    # ------------------------------------------------------------- 3. verify
    print("[3] verifying ...")
    ok = check()
    if not ok:
        print("\n[warn] OpenMM did not import cleanly; see the message above")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
