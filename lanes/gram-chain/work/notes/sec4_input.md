## 4. The bits that matter at layer l: input regime (sigma = 0, replicas = inputs; Part B)

4.1 How many directions: the input cloud's dimension is a four-point-vertex effect (HEURISTIC theory [C+A]; NUMERICAL
check, PB6 hit). At infinite width independent inputs are equicorrelated at every layer (correlation c_l, the kernel
iterate), so the infinite-width cloud is isotropic and the kernel says nothing about its dimension. Its anisotropy is a
1/n effect: for four inputs the double difference D = (u1 - u2).(u3 - u4) is free of radial fluctuations at linear
order and obeys D' = kappa'(c_l) D + zeta_l with Var zeta_l = E[(relu z1 - relu z2)^2 (relu z3 - relu z4)^2] (four
equicorrelated Gaussians, unit radius). The angular participation ratio is PR(l) = 4n(1 - c_l)^2 / Var D_l, and at depth
(theta_l ~ 3 pi/l, Var zeta ~ 2 theta^4, kappa' ~ 1 - theta/pi) PR(l) ~ 1.5 n/l.

| l | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 127 |
|---|---|---|---|---|---|---|---|---|
| exact chain, n = 256 (4 replicas, PR_w) | 166 | 110 | 62 | 36 | 18.8 | 12.1 | 6.1 | 3.6 |
| vertex recursion, n = 256 | 167 | 107 | 62 | 34 | 18.9 | 10.3 | 5.3 | 2.0 |
| input-bits nets, n = 256 (MEASURED there) | 159 | - | 57 | - | 17 | 9.6 | 6.1 | 3.6 (l = 128) |
| exact chain, n = 64 | 40.9 | 26.3 | 15.5 | 9.1 | 5.2 | 3.0 | - | - |
| vertex recursion, n = 64 | 41.7 | 26.8 | 15.4 | 8.6 | 4.7 | 2.6 | - | - |

The leading-order vertex is within 1-2% of the exact chain up to l = 16 and within 17% at l = 32-64; it fails at
l ~ n/2 (PR = O(1), where the 1/n expansion is not valid). So at ARC's 256 x 32 the input's directional information lives
in about 12 effective directions at the last layer (input-bits found "about 10"), and in general in about 1.5 n/l. This
is the input-regime answer to "how many bits matter at layer l": all the input's variance is relevant (the future is
deterministic at sigma = 0), and it lives in about 1.5 n/l angular directions plus the radius.

4.2 What carries it (PROVEN identity, kernel HEURISTIC, NUMERICAL check, PB7 hit). At sigma = 0, a = |h_l| F_l(u_l)
exactly, so log|a| = log|h_l| + log A_l(u_l): the radius at layer l carries the amplitude collected so far and the
direction carries the output direction plus the amplitude still to come. With the input-bits lane's per-layer gain
covariance, E_W Var_x(log|h_l|) = (1/2 + C_l)/n with C_l = (1/4) sum_{j<l} (5 - B(c_j)). Exact chain at 256 x 32:
the share of E_W Var_x(log|a|) carried by log|h_l| is 0.187, 0.288, 0.455, 0.643, 0.823, 0.925, 0.990 at l = 1, 2, 4, 8, 16,
24, 31, against the kernel's 0.19, 0.30, 0.46, 0.66, 0.85, 0.94, 0.99 (within 4% everywhere); the absolute values agree
too (Var_x(log|a|) = 0.0357 chain vs 0.0354 kernel). gpt-6-astra computed the raw-a version by an exact change of measure
(radius surgery removes 0.04, 0.31, 0.56, 0.63 of Var_x(a) at l = 0, 4, 16, 31): for raw a the radius never carries the
output direction's half, which is why that share saturates near 0.63.

4.3 Narrow-deep 8 x 256 (NUMERICAL; PB8 hit). Two effects dominate. (i) Extinction: an all-off layer (probability 2^-8
for any live state) kills the state; the chain's alive fraction is 0.377 at l = 255 against the exact (1 - 2^-8)^255 =
0.369, and 35% of input pairs are both alive at the output. (ii) Collapse: the input cloud's angular PR is 5.2, 2.3, 1.5,
1.3 at l = 1, 4, 8, 16 and about 1.1-1.4 afterwards: below l ~ 8 the input is one direction plus the radius (the
relevance lane predicts N = 1 there; the chain agrees on the dimension).

4.4 Small noise (descriptive runs). At 256 x 32 noise of sigma = 1e-3 or 1e-2 leaves the input cloud's dimension and the
radius shares unchanged (PR 168.9 / 60.5 / 18.8 / 11.3 at l = 1, 4, 16, 31 for sigma = 1e-3); sigma = 0.1 adds noise
directions at depth (PR 39.9 at l = 16, 48.0 at l = 31) and quadruples the output direction's variance. At 8 x 256 any
sigma >= 1e-3 ends the input regime within about 30-40 layers (the noise floor, T_mem = 40 layers at sigma = 1e-3): the
cloud's PR rises to about 6 of 8 and extinction disappears (99% of pairs alive). {{INPUTVP}}
