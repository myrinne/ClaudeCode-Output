---
name: gemini-image
description: Generate images (Nano Banana / Gemini image models) through Vidya's logged-in Gemini Pro account at gemini.google.com using Chrome automation. No API key or per-image billing. Use when she asks to generate, edit, or make an image/illustration/infographic with Gemini or Nano Banana.
---

# gemini-image

Drives gemini.google.com in Chrome (she is logged in as Pro). Verified 2026-10-07: prompt → image in ~20 s.

## Steps

1. Load Chrome tools in ONE ToolSearch call: `tabs_context_mcp, tabs_create_mcp, navigate, computer, javascript_tool, find, read_page`. Call `tabs_context_mcp` first; use a fresh tab.
2. Ask the output format/size if not given (she wants format asked before generating). Write the prompt in English unless she wants text inside the image in Indonesian.
3. `navigate` to `https://gemini.google.com/app`. Click the "Ask Gemini" box (center, ~(800,381) at 1440 wide), `type` the prompt starting with "Create an image:", press Return.
4. Wait ~20 s (two `wait` of 10 s). The tab title changes to the chat title when done. Do not screenshot while it is still rendering; screenshots can time out then.
5. Check completion with JS:
   `[...document.querySelectorAll('img')].filter(i=>i.naturalWidth>300).map(i=>({w:i.naturalWidth,h:i.naturalHeight,alt:i.alt}))`
   The result image has alt ", AI generated" and a `blob:` src (preview ~1024 px wide).
6. Show her the result via screenshot (`save_to_disk: true` if she wants it attached).
7. To save the full-size file: hover the image, click the Download icon. **Downloading requires her explicit yes in chat first** (state filename/source). The file lands in her Downloads folder; move it into this repo (`ClaudeCode Output`) with a descriptive name. Outputs never go in the vault unless she asks.
8. Edits/iterations: reply in the same chat ("make the background darker"); attach reference images via the "+" button.
9. Close the tab you opened when done.

## Notes and limits

- Uses her Pro quota; if Gemini shows a limit message, report it and stop.
- UI-dependent: if coordinates/labels changed, use `find` / `read_page` instead of fixed coordinates.
- Never put patient data, NRM, or identifiable clinical images in prompts.
- Generated images carry a Gemini watermark/SynthID; say so if used in formal documents.
- API alternative (needs a Gemini API key with image billing, not tested): the key in `MiroThinker/apps/miroflow-agent/.env` as `GEMINI_API_KEY`.
