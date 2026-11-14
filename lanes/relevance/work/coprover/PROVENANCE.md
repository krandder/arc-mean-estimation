# Provenance: Claude (C) and gpt-6-astra (A), relevance lane

## Round 1 (A: launched 21:10:16Z, xhigh, read-only, told not to read work/relevance/)
- Prompt `prompt_r1.md` (sha in `prompt_r1.sha256`), raw `astra_r1.raw` (model line: gpt-6-astra), answer
  `astra_r1_answer.md` (extracted from the raw log's last "codex" block once it finishes).
- My theory v1 (`FORMAL_v1_as_written.md`, sha 23ab1bb1, frozen 21:17:35Z) was written before A's answer.
  Disclosure: the freeze command at 21:17:35Z printed the last 300 bytes of A's running log; they contained only
  harness lines ("hook: PostToolUse", "hook: PostToolUse Completed"), no content. No other part of A's log was read
  before the freeze. PREREG Part 1 was hashed at 21:23:36Z, also before A's answer.
- A finished 21:34:28Z (exit 0); answer extracted 21:38Z (the raw log repeats the final message twice; one copy kept).

Found independently by both [C+A]:
- Decoupling: given the past, the future map is rotation-invariant about the mean direction (same split of W_{l+1}
  into a part along e and a transverse Gaussian block); the brief's "1/k forward variance x k-th backward amplification"
  is the wrong product; along every fixed (past-measurable) cloud axis the averaged backward amplification is the same
  (A: E_U[Sigma^{1/2} U Lam U^T Sigma^{1/2}] = (tr Lam/n) Sigma; C: Corollary 1b).
- The relevant linear matrix is Sigma^{1/2} B^T B Sigma^{1/2} with the cloud-averaged Jacobian B (C: FORMAL 1c, 2; A: Q2);
  scalar readout: N_1 = 1.
- Degree spectrum from the iterated kernel, s_d = Taylor coefficients of f_t(c_l + (1 - c_l) rho) (identical formulas),
  with the same large-depth asymptotics s_1 ~ l/L, s_2 ~ 3 l t/(4 L^2), D ~ (L/l)^2 (C: FORMAL 3a with theta_l ~
  3 pi/(l + 6); A: Q3).
- Finite width is leading order at ARC: the kernel alone gives s_1 = 0.11 at l = 0 (A), against 0.26 from A's exact
  Gram chain and 0.29 on my evaluation net 4000 (C: FORMAL 3c adds an amplitude channel; A: "the missing amplitude
  contribution materially changes the answer").
- Stationary regime with independent future noise: the L0 recursion without +1 in the cross term; angular relaxation
  rate theta*/pi = 0.672 Q^{-1/3} (A) = my lambda_a ~ theta*/pi + 1/Q (C, FORMAL 3a).
- The exact flip identity is valid but not an orthogonal decomposition; the frozen Jacobian is not B (C: FORMAL 2,
  DEFINITIONS 4.2; A: Q8).
- Degree-2 part as a sum over gate boundaries with normals pulled back to layer l; one future layer:
  V_2 = (1/2) sum_i s_i^2 phi(eta_i)^2 exactly (A); C: the same structure (DEFINITIONS 4.1).
- Numbers on other nets agree with mine: ARC (A's net 25600) N_vec(90/99/99.9%) = 189/231/246 at l = 0, 13/61/115 at
  l = 16, 8/39/83 at l = 31; scalar 1/3/20 at l = 31; narrow-deep survivors N = 1 from l = 32 on; stationary n = 64:
  19/39/51 at t = 1, 14/37/50 at t = 8.

New from A (to be used in theory v2, attributed):
- A rigorous LOWER bound: the first-chaos eigenvalue tail sum_{j>k} lambda_j(C_1) is <= the optimal residual of any
  k-dimensional P, so N(l, eps) >= min{k : sum_{j>k} lambda_j(C_1) <= eps V}; with the AS Poincare upper bound this
  brackets N. At ARC l = 31 (A's net): N >= 7, 37, 79 at eps = 0.1, 0.01, 0.001.
- The frozen-radius angular model has a long-time degree spectrum s_1 -> e^{pi/(2 sqrt 3)}/(2 sqrt 3) = 0.715,
  s_2 -> 0.179, D -> 3/2 (it does not become linear).
- Radial memory: squared-response rate about 5/(2n) + 1/Q ~ 4.23/n (my v1 had 5/n).
- At t = 64, n = 64 one mean-gradient direction captured ~71% and the cloud-mean direction ~30%: the slow coordinate is
  a future-dependent response, not the radius itself (CONJECTURE).
- Estimation caveats: the control-variate hybrid's variance formula; large N does not exclude an exact sample-free
  expectation (one layer: E relu(w.H) = s phi(eta) + (w.m) Phi(eta) in any dimension), so N is not an estimation lower
  bound without a computational model.
- A one-layer counterexample: the cloud-averaged B is not transversally isotropic (Phi(w.m / sqrt(w^T Sigma w))
  weights distinguish cloud axes), so the free-product statement for B is not exact (my v1 labelled it HEURISTIC).
- Predictive rate-distortion as a literal bits definition (with encoder cost recorded separately).

New from C (not in A's round 1): the dev and evaluation measurements of the free-product N_1 against the forward-only
count; the generic (Haar) capture model for degrees >= 2 and its dev check; the narrow-deep exact-synchronisation
mechanism (single-active-unit bottlenecks at n = 8); the gate counts G(l, eps) (Part 2); the radial-versus-top-direction
measurements in the stationary regime (Part 2, PS1).

## Round 2 (A: 21:48:48Z-22:04:53Z, xhigh, read-only, could read work/relevance; audit of FORMAL v1-v2, code, scorers)
Prompt `prompt_r2.md` (sha in `prompt_r2.sha256`), raw `astra_r2.raw` (model line gpt-6-astra), answer
`astra_r2_answer.md` (one copy of the repeated final message). v2 was frozen at 21:48:41Z, before this round started.
Accepted and applied: T1 items -> FORMAL errata E2-E17 (Corollary 1a scope, 1c bulk-only, 3a conditions, the stationary
s_1 >= 0.9 claim retracted, homogeneity is not first chaos, additive channel kernel heuristic, generic capture is a model
and the v2.4 lemma withdrawn, the N rule's missing common subspace and dropped high-degree mass, the debiased lower bound
uncertified, v2.2/v2.3 scopes, v2.5/v2.6 overstatements); T2/T3 -> Amendment 2A (cross-realisation first-chaos
subtraction, training inputs for gate spreads, SEs stored and the +2 SE rule applied, holdout complement for N_>=2,
scorer completeness and seen/prospective split) and the corrected Part 1 scorer; T4 -> the first-chaos counts reported as
uncertified estimates; T5 -> FORMAL v3.2 (conditional Wishart lower bound) [A]; T6-T8 -> the narrowed stationary and M1
statements. Not applied: none rejected; T4's certified bound was not computed (vacuous at the sample sizes run).

## Round 3 (A: 01:28:05Z-01:42:53Z, xhigh, read-only; told to read only coprover/r3_inputs/, the prompt, lib/rel.py,
## lib/accounting.py, lib/theory_v1.py, lib/theory_v2.py and work/stationary/lib/, and not FORMAL.md, PREREG.md,
## lib/theory_v33.py, scratch/, results/, logs/ or frozen/ (instruction only; the sandbox does not enforce it))
Prompt `prompt_r3.md` (sha in `prompt_r3.sha256`), inputs `r3_inputs/` (FORMAL.md through v3.2; raw per-net data for
nets 4000-4005 with the v2 predictions), raw `astra_r3.raw` (model line: gpt-6-astra), answer `astra_r3_answer.md`.
My theory v3.3 (FORMAL.md v3.3, lib/theory_v33.py) was frozen at 01:26:28Z, before the round started; I read A's
answer at about 01:50Z.
Found independently by both [C+A]: the exact rewriting D = Gamma (tr Sigma/E|X|^2)/(V/E|a|^2) with the per-net
tangent-to-forward gain ratio Gamma (my R); a forward-only predictor from active counts and radial gains along the
forward trajectories; its single-ray log law with mean 2t/n and variance 4t/n.
New from A: the trajectory-conditional predictor with radial transfer (more accurate than mine: median error 2.8%
against 3.6%, max 18% against 27%, on the seen nets); exact single-ray log moments and the H recursion; the proof that
Gamma does not determine s_1 (s_1 = C D with the Jacobian coherence C), which removes any general justification for my
direction-channel s_1 rule; the proof that the input radius has zero first chaos and the resulting radial-channel
correction of v2's s_1 (it explains most of the input bias); the correction of my claim that the budget is invariant to
Gamma. Implemented from A's text as lib/theory_v34_astra.py and registered as Amendment 3C (02:03:18Z) before any output
of the fresh nets was read.
New from C (not in A's round 3): the radial-fraction term r + (1 - r) R_perp (A has the per-sample r(X) instead) and the
direction-channel s_1 rule (HEURISTIC; A shows it is not general).

