# -*- coding: utf-8 -*-
"""
Step 3 - Tiered mechanism network of ethambutol ocular toxicity.

Data situation (established in earlier steps)
  * Open Targets records no human mechanism of action for ethambutol: the drug
    inhibits the mycobacterial arabinosyltransferases EmbA/EmbB (no human
    orthologue), so human ocular toxicity must be off-target / downstream.
  * A Europe PMC full-text mine over 3,034 papers (step 3b) yields 67 human genes
    with direct co-mention evidence, led by TNF, NAT2, OPA1, SDHB/SMAD4/GPX4
    (ferroptosis axis, PMID 41563626), BDNF/NGF/TRKB (Müller-glia rescue,
    PMID 41184893), TFEB (autophagy) and the cytochrome P450 set.
  * Open Targets supplies the optic-nerve phenotype gene landscape; the broad
    retinal-dystrophy phenotype is deliberately excluded because it floods the
    network with photoreceptor genes (RHO, PDE6B, ABCA4, ...) that have no
    mechanistic link to a ganglion-cell axonopathy.

Network tiers
  Tier A (focused)  : literature evidence >= 2 papers  U  curated core panel
  Tier B (extended) : Tier A  U  literature >= 1  U  optic-nerve phenotype
                      genes with OT association score >= 0.1
  Tier C (landscape): Tier B  U  top 50 optic-nerve phenotype genes per phenotype
                      (used only for over-representation background context)

For each tier: STRING PPI (confidence >= 0.4), hub ranking, g:Profiler enrichment.
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
for p in (DERIVED, RESULTS):
    p.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}
OT = "https://api.platform.opentargets.org/api/v4/graphql"

# optic-nerve / ganglion-cell phenotype space only (no retinal dystrophy)
OPTIC_DISEASES = {
    "MONDO_0003608": "optic atrophy",
    "MONDO_0010788": "Leber hereditary optic neuropathy",
    "MONDO_0020249": "hereditary optic neuropathy",
    "MONDO_0020250": "autosomal dominant optic atrophy",
    "MONDO_0014483": "retinal dystrophy with inner retinal dysfunction",
    "HP_0000505": "visual impairment",
}

# Papers whose gene co-mention is driven by mycobacterial-immunity or unrelated
# pharmacogenomics rather than ocular toxicity; excluded after manual review of
# the example titles returned by step 3b.
LIT_EXCLUDE = {"STAT1", "STAT3", "IFNGR1", "IFNGR2", "TYK2", "CYBB", "XIAP",
               "ABCG2", "SLC22A2", "IDH2", "ATG13", "ATG16L1", "MAP1LC3B",
               "PIK3R1", "NOS2", "TSC1", "MPO", "TLR4", "CS"}

CORE_PANEL = {
    "OPA1": "ADOA gene; mitochondrial cristae remodelling",
    "SDHB": "complex II; ferroptosis axis in EON",
    "SMAD4": "TGF-beta effector upstream of SDHB in EON",
    "GPX4": "ferroptosis gatekeeper",
    "SLC7A11": "xCT cystine import, ferroptosis",
    "ACSL4": "ferroptosis executioner",
    "BDNF": "TrkB-mediated RGC rescue",
    "NTRK2": "TrkB receptor",
    "AKT1": "survival kinase downstream of TrkB",
    "NFE2L2": "Nrf2 antioxidant programme",
    "HMOX1": "haem oxygenase 1",
    "SOD2": "mitochondrial superoxide dismutase",
    "MCOLN1": "TRPML1 lysosomal zinc release",
    "SLC30A10": "zinc efflux",
    "MT1A": "metallothionein zinc buffering",
    "POLG": "mtDNA polymerase",
    "MFN2": "mitochondrial fusion",
    "SLC25A4": "ANT1",
    "TXN2": "mitochondrial thioredoxin",
    "PRDX3": "mitochondrial peroxiredoxin",
    "TFEB": "lysosomal-autophagy master regulator",
    "NAT2": "N-acetyltransferase 2, anti-TB pharmacogenetics",
    "TNF": "neuroinflammation",
    "CASP3": "apoptotic executioner",
    "BAX": "pro-apoptotic",
    "BCL2": "anti-apoptotic",
    "TP53": "stress-induced apoptosis",
}


# ------------------------------------------------------------------ transport
def _post_graphql(query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    last = None
    for a in range(5):
        try:
            req = urllib.request.Request(
                OT, data=body, headers={**UA, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode()[:300]
            except Exception:  # noqa: BLE001
                pass
            raise RuntimeError(f"OT HTTP {exc.code}: {detail}")
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (a + 1))
    raise RuntimeError(f"OT failed: {last}")


def _string_post(endpoint: str, genes: list[str], extra: dict | None = None) -> str:
    payload = {"identifiers": "\r".join(genes), "species": 9606,
               "caller_identity": "ethambutol_eon"}
    if extra:
        payload.update(extra)
    req = urllib.request.Request(
        f"https://string-db.org/api/tsv/{endpoint}",
        data=urllib.parse.urlencode(payload).encode(), headers=UA)
    with urllib.request.urlopen(req, timeout=600, context=CTX) as r:
        return r.read().decode("utf-8", "replace")


def string_network(genes: list[str], score: int, tag: str) -> pd.DataFrame:
    cache = DERIVED / f"string_network_{tag}_{score}.tsv"
    if cache.exists():
        return pd.read_csv(cache, sep="\t") if cache.stat().st_size > 1 else pd.DataFrame()
    txt = _string_post("network", genes, {"required_score": score})
    cache.write_text(txt if txt.strip() else "\n", encoding="utf-8")
    return pd.read_csv(cache, sep="\t") if txt.strip() else pd.DataFrame()


def string_enrichment(genes: list[str], tag: str) -> pd.DataFrame:
    cache = DERIVED / f"string_enrichment_{tag}.tsv"
    if cache.exists():
        return pd.read_csv(cache, sep="\t") if cache.stat().st_size > 1 else pd.DataFrame()
    txt = _string_post("enrichment", genes)
    cache.write_text(txt if txt.strip() else "\n", encoding="utf-8")
    return pd.read_csv(cache, sep="\t") if txt.strip() else pd.DataFrame()


def gprofiler_universe() -> set[str]:
    """
    g:Profiler has no endpoint that returns the accepted gene universe
    (organisms_list carries metadata only), so identifier validity is handled by
    gprofiler() itself with a bisecting re-query.  Kept for API compatibility.
    """
    return set()


def _gost_call(query: list[str], tries: int = 4) -> dict | None:
    body = json.dumps({
        "organism": "hsapiens", "query": query,
        "sources": ["GO:BP", "GO:MF", "GO:CC", "KEGG", "REAC", "WP", "HP"],
        "user_threshold": 0.05, "significance_threshold_method": "fdr",
        "no_evidences": False, "ordered": False, "all_results": False,
    }).encode()
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(
                "https://biit.cs.ut.ee/gprofiler/api/gost/profile/", data=body,
                headers={**UA, "Content-Type": "application/json",
                         "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=420, context=CTX) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode()[:250]
            except Exception:  # noqa: BLE001
                pass
            last = f"HTTP {exc.code}: {detail}"
            if exc.code == 400:
                return {"__error__": last}
            time.sleep(2.0 * (a + 1))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2.0 * (a + 1))
    print(f"[g:Profiler] giving up: {last}")
    return None


def _flatten_intersections(items) -> str:
    """g:Profiler returns intersections either as symbols or as [symbol, evidence]."""
    out: list[str] = []
    for it in items or []:
        if isinstance(it, str):
            out.append(it)
        elif isinstance(it, (list, tuple)) and it:
            out.append(str(it[0]))
        elif isinstance(it, dict):
            out.append(str(it.get("gene") or it.get("id") or ""))
    return ";".join(sorted({g for g in out if g}))


def gprofiler(genes: list[str], tag: str) -> pd.DataFrame:
    cache = DERIVED / f"gprofiler_{tag}.json"
    if cache.exists():
        payload = json.loads(cache.read_text(encoding="utf-8"))
    else:
        query = sorted(set(genes))
        print(f"[g:Profiler:{tag}] querying {len(query)} symbols ...")
        payload = _gost_call(query)
        # g:Profiler rejects the whole request if any identifier is unknown, so
        # bisect to isolate and remove the offending symbols, then retry.
        for _ in range(8):
            if payload is None or "__error__" not in payload:
                break
            print(f"[g:Profiler:{tag}] bad identifier in set, bisecting ...")
            keep: list[str] = []
            stack = [query]
            while stack:
                chunk = stack.pop()
                if not chunk:
                    continue
                r = _gost_call(chunk, tries=2)
                if r is not None and "__error__" not in r:
                    keep.extend(chunk)
                    continue
                if len(chunk) == 1:
                    print(f"[g:Profiler:{tag}]   dropped {chunk[0]}")
                    continue
                mid = len(chunk) // 2
                stack.append(chunk[:mid])
                stack.append(chunk[mid:])
            query = sorted(set(keep))
            if not query:
                return pd.DataFrame()
            payload = _gost_call(query)
        if payload is None or "__error__" in (payload or {}):
            print(f"[g:Profiler:{tag}] FAILED: {payload}")
            return pd.DataFrame()
        cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    rows = [{
        "source": x.get("source"), "term_id": x.get("native"),
        "term_name": x.get("name"), "p_value": x.get("p_value"),
        "significant": x.get("significant"), "term_size": x.get("term_size"),
        "intersection_size": x.get("intersection_size"),
        "precision": x.get("precision"), "recall": x.get("recall"),
        "genes": _flatten_intersections(x.get("intersections")),
    } for x in payload.get("result", [])]
    df = pd.DataFrame(rows)
    n_sig = int(df["significant"].sum()) if not df.empty else 0
    print(f"[g:Profiler:{tag}] {len(df)} terms, {n_sig} significant (FDR<0.05)")
    return df


def disease_genes(efo: str, name: str, size: int = 800) -> pd.DataFrame:
    cache = DERIVED / f"ot_disease_{efo}.json"
    if cache.exists():
        payload = json.loads(cache.read_text(encoding="utf-8"))
    else:
        q = """
        query($id:String!,$size:Int!) {
          disease(efoId:$id) {
            id name
            associatedTargets(page:{index:0,size:$size}) {
              count rows { score target { id approvedSymbol } } }
          }
        }"""
        payload = _post_graphql(q, {"id": efo, "size": size})
        cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    dis = (payload.get("data") or {}).get("disease")
    if not dis:
        print(f"[OT] {efo} ({name}): NOT FOUND")
        return pd.DataFrame(columns=["gene", "score", "disease", "efo"])
    rows = [{"gene": r["target"]["approvedSymbol"], "score": r["score"],
             "disease": dis["name"], "efo": efo}
            for r in (dis.get("associatedTargets") or {}).get("rows") or []]
    print(f"[OT] {dis['name'][:48]:50s} total={(dis.get('associatedTargets') or {}).get('count')}"
          f" fetched={len(rows)}")
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ hub ranking
def analyse(tier: str, genes: list[str], score: int = 400) -> tuple[pd.DataFrame, nx.Graph]:
    print(f"\n[{tier}] {len(genes)} input genes -> STRING (confidence>={score/1000:.1f})")
    edges = string_network(genes, score, tier)
    G = nx.Graph()
    for _, e in edges.iterrows():
        a, b = e.get("preferredName_A"), e.get("preferredName_B")
        w = float(e.get("score", 0.4) or 0.4)
        if a and b:
            G.add_edge(a, b, weight=w)
    print(f"[{tier}] graph: nodes={G.number_of_nodes()} edges={G.number_of_edges()}")
    if G.number_of_edges() == 0:
        return pd.DataFrame(), G
    deg = dict(G.degree())
    btw = nx.betweenness_centrality(G)
    clo = nx.closeness_centrality(G)
    df = pd.DataFrame({"gene": list(G.nodes())})
    df["degree"] = df.gene.map(deg).fillna(0).astype(int)
    df["betweenness"] = df.gene.map(btw).fillna(0.0)
    df["closeness"] = df.gene.map(clo).fillna(0.0)
    df["tier"] = tier
    df = df.sort_values(["degree", "betweenness"], ascending=False)
    df["degree_rank"] = df.degree.rank(ascending=False, method="min").astype(int)
    return df, G


def main() -> int:
    print("=" * 78)
    print("STEP 3  tiered mechanism network of ethambutol ocular toxicity")
    print("=" * 78)

    lit = pd.read_csv(DERIVED / "literature_human_targets.csv", encoding="utf-8-sig")
    lit = lit[~lit.gene.isin(LIT_EXCLUDE)].copy()
    lit_ge2 = set(lit[lit.n_papers >= 2]["gene"])
    lit_all = set(lit["gene"])
    print(f"[lit] {len(lit_all)} genes after noise filter; {len(lit_ge2)} with >=2 papers")

    parts = []
    for efo, nm in OPTIC_DISEASES.items():
        try:
            parts.append(disease_genes(efo, nm))
        except Exception as exc:  # noqa: BLE001
            print(f"[OT] {efo} failed: {str(exc)[:120]}")
        time.sleep(0.3)
    dis = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["gene", "score", "disease", "efo"])
    dis.to_csv(DERIVED / "ot_optic_disease_genes.csv", index=False, encoding="utf-8-sig")
    dis_best = (dis.sort_values("score", ascending=False).drop_duplicates("gene")
                if not dis.empty else dis)
    dis_hi = set(dis_best[dis_best.score >= 0.1]["gene"]) if not dis.empty else set()
    print(f"[OT] optic-nerve phenotype genes: {dis_best.gene.nunique() if not dis.empty else 0}"
          f" (score>=0.10: {len(dis_hi)})")

    core = set(CORE_PANEL)
    tierA = sorted((lit_ge2 | core) & (lit_all | core))
    tierB = sorted(set(tierA) | (lit_all & (dis_hi | lit_all)) | (core))
    tierB = sorted(set(tierB) | {g for g in lit_all})
    tierB = sorted(set(tierB) | ({g for g in dis_hi} if dis_hi else set()))
    tiers = {"A_focused": tierA, "B_extended": tierB}
    print(f"\n[tiers] A={len(tierA)}  B={len(tierB)}")

    hubs_all = []
    for tier, genes in tiers.items():
        hub, G = analyse(tier, genes)
        if hub.empty:
            continue
        hub["in_core_panel"] = hub.gene.isin(core)
        hub["in_literature"] = hub.gene.isin(lit_all)
        hub["n_lit_papers"] = hub.gene.map(
            lit.set_index("gene")["n_papers"]).fillna(0).astype(int)
        hub["otic_assoc_score"] = hub.gene.map(
            dis_best.set_index("gene")["score"] if not dis_best.empty else {}).fillna(0.0)
        hub["otic_phenotype"] = hub.gene.map(
            dis_best.set_index("gene")["disease"] if not dis_best.empty else {})
        hub.to_csv(RESULTS / f"mechanism_hub_{tier}.csv", index=False,
                   encoding="utf-8-sig")
        hubs_all.append(hub)
        cols = ["gene", "degree", "betweenness", "n_lit_papers", "in_core_panel",
                "otic_assoc_score"]
        print(f"\n[{tier}] top 25 hubs:")
        print(hub.head(25)[cols].to_string(index=False, max_colwidth=26))

        # enrichment on the tier panel
        enr = gprofiler(genes, tier)
        if not enr.empty:
            enr.to_csv(RESULTS / f"mechanism_enrichment_{tier}.csv", index=False,
                       encoding="utf-8-sig")
            sig = enr[enr.significant == True].sort_values("p_value")  # noqa: E712
            if not sig.empty:
                print(f"\n[{tier}] top 20 enriched terms:")
                print(sig.head(20)[["source", "term_id", "term_name", "p_value",
                                    "intersection_size", "term_size"]]
                      .to_string(index=False, max_colwidth=52))
        se = string_enrichment(genes, tier)
        if not se.empty:
            se.to_csv(RESULTS / f"mechanism_string_enrichment_{tier}.csv", index=False,
                      encoding="utf-8-sig")
            keep = [c for c in ("category", "term", "description", "fdr",
                                "number_of_genes") if c in se.columns]
            print(f"\n[{tier}] STRING functional enrichment (top 12 by FDR):")
            print(se.sort_values("fdr")[keep].head(12)
                  .to_string(index=False, max_colwidth=46))

    if hubs_all:
        allh = pd.concat(hubs_all, ignore_index=True)
        allh.to_csv(RESULTS / "mechanism_hub_genes.csv", index=False,
                    encoding="utf-8-sig")

    # writer's table: the consensus hub panel
    if hubs_all:
        a_only = hubs_all[0]
        consensus = a_only.head(40)[["gene", "degree", "betweenness", "n_lit_papers",
                                     "in_core_panel", "otic_assoc_score",
                                     "otic_phenotype"]]
        consensus.to_csv(RESULTS / "mechanism_consensus_hubs.csv", index=False,
                         encoding="utf-8-sig")
        print(f"\n[consensus] top 40 focused-tier hubs -> "
              f"{RESULTS / 'mechanism_consensus_hubs.csv'}")

    print("\n[done] mechanism step complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
