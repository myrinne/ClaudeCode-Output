"""Fetch legal open-access PDFs by DOI (Unpaywall); fall back to the FKUI library proxy.

Usage:
    python fetch_papers.py 10.1000/xyz 10.1016/abc          # DOIs as args
    python fetch_papers.py --file dois.txt --out pdfs
    python fetch_papers.py --file dois.txt --open-proxy     # open closed ones via proxy in browser

Config (env vars):
    UNPAYWALL_EMAIL   required by Unpaywall (your real email)
    FKUI_PROXY_PREFIX EZproxy-style login prefix, e.g. https://login.ezproxy.ui.ac.id/login?url=
                      (check the exact URL on the FKUI/UI library "remote access" page)
"""
import argparse
import os
import re
import sys
import webbrowser
from pathlib import Path
from urllib.parse import quote

import requests
from unpywall import Unpywall
from unpywall.utils import UnpywallCredentials


def clean_doi(s):
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", s.strip(), flags=re.I)


def download(url, dest):
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    if r.ok and r.content[:4] == b"%PDF":
        dest.write_bytes(r.content)
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dois", nargs="*")
    ap.add_argument("--file", help="text file, one DOI per line")
    ap.add_argument("--out", default="pdfs")
    ap.add_argument("--open-proxy", action="store_true",
                    help="open paywalled DOIs through the FKUI proxy in your browser")
    a = ap.parse_args()

    email = os.environ.get("UNPAYWALL_EMAIL")
    if not email:
        sys.exit("Set UNPAYWALL_EMAIL first, e.g. $env:UNPAYWALL_EMAIL='you@example.com'")
    UnpywallCredentials(email)
    proxy = os.environ.get("FKUI_PROXY_PREFIX", "")

    dois = [clean_doi(d) for d in a.dois]
    if a.file:
        dois += [clean_doi(l) for l in Path(a.file).read_text(encoding="utf-8").splitlines() if l.strip()]
    if not dois:
        sys.exit("No DOIs given.")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    closed = []
    for doi in dois:
        dest = out / (re.sub(r"[^\w.-]", "_", doi) + ".pdf")
        try:
            data = Unpywall.get_json(doi) or {}
        except Exception as e:
            data = {}
            print(f"[err ] {doi}: lookup failed ({e})")
        locs = data.get("oa_locations") or []
        pdfs = [l["url_for_pdf"] for l in locs if l.get("url_for_pdf")]
        pages = [l.get("url_for_landing_page") or l.get("url") for l in locs]
        if any(download(u, dest) for u in pdfs):
            print(f"[ OA ] {doi} -> {dest}")
        elif pages:
            print(f"[page] {doi}: OA, no direct PDF — open {pages[0]}")
        else:
            closed.append(doi)
            print(f"[shut] {doi}: no free version")

    if closed:
        print("\nPaywalled / not found — via FKUI proxy:")
        for doi in closed:
            url = f"{proxy}{quote('https://doi.org/' + doi, safe=':/')}" if proxy else f"https://doi.org/{doi}"
            print(f"  {url}")
            if a.open_proxy and proxy:
                webbrowser.open(url)
        if not proxy:
            print("(FKUI_PROXY_PREFIX not set, so these are plain DOI links)")


if __name__ == "__main__":
    main()
