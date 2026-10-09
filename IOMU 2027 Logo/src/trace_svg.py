"""Trace the gunungan logo PNG into a flat 2-colour SVG (transparent background).

1. upscale 3x, 2. snap pixels to white / emerald / gold, 3. vtracer (cutout, spline),
4. drop white paths, set exact palette fills, write palette B and C files.
usage: python trace_svg.py <input.png> <out_dir>
"""
import os
import re
import sys
import tempfile
import numpy as np
import vtracer
from PIL import Image, ImageFilter

REFS = np.array([[252, 252, 252], [16, 68, 56], [208, 165, 90]], float)  # white, emerald, gold
QUANT = np.array([[255, 255, 255], [0, 0, 255], [255, 0, 0]], np.uint8)  # distinct tracer colours
FILLS = {
    "B": {"#0000FF": "#214940", "#FF0000": "#C69C54"},
    "C": {"#0000FF": "#6E442C", "#FF0000": "#B37B56"},
}
SCALE = 3


def main(src, out_dir):
    im = Image.open(src).convert("RGB")
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    d = np.stack([((a - r.astype(np.float32)) ** 2).sum(-1) for r in REFS], -1)
    lab = d.argmin(-1).astype(np.uint8)
    print("classified", lab.shape, flush=True)
    lab = np.asarray(Image.fromarray(lab * 100).filter(ImageFilter.ModeFilter(5))) // 100
    q = QUANT[lab]
    tmp = os.path.join(tempfile.gettempdir(), "iomu_quant.png")
    Image.fromarray(q).save(tmp)
    raw = os.path.join(tempfile.gettempdir(), "iomu_raw.svg")
    print("tracing", flush=True)
    vtracer.convert_image_to_svg_py(
        tmp, raw, colormode="color", hierarchical="cutout", mode="spline",
        filter_speckle=12, color_precision=8, layer_difference=64,
        corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=2)
    svg = open(raw, encoding="utf-8").read()
    w, h = im.width, im.height

    paths = re.findall(r"<path[^>]*/>", svg)
    keep = []
    for p in paths:
        m = re.search(r'fill="(#[0-9A-Fa-f]{6})"', p)
        if not m:
            continue
        rgb = np.array([int(m.group(1)[i:i + 2], 16) for i in (1, 3, 5)])
        # vtracer drifts a few levels (#0000FE, #0100FD...): snap to the nearest tracer colour
        idx = int(((QUANT.astype(int) - rgb) ** 2).sum(1).argmin())
        col = ["#FFFFFF", "#0000FF", "#FF0000"][idx]
        if col != "#FFFFFF":
            keep.append((col, p))
    print("paths total", len(paths), "kept", len(keep))

    os.makedirs(out_dir, exist_ok=True)
    for pal, fills in FILLS.items():
        body = []
        for col, p in keep:
            body.append(re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{fills[col]}"', p))
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
               f'width="{w // SCALE}" height="{h // SCALE}">\n' + "\n".join(body) + "\n</svg>\n")
        out = os.path.join(out_dir, f"iomu2027_gunungan_{pal}_v1.svg")
        open(out, "w", encoding="utf-8").write(doc)
        print(out, round(len(doc) / 1024), "KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
