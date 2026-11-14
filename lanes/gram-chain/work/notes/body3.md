## 4. The bits that matter at layer l: input regime (sigma = 0, replicas = inputs; Part B)

4.1 How many directions: the input cloud's dimension is a four-point-vertex effect (HEURISTIC theory [C+A]; NUMERICAL;
PB6 hit). At infinite width independent inputs are equicorrelated at every layer (correlation c_l, the kernel iterate), so
the infinite-width cloud is isotropic and the kernel says nothing about its dimension. Its anisotropy is a 1/n effect: for
four inputs the scaled double difference D = sqrt(n) (u1 - u2).(u3 - u4) has no radial term at linear order and obeys
D' = kappa'(c_l) D + zeta_l, Var zeta_l = E[(relu z1 - relu z2)^2 (relu z3 - relu z4)^2] (four equicorrelated Gaussians of
unit radius), Var D_0 = 4. The angular participation ratio is PR(l) = 4n(1 - c_l)^2 / Var D_l, and at depth
(theta_l ~ 3 pi/l, Var zeta ~ 2 theta^4, kappa' ~ 1 - theta/pi) PR(l) ~ 1.5 n/l. Correction after review: the first
numerical recursion interpolated a Monte Carlo source on a 201-point grid in c, which near c = 1 turns its quadratic
vanishing into linear and wrongly made the recursion collapse at depth; with the source by quadrature
(`scratch/vertex_exact.py`) the recursion tends to 1.5 n/l (PR/n = 0.650, 0.240, 0.0732, 0.0397, 0.0211, 0.0110, 0.0057 at
l = 1, 4, 16, 32, 64, 128, 256). The registered PB6 targets came from the first version; they differ from the corrected
values by under 2% at l <= 64.

| l | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 127 |
|---|---|---|---|---|---|---|---|---|
| exact chain, n = 256 (4 inputs, PR_w) | 166 | 110 | 62 | 36 | 18.8 | 12.1 | 6.1 | 3.6 |
| vertex recursion (quadrature), n = 256 | 166 | 107 | 61 | 34 | 18.7 | 10.2 | 5.4 | 2.8 |
| input-bits nets, n = 256 (MEASURED there) | 159 | - | 57 | - | 17 | 9.6 | 6.1 | 3.6 (l = 128) |
| exact chain, n = 64 | 40.9 | 26.3 | 15.5 | 9.1 | 5.2 | 3.0 | - | - |
| vertex recursion (quadrature), n = 64 | 41.6 | 26.7 | 15.3 | 8.5 | 4.7 | 2.5 | - | - |

The leading-order vertex is within 1-3% of the exact chain up to l = 16 (n = 256) and 11-27% below it at l = 32-127
(n = 256) and l = 16-32 (n = 64): the finite-width corrections grow as the PR falls toward O(1). (`figs/fig4_input.png`.) So at ARC's 256 x 32 the input's directional information lives
in about 12 effective directions at the last layer (the input-bits lane found "about 10"). The input-regime answer to "how
many bits matter at layer l": at sigma = 0 all of the input's variance is relevant at every layer (the future is
deterministic), and it lives in about 1.5 n/l angular directions plus the radius. The same structure as the stationary
cloud's (width x angular contraction rate theta/pi, halved for a decaying transient). The free-product formula does not
apply here (finite input differences are far outside the future's coherence radius).

4.2 What carries it (identity PROVEN, kernel HEURISTIC, NUMERICAL; PB7 hit). At sigma = 0, a = |h_l| F_l(u_l) exactly, so
log|a| = log|h_l| + log A_l(u_l): the radius at layer l carries the amplitude collected so far, the direction carries the
output direction and the amplitude still to come. With the input-bits lane's per-layer gain covariance,
E_W Var_x(log|h_l|) = (1/2 + C_l)/n, C_l = (1/4) sum_{j<l} (5 - B(c_j)). Exact chain at 256 x 32: the share of
E_W Var_x(log|a|) carried by log|h_l| is 0.187, 0.288, 0.455, 0.643, 0.823, 0.925, 0.990 at l = 1, 2, 4, 8, 16, 24, 31, against
the kernel's 0.19, 0.30, 0.46, 0.66, 0.85, 0.94, 0.99 (within 4%); the absolute value agrees too (0.0357 against 0.0354).
gpt-6-astra computed the raw-a version by an exact change of measure (radius surgery removes 0.04, 0.31, 0.56, 0.63 of
Var_x(a) at l = 0, 4, 16, 31): for raw a the radius never carries the output direction's share.

4.3 Narrow-deep 8 x 256 (NUMERICAL; PB8 hit). Extinction: an all-off layer (probability 2^-8 for any live state) kills the
state; the chain's alive fraction is 0.377 at l = 255 against the exact (1 - 2^-8)^255 = 0.369, and 35% of input pairs are
both alive at the output. Collapse: among chains whose four inputs all survive, the input cloud's angular PR is 5.2, 2.3, 1.5, 1.3 at
l = 1, 4, 8, 16, about 1.1-1.4 for l = 16-128 and 2.0 at l = 255, so after about 8 layers the input is about one direction
plus the radius (the relevance lane's N = 1 there).

4.4 Small noise (descriptive runs, added after registration; `runs/B_inputVP_*`). Closed relevance of the layer-l state
(input and noise up to l shared, noise after l independent), raw output / output direction:

| net | sigma | l = 0 | L/8 | L/4 | L/2 | 3L/4 | L - 2 |
|---|---|---|---|---|---|---|---|
| 256 x 32 | 1e-3 | 0.9994 / 0.998 | 0.9995 / 0.998 | 0.9996 / 0.999 | 0.9997 / 0.999 | 0.9999 / 0.999 | 1.000 / 1.000 |
| 256 x 32 | 1e-2 | 0.952 / 0.852 | 0.956 / 0.865 | 0.962 / 0.878 | 0.974 / 0.910 | 0.987 / 0.952 | 0.998 / 0.993 |
| 256 x 32 | 0.1 | 0.20 / 0.02 | 0.22 / 0.04 | 0.26 / 0.05 | 0.36 / 0.13 | 0.59 / 0.38 | 0.93 / 0.88 |
| 64 x 64 | 1e-3 | 0.9994 / 0.76 | 0.9995 / 0.76 | 0.9995 / 0.76 | 0.9997 / 0.81 | 0.9999 / 0.84 | 1.000 / 0.98 |
| 64 x 64 | 1e-2 | 0.965 / 0.08 | 0.971 / 0.09 | 0.975 / 0.11 | 0.983 / 0.12 | 0.990 / 0.20 | 0.999 / 0.86 |

At ARC's 256 x 32 with sigma = 1e-3 the layer-l state decides 99.94-100% of the variance at every layer: the input
regime holds. At 64 x 64 the output direction is already noise-dominated at sigma = 1e-2 (the input's directional
variance has decayed to ~n/L^2 of the amplitude's), while the raw output stays 96-100% input-decided. At 8 x 256 any
sigma >= 1e-3 hands the output to the noise within about 40 layers (T_mem = 40 at sigma = 1e-3): the cloud's PR rises to
about 6 of 8 and extinction disappears (99% of pairs alive); the closed-relevance estimates there are noise-dominated
(the input's variance at the output is tiny) and are not reported.
