# P2.0 parts 2-4: the code map from layer l to l+1 against the layer map (lambda = 0.01; medians over seeds)

T lin / T mlp = R^2 of the best affine / MLP map from the code at l to the code at l+1 (held out); path = R^2 of the layer path (decode at l, real layer l+1, encode at l+1) against the true next code; agree = R^2 between the MLP map and the layer path; lin share = R^2 of an affine fit to each map; gates = share of layer-(l+1) units whose gate the code at l predicts with accuracy >= 0.95 (top / bottom quartile of gradient energy); rot = mean cos^2 between the next code's subspace and the image of this code's subspace under the cloud-averaged Jacobian (identity image in brackets).

| net | l -> l+1 | class | T lin | T mlp | path | agree | lin share T / path | lin share T at lambda 0.1 / 0.001 | gates tracked (top / bottom energy) | rot (identity) | seeds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| relu 16x16 | input | local | 0.74 | 1.00 | 0.94 | 0.93 | 0.74 / 0.74 | 0.72 / 0.73 | 1.00 (1.00 / 1.00) | 0.89 (0.65) | 3 |
| relu 16x16 | input | unres | 1.00 | 0.99 | 0.98 | 0.97 | 0.99 / 0.98 | 0.99 / 0.98 | 0.00 (0.00 / 0.00) | 0.89 (0.14) | 3 |
| relu 16x16 | L/4 | local | 0.98 | 1.00 | 0.97 | 0.97 | 0.98 / 0.98 | 0.98 / 0.98 | 1.00 (1.00 / 1.00) | 0.51 (0.24) | 3 |
| relu 16x16 | L/4 | unres | 1.00 | 0.99 | 0.99 | 0.98 | 0.99 / 0.99 | 0.99 / 0.99 | 0.25 (0.25 / 0.50) | 0.49 (0.23) | 3 |
| relu 16x16 | L/2 | local | 0.99 | 1.00 | 0.98 | 0.97 | 0.99 / 0.98 | 0.99 / 0.99 | 1.00 (1.00 / 1.00) | 0.30 (0.16) | 3 |
| relu 16x16 | L/2 | unres | 1.00 | 0.99 | 0.99 | 0.98 | 0.99 / 0.99 | 0.99 / 0.99 | 0.62 (0.75 / 1.00) | 0.22 (0.15) | 3 |
| relu 16x16 | 3L/4 | local | 1.00 | 1.00 | 0.98 | 0.98 | 1.00 / 0.99 | 1.00 / 1.00 | 1.00 (1.00 / 1.00) | 0.24 (0.19) | 3 |
| relu 16x16 | 3L/4 | unres | 1.00 | 1.00 | 0.99 | 0.98 | 1.00 / 0.99 | 1.00 / 1.00 | 0.81 (0.75 / 1.00) | 0.23 (0.09) | 3 |
| relu 32x32 | input | local | 0.73 | 1.00 | 0.76 | 0.71 | 0.73 / 0.78 | 0.70 / 0.73 | 1.00 (1.00 / 1.00) | 0.90 (0.30) | 3 |
| relu 32x32 | input | unres | 1.00 | 0.97 | 0.99 | 0.97 | 0.98 / 0.99 | 0.98 / 0.98 | 0.00 (0.00 / 0.00) | 0.92 (0.03) | 3 |
| relu 32x32 | L/4 | local | 0.99 | 0.99 | 0.96 | 0.95 | 0.98 / 0.98 | 0.99 / 0.98 | 1.00 (1.00 / 1.00) | 0.24 (0.12) | 3 |
| relu 32x32 | L/4 | unres | 1.00 | 0.98 | 0.99 | 0.96 | 0.98 / 0.99 | 0.98 / 0.98 | 0.59 (0.62 / 1.00) | 0.18 (0.00) | 3 |
| relu 32x32 | L/2 | local | 0.79 | 1.00 | 0.98 | 0.98 | 0.66 / -0.64 | 0.70 / 1.00 | 1.00 (1.00 / 1.00) | 0.16 (0.04) | 3 |
| relu 32x32 | L/2 | unres | 1.00 | 0.99 | 0.99 | 0.98 | 0.99 / 0.99 | 0.99 / 0.99 | 0.94 (1.00 / 1.00) | 0.24 (0.04) | 3 |
| relu 32x32 | 3L/4 | local | 0.72 | 1.00 | 0.99 | 0.99 | -1.38 / -23.59 | 0.67 / -1.99 | 1.00 (1.00 / 1.00) | 0.00 (0.00) | 3 |
| relu 32x32 | 3L/4 | unres | 1.00 | 0.99 | 0.99 | 0.98 | 0.99 / 0.99 | 0.99 / 0.99 | 1.00 (1.00 / 1.00) | 0.00 (0.00) | 3 |
| tanh4 16x16 | input | local | 0.85 | 1.00 | 1.00 | 1.00 | 0.85 / 0.85 | 0.84 / 0.85 | 1.00 (1.00 / 1.00) | 0.95 (0.93) | 1 |
| tanh4 16x16 | input | unres | 0.84 | 0.94 | 0.92 | 0.91 | 0.88 / 0.82 | 0.96 / 0.85 | 0.88 (0.75 / 1.00) | 0.99 (0.85) | 1 |
| tanh4 16x16 | L/4 | local | 0.94 | 1.00 | 0.99 | 0.99 | 0.94 / 0.94 | 0.95 / 0.93 | 1.00 (1.00 / 1.00) | 0.84 (0.71) | 1 |
| tanh4 16x16 | L/4 | unres | 0.93 | 0.96 | 0.91 | 0.92 | 0.95 / 0.92 | 0.98 / 0.93 | 0.00 (0.00 / 0.00) | 0.81 (0.12) | 1 |
| tanh4 16x16 | L/2 | local | 0.96 | 1.00 | 0.98 | 0.98 | 0.96 / 0.96 | 0.97 / 0.96 | 1.00 (1.00 / 1.00) | 0.80 (0.45) | 1 |
| tanh4 16x16 | L/2 | unres | 0.98 | 0.98 | 0.96 | 0.95 | 0.98 / 0.96 | 0.99 / 0.97 | 0.00 (0.00 / 0.00) | 0.83 (0.34) | 1 |
| tanh4 16x16 | 3L/4 | local | 0.96 | 1.00 | 0.96 | 0.95 | 0.96 / 0.96 | 0.97 / 0.96 | 1.00 (1.00 / 1.00) | 0.77 (0.35) | 1 |
| tanh4 16x16 | 3L/4 | unres | 0.97 | 0.99 | 0.97 | 0.95 | 0.98 / 0.95 | 0.99 / 0.98 | 0.19 (0.25 / 0.00) | 0.81 (0.37) | 1 |

## Registered predictions (P2.0)

- H2: {"relu": "36/36", "tanh4_below_0_5": "0/8", "hit": false}
- H3: {"relu": "25/36", "hit": false}
- H4: {"relu_median": 0.2394487749111303, "tanh4_median": 0.8229517365829833, "hit": false}
