"""Schematic spirometry curve gallery for Catatan_Spirometri_v2.docx.

Curves are schematic (shape teaching only), not patient data.
Usage: python make_figures.py OUTDIR
"""
import sys
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#1F4E79"
GREY = "#9E9E9E"
RED = "#C62828"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False})


def expir(v, fvc, pef, k, vp=0.12):
    """Expiratory flow at volume v (0 = TLC)."""
    f = np.where(v < vp, pef * np.sin(np.pi / 2 * v / vp),
                 pef * np.clip((fvc - v) / (fvc - vp), 0, None) ** k)
    return f


def inspir(v, fvc, pif):
    return -pif * np.sin(np.pi * np.clip(v / fvc, 0, 1))


def loop(ax, fvc, pef, k, pif, ecap=None, icap=None, ref=True, title="", note=""):
    v = np.linspace(0, fvc, 400)
    e = expir(v, fvc, pef, k)
    i = inspir(v, fvc, pif)
    if ecap is not None:
        e = np.minimum(e, ecap)
    if icap is not None:
        i = np.maximum(i, -icap)
    if ref:
        vr = np.linspace(0, 5.0, 400)
        ax.plot(vr, expir(vr, 5.0, 10, 1.0), color=GREY, ls="--", lw=1)
        ax.plot(vr, inspir(vr, 5.0, 7), color=GREY, ls="--", lw=1)
    ax.plot(v, e, color=BLUE, lw=2)
    ax.plot(v, i, color=BLUE, lw=2)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xlim(-0.2, 5.6)
    ax.set_ylim(-8.5, 11.5)
    ax.set_title(title, fontsize=10, fontweight="bold", color=BLUE)
    ax.set_xlabel("Volume (L)  →  ekspirasi ke kanan", fontsize=7.5)
    ax.set_ylabel("Aliran (L/s)", fontsize=7.5)
    ax.tick_params(labelsize=7)
    if note:
        ax.text(0.98, 0.97, note, transform=ax.transAxes, ha="right", va="top",
                fontsize=7.2, color="#333333",
                bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="#DDDDDD"))


def fig_patterns():
    fig, axs = plt.subplots(2, 4, figsize=(13, 6.6))
    axs = axs.ravel()
    loop(axs[0], 5.0, 10, 1.0, 7, ref=False, title="Normal",
         note="Puncak tajam di awal\nturun hampir lurus\nloop inspirasi setengah\nlingkaran")
    loop(axs[1], 4.3, 6.5, 2.6, 6, title="Obstruktif",
         note="PEF turun, lengkung\nCEKUNG (scooped/coved)\nFEV1/FVC < LLN")
    loop(axs[2], 2.9, 8.5, 0.75, 5.5, title="Pola restriktif",
         note="Bentuk normal tapi\nSEMPIT (FVC kecil),\nekor cembung,\nFEV1/FVC normal/↑")
    loop(axs[3], 2.8, 5.0, 2.3, 4.5, title="Pola campuran",
         note="Sempit DAN cekung\nKonfirmasi TLC")
    loop(axs[4], 4.8, 10, 1.0, 7, ecap=3.2, icap=3.0,
         title="Saluran napas atas: FIXED",
         note="Plateau datar di\nekspirasi DAN inspirasi\n(stenosis trakea,\ntumor, struma)")
    loop(axs[5], 4.8, 10, 1.0, 7, icap=2.6,
         title="Variabel EKSTRAtoraks",
         note="Inspirasi mendatar,\nekspirasi relatif normal\n(paralisis/disfungsi\npita suara)")
    loop(axs[6], 4.8, 10, 1.0, 7, ecap=3.2,
         title="Variabel INTRAtoraks",
         note="Ekspirasi mendatar,\ninspirasi relatif normal\n(tumor trakea distal,\ntrakeomalasia)")
    ax = axs[7]
    ax.axis("off")
    ax.text(0.0, 0.95, "Cara membaca", fontsize=10, fontweight="bold", color=BLUE, va="top")
    ax.text(0.0, 0.82,
            "• Garis putus-putus abu = kurva normal\n  sebagai pembanding.\n"
            "• Ekspirasi di atas sumbu X, inspirasi\n  di bawah sumbu X.\n"
            "• Plateau datar = aliran dibatasi\n  diameter tetap (saluran napas besar).\n"
            "• Ekstratoraks: tekanan negatif saat\n  inspirasi menyempitkan lumen.\n"
            "• Intratoraks: tekanan pleura positif\n  saat ekspirasi paksa menyempitkan\n  lumen.\n"
            "• Obstruksi saluran napas atas tidak\n  terlihat tanpa manuver FIVC (loop\n  inspirasi).",
            fontsize=8, va="top", color="#222222")
    fig.suptitle("Galeri bentuk kurva flow-volume (skematis)", fontsize=13,
                 fontweight="bold", color=BLUE, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / "fig_pola_flow_volume.png", dpi=200)
    plt.close(fig)


def vt_normal(t, fvc=4.5, tau=0.55):
    return fvc * (1 - np.exp(-t / tau))


def vt_panel(ax, t, v, title, note, ref=True, mark=None):
    if ref:
        ax.plot(t, vt_normal(t), color=GREY, ls="--", lw=1)
    ax.plot(t, v, color=BLUE, lw=2)
    if mark is not None:
        dy = mark[3] if len(mark) > 3 else -1.4
        ax.annotate(mark[2], xy=(mark[0], mark[1]), xytext=(mark[0] + 1.3, mark[1] + dy),
                    arrowprops=dict(arrowstyle="->", color=RED), color=RED, fontsize=7.5)
    ax.set_xlim(-0.3, 8)
    ax.set_ylim(-0.1, 5.6)
    ax.set_title(title, fontsize=10, fontweight="bold", color=BLUE)
    ax.set_xlabel("Waktu (s)", fontsize=7.5)
    ax.set_ylabel("Volume (L)", fontsize=7.5)
    ax.tick_params(labelsize=7)
    ax.text(0.98, 0.04, note, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.2, color="#333333",
            bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="#DDDDDD"))


def fig_artefacts():
    t = np.linspace(0, 8, 800)
    fig, axs = plt.subplots(2, 4, figsize=(13, 6.6))
    axs = axs.ravel()
    vt_panel(axs[0], t, vt_normal(t), "Normal (acceptable)",
             "Naik tajam, plateau\n≥1 s (<25 mL)", ref=False)
    # hesitant start: slow ramp for 0.6 s before blast
    th = np.clip(t - 0.6, 0, None)
    v = np.where(t < 0.6, 0.35 * t / 0.6, 0.35 + (4.5 - 0.35) * (1 - np.exp(-th / 0.55)))
    vt_panel(axs[1], t, v, "Awal ragu (BEV besar)",
             "BEV > 5% FVC / >100 mL\nFEV1 & FVC tidak dipakai", mark=(0.3, 0.2, "awal landai", 1.6))
    # cough in first second
    v = vt_normal(t) - 0.35 * np.exp(-((t - 0.45) / 0.06) ** 2)
    vt_panel(axs[2], t, v, "Batuk di detik pertama",
             "FEV1 tidak acceptable,\nFVC bisa acceptable", mark=(0.45, 1.6, "takik"))
    # glottis closure / early termination
    v = np.where(t < 1.6, vt_normal(t), vt_normal(1.6))
    vt_panel(axs[3], t, v, "Penutupan glotis / henti dini",
             "Datar mendadak di volume\nlebih rendah: FVC tidak\nacceptable", mark=(1.7, vt_normal(1.6), "berhenti tiba-tiba"))
    # early termination with curve still rising (cut at 2.5 s)
    tt = t[t <= 2.5]
    vt_panel(axs[4], t, vt_normal(t), "EOFE tidak tercapai", "Kurva masih naik saat\ndiputus: FVC underestimate", ref=False)
    axs[4].lines[-1].set_visible(False)
    axs[4].plot(tt, vt_normal(tt, fvc=4.5, tau=1.4), color=BLUE, lw=2)
    axs[4].plot(t, vt_normal(t, fvc=4.5, tau=1.4), color=GREY, ls="--", lw=1)
    # leak: lower plateau and drifting down
    v = vt_normal(t, fvc=3.7) - np.clip(t - 2, 0, None) * 0.08
    vt_panel(axs[5], t, v, "Kebocoran (mulut/selang)",
             "Plateau rendah, bisa\nmenurun; tidak repeatable")
    # extra breath via nose: step at end
    v = vt_normal(t) + np.where(t > 4.5, 0.45 * (1 - np.exp(-(t - 4.5) / 0.3)), 0)
    vt_panel(axs[6], t, v, "Napas tambahan lewat hidung",
             "Tangga tambahan di ekor:\nFVC naik palsu,\nrasio turun palsu", mark=(4.7, 4.75, "tangga"))
    # zero-flow over-recording: endless linear drift
    v = vt_normal(t) + 0.09 * t
    vt_panel(axs[7], t, v, "Zero-flow error (over-record)",
             "Tidak pernah plateau,\nterus naik linear:\nobstruksi palsu")
    fig.suptitle("Galeri artefak pada kurva volume-time (skematis; abu putus-putus = kurva acceptable)",
                 fontsize=13, fontweight="bold", color=BLUE, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / "fig_artefak_volume_time.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_patterns()
    fig_artefacts()
    print("ok", OUT)
