## 2. The stationary law of the normalised Gram (Part A)

2.1 Structure (HEURISTIC, leading order in n^{-1/3}; [C+A] unless marked). Two replicas with independent noise have three
coordinates on three time scales.
- The radius: each replica's marginal is the exact one-input law (Q = (chi2_n/n) r, r a Kesten perpetuity); on the scale
  s = t/n it is the diffusion dq = ds + sqrt5 q dW, stationary density (2/5) q^-2 e^{-2/(5q)}, spectral gap 5/8 (the
  bottom of a continuous spectrum: a Morse potential with a single bound state) [C+A, PROVEN for the limiting diffusion].
- The angle: fast. It relaxes at rate theta*/pi per layer (tau = pi/theta* ~ 1.49 Q^{1/3} layers) to the mean-field fixed
  point delta*(Q) = eps(1 - 0.7 eps + O(eps^2)), eps = 2.231 Q^{-2/3} (the fixed point of rho' = Q kappa(rho)/(Q + 1); the
  two-term form is within 0.3% for Q >= 148) [C]. Its relative fluctuations are of order n^{-1/3}: one exact step has
  n Var(delta')/delta^2 = 6.0, 6.8, 7.3 at n = 64, 256, 1024, tending to 8 (`results/onestep.json`) [C; A gave the
  limit].
- The radius ratio y = n^{1/3}(log|h1| - log|h2|): slow, restored at rate 1/(Q + 1) per layer and injected at 4 delta/n per
  layer (one exact step: 4.05-4.09 delta/n). Jointly with q it is the diffusion dy = -(y/q) ds + 2 sqrt(A) q^{-1/3} dW'
  (A = 2.2309), whose stationary E[y^2 | q] has the closed form m(q) = (24A/25) beta^{-2/3} e^{beta/q} Gamma(2/3, beta/q)
  (beta = 2/5) [A], E y^2 = 3.561, so SD(log|h1| - log|h2|) -> 1.887 n^{-1/3} [C+A].

2.2 The exact chain against this (NUMERICAL; PREREG Part A; bootstrap SE over chains in parentheses; `results/partA_scores.json`).
{{TABLE_A}}

- The angle collapses in the n^{1/3} scaling (`figs/fig1_stationary_law.png`, left): the law of (delta/delta*(Q) - 1)
  n^{1/3} converges, with SD(delta/delta*(Q)) n^{1/3} = {{SDR}}.
- The radius ratio approaches the diffusion limit from below: SD(ell) n^{1/3} = {{SDL}} against 1.887; E[ell^2 | q] n^{2/3}
  approaches m(q) bin by bin (fig1, right).
- The angle's level: the median of delta/delta*(Q) is {{MED}} and the mean {{MEAN}}. Given the radius there is a
  systematic tilt: at n = 256, E[delta/delta*(Q) | q] = 1.06 for q < 0.3 and 0.83 for q > 10, shrinking roughly like n^{-2/3}
  in the central bins (the correlated angle-radius increments, a_{Q delta} ~ -4 Q delta/n [A], push the angle below its
  fixed point when the radius is high). gpt-6-astra's second-order coefficient for conditioning on the geometric-mean
  radius, +0.077 n^{-2/3} relative at the median, is far below the n = 256 tilt; the tilt is a finite-n effect not
  captured at that order.
- Mixing (autocorrelation of 200 contiguous traces of 4n layers): the angle decorrelates (to 1/e) in {{LAGR}} layers,
  1.2-1.3 times the mean-field 1.49 Q^{1/3}; the radius ratio in {{LAGL}} layers, 1.0-1.4 times Q + 1; log q in {{LAGQ}}
  layers, about 0.5-0.8 n (the spectral gap's 1.6 n is the slowest rate of a continuous spectrum, not an e-folding time;
  the 4n traces also bias long lags down).

2.3 Noise sharing (A-share; mean field depends only on E S_12 = t). {{SHARE}}

2.4 Three and four replicas: how many directions the stationary cloud spans.
- Four-point law (HEURISTIC [A], re-derived [C]): for four independent replicas the double difference
  D = (u1 - u2).(u3 - u4) relaxes at the angle's own rate theta*/pi and is driven by 8 delta^2/n per layer (nearly aligned
  replicas share their gates), so per net PR_C = (2 delta*)^2 / Var D = n theta*/pi = 0.672 n Q^{-1/3}; averaged with the
  chain's variance weighting, PR_w = E_W(tr C)^2 / E_W tr C^2 = 1.0865 n^{2/3}. The numerics lane's 1/k spectrum would give
  (log n)^2 and no radius dependence.
- Exact chain: PR_w = {{PRW}} at n = {{PRN}} (local log-log slopes {{SLOPES}}; 1/k predicts slopes falling to 0.34 by
  n = 256-1024, the four-point law 2/3). Binned by radius, the measured PR follows n theta*(Q)/pi across the whole radius
  range at fixed n: at n = 256 it falls from 56.8 to 16.1 between q = 0.2 and q = 10, against 44.1 to 12.5 predicted; the
  ratio measured/predicted is flat in q (1.14-1.29) and falls with n (about 1.9, 1.6, 1.4, 1.27, 1.18 at n = 16 ... 256)
  (`results/pr_by_radius.json`, fig3 right; post hoc). The radius dependence alone refutes a radius-independent 1/k
  spectrum. {{PA9}}
- Three replicas: {{TRI}}
- One time scale (HEURISTIC, FORMAL 7.10 [C]): T* = (Q + 1) delta* = 1.5 tau and PR_C = n/tau, so PR_C x T* = 3n/2 at every
  radius: a large-radius net has a smaller, longer-lived cloud, a small-radius net a larger, shorter-lived one.
