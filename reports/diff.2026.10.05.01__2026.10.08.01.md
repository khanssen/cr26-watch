> new version 2026.10.08.01: 2 substantive, 1 removed, 1 force-bearing

# CR26 diff 2026.10.05.01 -> 2026.10.08.01

| added | removed | substantive | ruleset/info | mapping | baseline | force-bearing | silent | cosmetic | derived |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

## Removed
- FRR:FRC-CSX-MOT

## Substantive
- FRD:FRD-SNT
    - `definition`: There may exist valid … full implications must be [-understand-] {+understood+} and carefully weighed. Parties … they handle such rules.
- FRR:SDR-CSX-KMT **FORCE**
    - `note`: null → For initial FedRAMP Certification, providers will need to have mechanisms in place and agree to meet this requirement in the event the cloud service has not bee…
    - `terms`: +['Initial Certification'] -[]
    - `varies_by_class.b.force`: [-MUST-] {+SHOULD+}
    - `varies_by_class.b.statement`: Providers with 20x Class B Certifications [-MUST-] {+SHOULD+} also include historical metrics … applicable Key Security Indicator:
    - `varies_by_class.c.following_information`: +['All daily metric data (including status of persistent validation) up to the past year (where available)'] -['All daily metric data up to the past year (where available)']

---
*FORCE* = normative keyword or `force` changed. *SILENT* = body changed, `updated` log did not.
