# OCR PDF → Editable PPTX

Converts a scanned PDF slide deck into a real, editable PowerPoint file.
Each page becomes one slide. Detected text is placed as editable text
boxes at its original position, size, colour and weight, and that text is
erased from the background image so nothing is printed twice.

**Main entry point: `ocr_pdf_to_pptx_hybrid.py`.** It uses Tesseract for
every page by default and can route specific hard pages to PaddleOCR
instead (see [Routing hard pages to PaddleOCR](#routing-hard-pages-to-paddleocr)
below). `ocr_pdf_to_pptx.py` is the shared Tesseract engine underneath it —
still fine to run directly for a Tesseract-only pass, but the hybrid script
is what you want by default.

## Core guarantee

Text is erased from the background **only** if it was successfully captured
as an editable text box. Anything OCR could not read stays visible as
pixels. Text can never silently disappear from a slide.

## Setup (one time)

1. **Install Tesseract OCR** with Indonesian + English language packs:
   - **Windows**: https://github.com/UB-Mannheim/tesseract/wiki (the installer
     has a language picker — tick Indonesian), or
     ```
     winget install UB-Mannheim.TesseractOCR
     ```
   - **Mac**: `brew install tesseract tesseract-lang`
   - **Linux**: `sudo apt install tesseract-ocr tesseract-ocr-ind`

   The script finds `tesseract.exe` automatically in the usual Windows
   install locations, so it does not need to be on PATH. Use `--tesseract`
   to point at it explicitly if yours lives elsewhere.

2. **Install Python packages:**
   ```
   pip install pymupdf pytesseract python-pptx pillow opencv-python-headless numpy
   ```

3. **(Optional) Set up PaddleOCR** — only needed if you plan to use
   `--paddle-pages` for hard pages (see below). PaddleOCR's dependency
   chain (`paddlepaddle` in particular) doesn't coexist with the packages
   above, so it needs its own virtualenv, e.g. `.venvs\paddleocr312\`:
   ```
   py -3.12 -m venv .venvs\paddleocr312
   .venvs\paddleocr312\Scripts\python.exe -m pip install paddlepaddle paddleocr pymupdf pytesseract python-pptx pillow opencv-python-headless numpy
   ```
   Tesseract-only runs need none of this and work fine under plain `py`.

## Usage

```
python ocr_pdf_to_pptx_hybrid.py input.pdf output.pptx
```

### Options

| Flag | Description |
|---|---|
| `--paddle-pages` | 1-based pages to run through PaddleOCR instead of Tesseract, e.g. `"9,16,20"` or `"9,14,16,20,23-24"`. All other pages use Tesseract. |
| `--lang ind+eng` | Tesseract language(s) (default: `ind+eng`) |
| `--paddle-lang en` | PaddleOCR language model (default: `en`) |
| `--dpi 400` | Render resolution for OCR (default: 400) |
| `--min-conf 35` | Tesseract confidence floor, 0-100 |
| `--paddle-min-conf 70.0` | PaddleOCR confidence floor, 0-100 |
| `--background clean` | `clean` = captured text erased (default) · `original` = untouched page image, text boxes on top · `none` = no background at all |
| `--bg-max-width 2400` | Downscale the background before embedding it |
| `--font Arial` | Font for the generated text boxes |
| `--pages 1-24` | Convert only some pages at all (default: whole deck) |
| `--no-refine` | Skip Tesseract's per-line re-OCR repair pass |
| `--no-recover` | Skip Tesseract's second-chance pass for missed text |
| `--tesseract PATH` | Full path to `tesseract.exe` |

### Batch

```bash
for f in *.pdf; do
  python ocr_pdf_to_pptx_hybrid.py "$f" "${f%.pdf}.pptx"
done
```

## Routing hard pages to PaddleOCR

Tesseract is ~6x faster (about 20-25s/slide vs 130-150s/slide on CPU-only
hardware) and is fine for ordinary text slides. Route a page to PaddleOCR
with `--paddle-pages` when it has:
- a line-art diagram/illustration (Tesseract hallucinates short "words"
  from crossing pencil strokes), or
- a dense multi-column table (Tesseract mis-clusters rows across columns
  and mis-reads small decimals).

**Workflow:** convert the whole deck first with plain Tesseract (no
`--paddle-pages`) and skim it — the slides that still look rough are the
ones to list for a second pass:

```
.venvs\paddleocr312\Scripts\python.exe ocr_pdf_to_pptx_hybrid.py input.pdf output.pptx --paddle-pages 9,16,20
```

`--paddle-pages` requires running under the PaddleOCR venv's interpreter
(see Setup step 3) — plain `py`/`python` won't have `paddleocr` installed.

## Checking the result

```
python preview_pptx.py output.pptx previews/
python preview_pptx.py output.pptx previews/ --pages 2,3
```

Renders an approximate PNG of each slide — background plus every text
box at its real position, size, colour and weight — so a conversion can
be checked without opening PowerPoint. Font metrics are approximated, so
treat it as a proof sheet, not a pixel-accurate render.

## How it works

1. Renders each page well above its native resolution.
2. Detects words in both polarities (normal + inverted) so light-on-dark
   text, such as a navy table header, is found too.
3. Clusters words into rows geometrically, then splits each row wherever
   a wide horizontal gap appears — otherwise Tesseract reports an entire
   table row as one line and welds the cells into a single string.
4. Re-OCRs uncertain lines as isolated, upscaled crops, which segment far
   more reliably than a whole page, and keeps a rewrite only when the
   confidence improves and the text did not fragment.
5. Two second-chance passes look for text the page-layout analysis
   skipped entirely, and accept only high-confidence finds.
6. Measures each line's colour, weight and point size from its own
   pixels, splitting a line into runs where the colour changes so
   mid-sentence emphasis survives.
7. Erases captured text: a flat repaint where the background is uniform,
   inpainting where it is not.
8. (Hybrid only) Steps 1-7 run per-page with either engine; both engines
   reduce a page to the same `{text, x0, y0, x1, y1, conf}` line shape, so
   everything downstream — colour/weight/size measurement, background
   erasing, PPTX assembly — is engine-agnostic and shared from
   `ocr_pdf_to_pptx.py`.

## Limits — worth knowing

- OCR accuracy is capped by the source. If the PDF's page images are
  low resolution, rendering at a higher `--dpi` only enlarges the blur, it
  does not add detail. In one 1376×768 deck the "%" sign is about eight
  pixels wide and Tesseract reads it as "4" at high confidence, so
  "23,5%" becomes "23,54". No preprocessing recovers it. Larger "%"
  glyphs on the same deck read correctly.
- Diagrams, photos, charts and icons are not rebuilt as PowerPoint
  objects. They stay as part of the background image; only text becomes
  editable.
- Tables become individually positioned text boxes, not real PowerPoint
  table objects. Cells are separate and editable, but there is no grid.
- The font is a stand-in (Arial by default). The original typeface is not
  identified; sizes are fitted so text occupies its original footprint.
- Always skim the result. Text is fully editable, so fixes are quick.
