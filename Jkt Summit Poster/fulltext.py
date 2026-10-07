# Full-text stage. Keyed by record number.
# Decisions from the full-text screening done 2026-10-05/06 (recorded in the vault note
# "Systematized Review - Data Extraction and Analysis"), with the review lead's corrections:
# 2026-10-06: abstract-only records are not included (they cannot be appraised) and
# reports whose full text could not be obtained are "Not retrieved".
# 2026-10-07: population is judged together with the index test. Workers or ex-workers examined
# with a test used in periodic occupational examinations are eligible even when the data come from
# an occupational-disease clinic or a claims setting (Moore 2023, Priego-Torres 2025, Dong 2022 now
# included); CT/HRCT is not a periodic-examination test (E10).
# status: "Retrieved" | "Not retrieved"; decision: "Include" | "Exclude"; reason: E-codes.
FT = {
    # Included (13)
    173: ("Retrieved", "Include", "", "Heo 2019: CXR TB, annual statutory worker surveillance"),
    41: ("Retrieved", "Include", "", "Wang 2020: CXR pneumoconiosis, dust-exposed screening setting"),
    46: ("Retrieved", "Include", "", "Young 2020: CAD silicosis/TB, gold miners"),
    652: ("Retrieved", "Include", "", "Charapaqui-Miranda 2020: work-entry MCU fit/unfit category (Peru)"),
    225: ("Retrieved", "Include", "", "Ehrlich 2022: CAD silicosis/TB, ex-miner screening days"),
    42: ("Retrieved", "Include", "", "Wang 2022/2023: CNN ECG, coal workers' periodic exams"),
    40: ("Retrieved", "Include", "", "Li 2024: CXR pneumoconiosis, dust-exposed workers"),
    131: ("Retrieved", "Include", "", "Liu 2026: CXR, US workers, B-reader consensus"),
    606: ("Retrieved", "Include", "", "He 2026: ViT CXR, dust-exposed workers screened at CDC"),
    410: ("Retrieved", "Include", "", "Vella 2026: LLM vs occupational physician, document-based fitness judgements"),
    50: ("Retrieved", "Include", "", "Moore 2023: audiometry MLP, military-service NIHL (veterans' claims vs controls); lead decision 2026-10-07, earlier E1"),
    179: ("Retrieved", "Include", "", "Priego-Torres 2025: CXR silicosis screening, engineered-stone workers; lead decision 2026-10-07, earlier E1"),
    310: ("Retrieved", "Include", "", "Dong 2022: CXR CWP imaging features, coal workers' cohort; lead decision 2026-10-07, earlier E1"),
    # Excluded at full text (7)
    181: ("Retrieved", "Exclude", "E10", "Dong 2025: HRCT, not a periodic-examination test"),
    122: ("Retrieved", "Exclude", "E10", "Groot Lipman 2023: CT for asbestosis, not a periodic-examination test"),
    358: ("Retrieved", "Exclude", "E1", "Smesseim 2025: compensation applicants, not workers at a periodic examination (also CT)"),
    405: ("Retrieved", "Exclude", "E4", "Prediction model of preclinical CWP"),
    813: ("Retrieved", "Exclude", "E4", "Metabolic syndrome prediction model"),
    507: ("Retrieved", "Exclude", "E7", "Ceramic workers: no reference-standard performance"),
    653: ("Retrieved", "Exclude", "E9", "Jacobs 2014: micronodule CAD for grading/quantification, not screening"),
    # Not retrieved (3)
    101: ("Not retrieved", "", "", "JOEM (Wolters Kluwer) not subscribed at UI; not open access; ProQuest/EBSCOhost searched"),
    352: ("Not retrieved", "", "", "Cui 2023: Chinese journal not subscribed at UI; abstract only, cannot be appraised"),
    578: ("Not retrieved", "", "", "SPIE conference paper; SPIE Digital Library not subscribed at UI; full text not found"),
}

EXTRA_REASONS = [
    ("E9", "Grading/quantification task, not screening/detection at a check-up"),
    ("E10", "Index test not used in periodic occupational examinations (CT/HRCT)"),
]

FT_POPULATION_RULE = (
    "Applied at full text (review lead, 2026-10-07): workers or ex-workers with occupational exposure, examined "
    "with a test that is part of periodic or pre-placement occupational examinations (chest radiograph, audiometry, "
    "spirometry, ECG, laboratory, examination records). Data may come from screening or surveillance programmes, "
    "occupational-disease clinics or claims assessments. CT/HRCT -> E10. Compensation applicants not examined "
    "as workers -> E1."
)
