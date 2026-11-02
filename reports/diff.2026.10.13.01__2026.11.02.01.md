> new version 2026.11.02.01: 19 substantive, 1 added, 13 silent

# CR26 diff 2026.10.13.01 -> 2026.11.02.01

| added | removed | substantive | ruleset/info | mapping | baseline | force-bearing | silent | cosmetic | derived |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 19 | 0 | 0 | 0 | 0 | 13 | 0 | 0 |

## Added
- FRD:FRD-MAS

## Substantive
- FRD:FRD-CRP **SILENT**
    - `reference_url`: [-https://fedramp.gov/docs/authority/law/#b-additional-definitions-] {+https://fedramp.gov/2026/authority/law/#b-additional-definitions+}
- FRD:FRD-FCR **SILENT**
    - `reference`: FedRAMP Certification Act (44 USC § 3608) → null
    - `reference_url`: https://www.fedramp.gov/docs/authority/law/#sec-3608-federal-risk-and-authorization-management-program → null
- FRD:FRD-FCT **SILENT**
    - `reference`: FedRAMP Certification Act (44 USC § 3608) → null
    - `reference_url`: https://www.fedramp.gov/docs/authority/law/#sec-3608-federal-risk-and-authorization-management-program → null
- FRD:FRD-VLN **SILENT**
    - `reference`: ISO/IEC 27001:2022 → null
    - `reference_url`: https://www.iso.org/standard/27001 → null
- FRD:FRD-VRF **SILENT**
    - `reference`: ISO/IEC 27001:2022 → null
    - `reference_url`: https://www.iso.org/standard/27001 → null
- FRR:CDS-CSO-SVC **SILENT**
    - `terms`: +['Minimum Assessment Scope'] -[]
- FRR:CPO-CSO-OVR **SILENT**
    - `terms`: +['Minimum Assessment Scope'] -[]
- FRR:FRC-CCL-DCC
    - `notes`: +['FRC-CCL-DNP (Downgrade Notification Period) applies - please DO NOT downgrade Certification Class without providing advance notification to all necessary parties!'] -['FRC-CCL-DNP (Downgrade Notification Period) applies - please DO NOT downgrade Certification Class with providing advance notification to all necessary parties!']
- FRR:FRC-CCL-UCC
    - `notes`: +['All applicable CR26 requirements are based on the obtain deadlines in each CR26 ruleset when applying to obtain a new FedRAMP Certification, even if it is an upgrade. FedRAMP may make case-by-case exceptions based on individual circumstances and critical government need, however, so please contact FedRAMP for guidance when planning an upgrade in 2027.'] -[]
    - `statement`: Providers MUST apply for … Class; all applicable requirements {+to obtain the new FedRAMP Certification+} MUST be met in advance.
- FRR:FRC-CLA-MFR
    - `following_information`: +['Security Decision Record: SDR-CSX-KSI (Key Security Indicators)'] -[]
    - `related`: +['SDR-CSX-KSI'] -[]
    - `terms`: +['Minimum Assessment Scope', 'Security Decision Record (SDR)'] -[]
- FRR:FRC-CLA-RFR
    - `following_information`: +[] -['Certification Package Overview: CPO-CSF-CPM (Certification Package Maintenance for Rev5)']
    - `related`: +[] -['CPO-CSF-CPM']
- FRR:FRC-CSX-MAS **SILENT**
    - `terms`: +['Minimum Assessment Scope'] -[]
- FRR:IEC-CSO-FIR **SILENT**
    - `notification`: [{"party": "FedRAMP", "method": "email", "target": "fedramp_security@fedramp.gov", "name": "fedramp_security@fedramp.gov"}, {"party": "Agency Customers", "metho… → [{"party": "FedRAMP", "method": "email", "target": "fedramp_security@fedramp.gov", "name": "fedramp_security@fedramp.gov"}, {"party": "Agency Customers", "metho…
- FRR:IEC-CSO-IIR **SILENT**
    - `notification`: [{"party": "FedRAMP", "method": "email", "target": "fedramp_security@fedramp.gov", "name": "fedramp_security@fedramp.gov"}, {"party": "Agency Customers", "metho… → [{"party": "FedRAMP", "method": "email", "target": "fedramp_security@fedramp.gov", "name": "fedramp_security@fedramp.gov"}, {"party": "Agency Customers", "metho…
- FRR:IEC-CSO-OIR **SILENT**
    - `notification`: [{"party": "FedRAMP", "method": "email", "target": "fedramp_security@fedramp.gov", "name": "fedramp_security@fedramp.gov"}, {"party": "Agency Customers", "metho… → [{"party": "FedRAMP", "method": "email", "target": "fedramp_security@fedramp.gov", "name": "fedramp_security@fedramp.gov"}, {"party": "Agency Customers", "metho…
- FRR:MAS-CSO-MDI **SILENT**
    - `terms`: +['Minimum Assessment Scope'] -[]
- FRR:MAS-CSO-TPR **SILENT**
    - `terms`: +['Minimum Assessment Scope'] -[]
- FRR:MKT-CSO-PML
    - `statement`: Providers MUST notify FedRAMP using the FedRAMP Marketplace [-Providing-] {+Provider+} Listing Request Form to … in the FedRAMP Marketplace.
- KSI:KSI-SCR-MIT
    - `statement`: [-Persistently identify, review, and mitigate potential-] {+Potential+} supply chain [-risks.-] {+risks are persistently identified, reviewed, and mitigated.+}

---
*FORCE* = normative keyword or `force` changed. *SILENT* = body changed, `updated` log did not.
