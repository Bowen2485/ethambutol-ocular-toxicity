# -*- coding: utf-8 -*-
"""Verify key records: write output to a UTF-8 file (avoids PowerShell UTF-16 redirects)."""
import io
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pmids = sys.argv[1]
outname = sys.argv[2]

buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
sys.argv = ["show_pmid.py", pmids]
try:
    runpy.run_path(os.path.join(ROOT, "src", "show_pmid.py"), run_name="__main__")
finally:
    sys.stdout = old

path = os.path.join(ROOT, "data", "derived", outname)
with open(path, "w", encoding="utf-8") as f:
    f.write(buf.getvalue())
print("written", path, len(buf.getvalue().splitlines()), "lines")
