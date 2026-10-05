"""Build the v2 (final search, 2026-10-05) title/abstract screening workbooks.

Reuses the v1 workbook builder with v2 records. Decisions: records already screened
in v1 carry their v1 R1 decision (marked in R1 Note); new records use decisions_r1_v2.

Outputs:
  Screening_TA_v2_master.xlsx   - R1 + R2 + consensus, PRISMA counts, kappa, v1-only sheet
  Screening_TA_v2_blind_R2.xlsx - no R1 columns; Record ID shows "(v1 #N)" so R2 can reuse
                                  their own v1 decision for records already screened
"""
import json

from openpyxl import Workbook
from openpyxl.styles import Font

import build_screening_xlsx as b
from decisions_r1 import D as D1
from decisions_r1_v2 import D2

V1_JSON = b.HERE / "records.json"  # v1 records (gitignored, local only)

data = json.loads((b.HERE / "records_v2.json").read_text(encoding="utf-8"))
v1 = json.loads(V1_JSON.read_text(encoding="utf-8"))

merged = {}
for r in data["records"]:
    if r["v1_no"]:
        dec, rsn, note = D1[r["v1_no"]]
        merged[r["no"]] = (dec, rsn, f"[v1 #{r['v1_no']}] {note}")
        r["id"] = f"{r['id']} (v1 #{r['v1_no']})"
    else:
        merged[r["no"]] = D2[r["no"]]

b.R, b.DUPS, b.COUNTS, b.D = data["records"], data["duplicates"], data["counts"], merged
b.CRITERIA = [c for c in b.CRITERIA if c[0] not in ("Searches", "Not restricted", "Reviewer 2")] + [
    ("Searches (v2)", "Run 2026-10-05: PubMed 478, Scopus 537 (v2.2, TITLE-ABS), ProQuest 128, IEEE Xplore 135 (two CSV pages; note says 125, export has 135). Strings in vault note 'Summit Jakarta Perdoki Keywords' (Search v2). 417 duplicates removed -> 861 unique."),
    ("v1 overlap", "203 of the 861 were already screened in the v1 search (2026-09-16); their R1 decision is carried over and marked '[v1 #N]' in R1 Note. 658 records are new."),
    ("v2 rules", "Pneumoconiosis/silicosis/TB CXR or CT AI: I if data come from exposed workers in screening/surveillance/occupational exams with reader/radiologist reference; M if hospital patients, public dataset or unclear. NIHL: audiogram/exam-data classification in workers -> I; exposure/risk-factor-only models in workers -> M; general population -> E1. Biomarker/omics/genetic ML -> E3."),
    ("Not restricted", "No date or language limit (several Chinese/Japanese/Russian-language records; English abstracts used)."),
    ("Reviewer 2", "Screen independently in Screening_TA_v2_blind_R2.xlsx. Records marked '(v1 #N)' in Record ID were in your v1 workbook: reuse your own v1 decision. Then paste your R2 columns into the master (same row order, check No.)."),
]


def v1_only_sheet(wb):
    """Records screened in v1 but not retrieved by the final v2 search."""
    ws = wb.create_sheet("v1-only (not in v2)")
    in_v2 = {r["v1_no"] for r in data["records"] if r["v1_no"]}
    cols = [("v1 No.", 7), ("Source", 11), ("Record ID", 16), ("Title", 80), ("R1 Decision", 9), ("R1 Reason", 8), ("R1 Note", 50)]
    b.header(ws, cols)
    ws.freeze_panes = "A2"
    row = 2
    for r in v1["records"]:
        if r["no"] in in_v2:
            continue
        dec, rsn, note = D1[r["no"]]
        if dec in "IM":
            note = "CARRY FORWARD as 'identified via other methods' (PRISMA-ScR). " + note
        for col, v in enumerate([r["no"], r["source"], r["id"], r["title"], dec, rsn, note], 1):
            ws.cell(row, col, v).alignment = b.WRAP
        row += 1
    ws.cell(row + 1, 1, f"{row - 2} v1 records were not retrieved by v2. They are outside the final search; only I/M ones are carried forward via 'other methods'.").font = Font(italic=True)


def main():
    for blind, name in [(False, "Screening_TA_v2_master.xlsx"), (True, "Screening_TA_v2_blind_R2.xlsx")]:
        wb = Workbook()
        _, idx, last = b.screening_sheet(wb, blind)
        b.criteria_sheet(wb)
        if not blind:
            b.dup_sheet(wb)
            b.prisma_sheet(wb, idx, last)
            v1_only_sheet(wb)
        wb.save(b.HERE / name)
        print("saved", name)


if __name__ == "__main__":
    main()
