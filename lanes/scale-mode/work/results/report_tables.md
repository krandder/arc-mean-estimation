### Section 5 table (L = n/8)

| n x L | LVTV2 nMSE @ cost | G_MC | G_RQ (wins vs MC, RQMC) | X_RQ | SL3 nMSE @ cost | SL3 G_RQ | gamma_SL | gamma_ARC | law |
|---|---|---|---|---|---|---|---|---|---|
| 32 x 4 | 7.2e-04 @ 200 | 7 | 1.8 (8/8, 7/8) | 1.8 | 8.3e-05 @ 1.6e+03 | 1.5 | 1 | 0.54 | 0.600 |
| 64 x 8 | 6.7e-04 @ 287 | 5.2 | 2 (8/8, 8/8) | 2 | 7.2e-05 @ 6.1e+03 | 0.73 | 0.72 | 0.37 | 0.500 |
| 128 x 16 | 6.0e-04 @ 426 | 4 | 2.4 (8/8, 8/8) | 2.1 | 9.5e-05 @ 2.1e+04 | 0.19 | 0.52 | 0.28 | 0.429 |
| 256 x 32 | 3.6e-04 @ 688 | 4 | 2.5 (5/5, 5/5) | 2.3 | 7.2e-05 @ 7.5e+04 | 0.067 | 0.3 | 0.31 | 0.375 |

### Section 6 table (L = n/4, the claim's diagonal; fresh nets)

| n x L | nets | LVTV2 nMSE @ cost | G_MC (median; of mean) | claim's G_MC | G_RQ (wins vs RQMC) | X_RQ | RQMC gain over MC near that cost | ARC best at <= cost / LVTV2 | SL3 nMSE @ cost, G_RQ | gamma_SL | law |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 64 x 16 | 8 | 2.0e-03 @ 302 | 1.7; 1.7 | 2.17 | 0.79 [0.59, 1.2] (1/8) | 0.81 | 2.2 | 3.5 | 3.8e-04 @ 1e+04, 0.091 | 0.45 | 0.333 |
| 128 x 32 | 8 | 1.8e-03 @ 436 | 1.3; 1.3 | 1.52 | 0.73 [0.3, 2] (2/8) | 0.7 | 1.8 | 3.3 | 1.2e-03 @ 3.3e+04, 0.0096 | 0.11 | 0.286 |
| 256 x 64 | 8 | 6.8e-04 @ 695 | 2.1; 2.1 | 1.51 | 1.2 [0.7, 1.5] (7/8) | 1.1 | 1.9 | 3.5 | 3.7e-04 @ 1.2e+05, 0.01 | 0.11 | 0.250 |
| 512 x 128 | 8 | 1.0e-03 @ 1208 | 0.81; 0.89 | 1.41 | 0.43 [0.22, 2.5] (3/8) | 0.45 | 1.8 | 1.1 | - | - | 0.222 |
| 1024 x 256 | 8 | 1.1e-04 @ 2233 | 4.1; 3.5 | 1.21 | 2 [0.97, 11] (7/8) | 1.9 | 1.7 | 3.8 | - | - | 0.200 |

### Section 7 table (1024 x 16, Phase 2 public MLPs 0-11)

Mean avg_variance 0.080; full-budget (65,536-pass) MC raw MSE 1.2e-06; full-budget RQMC raw MSE 7.5e-07.

| method | nets | mean raw final-layer MSE | cost (passes, ARC counter) | G_MC | G_RQ | full-budget RQMC raw / method raw (median) | adjusted score (contest formula, ARC-counter cost) |
|---|---|---|---|---|---|---|---|
| COV | 12 | 4.5e-06 | 2049 | 8.4 | 6.3 | 0.17 | 4.5e-07 |
| ARC-k2 | 12 | 4.5e-06 | 1545 | 11 | 8.7 | 0.17 | 4.5e-07 |
| ARC-k2a | 12 | 1.1e-06 | 1603 | 48 | 36 | 0.72 | 1.1e-07 |
| LVTV2 | 12 | 1.4e-06 | 2162 | 26 | 20 | 0.53 | 1.4e-07 |
| LVT | 12 | 1.9e-06 | 2157 | 19 | 14 | 0.4 | 1.9e-07 |
| LVTV2f1 | 12 | 1.4e-06 | 2162 | 26 | 19 | 0.53 | 1.4e-07 |
| LVT0 | 12 | 4.2e-06 | 2156 | 8.7 | 6.5 | 0.18 | 4.2e-07 |
| ARC-k3f | 6 | 4.0e-08 | 96968 | 22 | 13 | 19 | 5.8e-08 |
| SL3 | 6 | 3.2e-08 | 212483 | 12 | 7.5 | 24 | 1.0e-07 |

gamma_ARC (k2a -> k3f) median 0.83 [0.76, 0.88]; gamma_SL median 0.83; law log 64 / log 1024 = 0.600.
