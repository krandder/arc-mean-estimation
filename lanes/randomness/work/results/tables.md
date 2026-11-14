### Table A. 256 x 32, per net: harmonic shares of the radius-exact variance and Haar-randomised design gains over plain MC (E1)

| net | V | V_rb/V | odd | even | deg 1 | deg 2 | even >= 4 | even >= 6 | ONB | simplex | cross | Kerdock | T4 ceiling (vs MC) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 200 | 21.2 | 0.940 | 0.585 | 0.417 | 0.44 | 0.18 | 0.174 | 0.113 | 1.30 | 2.79 | 3.06 | 4.69 | 18.8 |
| 201 | 30.7 | 0.972 | 0.556 | 0.443 | 0.32 | 0.15 | 0.241 | 0.169 | 1.21 | 1.93 | 2.13 | 3.04 | 12.1 |
| 202 | 11.9 | 0.960 | 0.572 | 0.432 | 0.49 | -0.02 | 0.218 | 0.161 | 1.02 | 1.97 | 2.39 | 3.24 | 13.0 |
| 203 | 5.4 | 0.981 | 0.563 | 0.432 | 0.25 | 0.18 | 0.201 | 0.186 | 1.25 | 1.81 | 2.54 | 2.74 | 11.0 |
| 204 | 4.8 | 0.981 | 0.531 | 0.459 | 0.05 | 0.21 | 0.308 | 0.212 | 1.29 | 1.38 | 1.66 | 2.40 | 9.6 |

### Table B. Along L = n/8: medians over nets [min, max] (8 nets at n = 32, 64, 128; 5 at 256). Gains are over plain MC at equal points unless stated (E1)

| quantity | n = 32, L = 4 | n = 64, L = 8 | n = 128, L = 16 | n = 256, L = 32 |
|---|---|---|---|---|
| V_rb / V | 0.96 [0.94, 0.97] | 0.96 [0.95, 0.97] | 0.96 [0.95, 0.97] | 0.97 [0.94, 0.98] |
| odd share | 0.63 [0.61, 0.64] | 0.59 [0.57, 0.64] | 0.58 [0.54, 0.59] | 0.56 [0.53, 0.58] |
| degree-1 share | 0.47 [0.40, 0.58] | 0.38 [0.31, 0.42] | 0.29 [0.13, 0.37] | 0.32 [0.05, 0.49] |
| degree-2 share | 0.28 [0.22, 0.36] | 0.27 [0.23, 0.34] | 0.24 [0.08, 0.31] | 0.18 [-0.02, 0.21] |
| even >= 4 share | 0.09 [0.07, 0.11] | 0.15 [0.11, 0.18] | 0.20 [0.16, 0.31] | 0.22 [0.17, 0.31] |
| gain: orthonormal basis | 1.46 [1.33, 1.62] | 1.43 [1.35, 1.58] | 1.37 [1.12, 1.52] | 1.25 [1.02, 1.30] |
| gain: simplex (2-design) | 4.49 [3.58, 5.61] | 2.82 [2.54, 4.05] | 2.10 [1.52, 2.86] | 1.93 [1.38, 2.79] |
| gain: cross-polytope (antipodal 3-design) | 5.52 [4.74, 7.27] | 3.50 [2.91, 4.98] | 2.58 [1.67, 3.20] | 2.39 [1.66, 3.06] |
| gain: Kerdock (antipodal 5-design) | - | - | - | 3.04 [2.40, 4.69] |
| gain: scrambled Sobol, 2^14 | 5.29 [4.42, 6.89] | 3.26 [2.43, 4.90] | 2.37 [1.61, 3.04] | 1.87 [1.42, 2.42] |
| gain: scrambled Sobol, polar frame, 2^14 | 6.53 [5.93, 8.57] | 3.43 [2.27, 5.69] | 2.80 [1.80, 4.35] | 2.50 [1.54, 3.32] |
| gain: scrambled Sobol, SVD frame, 2^14 | 9.23 [7.30, 11.88] | 3.70 [3.03, 5.35] | 2.34 [1.84, 3.41] | 1.84 [1.58, 3.22] |
| gain: antipodal Sobol, 2^14 | 4.84 [3.84, 6.89] | 3.10 [2.29, 4.27] | 2.32 [1.67, 3.36] | 2.06 [1.78, 3.80] |
| multilevel prefix control, gain vs RB-MC | 0.83 [0.79, 0.86] | 0.86 [0.76, 0.93] | 0.94 [0.90, 0.97] | 0.99 [0.96, 1.03] |

### Table C. ARC's budget, 256 x 32 (E2): N = 2^16 points (Kerdock 66,048), radius exact, nMSE against the truth; gain = 1 / (nMSE x N), plain MC = 1

| sampler | random bits | net 200 | 201 | 202 | 203 | 204 | median gain |
|---|---|---|---|---|---|---|---|
| pairwise-independent MC | 16384 | 1.70 | 1.53 | 1.61 | 0.40 | 0.95 | 1.53 |
| scrambled Sobol (black-box) | 135168 | 2.77 | 1.97 | 2.13 | 2.15 | 1.95 | 2.13 |
| scrambled Sobol, polar frame of W_1 (white-box) | 135168 | 2.64 | 1.83 | 2.22 | 2.47 | 1.87 | 2.22 |
| Kerdock 5-design, Haar rotation | 1044480 | 3.93 | 3.15 | 2.79 | 2.89 | 2.20 | 2.89 |
| centred Sobol, fixed | 0 | 1.84 | 1.78 | 5.55 | 3.06 | 2.07 | 2.07 |
| centred Sobol, polar frame, fixed | 0 | 0.83 | 3.27 | 2.41 | 4.35 | 2.68 | 2.68 |

### Table D. Gate perimeter and noise sensitivity (E3): medians over nets

| n x L | layer-1 GSA / (n/sqrt(2 pi)) | total / (nL/sqrt(2 pi)) [min, max] | P(some gate changes), delta = 1e-6 | output NS slope (mean Hermite degree) | n / V |
|---|---|---|---|---|---|
| 32 x 4 | 1.008 | 1.010 [0.92, 1.11] | 0.054 | 2.9 | 3.0 |
| 64 x 8 | 0.988 | 0.943 [0.89, 1.02] | 0.191 | 5.1 | 4.7 |
| 128 x 16 | 0.992 | 0.910 [0.80, 1.20] | 0.566 | 8.6 | 10.8 |
| 256 x 32 | 1.008 | 1.006 [0.77, 1.07] | 0.964 | 18.6 | 21.6 |

### Table E. Zero-random-bit point sets against the truth (E4): median nMSE x N over nets (plain MC = 1); k-wise rows give N = q^k

| n x L | centred Sobol 2^10 / 2^14 / 2^16 | Sobol, polar frame 2^10 / 2^14 / 2^16 | Korobov lattice 2^14 | k-wise k = 2 | k = 3 | k = 4 | Kerdock fixed / polar-aligned |
|---|---|---|---|---|---|---|---|
| 32 x 4 | 0.24 (8/8) / 0.17 (8/8) / 0.11 (8/8) | 0.18 (8/8) / 0.14 (8/8) / 0.08 (8/8) | 0.36 (8/8) | 0.31 (8/8) | 0.41 (8/8) | 0.51 (2/8) | - / - |
| 64 x 8 | 0.33 (8/8) / 0.27 (8/8) / 0.24 (8/8) | 0.22 (8/8) / 0.37 (8/8) / 0.19 (8/8) | 0.56 (8/8) | 0.62 (8/8) | 0.99 (8/8) | 4.90 (1/8) | - / - |
| 128 x 16 | 0.32 (8/8) / 0.51 (8/8) / 0.33 (8/8) | 0.68 (8/8) / 0.42 (8/8) / 0.38 (8/8) | 0.88 (8/8) | 1.86 (8/8) | 1.49 (8/8) | - | - / - |
| 256 x 32 | 0.45 (5/5) / 0.34 (5/5) / 0.48 (5/5) | 0.64 (5/5) / 0.33 (5/5) / 0.37 (5/5) | 0.53 (5/5) | 1.90 (5/5) | - | - | 0.56 (5/5) / 95.94 (5/5) |

(Each cell: median over the nets resolved above 3x the truth floor, with (resolved / run) nets; - = not run. k-wise cells with few resolved nets are not evidence about k.)

