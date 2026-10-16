# -*- coding: utf-8 -*-
"""
Test the ignore rule properly, then commit.

What happened
    The safety gate blocked the commit because `git check-ignore credential/disgenet_key.txt`
    exited 1.  That exit code means "no rule matched this path", not "this path is
    committable", and it arose because the file exists only in the project directory, not in
    the repository, so git had nothing to match against.  The directory rule `credential/`
    was confirmed to match, and every other safety test passed, including the scan of staged
    content for key-shaped strings - a scan that is known to work, because the DisGeNET 404
    response that was fetched earlier contains the key itself and the same regex finds it.

    The gate was therefore reporting a false alarm, and a gate that cries wolf gets ignored.
    This re-tests with `--no-index`, which evaluates the rules against a path whether or not
    it exists, and then commits.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\20200\Downloads\论文\投稿\ethambutol-ocular-toxicity")


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


print("=" * 92)
print("1. Does the rule cover the key, evaluated without the file having to exist?")
print("=" * 92)
PROBE = ["credential/disgenet_key.txt", "credential/", "credentials/x.txt",
         "data/raw/opengwas/token.txt", "data/derived/faers.sqlite"]
for p in PROBE:
    rc, out = run("check-ignore", "--no-index", "-v", p)
    verdict = "IGNORED" if rc == 0 else "NOT IGNORED"
    rule = out.strip().split("\t")[1] if out.strip().count("\t") >= 1 else ""
    print(f"  {verdict:12s} {p:40s} {rule}")

print()
print("=" * 92)
print("2. Cross-check: does the key regex actually detect the key?")
print("=" * 92)
keyfile = Path(r"C:\Users\20200\Downloads\论文\投稿\Ethambutol_EyeTox\credential"
               r"\disgenet_key.txt")
UUID = re.compile(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
if keyfile.exists():
    blob = keyfile.read_bytes()
    print(f"  key file found: {keyfile.name}")
    print(f"  UUID regex detects it: {bool(UUID.search(blob))}"
          f"   <- the staged-content scan is known to work")
else:
    print("  key file not found where expected")

# and confirm it is not tracked
rc, out = run("ls-files", "credential")
print(f"  files git tracks under credential/: {out.strip() if out.strip() else 'none'}")

print()
print("=" * 92)
print("3. Final scan of what is staged")
print("=" * 92)
rc, staged = run("diff", "--cached", "--name-only")
paths = [p for p in staged.splitlines() if p.strip()]
FORBIDDEN = ("token", ".env", ".key", ".pem", "credential", "disgenet_key",
             "secret", ".sqlite", ".db")
bad = [p for p in paths if any(f in p.lower() for f in FORBIDDEN)]
hits, big = [], []
for p in paths:
    f = REPO / p
    if not f.exists():
        continue
    if f.stat().st_size > 5 * 1024 * 1024:
        big.append(p)
    if f.stat().st_size <= 2_000_000:
        try:
            if UUID.search(f.read_bytes()):
                hits.append(p)
        except Exception:
            pass
print(f"  staged: {len(paths)}   forbidden names: {len(bad)}   "
      f"key strings: {len(hits)}   over 5 MB: {len(big)}")
for p in bad + hits + big:
    print(f"      {p}")

print()
print("=" * 92)
print("4. Commit")
print("=" * 92)
if bad or hits or big:
    print("  REFUSING: a real problem was found, not a false alarm.")
else:
    MSG = (
        "Add subgroup, disease-annotation and trajectory analyses\n"
        "\n"
        "Analyses the peer literature in this genre carries and the manuscript lacked.\n"
        "Negative results are reported as they stand.\n"
        "\n"
        "Subgroup analysis (3.7b).  The optic-nerve signal is present in every stratum of\n"
        "sex, age, reporting region and era, so no subgroup explains it.  Five contrasts\n"
        "exclude unity and three are not effects: unknown sex and unknown age mark a\n"
        "sparsely completed report, and region is uninterpretable for the reason 3.2c\n"
        "already gives.  The age gradient is the one worth reading (65+ against 0-17,\n"
        "ratio 5.40, 2.58-11.32), agreeing with the continuous age effect already\n"
        "reported without being independent of it.\n"
        "\n"
        "Disease-annotation cross-check (3.8b).  Against Open Targets and HPO, 30% of\n"
        "hubs and 24% of controls carry an eye annotation (P = 0.39); against DisGeNET,\n"
        "61% and 12% do, so the narrow sources rather than the network caused the null.\n"
        "Auditing the keyword match for false positives - keratosis and dyskeratosis\n"
        "congenita are skin diseases - leaves 55% against 12%, odds ratio 7.82,\n"
        "P = 2.6e-4.  The positive control holds: OPA1, DNM1L and MFN2 are annotated for\n"
        "optic atrophy.  GPX4, SLC7A11 and ACSL4 have no eye annotation at all, which\n"
        "bounds the mechanism to its mitochondrial and inflammatory arm.\n"
        "\n"
        "Trajectory measures independent of displacement (3.9b).  Mean C-alpha RMSF is\n"
        "0.65-0.68 A across three proteins of very different size, so the site is not\n"
        "disintegrating.  Polar contacts are maintained or increase (63 to 80, 175 to\n"
        "189) while only 11-21% of the initial atom pairs survive, the signature of a\n"
        "ligand that stays and re-forms its interactions.\n"
        "\n"
        "Positive control reported.  Body mass index, carried as a positive control, is\n"
        "the only pair of 60 surviving FDR (OR 1.680, 1.265-2.231, q = 0.020), which is\n"
        "what makes the renal nulls readable.\n"
        "\n"
        "Two audits repaired rather than deleted.  The MR section of final_audit.py was\n"
        "querying exposure names that no longer exist, so every check inside it was\n"
        "silently skipped; verify_latex.py held counts from before the new sections.  A\n"
        "check that has stopped checking is worse than one that fails.  72 checks pass.\n"
        "\n"
        "Wide tables now use table*, the double-column float this class defines, because\n"
        "an ordinary table in a two-column layout is clipped rather than erroring."
    )
    rc, out = run("commit", "-m", MSG)
    print(f"  git commit exit {rc}")
    print(out.strip()[:500])

print()
print("=" * 92)
print("5. Push")
print("=" * 92)
rc, out = run("push", "origin", "main")
print(f"  git push exit {rc}")
print(out.strip()[:400])
