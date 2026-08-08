OCR PDF -> Editable PPTX
=========================

Converts a scanned PDF slide deck into a real, editable PowerPoint file.
Each page becomes one slide. Detected text is placed as editable text
boxes at its original position, size, colour and weight, and that text is
erased from the background image so nothing is printed twice.

CORE GUARANTEE
--------------
Text is erased from the background ONLY if it was successfully captured
as an editable text box. Anything OCR could not read stays visible as
pixels. Text can never silently disappear from a slide.


SETUP (one time)
----------------
1. Install Tesseract OCR with Indonesian + English language packs:
   Windows : https://github.com/UB-Mannheim/tesseract/wiki (the installer
             has a language picker -- tick Indonesian), or
             winget install UB-Mannheim.TesseractOCR
   Mac     : brew install tesseract tesseract-lang
   Linux   : sudo apt install tesseract-ocr tesseract-ocr-ind

   The script finds tesseract.exe automatically in the usual Windows
   install locations, so it does not need to be on PATH. Use
   --tesseract to point at it explicitly if yours lives elsewhere.

2. Install Python packages:
   pip install pymupdf pytesseract python-pptx pillow opencv-python-headless numpy


USAGE
-----
   python ocr_pdf_to_pptx.py input.pdf output.pptx

Options:
   --lang ind+eng      OCR language(s) (default: ind+eng)
   --dpi 400           Render resolution for OCR (default: 400)
   --min-conf 35       Drop text still below this confidence after refinement
   --background clean  clean    = captured text erased (default)
                       original = untouched page image, text boxes on top
                       none     = no background at all
   --bg-max-width 2400 Downscale the background before embedding it
   --font Arial        Font for the generated text boxes
   --pages 1-3         Convert only some pages (handy for spot checks)
   --no-refine         Skip the per-line re-OCR repair pass
   --no-recover        Skip the second-chance pass for missed text
   --tesseract PATH    Full path to tesseract.exe

Batch:
   for f in *.pdf; do
     python ocr_pdf_to_pptx.py "$f" "${f%.pdf}.pptx"
   done


CHECKING THE RESULT
-------------------
   python preview_pptx.py output.pptx previews/
   python preview_pptx.py output.pptx previews/ --pages 2,3

Renders an approximate PNG of each slide -- background plus every text
box at its real position, size, colour and weight -- so a conversion can
be checked without opening PowerPoint. Font metrics are approximated, so
treat it as a proof sheet, not a pixel-accurate render.


HOW IT WORKS
------------
1. Renders each page well above its native resolution.
2. Detects words in both polarities (normal + inverted) so light-on-dark
   text, such as a navy table header, is found too.
3. Clusters words into rows geometrically, then splits each row wherever
   a wide horizontal gap appears -- otherwise Tesseract reports an entire
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


LIMITS -- worth knowing
-----------------------
- OCR accuracy is capped by the source. If the PDF's page images are
  low resolution, rendering at a higher --dpi only enlarges the blur, it
  does not add detail. In one 1376x768 deck the "%" sign is about eight
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
