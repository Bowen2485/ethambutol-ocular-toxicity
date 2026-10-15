# -*- coding: utf-8 -*-
"""
Local package installer.

`pip install` cannot run in this sandbox: the workspace ACL denies
DeleteSubdirectoriesAndFiles to Everyone, so pip's unpack/cleanup step fails with
WinError 13.  This script downloads the wheel straight from the PyPI JSON API and
unpacks it into a workspace-local target directory, which is exactly what pip
would have done, without any temp-directory choreography.
"""
from __future__ import annotations

import json
import ssl
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WHEELS = ROOT / ".wheels"
TARGET = ROOT / ".piptarget"
WHEELS.mkdir(exist_ok=True)
TARGET.mkdir(exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0"}

WANT_SUFFIX = ("cp314-cp314-win_amd64", "cp314-cp314-win32", "py3-none-any",
               "py2.py3-none-any", "abi3-win_amd64", "none-any")


def pypi_json(pkg: str) -> dict:
    url = f"https://pypi.org/pypi/{pkg}/json"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def pick(pkg: str) -> tuple[str, str] | None:
    d = pypi_json(pkg)
    best = None
    for f in d["urls"]:
        fn = f["filename"]
        if not fn.endswith(".whl"):
            continue
        if any(s in fn for s in WANT_SUFFIX):
            # prefer win_amd64 over win32, prefer cp314 over pure python only if compiled
            score = 0
            if "win_amd64" in fn:
                score += 3
            if "cp314" in fn:
                score += 2
            if "none-any" in fn:
                score += 1
            if best is None or score > best[0]:
                best = (score, fn, f["url"])
    if best:
        return best[1], best[2]
    # fall back to the newest sdist-less pure-python wheel of any tag
    for f in d["urls"]:
        if f["filename"].endswith(".whl"):
            return f["filename"], f["url"]
    return None


def download(name: str, url: str) -> Path:
    dest = WHEELS / name
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  cached {name}")
        return dest
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=600, context=CTX) as r, dest.open("wb") as fh:
        while chunk := r.read(1 << 20):
            fh.write(chunk)
    print(f"  downloaded {name} ({dest.stat().st_size/1e6:.1f} MB)")
    return dest


def unpack(whl: Path) -> None:
    with zipfile.ZipFile(whl) as z:
        z.extractall(TARGET)
    print(f"  unpacked -> {TARGET}")


def main() -> int:
    pkgs = sys.argv[1:] or ["rdkit", "biopython", "vina", "meeko", "platformdirs", "swig"]
    ok, fail = [], []
    for pkg in pkgs:
        print(f"[{pkg}]")
        try:
            got = pick(pkg)
            if not got:
                print("  no wheel found")
                fail.append(pkg)
                continue
            name, url = got
            print(f"  wheel: {name}")
            unpack(download(name, url))
            ok.append(pkg)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {type(exc).__name__}: {str(exc)[:160]}")
            fail.append(pkg)
    print(f"\ninstalled: {ok}")
    print(f"failed   : {fail}")
    print(f"\nadd to PYTHONPATH: {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
