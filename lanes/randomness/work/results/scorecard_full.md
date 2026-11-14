| id | prediction (PREREG wording abbreviated) | measured | result |
|---|---|---|---|
| PS1 | median odd share in [0.45, 0.70], every net in [0.40, 0.75] (256 x 32) | [0.585, 0.556, 0.572, 0.563, 0.531] | HOLDS |
| PS2 | median share of degrees <= 2 in [0.30, 0.65] (256 x 32) | [0.619, 0.467, 0.472, 0.436, 0.263] | HOLDS |
| PS3 | median even >= 6 share in [0.08, 0.30] (256 x 32) | [0.113, 0.169, 0.161, 0.186, 0.212] | HOLDS |
| PB1 | Kerdock (Haar) gain over MC: median in [2.0, 5.0], >= 1.5 on 5 of 5 | [4.69, 3.04, 3.24, 2.74, 2.4] | HOLDS |
| PB2 | no Haar-randomised design gains more than 6 over MC (256 x 32) | 4.69 | HOLDS |
| PW1 | polar RQMC beats standard RQMC at 2^14 on >= 4 of 5 nets, median ratio >= 1.2 (256 x 32) | [1.37, 1.15, 1.76, 1.31, 0.82] | HOLDS |
| PW3 | polar-aligned Kerdock (signed permutations) biased: nMSE x m >= 5 on >= 4 of 5 | [94.6, 195.1, 54.2, 94.1, 93.2] | HOLDS |
| PW4 | multilevel two-level best gain over RB-MC <= 1.1 on 5 of 5 (256 x 32) | [1.0, 0.986, 1.03, 0.988, 0.961] | HOLDS |
| PS4 | simplex gain and E_1 share fall from n = 32 to 256 (medians) | {'simplex_gain': {'32': 4.49, '64': 2.82, '128': 2.1, '256': 1.93}, 'E1': {'32': 0.466, '64': 0.38, '128': 0.288, '256': 0.319}} | HOLDS |
| PW2 | polar/standard RQMC ratio at 2^14, median per width in [0.8, 1.3] for n = 32, 64, 128 | {'32': 1.26, '64': 0.99, '128': 1.17} | HOLDS |
| PC1 | rqmc_polar gain >= 2.0 on >= 4 of 5 and >= 1.2 x rqmc_std on >= 4 of 5 (N = 2^16) | {'polar': [2.64, 1.83, 2.22, 2.47, 1.87], 'std': [2.77, 1.97, 2.13, 2.15, 1.95]} | FAILS |
| PC2 | Kerdock gain >= 1.8 on >= 4 of 5 (66,048 points, vs truth) | [3.93, 3.15, 2.79, 2.89, 2.2] | HOLDS |
| PC3 | best structured sampler gains in [2, 8] over MC on every net (none reaches 10x) | [3.93, 3.15, 2.79, 2.89, 2.2] | HOLDS |
| PC4 | pairwise-independent MC: median nMSE x N / (V_rb/V) in [0.6, 1.5] | [0.63, 0.67, 0.65, 2.57, 1.08] | HOLDS |
| PC5 | zero-bit polar Sobol: median nMSE x N <= 1 | [1.2, 0.31, 0.41, 0.23, 0.37] | HOLDS |
| PN1 | layer-1 GSA (pooled delta = 1e-6..1e-4) within +-10% of n/sqrt(2 pi), every net, all widths | [0.94, 1.071, 29] | HOLDS |
| PN2 | per-layer GSA (l >= 2) in [0.5, 1.3] x n/sqrt(2 pi), every layer, every 256 net | [0.329, 1.313] | FAILS |
| PN3 | total partition GSA in [0.6, 1.2] x n L / sqrt(2 pi) (256 x 32) | [0.767, 0.853, 1.034, 1.006, 1.071] | HOLDS |
| PN4 | NS_out(1e-5)/1e-5 in [0.4, 1.5] x n/V on every 256 net | [0.873, 2.089, 0.861, 0.435, 0.551] | FAILS |
| PN5 | P(gate pattern changes) at delta = 1e-6 >= 0.8 on every 256 net | [0.928, 0.944, 0.968, 0.964, 0.976] | HOLDS |
| PN6 | validity: design tail tau_2 >= the T6 lower bound from NS_sph (tolerance 0.05), every net | [[0.381, 0.185, True], [0.533, 0.329, True], [0.528, 0.287, True], [0.564, 0.258, True], [0.737, 0.441, True]] | HOLDS |
| PQ1 | centred Sobol (rb) fitted rate p over N = 2^8..2^16: median in [0.6, 1.4] (256 x 32) | [1.07, 1.14, 1.14, 1.09, 0.84] | HOLDS |
| PQ4 | Korobov lattice (rb) median nMSE x N at 2^14 >= 0.5 (256 x 32) | [0.46, 1.0, 0.53, 0.77, 0.41] | HOLDS |
| PQ2 | centred Sobol (rb) median nMSE x N at 2^14 higher at n = 256 than at n = 32 | {'32': 0.166, '64': 0.266, '128': 0.506, '256': 0.337} | HOLDS |
| PQ3 | k-wise designs, every resolved (net, k): nMSE x N in [0.05, 5] | {'count': 114, 'min': 0.132, 'max': 4.896} | HOLDS |
| PA1 | rqmc_std median p over 2^8..2^18 in [0.85, 1.25] | 1.045 | HOLDS |
| PA2 | rqmc_polar median p in [0.85, 1.35] | 1.058 | HOLDS |
| PA3 | no series has median p > 1.5 at 256 x 32 | 1.13 | HOLDS |
| PA5 | 512 x 64: median degree <= 2 share in [0.45, 0.60] | 0.405 | FAILS |
| PA6 | 512 x 64: median odd share in [0.55, 0.59] | 0.542 | FAILS |
| PA7 | 512 x 64: median simplex gain in [1.8, 2.6] and cross-polytope gain in [2.0, 2.8] | [1.71, 2.11] | FAILS |
| PA8 | 512 x 64: n / (mean V over the nets) in [35, 45] | 48.4 | FAILS |
