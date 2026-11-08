# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal Claude Code workspace and configuration repository. It stores custom slash commands, Claude settings, and project outputs. All work is version-controlled and pushed to GitHub after each meaningful change.

## Session Start: Identity from the Vault

Context about the owner lives in `C:\Users\vidya\OneDrive\Documents\ClaudeCode Vault`, not in this repo. At the start of every session:

1. Read `ClaudeCode Vault/00_AGENT_README.md`, then `Identity/User.md`, `Identity/soul.md`, `Identity/identity.md`.
2. Use `Projects/`, `People/`, `Areas/`, `Knowledge/` there when a task touches them.
3. **Hats** (`identity.md`): when she says "switch ke <hat>" / "pakai hat <x>", apply that hat's scope, standards, and checks. If no hat is named, ask. Every hat asks for the output format before generating.

**Outputs always go to this repo (`ClaudeCode Output`)**, never into the vault, unless she explicitly asks for a vault note.

## Git Workflow

Commit and push to GitHub **throughout the session** — after every meaningful unit of work (a new file, a config change, a completed feature). Do not batch everything into one commit at the end. This ensures work is never lost and the history is easy to navigate.

```powershell
git add <specific-files>
git commit -m "Short imperative message describing the change"
git push
```

Commit message rules:
- Imperative mood, present tense: "Add X", "Fix Y", "Update Z"
- One line, concise — describe what changed and why if non-obvious
- Never use vague messages like "updates" or "misc changes"

Remote: `origin` → `https://github.com/myrinne/ClaudeCode-Output.git` (branch: `master`)

## Custom Slash Commands

Defined in `.claude/commands/`:

- `/notebooklm` — Interact with Google NotebookLM (create notebooks, add URL sources, generate artifacts). Requires the `notebooklm` CLI (`notebooklm-py`, installed as a uv tool in `~\.local\bin`, already on PATH). If it says "Not logged in", ask her to run `! notebooklm login`.
- `/research-search` — Search PubMed and Consensus in parallel for peer-reviewed articles, deduplicated and ranked by recency.

## Integrations

**Obsidian MCP** (user-scoped, global): reads the active vault at `C:\Users\vidya\OneDrive\Documents\ClaudeCode Vault` (read its `00_AGENT_README.md` first). The old vault `Obsidian-Vidya` is a read-only backup since 2026-10-01 — do not write to it. Requires Obsidian to be open with the Local REST API community plugin running. Server `obsidian` is the plugin's built-in MCP at `https://127.0.0.1:27124/mcp` (Bearer key stored in `~/.claude.json`); its self-signed cert is trusted through the user env var `NODE_EXTRA_CA_CERTS=C:\Users\vidya\.claude\obsidian-local-rest-api.crt` (cert expires 2027-06-14; re-download from `https://127.0.0.1:27124/obsidian-local-rest-api.crt` if the plugin regenerates it).

**Python**: 3.14 at `C:\Python314` (default `python`/`py`) and `C:\Users\vidya\AppData\Local\Python\pythoncore-3.14-64\`. Standalone CLIs are installed with `uv tool install` into `~\.local\bin` (on PATH). Full inventory: vault `Knowledge/Lainnya/claude-code-setup-inventory.md`.

## Permissions

Pre-approved in `.claude/settings.json` (no prompts needed):
- `Bash(git *)` 
- `Bash(gh *)`
