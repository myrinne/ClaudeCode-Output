"""Gunungan emblem from 'IOMU Gunungan Conference Emblem' + text block (font, kawung
ornament, rule, tagline) from 'IOMU Solo 2027 Emblem and Wordmark'."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(os.path.dirname(HERE), "ai-concepts", "Revised")
OUT = os.path.join(os.path.dirname(HERE), "ai-concepts", "iomu2027_merge_gunungan_serif-type_B_v1.png")

base = np.asarray(Image.open(os.path.join(REV, "IOMU Gunungan Conference Emblem.png")).convert("RGB")).astype(float)
src = Image.open(os.path.join(REV, "IOMU Solo 2027 Emblem and Wordmark.png")).convert("RGB")
H, W, _ = base.shape
BG = np.array([247, 237, 217.0])      # base cream
BG_SRC = np.array([254, 251, 243.0])  # source off-white

# text block in source: ink x 1001-1865, y 254-638; base text ink: x 623-1511, y 318-711
pad = 14
crop = src.crop((1001 - pad, 254 - pad, 1865 + pad, 638 + pad))
scale = (711 - 318) / (638 - 254)
crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
t = np.asarray(crop).astype(float)

# re-tint source background to base cream; ink keeps its colour
w_bg = np.clip(1 - np.abs(t - BG_SRC).sum(2, keepdims=True) / 90.0, 0, 1)
t = t + (BG - BG_SRC) * w_bg

canvas = base.copy()
canvas[:, 600:] = BG
x0, y0 = round(623 - pad * scale), round(318 - pad * scale)
h, w = t.shape[:2]
canvas[y0:y0 + h, x0:x0 + w] = t

# recentre horizontally
ink = np.abs(canvas - BG).sum(2) > 60
xs = np.where(ink.any(0))[0]
shift = int(round(W / 2 - (xs[0] + xs[-1]) / 2))
out = np.empty_like(canvas)
out[:] = BG
if shift >= 0:
    out[:, shift:] = canvas[:, :W - shift]
else:
    out[:, :W + shift] = canvas[:, -shift:]
print("scale", round(scale, 3), "ink", xs[0], xs[-1], "shift", shift)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(OUT)
print(OUT)
