# -*- coding: utf-8 -*-
"""Final statistics for the report."""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")


def main():
    tot = {}
    seen = set()
    for p in sorted(glob.glob(os.path.join(RAW, "epmc_*.json"))):
        n = os.path.basename(p)[5:-5]
        if n.endswith("meta"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        vals = [v for v in d.values() if isinstance(v, dict) and "title" in v]
        if not vals:
            continue
        tot[n] = len(d)
        for v in vals:
            seen.add(str(v.get("pmid") or v.get("id")))

    eth = sorted(k for k in tot if k.startswith("q") or k.startswith("s"))
    tcm = sorted(k for k in tot if k.startswith("t") or k == "s8_tcm_optic_extra")
    print("=== Europe PMC harvest groups ===")
    ethambutol_groups = ["q1_optic_neuropathy", "q2_imaging", "q3_pharmacovigilance",
                         "q4_mechanism", "q5_dose_risk", "q6_other_antiTB"]
    print("-- 乙胺丁醇主线 --")
    for k in ethambutol_groups:
        print(f"   {k:26s} {tot.get(k, 0)}")
    print(f"   {'小计':26s} {sum(tot.get(k, 0) for k in ethambutol_groups)}")
    supp = [k for k in tot if k.startswith("s") and k != "s8_tcm_optic_extra"]
    print("-- 定向补充检索 --")
    for k in sorted(supp):
        print(f"   {k:26s} {tot[k]}")
    print(f"   {'小计':26s} {sum(tot[k] for k in supp)}")
    print("-- 中医药 --")
    tcm_groups = ["t1_tcm_optic", "t2_network_pharm", "t3_monomers", "t4_formulas",
                  "s8_tcm_optic_extra"]
    for k in tcm_groups:
        print(f"   {k:26s} {tot.get(k, 0)}")
    print(f"   {'小计':26s} {sum(tot.get(k, 0) for k in tcm_groups)}")
    print(f"\n全部检索记录（去重后唯一记录数）: {len(seen)}")

    with open(os.path.join(ROOT, "data", "derived", "eon_corpus.json"),
              encoding="utf-8") as f:
        eon = json.load(f)
    print(f"EON 核心语料库（标题同时含乙胺丁醇与眼部词）: {len(eon)}")

    print("\n=== 交付文件 ===")
    grand = 0
    for name in ("literature_ethambutol_ocular.md", "tcm_optic_neuropathy_background.md"):
        path = os.path.join(ROOT, "docs", name)
        t = open(path, encoding="utf-8").read()
        pm = set(re.findall(r"PMID:\s*(\d{4,9})", t))
        grand += len(pm)
        print(f"   {path}")
        print(f"      行数 {len(t.splitlines())} | 字符 {len(t)} | 引用 PMID {len(pm)} 条")
    print(f"   两个文件合计引用 PMID（含重叠）: {grand}")


if __name__ == "__main__":
    main()
