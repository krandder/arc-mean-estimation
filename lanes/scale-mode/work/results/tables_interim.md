## T1. Every method at its own cost (medians over nets; min-max in brackets)

G_MC = gain over MC at the method's own cost; G_RQ = over RQMC; X_RQ = cost multiple at which RQMC reaches the method's error; R_ARC = best ARC variant at <= that cost / the method's error; wins = nets with G > 1.


### 32 x 4 (E2_n32)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 7.20e-04 [3.42e-04, 2.38e-03] | 200 | 7 [2.1, 15] | 1.8 [0.39, 4.8] (extrap.) | 8 / 7 | 1.8 | 1.5 |
| LVT | 8 | 8.90e-04 [4.88e-04, 2.37e-03] | 195 | 5.8 [2.2, 11] | 1.7 [0.4, 3.3] (extrap.) | 8 / 7 | 1.7 | 1.6 |
| LVTV2f1 | 8 | 9.44e-04 [4.15e-04, 2.56e-03] | 200 | 5.3 [1.9, 12] | 1.5 [0.36, 3.9] (extrap.) | 8 / 5 | 1.5 | 1.2 |
| LVT0 | 8 | 1.93e-03 [1.13e-03, 3.48e-03] | 194 | 2.7 [1.5, 4.6] | 0.64 [0.28, 1.5] (extrap.) | 8 / 1 | 0.64 | 0.72 |
| SL3 | 8 | 8.25e-05 [5.38e-05, 2.74e-04] | 1628 | 7.5 [2.2, 11] | 1.5 [0.36, 2.5] | 8 / 7 | 1.4 | 5.3 |
| ARC-k2 | 8 | 2.14e-03 [1.41e-03, 3.72e-03] | 58 | 8.1 [4.6, 12] | 1.9 [1, 4] (extrap.) | 8 / 8 | 1.9 | 1 |
| ARC-k2a | 8 | 1.14e-03 [8.91e-04, 2.91e-03] | 117 | 7.6 [2.9, 9.6] | 1.6 [0.55, 3.2] (extrap.) | 8 / 6 | 1.6 | 1 |
| ARC-k3f | 8 | 4.35e-04 [2.81e-04, 1.20e-03] | 826 | 2.8 [1, 4.3] | 0.64 [0.24, 0.87] | 8 / 0 | 0.7 | 1 |
| ARC-k3fa | 8 | 1.37e-04 [7.35e-05, 2.85e-04] | 6783 | 1.1 [0.52, 2] | 0.22 [0.084, 0.36] | 6 / 0 | 0.24 | 1 |

gamma_SL (LVTV2 -> SL3) median 1 [0.73, 1.3]; of medians 1. gamma_ARC (k2a -> best K = 3) median 0.54 [0.46, 0.73]. Uniform law log(n/L)/log n = 0.600; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 3.8, 1024: 4.2, 4096: 5.2, 16384: 5.1.

### 64 x 8 (E2_n64)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 6.74e-04 [4.92e-04, 8.60e-04] | 287 | 5.2 [4.1, 7.1] | 2 [1.5, 3.4] | 8 / 8 | 2 | 1.6 |
| LVT | 8 | 9.01e-04 [4.68e-04, 1.32e-03] | 281 | 4 [2.7, 7.6] | 1.6 [1.2, 4.1] | 8 / 8 | 1.5 | 1.3 |
| LVTV2f1 | 8 | 7.42e-04 [4.62e-04, 1.11e-03] | 287 | 4.7 [3.1, 7.5] | 1.8 [1.5, 3.6] | 8 / 8 | 1.7 | 1.6 |
| LVT0 | 8 | 2.23e-03 [1.70e-03, 3.67e-03] | 281 | 1.6 [0.97, 2.1] | 0.64 [0.35, 0.95] | 6 / 0 | 0.65 | 0.54 |
| SL3 | 8 | 7.18e-05 [6.25e-05, 1.42e-04] | 6057 | 2.3 [1.2, 2.9] | 0.73 [0.35, 0.84] | 8 / 0 | 0.75 | 6 |
| ARC-k2 | 8 | 2.39e-03 [1.70e-03, 3.86e-03] | 106 | 4 [2.5, 5.6] | 1.6 [0.94, 2.8] (extrap.) | 8 / 7 | 1.6 | 1 |
| ARC-k2a | 8 | 1.27e-03 [4.97e-04, 2.50e-03] | 164 | 4.8 [2.4, 12] | 1.9 [1.3, 6.2] (extrap.) | 8 / 8 | 1.9 | 1 |
| ARC-k3f | 8 | 5.22e-04 [1.17e-04, 1.12e-03] | 3114 | 0.63 [0.29, 2.7] | 0.18 [0.14, 0.74] | 3 / 0 | 0.21 | 1 |
| ARC-k3fa | 8 | 1.82e-04 [1.67e-04, 3.04e-04] | 25697 | 0.21 [0.13, 0.23] | 0.066 [0.04, 0.095] (extrap.) | 0 / 0 | 0.059 | 1 |

gamma_SL (LVTV2 -> SL3) median 0.72 [0.57, 0.84]; of medians 0.73. gamma_ARC (k2a -> best K = 3) median 0.37 [0.2, 0.5]. Uniform law log(n/L)/log n = 0.500; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 2.6, 1024: 3.2, 4096: 3.4, 16384: 3.1.

### 128 x 16 (E2_n128)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 5.99e-04 [2.96e-04, 1.00e-03] | 426 | 4 [2.3, 7.9] | 2.4 [1.2, 3.3] | 8 / 8 | 2.1 | 2.1 |
| LVT | 8 | 6.09e-04 [3.25e-04, 1.79e-03] | 421 | 3.9 [1.3, 7.3] | 2.1 [0.7, 4] | 8 / 7 | 1.8 | 1.2 |
| LVTV2f1 | 8 | 6.33e-04 [3.04e-04, 9.69e-04] | 426 | 3.7 [2.4, 7.7] | 2.2 [1.3, 3.2] | 8 / 8 | 2 | 1.9 |
| LVT0 | 8 | 1.53e-03 [5.46e-04, 4.25e-03] | 420 | 1.6 [0.56, 4.4] | 0.92 [0.3, 2.5] | 5 / 4 | 0.93 | 0.61 |
| SL3 | 8 | 9.48e-05 [4.75e-05, 1.96e-04] | 21493 | 0.47 [0.25, 1] | 0.19 [0.099, 0.28] (extrap.) | 1 / 0 | 0.21 | 2.3 |
| ARC-k2 | 8 | 1.63e-03 [5.14e-04, 4.40e-03] | 201 | 3.2 [1.1, 9.7] | 2 [0.52, 7] (extrap.) | 8 / 6 | 1.9 | 1 |
| ARC-k2a | 8 | 1.01e-03 [6.05e-04, 1.87e-03] | 260 | 3.9 [2.1, 6.4] | 2 [1.5, 5.5] | 8 / 8 | 1.9 | 1 |
| ARC-k3f | 8 | 2.65e-04 [1.21e-04, 4.74e-04] | 12297 | 0.31 [0.17, 0.67] | 0.12 [0.093, 0.25] | 0 / 0 | 0.17 | 1 |
| ARC-k3fa | 8 | 2.53e-04 [1.41e-04, 5.12e-04] | 100374 | 0.041 [0.019, 0.071] | 0.012 [0.0088, 0.032] (extrap.) | 0 / 0 | 0.02 | 0.97 |

gamma_SL (LVTV2 -> SL3) median 0.52 [0.22, 0.62]; of medians 0.47. gamma_ARC (k2a -> best K = 3) median 0.28 [0.23, 0.51]. Uniform law log(n/L)/log n = 0.429; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 1.6, 1024: 2.1, 4096: 2.1, 16384: 2.7.

### 256 x 32 (E1)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 5 | 3.63e-04 [2.93e-04, 4.77e-04] | 688 | 4 [3.1, 5] | 2.5 [2.3, 5.8] | 5 / 5 | 2.3 | 2.1 |
| LVT | 5 | 4.69e-04 [4.19e-04, 7.60e-04] | 682 | 3.1 [1.9, 3.5] | 2 [1.5, 3.6] | 5 / 5 | 1.9 | 1.4 |
| LVTV2f1 | 5 | 3.87e-04 [2.72e-04, 4.90e-04] | 688 | 3.8 [3, 5.4] | 2.4 [2.3, 6.2] | 5 / 5 | 2.3 | 2.2 |
| LVT0 | 5 | 1.24e-03 [1.00e-03, 2.02e-03] | 681 | 1.2 [0.73, 1.5] | 0.9 [0.56, 1] | 3 / 1 | 0.92 | 0.53 |
| SL3 | 5 | 7.18e-05 [3.34e-05, 1.39e-04] | 75281 | 0.18 [0.094, 0.42] | 0.067 [0.05, 0.25] (extrap.) | 0 / 0 | 0.088 | 1.8 |
| COV | 5 | 1.22e-03 [8.54e-04, 2.41e-03] | 513 | 1.6 [0.81, 2.3] | 1 [0.63, 1.6] | 3 / 3 | 1 | 0.57 |
| ARC-k2 | 5 | 1.22e-03 [8.54e-04, 2.41e-03] | 393 | 2.1 [1.1, 3] | 1.4 [0.83, 2.2] | 5 / 4 | 1.3 | 1 |
| ARC-k2a | 5 | 8.42e-04 [4.82e-04, 2.26e-03] | 452 | 2.6 [0.98, 4.6] | 2 [0.85, 4.6] | 4 / 4 | 1.9 | 1 |
| ARC-k3f | 5 | 2.01e-04 [6.16e-05, 2.83e-04] | 49097 | 0.1 [0.072, 0.33] | 0.057 [0.035, 0.18] | 0 / 0 | 0.062 | 1 |

gamma_SL (LVTV2 -> SL3) median 0.3 [0.21, 0.48]; of medians 0.35. gamma_ARC (k2a -> best K = 3) median 0.31 [0.23, 0.47]. Uniform law log(n/L)/log n = 0.375; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 1.2, 1024: 1.5, 4096: 1.7, 16384: 2.2, 65536: 2.1.

### 64 x 16 (E3_n64)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 1.98e-03 [1.57e-03, 2.87e-03] | 302 | 1.7 [1.2, 2.1] | 0.79 [0.59, 1.2] | 8 / 1 | 0.81 | 3.5 |
| LVT | 8 | 2.68e-03 [6.90e-04, 5.08e-03] | 297 | 1.3 [0.66, 4.9] | 0.51 [0.3, 2.7] | 5 / 3 | 0.53 | 3.6 |
| LVTV2f1 | 8 | 2.12e-03 [1.77e-03, 3.20e-03] | 302 | 1.6 [1, 1.9] | 0.68 [0.38, 1] | 8 / 1 | 0.69 | 3.1 |
| LVT0 | 8 | 9.14e-03 [2.76e-03, 1.70e-02] | 296 | 0.4 [0.2, 1.2] | 0.17 [0.091, 0.67] | 1 / 0 | 0.17 | 1 |
| SL3 | 8 | 3.77e-04 [2.62e-04, 1.30e-03] | 10420 | 0.25 [0.086, 0.33] | 0.091 [0.031, 0.17] | 0 / 0 | 0.095 | 12 |
| ARC-k2 | 8 | 8.97e-03 [2.29e-03, 1.98e-02] | 106 | 1.1 [0.48, 4.1] | 0.46 [0.23, 2.3] (extrap.) | 4 / 2 | 0.46 | 1 |
| ARC-k2a | 8 | 2.47e-02 [7.00e-03, 5.56e-02] | 165 | 0.25 [0.11, 0.86] | 0.12 [0.06, 0.56] (extrap.) | 0 / 0 | 0.12 | 0.43 |
| ARC-k3f | 8 | 4.86e-03 [3.97e-03, 9.85e-03] | 6251 | 0.033 [0.016, 0.04] | 0.013 [0.0049, 0.021] | 0 / 0 | 0.015 | 1 |

gamma_SL (LVTV2 -> SL3) median 0.45 [0.11, 0.55]; of medians 0.47. gamma_ARC (k2a -> best K = 3) median 0.45 [0.0077, 0.55]. Uniform law log(n/L)/log n = 0.333; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 2.2, 1024: 2.5, 4096: 2.4, 16384: 2.7.

128 x 32 (E3_n128): not scored (0 nets finished, < 3).


256 x 64 (E3_n256): not scored (0 nets finished, < 3).


512 x 128 (E3_n512): not scored (2 nets finished, < 3).


1024 x 256 (E3_n1024): not scored (0 nets finished, < 3).


### 1024 x 16 (E4)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|

gamma_SL (LVTV2 -> SL3) median - [-, -]; of medians -. gamma_ARC (k2a -> best K = 3) median - [-, -]. Uniform law log(n/L)/log n = 0.600; sampling 1.

Phase 2 contest metric: mean avg_variance 0.080; full-budget MC raw MSE 1.22e-06; full-budget RQMC raw MSE - (mean over nets).
| method | mean raw final-layer MSE | its cost (passes, ARC counter) | adjusted score with ARC-counter cost |
|---|---|---|---|

## T2. Width exponents (slope of log median on log n; 95% bootstrap over nets)

| series | slope | 95% CI | widths |
|---|---|---|---|
| L=n/8 ARC-k2 C | +0.92 | [+0.92, +0.92] | 32, 64, 128, 256 |
| L=n/8 ARC-k2 G_MC | -0.62 | [-0.98, -0.40] | 32, 64, 128, 256 |
| L=n/8 ARC-k2 G_RQ | -0.11 | [-0.42, +0.17] | 32, 64, 128, 256 |
| L=n/8 ARC-k2 e | -0.30 | [-0.52, +0.05] | 32, 64, 128, 256 |
| L=n/8 ARC-k2a C | +0.65 | [+0.65, +0.65] | 32, 64, 128, 256 |
| L=n/8 ARC-k2a G_MC | -0.49 | [-0.93, -0.09] | 32, 64, 128, 256 |
| L=n/8 ARC-k2a G_RQ | +0.08 | [-0.31, +0.48] | 32, 64, 128, 256 |
| L=n/8 ARC-k2a e | -0.16 | [-0.59, +0.27] | 32, 64, 128, 256 |
| L=n/8 LVTV2 C | +0.59 | [+0.59, +0.59] | 32, 64, 128, 256 |
| L=n/8 LVTV2 G_MC | -0.28 | [-0.49, -0.06] | 32, 64, 128, 256 |
| L=n/8 LVTV2 G_RQ | +0.14 | [+0.00, +0.55] | 32, 64, 128, 256 |
| L=n/8 LVTV2 e | -0.31 | [-0.53, -0.12] | 32, 64, 128, 256 |

## T3. Registered predictions and the decision rule (PREREG sections 5-6)

| id | registered statement | result | measured |
|---|---|---|---|
| C1 L=n/8 | claim: LVTV2 beats naive MC at its own FLOPs in every cell (MC / mean nMSE > 1) | HOLDS | E1: 4; E2_n32: 5.5; E2_n64: 5.2; E2_n128: 3.7 |
| C1 L=n/4 | claim: LVTV2 beats naive MC at its own FLOPs in every cell (MC / mean nMSE > 1) | HOLDS | E3_n64: 1.7 |
| C1 1024x16 | claim: LVTV2 beats naive MC at its own FLOPs in every cell (MC / mean nMSE > 1) | UNDETERMINED | E4: - |
| C2 E1 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 5/5 |
| C2 E2_n32 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C2 E2_n64 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C2 E2_n128 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C2 E3_n64 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C3 E1 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 5/5 |
| C3 E2_n32 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E2_n64 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E2_n128 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E3_n64 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C4 E3_n64 | claim: LVTV2 beats the best ARC variant at <= its cost (median ratio > 1) | HOLDS | 3.52 |
| C5 E4 | claim scope: LVTV2 worse than ARC k2a at 1024x16 on >= 9/12 nets | UNDETERMINED | 0/0 |
| C6 L=n/4 | claim: LVTV2 margin over naive MC narrows with width (exponent < 0) | UNDETERMINED | None |
| P1a E1 | LVTV2 beats RQMC at its own cost on >= 4/5 nets | HOLDS | 5/5 |
| P1b E1 | RQMC reaches LVTV2 error at <= 5x its cost on >= 4/5 nets | HOLDS | 5/5 |
| P2 E1 | at 64,850 passes RQMC >= 20x below the best affordable scale-law method on 5/5 nets | HOLDS | [33.3, 54.3, 46.3, 64.9, 38.9] |
| P3 L=n/8 | gamma_SL median < 1 at n = 64, 128, 256 and < 0.6 at n = 256 | HOLDS | E2_n64: 0.72; E2_n128: 0.52; E1: 0.3 |
| P4 L=n/8 | width exponent of median G_MC(LVTV2) along L = n/8 (n = 32-256) < 0 | HOLDS | slope: -0.28; lo: -0.49; hi: -0.06; widths: [32, 64, 128, 256] |
| P5 L=n/8 | width exponent of median G_RQ(LVTV2) along L = n/8 < 0.5 | HOLDS | slope: 0.14; lo: 0.00059; hi: 0.55; widths: [32, 64, 128, 256] |
| P6 | SL3 loses to RQMC at its own cost on >= 4/5 nets at 256x32 and >= 6/8 at 128x16 | HOLDS | 5/5, 8/8 |
| P7a L=n/4 | the claim's margin over naive MC replicates within 2x at every E3 width (median G_MC(LVTV2)) | HOLDS | E3_n64: 1.7 |
| P7b L=n/4 | median G_RQ(LVTV2) < 1.5 at every E3 width >= 256 | UNDETERMINED |  |
| P7c L=n/4 | width exponent of median G_RQ(LVTV2) along L = n/4 < 0.25 | UNDETERMINED | None |
| P7d L=n/4 | SL3 loses to RQMC at its own cost on >= 75% of nets at 128x32 and 256x64 | UNDETERMINED | E3_n128: 0/0; E3_n256: 0/0 |
| P8a E4 | COV (starter kit) and ARC k2 give the same error (to 1e-6 relative) on 12/12 | UNDETERMINED | 0/0 |
| P8b E4 | COV mean raw final-layer MSE in [3.0e-6, 5.5e-6] | UNDETERMINED | None |
| P8c E4 | COV beats RQMC at its own cost by >= 3x on 12/12 | UNDETERMINED | 0/0 |
| P8d E4 | full-budget RQMC (2^16) below COV in raw MSE on 12/12 and below ARC k2a on >= 9/12 | UNDETERMINED | COV 0/0, k2a 0/0 |
| P8e E4 | claim (b) in the contest metric: COV's adjusted score (0.1 x raw) below full-budget MC's on >= 11/12 | UNDETERMINED | 0/0 |
| P8f E4 | ARC k3f (MLPs 0-5): raw MSE <= 1e-7, >= 5x below full-budget RQMC, and costs > 65,536 passes, on 6/6 | UNDETERMINED | None |
| P8g E4 | gamma_ARC (k2a -> k3f) median over MLPs 0-5 in [0.6, 1.0] | UNDETERMINED | [] |
| N2 E4 | our negative applies at Phase 2: full-budget RQMC beats every affordable deductive method run here on >= 10/12 | UNDETERMINED | count: 0/0; best_affordable_over_rqmc: [] |
| D1 | ESCAPE route 1: gamma_SL >= 0.9 at n = 128 and 256 (L = n/8) AND SL3 beats RQMC at its own cost on >= 4/5 E1 nets | FAILS | gamma_SL_128: 0.52; gamma_SL_256: 0.3; SL3_beats_RQMC: 0/5 |
| D2 | ESCAPE route 2: on L = n/4, median G_RQ(LVTV2) > 1 at every width AND its width exponent has bootstrap CI lower bound > 0 | UNDETERMINED | med_G_RQ: {"E3_n64": 0.7858667320714281}; exponent: - |
| D | the scale-mode claim escapes the ladder (D1 or D2) | UNDETERMINED | None |
