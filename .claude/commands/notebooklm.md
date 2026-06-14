Interact with Google NotebookLM via the `notebooklm` CLI. You can create notebooks, add URL sources, and generate artifacts (infographic, flashcards, summary, data table, slide deck).

Before any command, ensure the PATH includes the Scripts dir:
`$env:PATH += ";C:\Users\LENOVO\AppData\Local\Python\pythoncore-3.14-64\Scripts"`

---

## Argument parsing

Parse `$ARGUMENTS` for intent. Examples:
- "create notebook Research on AI" → create notebook
- "add https://example.com to My Notebook" → add URL source
- "generate flashcards for My Notebook" → generate artifact
- "generate summary" → generate summary for current notebook
- "list notebooks" → list all notebooks
- "list artifacts" → list artifacts for current notebook

If the intent is ambiguous, ask the user to clarify before proceeding.

---

## Operations

### 1. List notebooks
```powershell
notebooklm list
```
Show the user their notebooks (ID and title). Suggest using a notebook with `notebooklm use <id>`.

### 2. Create a notebook
```powershell
notebooklm create "<notebook title>"
```
After creation, run `notebooklm list` to confirm it exists and show its ID.
Then automatically set it as the active notebook:
```powershell
notebooklm use <id>
```

### 3. Add URL source(s) to a notebook
If a specific notebook is mentioned, set it active first:
```powershell
notebooklm use <partial-id-or-name>
```
Then add each URL:
```powershell
notebooklm source add "<url>"
```
If multiple URLs are provided, add them one by one. After adding, run:
```powershell
notebooklm source list
```
to confirm the sources were added.

### 4. Generate an artifact

First ensure the correct notebook is active (`notebooklm use <id>`), then run the matching generate command:

| User asks for       | Command                            |
|---------------------|------------------------------------|
| infographic         | `notebooklm generate infographic`  |
| flashcards          | `notebooklm generate flashcards`   |
| summary             | `notebooklm summary`               |
| data table          | `notebooklm generate data-table`   |
| slide deck / slides | `notebooklm generate slide-deck`   |

After triggering generation, poll for completion:
```powershell
notebooklm artifact wait
```
Then list the finished artifacts:
```powershell
notebooklm artifact list
```
If the artifact is downloadable, offer to download it:
```powershell
notebooklm download <type>
```

### 5. List artifacts for current notebook
```powershell
notebooklm artifact list
```
Show the user the artifact titles, types, and status.

---

## Output format

After each operation, summarize what happened in plain language:
- Notebook created: name and ID
- Sources added: count and URLs
- Artifact generation: type, status, and location of downloaded file if applicable

If a command fails, show the error and suggest the most likely fix (e.g., run `notebooklm login` if unauthenticated, or `notebooklm use <id>` if no notebook is active).
