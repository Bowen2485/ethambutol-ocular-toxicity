# -*- coding: utf-8 -*-
"""Refresh the period-coverage block inside main_results.json.

The block was embedded before the coverage query was corrected to distinguish cases from demo
rows; it still carried the superseded in_range figure (20,692,645) that the manuscript no longer
uses.  This replaces it with the verified counts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
main = json.loads((RES / "main_results.json").read_text(encoding="utf-8"))
cov = json.loads((RES / "audit_period_coverage.json").read_text(encoding="utf-8"))
main["period_coverage"] = cov
(RES / "main_results.json").write_text(json.dumps(main, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
print("period_coverage refreshed:", cov)
