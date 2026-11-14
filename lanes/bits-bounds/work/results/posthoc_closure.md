# Closure test across widths (POST HOC statistics; registered scores in closure_scores.json and closure4_scores.json)

Per net: nMSE = |a - mu|^2 / V by the unbiased cross-product; gain = (1/(2n)) / nMSE (MC at the closure's matrix-product cost of 2n passes).

| n x L | nets | median gain | geo-mean nMSE | log10 nMSE mean +- SE | n E[err^2]/E[V] |
|---|---|---|---|---|---|
| 16 x 16 | 8 | 0.38 | 7.88e-02 | -1.10 +- 0.14 | 0.977 |
| 32 x 32 | 8 | 0.28 | 3.72e-02 | -1.43 +- 0.20 | 0.433 |
| 64 x 64 | 8 | 0.63 | 5.91e-03 | -2.23 +- 0.32 | 0.619 |
| 128 x 128 | 8 | 3.26 | 1.52e-03 | -2.82 +- 0.28 | 0.209 |
| 192 x 192 | 4 | 0.87 | 3.58e-03 | -2.45 +- 0.27 | 0.281 |
| 256 x 256 | 4 | 1.02 | 1.79e-03 | -2.75 +- 0.22 | 0.728 |
| 16 x 8 | 8 | 2.28 | 1.32e-02 | -1.88 +- 0.14 | 0.207 |
| 32 x 16 | 8 | 0.59 | 2.67e-02 | -1.57 +- 0.16 | 0.602 |
| 64 x 32 | 8 | 0.80 | 9.64e-03 | -2.02 +- 0.09 | 0.582 |
| 128 x 64 | 8 | 0.89 | 3.89e-03 | -2.41 +- 0.18 | 0.344 |
| 256 x 128 | 4 | 0.40 | 2.60e-03 | -2.58 +- 0.33 | 1.253 |

Log-log slope of per-net nMSE against n (all nets, least squares; slope +- SE):
- alpha=1.0 n=16-128: -1.97 +- 0.35
- alpha=1.0 n=128-256: 0.53 +- 1.29
- alpha=1.0 n=16-256: -1.54 +- 0.26
- alpha=0.5 n=16-128: -0.67 +- 0.24
- alpha=0.5 n=128-256: -0.58 +- 1.13
- alpha=0.5 n=16-256: -0.73 +- 0.20

Extrapolation test: fit log10 nMSE on log10 n over n = 16-128 (all nets), predict the mean at larger n
(prediction SE from the fit covariance), compare with the observed mean +- SE; z = (obs - pred)/SE_comb.
- alpha=1.0 n=192: predicted -3.13 +- 0.25, observed -2.45 +- 0.27, z = 1.86
- alpha=1.0 n=256: predicted -3.38 +- 0.29, observed -2.75 +- 0.22, z = 1.72
- alpha=0.5 n=256: predicted -2.48 +- 0.20, observed -2.58 +- 0.33, z = -0.28
