"""Tone down the 'AI look' of generated images: muted film-like grade instead of
hyper-saturated HDR. Usage: python humanize.py in.png out.jpg [natural|film]"""
import sys
import numpy as np
from PIL import Image, ImageFilter

PRESETS = {
    # base sat, orange sat, green sat, highlight sat, contrast, shoulder, black lift, clarity cut, grain, haze
    "natural": dict(sat=0.80, sat_or=0.70, sat_gr=0.74, sat_hi=0.75, con=0.90, sh=0.70, lift=0.03, soft=0.28, grain=0.020, haze=0.06),
    "film":    dict(sat=0.70, sat_or=0.60, sat_gr=0.64, sat_hi=0.65, con=0.84, sh=0.62, lift=0.05, soft=0.38, grain=0.030, haze=0.10),
}


def hue_masks(rgb_u8):
    hsv = np.asarray(Image.fromarray(rgb_u8).convert("HSV"), dtype=float)
    h = hsv[..., 0] * 360 / 255
    s = hsv[..., 1] / 255

    def band(lo, hi, feather=12):
        m = np.clip((h - (lo - feather)) / feather, 0, 1) * np.clip(((hi + feather) - h) / feather, 0, 1)
        return m * np.clip(s * 2, 0, 1)
    return band(12, 52), band(70, 170)


def humanize(src, dst, preset="natural"):
    p = PRESETS[preset]
    im = Image.open(src).convert("RGB")
    u8 = np.asarray(im)
    x = u8.astype(float) / 255

    # 1. clarity cut: blend with a softened copy (kills crunchy HDR micro-contrast)
    soft = np.asarray(im.filter(ImageFilter.GaussianBlur(1.6)), dtype=float) / 255
    x = x * (1 - p["soft"]) + soft * p["soft"]

    # 2. hue-selective desaturation (neon orange + neon green), extra on highlights
    orange, green = hue_masks(u8)
    L = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    s = np.full(L.shape, p["sat"])
    s = s * (1 - orange[..., None]) + p["sat_or"] * orange[..., None]
    s = s * (1 - green[..., None]) + np.minimum(s, p["sat_gr"]) * green[..., None]
    s = s * (1 - np.clip((L - 0.65) / 0.3, 0, 1) * (1 - p["sat_hi"]))
    x = L + (x - L) * s

    # 3. tone: lower contrast, roll off highlights (no glow), lift blacks (matte)
    x = 0.5 + (x - 0.5) * p["con"]
    hi = x > 0.68
    x[hi] = 0.68 + (x[hi] - 0.68) * p["sh"]
    x = p["lift"] + x * (1 - p["lift"])

    # 4. slight neutral balance: cool the warm highlights a touch
    w = np.clip((L - 0.5) / 0.5, 0, 1)
    x[..., 0] -= 0.025 * w[..., 0]
    x[..., 2] += 0.02 * w[..., 0]

    # 5. atmospheric haze toward the middle band (distance) and soft vignette
    hgt, wid = x.shape[:2]
    yy = np.linspace(0, 1, hgt)[:, None, None]
    haze = p["haze"] * np.exp(-((yy - 0.42) / 0.18) ** 2)
    x = x * (1 - haze) + np.array([0.78, 0.80, 0.76]) * haze
    xx = np.linspace(-1, 1, wid)[None, :, None]
    yv = np.linspace(-1, 1, hgt)[:, None, None]
    x *= 1 - 0.10 * np.clip(xx ** 2 + yv ** 2 - 0.35, 0, 1)

    # 6. organic film grain (luma, slightly blurred, stronger in midtones)
    rng = np.random.default_rng(7)
    n = rng.normal(0, 1, (hgt, wid)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), dtype=float)
    n = (n - 128) / 40
    mid = 1 - np.abs(L - 0.5) * 1.2
    x += (p["grain"] * n)[..., None] * mid

    out = Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8))
    out.save(dst, quality=95)
    return dst


if __name__ == "__main__":
    humanize(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "natural")
