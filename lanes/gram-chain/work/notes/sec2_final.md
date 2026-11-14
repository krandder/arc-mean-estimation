## 2. The stationary law of the normalised Gram (Part A)

2.1 Structure (HEURISTIC, leading order in n^{-1/3}; [C+A] unless marked; FORMAL 2, 7). Two replicas with independent
noise have three coordinates on three time scales.
- The radius. Each replica's marginal is the exact one-input law (Q = (chi2_n/n) r, r a Kesten perpetuity). On the scale
  s = t/n it is the diffusion dq = ds + sqrt5 q dW with stationary density (2/5) q^{-2} e^{-2/(5q)} and spectral gap 5/8:
  in u = log q the generator is a Morse problem with a single bound state, so the gap is the bottom of a continuous
  spectrum (PROVEN for the limit diffusion).
- The angle. Fast: it relaxes at rate theta*/pi per layer (tau = pi/theta* ~ 1.49 Q^{1/3} layers) to the fixed point of
  the mean-field closure rho' = Q kappa(rho)/(Q + 1), delta*(Q) = eps(1 - 0.7 eps + O(eps^2)), eps = A Q^{-2/3} (two-term
  form within 0.3% at Q >= 148) [C]. One exact step has n Var(delta')/delta^2 = 6.0, 6.8, 7.3 at n = 64, 256, 1024, tending
  to 8 [C measured; A limit], so delta fluctuates by order n^{-1/3} relative.
- The radius ratio y = n^{1/3}(log|h1| - log|h2|). Slow: pulled back at rate 1/(Q + 1) per layer, driven at 4 delta/n per
  layer (one exact step: 4.05-4.09 delta/n). With q it forms the limit diffusion dy = -(y/q) ds + 2 sqrt(A) q^{-1/3} dW',
  whose E[y^2 | q] has the closed form m(q) = (24A/25) beta^{-2/3} e^{beta/q} Gamma(2/3, beta/q), beta = 2/5 [A];
  E y^2 = 3.561, so SD(log|h1| - log|h2|) -> 1.887 n^{-1/3} [C+A].

2.2 The exact chain (NUMERICAL; PREREG Part A; P = 8000 chains at n <= 64 down to 500 at n = 1024, 8n burn-in from the
exact radius law, 64 samples per chain; bootstrap SE over chains in parentheses; `results/partA_scores.json`,
`figs/fig1_stationary_law.png`).

{{TABLE_A}}

- Scaling: the law of (delta/delta*(Q) - 1) n^{1/3} collapses across n (fig 1, left), and SD(delta/delta*(Q)) n^{1/3}
  rises slowly from 1.65 to 1.83 between n = 64 and 1024 (PA4 hit), short of the 2.2 that kappa_x = 8 would give: the
  finite-n one-step variance is still below its limit.
- The radius ratio reaches its limit: SD(ell) n^{1/3} = 1.875 (0.025) at n = 1024 against 1.887 (PA1 hit), and
  E[ell^2 | q] n^{2/3} matches m(q) within 1-8% in every radius bin at n = 1024 (PA2 hit; fig 1, right).
- The angle's level: the median of delta/delta*(Q) approaches 1 from below (0.962 at n = 64, 0.989 at n = 1024) and the
  mean is 1.000 at n = 1024. PA3 missed: the median is below 0.97 at n = 64 and 128, and n^{2/3}(mean - 1) is not constant
  (0.20, 0.13, 0.05, 0.08, 0.00 at n = 64-1024). Given the radius there is a tilt: at n = 1024, E[delta/delta*(Q) | q] =
  1.030 for q < 0.3 and 0.920 for q > 10, shrinking roughly like n^{-1/2} (1.063 and 0.835 at n = 256). The correlated
  angle-radius increments (a_{Q delta} ~ -4 Q delta/n [A]) push the angle below its fixed point when the radius is high.
  gpt-6-astra's second-order coefficient for the geometric-mean radius (+0.077 n^{-2/3} relative at the median) is far
  smaller than this tilt, so the tilt is a finite-n effect beyond that order (not derived).
- Mixing (200 contiguous traces of 4n layers per n): autocorrelations fall to 1/e after 6, 8, 10, 13, 17 layers for the
  angle (1.2-1.4 x the mean-field 1.49 Q^{1/3}), 39-663 layers for the radius ratio (1.0-1.4 x (Q + 1)), and 51-797
  layers for log q, about 0.8n. PA6 missed on its log-radius clause (0.78n at n = 1024 against the band's 0.8n): the
  spectral gap's 1.6n is the slowest rate of a continuous spectrum, not the 1/e time.

2.3 Noise sharing (A-share). The mean field depends only on E S_12 = t, so Gaussian correlation t (Hermite degrees),
per-coordinate sharing (ANOVA over scalar coordinates) and per-layer sharing (ANOVA over layer blocks) share the curve
C(t) = 1 - E delta_t / E delta_0 -> 1 - (1 - t)^{2/3} [A, input-bits round 1].

{{TABLE_SHARE}}

{{READ_SHARE}}

2.4 Three and four replicas: how many directions the stationary cloud spans.
- Four-point law (HEURISTIC [A], re-derived [C], FORMAL 7.5). For four independent replicas the double difference
  D = (u1 - u2).(u3 - u4) relaxes at the angle's own rate theta*/pi and is driven by 8 delta^2/n per layer (nearly
  aligned replicas share their gates, and z1 - z2, z3 - z4 are independent). Hence, per net, PR_C = (2 delta*)^2 / Var D =
  n theta*/pi = 0.672 n Q^{-1/3}, of order n^{2/3}; with the chain's variance weighting,
  PR_w = E_W (tr C)^2 / E_W tr C^2 = 1.0865 n^{2/3}. The numerics lane's 1/k spectrum would give (log n)^2 with no radius
  dependence.

{{TABLE_A4}}

- Binned by radius (post hoc, `results/pr_by_radius.json`, fig 3 right), the chain's PR follows n theta*(Q)/pi across the
  whole radius range at each n: at n = 256 it falls from 56.8 to 16.1 between q = 0.2 and q = 10 against 44.1 to 12.5
  predicted; measured/predicted is flat in q (1.14-1.29) and falls with n (about 1.9, 1.6, 1.4, 1.27, 1.18 at
  n = 16 ... 256). A radius-independent 1/k shape cannot produce this. {{PA9_TEXT}} PA8 (1/k moments) missed already at
  n = 64 (the radius-normalised PR is 27% below the 1/k value). {{R3_TEXT}}
- Three replicas: {{TRI_TEXT}}
- One time scale (HEURISTIC, FORMAL 7.10 [C]): T* = (Q + 1) delta* = 1.5 tau and PR_C = n/tau at leading order, so
  PR_C x T* = 3n/2 at every radius: a large-radius net has a smaller, longer-lived cloud and a small-radius net a larger,
  shorter-lived one. The same structure (dimension = width x angular contraction rate theta/pi, halved for a transient)
  gives the input regime's 1.5 n/l (section 4).
