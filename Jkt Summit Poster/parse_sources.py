"""Parse the four database exports (PubMed, Scopus, ProQuest, IEEE) into one
deduplicated record list with abstracts, saved as records.json.

PubMed export is citation-only -> abstracts fetched via NCBI E-utilities.
IEEE export has no abstracts -> fetched from OpenAlex by DOI.
Scopus came as an emailed document list (.msg) because RIS download failed.
"""
import html
import json
import re
import time
from pathlib import Path

import extract_msg
import requests

SRC = Path(r"C:\Users\vidya\OneDrive\Documents\PPDS Okupasi\Jkt Summit")
OUT = Path(__file__).parent / "records.json"


def clean(s):
    s = re.sub(r"<!--.*?-->", "", s or "", flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


# ---------- PubMed ----------
def parse_pubmed(path=None):
    txt = Path(path or SRC / "Pubmed search.txt").read_text(encoding="utf-8")
    pmids = re.findall(r"PMID:\s*(\d+)", txt)
    recs = []
    for i in range(0, len(pmids), 100):
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db": "pubmed", "id": ",".join(pmids[i:i + 100]), "retmode": "xml"},
            timeout=60,
        )
        for art in re.findall(r"<Pubmed(?:Book)?Article>.*?</Pubmed(?:Book)?Article>", r.text, re.S):
            pmid = re.search(r'<PMID[^>]*>(\d+)', art).group(1)
            title = clean(re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", art, re.S).group(1))
            parts = re.findall(r"<AbstractText([^>]*)>(.*?)</AbstractText>", art, re.S)
            abstract = " ".join(
                (f"{m.group(1)}: " if (m := re.search(r'Label="([^"]+)"', a)) else "") + clean(b)
                for a, b in parts
            )
            year = re.search(r"<PubDate>.*?<Year>(\d{4})", art, re.S) or re.search(r"<Year>(\d{4})", art)
            journal = re.search(r"<Title>(.*?)</Title>", art, re.S) or re.search(r"<BookTitle[^>]*>(.*?)</BookTitle>", art, re.S)
            doi = re.search(r'<ArticleId IdType="doi">(.*?)</ArticleId>', art)
            authors = re.findall(r"<LastName>(.*?)</LastName>", art)
            ptypes = re.findall(r"<PublicationType[^>]*>(.*?)</PublicationType>", art)
            recs.append({
                "source": "PubMed", "id": f"PMID {pmid}", "title": title, "abstract": abstract,
                "year": year.group(1) if year else "", "journal": clean(journal.group(1)) if journal else "",
                "doi": doi.group(1).lower() if doi else "",
                "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
                "pub_type": "; ".join(ptypes),
            })
        time.sleep(0.4)
    order = {f"PMID {p}": i for i, p in enumerate(pmids)}
    return sorted(recs, key=lambda r: order.get(r["id"], 9999))


# ---------- Scopus (.msg email) ----------
def parse_scopus():
    h = extract_msg.Message(str(SRC / "Results From Scopus.msg")).htmlBody.decode("utf-8", "replace")
    blocks = re.split(r'<td data-id="__react-email-column"[^>]*><p[^>]*>&nbsp;</p><p[^>]*>(\d+)</p></td>', h)
    recs = []
    for k in range(1, len(blocks), 2):
        num, b = blocks[k], blocks[k + 1]
        authors = re.findall(r"<li[^>]*><p[^>]*>(.*?)<sup>", b, re.S)
        authors = [clean(a).split(",")[0].strip() for a in authors]
        title = re.search(r"<a [^>]*>(.*?)</a>", b, re.S)
        after = b[title.end():] if title else b
        ps = [clean(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", after, re.S)]
        ps = [p for p in ps if p]
        journal, abstract = "", ""
        if "Abstract" in ps:
            j = ps.index("Abstract")
            journal = ps[j - 1] if j else ""
            abstract = " ".join(ps[j + 1:])
        else:
            journal = ps[-1] if ps else ""
        year = re.search(r"©\s*(?:The Author\(s\)\s*)?(\d{4})", abstract) or re.search(r"(\d{4})\.?\s*$", abstract)
        recs.append({
            "source": "Scopus", "id": f"Scopus #{num}", "title": clean(title.group(1)) if title else "",
            "abstract": abstract, "year": year.group(1) if year else "", "journal": journal, "doi": "",
            "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""), "pub_type": "",
        })
    return recs


# ---------- ProQuest ----------
def parse_proquest(path=None):
    txt = Path(path or SRC / "ProQuestDocuments-2026-09-16.txt").read_text(encoding="utf-8")
    recs = []
    for n, chunk in enumerate(re.split(r"(?m)^_{20,}$", txt), 1):
        lines = [l for l in chunk.strip().splitlines() if l.strip()]
        if not any(l.startswith("https://www.proquest.com") for l in lines):
            continue
        title = lines[0].strip()
        get = lambda key: next((l.split(":", 1)[1].strip() for l in lines if l.startswith(key + ":")), "")
        abstract = re.sub(r"^English:\s*", "", get("Abstract"))
        abstract = re.split(r"\s(?:German|French|Spanish):\s*$", abstract)[0]
        url = next((l.strip() for l in lines if l.startswith("https://www.proquest.com")), "")
        doi = get("DOI")
        year = get("Publication year") or (re.search(r"\b(19|20)\d{2}\b", get("Publication info")) or [""])[0]
        recs.append({
            "source": "ProQuest", "id": "ProQuest " + (re.search(r"docview/(\d+)", url).group(1) if "docview" in url else str(n)),
            "title": title, "abstract": abstract, "year": str(year), "journal": get("Publication title"),
            "doi": doi.lower(), "authors": get("Author").split(";")[0][:60], "pub_type": get("Document type"),
        })
    return recs


# ---------- IEEE ----------
def openalex_abstract(doi):
    try:
        r = requests.get(f"https://api.openalex.org/works/doi:{doi}", params={"mailto": "research@example.org"}, timeout=30)
        inv = r.json().get("abstract_inverted_index") if r.ok else None
    except Exception:
        return ""
    if not inv:
        return ""
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)


def parse_ieee():
    f = next(SRC.glob("IEEE Xplore*.txt"))
    txt = f.read_text(encoding="utf-8")
    recs = []
    for n, entry in enumerate(re.split(r"\n\s*\n", txt.strip()), 1):
        m = re.match(r'(.*?),\s*"(.*?),?"\s*(?:in\s+)?(.*?),\s.*?(\b(?:19|20)\d{2}\b)', entry, re.S)
        doi = re.search(r"doi:\s*(\S+?)[\.,]?\s", entry + " ")
        if not m:
            continue
        doi = doi.group(1).lower() if doi else ""
        recs.append({
            "source": "IEEE Xplore", "id": f"IEEE #{n}", "title": clean(m.group(2)).rstrip(","),
            "abstract": openalex_abstract(doi) if doi else "", "year": m.group(4),
            "journal": clean(m.group(3)), "doi": doi, "authors": clean(m.group(1))[:60], "pub_type": "",
        })
        time.sleep(0.15)
    return recs


def main():
    sources = {"PubMed": parse_pubmed(), "Scopus": parse_scopus(), "ProQuest": parse_proquest(), "IEEE Xplore": parse_ieee()}
    seen, records, dups = {}, [], []
    for name in ["PubMed", "Scopus", "ProQuest", "IEEE Xplore"]:
        for r in sources[name]:
            keys = [k for k in ("doi:" + r["doi"] if r["doi"] else "", "t:" + norm_title(r["title"])) if k and k != "t:"]
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
    for i, r in enumerate(records, 1):
        r["no"] = i
    OUT.write_text(json.dumps({"counts": {k: len(v) for k, v in sources.items()},
                               "records": records, "duplicates": dups}, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: len(v) for k, v in sources.items()}, "unique:", len(records), "dups:", len(dups),
          "no abstract:", sum(1 for r in records if not r["abstract"]))


if __name__ == "__main__":
    main()
