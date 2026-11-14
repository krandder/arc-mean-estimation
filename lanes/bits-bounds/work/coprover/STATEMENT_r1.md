# Bits-bounds: bounded-memory sweep estimators and the bits that matter at layer l (statement for the co-prover, round 1)

Lane: bits-bounds (theory, target M1). Fixed 2026-11-01 ~21:20Z. This file states the setting, what earlier lanes of
this project proved or measured, and the questions. It contains no new lemmas from this lane.

## 1. Setting

- Width n, depth L. Input x ~ N(0, I_n). h_0 = x, z_l = W_l h_{l-1}, h_l = relu(z_l) for l = 1..L, output a = h_L in
  R^n. W_l iid entries N(0, 2/n) (critical He-ReLU), independent over l, no biases.
- Noise regime ("Model S", optional): h_l = relu(W_l h_{l-1}) + sigma xi_l, xi_l ~ N(0, I) fresh each layer; sigma is a
  pure scale (relu is positively homogeneous). The noiseless input regime (sigma = 0) is the main case.
- Estimand mu(W) = E_x a in R^n. Per-net variance V(W) = tr Var_x a. Criterion (ARC's matching-sampling principle,
  random-MLP instance): an estimator succeeds at precision eps if |est - mu|^2 <= eps^2 V(W) (per net, or averaged over
  W). N-sample Monte Carlo (MC) scores 1/N in that normalisation. Cost unit: one n x n matrix-vector product; a forward
  pass costs L of them. The interesting regime is n -> infinity with L growing with n (L = alpha n in particular),
  budgets polynomial in n. ARC's own instance is n = 256, L = 32.
- Notation for a cut at layer l: the cloud P_l = law of h_l(x) over the input (and noise); the future map
  g_l = (layers l+1..L): R^n -> R^n, positively 1-homogeneous and piecewise linear (sigma = 0), so mu = E_{h ~ P_l}
  g_l(h). J_l(h) = Jacobian of g_l at h. L' = L - l layers remain.

## 2. Known from earlier lanes (you may use these; they are stated, not to be re-derived)

Communication and summaries across a cut (random front W_1..W_l, random back W_{l+1..L}, independent):
- (K1) One-way LINEAR summaries: the minimal size is the eps-rank of the cut operator; for the genuine ensemble at
  fixed (n, l >= 3, L') it is Theta(eps^{-2(n-1)/3}) as eps -> 0, via a rare event (probability ~2^{-n^2}) on which
  the cut state is a ray. Polynomial in n at fixed depth and eps. The back's averaged kernel is
  E_back g(h).g(h') = |h||h'| kappa_{n,L'}(cos angle(h, h')) at every finite width, with a (1-t)^{3/2} endpoint
  singularity coming from the gate kinks.
- (K2) Nonlinear readouts break this: the front's weights (n^2 l numbers) with a locally Lipschitz decoder are exact;
  Lipschitz decoders need between n(n+1)/2 and n^2 l numbers; two rounds of real messages are exact (the back sends its
  weights). Bits, any number of rounds, any decoder: at least n log2(1/eps) - O(1); one-way at least
  (n(n+1)/2) log2(1/eps) - O(1); (n^2 l + o(1)) log2(1/eps) suffice. So any hardness must be computational.
- (K3) ARC's basic cumulant truncation of order K, fed the exact cut cumulants, is biased on the ray event at every
  fixed K; it needs K log K >~ log(1/eps).

Unrestricted estimators:
- (K4) On random weights, determinism is no restriction (an exact symmetric derandomisation exists in an idealised
  arithmetic model), so the question is whether sampling, implemented as well as possible, is optimal.
- (K5) A multilevel shared-trajectory sampler beats radius-exact MC by Omega(n/log^2 n) at L = alpha n (under
  layerwise cost hypotheses). Construction: one reference direction Q is run through the net (normalised path q_l,
  per-layer norms); for an input direction U the control G_r(U) = m_n s_r |h_r(U)| q_L runs U through r layers only and
  then treats it as merged with the reference (s_r = product of the reference's norms after r); the telescoping sum
  over dyadic r with independent samples per level is unbiased; E|Y - G_r|^2 = O(1/r + n/L^2) relative to the angular
  variance. Measured ideal two-level gains: about 1 at L <= n/4 (1.01 at 256 x 32), 1.5x at L = n = 128, 15x at
  8 x 256.
- (K6) A certified branch-and-bound over input cones never beat RQMC with its deductive (bounds-only) estimate; its
  cost to nMSE 1e-4 grows about 10x per unit of width (widths 3-6). Restricted classes that provably fail: fixed point
  designs (gain <= about 4 in the mean-field limit at depth ~ width), polynomials of degree D in the weights, stable
  estimators, cell selection. No unrestricted lower bound is in reach (a super-linear time lower bound for an
  explicit problem). Open conjecture C0*: no estimator beats the best multilevel sampler by a polynomially growing
  factor at L = alpha n.
- (K7) kstar-frames, Proposition 2 (sigma = 0): the top-k right singular frame F of J_l along an input's path is
  determined by the future: any subspace computed from the input and W_1..W_l overlaps F, in expectation, at most as
  much as a random subspace plus the state direction. Measured: two inputs' frames agree (90% captured sensitivity)
  only while their states are within about 1.4/L' radians; about n/2 gates differ along the rest of the depth at that
  radius.

Measured structure (input regime, sigma = 0):
- (K8) Two inputs' states at layer l are at angle about 3 pi/l (iterated arc-cosine kernel, 1 - kappa^(l)(0) ~
  9 pi^2/(2 l^2)); the number of gates that differ between them at layer l decays like 3n/l. Finite input differences
  contract like the kernel; infinitesimal ones do not contract on average (E_W |J u|^2 = |u|^2 exactly; the typical
  |J u|^2 decays like exp(-2.5 t/n)); rank-conditioned Lyapunov exponents are about -(k + 1/4)/n per layer.
- (K9) tr Var_x(a) = V_rad + V_amp + V_dir exactly (input radius, amplitude = the input-dependent gain of the whole
  stack, output direction). At 256 x 32: amplitude 0.49, direction 0.47, |x| 0.034. At fixed L/n the direction term
  vanishes like 1/n and the amplitude carries nearly everything; its weight-averaged variance tends to a constant
  (10.65) as n, L -> infinity. The input's directional information at 256 x 32 lives in about 10 effective
  directions; by l ~ n the input cloud is >= 90% radial. Interactions of the input map: mean ANOVA dimension 9-12 at
  256 x 32, about 30% additive at every width.

Measured structure (noise regime, Model S):
- (K10) The stationary state exists and is unique; it is a thin near-Gaussian cloud whose angular size is set by the
  ReLU kernel's finite-angle contraction (two noise replicas at angle about 2.23 Q^{-2/3}, Q = |h|^2/(n sigma^2) ~
  0.58 n). About 0.5-0.6 sqrt(n) gates flip per layer from the newest noise; one flip causes about 0.2 n further gate
  differences over the next 2n layers and its effect lasts about 1.5 n layers. The mean interaction order of h_0 in
  layer blocks grows with width (1.4 -> 3.9 at n = 8-256); freezing all gates makes it exactly 1; letting only units
  within k noise SDs of their boundary switch recovers about 0.2, 0.3, 0.6, 1.0 of the excess for k = 0.5, 1, 2, 4.
  Every unbiased method's error falls like 1/compute; structured sampling buys constants of 2-8x that do not grow with
  width.
- (K11) The Gram matrix of R replicas sharing the weights (differing in noise or input) is an exact Markov chain with
  the weights integrated out, O(n R^2) per layer; it computes every rotation-invariant annealed replica quantity,
  including tangent (Jacobian) replicas, but not which directions.

## 3. The question (Kelvin, 1 November)

"I am frustrated by the failure to have a proper theory to account for 'near all the bits that matter' at a specific
layer (accounting for the Lyapunov covariances, or what future layers will amplify etc)." And earlier (his "hash"
argument): on any deep enough net, n effectively collapses to k* dimensions that interact fully connected through
random gates, like a hash over bits, followed by final layers that are hard to average, so nothing beats sampling.

Goal: tie hardness and upper bounds to one parameter, the bits that matter at layer l, N(l, eps), in a computational
model that covers real deductive estimators.

**Target 1, the model.** Define a computational model broad enough to include: ARC-style layer-by-layer deduction
(cumulant / moment propagation with a closure); Gaussian closures with gate splits (mixtures); branch-and-bound over
input cells; the multilevel shared-trajectory samplers of (K5). For example: estimators that sweep the layers (forward,
backward or both, with a bounded number of passes), keep a state of M numbers or bits, do poly(n) work per layer, and
may read the weights. Say precisely how each of the four families sits in it (passes, state, per-layer work).

**Target 2, N(l, eps) and lower bounds.** Propose a definition of the bits that matter at layer l, N(l, eps), that
accounts for both the past (the law of the state at layer l: its covariance, its Lyapunov structure) and the future
(what layers l+1..L amplify, where they are nonlinear). Then prove lower bounds on M (or on time) for eps-accurate
estimation of mu in terms of N(l, eps), in your model or in natural sub-models. For example: a forward-only sweep must
keep everything any future could need, while a sweep that first reads the future weights can keep only the relevant
bits; is there a provable separation between the two, and how large? Separate sharply what is provable
(information-theoretic, communication-complexity, streaming, approximation-theoretic or quantization lower bounds;
reductions) from conjecture. Note (K2): information bounds on unrestricted states are capped by the description length
of the weights, so say what kind of restriction makes N(l, eps) (a count about the input's or noise's bits) the right
lower-bound parameter, and whether that restriction still contains the four families.

**Target 3, upper bounds.** Give an estimator whose cost matches the bound: sample or enumerate the relevant bits and
integrate the rest. Compare it with the best multilevel sampler of (K5), and say whether and when (in which depth
regimes: L < sqrt(n), sqrt(n) < L < n, L ~ alpha n, L >> n) it could beat sampling by a polynomially growing factor.
Estimate N(l, eps) for random deep nets as a function of n, L, l, eps (and sigma in the noise regime), from the facts
in section 2 or your own derivations, with the reasoning, and say which estimates are provable.

**Target 4, the hash argument.** In this model, which part of Kelvin's hash argument survives as a statement about
N(l, eps) and the final layers, and which part fails? Be specific: a precise statement that is true (proven or
conjectured with evidence) and a precise statement that is false (with the counterexample or the reason).

## 4. Deliverables

Numbered sections, each claim marked PROVEN / PROVEN UNDER (stated hypothesis) / HEURISTIC / CONJECTURE. For each step
you cannot prove: the weakest precise conjecture that would close it, the conditional proof, whether it is a known open
problem or new ("unsure" if unsure), evidence for and against, and the cheapest numerical test that could refute it.
Mark the single bottleneck. Literature: only references you are confident of; mark uncertain ones "unverified".
