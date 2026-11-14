| series | nets | median p | 95% CI (bootstrap over nets) | p per net |
|---|---|---|---|---|
| rqmc_std | 5 | 1.045 | [1.031, 1.076] | [np.float64(1.053), np.float64(1.031), np.float64(1.032), np.float64(1.076), np.float64(1.045)] |
| rqmc_polar | 5 | 1.058 | [1.008, 1.075] | [np.float64(1.058), np.float64(1.023), np.float64(1.064), np.float64(1.075), np.float64(1.008)] |
| sobol_rb | 5 | 1.085 | [0.835, 1.139] | [1.072, 1.137, 1.139, 1.085, 0.835] |
| sobol_rb_polar | 5 | 1.072 | [1.014, 1.189] | [1.189, 1.152, 1.053, 1.072, 1.014] |
| sobol_plain | 5 | 1.120 | [1.024, 1.475] | [1.475, 1.284, 1.115, 1.12, 1.024] |
| lattice_rb | 5 | 1.130 | [1.009, 1.223] | [1.223, 1.009, 1.145, 1.13, 1.099] |
| lattice_baker_rb | 5 | 1.063 | [0.994, 1.181] | [0.994, 1.045, 1.063, 1.181, 1.093] |
| polar_minus_std | 5 | -0.002 | [-0.036, 0.032] | [np.float64(0.005), np.float64(-0.008), np.float64(0.032), np.float64(-0.002), np.float64(-0.036)] |

| id | prediction | measured | result |
|---|---|---|---|
| PA1 | rqmc_std median p over 2^8..2^18 in [0.85, 1.25] | 1.045 | HOLDS |
| PA2 | rqmc_polar median p in [0.85, 1.35] | 1.058 | HOLDS |
| PA3 | no series has median p > 1.5 at 256 x 32 | 1.130 | HOLDS |
