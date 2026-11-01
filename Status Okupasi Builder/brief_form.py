"""
Isi formulir BRIEF(TM) Survey v3.0 (PDF isian Humantech) dan render jadi PNG.

Spesifikasi satu aktivitas (dict):
{
  "title": "Mengantar penumpang",            # dipakai sebagai Job Name bila "job" kosong
  "job": "...", "site": "...", "station": "...", "date": "...", "dept": "...", "shift": "...", "product": "...",
  "parts": {"RHW": "PFD", "Neck": "PD", ...},  # P=Posture F=Force D=Duration R=Frequency
  "postures": ["HWExtended", "NeckFlex"],      # ikon postur yang dicentang
  "stressors": {"V": ["LeftHand", "RightHand", "Whole Body"]}  # V/L/S/I/G -> bagian tubuh Step 4
}
Bagian tubuh: LHW RHW LE RE LS RS Neck Back Legs.
Skor = jumlah kategori tercentang; Risk Rating: 3-4 = H, 2 = M, 0-1 = L (aturan form).
"""
import fitz

PARTS = ["LHW", "RHW", "LE", "RE", "LS", "RS", "Neck", "Back", "Legs"]
CODES = {"P": "1", "F": "2", "D": "3", "R": "4"}
STRESSORS = {"V": "Vibration", "L": "LowTemp", "S": "SoftTissue", "I": "Impact", "G": "GloveIssues"}
POSTURES = {"HWFlexed", "HWExtended", "HWUlnar", "HWRadial", "ElbowRotate", "ElbowExtend",
            "ShoulderBehind", "ShoulderRaised", "ShoulderShrug", "NeckFlex", "NeckSide",
            "NeckExtend", "NeckTwist", "BackFlex", "BackSide", "BackExtend", "BackTwist",
            "BackUnsupp", "LegsSquat", "LegsKneel", "LegsUnsupp"}
TEXT = {"job": "Job Name", "site": "Site Name", "station": "Station Name", "date": "Date",
        "dept": "Department Name", "shift": "Shift", "product": "Product"}
GREEN = (0.0, 1.0, 0.0)


def rating(score):
    return "H" if score >= 3 else ("M" if score == 2 else "L")


def fill(template, spec, out_png, dpi=150):
    doc = fitz.open(template)
    page = doc[0]
    widgets = {w.field_name: w for w in page.widgets()}

    def check(name):
        w = widgets[name]
        w.field_value = w.on_state()
        w.update()

    def text(name, value):
        w = widgets[name]
        w.field_value = value
        w.update()

    for key, field in TEXT.items():
        val = spec.get(key) or (spec.get("title") if key == "job" else "")
        if val:
            text(field, val)

    for pos in spec.get("postures", []):
        if pos not in POSTURES:
            raise KeyError("Ikon postur tidak dikenal: %s" % pos)
        check(pos)

    scores = {}
    for part in PARTS:
        codes = spec.get("parts", {}).get(part, "")
        bad = set(codes) - set(CODES)
        if bad:
            raise ValueError("%s: kode tidak dikenal %s" % (part, bad))
        if ("D" in codes or "R" in codes) and not ("P" in codes or "F" in codes):
            raise ValueError("%s: Duration/Frequency hanya boleh bila Posture/Force dicentang" % part)
        for c in codes:
            check(part + CODES[c])
        score = len(set(codes))
        scores[part] = score
        text(part + "Score", str(score))
        chosen = rating(score)
        for r in "HML":
            name = next((n for n in (part + r, part + "W" + r) if n in widgets), None)
            if name is None:
                continue
            w = widgets[name]
            if r == chosen:
                w.border_color = GREEN
                w.border_width = 2
            else:
                w.border_color = None
                w.border_width = 0
            w.update()

    body = {}
    for letter, places in spec.get("stressors", {}).items():
        check(STRESSORS[letter])
        for pl in places:
            body.setdefault(pl, []).append(letter)
    for pl, letters in body.items():
        text(pl, "".join(letters))

    page.get_pixmap(dpi=dpi).save(out_png)
    doc.close()
    return {p: (s, rating(s)) for p, s in scores.items()}
