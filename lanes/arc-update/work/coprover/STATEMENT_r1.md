# arc-update lane: lemma-free statement for the co-prover (round 1)

Written 2 November 2026, 04:40Z, before any theory of this lane was written. It contains the setting, the estimator
classes, prior results from earlier lanes (with their labels), and the questions. It contains none of this lane's own
lemmas.

## Setting

- Nets: width n, depth L, h_0 = x ~ N(0, I_n), z_l = W_l h_{l-1}, h_l = relu(z_l), output a = h_L (ARC's contest form;
  the final linear layer of Wu et al. makes no difference). W_l iid N(0, 2/n) (He, critical), no biases, no noise.
- Estimand: mu(W) = E_x a in R^n for one fixed W (a quenched average). Per-net error nMSE = |est - mu|^2 / V(W),
  V(W) = tr Var_x a; plain Monte Carlo with N samples scores 1/N. ARC also uses the weight-averaged criterion
  E_W |est - mu|^2 <= eps^2 E_W V.
- Cost: one forward pass = 2 n^2 L flops (schoolbook). Gain of a method at its own cost C = (error of the comparator at
  cost C) / (error of the method).
- ARC's target instance: n = 256, L = 32 (the contest's Phase 1; L = n/8). ARC's open problem (Wu et al. 2026, sec. 7.3;
  Hilton's blog fn. 7): match sampling "with the depth growing linearly in the width", or as L -> infinity, or at fixed n
  as eps -> 0. "Matching sampling" (ARC's matching sampling principle): error <= eps^2 E Var at time
  O(eps^-2 x Time(forward pass)), for all eps, with a "mechanistic" (deductive) estimator.

## ARC's estimators (sources and exact claims: /home/agent/workspaces/mats/work/cut-rank-ext/notes/arc_estimators.md)

- Order-K cumulant propagation (Wu, Lecomte, Winer, Robinson, Hilton, Christiano, arXiv 2605.05179): state = symmetric
  cumulant tensors of orders 1..K of h_l (plus one trace scalar for odd K); linear step exact (tensor contraction with
  W); nonlinear step = per-neuron Hermite expansion of relu around N(mu_i, sigma_i^2) with a truncated diagram sum;
  everything above order K set to zero. Variants: basic (cost ~ n^{K+1} L), augmented, factorized (top tensor kept as
  O(n) factors per layer, cost ~ L^2 n^K for K >= 3). K = 2 is a Gaussian closure whose off-diagonal update keeps only
  the leading Hermite term ('simple'). Their conjecture: MSE <= c_K (L/n)^K. Proven only for polynomial activations at
  fixed L. Code: /home/agent/workspaces/mats/work/arc-noisy/ext/mlp_cumulant_propagation (main at 93d091a).
- Deduction-projection (Hilton halfspace note; W. Wu notes): propagate an "expectation machine" layer by layer and
  project onto a fixed family.
- Natural extensions to cover: exact Gaussian closures (moment matching with exact bivariate ReLU moments), Gaussian
  mixtures / gate splits (e.g. G. Wu's GMHP), layer-wise code (quantised-state) propagation, region (cell) merging and
  enumeration, branch-and-bound with symbolic bounds; each in a forward-only version (state at layer l computed from
  W_1..W_l only) and a future-aware version (may read W_{l+1..L} first, e.g. two-sided meets, backward value functions).

## Prior results (earlier lanes; reports in /home/agent/workspaces/mats/outbox; labels as given there)

- Information bounds on an unrestricted state are useless: the weights (n^2 L numbers) are a short exact description;
  nonlinear readouts of moment summaries collapse every precision-power bound; finite moment order determines the cut
  law at fixed architecture (cut-rank-ext-2026-10-31.md, PROVEN). So any lower bound must restrict computation.
- Relevance lane Theorem 1 (PROVEN, relevance-accounting-2026-11-01.md): given the past and the mean direction e, the
  first future layer is W_{l+1} = g e^T + M B^T with M iid N(0, 2/n) independent of everything; past-measurable
  transverse directions all get the same expected backward amplification.
- Forward-only defects (bits-bounds-2026-11-01.md, Prop 4.4, PROVEN): averaged over the independent future, the effect
  of a past-measurable measure defect at layer l is a kernel discrepancy under k(h, h') = |h||h'| kappa_{n,L-l}(cos angle).
  Telescoping (Thm 4.2): error = sum over layers of closure defects tested against the exact future.
- Exact single-Gaussian recursion at L = alpha n (bits-bounds round 3): annealed error >= c(alpha) E V / n PROVEN UNDER a
  one-layer radius hypothesis (H_R); unconditional for one Gaussianisation step plus exact suffix. Its gain over MC at
  its own cost (~2n passes) is therefore bounded. A product-law toy gives the order-K exponent a_K = 2 floor(K/2) - 1.
  Measured gain <= ~3 up to n = 256 at L = n (matrix-product cost), < 0.4 at the estimated implementation cost.
- Multilevel shared-trajectory sampler (unrestricted-estimators-2026-10-31.md, PROVEN UNDER schoolbook layerwise cost
  hypotheses): gain over radius-exact MC Omega(n / log^2 n) at L = alpha n; measured ~1.0 at 256 x 32, 1.2-2.4 at L = n.
  Its conjecture C0*: nothing beats this sampler by a polynomially growing factor at L = alpha n.
- Forward-only cell methods (bits-bounds Thm 7.1, 7.3, PROVEN in class): need log2 M >= rate-distortion of the cloud under
  the future-averaged distortion; point methods M^{-1-2H/d} PROVEN UNDER a Gaussian surrogate.
- Measured at 256 x 32 (arc-noisy-deep-2026-10-29.md, sigma = 0.001, medians of 24 nets): ARC's K = 2 augmented nMSE
  1.4e-3 at 1.9e9 flops; factorized K = 3 2.2e-4 at 2.06e11 flops; a Kerdock (mutually unbiased bases) design
  0.40/N (2.4x plain MC). A Gaussian replacement of the exact law at layer 8, 16 or 24 followed by the exact remaining
  layers leaves nMSE 8e-5 to 5e-4. ARC's K = 2 along L = alpha n: nMSE ~ n^{-0.41}, n^{-0.56}, n^{-0.74} at
  alpha = 1/8, 1/4, 1/2 (hardness lane).
- Structure (gram-chain, relevance, bits-bounds, input-bits lanes; MEASURED and HEURISTIC): the angular cloud at layer l
  has participation ratio ~1.5 n/l; angular size ~3 pi/(l + 6); the future of depth t is linear on the cloud only below
  an angle ~2.45/t; the output's variance is made early (log-radius martingale; share left after layer l ~ 8.3/(l + 9));
  at 256 x 32 the input variance splits amplitude 0.49 / direction 0.47 / |x| 0.03; mean Hermite degree of the value
  function on the layer-l Gaussianised cloud 21, 7.7, 4.1, 1.9, 1.3 at l = 0, 4, 8, 16, 24; linear features for 99%
  N(l, 0.01) = 256, 192, 128, 80, 48; learned local codes (one-ReLU-layer encoder) need > 256 bits at l <= 4 for 10%
  error, 135 at l = 8, 43 at l = 16, ~25 from l = 24 (output's own 19-39); consecutive layers' learned codes are related
  by near-linear threshold maps (bit-accounting lane, v1).

## Questions (label every claim PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE)

1. Model. Define a computational model that contains ARC's estimators (all K and variants) and the natural extensions
   above, forward-only and future-aware, in which a nontrivial lower bound on error at given cost can actually be proven.
   Say exactly which estimators it contains and which it does not.
2. Lower bounds. Prove the strongest lower bounds you can in that model, relative to the best sampler (plain MC, RQMC,
   the multilevel sampler), (a) asymptotically at L = alpha n, (b) at fixed (n, L) = (256, 32) with explicit constants
   where possible. In particular: for order-K cumulant hierarchies, is ARC's conjectured c_K (L/n)^K tight (a matching
   lower bound at fixed L, large n), and what is the right exponent at L = alpha n? How can cancellation between the
   defects of different layers be excluded, or must it be assumed?
3. Forward-only versus future-aware. What exactly must a forward-only method carry, given that the future is
   rotation-invariant relative to the past? What must a future-aware layer-wise method carry? Is there a theorem of the
   form "both pay for the growth of the cloud's joint (higher-order) structure with depth, unless it factorises"?
   Make "factorises" precise.
4. Kelvin's hypothesis, latest form: "whether the bits get scrambled when correctly compressed". Give a precise
   formalisation (or two), and prove, refute or reduce each to a checkable condition.
5. Steelman the positive side: the strongest constructions that could still give a deductive win at 256 x 32 or at
   L = alpha n (low-order ANOVA parts, depth synchronisation, the multilevel sampler's structure used deductively,
   factorised codes, anything else), with the best quantitative case you can argue for.
6. Falsifiable predictions: give 3-6 quantitative predictions at 256 x 32 or along L = n/8 (n = 32-256) that would
   confirm or refute your bounds, each with the cheapest test.

Prefer a correct weaker statement to a strong wrong one. Write everything to stdout.
