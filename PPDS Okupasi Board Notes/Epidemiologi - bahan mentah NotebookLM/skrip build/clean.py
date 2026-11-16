"""Clean a raw `notebooklm ask` answer (raw/Qnn.txt) into short/<name>.md.
Usage: python clean.py raw.txt out.md
 - drops CLI header/footer, the trailing per-answer source list and the emoji follow-up offer
 - unwraps the 80-column hard wrapping (paragraphs, bullets, table rows, display math)
 - removes citation markers like [1, 2], [8-10]
 - converts \\( \\) -> $ $ and \\[ \\] -> $$ $$ (Obsidian); build_epi.py converts back for docx
 - a source-list line mentioning 'pengetahuan umum' is kept as a '!SUMBER' callout"""
import re, sys

raw = open(sys.argv[1], encoding="utf-8").read().replace("\r", "")
lines = raw.split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("Answer:"))
lines = lines[start + 1:]
lines = [l for l in lines if not l.startswith(("Resumed conversation", "Continuing conversation", "Started new conversation", "New conversation"))]

# cut off the source block: first heading/bold line containing 'Sumber' near the end
cut = None
for i, l in enumerate(lines):
    if re.match(r"^\s*(#{1,4}\s*)?\**\s*(\d+\.\s*)?(Sumber|Daftar Sumber|Referensi)\b.*", l, re.I) and i > len(lines) * 0.5:
        cut = i
        break
src_block = []
if cut is not None:
    src_block = lines[cut:]
    lines = lines[:cut]
# also drop trailing emoji follow-up offer and trailing hr
while lines and (not lines[-1].strip() or lines[-1].strip() == "---" or re.match(r"^\W*(📊|💡|📌|🔍|✅|📝)", lines[-1])):
    lines.pop()

general = [l.strip() for l in src_block if re.search(r"pengetahuan umum|general knowledge", l, re.I)]

# join wrapped lines
MARK = re.compile(r"^\s*(#{1,6}\s|[*\-+]\s|\d+[.)]\s|>|\||---|\\\[|\\\\\[|```|\$\$)")
out, i, n = [], 0, len(lines)
in_math = False
in_code = False
while i < n:
    l = lines[i].rstrip()
    if l.strip().startswith("```"):
        in_code = not in_code
        out.append(l); i += 1; continue
    if in_code:
        out.append(l); i += 1; continue
    # table row: join until it ends with '|'
    if l.lstrip().startswith("|"):
        row = l
        while not row.rstrip().endswith("|") and i + 1 < n:
            i += 1
            row = row.rstrip() + " " + lines[i].strip()
        out.append(row.strip()); i += 1; continue
    # display math starting at line: join until closing
    if re.match(r"^\s*(\\\\\[|\\\[)", l):
        blk = l.strip()
        while not re.search(r"(\\\\\]|\\\])\s*$", blk) and i + 1 < n:
            i += 1
            blk += " " + lines[i].strip()
        out.append(blk); i += 1; continue
    if not l.strip():
        out.append(""); i += 1; continue
    # paragraph / bullet: absorb continuation lines
    cur = l
    while i + 1 < n and not l.lstrip().startswith("#"):
        nxt = lines[i + 1]
        if not nxt.strip() or MARK.match(nxt) or (nxt.startswith("   ") and MARK.match(nxt.strip())):
            break
        i += 1
        cur = cur.rstrip() + " " + nxt.strip()
    out.append(cur); i += 1

text = "\n".join(out)
# empty inline math left by the CLI, e.g. \(\)
text = re.sub(r"\s*\\{1,2}\(\s*\\{1,2}\)", "", text)
# citations
text = re.sub(r"\s*\[\s*\d+(?:\s*[,\-–]\s*\d+)*\s*\]", "", text)
text = re.sub(r"\s*\\quad\s*(?=\\\\?[\]\)]|\$)", "", text)
# math -> $
text = re.sub(r"\\\\?\[(.+?)\\\\?\]", lambda m: "\n\n$$" + m.group(1).strip() + "$$\n\n", text, flags=re.S)
text = re.sub(r"\\\\?\((.+?)\\\\?\)", lambda m: "$" + m.group(1).strip() + "$", text, flags=re.S)
text = re.sub(r"\n{3,}", "\n\n", text)
text = re.sub(r"[ \t]+\n", "\n", text)
# demote headings: '### 1.' -> '### ' stays; '## ' -> '### ' so section heading is H2 in vault
text = re.sub(r"(?m)^#{1,2}\s", "### ", text)
text = text.strip() + "\n"
for g in general:
    text += "\n!SUMBER " + re.sub(r"^[*\-\d.\s]+", "", re.sub(r"\[\s*\d+(?:\s*[,\-–]\s*\d+)*\s*\]", "", g)) + "\n"
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(text)
print("ok", sys.argv[2], len(text))
