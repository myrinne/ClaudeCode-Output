"""Build the title/abstract screening workbooks for the final search (2026-10-05).

Reuses the workbook builder in build_screening_xlsx with the final-search records.
R1 decisions come from decisions_r1 (records also found by the earlier pilot search,
linked via v1_no) and decisions_r1_v2 (all others). The workbooks themselves show
no trace of the pilot search.

Outputs (replace the earlier pilot workbooks of the same name):
  Screening_TA_master.xlsx   - R1 + R2 + consensus, PRISMA counts, kappa
  Screening_TA_blind_R2.xlsx - same records and criteria, no R1 columns
"""
import json
import re

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.datavalidation import DataValidation

import build_screening_xlsx as b
from decisions_r1 import D as D1
from decisions_r1_v2 import D2
from decisions_r1_refine import R as REFINE
from decisions_r1_final import DATE_CUTOFF, LEAD, PREDICTION
from fulltext import FT

data = json.loads((b.HERE / "records_v2.json").read_text(encoding="utf-8"))
to_final_no = {r["v1_no"]: r["no"] for r in data["records"] if r["v1_no"]}


def carried(v1_no):
    """Pilot decision with any '#N' cross-reference renumbered to the final record list."""
    dec, rsn, note = D1[v1_no]
    note = re.sub(r"#(\d+)", lambda m: f"#{to_final_no[int(m.group(1))]}" if int(m.group(1)) in to_final_no else "a pilot-only record", note)
    return dec, rsn, note


decisions = {r["no"]: carried(r["v1_no"]) if r["v1_no"] else D2[r["no"]] for r in data["records"]}
decisions.update(REFINE)
decisions.update(LEAD)
decisions.update(PREDICTION)
for r in data["records"]:
    year = int(r["year"]) if str(r["year"]).isdigit() else None
    if year and year < DATE_CUTOFF and decisions[r["no"]][0] in "IM":
        decisions[r["no"]] = ("E", "E8", f"Published {year} (>20 years old). Earlier: {decisions[r['no']][2]}")

b.REASONS = [(c, t) for c, t in b.REASONS if c != "E4"] + [
    ("E4", "Prediction/risk model: predicts risk, susceptibility or a future outcome instead of AI analysing (classifying/detecting) the current check-up result against a reference"),
    ("E8", f"Published before {DATE_CUTOFF} (more than 20 years old)"),
]
b.REASONS.sort()

b.R, b.DUPS, b.COUNTS, b.D = data["records"], data["duplicates"], data["counts"], decisions
b.CRITERIA = [c for c in b.CRITERIA if c[0] not in ("Searches", "Not restricted")] + [
    ("Searches", "Run 2026-10-05: PubMed 478, Scopus 537 (TITLE-ABS), ProQuest 128, IEEE Xplore 135 (two CSV pages). Strings in vault note 'Summit Jakarta Perdoki Keywords'. 417 duplicates removed -> 861 unique."),
    ("Population rule (P)", "Applied strictly to every study: the abstract must show the data come from workers (occupational/periodic/pre-placement exam, screening or surveillance programme, or a worker/exposed cohort). Hospital patients, public image datasets, ILO standard films only, and technical papers that do not describe a worker population -> E1."),
    ("Input rule (I)", "Risk/prediction models count only if examination results (audiometry, laboratory, spirometry, imaging, ECG) are model inputs. Exposure/demographic/questionnaire-only inputs -> E3. Biomarker/omics/genetic ML (not routine exam data) -> E3."),
    ("Scope (aim)", "AI that ANALYSES medical check-up data, i.e. classifies or detects the current examination result against a physician/clinical reference. Prediction, risk, susceptibility and early-warning models are out of scope (E4)."),
    ("Date limit", f"Published {DATE_CUTOFF} or later (last 20 years); older -> E8. No language limit (English abstracts used)."),
]


def fulltext_sheet(wb):
    """Full-text retrieval and eligibility for records kept at title/abstract (I or M)."""
    ws = wb.create_sheet("Full text", 1)
    cols = [("No.", 6), ("Record ID", 16), ("Year", 6), ("First authors", 18), ("Title", 60), ("DOI", 26),
            ("TA decision", 9), ("FT status", 13), ("FT decision", 11), ("FT reason", 9), ("FT note", 50)]
    b.header(ws, cols, {n: b.CFILL for n in ("FT status", "FT decision", "FT reason", "FT note")})
    ws.freeze_panes = "F2"
    row = 2
    for r in data["records"]:
        dec = decisions[r["no"]][0]
        if dec not in "IM":
            continue
        st, fd, fr, fn = FT.get(r["no"], ("", "", "", ""))
        for col, v in enumerate([r["no"], r["id"], r["year"], r["authors"], r["title"], r["doi"], dec, st, fd, fr, fn], 1):
            ws.cell(row, col, v).alignment = b.WRAP
        row += 1
    last = row - 1
    for formula, rng in [('"Retrieved,Not retrieved"', "H"), ('"Include,Exclude"', "I"),
                         ('"' + ",".join(c for c, _ in b.REASONS) + '"', "J")]:
        dv = DataValidation(type="list", formula1=formula, allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{rng}2:{rng}{last}")
    ws.auto_filter.ref = f"A1:K{last}"
    return last


def fulltext_prisma(wb, last):
    """Append full-text counts below the existing PRISMA rows."""
    ws = wb["PRISMA counts"]
    F = "'Full text'!"
    st, fd, fr = (f"{F}${c}$2:${c}${last}" for c in "HIJ")
    rows = [("FULL-TEXT STAGE", None, None),
            ("Reports sought for retrieval", f"=COUNTA({F}$A$2:$A${last})", "Records kept (I/M) at title/abstract"),
            ("Reports not retrieved", f'=COUNTIF({st},"Not retrieved")', "Not subscribed / not open access; reported, not excluded"),
            ("Reports assessed for eligibility", f'=COUNTIF({st},"Retrieved")', ""),
            ("Reports excluded at full text", f'=COUNTIF({fd},"Exclude")', "")]
    rows += [(f"   {c}: {t[:70]}", f'=COUNTIFS({fd},"Exclude",{fr},"{c}")', "") for c, t in b.REASONS]
    rows += [("Studies included in review", f'=COUNTIF({fd},"Include")', ""),
             ("Full-text decisions still pending", f'=B{{sought}}-COUNTIF({st},"Not retrieved")-COUNTA({fd})', "Should reach 0")]
    start = ws.max_row + 2
    sought = start + 1
    for i, (a, val, note) in enumerate(rows):
        rr = start + i
        ws.cell(rr, 1, a)
        if val is None:
            ws.cell(rr, 1).font = Font(bold=True, color="1F4E78")
        else:
            ws.cell(rr, 2, val.replace("{sought}", str(sought)))
        if note:
            ws.cell(rr, 3, note).alignment = b.WRAP


def main():
    for blind, name in [(False, "Screening_TA_master.xlsx"), (True, "Screening_TA_blind_R2.xlsx")]:
        wb = Workbook()
        _, idx, last = b.screening_sheet(wb, blind)
        b.criteria_sheet(wb)
        if not blind:
            b.dup_sheet(wb)
            b.prisma_sheet(wb, idx, last)
            fulltext_prisma(wb, fulltext_sheet(wb))
        wb.save(b.HERE / name)
        print("saved", name)


if __name__ == "__main__":
    main()
