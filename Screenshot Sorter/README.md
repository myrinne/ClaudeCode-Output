# Screenshot Sorter

Reads phone screenshots with Claude vision (Haiku 4.5), extracts the information, organizes it
into the Obsidian vault, and suggests whether each screenshot can be deleted.

## Setup (once)

```powershell
python -m pip install anthropic pillow imagehash
```

Put the API key in `Screenshot Sorter\.env` (gitignored):

```
ANTHROPIC_API_KEY=sk-ant-...
```

Paths, model, and the category taxonomy are in `config.json`.

## Workflow

```powershell
cd "Screenshot Sorter"

# 1. Extract — sends new screenshots to Claude, writes the manifest + review note
python screenshot_sorter.py extract --latest 50          # sample: 50 most recent
python screenshot_sorter.py extract --since 2026-09-01   # or by date
python screenshot_sorter.py extract --max-cost 5         # or everything, capped at $5

# 2. Review — open in Obsidian:
#    88. AI AGENTS WORKPLACE/03. Active Processing (WIP)/Screenshot Review.md
#    Edit the **Action** column: keep / delete / review / skip

# 3. Apply — writes notes, copies kept images, moves "delete" files aside
python screenshot_sorter.py apply --dry-run               # preview
python screenshot_sorter.py apply

python screenshot_sorter.py status
```

## Zero-cost mode (inside a Claude Code session)

Instead of the API, Claude Code can look at the images itself (billed to the subscription):

```powershell
python screenshot_sorter.py prepare-manual --latest 50    # writes data/manual_queue.json
# ... Claude reads each image and writes data/manual_batchN.json (list of Extraction objects + "id")
python screenshot_sorter.py import-manual data/manual_batch*.json
```

Then review + apply exactly as above.

## What `apply` writes

One note **per category** in `3. RESOURCES/Screenshots/` (`Okupasi Klinis.md`, `Board Exam.md`,
`Administrasi & Organisasi.md`, …). Each screenshot becomes a `## <date> · <title>` section with
summary, key facts, a foldable full-text quote, and the embedded image when kept. Sections carry an
`<!-- screenshot:<id> -->` marker so re-applying replaces rather than duplicates them; anything you
write outside those sections is preserved.

| Action | Section in category note | Image | Original file |
|---|---|---|---|
| `keep` | yes, with embedded image | copied to `99. ATTACHMENTS/Screenshots/` | left in place |
| `delete` | yes (text extracted) | — | **moved** to `Screenshots 1_to-delete/` (never deleted) |
| `review` | yes | — | left in place |
| `skip` | nothing | — | untouched |

Daily notes are not written (`"write_daily_notes": false` in `config.json` — flip it to also get a
`## 📸 Screenshots` section per day in `0. INBOX (Daily Notes)/`).

Near-duplicate screenshots (perceptual hash distance ≤ 4) are flagged `delete` without an API call.
Different *crops* of the same content are not caught by the hash — the extractor's `action_reason`
notes them instead.

Screenshots flagged **sensitive** (patient data, NRM, ID documents, bank details) get a minimal
section in `Sensitive.md` (tagged `#airestricted`) with no transcription. Their suggested action is
forced to `keep`, but an explicit edit in the review note overrides that. In API mode the image has
already been sent to Claude at that point — the pre-check is model-based, not local.

## State

`data/manifest.jsonl` — one record per screenshot (content hash, phash, extraction, usage, action).
Gitignored because it contains extracted personal text. Delete it to start over.
