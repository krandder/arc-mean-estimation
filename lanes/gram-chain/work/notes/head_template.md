# The replica Gram chain as a theory of the bits that matter at a layer (1-2 November 2026)

{{STATUS_LINE}}

Lane: gram-chain (target M1), bead pool-qxszj1.23 under Kelvin's stationary ask pool-qxszj1. Work directory
`work/gram-chain/`. First deliverable, the explainer: `outbox/gram-chain-explainer-2026-11-01.md` (checked by
gpt-6-astra, revised). Model S throughout: h_l = relu(W_l h_{l-1}) + sigma xi_l, W_l iid N(0, 2/n), output
a = relu(W_L h_{L-1}). Labels: PROVEN, NUMERICAL (exact chain, sampled, bootstrap errors over chains), MEASURED (real
nets), HEURISTIC (mean field or leading order, tested), CONJECTURE. Provenance: [C] Claude, [A] gpt-6-astra, [C+A] both
independently. "Annealed" = averaged over the weights; "per net" = fixed weights. t = layers to go counting the output
layer, so layer l = L - t. Q = |h|^2/n, q = Q/n, delta = 1 - cos(angle between two replicas), A = 2.2309,
c_k = 2 sqrt2/(3 pi), theta* = arccos(1 - delta*), tau = pi/theta*.

## Summary for Kelvin

**Short answer.** The chain works as a theory tool, and with it the bits that matter at a layer have a quantitative,
weight-averaged theory: the exact chain confirms its closed-relevance curves to within 0.003-0.014 (absolute) at
n = 256-1024 and its other laws to within 10-30%, and real nets follow it once each net's radius is used. At layer L - t of a stationary net, the state
decides a fraction 1 - Y((t - 1)/T*) of the output direction's variance (Y' = 1 - Y^{3/2}; T* = 2.23 Q^{1/3}, about
2 n^{1/3} layers), and that part lives in about n/(n/PR_C + c t) directions (c ~ 1.1-1.6; PR_C = n/tau, tau = T*/1.5;
order n^{2/3} directions near the output); the radius carries a further, net-dependent share rho(q) of the output variance
for order n layers. In the input regime the input's
directional information at layer l lives in about 1.5 n/l directions (a 1/n four-point effect that the kernel cannot see),
and the radius carries the kernel share (1/2 + C_l)/(1/2 + C_L) of the log-amplitude. Your "Lyapunov covariance times
what the future amplifies, direction by direction" becomes a free product: the cloud's principal axes and the future's
amplified directions sit in random relative position (PROVEN for the frozen Jacobian given the past, HEURISTIC for
the full nonlinear relevance operator), so dimensions combine harmonically,
1/PR = 1/PR_cloud + 1/PR_future - 1/n (plus a gate-switching excess beyond a few layers). What the chain cannot give is
which directions: it is invariant under rotations of the layer that fix the replicas, so it carries no orientation
information; describing a k-dimensional relevant subspace to precision eps takes about k(n - k) log2(1/eps) bits, which
annealed theory does not supply (this is a description length, not a proven cost for estimating the mean). Per net, the
scale of all of this is set by the net's radius, which does not self-average; the radius law predicts a net's cloud size
with R^2 = 0.88-0.93 at n = 64-256.

1. **The tool** (PROVEN; tested). The replica Gram chain integrates the weights out exactly at any width, for any noise
   sharing, tangent vectors, perturbations and inputs (`lib/gc2.py`, 19 checks against explicit nets). It computes the
   weight average of any noise expectation of a replica Gram path: closed and total relevance, Sobol and noise-stability
   curves, participation ratios, and the across-net scatter of each. In the stationary regime raw-state annealed moments
   are infinite (heavy radius tail), so everything here uses directions and log radii.
2. **The stationary law of two to four replicas** (HEURISTIC limit [C+A]; NUMERICAL, n = 8-1024). The angle is slaved to
   the noisy-kernel fixed point delta*(Q) = 2.231 Q^{-2/3}(1 - 1.56 Q^{-2/3} + ...) with relative fluctuations of about
   1.8 n^{-1/3} (the rescaled law collapses); its median ratio to delta*(Q) rises to 0.989 and its mean is 1.000 at
   n = 1024. The radius ratio of two replicas is a slow diffusion jointly with the radius, with a closed form for
   E[ell^2 | q] [A]: the chain's SD(ell) n^{1/3} rises to 1.875 (0.025) at n = 1024 against the limit 1.887 and matches the
   closed form within 1-8% in every radius bin. The radius mixes at rate 5/(8n) per layer (spectral gap of the limit
   diffusion, PROVEN there); autocorrelations fall to 1/e in about 0.8n (radius), 1.0-1.4 Q (radius ratio) and
   1.2-1.4 x 1.49 Q^{1/3} layers (angle).
3. **How many directions the stationary cloud spans** (HEURISTIC four-point balance, [A] first, re-derived [C];
   NUMERICAL; MEASURED). PR_C = n theta*/pi = 0.67 n Q^{-1/3}, of order n^{2/3}, not the (log n)^2 of the numerics lane's
   assumed 1/k spectrum. In the chain, binned by radius, PR follows n theta*(Q)/pi over the whole radius range (a 3.5x
   fall from q = 0.2 to 10 at n = 256; measured/predicted 1.14-1.29 at n = 256 and 1.04-1.16 at n = 1024); on real nets
   the per-net PR falls
   with the net's radius with log-log slope -0.22 to -0.32 at n >= 32 (predicted -1/3; Spearman -0.73 to -0.87). A
   radius-independent 1/k shape cannot do this. {{PA9_SUMMARY}}
   With the relevance horizon below: PR_C x T* = 3n/2 at
   every radius to leading order (1.28n, 1.40n, 1.46n at the median radius for n = 64, 256, 1024).
4. **How much the state at layer L - t matters, and for how long, stationary** (HEURISTIC [C+A]; NUMERICAL; PB2 hit, PB1
   hit only under the revised analysis).
   The closed relevance of the state at layer L - t for the output direction is 0.877, 0.666, 0.377, 0.126 at
   t = 2, 4, 8, 16 for n = 256 against the mean field's 0.877, 0.665, 0.374, 0.123, and 0.928, 0.795, 0.566, 0.294 at n = 1024 against 0.928, 0.792, 0.567, 0.283; the
   curves collapse in (t - 1)/T*. The total relevance decays algebraically with a slower, radius-driven tail [A]. The
   log-amplitude's closed relevance collapses in t/n and halves after about n/4 layers. The radial share of a net's
   output variance has the closed form rho(q) = m(q)/(m(q) + 2A q^{-2/3}) [C, with A's m] (0.35 at the median radius,
   n-independent; HEURISTIC, a small-fluctuation variance proxy, not a Sobol share): the chain's ratio of means is 0.375,
   0.349, 0.354 at n = 64, 256, 1024, and on real nets the per-net radial share follows rho of the net's own radius
   (median deviation 12%, 11%, 5% at n = 64, 128, 256; PC7 hit).
5. **How many directions are relevant at layer L - t, stationary** (HEURISTIC free product [C+A; relevance lane];
   NUMERICAL; PB3 missed on 1 of 12 clauses). The linear free-product value n/(n/PR_C + 2t) is 9-16% below the chain's
   exact participation ratio at t = 1 (and t = 2 at n = 256) and 22-58% below it at t = 2-4; beyond a couple of layers,
   gates switching across the cloud spread relevance over more directions, and empirically PR_rel ~ n/(n/PR_C + c t) with
   c ~ 1.1-1.6 (closed version) instead of the frozen-gate 2. At n = 256 the closed relevance at t = 1, 2, 4, 8, 16 has
   variance-weighted participation ratios 39, 30, 24, 16, 9 (annealed moment ratios; the median net's is about 0.7 of
   these, section 5). The future's second spectral moment matches free probability (tangent probes within 3-5% of
   n/(2t) at t = 2-16).
6. **Input regime** (HEURISTIC vertex recursion [C+A]; NUMERICAL; PB6, PB7, PB8 hit). The input cloud's angular PR at
   layer l follows a 1/n vertex recursion that tends to 1.5 n/l: chain 166, 62, 18.8, 12.1, 6.1 at l = 1, 4, 16, 32, 64
   (n = 256) against the recursion's 166, 61, 18.7, 10.2, 5.4 and the input-bits nets' 159, 57, 17, 9.6, 6.1. The radius
   share of the log-amplitude matches the kernel within 4% at every layer of 256 x 32. At 8 x 256 the input is one direction plus the
   radius after about 8 layers (PR 1.1-1.4 at l = 16-128, among chains whose four inputs all survive) and 63% of inputs
   die in all-off layers. Small noise: at 256 x 32, sigma = 1e-3 leaves 99.94-100% of the variance decided by the layer-l state at every l; sigma = 1e-2 leaves 95-100% of the raw output and
   85-99% of its direction; sigma = 0.1 hands most of it to the noise (20-59% of the raw output, 2-38% of the direction
   decided at l <= 24).
7. **Annealed versus quenched** (MEASURED on 168 nets, n = 8-256; PC1, PC2, PC3, PC5, PC6, PC7 hit, PC4 missed). The
   per-net cloud size is not self-averaging: its across-net CV is 0.39-0.75 against the chain's 0.42-0.62 (rising toward
   0.68); divided by delta*(Qbar) the CV falls to 0.14-0.20 (squared CV cut by 87-97%; the radius law alone predicts a
   net's cloud size with R^2 = 0.88, 0.92, 0.93 at n = 64, 128, 256). Per-net closed relevance follows the mean field at the net's own radius within 0.02-0.08. Where the annealed count misleads:
   the chain's variance-weighted PR overstates the median net's dimension by 1.4-1.5x at n = 128-256 (small-radius nets
   have bigger clouds and dominate the weights; 1.35x in the limit), and the annealed relevance curve sits below the
   median net's (0.67 against 0.74 at t = 4, n = 256).
8. **What the chain explains of earlier measurements** (section 6): the cloud's size per net (A q^{-2/3} collapses 168
   nets), births, the interaction order's mechanism and growth (chain's finite-eps block order 1.90, 2.60, 3.34 at
   n = 16, 64, 256, slope 0.20, against the nets' 0.17-0.26), the flat low-order shares (chain C(t) = 0.156-0.186,
   0.359-0.389, 0.591-0.632 at t = 0.25, 0.5, 0.75 for n = 16-1024, per-coordinate sharing, against the closure's 0.175, 0.370, 0.603 and the
   input-bits nets' 0.16-0.18, 0.36-0.38, 0.60-0.64), the antithetic even share (0.198-0.209 against 0.23-0.27 on nets),
   the 3n/l gate decay, the "about 10 directions" of the input at 256 x 32, and the amplitude/direction split gap (an
   averaging effect). Not explained: the top-k shape of the cloud spectrum and per-net residuals beyond the radius.
9. **Scorecard and review.** {{SCORE_SUMMARY}}
