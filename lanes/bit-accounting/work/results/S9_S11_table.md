# S9 real-valued chains and S11 controls

W1 = degree-1 (linear) share of each learned transition in the Gaussian convention; R2_T = transition fit; inputs = inputs with total effect > 1% (of 8); baselines: random linear (W1 = 1) / random sine map.

| net | chain | lambda | rate by layer | own nMSE | chain nMSE | W1 of T | R2 of T | inputs | baselines lin/sine |
|---|---|---|---|---|---|---|---|---|---|
| relu | n16_L16_s5000_local | 0.03 | [9.8, 4.2, 3.6, 5.0, 3.2] | [0.197, 0.15, 0.104, 0.105, 0.142] | [0.197, 0.241, 0.269, 0.297, 0.338] | [0.84, 0.98, 0.95, 0.97] | [0.86, 0.92, 0.94, 0.95] | [7, 5, 3, 4] | 0.998 / 0.024 |
| relu | n16_L16_s5000_local | 0.01 | [13.4, 6.0, 7.2, 8.1, 5.3] | [0.183, 0.121, 0.08, 0.074, 0.105] | [0.183, 0.215, 0.238, 0.259, 0.294] | [0.74, 0.97, 0.97, 0.96] | [0.87, 0.93, 0.95, 0.96] | [8, 6, 7, 6] | 0.994 / 0.018 |
| relu | n16_L16_s5000_local | 0.003 | [13.8, 8.2, 9.5, 8.5, 7.5] | [0.188, 0.114, 0.066, 0.055, 0.073] | [0.188, 0.219, 0.235, 0.25, 0.274] | [0.82, 0.98, 0.96, 0.96] | [0.86, 0.94, 0.96, 0.97] | [8, 7, 6, 7] | 1.000 / 0.025 |

# S10 compressed simulator (final-layer nMSE by transition class; deductive error vs MC/RQMC)

| net | class | rate c0 | nMSE at each grid layer (lambda 0.01) | final nMSE (0.01 / 0.001) | deductive err N=4096 / 65536 | MC / RQMC at 65536 |
|---|---|---|---|---|---|---|
| relu 16x16 | linear | [11.8, 12.2] | [0.266, 0.277, 0.282, 0.284, 0.286] | 0.286 / 0.27 | 8.2e-05 / 7.8e-05 | 4.9e-05 / 4.1e-07 |
| relu 16x16 | mlp | [12.3, 12.2] | [0.23, 0.23, 0.23, 0.229, 0.229] | 0.229 / 0.247 | - | 4.9e-05 / 4.1e-07 |
| relu 32x32 | linear | [12.1, 13.3] | [0.454, 0.467, 0.474, 0.478, 0.481] | 0.481 / 0.457 | 1.1e-04 / 1.2e-04 | 3.5e-05 / 2.7e-07 |
| relu 32x32 | mlp | [12.6, 13.2] | [0.409, 0.411, 0.412, 0.412, 0.412] | 0.412 / 0.401 | - | 3.5e-05 / 2.7e-07 |

# S11: bits by layer (gfix R(0.1), fixed-noise real code) for the controls vs ReLU 16 x 16 seed 5000

| net | class | l = 0 | 4 | 8 | 12 | 15 | out |
|---|---|---|---|---|---|---|---|
| relu | local | unreached | 3.4 | - | - | - | - |
| relu | unres | 2.6 | - | - | - | - | - |
| tanh4 | local | - | - | - | - | - | - |
| tanh4 | unres | - | - | - | - | - | - |
| feistel | local | - | - | - | - | - | - |
| feistel | unres | - | - | - | - | - | - |
