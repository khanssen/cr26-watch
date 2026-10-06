> new version 2026.10.05.01: 7 substantive, 1 force-bearing

# CR26 diff 2026.09.13.02 -> 2026.10.05.01

| added | removed | substantive | ruleset/info | mapping | baseline | force-bearing | silent | cosmetic | derived |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 7 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

## Substantive
- FRR:CDS-CSO-PUB
    - `following_information`: +['Link to Product Logo (must be a valid image link, properly named, that will display in a browser without processing - transparent PNG preferred)'] -['Link to Product Logo']
    - `note`: Generally, this information should be available on a public webpage or publicly shared in a FedRAMP-compatible trust center. → null
    - `notes`: null → ["Generally, this information should be available on a public webpage or publicly shared in a FedRAMP-compatible trust center.", "The JSON data for this rule wi…
- FRR:CMU-CSO-UVM
    - `note`: null → Cryptographic modules include specific algorithms by definition; if an update stream of a cryptographic module adds new algorithms that were not previously vali…
- FRR:FRC-CSF-RDY
    - `statement`: Providers with FedRAMP Rev5 … by whichever of the [-follow-] {+following+} dates is later: the … on December 31, 2027).
- FRR:FRC-CSO-JSN **FORCE**
    - `following_information`: null → ["Cross-Origin Resource Sharing (CORS) should allow web applications running on a different domain to access the public JSON data directly.", "Proper web applic…
    - `note`: FedRAMP JSON schemas are designed to be lightweight and flexible to establish a minimum set of structured information while allowing providers to improve on the… → null
    - `notes`: null → ["FedRAMP JSON schemas are designed to be lightweight and flexible to establish a minimum set of structured information while allowing providers to improve on t…
    - `statement`: Providers MUST supply machine-readable … otherwise specified in the [-rule.-] {+rule; public JSON data MUST be supplied in a manner compatible with modern web frameworks, including:+}
    - `terms`: +['Likely'] -[]
- FRR:MKT-CAS-LRQ
    - `notification`: [{"party": "FedRAMP", "method": "form", "target": "https://help.fedramp.gov/hc/en-us/requests/new?ticket_form_id=52060327520795", "name": "[For Assessors/Adviso… → [{"party": "FedRAMP", "method": "form", "target": "https://help.fedramp.gov/hc/en-us/requests/new?ticket_form_id=52060327520795", "name": "[For Advisors] Market…
- FRR:MKT-IAS-LRQ
    - `notification`: [{"party": "FedRAMP", "method": "form", "target": "https://help.fedramp.gov/hc/en-us/requests/new?ticket_form_id=52060327520795", "name": "[For Assessors/Adviso… → [{"party": "FedRAMP", "method": "form", "target": "https://help.fedramp.gov/hc/en-us/requests/new?ticket_form_id=54220455254427", "name": "[For Assessors] Marke…
- FRR:VER-EVA-EPA
    - `following_information_bullets`: +['**N0**: Exploitation is extremely unlikely to have any adverse effects on agencies that use the cloud service offering.'] -[]
    - `statement`: Providers MUST evaluate detected … offering, to estimate the {+likely+} potential agency impact of … Agency Impact N-ratings (PAIN):
    - `terms`: +['Likely'] -[]

---
*FORCE* = normative keyword or `force` changed. *SILENT* = body changed, `updated` log did not.
