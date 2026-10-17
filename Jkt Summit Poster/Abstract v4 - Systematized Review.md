---
type: project
status: draft
date: 2026-10-17
deadline: 2026-10-21
tags: [project, poster, perdoki, systematized-review, abstract]
---
# Abstract v4: systematized review (13 included studies)

Revision of `Abstract v3 - Systematized Review.md` (vault, `Projects/Poster Ilmiah - Jakarta 1st Summit/`) after Council Review 3 (2026-10-17, OccMed + Researcher hats). Submission: OEMJI ScholarHub, Supplement Issue, deadline **extended to 2026-10-21**; abstract limit 255 words incl. bold subheadings, title limit 250 characters, 3-5 keywords in alphabetical order, no references, no author or institution names in the PDF. Poster upload only after acceptance (after 21 Oct). Diagram: `PRISMA Flow v2.drawio` (this folder).

## Title (108 characters, unchanged; decision open)
**AI Decision Support in Periodic Occupational Health Examinations: A Systematized Review of Evidence and Gaps**

Option raised by two councils (included studies are not all periodic: Moore claimants, Priego-Torres and Dong clinic cohorts, Charapaqui-Miranda work-entry; and the studies test reading accuracy, not decision support):
**Artificial Intelligence for Interpreting Occupational Health Examination Tests: A Systematized Review of Evidence and Gaps** (124 characters)

## Abstract (253 words including the five subheadings; limit 255)

**Introduction** Periodic occupational health examinations generate large volumes of routine test results. Whether artificial intelligence (AI) can validly interpret these results remains unclear.

**Methods** This systematized review followed PRISMA 2020 reporting. PubMed, Scopus, ProQuest and IEEE Xplore were searched on 5 October 2026 for studies (2006 onwards) in which AI interpreted occupational examination tests of workers or ex-workers against a physician or clinically validated reference. Models forecasting future disease were excluded. Study quality was appraised with the JBI diagnostic test accuracy checklist.

**Results** From 861 records screened, 13 studies were included evaluating AI in chest radiography (n=9), audiometry (n=1), electrocardiography (n=1), and multimodal examination records (n=2). No spirometry or laboratory study met the criteria. None came from Southeast Asia. Imaging area under the curve (AUC) ranged from 0.84 to 1.00, highest in case-control designs; sensitivity (62–100%) and specificity (46–98%) varied with threshold. Only two enrolled consecutive samples, three performed external validation, two reported negative predictive value, none evaluated AI prospectively, and eight were rated high concern on appraisal.

**Discussion** Evidence is concentrated in chest radiography for dust-related disease, mostly from enriched datasets that likely overstate screening performance. Two studies used physicians' fit/unfit status as the reference, both weakly (AUC 0.60; one physician rating documents). None assessed fitness to work against actual job demands.

**Conclusion** Evidence is insufficient to support AI interpretation in routine periodic examinations; AI should remain decision support under physician responsibility. Adoption requires external validation in unselected worker populations, negative predictive value reporting, comparison with occupational physicians' determinations, and prospective evaluation.

**Keywords:** artificial intelligence; chest radiography; clinical decision support; occupational health surveillance; pneumoconiosis

## Changes from v3
| v3 | v4 | Why |
|---|---|---|
| "the clinical validity of AI as an interpretive tool has yet to be established" | "Whether AI can validly interpret these results remains unclear" | v3 stated the conclusion before the Methods |
| "AI analysed current examination results of workers" | "AI interpreted occupational examination tests of workers or ex-workers" | Matches the 2026-10-07 population rule (ex-miners, ex-military, clinic and claims settings) |
| "Prediction models were excluded" | "Models forecasting future disease were excluded" | To a general reader every classifier "predicts" |
| "multimodal data" | "multimodal examination records" | Says what the data are |
| "No studies originated from Southeast Asia" | "None came from Southeast Asia" | Shorter; same claim |
| "AI model area under the curve (AUC) ranged from 0.84 to 1.00, with highly variable sensitivity … and specificity …" | "AUC ranged from 0.84 to 1.00, highest in case-control designs; sensitivity … and specificity … varied with threshold" | The top values (Priego-Torres 1.00, Young 0.986, Dong 0.98, He 0.962) all have JBI Q2 = N; the Se/Sp extremes are different operating points (Liu Sp 46% is its high-sensitivity mode) |
| "Methodological quality was subpar: all were retrospective, …" | "Only two enrolled consecutive samples, …, none evaluated AI prospectively, …" | Restores the 2026-10-07 correction (Dong 2022 and part of Priego-Torres 2025 collected images prospectively); "subpar" is a judgement word; Q1 = Y only in Heo and Ehrlich |
| "two reported negative predictive values" | "two reported negative predictive value" | Grammar |
| "enriched datasets that overstate" | "that likely overstate" | Not measured in the review |
| "Only two studies compared AI with physicians' fit/unfit decisions, both weak (AUC 0.60 and one physician, documents only). No study addressed fitness-to-work assessment, which requires job-specific evaluation." | "Two studies used physicians' fit/unfit status as the reference, both weakly (AUC 0.60; one physician rating documents). None assessed fitness to work against actual job demands." | Removes the contradiction (Vella did make fitness judgements, from documents only) and states the MCU-status vs fitness-to-work difference |
| "insufficient evidence to support AI  for routine periodic examinations and AI should remain …" | "Evidence is insufficient to support AI interpretation in routine periodic examinations; AI should remain …" | Double space; grammar |
| "validation against physicians' decisions, routine reporting of negative predictive value and external validation, and prospective implementation" | "external validation in unselected worker populations, negative predictive value reporting, comparison with occupational physicians' determinations, and prospective evaluation" | Separates reading accuracy (external validation, unselected spectrum, NPV) from decision agreement (Sp.Ok determinations) |
| Keywords: artificial intelligence; clinical decision support; chest radiography; … | artificial intelligence; chest radiography; clinical decision support; … | Alphabetical order is a submission rule |

## Number check (all from the extraction and appraisal notes)
| Claim | Source |
|---|---|
| 1,278 identified, 417 duplicates, 861 screened, 23 sought, 3 not retrieved, 20 assessed, 7 excluded, 13 included | PRISMA table / workbook sheet "Full text" |
| Chest radiography 9, audiometry 1, ECG 1, multimodal 2 | Table 1 |
| No spirometry or laboratory study | Synthesis, "Modality"; laboratory terms not in the strings, supplementary PubMed check found none (Keywords note, gap check) |
| AUC 0.84–1.00 (imaging) | Ehrlich 0.839 (lowest), Priego-Torres 1.00 (highest) |
| "highest in case-control designs" | Priego-Torres 1.00, Young 0.986, Dong 0.98, He 0.962: all JBI Q2 = N. Heo 0.92 (Q2 = Y) is next |
| Imaging Se 62–100%, Sp 46–98% | Wang 2020 Se 62.3; Li 2024 (derived) and Priego-Torres Se 100; Liu 2026 Sp 46 (high-sensitivity mode); Young 98.2 |
| Two enrolled consecutive samples | JBI Q1 = Y: Heo 2019, Ehrlich 2022 |
| External validation 3/13, NPV 2/13, no prospective AI evaluation | Synthesis, "Validation" and "Safety-critical reporting" |
| High concern 8/13 | Appraisal: Low 1, Moderate 4, High 8 |
| Two studies with a physician fit/unfit reference | Charapaqui-Miranda 2020 (AUC 0.60); Vella 2026 (one physician, documents only, kappa 1.00) |

Word count: 253 (whitespace tokens, subheadings included, keywords excluded). Recount in the submission form, which may count differently.

## Q&A preparation (from Council Review 3)
- **"Did you re-screen the 386 title/abstract E1 exclusions under the new population rule?"** No. The rule was set at full text on 2026-10-07; this is a limitation, and a re-screen is planned for the paper.
- **"Moore's reference is group membership, not a diagnosis."** Yes: claimants with a medical report excluding other causes vs noise-screened controls; rated JBI Q6 = N and High concern.
- **"Why is the ECG study (3/10) Moderate but Charapaqui-Miranda (5/10) High?"** The overall-concern rule is item-based, not a sum: Q10 = N (8% of records analysed) and Q3 = N force High; the ECG study's items are mostly unclear, not negative.
- **"AUC 1.00?"** Priego-Torres: image-level cross-validation (the same patient can sit in training and validation) with public VinDr controls from Vietnam.
- **"Why is Charapaqui-Miranda not a prediction model?"** It classifies the current examination result into the examining doctor's fit/unfit category; it does not forecast a future outcome.
- **Reference standards differ** (ILO B-readers, radiologist panels, China GBZ 70-2015, group membership, single physician), so ranges are descriptive and were not pooled.

## Still open
1. Title: keep, or switch to the option above.
2. Workbook `Screening_TA_master.xlsx` sheet "Full text": Smesseim 2025 reason E1 → E10 to match `PRISMA Flow v2.drawio`.
3. Vault notes (Abstract v3, Data Extraction, PRISMA Flow.drawio) still show the v3 text and Smesseim as E1.
4. Poster (after acceptance): footnote AUC 1.00/0.98; "Li 2024 NPV derived, not reported"; MCU status ≠ fitness to work box; disclose AI-assisted appraisal drafting and Li 2024's developer conflict.
