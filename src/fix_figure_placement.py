# -*- coding: utf-8 -*-
"""Place the figures inline instead of as [p] floats, and escape LaTeX specials in the captions.

Two faults: "95% confidence intervals" was cut at the percent sign, because % starts a comment in
LaTeX, and a float page centres its content vertically, which left most of each figure page blank.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "src" / "build_tads_pdf.py"
s = p.read_text(encoding="utf-8")

start = s.index("fig_block = []")
end = s.index('main_start = text.find("## 1. Introduction")')
new = '''def tex_escape(t: str) -> str:
    """Percent, ampersand and underscore are active in LaTeX and truncate or break the caption."""
    return (t.replace("\\\\", r"\\textbackslash{}").replace("%", r"\\%")
             .replace("&", r"\\&").replace("_", r"\\_")
             .replace("#", r"\\#").replace("$", r"\\$"))


fig_block = []
for key, stem in FIG_FILES.items():
    path = FIG / f"{stem}.pdf"
    if not path.exists():
        print(f"  missing figure {path}")
        continue
    n = int(re.sub(r"[^0-9]", "", key) or 0)
    caption = tex_escape(legend_text.get(n, ""))
    #: an inline figure starts at the top of a fresh page; a [p] float is centred vertically,
    #: which left most of each figure page empty
    fig_block.append(r"\\clearpage")
    fig_block.append(r"\\noindent\\includegraphics[width=0.96\\linewidth]{" + str(path.as_posix()) + "}")
    if caption:
        fig_block.append(r"\\par\\vspace{8pt}")
        fig_block.append(r"{\\footnotesize\\raggedright\\noindent\\textbf{Figure " + str(n) + ".} "
                         + caption + r"\\par}")

'''
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("figures: inline placement and escaped captions")
