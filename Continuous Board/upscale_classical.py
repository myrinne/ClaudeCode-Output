"""Classical (no AI, no extra install) 4x upscale of the corridor illustration.

Two 2x Lanczos steps with a gentle unsharp mask after each. Works on a locked-down
Windows machine (only Pillow needed). Also writes a side-by-side crop to judge it.

usage: python upscale_classical.py [crop_png_out]
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter

here = Path(__file__).parent
src = Image.open(here / "images" / "corridor-long.png").convert("RGB")
print("source", src.size)

s1 = src.resize((src.width * 2, src.height * 2), Image.LANCZOS)
s1 = s1.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=4))
s2 = s1.resize((src.width * 4, src.height * 4), Image.LANCZOS)
s2 = s2.filter(ImageFilter.UnsharpMask(radius=1.6, percent=28, threshold=6))
out = here / "images" / "corridor-long-4x.png"
s2.save(out, optimize=True)
print("wrote", out.name, s2.size)

# side-by-side crop (surgeon + x-ray area) at 1:1 of the 4x size: plain bicubic vs ours
box = (330, 70, 530, 260)                       # source coords
plain = src.resize((src.width * 4, src.height * 4), Image.BICUBIC).crop(tuple(v * 4 for v in box))
ours = s2.crop(tuple(v * 4 for v in box))
w, h = plain.size
cmp_img = Image.new("RGB", (w * 2 + 20, h), "white")
cmp_img.paste(plain, (0, 0))
cmp_img.paste(ours, (w + 20, 0))
cmp_out = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "_compare.png"
cmp_img.save(cmp_out)
print("compare", cmp_out)
