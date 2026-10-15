# -*- coding: utf-8 -*-
"""Print the journal map compactly."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "data", "derived", "journal_map.json"), encoding="utf-8") as f:
    m = json.load(f)
for pm, v in sorted(m.items(), key=lambda kv: (kv[1].get("year") or "", kv[0])):
    au = (v.get("authors") or "").split(",")[0].strip()
    print(f"{pm}|{v.get('year')}|{au}|{v.get('journal')}|{(v.get('title') or '')[:95]}")
