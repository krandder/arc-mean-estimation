## 1. The tool

The replica Gram chain (explainer section 2; numerics lane P-G1) is exact at every width: given the past, the rows of
W_l see the replicas only through their Gram matrix, so G_l = (1/n) sum_i v_i v_i^T with v_i = relu(z_i) + xi_i,
z_i ~ N(0, 2 G_{l-1}). This lane extended it (FORMAL 1.2, `lib/gc2.py`) to correlated noise, per-coordinate and per-layer
Bernoulli noise sharing, tangent vectors, Gram surgery (perturbations, radius rescaling, direction swaps), inputs at
sigma = 0 and the noiseless output layer, all exact by the same argument and tested against explicit networks (19 KS and
mean checks pass, `logs/test_gc2.log`). Three facts frame what follows.
- Response invariance (PROVEN, FORMAL 1.3; the relevance lane's Theorem 1 is the sharper form): given the past, the
  future's response to a perturbation of layer l depends on it only through its Gram relations with the replicas, so
  annealed theory can count and weigh relevant directions but cannot name them.
- Annealed tangent conservation (PROVEN, FORMAL 1.4): E_W |J v|^2 = |v|^2 at every depth while the typical value decays,
  so annealed linear-response means are carried by rare nets and are not used as relevance measures.
- Integrability (FORMAL 1.5; NUMERICAL check): E Q = infinity and the radius ratio between replicas does not shrink at
  large Q, so the annealed second moments of raw-state differences are infinite (n = 64: the top 1% of chains by radius
  carry 82% of the sample mean of |h1 - h2|^2, 94% of it radial). The annealed quantities here use the direction
  u = h/|h| or a/|a| and log radii. Both need a convention on the all-off event (a = 0, probability 2^-n per layer for a
  noiseless output layer): the code floors |a|^2 at 1e-300 (Part B) or |a| at 1e-300 (Part C), so log|a| moments are
  regularised estimands; likewise Part B's direction distance 2(1 - cos) is not meaningful when an output is zero, while
  Part C sets u(0) = 0. At n >= 64 the event never occurred in these runs; at n = 16 it did and the log channel is not
  used. This is also why the numerics lane's annealed D_h was "too noisy".

## 2. The stationary law of the normalised Gram (Part A)

2.1 Structure (HEURISTIC, leading order in n^{-1/3}; [C+A] unless marked; FORMAL 2 and 7). Two replicas with independent
noise have three coordinates on three time scales.
- The radius. Each replica's marginal is the exact one-input law. On the scale s = t/n it is the diffusion
  dq = ds + sqrt5 q dW with stationary density (2/5) q^{-2} e^{-2/(5q)}; in u = log q its generator is a Morse problem with
  a single bound state, so the spectral gap is 5/8, the bottom of a continuous spectrum (PROVEN for the limit diffusion).
- The angle. Fast: it relaxes at rate theta*/pi per layer (tau ~ 1.49 Q^{1/3} layers) to the fixed point of the
  mean-field closure rho' = Q kappa(rho)/(Q + 1), delta*(Q) = eps(1 - 0.7 eps + O(eps^2)), eps = A Q^{-2/3} (two-term form
  within 0.3% at Q >= 148) [C]. One exact step has n Var(delta')/delta^2 = 6.0, 6.8, 7.3 at n = 64, 256, 1024, tending to
  8 [C measured; A limit], so delta fluctuates by order n^{-1/3} relative.
- The radius ratio y = n^{1/3}(log|h1| - log|h2|). Slow: pulled back at rate 1/(Q + 1) per layer and driven at 4 delta/n
  per layer (one exact step: 4.05-4.09 delta/n). With q it forms the limit diffusion dy = -(y/q) ds + 2 sqrt(A) q^{-1/3} dW',
  and E[y^2 | q] has the closed form m(q) = (24A/25) beta^{-2/3} e^{beta/q} Gamma(2/3, beta/q), beta = 2/5 [A]; E y^2 = 3.561,
  so SD(log|h1| - log|h2|) -> 1.887 n^{-1/3} [C+A].

2.2 The exact chain (NUMERICAL; PREREG Part A; P = 8000 chains at n <= 64 down to 500 at n = 1024, 8n burn-in from the
exact radius law, 64 samples per chain over 8n layers; bootstrap SE over chains in parentheses;
`results/partA_scores.json`, `figs/fig1_stationary_law.png`).

| n | median delta/delta*(Q) | mean | SD(delta/delta*) n^{1/3} | SD(ell) n^{1/3} (limit 1.887) | 1/e lag: angle / ratio / log q (layers) |
|---|---|---|---|---|---|
| 8 | 0.980 (0.002) | 1.0841 (0.0019) | 1.37 | 1.421 (0.005) | 2 / 5 / 5 |
| 16 | 0.966 (0.002) | 1.0507 (0.0015) | 1.47 | 1.542 (0.005) | 3 / 10 / 10 |
| 32 | 0.956 (0.001) | 1.0246 (0.0011) | 1.56 | 1.635 (0.005) | 4 / 22 / 41 |
| 64 | 0.962 (0.001) | 1.0125 (0.0010) | 1.65 | 1.720 (0.005) | 6 / 39 / 51 |
| 128 | 0.969 (0.001) | 1.0051 (0.0009) | 1.73 | 1.798 (0.008) | 8 / 94 / 158 |
| 256 | 0.974 (0.001) | 1.0011 (0.0010) | 1.78 | 1.819 (0.010) | 10 / 204 / 229 |
| 512 | 0.984 (0.001) | 1.0012 (0.0010) | 1.79 | 1.843 (0.016) | 13 / 325 / 410 |
| 1024 | 0.989 (0.001) | 1.0000 (0.0010) | 1.83 | 1.875 (0.025) | 17 / 663 / 797 |

- Scaling: the law of (delta/delta*(Q) - 1) n^{1/3} collapses across n (fig 1, left); SD(delta/delta*) n^{1/3} rises
  slowly, 1.65 to 1.83 between n = 64 and 1024 (PA4 hit), short of the 2.2 that the one-step limit 8 would give.
- The radius ratio reaches its limit: SD(ell) n^{1/3} = 1.875 (0.025) at n = 1024 against 1.887 (PA1 hit), and
  E[ell^2 | q] n^{2/3} = 2.66, 3.24, 3.79, 4.16, 4.11, 4.66, 4.91 in the radius bins [0, .3), ..., [10, inf) at n = 1024
  against the closed form's 2.74, 3.30, 3.73, 4.14, 4.49, 4.75, 5.13 (PA2 hit; fig 1, right).
- The angle's level: the median of delta/delta*(Q) approaches 1 from below and the mean is 1.000 at n = 1024. PA3 missed:
  the median is below 0.97 at n = 64 and 128, and n^{2/3}(mean - 1) is not constant (0.20, 0.13, 0.05, 0.08, 0.00 at
  n = 64-1024). Given the radius there is a tilt: E[delta/delta*(Q) | q] is 1.030 for q < 0.3 and 0.920 for q > 10 at
  n = 1024 (1.063 and 0.835 at n = 256), shrinking roughly like n^{-1/2}. Correlated angle-radius increments
  (a_{Q delta} ~ -4 Q delta/n [A]) push the angle below its fixed point when the radius is high; gpt-6-astra's
  second-order coefficient for this conditioning (+0.077 n^{-2/3} relative at the median) is far smaller, so the tilt is a
  finite-n effect beyond that order (not derived).
- Mixing: autocorrelations of 200 contiguous traces (4n layers) fall to 1/e in 1.2-1.4 x the mean-field 1.49 Q^{1/3}
  layers (angle), 1.0-1.4 x (Q + 1) layers (radius ratio) and about 0.8n layers (log radius). PA6 missed on its
  log-radius clause by under 3% (0.78n at n = 1024 against the band's 0.8n): the gap's 1.6n is the slowest rate of a
  continuous spectrum, not the 1/e time.

2.3 Noise sharing (A-share; NUMERICAL). The mean field depends only on E S_12 = t, so Gaussian correlation t (Hermite
degrees), per-coordinate sharing (ANOVA over scalar coordinates) and per-layer sharing (ANOVA over layer blocks) share
C(t) = 1 - E delta_t / E delta_0 -> 1 - (1 - t)^{2/3} = 0.175, 0.370, 0.603 at t = 0.25, 0.5, 0.75 [A, input-bits round 1].
Values below use the registered baseline (E delta_0 from the A-r2 run at the same n). Deviations from the registration:
the sharing runs used a 2n burn-in and 4n recorded layers (registered: 6n and 8n), n = 1024 omits t = 0.9 and 0.99, and
the first scorer used each sharing run's own independent-noise baseline (at n = 256 that gave coordinate C(0.25) = 0.164
and an antithetic ratio 1.605 instead of 0.173 and 1.587; every PA5 clause passes either way).

| n | correlation | per coordinate | per layer | finite-eps mean order G(0.01)/0.01: corr / coord / layer | antithetic E delta(-1)/E delta(0) (2^{2/3} = 1.587) |
|---|---|---|---|---|---|
| 16 | 0.182, 0.386, 0.630 | 0.186, 0.389, 0.632 | 0.193, 0.406, 0.654 | 2.79 / 2.54 / 1.90 | 1.603 |
| 64 | 0.179, 0.383, 0.616 | 0.183, 0.383, 0.617 | 0.187, 0.389, 0.629 | 3.45 / 3.44 / 2.60 | 1.583 |
| 256 | 0.186, 0.368, 0.606 | 0.173, 0.374, 0.610 | 0.177, 0.380, 0.613 | 4.06 / 4.06 / 3.34 | 1.587 |
{{SHARE1024_ROW}}

The three kinds of sharing agree within 0.03 at t <= 0.75 and match the closure within 0.03 at n >= 64 (within 0.015 for
correlation and per-coordinate sharing at n = 64-256; at n = 1024 they sit 0.01-0.025 below it); the
input-bits lane measured 0.16-0.18, 0.36-0.38, 0.60-0.64 for the output under per-coordinate sharing on nets at n = 8-128.
They separate only at small refresh rates (t >= 0.9), where single-layer injections stop overlapping: the per-layer
(block) mean order is the smallest and grows like n^{0.21} (1.90 to 3.34 from n = 16 to 256), the slope of the numerics
lane's nets (0.17-0.26). Antithetic noise multiplies the stationary angle by 2^{2/3} to within 0.0-1.0% (1.583-1.603;
the even share of the direction is then 0.198-0.209, gain 2.4-2.5; nets 0.23-0.27). {{PA5_TEXT}}

2.4 Three and four replicas: how many directions the stationary cloud spans.
- Four-point law (HEURISTIC [A], re-derived [C], FORMAL 7.5). For four independent replicas the double difference
  D = (u1 - u2).(u3 - u4) relaxes at the angle's own rate theta*/pi and is driven by 8 delta^2/n per layer (nearly aligned
  replicas share their gates; z1 - z2 and z3 - z4 are independent). Hence, per net, PR_C = (2 delta*)^2 / Var D =
  n theta*/pi = 0.672 n Q^{-1/3}, of order n^{2/3}; with the chain's variance weighting
  PR_w = E_W (tr C)^2 / E_W tr C^2 = 1.0865 n^{2/3}. A 1/k spectrum would give (log n)^2 with no radius dependence.

| n | PR_w (exact chain, 4 replicas) | 1/k spectrum | 1.0865 n^{2/3} | across-net CV of tr C (chain) |
|---|---|---|---|---|
| 16 | 10.04 (0.03) | 9.7 | 6.9 | 0.425 |
| 32 | 14.77 (0.04) | 15.2 | 11.0 | 0.491 |
| 64 | 21.73 (0.07) | 22.3 | 17.4 | 0.555 |
| 128 | 32.12 (0.14) | 30.8 | 27.6 | 0.594 |
| 256 | 48.96 (0.30) | 41.0 | 43.8 | 0.619 |
{{PR_ROWS_512_1024}}

- Binned by radius (post hoc, `results/pr_by_radius.json`, fig 3 right), the chain's PR follows n theta*(Q)/pi across the
  whole radius range at each n: at n = 256 it falls from 56.8 to 16.1 between q = 0.2 and q = 10 against 44.1 to 12.5
  predicted, measured/predicted is flat in q (1.14-1.29) and falls with n (median over bins about 1.9, 1.6, 1.4, 1.27,
  1.18, 1.13, 1.08 at n = 16 ... 1024; at n = 1024 every bin is within 4-16%). On real nets the per-net PR falls with the radius too (section 5). A radius-independent 1/k shape
  cannot do this. {{PA9_TEXT}} PA8 (1/k moments) missed: the radius-normalised PR is already 27% below the 1/k value at
  n = 64. {{R3_TEXT}}
- Three replicas: {{TRI_TEXT}}
- One time scale (HEURISTIC, FORMAL 7.10 [C]): T* = (Q + 1) delta* = 1.5 tau and PR_C = n/tau at leading order, so
  PR_C x T* = 3n/2 at every radius to leading order (with the finite-Q definitions 1.28n, 1.40n, 1.46n at the median radius
  for n = 64, 256, 1024): a large-radius net has a smaller, longer-lived cloud and a small-radius net a larger,
  shorter-lived one.
