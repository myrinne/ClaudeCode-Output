"""Render concepts/*.svg to PNG (resvg) and build a review contact sheet.

usage: python render.py [version] [--sheet out.png] [--small]
"""
import glob
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CON = os.path.join(os.path.dirname(HERE), "concepts")


def render(svg, png, width):
    subprocess.run(["npx", "-y", "@resvg/resvg-js-cli", "--fit-width", str(width), svg, png],
                   check=True, capture_output=True, shell=(os.name == "nt"))


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    svgs = sorted(glob.glob(os.path.join(CON, f"*_{ver}.svg")))
    pngs = []
    for s in svgs:
        p = s[:-4] + ".png"
        render(s, p, 1200)
        pngs.append(p)
        print(p)
    if "--sheet" in sys.argv:
        out = sys.argv[sys.argv.index("--sheet") + 1]
        T = 560
        cols = 2
        rows = (len(pngs) + 1) // 2
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
        sheet = Image.new("RGB", (cols * T, rows * (T + 30)), "white")
        dr = ImageDraw.Draw(sheet)
        for i, p in enumerate(pngs):
            im = Image.open(p).convert("RGBA")
            im.thumbnail((T - 20, T - 20))
            bg = Image.new("RGB", (T - 10, T - 10), "#FFFFFF")
            bg.paste(im, ((T - 10 - im.width) // 2, (T - 10 - im.height) // 2), im)
            x, y = (i % cols) * T, (i // cols) * (T + 30)
            sheet.paste(bg, (x + 5, y + 5))
            dr.rectangle([x + 5, y + 5, x + T - 5, y + T - 5], outline="#cccccc")
            dr.text((x + 8, y + T), os.path.basename(p), fill="black", font=font)
        sheet.save(out)
        print(out)
    if "--small" in sys.argv:
        # 32 px / 16 px legibility test strip
        strip = Image.new("RGB", (len(pngs) * 120, 70), "white")
        for i, p in enumerate(pngs):
            im = Image.open(p).convert("RGBA")
            for j, sz in enumerate((32, 16)):
                t = im.copy()
                t.thumbnail((sz * 3, sz))
                strip.paste(t, (i * 120 + 5, 5 + j * 36), t)
        out = os.path.join(CON, f"_smalltest_{ver}.png")
        strip = strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST)
        strip.save(out)
        print(out)


if __name__ == "__main__":
    main()
