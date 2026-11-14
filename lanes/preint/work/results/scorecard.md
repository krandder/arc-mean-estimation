| test | prediction | outcome |
|---|---|---|
| P1 cost law (window vertices / Rice) | in [0.6, 1.5] on 13 of 13 | holds, 13 of 13 (ratios 0.94, 1.02, 1.07, 0.89, 0.89, 0.89, 0.81, 1.20, 1.01, 0.88, 1.07, 1.02, 1.11) |
| P2 line variance ratio, n >= 64 | rand >= 0.8, active >= 0.6 on all | holds (rand 0.91, 0.93, 0.91, 0.92, 0.90, 0.91, 0.98, 0.80, 0.95, 0.81; active 0.63, 0.77, 0.74, 0.83, 0.79, 0.83, 0.85, 0.75, 0.88, 0.87) |
| P3a PI >= 10x worse than RQMC at equal cost (S3) | all 13 | holds, 13 of 13 (min ratios 26, 21, 22, 128, 108, 109, 386, 308, 361, 647, 1067, 1410, 766) |
| P3b alpha(PI best) <= alpha(RQMC) + 0.15, n >= 128 | >= 5 of 7 | fails, 4 of 7 |
| P3c PI_as steeper by > 0.1: n = 32 (>= 2 of 3), n = 64 (<= 1 of 3) | both | fails (n=32: 3, n=64: 2) |
| P4 small nets: alpha(PI_as) > alpha(RQMCRB) + 0.1 | >= 6 of 9 | holds, 8 of 9 |
| P5a 8 x 256: PIJ worse than RQMCJ at every common cost | >= 5 of 6 | holds, 6 of 6 |
| P5b 8 x 256: abs(alpha(PIJ best) - alpha(RQMCJ)) < 0.3 | >= 4 of 6 | holds, 6 of 6 |
| P6 RQMC N x nMSE >= NNGP-proxy bound | all 13 | fails, 12 of 13 (min measured/bound 2.45, 2.90, 3.07, 1.77, 2.12, 1.77, 1.39, 1.79, 1.94, 1.63, 0.96, 1.52, 1.90) |
| P7 RQMC local exponent (last 3 budgets) <= 1.3 | >= 10 of 13 | holds, 12 of 13 |
| P8 MLMC alpha in [0.8, 1.2] | all | fails, 11 of 19 |

Validity: bias-flag cells by method: {'RQMC': 1, 'PIJ_as': 1, 'MLMC_32': 1}; suspect methods: []
