# P2.0 part 1: how linear are the anchored codes, and what does linearity cost? (medians over seeds and the prices lambda = 0.1, 0.01; error levels 10% and 1%)

lin share = R^2 of the best linear map from the layer state to the code mean (1 = the code is a linear function of the layer). k = code directions above the noise. cos^2 G = mean cos^2 of the principal angles between the code's directions and the top-k eigenvectors of G = E[J^T J] (the Jacobian linearisation from the output back to this layer); G capture = the share of G's energy the code's directions capture relative to the best k directions. gates = share of local ReLU units switching inside the data cloud (0 = affine on the data). Price of linearity = bits of the linear reference code (G's directions, water-filled power, linear MMSE decoding, real net) / bits of the best code found (R*) or of the anchored single model (r0). Explorer / linear = bits of the best local code with gates inside the cloud / bits of the linear reference.

| net | layer | class | lin share | k | cos^2 G | G capture | gates (anchored) | gates (explorer) | linear / R* | linear / r0 | explorer / linear | cells |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| relu 16x16 | input | local | 1.000 | 4 | 1.00 | 1.00 | 0.00 | 1.00 | 1.17 | 1.00 | 0.85 | 3 |
| relu 16x16 | input | unres | 0.417 | 2 | 0.56 | 0.82 | - | - | 9.40 | 8.52 | - | 3 |
| relu 16x16 | L/4 | local | 1.000 | 2 | 0.98 | 0.98 | 0.00 | 0.78 | 1.68 | 1.40 | 0.60 | 3 |
| relu 16x16 | L/4 | unres | 0.903 | 2 | 0.90 | 0.91 | - | - | 2.90 | 2.85 | - | 3 |
| relu 16x16 | L/2 | local | 1.000 | 2 | 0.96 | 0.97 | 0.00 | 0.56 | 1.88 | 1.55 | 0.53 | 3 |
| relu 16x16 | L/2 | unres | 0.975 | 2 | 0.94 | 0.95 | - | - | 2.15 | 2.12 | - | 3 |
| relu 16x16 | 3L/4 to L-1 | local | 1.000 | 2 | 0.97 | 0.99 | 0.00 | 0.41 | 1.35 | 1.31 | 0.74 | 6 |
| relu 16x16 | 3L/4 to L-1 | unres | 0.992 | 2 | 0.96 | 0.99 | - | - | 1.39 | 1.37 | - | 6 |
| relu 16x16 | output | unres | 0.993 | 2 | 0.99 | 1.00 | - | - | 1.33 | 1.33 | - | 3 |
| relu 16x4 | input | local | 1.000 | 5 | 1.00 | 1.00 | 0.00 | 1.00 | 1.39 | 1.00 | 0.72 | 3 |
| relu 16x4 | input | unres | 0.533 | 4 | 0.80 | 0.92 | - | - | 2.93 | 2.78 | - | 3 |
| relu 16x4 | L/4 | local | 1.000 | 4 | 0.95 | 0.98 | 0.00 | 0.97 | 1.51 | 1.17 | 0.66 | 3 |
| relu 16x4 | L/4 | unres | 0.813 | 4 | 0.76 | 0.92 | - | - | 2.34 | 2.12 | - | 3 |
| relu 16x4 | L/2 | local | 1.000 | 4 | 0.97 | 0.98 | 0.00 | 0.88 | 1.49 | 1.27 | 0.67 | 3 |
| relu 16x4 | L/2 | unres | 0.887 | 4 | 0.89 | 0.96 | - | - | 1.77 | 1.74 | - | 3 |
| relu 16x4 | 3L/4 to L-1 | local | 1.000 | 4 | 0.98 | 0.99 | 0.00 | 0.66 | 1.37 | 1.29 | 0.73 | 3 |
| relu 16x4 | 3L/4 to L-1 | unres | 0.964 | 4 | 0.96 | 0.98 | - | - | 1.49 | 1.46 | - | 3 |
| relu 16x4 | output | unres | 0.977 | 4 | 0.94 | 0.99 | - | - | 1.61 | 1.58 | - | 3 |
| relu 32x32 | input | local | 1.000 | 4 | 0.91 | 0.97 | 0.00 | 1.00 | 1.12 | 1.00 | 0.90 | 3 |
| relu 32x32 | input | unres | 0.487 | 1 | 0.75 | 0.87 | - | - | 24.12 | 23.64 | - | 3 |
| relu 32x32 | L/4 | local | 1.000 | 2 | 0.49 | 0.42 | 0.00 | 0.47 | 1.81 | 1.39 | 0.55 | 3 |
| relu 32x32 | L/4 | unres | 0.939 | 1 | 0.00 | 0.00 | - | - | 3.82 | 3.79 | - | 3 |
| relu 32x32 | L/2 | local | 1.000 | 1 | 0.00 | 0.00 | 0.00 | 0.23 | 1.27 | 1.19 | 0.79 | 3 |
| relu 32x32 | L/2 | unres | 0.992 | 1 | 0.00 | 0.00 | - | - | 1.34 | 1.33 | - | 3 |
| relu 32x32 | 3L/4 to L-1 | local | 1.000 | 1 | 0.74 | 0.58 | 0.00 | 0.12 | 1.08 | 1.08 | 0.93 | 6 |
| relu 32x32 | 3L/4 to L-1 | unres | 0.999 | 1 | 0.74 | 0.93 | - | - | 1.09 | 1.09 | - | 6 |
| relu 32x32 | output | unres | 0.999 | 1 | 1.00 | 1.00 | - | - | 1.09 | 1.08 | - | 3 |
| relu 32x8 | input | local | 1.000 | 6 | 0.98 | 0.99 | 0.00 | 1.00 | 1.33 | 1.00 | 0.76 | 3 |
| relu 32x8 | input | unres | 0.505 | 4 | 0.70 | 0.89 | - | - | 4.23 | 3.86 | - | 3 |
| relu 32x8 | L/4 | local | 1.000 | 4 | 0.97 | 0.98 | 0.00 | 0.84 | 1.67 | 1.17 | 0.61 | 3 |
| relu 32x8 | L/4 | unres | 0.865 | 3 | 0.90 | 0.93 | - | - | 2.86 | 2.80 | - | 3 |
| relu 32x8 | L/2 | local | 1.000 | 4 | 0.99 | 1.00 | 0.00 | 0.72 | 1.47 | 1.23 | 0.68 | 3 |
| relu 32x8 | L/2 | unres | 0.947 | 4 | 0.92 | 0.97 | - | - | 1.83 | 1.75 | - | 3 |
| relu 32x8 | 3L/4 to L-1 | local | 1.000 | 4 | 0.98 | 1.00 | 0.00 | 0.42 | 1.29 | 1.26 | 0.75 | 6 |
| relu 32x8 | 3L/4 to L-1 | unres | 0.987 | 3 | 0.97 | 0.99 | - | - | 1.40 | 1.39 | - | 6 |
| relu 32x8 | output | unres | 0.993 | 4 | 0.95 | 0.99 | - | - | 1.59 | 1.56 | - | 3 |
| feistel 16x16 | input | local | 1.000 | 0 | - | - | 0.00 | - | - | - | - | 1 |
| feistel 16x16 | input | unres | 0.575 | 0 | - | - | - | - | - | - | - | 1 |
| feistel 16x16 | L/4 | local | 1.000 | 0 | - | - | 0.00 | - | - | - | - | 1 |
| feistel 16x16 | L/4 | unres | 0.505 | 0 | - | - | - | - | - | - | - | 1 |
| feistel 16x16 | L/2 | local | 1.000 | 0 | - | - | 0.00 | - | - | - | - | 1 |
| feistel 16x16 | L/2 | unres | 0.553 | 0 | - | - | - | - | - | - | - | 1 |
| feistel 16x16 | 3L/4 to L-1 | local | 1.000 | 8 | 1.00 | 1.00 | 0.00 | - | 4.92 | 4.57 | - | 2 |
| feistel 16x16 | 3L/4 to L-1 | unres | 1.000 | 16 | 1.00 | 1.00 | - | - | 4.85 | 4.60 | - | 2 |
| feistel 16x16 | output | unres | 1.000 | 8 | 1.00 | 1.00 | - | - | 1.74 | 1.65 | - | 1 |
| linear 16x16 | input | local | 1.000 | 2 | 1.00 | 1.00 | 0.00 | - | 0.99 | 0.99 | - | 1 |
| linear 16x16 | input | unres | 1.000 | 2 | 1.00 | 1.00 | - | - | 0.99 | 0.99 | - | 1 |
| linear 16x16 | L/4 | local | 1.000 | 2 | 1.00 | 1.00 | 0.00 | - | 0.99 | 0.99 | - | 1 |
| linear 16x16 | L/4 | unres | 1.000 | 2 | 1.00 | 1.00 | - | - | 0.99 | 0.99 | - | 1 |
| linear 16x16 | L/2 | local | 1.000 | 2 | 1.00 | 1.00 | 0.00 | - | 0.99 | 0.99 | - | 1 |
| linear 16x16 | L/2 | unres | 1.000 | 2 | 0.99 | 0.99 | - | - | 0.99 | 0.99 | - | 1 |
| linear 16x16 | 3L/4 to L-1 | local | 1.000 | 2 | 1.00 | 1.00 | 0.00 | - | 0.99 | 0.99 | - | 2 |
| linear 16x16 | 3L/4 to L-1 | unres | 1.000 | 2 | 1.00 | 1.00 | - | - | 0.99 | 0.99 | - | 2 |
| linear 16x16 | output | unres | 1.000 | 2 | 1.00 | 1.00 | - | - | 0.99 | 0.99 | - | 1 |
| tanh4 16x16 | input | local | 1.000 | 8 | 0.95 | 0.99 | 0.00 | - | 1.00 | 0.99 | - | 1 |
| tanh4 16x16 | input | unres | 0.626 | 8 | 0.71 | 0.81 | - | - | 1.01 | 1.01 | - | 1 |
| tanh4 16x16 | L/4 | local | 1.000 | 6 | 1.00 | 1.00 | 0.00 | - | 1.06 | 1.03 | - | 1 |
| tanh4 16x16 | L/4 | unres | 0.531 | 4 | 0.86 | 0.91 | - | - | 2.63 | 1.24 | - | 1 |
| tanh4 16x16 | L/2 | local | 1.000 | 5 | 0.99 | 0.99 | 0.00 | - | 1.26 | 1.17 | - | 1 |
| tanh4 16x16 | L/2 | unres | 0.727 | 4 | 0.90 | 0.93 | - | - | 2.40 | 2.23 | - | 1 |
| tanh4 16x16 | 3L/4 to L-1 | local | 1.000 | 4 | 0.98 | 0.99 | 0.00 | - | 1.52 | 1.48 | - | 2 |
| tanh4 16x16 | 3L/4 to L-1 | unres | 0.939 | 4 | 0.94 | 0.97 | - | - | 2.12 | 1.95 | - | 2 |
| tanh4 16x16 | output | unres | 0.977 | 4 | 0.97 | 0.98 | - | - | 2.08 | 1.90 | - | 1 |
