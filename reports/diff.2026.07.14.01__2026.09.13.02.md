> new version 2026.09.13.02: 12 substantive, 2 ruleset, 5 added, 1 force-bearing, 10 silent, 1 cosmetic, 233 derived
> Regenerated 2026-09-24 with the revised diff (ruleset metadata, full-body comparison). The original report listed only 5 added definitions and 2 statement changes.

# CR26 diff 2026.07.14.01 -> 2026.09.13.02

| added | removed | substantive | ruleset/info | mapping | baseline | force-bearing | silent | cosmetic | derived |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | 12 | 2 | 0 | 0 | 1 | 10 | 1 | 233 |

## Ruleset / dataset metadata
- SET:FRR/CPO
    - `rev5.effective.date.grace.default`: [-2027-01-01-] {+2027-07-01+}
    - `rev5.subsets.CSF.applicability.classes`: +[] -['A']
- SET:FRR/FRC
    - `subsets.CCL.applicability.classes`: +[] -['A']

## Added
- FRD:FRD-MAY
- FRD:FRD-MNT
- FRD:FRD-MST
- FRD:FRD-SHD
- FRD:FRD-SNT

## Substantive
- FRD:FRD-ADV **SILENT**
    - `ignore_in_terms`: null → true
- FRD:FRD-AGY **SILENT**
    - `ignore_in_terms`: null → true
- FRD:FRD-ASR **SILENT**
    - `ignore_in_terms`: null → true
- FRD:FRD-PRV **SILENT**
    - `ignore_in_terms`: null → true
- FRR:AGU-AGC-LIA
    - `reference_url`: [-https://www.fedramp.gov/preview/2026/agencies/support/liaisons-] {+https://www.fedramp.gov/2026/agencies/support/liaisons+}
    - `terms` *(derived)*: -['Agency']
- FRR:AGU-USE-ABU **SILENT**
    - `reference_url`: [-https://fedramp.gov/preview/2026/agencies/use-] {+https://www.fedramp.gov/2026/agencies/use+}
    - `terms` *(derived)*: -['Agency']
- FRR:CCM-OCR-AVL **FORCE**
    - `statement`: Providers MUST supply an … at least the following [-information:-] {+information (if applicable):+}
    - `terms` *(derived)*: -['Agency', 'Provider']
    - `timeframe_num`: null → 3
    - `timeframe_type`: null → months
- FRR:CCM-QTR-SAR **SILENT**
    - `terms` *(derived)*: -['Provider']
    - `timeframe_num_max`: null → 10
    - `timeframe_num_min`: null → 3
    - `timeframe_type`: null → bizdays
- FRR:IVV-CSF-MCA **SILENT**
    - `terms` *(derived)*: -['Provider']
    - `timeframe_num`: null → 3
    - `timeframe_type`: null → years
- FRR:MKT-CAS-RFR **SILENT**
    - `terms` *(derived)*: -['Advisor']
    - `timeframe_num`: null → 5
    - `timeframe_type`: null → bizdays
- FRR:MKT-IIP-DLA **SILENT**
    - `terms` *(derived)*: -['Provider']
    - `timeframe_num`: null → 2
    - `timeframe_type`: null → years
- FRR:VDR-TFR-NMV **SILENT**
    - `terms` *(derived)*: -['Provider']
    - `timeframe_num`: null → 3
    - `timeframe_type`: null → months

## Cosmetic (normalized text identical)
- FRR:IEC-CSO-OIR
    - `terms` *(derived)*: -['Provider']
    - `varies_by_class.a.statement` *(cosmetic)*: Providers with Class A … as much of the [-the-] following additional information that … status for each item:
    - `varies_by_class.b.statement` *(cosmetic)*: Providers with Class B … as much of the [-the-] following additional information that … status for each item:
    - `varies_by_class.c.statement` *(cosmetic)*: Providers with Class C … as much of the [-the-] following additional information that … status for each item:
    - `varies_by_class.d.statement` *(cosmetic)*: Providers with Class D … as much of the [-the-] following additional information that … status for each item:

## Derived
- 233 items: `terms` lost only ['Advisor', 'Agency', 'Assessor', 'MAY', 'MUST', 'MUST NOT', 'Provider', 'SHOULD', 'SHOULD NOT'] (definitions newly flagged `ignore_in_terms`). No other field changed on these items.

---
*FORCE* = normative keyword or `force` changed. *SILENT* = body changed, `updated` log did not.
