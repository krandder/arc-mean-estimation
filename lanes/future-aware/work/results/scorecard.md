| id | prediction (abbreviated) | measured | result |
|---|---|---|---|
| P1 | n = 256: median b2(cond_futnl64)/b2(cond_pca64) <= 0.5 at >= 3 of l = 4, 8, 16, 24 | l=4: 0.284 (5 nets); l=8: 0.0897 (3 nets); l=16: 0.552 (4 nets); l=24: 0.909 (3 nets) | FAILS |
| P2 | I_16(256) < I_16(64), I_16 = gauss/futnl16 in the recursion | 64: 5.23; 128: 2.26; 256: 1.36 | HOLDS |
| P3 | gauss/futnl{n/4} >= 2 and gauss/futnl{n/2} >= 10 at every width | 64: 5.23, 75.2; 128: 9.12, 121; 256: 18.8, 204 | HOLDS |
| P4 | median b2 futnl{n/4} < pca{n/4} at every width | 64: 0.000501 vs 0.000795; 128: 0.000204 vs 0.000578; 256: 6.44e-05 vs 0.000308 | HOLDS |
| P5 | particle recursion futnl{n/2} at its honest cost: G_RQMC < 0.5 on every net | 64: max 0.00724; 128: max 0.0273; 256: max 0.0289 | HOLDS |
| P6 | (a) R(futv, n/4) >= 0.7; (b) R(pca, n/8) < R(futv, n/8), every width | 64: R(futv,n/4) 0.984, R(futv,n/8) 0.787 vs R(pca,n/8) 0.651; 128: R(futv,n/4) 0.949, R(futv,n/8) 0.763 vs R(pca,n/8) 0.676; 256: R(futv,n/4) 0.977, R(futv,n/8) 0.867 vs R(pca,n/8) 0.782 | HOLDS |
| P7 | n = 256: every D1 variant at its implemented cost has G_RQMC < 0.2 (5/5 nets) | hashed scorer: fails (NaN runs included); corrected (NaN runs excluded, deviations item 3): max G 0.181 over 57 runs, 8 failed runs | HOLDS |
| P8 | n = 256, dedicated best-case cost: median G_RQMC of k3p(futmf2, 64) and k3p(futv, 64) <= 3 | hashed scorer: futmf2: nan; futv: 0.0236 (FAILS: it looked up "futmf264", the runs are "futmf2_64"; deviations item 7); post hoc with the actual names: futmf2: 2.37; futv: 0.0236 -> holds | FAILS |
| P9 | (a) l = 1 best eta >= 0.25; (b) l >= 8 every control beta_eg >= 1e-4; (c) best equal-cost gain at 6.5e4 passes <= 2 (n = 256) | (a) median eta 0.546: True; (b) min median beta 0.000277: True; (c) median gain 0.83: True | HOLDS |
