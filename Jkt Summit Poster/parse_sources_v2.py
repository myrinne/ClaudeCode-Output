"""Parse the v2 search exports (2026-10-05) into one deduplicated record list,
flag records already screened in v1 (records.json), save records_v2.json.

PubMed: citation-format export -> abstracts via NCBI E-utilities (reused from v1).
Scopus: plain-text export (one record per EID: line).
ProQuest: full 128-record text export (the 100-record file is a partial subset).
IEEE Xplore: two CSV pages (100 + 35, no overlap); abstracts included.
"""
import csv
import json
import re
import time
from pathlib import Path

import requests

import parse_sources as v1

SRC = Path(r"C:\Users\vidya\OneDrive\Documents\PPDS Okupasi\Jkt Summit\Search Result V2")
HERE = Path(__file__).parent
V1_JSON = Path(r"C:\Users\vidya\OneDrive\Documents\ClaudeCode Output\Jkt Summit Poster\records.json")
OUT = HERE / "records_v2.json"


def parse_pubmed():
    return v1.parse_pubmed(SRC / "Pubmedsummary-Occupation-set.txt")


def parse_scopus():
    txt = (SRC / "Scopus Export.txt").read_text(encoding="utf-8").replace("\r", "")
    recs = []
    for n, chunk in enumerate(re.split(r"\nEID: [^\n]+\n", txt), 1):
        lines = [l for l in chunk.split("\n") if l.strip()]
        url_i = next((i for i, l in enumerate(lines) if l.startswith("https://www.scopus.com")), None)
        if url_i is None:
            continue
        abstract = next((l[len("ABSTRACT: "):] for l in lines[url_i:] if l.startswith("ABSTRACT: ")), "")
        abstract = re.sub(r"\s*©.*$", "", abstract)
        doi = next((l[5:].strip() for l in lines[:url_i] if l.startswith("DOI: ")), "")
        head = [l for l in lines[:url_i] if not l.startswith(("DOI: ", "AUTHOR FULL NAMES:", "Scopus", "EXPORT DATE"))
                and not re.fullmatch(r"[\d; ]+", l)]
        # head = [authors, title, (year) ...] ; authors line may be absent
        yi = next((i for i, l in enumerate(head) if re.match(r"^\((19|20)\d{2}\)", l)), len(head))
        title = head[yi - 1] if yi >= 1 else ""
        authors = head[0] if yi >= 2 else ""
        year = re.match(r"^\(((?:19|20)\d{2})\)", head[yi]).group(1) if yi < len(head) else ""
        eid = re.search(r"publications/(\d+)", lines[url_i]).group(1)
        recs.append({"source": "Scopus", "id": f"Scopus {eid}", "title": title, "abstract": abstract, "year": year,
                     "journal": head[yi][len(year) + 2:].strip(" ,") if yi < len(head) else "", "doi": doi.lower(),
                     "authors": ", ".join(authors.split(", ")[:3]) + (" et al." if authors.count(",") > 2 else ""),
                     "pub_type": ""})
    return recs


def parse_proquest():
    return v1.parse_proquest(SRC / "ProQuestDocuments-2026-10-05 (1).txt")


def parse_ieee():
    recs = []
    for f in sorted(SRC.glob("ieee_export*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            au = [a.strip() for a in r["Authors"].split(";") if a.strip()]
            recs.append({"source": "IEEE Xplore", "id": f"IEEE {r['Document Identifier'][:12]} {len(recs) + 1}",
                         "title": r["Document Title"], "abstract": r["Abstract"], "year": r["Publication Year"],
                         "journal": r["Publication Title"], "doi": r["DOI"].lower(),
                         "authors": ", ".join(au[:3]) + (" et al." if len(au) > 3 else ""), "pub_type": ""})
    return recs


def fill_missing(records):
    for r in records:
        if r["abstract"] or not r["doi"]:
            continue
        a = v1.openalex_abstract(r["doi"])
        if not a:
            try:
                j = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{r['doi']}",
                                 params={"fields": "abstract"}, timeout=30).json()
                a = j.get("abstract") or ""
            except Exception:
                a = ""
            time.sleep(1.2)
        r["abstract"] = a


def main():
    sources = {"PubMed": parse_pubmed(), "Scopus": parse_scopus(), "ProQuest": parse_proquest(), "IEEE Xplore": parse_ieee()}
    seen, records, dups = {}, [], []
    for name in ["PubMed", "Scopus", "ProQuest", "IEEE Xplore"]:
        for r in sources[name]:
            keys = [k for k in ("doi:" + r["doi"] if r["doi"] else "", "t:" + v1.norm_title(r["title"])) if k and k != "t:"]
            hit = next((seen[k] for k in keys if k in seen), None)
            if hit is not None:
                kept = records[hit]
                kept["also_in"] = ", ".join(filter(None, [kept.get("also_in", ""), r["source"]]))
                for f in ("abstract", "doi", "year", "journal"):
                    if not kept[f] and r[f]:
                        kept[f] = r[f]
                dups.append({**r, "duplicate_of": kept["id"]})
                continue
            for k in keys:
                seen[k] = len(records)
            records.append(r)
    fill_missing(records)

    old = json.loads(V1_JSON.read_text(encoding="utf-8"))
    kept_no = {r["id"]: r["no"] for r in old["records"]}
    v1map = {}
    for r in old["records"] + old["duplicates"]:
        no = r.get("no") or kept_no.get(r.get("duplicate_of"))
        if r["doi"]:
            v1map["doi:" + r["doi"]] = no
        v1map["t:" + v1.norm_title(r["title"])] = no
    for i, r in enumerate(records, 1):
        r["no"] = i
        r["v1_no"] = next((v1map[k] for k in ("doi:" + r["doi"], "t:" + v1.norm_title(r["title"])) if k in v1map and k != "doi:"), None)
    OUT.write_text(json.dumps({"counts": {k: len(v) for k, v in sources.items()}, "records": records, "duplicates": dups},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: len(v) for k, v in sources.items()}, "unique:", len(records), "dups:", len(dups),
          "already screened in v1:", sum(1 for r in records if r["v1_no"]),
          "new:", sum(1 for r in records if not r["v1_no"]),
          "no abstract:", sum(1 for r in records if not r["abstract"]))


if __name__ == "__main__":
    main()
