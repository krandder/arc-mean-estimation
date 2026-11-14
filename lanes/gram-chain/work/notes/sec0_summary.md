**Short answer.** The chain works as a theory tool, and with it the bits that matter at a layer have a quantitative
(weight-averaged) theory that the exact chain confirms to within a few percent, and real nets to within their radius
scatter. At layer L - t of a stationary net, the state's direction decides a fraction 1 - Y((t - 1)/T*) of the output
direction's variance (T* = 2.23 Q^{1/3}, about 2 n^{1/3} layers), spread over about n/(tau + 2t) directions (tau = T*/1.5;
order n^{2/3} directions near the output); the radius carries a further share rho(q) of a net's output variance for order
n layers. In the input regime the input's directional information at layer l lives in about 1.5 n/l directions (a 1/n
four-point effect, invisible to the kernel), and the radius carries the kernel share (1/2 + C_l)/(1/2 + C_L) of the
log-amplitude. The "Lyapunov covariance times future amplification, direction by direction" picture is replaced by a free
product: the cloud's axes and the future's amplified directions sit in random relative position, so dimensions combine
harmonically. What the chain provably cannot give is which directions: about k(n - k) log2(1/eps) bits per layer of
net-specific orientation that no weight-averaged or forward-only theory can supply. Per net, the scale of everything is set
by the net's radius, which does not self-average (CV 0.68); {{PC_SHORT}}

1. **The tool** (PROVEN; tested). The replica Gram chain integrates the weights out exactly at any width, for any noise
   sharing, tangents, perturbations and inputs (`lib/gc2.py`, 19 checks against explicit nets). It computes weight
   averages of any noise expectation of a replica Gram path: total and closed relevance, Sobol and noise-stability curves,
   participation ratios, and the across-net scatter of all of these. Raw-state annealed moments are infinite in the
   stationary regime (heavy radius tail), so everything uses directions and log radii. Explainer:
   `outbox/gram-chain-explainer-2026-11-01.md`.
2. **The stationary law of 2-4 replicas** (HEURISTIC limit [C+A]; NUMERICAL). The angle is slaved to the noisy-kernel
   fixed point delta*(Q) = 2.231 Q^{-2/3}(1 - 1.56 Q^{-2/3} + ...) with n^{-1/3} relative fluctuations (the rescaled law
   collapses, n = 8-1024); the radius ratio is a slow diffusion jointly with the radius, SD -> 1.887 n^{-1/3} with a closed
   form for E[ell^2 | q] [A] (chain {{SDL_SHORT}}); the radius mixes at rate 5/(8n) per layer (spectral gap, PROVEN for the
   limit diffusion). {{SHARE_SHORT}}
3. **How many directions the stationary cloud spans** (HEURISTIC four-point balance, [A] first, re-derived [C];
   NUMERICAL). PR_C = n theta*/pi = 0.67 n Q^{-1/3}, order n^{2/3}: the exact chain follows its radius dependence (a 3.5x
   fall from q = 0.2 to 10 at n = 256, as predicted, measured/predicted 1.14-1.29 and falling with n). This refutes the
   numerics lane's 1/k spectrum ((log n)^2, radius independent). {{PA9_SHORT}} With the relevance horizon: PR_C x T* = 3n/2
   at every radius.
4. **How much and how long it matters, stationary** (HEURISTIC [C+A]; NUMERICAL, PB1-PB2). Closed relevance of layer L - t:
   chain 0.877, 0.666, 0.377, 0.126, 0.016 at t = 2, 4, 8, 16, 32 against the mean field 0.877, 0.665, 0.374, 0.123, 0.019
   (n = 256); half-life 4, 6-7, {{H1024}} layers at n = 64, 256, 1024; total relevance decays algebraically with a slower
   radius-driven tail [A]. The log-amplitude's closed relevance halves after about n/4 layers. The radial share of a net's
   output variance is rho(q) = m(q)/(m(q) + 2A q^{-2/3}) (0.35 at the median radius, n-independent; chain 0.35-0.37).
5. **How many directions are relevant at layer L - t, stationary** (HEURISTIC free product [C+A, relevance lane];
   NUMERICAL, PB3). PR_rel(t) = n/(tau + 2t). {{PR_SHORT}}
6. **Input regime** (HEURISTIC vertex [C+A]; NUMERICAL, PB6-PB8 hit). The input cloud's angular PR at layer l is
   n (1 - c_l)^2 / Var D_l -> 1.5 n/l: chain 166, 62, 18.8, 12.1, 6.1 at l = 1, 4, 16, 32, 64 (n = 256) against 167, 62, 19,
   10.3, 5.3, and the input-bits nets' 159, 57, 17, 9.6, 6.1. The radius share of the log-amplitude matches the kernel
   within 4% at every layer of 256 x 32. At 8 x 256 the input is one direction plus the radius after about 8 layers, 63%
   of inputs die (all-off layers), and any sigma >= 1e-3 hands the output to the noise within about 40 layers.
7. **Annealed versus quenched** (MEASURED, Part C). {{PC_LONG}}
8. **What the chain explains of earlier measurements** (section 6): the cloud's size (kernel fixed point at each net's
   radius), births, the interaction order's mechanism and Q^{1/6} growth, the flat low-order shares
   ({{CT_SHORT}}), the 3n/l gate decay, the "~10 directions" of the input at 256 x 32, and the amplitude/direction split
   gap (an averaging effect). It does not explain the top-k shape of the cloud spectrum or per-net residuals beyond the
   radius.
9. **Scorecard** {{SCORE_SHORT}}; review: {{REVIEW_SHORT}}.
