"""Merge concept 1's ribbon-figure symbol with concept 2's wordmark and ornaments.

Both source images are 1774x887 ChatGPT renders on near-identical cream.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
AI = os.path.join(os.path.dirname(HERE), "ai-concepts")
OUT = os.path.join(AI, "iomu2027_merge_c1-symbol_c2-type_B_v1.png")

c1 = np.asarray(Image.open(os.path.join(AI, "iomu2027_chatgpt_c1_ribbon-figure_B.png")).convert("RGB")).astype(float)
c2 = np.asarray(Image.open(os.path.join(AI, "iomu2027_chatgpt_c2_kawung-cross_B.png")).convert("RGB")).astype(float)
H, W, _ = c2.shape
BG1 = np.array([245, 235, 215.0])
BG2 = np.array([245, 237, 219.0])

# 1. concept 2 without its kawung symbol (symbol occupies x<=707, text starts at x=739)
canvas = c2.copy()
canvas[:, :725] = BG2

# 2. concept 1 symbol region: x<705 everywhere, plus the arm tip up to x<735 above row 265
region = np.zeros((H, W), bool)
region[:, :705] = True
region[:265, 705:735] = True
mask = Image.fromarray((region * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
m = np.asarray(mask).astype(float)[..., None] / 255.0
sym = c1 + (BG2 - BG1)  # match cream

# shift symbol right so its right edge (x~724) sits just left of the wordmark (x=739)
dx = 739 - 724 - 25
sym = np.roll(sym, dx, axis=1)
m = np.roll(m, dx, axis=1)
canvas = canvas * (1 - m) + sym * m

# 3. recentre horizontally
ink = (np.abs(canvas - BG2).sum(2) > 60)
xs = np.where(ink.any(0))[0]
shift = int(round(W / 2 - (xs[0] + xs[-1]) / 2))
out = np.empty_like(canvas)
out[:] = BG2
if shift >= 0:
    out[:, shift:] = canvas[:, :W - shift]
else:
    out[:, :W + shift] = canvas[:, -shift:]
print("ink x", xs[0], xs[-1], "shift", shift)

Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(OUT)
print(OUT)
