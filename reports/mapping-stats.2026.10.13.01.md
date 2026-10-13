# KSI -> SP 800-53 mapping stats, CR26 2026.10.13.01

- KSIs: 46; unmapped KSIs: ['KSI-PIY-RES']
- Distinct control ids: 302 (133 base + 169 enhancements) across 16 families
- Families absent: ['MA', 'MP', 'PE', 'PT']
- Fan-out per KSI: min 0 / median 10 / max 52
- Controls mapped from >1 KSI: 142 of 302; max fan-in 9
- CTL: 79 control entries; 16 uniform parameter values; 5 class-varying values

## KSI reference coverage of the CR26 Rev5 baselines (FRC-CSF-BSL)

| Class | Baseline ids | Referenced by any KSI | No KSI reference | Families with none |
|---|---|---|---|---|
| B | 155 | 104 (67.1%) | 51 | MA, MP, PE |
| C | 322 | 243 (75.5%) | 79 | MA, MP, PE |
|  | +167 over B | 139 of the increment | 28 of the increment | |
| D | 409 | 292 (71.4%) | 117 | MA, MP, PE |
|  | +87 over C | 49 of the increment | 38 of the increment | |

- KSI-referenced ids in no Rev5 baseline: 10 (ac-2.6, at-3.5, au-3.3, ir-2.3, ir-8.1, pl-9, pm-3, pm-7, si-12.3, si-18.4)

## Top fan-in controls
- ir-9.4: 9 -> KSI-CED-RAT, KSI-CMT-VTD, KSI-CNA-DFP, KSI-CNA-EIS, KSI-IAM-ELP, KSI-MLA-LET, KSI-SVC-EIS, KSI-SVC-PRR, KSI-SVC-SIN
- sc-7.18: 8 -> KSI-CNA-EIS, KSI-CNA-IBP, KSI-CNA-MAT, KSI-CNA-RNT, KSI-CNA-RVP, KSI-SVC-ACM, KSI-SVC-PRR, KSI-SVC-SIN
- sc-23: 6 -> KSI-IAM-APM, KSI-IAM-ELP, KSI-IAM-JIT, KSI-SVC-SIN, KSI-SVC-VCM, KSI-SVC-VRI
- ac-19: 6 -> KSI-MLA-EVC, KSI-SCR-MIT, KSI-SCR-MON, KSI-SVC-PRR, KSI-SVC-VCM, KSI-SVC-VRI
- cm-2: 5 -> KSI-CMT-RMV, KSI-CNA-DFP, KSI-CNA-IBP, KSI-MLA-EVC, KSI-SVC-ACM
- ac-17.3: 5 -> KSI-CNA-IBP, KSI-CNA-MAT, KSI-CNA-RNT, KSI-CNA-ULN, KSI-IAM-ELP
- ac-20.1: 5 -> KSI-CNA-MAT, KSI-IAM-ELP, KSI-IAM-JIT, KSI-MLA-LET, KSI-MLA-OSM
- si-4.4: 5 -> KSI-CNA-RNT, KSI-IAM-SUS, KSI-MLA-LET, KSI-MLA-OSM, KSI-MLA-RVL
- sc-4: 5 -> KSI-CNA-ULN, KSI-IAM-ELP, KSI-PIY-RSD, KSI-SVC-PRR, KSI-SVC-SIN
- au-2: 4 -> KSI-CMT-LMC, KSI-MLA-LET, KSI-MLA-OSM, KSI-MLA-RVL

## Fan-out per KSI
- KSI-IAM-ELP: 52
- KSI-IAM-JIT: 51
- KSI-SCR-MIT: 31
- KSI-MLA-OSM: 22
- KSI-IAM-SUS: 20
- KSI-CED-RAT: 19
- KSI-SVC-SIN: 19
- KSI-IAM-APM: 17
- KSI-MLA-LET: 16
- KSI-RPL-ARP: 16
- KSI-CNA-MAT: 15
- KSI-SVC-ACM: 15
- KSI-PIY-RSD: 14
- KSI-SCR-MON: 14
- KSI-SVC-VRI: 14
- KSI-CNA-RNT: 13
- KSI-CNA-EIS: 12
- KSI-CNA-ULN: 12
- KSI-INR-RIR: 12
- KSI-RPL-TRC: 12
- KSI-SVC-EIS: 12
- KSI-PIY-RIS: 11
- KSI-IAM-AAM: 10
- KSI-IAM-SNU: 10
- KSI-MLA-RVL: 10
- KSI-CMT-LMC: 9
- KSI-INR-RPI: 9
- KSI-PIY-GIV: 9
- KSI-CMT-RMV: 7
- KSI-MLA-EVC: 7
- KSI-SVC-VCM: 7
- KSI-CMT-RVP: 6
- KSI-CMT-VTD: 6
- KSI-INR-AAR: 6
- KSI-SVC-ASM: 6
- KSI-CNA-DFP: 5
- KSI-CNA-RVP: 5
- KSI-RPL-ABO: 5
- KSI-SVC-PRR: 5
- KSI-SVC-RUD: 5
- KSI-CNA-IBP: 4
- KSI-MLA-ALA: 3
- KSI-CNA-OFA: 2
- KSI-RPL-RRO: 2
- KSI-PIY-RVD: 1
- KSI-PIY-RES: 0
