"""Recolour a palette-B logo (emerald + gold on white) to palette C (sogan + light sogan).

Channel-wise scaling against white keeps anti-aliasing, texture and shading:
    out = W - (W - px) * (W - target) / (W - source_ref)
Green-family and gold-family results are blended by hue.
usage: python recolor_palette_c.py <input.png>
"""
import colorsys
import os
import sys
import numpy as np
from PIL import Image

W = 248.0
GREEN_REF = np.array([16, 68, 56.0])
GOLD_REF = np.array([208, 165, 90.0])
SOGAN = np.array([0x6E, 0x44, 0x2C], float)
SOGAN_LIGHT = np.array([0xB3, 0x7B, 0x56], float)
CREAM = np.array([0xF4, 0xE9, 0xD7], float)


def remap(px, ref, target):
    return W - (W - px) * (W - target) / (W - ref)


def main(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    # emerald family: map darkness (luminance vs white) onto sogan, so no green/teal tint survives
    lum = a @ np.array([0.299, 0.587, 0.114])
    ref_lum = GREEN_REF @ np.array([0.299, 0.587, 0.114])
    t = np.clip((W - lum) / (W - ref_lum), 0, 1.6)[..., None]
    g = np.clip(W - t * (W - SOGAN), 0, 255)
    o = remap(a, GOLD_REF, SOGAN_LIGHT)
    hsv = np.asarray(Image.fromarray(a.astype(np.uint8)).convert("HSV")).astype(float)
    hue = hsv[..., 0] * 360 / 255
    w_green = np.clip((hue - 70) / 60, 0, 1)[..., None]
    out = np.clip(g * w_green + o * (1 - w_green), 0, 255)

    # cleanup: any pixel still green/teal (green-gold edge blends) falls back to the sogan mapping
    ohsv = np.asarray(Image.fromarray(out.astype(np.uint8)).convert("HSV")).astype(float)
    ohue, osat = ohsv[..., 0] * 360 / 255, ohsv[..., 1] / 255
    stray = ((ohue > 55) & (ohue < 200) & (osat > 0.1))[..., None]
    out = np.where(stray, g, out)

    # leave the neutral white background exactly as it was (its hue is random noise)
    sat = hsv[..., 1] / 255
    neutral = ((sat < 0.06) & (lum > 235))[..., None]
    out = np.where(neutral, a, out)

    base = os.path.splitext(path)[0].replace("_white_B", "")
    Image.fromarray(out.astype(np.uint8)).save(base + "_white_C.png")
    print(base + "_white_C.png")


if __name__ == "__main__":
    main(sys.argv[1])
