"""
Screenshot Sorter — extract information from phone screenshots with Claude vision,
organize it into an Obsidian vault, and suggest keep/delete for each image.

Workflow (two passes, nothing is ever truly deleted):

    python screenshot_sorter.py extract --latest 50      # API pass -> manifest + review note
    python screenshot_sorter.py apply                     # writes vault notes, moves "delete" files
    python screenshot_sorter.py status                    # counts + cost so far

Review the generated "Screenshot Review.md" in Obsidian between the two passes and edit the
`action` column (keep / delete / review / skip). `apply` honours your edits.

All state lives in data/manifest.jsonl (one JSON record per screenshot, keyed by content hash),
so re-runs are incremental and never re-pay for an image already extracted.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"
DATA_DIR = HERE / "data"
MANIFEST_PATH = DATA_DIR / "manifest.jsonl"

SECTION_START = "<!-- screenshot-sorter:start -->"
SECTION_END = "<!-- screenshot-sorter:end -->"
FILENAME_RE = re.compile(r"Screenshot[ _](\d{4})-(\d{2})-(\d{2})[ _](\d{2})(\d{2})(\d{2})")
ACTIONS = ("keep", "delete", "review", "skip")


# --------------------------------------------------------------------------- config / manifest

def load_dotenv() -> None:
    """Load KEY=VALUE lines from a .env file next to the script (only for keys not already set)."""
    import os
    env_path = HERE / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def load_config() -> dict:
    load_dotenv()
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg["screenshot_dir"] = Path(cfg["screenshot_dir"])
    cfg["to_delete_dir"] = Path(cfg["to_delete_dir"])
    cfg["vault_dir"] = Path(cfg["vault_dir"])
    return cfg


def load_manifest() -> dict[str, dict]:
    records: dict[str, dict] = {}
    if MANIFEST_PATH.exists():
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                records[rec["id"]] = rec  # later lines win -> append-only updates
    return records


def save_manifest(records: dict[str, dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for rec in sorted(records.values(), key=lambda r: r["taken_at"]):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(MANIFEST_PATH)


# --------------------------------------------------------------------------- scanning

def taken_at_from(path: Path) -> datetime:
    m = FILENAME_RE.search(path.name)
    if m:
        y, mo, d, hh, mm, ss = (int(x) for x in m.groups())
        return datetime(y, mo, d, hh, mm, ss)
    return datetime.fromtimestamp(path.stat().st_mtime)


def scan_screenshots(cfg: dict) -> list[Path]:
    files = [p for p in cfg["screenshot_dir"].iterdir()
             if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    return sorted(files, key=taken_at_from)


def content_id(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def perceptual_hash(path: Path) -> str:
    import imagehash
    from PIL import Image
    with Image.open(path) as im:
        return str(imagehash.phash(im))


def hamming(a: str, b: str) -> int:
    import imagehash
    return imagehash.hex_to_hash(a) - imagehash.hex_to_hash(b)


def register_files(cfg: dict, records: dict[str, dict], files: list[Path]) -> list[dict]:
    """Add new files to the manifest (hash + dedupe). Returns the records for `files`, in order."""
    out = []
    seen_hashes = [(r["phash"], r["id"]) for r in records.values() if r.get("phash")]
    for path in files:
        cid = content_id(path)
        rec = records.get(cid)
        if rec is None:
            ph = perceptual_hash(path)
            rec = {
                "id": cid,
                "filename": path.name,
                "path": str(path),
                "taken_at": taken_at_from(path).isoformat(timespec="seconds"),
                "phash": ph,
                "dup_of": None,
                "status": "new",          # new -> extracted -> applied
                "action": None,           # final decision applied
                "extraction": None,
                "usage": None,
            }
            for other_ph, other_id in seen_hashes:
                if other_id != cid and hamming(ph, other_ph) <= cfg["phash_distance"]:
                    rec["dup_of"] = other_id
                    rec["status"] = "extracted"
                    rec["extraction"] = {"suggested_action": "delete",
                                         "action_reason": f"near-duplicate of {other_id}"}
                    break
            seen_hashes.append((ph, cid))
            records[cid] = rec
        elif rec["path"] != str(path):
            rec["path"] = str(path)  # file was moved/renamed; keep tracking it
        out.append(rec)
    return out


# --------------------------------------------------------------------------- extraction (Claude)

def build_schema():
    from pydantic import BaseModel, Field

    class Extraction(BaseModel):
        category: Literal["thesis", "board-exam", "occ-med", "env-health", "ai-tools",
                          "chat", "schedule", "reference", "personal", "sensitive"]
        title: str = Field(description="Short descriptive title, max 80 characters")
        summary: str = Field(description="1-3 sentences capturing what this screenshot is about")
        key_facts: list[str] = Field(description="Bullet-ready facts: names, numbers, dates, decisions, action items — verbatim where possible")
        full_text: str = Field(description="Faithful transcription of all readable text if the screenshot is text-heavy (article, slide, chat, document). Empty string if the text is trivial or the image is mostly visual.")
        source_app: str = Field(description="App or source visible, e.g. WhatsApp, Instagram, PowerPoint, Chrome, PDF, Gallery, Unknown")
        content_language: Literal["id", "en", "mixed", "none"]
        has_irreplaceable_visual: bool = Field(description="True if the image contains a chart, diagram, photo, table layout, or figure whose meaning cannot be fully captured by the text extraction")
        sensitive: bool = Field(description="True if the screenshot contains patient-identifiable data, medical record numbers (NRM), ID documents, bank/credit card details, or passwords")
        sensitive_reason: str
        suggested_action: Literal["keep", "delete", "review"]
        action_reason: str = Field(description="One sentence explaining the keep/delete/review suggestion")
        suggested_tags: list[str] = Field(description="Additional lowercase tags from the tag registry, e.g. source/article, source/regulation, type/literature")

    return Extraction


SYSTEM_PROMPT = """You are an information-extraction assistant for a physician (occupational medicine resident, PPDS Sp.Ok at FKUI/RSCM, Indonesia) who is triaging phone screenshots into an Obsidian knowledge vault.

For each screenshot, extract the information faithfully and classify it. Follow these rules:

CATEGORIES (choose exactly one):
- thesis: WBGT / heat stress, TEWL, H2O2, oxidative stress, mediation analysis, PROCESS macro, thesis statistics, hospital kitchen (Instalasi Gizi) study
- board-exam: occupational-medicine board exam material — slides, textbook pages, regulations (Permenaker/Permenkes/UU/PP), OSHA/NIOSH/ACGIH, PERDOKI consensus, exam schedules
- occ-med: clinical occupational medicine — MCU (medical check-up), fit-to-work (FTW), health risk assessment (HRA), return-to-work, occupational disease (PAK), ergonomics, JSA, workplace hazards
- env-health: environmental health — indoor air quality, PM2.5/PM10, ventilation/ACH, sick building syndrome, occupational radiology, noise, lighting
- ai-tools: Claude, ChatGPT, NotebookLM, Obsidian, Claude Code, prompts, AI workflows, software tips
- chat: WhatsApp/Telegram/LINE/email conversations, group announcements, meeting coordination
- schedule: timetables, agendas, event posters, webinar announcements, calendars, deadlines
- reference: articles, journal abstracts, social media posts (Instagram/X/LinkedIn), quotes, general knowledge, book pages that do not fit a domain above
- personal: receipts, orders, shopping, travel bookings, photos, memes, family, hobbies, misc
- sensitive: patient-identifiable data, medical record numbers (NRM), ID cards/passports, bank or card details, passwords. ONLY use this if the data is truly identifying — anonymised clinical teaching material is NOT sensitive.

LANGUAGE: write title, summary and key_facts in the same language as the screenshot's dominant text (Indonesian or English). If there is no text, use Indonesian. Tags are always English.

KEEP / DELETE RULE:
- delete: text-heavy content that your full_text + key_facts capture completely (articles, chats, slides with only text, announcements). The screenshot adds nothing beyond the extracted text.
- keep: charts, graphs, diagrams, photos, tables with complex layout, figures, anything where seeing the image matters, ID documents, anything sensitive.
- review: unsure, partially readable, cropped mid-content, or a screenshot that seems to be part of a multi-image sequence.

Be concise but complete. Never invent text that is not visible. Preserve numbers, units, names and dates exactly."""


def prepare_image(path: Path, max_edge: int) -> tuple[str, str]:
    """Downscale + JPEG-encode for the API. Returns (media_type, base64)."""
    from PIL import Image
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale = max_edge / max(w, h)
        if scale < 1:
            im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=85, optimize=True)
    return "image/jpeg", base64.standard_b64encode(buf.getvalue()).decode("ascii")


def extract_one(client, cfg: dict, rec: dict, schema) -> None:
    media_type, data = prepare_image(Path(rec["path"]), cfg["max_image_edge"])
    response = client.messages.parse(
        model=cfg["model"],
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": f"Screenshot filename: {rec['filename']} (taken {rec['taken_at']}). Extract and classify it."},
            ],
        }],
        output_format=schema,
    )
    parsed = response.parsed_output
    rec["extraction"] = parsed.model_dump()
    if parsed.sensitive:
        rec["extraction"]["category"] = "sensitive"
        rec["extraction"]["suggested_action"] = "keep"
    rec["usage"] = {"input": response.usage.input_tokens, "output": response.usage.output_tokens}
    rec["status"] = "extracted"
    rec["extracted_at"] = datetime.now().isoformat(timespec="seconds")


def cost_of(cfg: dict, records) -> float:
    p = cfg["price_per_mtok"]
    total = 0.0
    for r in records:
        u = r.get("usage")
        if u:
            total += u["input"] / 1e6 * p["input"] + u["output"] / 1e6 * p["output"]
    return total


# --------------------------------------------------------------------------- review note

def review_table_rows(cfg: dict, recs: list[dict]) -> str:
    lines = ["| ID | Taken | Category | Title | Source | Suggested | Reason | **Action** |",
             "|---|---|---|---|---|---|---|---|"]
    for r in recs:
        ex = r.get("extraction") or {}
        action = r.get("action") or ex.get("suggested_action", "review")
        cell = lambda s: str(s or "").replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{r['id']}` | {r['taken_at'][:16].replace('T', ' ')} | {cell(ex.get('category'))} "
            f"| {cell(ex.get('title'))} | {cell(ex.get('source_app'))} | {cell(ex.get('suggested_action'))} "
            f"| {cell(ex.get('action_reason'))} | {action} |")
    return "\n".join(lines)


def write_review_note(cfg: dict, recs: list[dict]) -> Path:
    path = cfg["vault_dir"] / cfg["review_note"]
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = [r for r in recs if r["status"] == "extracted"]
    parts = [
        "---", "tags:", "  - ai-generated", "  - screenshot-review",
        f"generated: {datetime.now().isoformat(timespec='minutes')}", "---",
        "# 📸 Screenshot Review",
        "",
        f"{len(pending)} screenshot(s) extracted and waiting for `apply`. Estimated API cost so far: "
        f"**${cost_of(cfg, recs):.3f}**.",
        "",
        "Edit the **Action** column (`keep` / `delete` / `review` / `skip`), then run "
        "`python screenshot_sorter.py apply`. `skip` leaves the file untouched and writes nothing.",
        "",
        review_table_rows(cfg, pending),
        "",
        "---",
        "## Details",
        "",
    ]
    for r in pending:
        ex = r.get("extraction") or {}
        img_uri = Path(r["path"]).as_uri()
        parts += [
            f"### `{r['id']}` — {ex.get('title', r['filename'])}",
            f"- **File:** {r['filename']} · **Taken:** {r['taken_at'].replace('T', ' ')} · "
            f"**Category:** {ex.get('category')} · **Source:** {ex.get('source_app')}",
            f"- **Suggested:** {ex.get('suggested_action')} — {ex.get('action_reason', '')}",
        ]
        if r.get("dup_of"):
            parts.append(f"- **Duplicate of:** `{r['dup_of']}`")
        if ex.get("sensitive"):
            parts.append(f"- ⚠️ **Sensitive:** {ex.get('sensitive_reason')} — details withheld, will be tagged #airestricted")
        elif ex.get("summary"):
            parts.append(f"- **Summary:** {ex['summary']}")
            if ex.get("key_facts"):
                parts.append("- **Key facts:**")
                parts += [f"    - {k}" for k in ex["key_facts"]]
        parts += [f"![]({img_uri})", ""]
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def read_review_overrides(cfg: dict) -> dict[str, str]:
    """Parse the Action column the user may have edited in the review note."""
    path = cfg["vault_dir"] / cfg["review_note"]
    overrides: dict[str, str] = {}
    if not path.exists():
        return overrides
    row_re = re.compile(r"^\|\s*`([0-9a-f]{12})`\s*\|.*\|\s*([a-zA-Z]+)\s*\|\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        m = row_re.match(line)
        if m and m.group(2).lower() in ACTIONS:
            overrides[m.group(1)] = m.group(2).lower()
    return overrides


# --------------------------------------------------------------------------- vault writing

def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r'[\\/:*?"<>|#^\[\]]+', " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len].rstrip(" .") or "untitled"


def is_airestricted(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open(encoding="utf-8", errors="ignore") as f:
        head = "".join(f.readline() for _ in range(30))
    return "airestricted" in head


def category_note_path(cfg: dict, rec: dict) -> Path:
    ex = rec["extraction"]
    cat = cfg["categories"].get(ex["category"], cfg["categories"]["reference"])
    stamp = rec["taken_at"].replace("T", " ").replace(":", "")[:17]  # "2026-09-18 113013"
    name = f"{stamp} {slugify(ex.get('title') or rec['filename'])}.md"
    return cfg["vault_dir"] / cfg["category_root"] / cat["folder"] / name


def write_category_note(cfg: dict, rec: dict, action: str) -> Path:
    ex = rec["extraction"]
    cat = cfg["categories"].get(ex["category"], cfg["categories"]["reference"])
    path = category_note_path(cfg, rec)
    path.parent.mkdir(parents=True, exist_ok=True)
    taken = datetime.fromisoformat(rec["taken_at"])
    tags = ["screenshot", "ai-generated", *cat["tags"]]
    if not ex.get("sensitive"):
        tags += [t.strip("#").lower() for t in ex.get("suggested_tags", []) if t.strip("#")]
    tags = list(dict.fromkeys(tags))

    fm = ["---", "tags:", *[f"  - {t}" for t in tags],
          f'date: "{taken:%Y-%m-%d}"', f'time: "{taken:%H:%M}"',
          f"category: {ex['category']}", f"source_app: \"{ex.get('source_app', '')}\"",
          f"screenshot_action: {action}", f"screenshot_id: {rec['id']}",
          f'original_file: "{rec["filename"]}"', "---"]
    body = [f"# {ex.get('title') or rec['filename']}", ""]
    if ex.get("sensitive"):
        body += ["> [!warning] Sensitive screenshot", f"> {ex.get('sensitive_reason', '')}",
                 "> Content intentionally not transcribed. Image kept in attachments.", ""]
    else:
        body += [ex.get("summary", ""), ""]
        if ex.get("key_facts"):
            body += ["## Key Facts", *[f"- {k}" for k in ex["key_facts"]], ""]
        if ex.get("full_text"):
            body += ["## Full Text", "", "```text", ex["full_text"].strip(), "```", ""]
    if action == "keep":
        body += ["## Image", f"![[{cfg['attachments_dir']}/{rec['filename']}]]", ""]
    body += ["---", f"Screenshot taken {taken:%Y-%m-%d %H:%M} · daily note: [[{taken:%Y-%m-%d}]] "
             f"· original: `{rec['filename']}`"]
    path.write_text("\n".join(fm + body), encoding="utf-8")
    return path


def ensure_daily_note(cfg: dict, day: datetime) -> Path | None:
    path = cfg["vault_dir"] / cfg["daily_notes_dir"] / f"{day:%Y-%m-%d}.md"
    if path.exists():
        return None if is_airestricted(path) else path
    template = cfg["vault_dir"] / cfg["daily_template"]
    text = template.read_text(encoding="utf-8") if template.exists() else f"# 📅 {day:%Y-%m-%d}\n"
    text = (text.replace("{{date:YYYY-MM-DD}}", f"{day:%Y-%m-%d}")
                .replace("{{date:dddd}}", f"{day:%A}"))
    path.write_text(text, encoding="utf-8")
    return path


def update_daily_note(cfg: dict, day: datetime, entries: list[tuple[dict, Path, str]]) -> Path | None:
    """Regenerate the marker-bounded screenshots section for one day."""
    path = ensure_daily_note(cfg, day)
    if path is None:
        return None
    lines = [SECTION_START, "## 📸 Screenshots", "*(auto-generated by screenshot_sorter — edit above/below the markers)*"]
    for rec, note_path, action in sorted(entries, key=lambda e: e[0]["taken_at"]):
        ex = rec["extraction"]
        t = rec["taken_at"][11:16]
        link = f"[[{note_path.stem}]]"
        icon = {"keep": "🖼️", "delete": "🗑️", "review": "❓"}.get(action, "")
        if ex.get("sensitive"):
            lines.append(f"- {t} {icon} {link} — *sensitive, details withheld* (#{ex['category']})")
        else:
            lines.append(f"- {t} {icon} {link} — {ex.get('summary', '').strip()} *(#{ex['category']}, {ex.get('source_app', '')})*")
    lines.append(SECTION_END)
    section = "\n".join(lines)

    text = path.read_text(encoding="utf-8")
    if SECTION_START in text and SECTION_END in text:
        pre, rest = text.split(SECTION_START, 1)
        _, post = rest.split(SECTION_END, 1)
        text = pre + section + post
    else:
        text = text.rstrip("\n") + "\n\n" + section + "\n"
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------- commands

def select_records(cfg: dict, records: dict[str, dict], args) -> list[dict]:
    files = scan_screenshots(cfg)
    if args.since:
        files = [f for f in files if taken_at_from(f) >= datetime.fromisoformat(args.since)]
    if args.latest:
        files = files[-args.latest:]
    return register_files(cfg, records, files)


def cmd_extract(cfg: dict, args) -> None:
    import anthropic
    records = load_manifest()
    recs = select_records(cfg, records, args)
    save_manifest(records)
    todo = [r for r in recs if r["status"] == "new" or (args.force and r["status"] != "applied")]
    dups = sum(1 for r in recs if r.get("dup_of"))
    print(f"Selected {len(recs)} screenshot(s): {len(todo)} to extract, {dups} duplicate(s) auto-flagged, "
          f"{len(recs) - len(todo) - dups} already done.")
    if args.limit:
        todo = todo[:args.limit]

    client = anthropic.Anthropic()
    schema = build_schema()
    spent = cost_of(cfg, recs)
    for i, rec in enumerate(todo, 1):
        if args.max_cost and spent >= args.max_cost:
            print(f"Stopping: cost cap ${args.max_cost:.2f} reached.")
            break
        try:
            extract_one(client, cfg, rec, schema)
        except anthropic.RateLimitError as e:
            print(f"  rate limited on {rec['filename']}: {e}. Stopping; re-run to continue.")
            break
        except anthropic.APIStatusError as e:
            print(f"  API error on {rec['filename']}: {e.status_code} {e.message}")
            rec["status"] = "error"
            rec["error"] = str(e)
            continue
        except anthropic.APIConnectionError as e:
            print(f"  connection error: {e}. Stopping; re-run to continue.")
            break
        spent = cost_of(cfg, recs)
        ex = rec["extraction"]
        print(f"[{i}/{len(todo)}] {rec['filename']} -> {ex['category']:10} {ex['suggested_action']:6} "
              f"{ex['title'][:50]!r}  (${spent:.3f} total)")
        save_manifest(records)  # checkpoint after every image

    review = write_review_note(cfg, [r for r in records.values() if r["status"] == "extracted"])
    print(f"\nReview note written: {review}")
    print(f"Total API cost so far: ${cost_of(cfg, records.values()):.3f}")


def cmd_apply(cfg: dict, args) -> None:
    records = load_manifest()
    overrides = read_review_overrides(cfg)
    pending = [r for r in records.values() if r["status"] == "extracted"]
    if args.latest or args.since:
        selected_ids = {r["id"] for r in select_records(cfg, records, args)}
        pending = [r for r in pending if r["id"] in selected_ids]
    if not pending:
        print("Nothing to apply.")
        return

    cfg["to_delete_dir"].mkdir(parents=True, exist_ok=True)
    attach_dir = cfg["vault_dir"] / cfg["attachments_dir"]
    by_day: dict[str, list[tuple[dict, Path, str]]] = {}
    counts = {a: 0 for a in ACTIONS}

    for rec in pending:
        ex = rec["extraction"]
        action = overrides.get(rec["id"]) or ex.get("suggested_action", "review")
        if ex.get("sensitive"):
            action = "keep" if action == "delete" else action
        if action == "skip":
            counts["skip"] += 1
            continue
        src = Path(rec["path"])
        if not src.exists():
            print(f"  missing file, skipping: {src}")
            continue
        if rec.get("dup_of") and not ex.get("title"):
            # duplicate: no note, just move it aside and link the original
            if not args.dry_run:
                shutil.move(str(src), str(cfg["to_delete_dir"] / src.name))
                rec.update(status="applied", action="delete", applied_at=datetime.now().isoformat(timespec="seconds"))
            counts["delete"] += 1
            print(f"  duplicate -> _to-delete: {src.name}")
            continue

        if args.dry_run:
            print(f"  [dry-run] {action:6} {src.name} -> {category_note_path(cfg, rec).relative_to(cfg['vault_dir'])}")
            counts[action] += 1
            continue

        if action == "keep":
            attach_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, attach_dir / src.name)
        note = write_category_note(cfg, rec, action)
        if action == "delete":
            shutil.move(str(src), str(cfg["to_delete_dir"] / src.name))
            rec["path"] = str(cfg["to_delete_dir"] / src.name)
        by_day.setdefault(rec["taken_at"][:10], []).append((rec, note, action))
        rec.update(status="applied", action=action, note=str(note.relative_to(cfg["vault_dir"])),
                   applied_at=datetime.now().isoformat(timespec="seconds"))
        counts[action] += 1
        print(f"  {action:6} {src.name} -> {note.relative_to(cfg['vault_dir'])}")

    if not args.dry_run:
        for day, entries in by_day.items():
            # include earlier applied entries of the same day so the section stays complete
            all_entries = [(r, cfg["vault_dir"] / r["note"], r["action"]) for r in records.values()
                           if r["status"] == "applied" and r.get("note") and r["taken_at"][:10] == day]
            result = update_daily_note(cfg, datetime.fromisoformat(day), all_entries or entries)
            print(f"  daily note {'updated' if result else 'SKIPPED (#airestricted)'}: {day}")
        save_manifest(records)
        write_review_note(cfg, [r for r in records.values() if r["status"] == "extracted"])
    print(f"\nApplied: {counts}")


def cmd_status(cfg: dict, args) -> None:
    records = load_manifest()
    files = scan_screenshots(cfg)
    by_status: dict[str, int] = {}
    for r in records.values():
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    print(f"Screenshots in folder : {len(files)}")
    print(f"Tracked in manifest   : {len(records)}  {by_status}")
    print(f"Duplicates flagged    : {sum(1 for r in records.values() if r.get('dup_of'))}")
    print(f"API cost so far       : ${cost_of(cfg, records.values()):.3f}")
    applied = [r for r in records.values() if r["status"] == "applied"]
    if applied:
        acts: dict[str, int] = {}
        for r in applied:
            acts[r["action"]] = acts.get(r["action"], 0) + 1
        print(f"Applied actions       : {acts}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def selection(p):
        p.add_argument("--latest", type=int, help="only the N most recent screenshots")
        p.add_argument("--since", help="only screenshots taken on/after this date (YYYY-MM-DD)")

    p = sub.add_parser("extract", help="run Claude vision on new screenshots, write review note")
    selection(p)
    p.add_argument("--limit", type=int, help="max number of API calls this run")
    p.add_argument("--max-cost", type=float, help="stop when cumulative cost (USD) reaches this")
    p.add_argument("--force", action="store_true", help="re-extract already-extracted (not applied) items")

    p = sub.add_parser("apply", help="write vault notes and move files according to decisions")
    selection(p)
    p.add_argument("--dry-run", action="store_true", help="show what would happen, write nothing")

    sub.add_parser("status", help="show manifest counts and cost")

    args = ap.parse_args()
    cfg = load_config()
    {"extract": cmd_extract, "apply": cmd_apply, "status": cmd_status}[args.cmd](cfg, args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
