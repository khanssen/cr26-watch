# KSI -> SP 800-53 mapping stats, CR26 2026.09.13.02

- KSIs: 46; unmapped KSIs: ['KSI-CNA-OFA', 'KSI-PIY-RES']
- Distinct control ids: 209 (113 base + 96 enhancements) across 17 families
- Families absent: ['MP', 'PE', 'PT']
- Fan-out per KSI: min 0 / median 7 / max 38
- Controls mapped from >1 KSI: 98 of 209; max fan-in 6
- CTL: 79 control entries; 16 uniform parameter values; 5 class-varying values

## KSI reference coverage of the CR26 Rev5 baselines (FRC-CSF-BSL)

| Class | Baseline ids | Referenced by any KSI | No KSI reference | Families with none |
|---|---|---|---|---|
| B | 155 | 95 (61.3%) | 60 | MP, PE |
| C | 322 | 199 (61.8%) | 123 | MP, PE |
|  | +167 over B | 104 of the increment | 63 of the increment | |
| D | 409 | 199 (48.7%) | 210 | MP, PE |
|  | +87 over C | 0 of the increment | 87 of the increment | |

- KSI-referenced ids in no Rev5 baseline: 10 (ac-2.6, at-3.5, au-3.3, ir-2.3, ir-8.1, pl-9, pm-3, pm-7, si-12.3, si-18.4)

## Top fan-in controls
- sc-23: 6 -> KSI-IAM-APM, KSI-IAM-ELP, KSI-IAM-JIT, KSI-SVC-SIN, KSI-SVC-VCM, KSI-SVC-VRI
- cm-2: 5 -> KSI-CMT-RMV, KSI-CNA-DFP, KSI-CNA-IBP, KSI-MLA-EVC, KSI-SVC-ACM
- ac-17.3: 5 -> KSI-CNA-IBP, KSI-CNA-MAT, KSI-CNA-RNT, KSI-CNA-ULN, KSI-IAM-ELP
- ac-20.1: 5 -> KSI-CNA-MAT, KSI-IAM-ELP, KSI-IAM-JIT, KSI-MLA-LET, KSI-MLA-OSM
- au-2: 4 -> KSI-CMT-LMC, KSI-MLA-LET, KSI-MLA-OSM, KSI-MLA-RVL
- cm-3: 4 -> KSI-CMT-LMC, KSI-CMT-RMV, KSI-CMT-RVP, KSI-CMT-VTD
- cm-6: 4 -> KSI-CMT-LMC, KSI-CMT-RMV, KSI-MLA-EVC, KSI-SVC-ACM
- cm-7.1: 4 -> KSI-CMT-RVP, KSI-CNA-RNT, KSI-SVC-ACM, KSI-SVC-EIS
- sc-4: 4 -> KSI-CNA-ULN, KSI-IAM-ELP, KSI-PIY-RSD, KSI-SVC-PRR
- ia-5.2: 4 -> KSI-IAM-APM, KSI-IAM-ELP, KSI-IAM-SNU, KSI-SVC-ASM

## Fan-out per KSI
- KSI-IAM-JIT: 38
- KSI-IAM-ELP: 34
- KSI-MLA-OSM: 18
- KSI-RPL-ARP: 16
- KSI-CNA-MAT: 14
- KSI-IAM-APM: 13
- KSI-PIY-RSD: 12
- KSI-SCR-MIT: 12
- KSI-SVC-SIN: 12
- KSI-CED-RAT: 11
- KSI-SVC-ACM: 11
- KSI-INR-RIR: 10
- KSI-MLA-LET: 10
- KSI-RPL-TRC: 10
- KSI-SCR-MON: 10
- KSI-IAM-AAM: 9
- KSI-PIY-RIS: 9
- KSI-SVC-EIS: 9
- KSI-CNA-ULN: 8
- KSI-CMT-LMC: 7
- KSI-CMT-RMV: 7
- KSI-IAM-SNU: 7
- KSI-IAM-SUS: 7
- KSI-MLA-RVL: 7
- KSI-PIY-GIV: 7
- KSI-SVC-VRI: 7
- KSI-CMT-RVP: 6
- KSI-RPL-ABO: 6
- KSI-CNA-RNT: 5
- KSI-INR-RPI: 5
- KSI-SVC-ASM: 5
- KSI-CMT-VTD: 4
- KSI-INR-AAR: 4
- KSI-MLA-EVC: 4
- KSI-CNA-IBP: 3
- KSI-CNA-RVP: 3
- KSI-CNA-DFP: 2
- KSI-CNA-EIS: 2
- KSI-RPL-RRO: 2
- KSI-SVC-RUD: 2
- KSI-SVC-VCM: 2
- KSI-MLA-ALA: 1
- KSI-PIY-RVD: 1
- KSI-SVC-PRR: 1
- KSI-CNA-OFA: 0
- KSI-PIY-RES: 0
