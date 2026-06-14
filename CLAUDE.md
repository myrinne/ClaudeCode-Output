# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal Claude Code workspace and configuration repository. It stores custom slash commands, Claude settings, and project outputs. All work is version-controlled and pushed to GitHub after each meaningful change.

## Git Workflow

Always commit and push after completing any meaningful task:

```powershell
git add <specific-files>
git commit -m "Short imperative message describing the change"
git push
```

Remote: `origin` → `https://github.com/myrinne/ClaudeCode-Output.git` (branch: `master`)

## Custom Slash Commands

Defined in `.claude/commands/`:

- `/notebooklm` — Interact with Google NotebookLM (create notebooks, add URL sources, generate artifacts). Requires the `notebooklm` CLI; prepend `$env:PATH += ";C:\Users\LENOVO\AppData\Local\Python\pythoncore-3.14-64\Scripts"` before running any `notebooklm` command.
- `/research-search` — Search PubMed and Consensus in parallel for peer-reviewed articles, deduplicated and ranked by recency.

## Integrations

**Obsidian MCP** (user-scoped, global): reads the vault at `C:\Users\LENOVO\OneDrive\Documents\Obsidian-Vidya`. Requires Obsidian to be open with the Local REST API community plugin running. Configured via `claude mcp` with `OBSIDIAN_API_KEY`.

**Python**: available at `C:\Users\LENOVO\AppData\Local\Python\pythoncore-3.14-64\`. Scripts (pip-installed CLIs) live in the `Scripts\` subdirectory of that path — add it to PATH when running Python tools from shell.

## Permissions

Pre-approved in `.claude/settings.json` (no prompts needed):
- `Bash(git *)` 
- `Bash(gh *)`
