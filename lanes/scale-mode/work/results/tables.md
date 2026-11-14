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
| ARC-k3fa | 1 | 9.53e-05 [9.53e-05, 9.53e-05] | 397176 | 0.026 [0.026, 0.026] | 0.016 [0.016, 0.016] (extrap.) | 0 / 0 | 0.01 | 0.65 |

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

### 128 x 32 (E3_n128)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 1.84e-03 [4.60e-04, 3.31e-03] | 436 | 1.3 [0.69, 5] | 0.73 [0.3, 2] | 6 / 2 | 0.7 | 3.3 |
| LVT | 8 | 3.11e-03 [5.48e-04, 6.34e-03] | 430 | 0.78 [0.37, 4.2] | 0.43 [0.22, 2.1] | 3 / 1 | 0.49 | 2.1 |
| LVTV2f1 | 8 | 1.99e-03 [5.02e-04, 3.31e-03] | 436 | 1.2 [0.69, 4.6] | 0.66 [0.31, 1.8] | 5 / 2 | 0.69 | 3.3 |
| LVT0 | 8 | 5.02e-03 [1.77e-03, 1.22e-02] | 429 | 0.47 [0.19, 1.3] | 0.24 [0.11, 0.64] | 2 / 0 | 0.28 | 1 |
| SL3 | 8 | 1.20e-03 [4.70e-04, 3.83e-03] | 33222 | 0.025 [0.0074, 0.066] | 0.0096 [0.0014, 0.032] (extrap.) | 0 / 0 | 0.014 | 2.9 |
| ARC-k2 | 8 | 4.95e-03 [1.68e-03, 1.67e-02] | 201 | 1 [0.3, 3] | 0.59 [0.22, 1.5] (extrap.) | 4 / 2 | 0.59 | 1 |
| ARC-k2a | 8 | 1.61e-02 [8.20e-03, 9.37e-01] | 260 | 0.24 [0.0041, 0.47] | 0.13 [0.0021, 0.19] | 0 / 0 | 0.13 | 0.41 |
| ARC-k3f | 8 | 3.45e-03 [2.57e-03, 3.71e-02] | 24714 | 0.012 [0.0011, 0.016] | 0.0043 [0.00021, 0.0072] (extrap.) | 0 / 0 | 0.0058 | 1 |

gamma_SL (LVTV2 -> SL3) median 0.11 [-0.48, 0.34]; of medians 0.099. gamma_ARC (k2a -> best K = 3) median 0.33 [0.26, 0.71]. Uniform law log(n/L)/log n = 0.286; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 1.8, 1024: 2.3, 4096: 2.2, 16384: 2.6.

### 256 x 64 (E3_n256)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 6.82e-04 [5.47e-04, 9.66e-04] | 695 | 2.1 [1.5, 2.6] | 1.2 [0.7, 1.5] | 8 / 7 | 1.1 | 3.5 |
| LVT | 8 | 7.77e-04 [4.15e-04, 1.71e-03] | 689 | 1.9 [0.85, 3.5] | 0.93 [0.46, 1.7] | 6 / 3 | 0.94 | 2.3 |
| LVTV2f1 | 8 | 6.40e-04 [4.92e-04, 1.00e-03] | 695 | 2.2 [1.4, 2.9] | 1.2 [0.69, 1.6] | 8 / 6 | 1.2 | 4 |
| LVT0 | 8 | 2.16e-03 [5.46e-04, 3.67e-03] | 688 | 0.67 [0.4, 2.7] | 0.37 [0.22, 0.97] | 3 / 0 | 0.44 | 1.1 |
| SL3 | 8 | 3.67e-04 [1.18e-04, 2.37e-03] | 124095 | 0.022 [0.0032, 0.07] | 0.01 [0.0021, 0.027] (extrap.) | 0 / 0 | 0.01 | 3.1 |
| ARC-k2 | 8 | 2.17e-03 [7.30e-04, 4.17e-03] | 393 | 1.2 [0.61, 3.5] | 0.78 [0.29, 1.4] | 4 / 2 | 0.79 | 1 |
| ARC-k2a | 8 | 1.67e-02 [6.59e-03, 2.45e-01] | 452 | 0.14 [0.009, 0.34] | 0.064 [0.0035, 0.22] | 0 / 0 | 0.062 | 0.083 |
| ARC-k3f | 8 | 2.10e-03 [7.32e-04, 5.46e-02] | 98505 | 0.005 [0.00019, 0.014] | 0.0022 [0.00012, 0.0054] (extrap.) | 0 / 0 | 0.0026 | 0.6 |

gamma_SL (LVTV2 -> SL3) median 0.11 [-0.23, 0.32]; of medians 0.12. gamma_ARC (k2a -> best K = 3) median 0.37 [0.25, 0.52]. Uniform law log(n/L)/log n = 0.250; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 1.9, 1024: 1.7, 4096: 2.4, 16384: 2.5.

### 512 x 128 (E3_n512)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 1.02e-03 [1.41e-04, 2.44e-03] | 1208 | 0.81 [0.34, 5.9] | 0.43 [0.22, 2.5] | 3 / 3 | 0.45 | 1.1 |
| LVT | 8 | 4.75e-04 [3.90e-05, 2.08e-03] | 1203 | 1.8 [0.4, 21] | 0.88 [0.11, 18] | 5 / 3 | 0.82 | 1.6 |
| LVTV2f1 | 8 | 9.55e-04 [1.40e-04, 2.07e-03] | 1208 | 0.87 [0.4, 5.9] | 0.45 [0.24, 3.1] | 3 / 3 | 0.47 | 1.2 |
| LVT0 | 8 | 8.01e-04 [3.36e-04, 3.35e-03] | 1202 | 1.1 [0.25, 2.5] | 0.61 [0.066, 2.4] | 4 / 2 | 0.57 | 1 |
| ARC-k2 | 8 | 8.13e-04 [3.60e-04, 2.98e-03] | 777 | 1.7 [0.43, 3.6] | 0.93 [0.14, 3.8] | 5 / 4 | 0.86 | 1 |
| ARC-k2a | 8 | 1.69e-02 [4.37e-03, 3.21e-01] | 836 | 0.071 [0.0037, 0.27] | 0.046 [0.0023, 0.099] | 0 / 0 | 0.036 | 0.047 |

gamma_SL (LVTV2 -> SL3) median - [-, -]; of medians -. gamma_ARC (k2a -> best K = 3) median - [-, -]. Uniform law log(n/L)/log n = 0.222; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 1.5, 1024: 1.9, 4096: 1.8, 8192: 1.5.

### 1024 x 256 (E3_n1024)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 8 | 1.09e-04 [2.34e-05, 2.99e-04] | 2233 | 4.1 [1.5, 19] | 2 [0.97, 11] | 8 / 7 | 1.9 | 3.8 |
| LVT | 8 | 1.06e-04 [4.03e-05, 4.50e-04] | 2227 | 4.3 [1, 11] | 2.6 [0.61, 4.7] | 7 / 7 | 2.4 | 2.8 |
| LVTV2f1 | 8 | 9.85e-05 [2.13e-05, 2.85e-04] | 2233 | 4.6 [1.6, 21] | 2 [0.97, 12] | 8 / 7 | 1.9 | 3.8 |
| LVT0 | 8 | 3.24e-04 [2.24e-04, 7.89e-04] | 2226 | 1.4 [0.57, 2] | 0.76 [0.35, 1.1] | 6 / 3 | 0.77 | 1 |
| ARC-k2 | 8 | 3.38e-04 [2.25e-04, 9.18e-04] | 1545 | 1.9 [0.7, 2.9] | 0.93 [0.32, 2.2] | 7 / 3 | 0.92 | 1 |
| ARC-k2a | 8 | 4.17e-03 [2.34e-03, 9.54e+13] | 1604 | 0.15 [6.5e-18, 0.27] | 0.078 [3.1e-18, 0.15] | 0 / 0 | 0.058 | 0.084 |

gamma_SL (LVTV2 -> SL3) median - [-, -]; of medians -. gamma_ARC (k2a -> best K = 3) median - [-, -]. Uniform law log(n/L)/log n = 0.200; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 1.7, 1024: 2, 4096: 2.1, 16384: 1.9.

### 1024 x 16 (E4)

| method | nets | nMSE | cost (passes) | G_MC | G_RQ | wins vs MC / RQMC | X_RQ | R_ARC |
|---|---|---|---|---|---|---|---|---|
| LVTV2 | 12 | 1.78e-05 [1.36e-05, 2.02e-05] | 2162 | 26 [23, 34] | 20 [17, 26] | 12 / 12 | 16 | 0.8 |
| LVT | 12 | 2.42e-05 [1.79e-05, 3.05e-05] | 2157 | 19 [15, 26] | 14 [10, 20] | 12 / 12 | 12 | 0.58 |
| LVTV2f1 | 12 | 1.77e-05 [1.35e-05, 2.03e-05] | 2162 | 26 [23, 34] | 19 [16, 26] | 12 / 12 | 16 | 0.79 |
| LVT0 | 12 | 5.32e-05 [3.75e-05, 6.61e-05] | 2156 | 8.7 [7, 12] | 6.5 [4.8, 9.4] | 12 / 12 | 5.3 | 0.26 |
| SL3 | 6 | 3.89e-07 [3.35e-07, 4.52e-07] | 212483 | 12 [10, 15] | 7.5 [6.6, 8.9] (extrap.) | 6 / 6 | 7.5 | 1.3 |
| COV | 12 | 5.80e-05 [4.08e-05, 7.10e-05] | 2049 | 8.4 [6.9, 12] | 6.3 [4.7, 9.1] | 12 / 12 | 5.3 | 0.25 |
| ARC-k2 | 12 | 5.80e-05 [4.08e-05, 7.10e-05] | 1545 | 11 [9.1, 16] | 8.7 [6.5, 12] | 12 / 12 | 7 | 1 |
| ARC-k2a | 12 | 1.31e-05 [9.63e-06, 1.80e-05] | 1603 | 48 [35, 65] | 36 [26, 49] | 12 / 12 | 29 | 1 |
| ARC-k3f | 6 | 4.73e-07 [4.40e-07, 5.19e-07] | 96968 | 22 [20, 23] | 13 [13, 14] (extrap.) | 6 / 6 | 13 | 1 |

gamma_SL (LVTV2 -> SL3) median 0.83 [0.8, 0.88]; of medians 0.84. gamma_ARC (k2a -> best K = 3) median 0.83 [0.76, 0.88]. Uniform law log(n/L)/log n = 0.600; sampling 1.
RQMC gain over MC (median over nets) by N: 256: 1.2, 1024: 1.2, 4096: 1.5, 16384: 1.7, 65536: 1.6.

Phase 2 contest metric: mean avg_variance 0.080; full-budget MC raw MSE 1.22e-06; full-budget RQMC raw MSE 7.48e-07 (mean over nets).
| method | mean raw final-layer MSE | its cost (passes, ARC counter) | adjusted score with ARC-counter cost |
|---|---|---|---|
| LVTV2 | 1.37e-06 | 2162 | 1.37e-07 |
| LVT | 1.91e-06 | 2157 | 1.91e-07 |
| LVTV2f1 | 1.37e-06 | 2162 | 1.37e-07 |
| LVT0 | 4.21e-06 | 2156 | 4.21e-07 |
| SL3 | 3.16e-08 | 212483 | 1.01e-07 |
| COV | 4.47e-06 | 2049 | 4.47e-07 |
| ARC-k2 | 4.47e-06 | 1545 | 4.47e-07 |
| ARC-k2a | 1.08e-06 | 1603 | 1.08e-07 |
| ARC-k3f | 3.95e-08 | 96968 | 5.85e-08 |

## T2. Width exponents (slope of log median on log n; 95% bootstrap over nets)

| series | slope | 95% CI | widths |
|---|---|---|---|
| L=n/4 ARC-k2 C | +0.97 | [+0.97, +0.97] | 64, 128, 256, 512, 1024 |
| L=n/4 ARC-k2 G_MC | +0.24 | [-0.04, +0.48] | 64, 128, 256, 512, 1024 |
| L=n/4 ARC-k2 G_RQ | +0.27 | [-0.04, +0.52] | 64, 128, 256, 512, 1024 |
| L=n/4 ARC-k2 e | -1.21 | [-1.44, -0.94] | 64, 128, 256, 512, 1024 |
| L=n/4 ARC-k2a C | +0.82 | [+0.82, +0.82] | 64, 128, 256, 512, 1024 |
| L=n/4 ARC-k2a G_MC | -0.32 | [-1.22, -0.12] | 64, 128, 256, 512, 1024 |
| L=n/4 ARC-k2a G_RQ | -0.28 | [-1.22, -0.04] | 64, 128, 256, 512, 1024 |
| L=n/4 ARC-k2a e | -0.51 | [-0.72, +0.44] | 64, 128, 256, 512, 1024 |
| L=n/4 LVTV2 C | +0.72 | [+0.72, +0.72] | 64, 128, 256, 512, 1024 |
| L=n/4 LVTV2 G_MC | +0.20 | [-0.05, +0.65] | 64, 128, 256, 512, 1024 |
| L=n/4 LVTV2 G_RQ | +0.19 | [-0.01, +0.74] | 64, 128, 256, 512, 1024 |
| L=n/4 LVTV2 e | -0.92 | [-1.37, -0.66] | 64, 128, 256, 512, 1024 |
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
| C1 L=n/4 | claim: LVTV2 beats naive MC at its own FLOPs in every cell (MC / mean nMSE > 1) | FAILS | E3_n64: 1.7; E3_n128: 1.3; E3_n256: 2.1; E3_n512: 0.89; E3_n1024: 3.5 |
| C1 1024x16 | claim: LVTV2 beats naive MC at its own FLOPs in every cell (MC / mean nMSE > 1) | HOLDS | E4: 27 |
| C2 E1 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 5/5 |
| C2 E2_n32 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C2 E2_n64 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C2 E2_n128 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C2 E3_n64 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 8/8 |
| C2 E3_n128 | claim: SL3 < LVTV2 on >= 80% of nets | FAILS | 6/8 |
| C2 E3_n256 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 7/8 |
| C2 E4 | claim: SL3 < LVTV2 on >= 80% of nets | HOLDS | 6/6 |
| C3 E1 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 5/5 |
| C3 E2_n32 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E2_n64 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E2_n128 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E3_n64 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E3_n128 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E3_n256 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 8/8 |
| C3 E4 | claim: SL3 < ARC k3f on >= 80% of nets | HOLDS | 6/6 |
| C4 E3_n64 | claim: LVTV2 beats the best ARC variant at <= its cost (median ratio > 1) | HOLDS | 3.52 |
| C4 E3_n128 | claim: LVTV2 beats the best ARC variant at <= its cost (median ratio > 1) | HOLDS | 3.31 |
| C4 E3_n256 | claim: LVTV2 beats the best ARC variant at <= its cost (median ratio > 1) | HOLDS | 3.47 |
| C4 E3_n512 | claim: LVTV2 beats the best ARC variant at <= its cost (median ratio > 1) | HOLDS | 1.1 |
| C4 E3_n1024 | claim: LVTV2 beats the best ARC variant at <= its cost (median ratio > 1) | HOLDS | 3.8 |
| C5 E4 | claim scope: LVTV2 worse than ARC k2a at 1024x16 on >= 9/12 nets | HOLDS | 12/12 |
| C6 L=n/4 | claim: LVTV2 margin over naive MC narrows with width (exponent < 0) | FAILS | slope: 0.2; lo: -0.046; hi: 0.65; widths: [64, 128, 256, 512, 1024] |
| P1a E1 | LVTV2 beats RQMC at its own cost on >= 4/5 nets | HOLDS | 5/5 |
| P1b E1 | RQMC reaches LVTV2 error at <= 5x its cost on >= 4/5 nets | HOLDS | 5/5 |
| P2 E1 | at 64,850 passes RQMC >= 20x below the best affordable scale-law method on 5/5 nets | HOLDS | [33.3, 54.3, 46.3, 64.9, 38.9] |
| P3 L=n/8 | gamma_SL median < 1 at n = 64, 128, 256 and < 0.6 at n = 256 | HOLDS | E2_n64: 0.72; E2_n128: 0.52; E1: 0.3 |
| P4 L=n/8 | width exponent of median G_MC(LVTV2) along L = n/8 (n = 32-256) < 0 | HOLDS | slope: -0.28; lo: -0.49; hi: -0.06; widths: [32, 64, 128, 256] |
| P5 L=n/8 | width exponent of median G_RQ(LVTV2) along L = n/8 < 0.5 | HOLDS | slope: 0.14; lo: 0.00059; hi: 0.55; widths: [32, 64, 128, 256] |
| P6 | SL3 loses to RQMC at its own cost on >= 4/5 nets at 256x32 and >= 6/8 at 128x16 | HOLDS | 5/5, 8/8 |
| P7a L=n/4 | the claim's margin over naive MC replicates within 2x at every E3 width (median G_MC(LVTV2)) | FAILS | E3_n64: 1.7; E3_n128: 1.3; E3_n256: 2.1; E3_n512: 0.81; E3_n1024: 4.1 |
| P7b L=n/4 | median G_RQ(LVTV2) < 1.5 at every E3 width >= 256 | FAILS | E3_n256: 1.2; E3_n512: 0.43; E3_n1024: 2 |
| P7c L=n/4 | width exponent of median G_RQ(LVTV2) along L = n/4 < 0.25 | HOLDS | slope: 0.19; lo: -0.015; hi: 0.74; widths: [64, 128, 256, 512, 1024] |
| P7d L=n/4 | SL3 loses to RQMC at its own cost on >= 75% of nets at 128x32 and 256x64 | HOLDS | E3_n128: 8/8; E3_n256: 8/8 |
| P8a E4 | COV (starter kit) and ARC k2 give the same error (to 1e-6 relative) on 12/12 | HOLDS | 12/12 |
| P8b E4 | COV mean raw final-layer MSE in [3.0e-6, 5.5e-6] | HOLDS | 4.47e-06 |
| P8c E4 | COV beats RQMC at its own cost by >= 3x on 12/12 | HOLDS | 12/12 |
| P8d E4 | full-budget RQMC (2^16) below COV in raw MSE on 12/12 and below ARC k2a on >= 9/12 | HOLDS | COV 12/12, k2a 12/12 |
| P8e E4 | claim (b) in the contest metric: COV's adjusted score (0.1 x raw) below full-budget MC's on >= 11/12 | HOLDS | 12/12 |
| P8f E4 | ARC k3f (MLPs 0-5): raw MSE <= 1e-7, >= 5x below full-budget RQMC, and costs > 65,536 passes, on 6/6 | HOLDS | raw: [3.704569562168001e-08, 4.4592040888064956e-08, 4.5890207083826793e-08, 4.091897499292581e-08, 3.6337280808053576e-08, 3; rqmc_full_over_k3f: [20.566395243959317, 18.713770139482676, 18.513353720835692, 19.603195497 |
| P8g E4 | gamma_ARC (k2a -> k3f) median over MLPs 0-5 in [0.6, 1.0] | HOLDS | [0.8545757228762125, 0.7863423926168623, 0.7587182682465168, 0.8049259938732258, 0.8709342865625732, 0.8836222057577791] |
| N2 E4 | our negative applies at Phase 2: full-budget RQMC beats every affordable deductive method run here on >= 10/12 | HOLDS | count: 12/12; best_affordable_over_rqmc: [["p2_00", "ARC-k2a", 1.62], ["p2_01", "ARC-k2a", 1.35], ["p2_02", "ARC-k2a", 1.21], ["p2_03", "ARC-k2a", 1.39], ["p2_04 |
| D1 | ESCAPE route 1: gamma_SL >= 0.9 at n = 128 and 256 (L = n/8) AND SL3 beats RQMC at its own cost on >= 4/5 E1 nets | FAILS | gamma_SL_128: 0.52; gamma_SL_256: 0.3; SL3_beats_RQMC: 0/5 |
| D2 | ESCAPE route 2: on L = n/4, median G_RQ(LVTV2) > 1 at every width AND its width exponent has bootstrap CI lower bound > 0 | FAILS | med_G_RQ: {"E3_n64": 0.7858667320714281, "E3_n128": 0.7253052206339259, "E3_n256": 1.1582265017247602, "E3_n512": 0.42625835196331; exponent: {"slope": 0.18768625089069957, "lo": -0.014500316781634331, "hi": 0.7384347393 |
| D | the scale-mode claim escapes the ladder (D1 or D2) | FAILS | None |
