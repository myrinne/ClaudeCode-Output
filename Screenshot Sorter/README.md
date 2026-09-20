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

## What `apply` writes

| Action | Category note in `3. RESOURCES/Screenshots/<Category>/` | Image | Original file |
|---|---|---|---|
| `keep` | yes, with embedded image | copied to `99. ATTACHMENTS/Screenshots/` | left in place |
| `delete` | yes (text extracted) | — | **moved** to `Screenshots 1_to-delete/` (never deleted) |
| `review` | yes | — | left in place |
| `skip` | nothing | — | untouched |

Every day that has processed screenshots gets a `## 📸 Screenshots` section in its daily note
(`0. INBOX (Daily Notes)/YYYY-MM-DD.md`, created from the daily template if missing), bounded by
`<!-- screenshot-sorter:start/end -->` markers and regenerated on each apply. Text outside the
markers is never touched. Daily notes tagged `#airestricted` are skipped.

Near-duplicate screenshots (perceptual hash distance ≤ 4) are flagged `delete` without an API call.

Screenshots the model flags as **sensitive** (patient data, NRM, ID documents, bank details) get a
minimal note tagged `#airestricted` with no transcription, and are forced to `keep`. Note that the
image itself has already been sent to the API at that point — the pre-check is model-based, not local.

## State

`data/manifest.jsonl` — one record per screenshot (content hash, phash, extraction, usage, action).
Gitignored because it contains extracted personal text. Delete it to start over.
