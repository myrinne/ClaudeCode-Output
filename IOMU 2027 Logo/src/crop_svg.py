"""Tighten an SVG's viewBox to its drawn content (+ margin), using a transparent render.

usage: python crop_svg.py <render.png> <file.svg> [<file.svg> ...]
The render must be of the first SVG at its native viewBox size (no background).
"""
import re
import sys
import numpy as np
from PIL import Image

MARGIN = 0.03  # of content height


def main(render, svgs):
    a = np.asarray(Image.open(render).convert("RGBA"))[..., 3]
    ys, xs = np.where(a > 8)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    m = (y1 - y0) * MARGIN
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    w, h = x1 - x0, y1 - y0
    for path in svgs:
        s = open(path, encoding="utf-8").read()
        s = re.sub(r'viewBox="[^"]*" width="[^"]*" height="[^"]*"',
                   f'viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}" width="{w / 3:.0f}" height="{h / 3:.0f}"', s, count=1)
        open(path, "w", encoding="utf-8").write(s)
        print(path, f"viewBox {x0:.0f} {y0:.0f} {w:.0f} {h:.0f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
