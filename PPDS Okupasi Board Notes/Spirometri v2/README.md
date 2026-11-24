# Catatan Spirometri v2 (board Sp.Ok)

Builds `Catatan_Spirometri_v2.docx` from the original `Catatan_Spirometri.docx` in
`PPDS Okupasi\Materi Board\Catatan Vidya\` (the original is only read, never changed).
The output docx lives in OneDrive beside the original, not in this repo.

## Rebuild

```powershell
# 1. figures (schematic curve galleries)
uvx --with matplotlib --with numpy python -I make_figures.py <FIGDIR>
# 2. document
$env:PYTHONIOENCODING='utf-8'
uvx --from python-docx python build_v2.py "<...>\Catatan_Spirometri.docx" "<...>\Catatan_Spirometri_v2.docx" <FIGDIR>
```

`build_v2.py` stops with `FAILED:` if an anchor paragraph is not found, so edits to the
original notes show up immediately.

## Files

- `build_v2.py`: fixes, cross-reference replacement, insert positions
- `docx_ops.py`: paragraph/table/callout helpers (same callout colours as the original)
- `content_*.py`: the new text, one module per topic
- `make_figures.py`: flow-volume pattern gallery and volume-time artefact gallery
- `jawaban NotebookLM/`: questions (`qNN_pertanyaan.txt`) and answers (`qNN.md`) from the
  Spirometri notebook, source citations resolved to document names; `q12` was limited to
  the ERS/ATS 2022 PDF
- `make_q.py`, `ask_all.ps1`, `extract.py`: how the questions were sent (one per call)

## Sources outside the notebook

ATS/ERS 2019 full text (PMC6794117), PubMed records for occupational asthma diagnostics
(doi:10.4168/aair.2019.11.2.188, 10.1378/chest.08-0778, 10.1093/occmed/kqp081,
10.1093/occmed/kqs097, 10.1183/13993003.01526-2016), and the owner's own
"Catatan Kecacatan (AMA + Permenaker) Gabungan" for section 11.5.
