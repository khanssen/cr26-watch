# The KSI → SP 800-53 Mapping Is Not an Assessment Bridge

**Source basis:** `FedRAMP/rules` `fedramp-consolidated-rules.json` **v2026.09.13.02** (`[DATA]` figures recomputed against this version on 2026-09-24; unchanged from v2026.07.14.01). CR26 provider guidance `providers/20x/key-security-indicators/index.md`.
**Markers:** `[RULE]` = quoted or ID-cited CR26 text. `[DATA]` = computed from the JSON by a script in this repo. `[ANALYSIS]` = author position. `[UNVERIFIED]` = flagged, not yet sourced.

---

## 1. Position `[ANALYSIS]`

The KSI `controls` arrays in CR26 cannot be used to derive control-level determinations from a 20x certification. A KSI pass is not evidence that "the mapped controls are implemented," and the mapping cannot generate an SSP, a SAR, a control-level SDR, or a DoD IL4 Table D-1 package from a 20x package. The mapping is not normative, not bidirectional, and not complete. §2 and §3 show why; §4 says what it is good for.

---

## 2. What the mapping is `[DATA]` `[RULE]`

- 46 KSIs across 10 themes. 44 carry a `controls` array; `KSI-CNA-OFA` and `KSI-PIY-RES` carry none. `[DATA]`
- The 44 mapped KSIs reference **209 distinct SP 800-53 identifiers**: 113 base controls and 96 enhancements, across 17 families. **MP, PE, and PT are entirely absent.** `[DATA]`
- Among the 44 mapped KSIs, fan-out ranges from 1 to 38 controls (median 7). `KSI-IAM-JIT` maps to 38; `KSI-IAM-ELP` maps to 34. `[DATA]`
- Control fan-in: 98 of 209 controls are mapped from more than one KSI (max 6: `SC-23` ← IAM-APM, IAM-ELP, IAM-JIT, SVC-SIN, SVC-VCM, SVC-VRI). `[DATA]`
- Zero FRR rules carry a `controls` field. The process rules contribute nothing to the map. `[DATA]`
- The `CTL` section supplies FedRAMP-assigned parameter values for **14 controls (16 values)** plus 5 class-varying values on `SA-09-05`, and guidance strings for 63 controls. That is the entirety of control-level parameterization in CR26. `[DATA]`
- The mapping is labeled "Related SP 800-53 Controls" in the human-readable rules. No CR26 rule assigns it force, requires it to be used, or defines what a relation means. `[RULE]` (absence; verified by searching all `all`/`20x` FRR rules for "800-53" and "mapp". The only hit is `FRC-CLA-MFR`, which uses "mapping" to mean artifact-to-rule mapping. `FRC-CSF-BSL` also matches but is Rev5-scoped.)
- Against the Rev5 baselines CR26 itself defines (`FRC-CSF-BSL`), KSI references cover 61.3% of Class B (95 of 155), 61.8% of Class C (199 of 322), and 48.7% of Class D (199 of 409). The baselines nest (B ⊂ C ⊂ D). **None of the 87 controls Class D adds over Class C is referenced by any KSI.** MP and PE have no KSI reference in any class. Ten KSI-referenced identifiers appear in no Rev5 baseline at all. `[DATA]` (`scripts/mapping_stats.py`)
- The mapping has no change history of its own. A KSI's `updated` log does not record edits to its `controls` array, so remapping is visible only by diffing dataset versions (`scripts/diff_versions.py`, which flags such changes `SILENT`). `[DATA]`

Formal properties: `[ANALYSIS, from DATA]`

| Property | Meaning here | Consequence |
|---|---|---|
| **Non-injective** | Many controls map to multiple KSIs; many KSIs map to multiple controls | A KSI result cannot be attributed to a single control, and a control's status cannot be read from a single KSI |
| **Non-total** | 38% of Class C and 51% of Class D baseline controls are untouched, including the entire C→D increment; MP and PE absent; two KSIs map to nothing | Much of the baseline has no 20x signal at all |
| **Non-normative** | No rule requires or defines the relation; label is "Related" | Nothing in the mapping can be asserted as a requirement or a determination |
| **Unparameterized** | Only 16 (+5) ODP values exist program-wide (`CTL`) | Even a perfectly mapped control has no FedRAMP-assigned parameter to test against |
| **Not invertible** | All of the above together | There is no function from a set of KSI results to a set of control determinations. This is a structural property, not a documentation gap. |

---

## 3. What 20x actually evaluates `[RULE]`

CR26 does not evaluate 20x offerings against SP 800-53 controls. The evaluand is **FedRAMP Practices**:

- `FRD-FPR` (FedRAMP Practices): "…expressed in FedRAMP 20x Key Security Indicators **or** FedRAMP Rev5 Controls and supplemented by FedRAMP rules." The disjunction is the point: 20x = KSIs; Rev5 = controls.
- `IVV-IAS-VIM` (MUST): assessors verify that implemented measures match what the provider documented "to meet FedRAMP Practices."
- `IVV-IAS-VEF` (MUST): assessors validate effectiveness "for meeting FedRAMP Practices."
- `IVV-IAS-SUM` (MUST): the assessor summary is per **FedRAMP Practice**, meaning per KSI or rule, not per control.
- `SDR-CSX-KSI` (MUST, 20x): Security Decision Record content is per Key Security Indicator. No control field exists in the 20x SDR requirement.
- Contrast the Rev5 side: `FRC-CSF-ACP` (MUST assign all ODPs), `FRC-CSF-FFG` (MUST follow Rev5 Controls Guidance), `SDR-CSF-CTF` (per-control summaries), `IVV-CSF-MCA` (full-baseline coverage every 3 years). CR26 knows how to require a control-indexed package. It requires one only on the Rev5 path.
- Provider guidance (`providers/20x/key-security-indicators/index.md`) tells providers not to approach KSIs from a traditional compliance standpoint, rendered as a `danger` admonition. Guidance is not a rule, but it removes any doubt about intent.

`[ANALYSIS]` In a 20x engagement, the assessor's determination is a determination about KSIs. A 20x workpaper that states control-level conclusions asserts something the rules did not ask for and the evidence does not support. Under ISO/IEC 17020, that is an out-of-scope conformity statement.

---

## 4. What the mapping is good for `[ANALYSIS]`

"No purpose at all" overstates it. The mapping supports three things:

1. **Orientation.** It tells a Rev5-fluent reader roughly which security topic a KSI concerns. That is what "Related" means.
2. **Corroborating evidence, one input among several.** Where a KSI maps to a single control (e.g., `KSI-MLA-ALA` → `si-11` only), a KSI result plus its artifact is admissible as *one* input to an agency's own assessment of that control. It is neither sufficient nor independent.
3. **Monitoring signal.** `CCM` Ongoing Certification Reports and `VDR`/`VER` reports give an agency ISCM program continuous inputs it can associate with the mapped identifiers *after* the agency has done its own authorization.

It is not good for SSP generation, SAR generation, control-level SDRs, ODP inheritance, IL4/Table D-1 packages, or any statement of the form "control X is satisfied because KSI Y passed."

**For agencies:** for an agency running its own authorization process, 20x data can serve as supplementary and monitoring evidence, but it cannot serve as the assessment on which the authorization rests, for any control in the baseline.

---

## 5. Terminology note

`FRD-FPR` is FedRAMP Practices (the scope of assessment). `FRD-FRA` is FedRAMP Recognized (assessor status). They are easy to transpose; citations elsewhere should be checked.

---

## 6. Open items

- *Resolved 2026-09-24:* the earlier "~409 Moderate-baseline identifiers" figure was the Class D count, not a Moderate-sized baseline. Coverage is now computed per class from CR26's own baselines (§2).
- `[DATA]` **AGU (Agency Use)** is populated: 20 rules as of v2026.09.13.02. None defines an agency-side mapping, control inheritance, or any use of the KSI `controls` arrays; the only "control" string is the OSCAL name in `AGU-AGC-GRC`. The ruleset's own `info.status` still reads `placeholder`. The watcher flags any change to ruleset status or content (`cr26-ruleset` label). If an agency-side mapping or inheritance rule appears, §3–§4 need re-checking against it.
