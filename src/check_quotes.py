# -*- coding: utf-8 -*-
"""Report lines of a Python file with an odd number of ASCII double quotes."""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()
n = 0
for i, line in enumerate(s.splitlines(), 1):
    if line.count('"') % 2 == 1:
        n += 1
        print(i, "|", line[:160])
print("total odd-quote lines:", n)
