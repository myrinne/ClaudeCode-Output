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

import build_screening_xlsx as b
from decisions_r1 import D as D1
from decisions_r1_v2 import D2
from decisions_r1_refine import R as REFINE

data = json.loads((b.HERE / "records_v2.json").read_text(encoding="utf-8"))
to_final_no = {r["v1_no"]: r["no"] for r in data["records"] if r["v1_no"]}


def carried(v1_no):
    """Pilot decision with any '#N' cross-reference renumbered to the final record list."""
    dec, rsn, note = D1[v1_no]
    note = re.sub(r"#(\d+)", lambda m: f"#{to_final_no[int(m.group(1))]}" if int(m.group(1)) in to_final_no else "a pilot-only record", note)
    return dec, rsn, note


decisions = {r["no"]: carried(r["v1_no"]) if r["v1_no"] else D2[r["no"]] for r in data["records"]}
decisions.update(REFINE)

b.R, b.DUPS, b.COUNTS, b.D = data["records"], data["duplicates"], data["counts"], decisions
b.CRITERIA = [c for c in b.CRITERIA if c[0] not in ("Searches", "Not restricted")] + [
    ("Searches", "Run 2026-10-05: PubMed 478, Scopus 537 (TITLE-ABS), ProQuest 128, IEEE Xplore 135 (two CSV pages). Strings in vault note 'Summit Jakarta Perdoki Keywords'. 417 duplicates removed -> 861 unique."),
    ("Population rule (P)", "Applied strictly to every study: the abstract must show the data come from workers (occupational/periodic/pre-placement exam, screening or surveillance programme, or a worker/exposed cohort). Hospital patients, public image datasets, ILO standard films only, and technical papers that do not describe a worker population -> E1."),
    ("Input rule (I)", "Risk/prediction models count only if examination results (audiometry, laboratory, spirometry, imaging, ECG) are model inputs. Exposure/demographic/questionnaire-only inputs -> E3. Biomarker/omics/genetic ML (not routine exam data) -> E3."),
    ("Not restricted", "No date or language limit (several Chinese/Japanese/Russian-language records; English abstracts used)."),
]


def main():
    for blind, name in [(False, "Screening_TA_master.xlsx"), (True, "Screening_TA_blind_R2.xlsx")]:
        wb = Workbook()
        _, idx, last = b.screening_sheet(wb, blind)
        b.criteria_sheet(wb)
        if not blind:
            b.dup_sheet(wb)
            b.prisma_sheet(wb, idx, last)
        wb.save(b.HERE / name)
        print("saved", name)


if __name__ == "__main__":
    main()
