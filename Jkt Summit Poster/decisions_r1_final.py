# Final title/abstract decisions after review-lead edits (2026-10-05).
# 1) Review lead's own decisions made directly in Screening_TA_master.xlsx
#    (reason codes added here).
# 2) Prediction rule (E4, widened): the review is about AI that ANALYSES
#    medical check-up data (classifies/detects the current exam result against
#    a reference). Risk, susceptibility, early-warning or future-outcome
#    prediction models are excluded.
# 3) Date rule (E8): published before 2006 (more than 20 years old).
# Applied on top of decisions_r1 / decisions_r1_v2 / decisions_r1_refine.

LEAD = {  # review lead's edits in the workbook
    53: ("E", "E7", "Lead: threshold analysis of published CAD data; no new diagnostic evaluation"),
    84: ("E", "E4", "Lead: NIHL susceptibility prediction"),
    86: ("E", "E4", "Lead: hearing-loss prediction equation"),
    119: ("E", "E4", "Lead: CWP prediction from clinical data"),
    159: ("E", "E7", "Lead: factor analysis of medical capability, no diagnostic reference"),
    182: ("E", "E4", "Lead: COPD risk assessment model"),
    205: ("E", "E3", "Lead: acoustic spiroanalyser, not routine check-up data"),
    211: ("E", "E4", "Lead: hearing-loss prediction"),
    227: ("E", "E4", "Lead: NIHL risk prediction model"),
    244: ("E", "E4", "Lead: high-risk population early-warning model"),
    245: ("E", "E4", "Lead: fitness-for-work risk stratification / predictor identification"),
    275: ("E", "E7", "Lead: efficiency simulation of claims triage, no diagnostic accuracy"),
    282: ("E", "E1", "Lead: population not described"),
    304: ("E", "E4", "Lead: ONIHL risk-factor prediction"),
    313: ("E", "E4", "Lead: predictive tools, no abstract"),
    326: ("E", "E4", "Lead: preclinical CWP prediction / individual risk evaluation"),
    344: ("E", "E4", "Lead: ONIHL risk prediction model"),
    365: ("E", "E4", "Lead: early pneumoconiosis risk prediction model"),
    389: ("E", "E4", "Lead: black lung prediction (longitudinal incidence)"),
    390: ("E", "E4", "Lead: abnormal lung function risk assessment model"),
    434: ("E", "E7", "Lead: reference is a fatigue questionnaire, not a clinical diagnosis"),
    449: ("E", "E4", "Lead: pneumoconiosis risk prediction model"),
    498: ("E", "E7", "Lead: association/causal analysis, no diagnostic reference"),
    528: ("E", "E4", "Lead: hearing-loss change prediction"),
    579: ("E", "E4", "Lead: CWP risk prediction model"),
    584: ("E", "E4", "Lead: lung ventilation dysfunction risk prediction"),
    638: ("E", "E1", "Lead: hospital DR data, not a check-up population"),
    713: ("E", "E4", "Lead: NIHL prediction"),
    122: ("I", "", "Lead: AI on CT (+DLCO) vs pulmonologist panel, workers applying for asbestosis aid"),
    224: ("I", "", "Lead: computer vs experts on pneumoconiosis screening films"),
    247: ("I", "", "Lead: OASYS expert system for serial PEF in workers"),
    269: ("I", "", "Lead: OASYS-2 computer diagnostic aid for workers' PEF"),
    272: ("I", "", "Lead: computer classification of profusion on coal workers' radiographs"),
    358: ("I", "", "Lead: prospective validation of AI asbestosis assessment (Se/Sp/PPV/NPV)"),
    472: ("I", "", "Lead: computer-aided disability scoring vs expert assessment, silicosis"),
}

PREDICTION = {  # remaining I/M that are risk/prediction models
    588: ("E", "E4", "Hearing-loss risk assessment models"),
    663: ("E", "E4", "High-frequency hearing loss RISK prediction model"),
}

DATE_CUTOFF = 2006  # E8 for year < 2006
