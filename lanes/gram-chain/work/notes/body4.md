## 5. Annealed versus quenched (Part C: real nets)

168 fresh nets (seeds 5000+: 32 at each of n = 8, 16, 32, 64, 24 at n = 128, 16 at n = 256), each with 256 independent noise replicas run from
h = 0 for 8n layers; per net the median radius Qbar, the direction cloud's trace and participation ratio, the output
direction's and log-amplitude's variances, and the closed and total relevance at t = 1-64 (`scratch/partC.py`,
`results/partC_scores.json`, `figs/fig5_per_net.png`). Chain comparators are Part A and B outputs at the same n.

| n | nets | median Qbar/n | CV of cloud size: nets / chain | CV after dividing by delta*(Qbar) | mean cloud size: nets (SE) / chain | median per-net PR / chain PR_w | slope of log PR on log Qbar (Spearman) | median radial share: nets / rho(q) |
|---|---|---|---|---|---|---|---|---|
| 8 | 32 | 0.50 | 0.32 / - | 0.09 | 0.567 (0.032) / - | 6.7 / - | -0.13 (-0.52) | - |
| 16 | 32 | 0.65 | 0.39 / 0.42 | 0.15 | 0.408 (0.028) / 0.403 | 9.0 / 10.0 | -0.13 (-0.61) | - |
| 32 | 32 | 0.73 | 0.45 / 0.49 | 0.17 | 0.276 (0.022) / 0.288 | 13.4 / 14.8 | -0.30 (-0.73) | - |
| 64 | 32 | 0.73 | 0.57 / 0.56 | 0.20 | 0.177 (0.018) / 0.196 | 17.8 / 21.7 | -0.22 (-0.79) | 0.37 / 0.40 |
| 128 | 24 | 0.86 | 0.47 / 0.59 | 0.16 | 0.112 (0.011) / 0.132 | 21.5 / 32.1 | -0.32 (-0.79) | 0.43 / 0.43 |
| 256 | 16 | 0.99 | 0.75 / 0.62 | 0.14 | 0.065 (0.012) / 0.087 | 34.5 / 49.0 | -0.26 (-0.87) | 0.41 / 0.46 |

- The scale does not self-average (PC1, PC2 hit). The per-net cloud size tr Var(u | W) has an across-net CV of 0.39-0.75,
  matching the chain's 4-replica prediction 0.42-0.62 within 30%, and the chain's prediction rises with n toward the
  inverse-gamma limit 0.68 (FORMAL 5.1). The annealed mean is within 2.5 SE of the nets' mean at every n.
- The radius explains the scatter (PC3 hit; hypothesis H-rad). Dividing each net's cloud size by delta*(Qbar(W)), the
  noisy-kernel fixed point at that net's radius, cuts the CV to 0.14-0.20 at n = 64-256 (the squared CV falls by 87%,
  89%, 97%); used directly as a predictor, delta*(Qbar(W)) has R^2 = 0.88, 0.92, 0.93 for the per-net cloud size at
  n = 64, 128, 256 (0.92-0.95 with one fitted scale factor 1.06-1.11). The normalised cloud size is 1.01-1.16 (median) at
  every n: per net, the cloud is the fixed point at the net's own radius (fig 5, left: 168 nets collapse on
  A q^{-2/3} n^{-2/3}).
- The shape self-averages, but the annealed dimension is biased (PC4 missed). Per-net PRs scatter by 0.15-0.35 (CV,
  including sampling noise from 256 replicas) and fall with the net's radius (slope -0.22 to -0.32 at n >= 32, predicted
  -1/3); the median net's PR is 0.89, 0.91, 0.82, 0.67, 0.71 times the chain's variance-weighted PR_w at n = 16-256, which
  fails the registered 25% band at n = 128 and 256. The bias is the radius again: PR_w weights nets by (tr C)^2 ~ Q^{-4/3},
  i.e. small-radius nets, whose clouds are bigger and span more directions; with PR_C ~ Q^{-1/3} the limit ratio is 1.35.
  This is the clearest case of an annealed count misleading about the typical net.
- Relevance per net follows the net's radius (PC5, PC6 hit). The Spearman correlation of V_P(t = 8; W) with Qbar(W) is
  0.67, 0.70, 0.94 at n = 64, 128, 256, and the per-net closed relevance is within 0.02-0.08 (median) of the mean field
  evaluated at the net's own radius at t = 2-16. The annealed curve (a ratio of means dominated by small-radius,
  fast-forgetting nets) sits below the median net's: 0.469 against 0.526 and 0.166 against 0.207 at t = 4, 8 (n = 64);
  0.666 against 0.743 and 0.377 against 0.484 (n = 256).
- The radial share per net follows rho(q) (PC7 hit): median deviation 12%, 11%, 5% at n = 64, 128, 256, Spearman with the
  radius 0.89-0.99 (fig 5, right).
- So per net, the chain's annealed theory plus the net's radius predicts the cloud's size, its relevance horizon, its
  radial share and (with a 1.35x weighting correction) its dimension. What it does not predict is any net-specific
  direction (section 7).

## 6. What the chain explains of what we measured, and what it does not (Part D)

| measured (lane) | chain / theory | status |
|---|---|---|
| cloud size: two noise replicas at angle 2.23 X^{-2/3}, nets measured/law 0.87 (0.72-1.24) (stationary lane, A3) | exact chain: median delta/delta*(Q) 0.96-0.99 at n = 64-1024; per net, cloud size / delta*(Qbar) = 1.01-1.16 (median), R^2 0.88-0.93 | explained: the noisy-kernel fixed point at each net's own radius; nets scatter because their radii do |
| cloud 5-8x above the Lyapunov formula, with an assumed 1/k shape (stationary and numerics lanes) | trace explained by delta*(Q); dimension n theta*/pi ~ n^{2/3} (four-point law), radius dependent in chain and nets | size explained; the 1/k shape is refuted as a global law; the top-k eigenvalue ratios (k = 2-8) were not computed |
| births: 0.48-0.64 sqrt(n) noise-decided gate flips per layer (stationary lane) | exact chain 0.62-0.63 sqrt(n); mean field n arccos(Q/(Q+1))/pi = 0.59 sqrt(n) (numerics lane) | explained in law; per-net spread follows the radius (births ~ (n/Q)^{1/2}) |
| interaction order: direction 1.72 -> 3.97, h_0 1.41 -> 3.87 at n = 8 -> 256 (numerics lane) | mechanism: a lone injection decays algebraically while the cloud relaxes on tau, D_u -> 2.99 Q^{1/6} (numerics lane); exact chain's finite-eps block order 1.90, 2.60, 3.34 at n = 16, 64, 256 (slope 0.20; a lower bound) | explained in mechanism and growth rate; level within about 25% |
| flat low-order shares: C(t) = 0.16-0.18, 0.36-0.38, 0.60-0.64 at t = 0.25, 0.5, 0.75 and S1 0.59-0.66 for n = 8-128 (input-bits) | closure 1 - (1 - t)^{2/3} [A]: 0.175, 0.370, 0.603, first coefficient 2/3; exact chain 0.164-0.192, 0.361-0.406, 0.601-0.654 at n = 16-256 for three kinds of sharing | explained: one fixed point at every width; the growing mean order sits in a tail that C(t <= 0.75) cannot see |
| antithetic noise: even share 0.23-0.27, gain 1.9-2.2 (stationary, input-bits) | E delta(-1)/E delta(0) = 1.58-1.61 (2^{2/3} = 1.587); even share of the direction 0.198-0.209 | explained to within 0.03-0.07 in the even share |
| input regime 256 x 32: amplitude/direction 0.49/0.47 (per-net medians) vs 0.60/0.36 (annealed chain) (input-bits) | the gap is annealed vs quenched (ratio of means weights large-gain nets); in log form the radius share matches the kernel within 4% (4.2) | explained as an averaging effect; the per-net median split is not a replica quantity |
| 3n/l decay of differing gates (input-bits: 128, 100, 74, 51, 33, 18, 11, 5 at layers 1-128, n = 256) | exact chain E[n arccos(rho)/pi] = 128, 101.6, 85.8, 66.7, 47.1, 30.1, 17.5, 9.3, 4.6 for the gates of layers 1, 2, 3, 5, 9, 17, 33, 65, 129; kernel 128, 101.6, 85.9, 67.0, 47.6, 30.8, 18.4, 10.3, 5.5 (`results/partD_gates.json`) | explained (kernel; the chain adds the finite-width deficit seen in the nets at depth) |
| the input's direction lives in about 10 effective directions at 256 x 32 (input-bits) | vertex law PR(l) ~ 1.5 n/l: 12.1 at l = 32 (exact chain), 10.3 (recursion) | explained (new) |

What it does not explain: which directions carry the relevance in a given net (section 7); per-net deviations beyond
what the radius fixes (the 0.14-0.20 residual CV of the cloud size, the 0.15-0.35 scatter of per-net PR); the top-k shape
of the stationary cloud's spectrum (only its participation ratio is pinned down); and anything about estimators, which is
the relevance and estimator lanes' work.
