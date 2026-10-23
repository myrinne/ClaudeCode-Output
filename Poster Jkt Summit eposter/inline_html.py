"""Make a self-contained copy of a poster HTML (images embedded as data URIs) so it opens anywhere.
Usage: python inline_html.py poster_alt3.html OUT.html
"""
import base64
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
src, out = Path(sys.argv[1]), Path(sys.argv[2])
html = (HERE / src).read_text(encoding="utf-8")


def data_uri(rel):
    p = HERE / rel
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


html = re.sub(r'(src=")(assets/[^"]+)(")', lambda m: m.group(1) + data_uri(m.group(2)) + m.group(3), html)
html = re.sub(r'(url\(")(assets/[^"]+)("\))', lambda m: m.group(1) + data_uri(m.group(2)) + m.group(3), html)
assert "assets/" not in html, "unresolved asset reference"
out.write_text(html, encoding="utf-8")
print(out, round(out.stat().st_size / 1e6, 1), "MB")
