# Project Instruction: The KSI → SP 800-53 Mapping Is Not the Answer

**Status:** Standing instruction for all conversations in this project.
**Source basis:** `FedRAMP/rules` `fedramp-consolidated-rules.json` v2026.07.14.01 (pushed 2026-08-13); CR26 provider guidance `providers/20x/key-security-indicators/index.md`.
**Marker legend:** `[RULE]` = quoted or ID-cited CR26 text. `[DATA]` = computed from the JSON with a parser. `[ANALYSIS]` = firm position. `[UNVERIFIED]` = flagged, not yet sourced.

---

## 1. The instruction

When any question in this project touches how a FedRAMP 20x certification relates to NIST SP 800-53 controls, Claude does **not**:

- Propose the KSI `controls` mapping as a way to derive control-level determinations from KSI results.
- Describe a KSI pass as evidence that "the mapped controls are implemented."
- Suggest that an agency, assessor, or provider "use the mapping" to produce an SSP, SAR, control-level SDR, or IL4 Table D-1 package from a 20x package.
- Treat the mapping as normative, bidirectional, or complete.
- Re-derive any of this from scratch. The facts below are settled for this project; cite this file and move on.

When a user (including Karen) proposes the mapping as a bridge, Claude says so directly and points to §3 below.

---

## 2. What the mapping is `[DATA]` `[RULE]`

- 46 KSIs across 10 themes. 44 carry a `controls` array; `KSI-CNA-OFA` and `KSI-PIY-RES` carry none. `[DATA]`
- The 44 mapped KSIs reference **209 distinct SP 800-53 identifiers**: 113 base controls and 96 enhancements, across 17 families. **MP, PE, and PT are entirely absent.** `[DATA]`
- KSI fan-out ranges from 1 to 38 controls per KSI (median 7). `KSI-IAM-JIT` maps to 38; `KSI-IAM-ELP` maps to 34. `[DATA]`
- Control fan-in: 98 of 209 controls are mapped from more than one KSI (max 6: `SC-23` ← IAM-APM, IAM-ELP, IAM-JIT, SVC-SIN, SVC-VCM, SVC-VRI). 111 controls are mapped from exactly one KSI. `[DATA]`
- Zero FRR rules carry a `controls` field. The process rules contribute nothing to the map. `[DATA]`
- The `CTL` section supplies FedRAMP-assigned parameter values for **14 controls (16 values)** plus 5 class-varying values on `SA-09-05`, and guidance strings for 63 controls. That is the entirety of control-level parameterization in CR26. `[DATA]`
- The mapping is labeled "Related SP 800-53 Controls" in the human-readable rules. No CR26 rule assigns it force, requires it to be used, or defines what a relation means. `[RULE]` (absence; verified by search of all `all`/`20x` FRR rules for "800-53" and "mapp" — only hit is `FRC-CLA-MFR`, which uses "mapping" to mean artifact-to-rule mapping, not control mapping.)

Formal properties, stated once so they need not be re-argued: `[ANALYSIS, from DATA]`

| Property | Meaning here | Consequence |
|---|---|---|
| **Non-injective** | Many controls map to multiple KSIs; many KSIs map to multiple controls | A KSI result cannot be attributed to a single control, and a control's status cannot be read from a single KSI |
| **Non-total** | ~200 of ~409 Moderate-baseline identifiers are untouched; three families absent; two KSIs map to nothing | Roughly half the baseline has no 20x signal at all |
| **Non-normative** | No rule requires or defines the relation; label is "Related" | Nothing in the mapping can be asserted as a requirement or a determination |
| **Unparameterized** | Only 16 (+5) ODP values survive program-wide (`CTL`) | Even a perfectly mapped control has no FedRAMP-assigned parameter to test against |
| **Not invertible** | All of the above together | There is no function from a set of KSI results to a set of control determinations. This is a structural property, not a documentation gap. |

---

## 3. What 20x actually evaluates `[RULE]`

CR26 does not evaluate 20x offerings against SP 800-53 controls. The evaluand is **FedRAMP Practices**, and the rules are explicit about it:

- `FRD-FPR` (FedRAMP Practices): "…expressed in FedRAMP 20x Key Security Indicators **or** FedRAMP Rev5 Controls and supplemented by FedRAMP rules." The disjunction is the whole point: 20x = KSIs; Rev5 = controls. There is no path where 20x = controls.
- `IVV-IAS-VIM` (MUST): assessors verify that implemented measures match what the provider documented "to meet FedRAMP Practices."
- `IVV-IAS-VEF` (MUST): assessors validate effectiveness "for meeting FedRAMP Practices."
- `IVV-IAS-SUM` (MUST): the assessor summary is per **FedRAMP Practice**, i.e., per KSI or rule — not per control.
- `SDR-CSX-KSI` (MUST, 20x): the Security Decision Record content is per Key Security Indicator: measures, cycle, verification, automation, validation. No control field exists in the 20x SDR requirement.
- Contrast the Rev5 side of the same rules: `FRC-CSF-ACP` (MUST assign all ODPs and document in SDR), `FRC-CSF-FFG` (MUST follow Rev5 Controls Guidance), `SDR-CSF-CTF` (per-control summaries), `IVV-CSF-MCA` (full-baseline coverage every 3 years). CR26 knows how to require a control-indexed package. It requires one only on the Rev5 path, which closes to new certifications on **June 11, 2027**.
- Provider guidance (`providers/20x/key-security-indicators/index.md`): "FedRAMP 20x works differently than a traditional compliance approach by asking cloud service providers to demonstrate desired security capabilities instead of telling them to meet specific security requirements," and: **"Do not attempt to approach Key Security Indicators from a traditional compliance standpoint!"** (rendered as a `danger` admonition). Guidance is T4, not a rule, but it removes any doubt about intent.

`[ANALYSIS]` Net: the assessor's determination in a 20x engagement is a determination about KSIs. An assessor who writes control-level conclusions in a 20x workpaper is asserting something the rules did not ask for and the evidence does not support. Under ISO 17020 that is an out-of-scope conformity statement.

---

## 4. What the mapping is good for (and only this) `[ANALYSIS]`

To prevent over-correction — "absolutely no purpose" is an overreach a reviewer will exploit:

1. **Orientation.** It tells a Rev5-fluent reader roughly which security topic a KSI is about. That is what "Related" means.
2. **Corroborating evidence, one piece among several.** Where a KSI maps to a single control (e.g., `KSI-MLA-ALA` → `si-11` only), a KSI result plus its artifact is admissible as *one* input to an agency's own assessment of that control — same standing as a vendor screenshot. Not sufficient, not independent in the §3613(e) sense.
3. **Monitoring signal.** `CCM` OCRs and `VDR`/`VER` reports give an agency ISCM program continuous inputs it can associate with the ~200 mapped identifiers *after* the agency has done its own authorization.

It is not good for: SSP generation, SAR generation, control-level SDRs, ODP inheritance, IL4/Table D-1 packages, or any statement of the form "control X is satisfied because KSI Y passed."

---

## 5. Standing consequences for project work

- **Structural critique (`cr26-structural-analysis.md`):** the mapping finding is closed. Cite this file. New work goes to *consequences* (agency authorization gap, CC SRG path, §3613(e) scope), not to re-establishing the mapping's properties.
- **Class C workpapers (`classc-workpapers.html`):** determinations are per KSI, gated on mechanisms. No control-level fields. If a client asks for control mapping in the workpaper, that is a separate, out-of-scope, fee-bearing deliverable and it is labeled as firm analysis, not assessment result.
- **Rosetta:** the product thesis rests on §2–§3. Rosetta produces control-indexed, parameterized, benchmark-anchored evidence *from the provider's implementation*, not from the KSI results. The 20x certification is a byproduct. Any design that starts from the mapping is starting from the wrong end.
- **Agency-facing content:** the sentence to use is: *for an agency running its own authorization process, 20x data can serve as supplementary and monitoring evidence but cannot serve as the assessment on which the authorization rests, for any control in the baseline.*
- **Pricing (`KHS_Estimates_2.xlsx`):** LOE is scoped to 92 KSI-slots and the mechanism registry. Control mapping is not in the base LOE.

---

## 6. Corrections to prior project notes `[ANALYSIS]`

- Prior notes cite "`FRD-FRP` bounds assessor scope to KSIs." The definition ID is **`FRD-FPR`** (FedRAMP Practices). `FRD-FRA` is "FedRAMP Recognized" (assessor status), which is the correct cite for the accreditation-anchor finding. Both should be checked wherever they appear.
- Prior notes describe the mapping as non-injective, non-total, non-normative. Confirmed by `[DATA]` above; add **unparameterized** and **not invertible** as the operative consequences.

---

## 7. Open items `[UNVERIFIED]`

- The "~409 baseline identifiers" figure is from prior project work, not recomputed here against a Moderate baseline file. Recompute when the OSCAL Moderate profile is loaded; the ~50% coverage claim depends on it.
- `AGU` (Agency Use of FedRAMP Certified Cloud Services) is `status: placeholder`. If PMO fills it with an agency-side mapping or inheritance rule, §3–§4 need re-checking against that text. Monitor the `FedRAMP/rules` repo `updated` history for `AGU-*`.
- The mapping itself has no `updated` history separate from the KSI. Changes to `controls` arrays are only detectable by diffing JSON versions. Keep a copy of each version.
