### Table C. ARC's budget, 256 x 32 (E2): N = 2^16 points (Kerdock 66,048), radius exact, nMSE against the truth; gain = 1 / (nMSE x N), plain MC = 1

| sampler | random bits | net 200 | 201 | 202 | 203 | 204 | median gain |
|---|---|---|---|---|---|---|---|
| pairwise-independent MC | 16384 | 1.70 | 1.53 | 1.61 | 0.40 | 0.95 | 1.53 |
| scrambled Sobol (black-box) | 135168 | 2.77 | 1.97 | 2.13 | 2.15 | 1.95 | 2.13 |
| scrambled Sobol, polar frame of W_1 (white-box) | 135168 | 2.64 | 1.83 | 2.22 | 2.47 | 1.87 | 2.22 |
| Kerdock 5-design, Haar rotation | 1044480 | 3.93 | 3.15 | 2.79 | 2.89 | 2.20 | 2.89 |
| centred Sobol, fixed | 0 | 1.84 | 1.78 | 5.55 | 3.06 | 2.07 | 2.07 |
| centred Sobol, polar frame, fixed | 0 | 0.83 | 3.27 | 2.41 | 4.35 | 2.68 | 2.68 |