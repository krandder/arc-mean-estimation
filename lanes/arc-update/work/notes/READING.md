# Reading notes: what the earlier lanes establish, as used by the arc-update argument (2 November 2026, 04:45Z)

Labels as in the source. Paths relative to /home/agent/workspaces/mats/outbox unless stated.

## Information-theoretic route is closed (cut-rank-lower-bound-2026-10-30.md; cut-rank-ext-2026-10-31.md)
- One-way LINEAR summaries of a front need r(eps) = Theta(eps^{-2(n-1)/3}) numbers at fixed (n, c >= 3, d) (PROVEN; rests
  on a rare ray event, constants ~2^{-n^2}). At fixed depth and precision r is polynomial in n; exp(c k*) refuted.
- Nonlinear readouts collapse it: the front weights (n^2 c numbers) or the ray mean decode exactly (PROVEN). Bits: any
  rounds >= n log2(1/eps) - O(1) (PROVEN). Finite moment order Q(n, c) determines the cut law (PROVEN, not explicit).
- ARC's basic truncation fed EXACT cut cumulants is biased on the ray event at every fixed K; bias >= c exp(-C K log K)
  (PROVEN, narrow). Measured 1-4% at K = 4 on a ray family.
- Coverage map: ARC's ReLU closures are nonlinear without uniform regularity: no dimension bound applies; "what is left is
  running time".

## Running-time route (unrestricted-estimators-2026-10-31.md)
- Determinism is no restriction on random weights (PROVEN in idealised arithmetic). Batched MC beats serial by n^{0.19}.
- Certified branch-and-bound: deductive midpoint never beats RQMC; cost x10 per unit width (MEASURED).
- Multilevel shared-trajectory sampler: gain Omega(n / log^2 n) over radius-exact MC at L = alpha n (PROVEN UNDER
  layerwise schoolbook cost hypotheses); ideal two-level gains ~1.0 at 256 x 32, 1.5x at L = n = 128, 15x at 8 x 256.
- C0* (bottleneck CONJECTURE): no estimator beats the best multilevel sampler by a polynomially growing factor at
  L = alpha n. Unrestricted lower bounds = super-linear time lower bounds; no technique known (HEURISTIC).
- Restricted classes: positive-weight designs gain <= ~4 (mean field, PROVEN [A]); polynomials of degree D in the
  weights: risk = Hermite tail T_D, T_D = Theta(S D^{-2/3}) in mean field (PROVEN [A]); cell selection fails.
- Plug-in at 256 x 32: harmonic-degree 1-2 share of angular variance 0.30-0.43 (2-design ceiling 1.7 vs RB-MC).

## Bits theory (bits-bounds-2026-11-01.md)
- Model: p-pass sweeps with M bits of state; ARC cumulant propagation (via a stated measure reconstruction), Gaussian
  closures with splits, B&B, multilevel sampler all placed (PROVEN placements).
- Telescoping identity (Thm 4.2): error = sum of closure defects tested against the exact future. Forward-only defect,
  future-averaged = kernel discrepancy under k(h,h') = |h||h'| kappa_{n,L'}(cos angle) (Prop 4.4, PROVEN [C+A]).
- Future's linearity scale ~2.45/L' rad (PROVEN one layer, mean field L'); rough beyond.
- Variance made early: log-radius martingale (PROVEN every width); share left after l ~ 8.3/(l + 9) (mean field).
- Cloud PR = 1.04 n/l + 1.38 (MEASURED, post hoc fit).
- Bits formula N_l(eps) ~ (d_l/p) log2(D_l(1)/eps^2) (HEURISTIC; registered test 6/6, intermediate counts within ~2x).
  At 256 x 32 with d = PR: 224, 112, 45 bits at l = 4, 8, 16 (eps^2 = 0.1), matching learned local codes 230, 104, 34-52.
- Lower bounds: forward-only cells log2 M >= R(eps^2 V) (PROVEN); cell separation (PROVEN under hypotheses);
  merges ~ stratified sampling D/M (identity + conditional upper bound); point methods M^{-1-2H/d} under (G).
- Averaging methods (closures) evade all of these. Exact single-Gaussian recursion: annealed error >= c(alpha) E V/n at
  L = alpha n PROVEN UNDER (H_R) [one-layer radius hypothesis]; unconditional for one Gaussianisation step + exact
  suffix (first step raises mean radius by 9/(16 sqrt n); radius kernel survives with e^{-5 alpha/4}). Gain <= ~470
  annealed. Measured gain (matrix-product cost 2n passes): L = n: 0.38, 0.28, 0.63, 3.26, 0.87, 1.02 (n = 16..256);
  L = n/2: 2.28, 0.59, 0.80, 0.89, 0.40; at estimated implementation cost < 0.4 everywhere (0.005-0.37).
- Order-K product-law toy: radius-based exponent a_K = 2 floor(K/2) - 1 (PROVEN UNDER toy); "meets the own-cost MC
  criterion" (bounded gain). Transfer to actual cumulant recursion NOT proved. Possible failure mechanism: successive
  Gaussianisations cancel the radius defect (HEURISTIC).
- Hash proposition: random hash with known ensemble mean is easy to average (gain >= 4(K-1)/K).
- C4 (= C0* for sweeps), the bottleneck: closures and adaptive point methods on actual nets uncovered.

## Relevance (relevance-accounting-2026-11-01.md)
- Theorem 1 (PROVEN [C+A]): given the past and the mean direction e, W_{l+1} = g e^T + M B^T with M iid N(0,2/n)
  independent; every past-measurable transverse direction gets the same expected backward amplification (2/n)|K|_F^2.
  Covariant Lyapunov vectors k >= 2 are future-measurable.
- Free-product relevance spectrum (PROVEN for Haar-oriented operator; HEURISTIC for cloud-averaged Jacobian).
- At 256 x 32 (4 nets, medians): V/E|a|^2 ~ 0.051-0.057 flat; degree-1 share 0.22, 0.48, 0.61, 0.77, 0.92, 0.93, 0.97 at
  l = 0, 4, 8, 16, 24, 28, 31; mean Hermite degree D = 21.2, 7.7, 4.1, 1.9, 1.26, 1.10, 1.04 (exact: D = R x
  (tr Sigma/E|X|^2)/(V/E|a|^2), R per-net gain factor 0.61-2.4).
- N(l, 0.01) = 256, 192, 128, 80, 48, 48, 48 at l = 0, 4, 8, 16, 24, 28, 31 (point estimates, best of three bases);
  first-chaos (linear) only 7-30. Gates: G(l, 0.01) = 4913 (l = 8), 1952 (16), 521 (24) in importance order; 5-9% of
  gates flip per sample vs the mean path.
- Conditional lower bound (PROVEN UNDER iid Haar gate normals + isotropic r-dim cloud [A]): any k-dim projection leaves
  >= (1 - k/r) of the degree-2 part.
- Exact conditional-mean control on top-k AS features at the input: gain <= 1.05, 1.33, 1.80, 3.11 (k = 1, 16, 64, 128).

## Gram chain (gram-chain-2026-11-01.md)
- Exact replica Gram chain (PROVEN). Response invariance: annealed theory cannot name directions (PROVEN).
- Input regime: angular PR(l) ~ 1.5 n/l (vertex recursion; chain 166, 62, 18.8, 12.1 at l = 1, 4, 16, 32 for n = 256).
- Radius carries share (1/2 + C_l)/(1/2 + C_L) of log-amplitude (within 4% at 256 x 32).
- 256 x 32, sigma = 1e-3: layer-l state decides 99.94-100% of variance: input regime holds.

## Input bits (input-bits-2026-10-31.md)
- Exact split at 256 x 32: amplitude 0.49, direction 0.47, |x| 0.034 (medians). Annealed mean Hermite degree of the
  input map = n / E_W V exactly (PROVEN [A]); ~19 at ARC; grows like n at fixed L/n. ANOVA mean dimension 9-12; ~30%
  additive, ~20% pairwise. Gates differing between inputs ~3n/l (kernel). Amplitude collects variance over ~100 layers:
  E_W V_amp -> C_inf = 10.65 (PROVEN [A]).
- RQMC over inputs at 256 x 32: 1.25-1.72x; model G_pred = 1/(1 - S1 - (1 - rho_2(N/d)) W2_off) within 1.5x on 44/48.
- Multilevel two-level gain at L = 32 fixed does not grow with width (1.08, 1.02, 0.93 at n = 64, 128, 256).

## Stationary lanes (stationary-regime, stationary-numerics): noisy regime; at ARC's point sigma = 1e-3 negligible
  (input share 0.9992). Interaction order of the noise map grows like n^{0.26}; gate switching is the mechanism.

## kstar-frames (kstar-frames-2026-10-30.md)
- Proposition 2 (PROVEN, sigma = 0, spectral gap): any frame computed from the input and weights up to layer c overlaps
  the true k*-frame in expectation at most as much as a random frame plus the state's own direction.
- A learned polynomial-size map recovers 93-99% of sensitivity weight (so directions are not a hash of the input).

## Narrow-deep (narrow-deep-m1-2026-10-30.md) and nd-exact (work/nd-exact, in progress)
- Width 8, depth 256: sample-free estimators do not reach M1; isolated wins are cancellations.
- Region census (2^22 inputs): regions of layers 1..d carrying 99% of output mass: 1.5-1.9e3 (d = 2), 0.7-1.7e4 (d = 4),
  3.4-5.9e4 (d = 8), 4-11e4+ (d = 16-32). Deterministic cell code CS2 at 2^25 mv: nMSE 7.5e-3 (net 203).

## ARC empirical numbers at 256 x 32 (arc-noisy-deep-2026-10-29.md, sigma = 0.001, 24 nets)
- K = 2 augmented 1.4e-3 [1.1e-3, 1.6e-3] at 1.9e9 flops; factorised K = 3 2.2e-4 [1.5e-4, 2.9e-4] at 2.06e11.
- Kerdock MUB design 3.6e-5 at 6.8e10, 6.7e-6 at 2.72e11 (0.40/N; plain MC 1/N; one pass ~4.2e6 flops).
- Gaussian replacement at layer 8/16/24 then exact: nMSE 8e-5 to 5e-4 (3 nets); one-step error dominated by
  per-neuron 3rd/4th cumulants of next-layer pre-activations (19-120x), top-8 modes recover only 1.9-4.1x.
- An error at layer l keeps ~(l/L)^3 of its energy (participants, mean-field cosine law).
- Contest: Phase 1 256 x 32, best methods "variations of sampling" (organizer); participants: moment chain fed true
  means and covariances at every layer 8.1e-7 vs best structured sampler 1.5e-7 (raw MSE, unreproduced).
- Hardness lane: ARC K = 2 along L = alpha n: nMSE ~ n^{-0.41, -0.56, -0.74} (alpha = 1/8, 1/4, 1/2), gain 2-8x at
  n = 32-128, ~1 at 1024.

## Bit accounting (work/bit-accounting/bit-accounting.md v1; phase 1 certified curves in progress)
- Unrestricted encoder: every layer needs exactly the output's bits (shortcut, PROVEN).
- Local encoder (one ReLU layer): ARC 256 x 32 needs > 256 bits at l <= 4 (10% error), 135 at l = 8, 43 at l = 16, ~25
  from l = 24; output's own 19-39. At 1%: > 256 at l <= 8.
- Not scrambled: next-code bits predicted by linear threshold of current bits (96% of predictable part); real codes
  74-98% linear. But lossy: next code predictable as a whole 8-37%; the loss is information, not noise.
- Code-law propagation: bias 1e-3 to 1e-4, does not fall with bits.
- bit-accounting-arc (certified per-layer curves at 256 x 32): GPU runs started 03:56-04:04Z; no results yet.

## Added 05:05Z (main, from nd-exact draft work/nd-exact/nd-exact.md; astra review running; 6 eval nets, 8 x 256)
- Certified deterministic code (exact cone masses, gates certified per cell, exact maps, certified tail): 0 of up to
  890k cells certified; 23-106x worse than RQMC, 108-910x worse than RQMC with the exact tail (RQMCJ); 3.1-8.5 bits
  per halving of error vs sampling's 2.
- Region code with free exact integration still loses to RQMCJ by 7-1,222x.
- Mechanism: a typical direction lies 0.003-0.006 from a region boundary in 7 angular dimensions -> certifiable cells
  ~1e16-1e18. Single layer: exactness wins at widths 2-3, loses from width 4 (width crossover for part C).
- What pays is the exact zero-bit tail (RQMCJ 3-15x better than RQMC): structured sampling, not deduction.

## Added 05:35Z (main; bit-accounting interim, NOT certified: an astra review found 8 fixable issues, rerun as P1-A by ~11:30Z)
- 16 x 16, seeds 5000-5001, local class, bits for 10% / 1% output error: l = 0: 24-35 / 55-62; l = 4: 3.7-5.9 / 13-21;
  l = 8: 2.1-2.7 / 9.2-9.7; l = 12-15: 1.7-2.6 / 5.8-7.3; output 1.7-2.4 / 5.6-6.5.
- Slope: ~8-10 bits per halving of error at the input (where the law is computable) vs ~1-1.4 near the output (below
  sampling's 2, but there the law is not computable). Main: "the computability-vs-slope split". Provisional.

## ARC sources re-verified (notes/ARC_SOURCES.md, sonnet worker, 04:41-05:04Z; 93/93 quotes match)
- No official Phase 1 or Phase 2 results published (Phase 2 winners ~15 Nov 2026). Code HEAD still 93d091a.
- Hilton 23 Jun 2026 (LessWrong comment): "Our existing algorithms scale poorly with depth"; warm-up winners were
  factorised K = 3 plus learned networks on cumulant features.
- Christiano 3 Jun 2026 (same thread): "We think there probably do exist adequate algorithms for analyzing random
  networks and the reason we haven't found them is because so little research has addressed the question head on."
- Phase 1 budget 2.72e11 flops = 6.5e4 forward passes at 256 x 32.
