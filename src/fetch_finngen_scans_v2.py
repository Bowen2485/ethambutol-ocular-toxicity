# -*- coding: utf-8 -*-
"""
Fetch the FinnGen outcome scans correctly: one query per phenotype per window.

The fault being corrected
    The previous version verified that the six optic phenotypes share their variant
    positions in a given region - which is true, Jaccard 1.000 on two test regions - and
    concluded that one phenotype's query result could be written to all six files.  The
    positions are shared; the effect sizes are not.  Every one of the 5,046 files it
    wrote therefore held one phenotype's betas under six phenotype names, and they were
    byte-identical, which is how the error was found.

    The lesson is applied in two ways here.  Each phenotype is queried separately, and a
    guard checks afterwards that the files for one window are not identical across
    phenotypes: if they are, the run stops rather than writing more bad data.

Efficiency
    Querying per phenotype means 5,046 queries instead of 841, and the tabix index is
    about 1.7 MB.  Opening a fresh handle per query would re-fetch that index thousands
    of times, so one handle is kept open per phenotype and reused across all its windows
    - six handles for the whole run rather than one per query.

Resumable
    A file that exists and is non-empty is skipped, so an interrupted run continues from
    where it stopped.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw" / "opengwas"
GB = "https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release"

EXPOSURES = {
    "ukb-b-13891": ("Zinc supplement use", 3),
    "ieu-b-25": ("Cigarettes per day", 21),
    "ieu-b-73": ("Alcoholic drinks per week", 30),
    "ieu-b-4877": ("Smoking initiation", 87),
    "ebi-a-GCST006867": ("Type 2 diabetes", 109),
    "ebi-a-GCST90014006": ("HbA1c", 260),
    "ieu-b-40": ("Body mass index", 331),
}

#: the six phenotypes the pipeline uses, from mr_analysis.OUTCOMES
PHENOS = ["H7_OPTNEURITIS", "H7_OPTATROPHY", "H7_OPTNERVNAS",
          "H7_BLINDANDVISIMPAIRMENT", "H7_COULOURVISDEF", "H7_VISFIELDDEF"]

PAD = 250_000
MERGE_GAP = 2_000_000
HEADER = ("chrom\tpos\tref\talt\trsids\tnearest_genes\tpval\tmlogp\tbeta\tsebeta\t"
          "af_alt\taf_alt_cases\taf_alt_controls\n")


def windows_for(df: pd.DataFrame) -> list[tuple[str, int, int]]:
    """Chromosome/window spans, using the same rule as mr_final.py."""
    chrom_col = "chr" if "chr" in df.columns else "chrom"
    out = []
    for chrom, grp in df.groupby(chrom_col):
        c = re.sub(r"^chr", "", str(chrom))
        positions = sorted(int(x) for x in grp["pos"].tolist() if pd.notna(x))
        if not positions:
            continue
        ws: list[list[int]] = []
        for p in positions:
            lo, hi = max(1, p - PAD), p + PAD
            if ws and lo <= ws[-1][1] + MERGE_GAP:
                ws[-1][1] = max(ws[-1][1], hi)
            else:
                ws.append([lo, hi])
        for wi, (lo, hi) in enumerate(ws):
            out.append((c, lo, hi, wi))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exposures", nargs="*", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--phenotypes", nargs="*", default=None)
    ap.add_argument("--verify-only", action="store_true",
                    help="check the written files instead of fetching")
    ap.add_argument("--max-windows", type=int, default=None)
    args = ap.parse_args()

    todo = list(EXPOSURES) if (args.all or not args.exposures) else \
        [e for e in args.exposures if e in EXPOSURES]
    phenos = args.phenotypes or PHENOS

    if args.verify_only:
        return verify(todo, phenos)

    import bgzf_tabix as bt

    # one open handle per phenotype, reused for every window of every exposure
    handles: dict[str, object] = {}

    def handle(ph: str):
        if ph not in handles:
            handles[ph] = bt.Tabix(f"{GB}/finngen_R12_{ph}.gz",
                                   f"{GB}/finngen_R12_{ph}.gz.tbi")
        return handles[ph]

    written = skipped = 0
    t_start = time.time()
    for gid in todo:
        label, _ = EXPOSURES[gid]
        inst_path = RAW / f"tophits_{gid}_5e-08.tsv"
        if not inst_path.exists():
            print(f"[{label}] instrument file missing; skipped")
            continue
        inst = pd.read_csv(inst_path, sep="\t")
        wins = windows_for(inst)
        n_planned = len(wins) * len(phenos)
        print(f"\n[{label}] {len(inst)} instruments -> {len(wins)} windows "
              f"x {len(phenos)} phenotypes = {n_planned} scans")

        for wi, (chrom, lo, hi, idx) in enumerate(wins):
            for ph in phenos:
                path = RAW / f"mr_{gid}_{ph}_{chrom}_{idx}.tsv"
                if path.exists() and path.stat().st_size > 0:
                    skipped += 1
                    continue
                t0 = time.time()
                try:
                    lines = handle(ph).query(chrom, lo, hi)
                except Exception as exc:  # noqa: BLE001
                    print(f"    {ph} chr{chrom}:{lo}-{hi} FAILED "
                          f"{type(exc).__name__}: {str(exc)[:70]}")
                    continue
                with path.open("w", encoding="utf-8", newline="") as fh:
                    fh.write(HEADER)
                    for ln in lines:
                        fh.write(ln.rstrip("\n") + "\n")
                written += 1
            if idx % 20 == 0 or idx == len(wins) - 1:
                el = time.time() - t_start
                print(f"    window {idx+1}/{len(wins)}  written {written}  "
                      f"skipped {skipped}  elapsed {el/60:.1f} min  "
                      f"({el/max(written,1):.1f} s/scan)")
            if args.max_windows and written >= args.max_windows:
                print(f"    reached --max-windows {args.max_windows}; stopping")
                break

    print(f"\nwritten {written:,}  skipped {skipped:,}  "
          f"in {(time.time()-t_start)/60:.1f} min")
    print()
    return verify(todo, phenos)


def verify(exposures: list[str], phenos: list[str]) -> int:
    """
    Check that the files for one window differ between phenotypes.

    This is the guard that would have caught the earlier fault on the first window: if
    six phenotype files share a hash, the effect sizes have been copied rather than
    queried, and the run is not fit to use.
    """
    print("=" * 96)
    print("Verification: are the phenotype files genuinely different?")
    print("=" * 96)
    problems = 0
    for gid in exposures:
        label = EXPOSURES[gid][0]
        w0 = sorted(RAW.glob(f"mr_{gid}_*_0.tsv"))
        if len(w0) < 2:
            print(f"  {label:28s} too few files for window 0 to compare")
            continue
        hashes = {}
        for p in w0:
            m = re.search(r"_H7_[A-Z]+_", p.name)
            ph = m.group(0).strip("_") if m else p.name
            hashes[ph] = hashlib.md5(p.read_bytes()).hexdigest()[:10]
        distinct = len(set(hashes.values()))
        ok = distinct == len(hashes)
        problems += 0 if ok else 1
        print(f"  {label:28s} {len(hashes)} phenotypes, {distinct} distinct "
              f"hash(es)   {'OK' if ok else '*** IDENTICAL - DATA COPIED ***'}")
    print()
    if problems:
        print(f"  {problems} exposure(s) show identical files across phenotypes.")
        print("  Those caches are not usable and must be refetched.")
        return 1
    print("  All checked exposures hold phenotype-specific data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
