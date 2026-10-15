# -*- coding: utf-8 -*-
"""Probe the mechanism-analysis APIs: Open Targets, STRING, Enrichr, PubChem, ChEMBL."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}


def post(url, payload, hdr=None, timeout=90):
    h = dict(UA)
    h["Content-Type"] = "application/json"
    if hdr:
        h.update(hdr)
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "replace")


def get(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "replace")


def show(name, fn):
    try:
        fn()
    except urllib.error.HTTPError as e:
        print(f"[HTTP{e.code}] {name}: {e.read()[:150]!r}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name}: {type(e).__name__} {str(e)[:120]}")


OT = "https://api.platform.opentargets.org/api/v4/graphql"


def ot_drug_targets():
    q = """
    { search(queryString:"ethambutol", entityNames:["drug"]) {
        hits { id name entity } } }
    """
    r = json.loads(post(OT, {"query": q}))
    print("[OK  ] OT drug search:", json.dumps(r)[:400])


def ot_drug_known_targets():
    q = """
    { drug(chemblId:"CHEMBL448633") {
        id name drugType maximumClinicalTrialPhase
        mechanismsOfAction { rows { mechanismOfAction targetName targets { id approvedSymbol } } } } }
    """
    r = json.loads(post(OT, {"query": q}))
    print("[OK  ] OT drug MoA:", json.dumps(r)[:900])


def ot_disease_genes():
    q = """
    { disease(efoId:"EFO_0007401") {
        id name
        associatedTargets(page:{index:0,size:10}) {
          count
          rows { score target { id approvedSymbol approvedName } } } } }
    """
    r = json.loads(post(OT, {"query": q}))
    print("[OK  ] OT optic atrophy assoc:", json.dumps(r)[:700])


def ot_search_disease():
    for term in ["optic neuropathy", "optic atrophy", "toxic optic neuropathy",
                 "visual impairment", "retinal ganglion cell"]:
        q = '{ search(queryString:"%s", entityNames:["disease"]) { hits { id name } } }' % term
        r = json.loads(post(OT, {"query": q}))
        hits = r.get("data", {}).get("search", {}).get("hits", [])[:3]
        print(f"[OK  ] OT disease '{term}':", [(h["id"], h["name"]) for h in hits])


def string_api():
    u = ("https://string-db.org/api/tsv/network?identifiers=OPA1%0dMFN2%0dPOLG"
         "&species=9606&required_score=400")
    r = get(u)
    print("[OK  ] STRING network rows:", len(r.strip().split("\n")) - 1)
    u2 = ("https://string-db.org/api/tsv/ppi_enrichment?identifiers=OPA1%0dMFN2%0dPOLG"
          "&species=9606")
    print("[OK  ] STRING ppi_enrichment:", get(u2).replace("\n", " | ")[:400])


def enrichr():
    add = "https://maayanlab.cloud/Enrichr/addList"
    data = urllib.parse.urlencode({
        "list": "\n".join(["OPA1", "MFN2", "POLG", "SLC25A4", "BDNF", "NGF",
                           "SDHB", "SMAD4", "SOD2", "GPX4", "NFE2L2", "AKT1"]),
        "description": "test"}).encode()
    req = urllib.request.Request(add, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        j = json.loads(r.read().decode())
    uid = j["userListId"]
    print("[OK  ] Enrichr addList userListId:", uid)
    for lib in ["GO_Biological_Process_2023", "KEGG_2021_Human",
                "GO_Molecular_Function_2023", "GO_Cellular_Component_2023",
                "DisGeNET", "Jensen_DISEASES", "Reactome_2022",
                "MSigDB_Hallmark_2020", "WikiPathway_2023_Human",
                "TCMSP_Genes", "DSigDB", "CTD_Genes"]:
        try:
            u = f"https://maayanlab.cloud/Enrichr/enrich?userListId={uid}&backgroundType={lib}"
            d = json.loads(get(u, timeout=90))
            n = len(d.get(lib, []))
            print(f"[OK  ] Enrichr lib {lib}: {n} terms")
        except urllib.error.HTTPError as e:
            print(f"[HTTP{e.code}] Enrichr lib {lib}: unavailable")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] Enrichr lib {lib}: {str(e)[:60]}")


def pubchem_chem():
    for name in ["ethambutol", "quercetin", "luteolin", "chlorogenic acid",
                 "puerarin", "betaine", "astragaloside IV", "salvianolic acid B",
                 "ginkgolide B", "crocin", "kaempferol", "ferulic acid"]:
        try:
            u = (f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                 f"{urllib.parse.quote(name)}/property/MolecularFormula,CanonicalSMILES,"
                 f"MolecularWeight,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount/JSON")
            d = json.loads(get(u, timeout=45))["PropertyTable"]["Properties"][0]
            print(f"[OK  ] PubChem {name:22s} CID={d['CID']} {d.get('MolecularFormula')} "
                  f"MW={d.get('MolecularWeight')}")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] PubChem {name:22s} {type(e).__name__} {str(e)[:50]}")


def chembl():
    try:
        u = ("https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?"
             "q=ethambutol&limit=3")
        d = json.loads(get(u))
        for m in d["molecules"]:
            print("[OK  ] ChEMBL:", m["molecule_chembl_id"], m.get("pref_name"),
                  m.get("max_phase"))
    except Exception as e:  # noqa: BLE001
        print("[FAIL] ChEMBL:", str(e)[:90])


def uniprot_gene_lists():
    """Pull canonical gene sets for ocular / mitochondrial terms from UniProt."""
    for query, label in [
        ("(gene:OPA1 OR gene:MFN2 OR gene:POLG)", "mito"),
        ("reviewed:true AND organism_id:9606 AND go:0007601", "visual_perception"),
    ]:
        u = (f"https://rest.uniprot.org/uniprotkb/search?query="
             f"{urllib.parse.quote(query)}&size=5&format=json&fields=gene_primary,accession")
        try:
            d = json.loads(get(u, timeout=60))
            print(f"[OK  ] UniProt {label}: {len(d.get('results', []))} results")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] UniProt {label}: {str(e)[:70]}")


for n, f in [("OT_search_drug", ot_drug_targets), ("OT_MoA", ot_drug_known_targets),
             ("OT_disease_genes", ot_disease_genes), ("OT_disease_search", ot_search_disease),
             ("STRING", string_api), ("Enrichr", enrichr), ("PubChem", pubchem_chem),
             ("ChEMBL", chembl), ("UniProt", uniprot_gene_lists)]:
    show(n, f)
