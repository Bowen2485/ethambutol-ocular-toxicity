# -*- coding: utf-8 -*-
"""Repair Chinese inner quotes that were normalised to ASCII double quotes.

Rule (character level, no string-state machine): a '"' is an INNER quote when
    * the character AFTER it is CJK / full-width (>= U+2000), AND
    * the character BEFORE it is CJK / full-width, or '*'
Legitimate Python delimiters are always adjacent to ASCII (space, comma, paren,
colon, backslash), except an opening delimiter that directly precedes CJK text,
in which case the preceding character is '(' ',' ':' '=' or a space -- none of
which are CJK and none of which are '*'.  So delimiters are preserved.

Use --revert to turn previously inserted 「 / 」 back into '"' first, making the
transform idempotent.
"""
import sys

CJK_MIN = 0x2000


def revert(text):
    return text.replace("「", '"').replace("」", '"')


def is_cjk(ch):
    return bool(ch) and ord(ch) >= CJK_MIN


DELIM_NEXT = set(",)]:}")

def fix(text):
    out_lines = []
    n = 0
    for line in text.split("\n"):
        if '"' not in line or not any(is_cjk(c) for c in line):
            out_lines.append(line)
            continue
        res = []
        open_inner = False
        last = ""          # last EMITTED character
        for i, ch in enumerate(line):
            if ch != '"':
                res.append(ch)
                last = ch
                continue
            nxt = line[i + 1] if i + 1 < len(line) else ""
            if open_inner:
                if nxt in DELIM_NEXT or nxt == "":
                    # string delimiter, not an inner quote
                    res.append(ch)
                    open_inner = False
                else:
                    res.append("」")
                    open_inner = False
                    n += 1
                last = res[-1]
                continue
            if is_cjk(nxt) and (is_cjk(last) or last == "*"):
                res.append("「")
                open_inner = True
                n += 1
            else:
                res.append(ch)
            last = res[-1]
        out_lines.append("".join(res))
    return "\n".join(out_lines), n


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0]
    with open(path, encoding="utf-8") as f:
        src = f.read()
    if "--revert" in sys.argv:
        src = revert(src)
    fixed, n = fix(src)
    with open(path, "w", encoding="utf-8") as f:
        f.write(fixed)
    print(f"replaced {n} inner quotes in {path}")


if __name__ == "__main__":
    main()
