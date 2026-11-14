# Provenance: Claude (C) and gpt-6-astra (A), gram-chain lane

All astra runs: `codex-any exec -m gpt-6-astra`, read-only sandbox; the "model: gpt-6-astra" line is present in every
raw log's header (checked).

## Explainer check (A: 20:51:15-20:56:14Z, high effort)
Prompt `prompt_explainer_check.md`, raw `explainer_check.raw`, answer `explainer_check_answer.md`. The explainer v1 as
sent is `explainer_v1_as_sent.md` (sha in `explainer_v1.sha256`). 27 findings (13 errors); all applied in v2
(outbox/gram-chain-explainer-2026-11-01.md, section 7). It reproduced every exploratory number by rerunning my scripts.

## Round 1 (A: 21:06:52-21:31:10Z, xhigh; told not to read work/gram-chain/; it reports that it did not)
Prompt `prompt_r1.md` (sha in `prompt_r1.sha256`), raw `astra_r1.raw`, answer `astra_r1_answer.md`.
My FORMAL v1 (`FORMAL_v1_as_written.md`) was frozen at 21:14:08Z (sha in ../prereg_hashes.txt), before A's answer
existed; I did not look at A's running log before reading the finished answer at 21:32Z.

Found independently by both [C+A]:
- the slow (q, y = n^{1/3} ell) diffusion dq = ds + sqrt5 q dW, dy = -(y/q) ds + 2 sqrt(A) q^{-1/3} dW' with the angle
  slaved to A q^{-2/3} n^{-2/3}, A = 2.2309; the one-step coefficients Var(d ell) ~ 4 delta/n and E d ell ~ -ell/Q;
  SD(ell) -> 1.887 n^{-1/3} (C: 1.89 by simulating the SDE; A: closed form);
- the angle's relaxation time 1.488 Q^{1/3} layers;
- the radius diffusion's spectral gap 5/8 per n layers (C: Morse potential with lambda = 1, no excited bound state;
  A: bottom of the continuous spectrum);
- the closed-relevance curve w' = 1 - w^{3/2} (V_P = 1 - w) and the total-relevance curve from the shared-noise map;
- the free-position formula 1/PR = 1/PR_C + 1/PR_M - 1/n and PR_M ~ n/(1 + 2t) for t frozen-gate ReLU layers;
- the input regime's double-difference vertex recursion, PR_ang(l) ~ n (1 - c_l)^2 / v_l, numbers 166.5, 61.4, 18.7, 10.2,
  5.41 (A) vs 167, 62, 19, 10.3, 5.3 (C) at n = 256, and the 3n/(2l) asymptote;
- the across-net CV of the fixed-weight direction variance -> sqrt(Gamma(7/3)/Gamma(5/3)^2 - 1) = 0.679 (radius-driven);
- survival (1 - 2^-n)^L at sigma = 0 (0.367 at 8 x 256);
- integrability: raw-state annealed second moments diverge; annealed tangent means are carried by rare nets.

New from A (adopted in FORMAL v2, labelled [A]):
- the closed form m(x) = E[y^2 | q = x] = (24A/25) beta^{-2/3} e^{beta/x} Gamma(2/3, beta/x), beta = 2/5, with
  E y^2 = 3.5613, m(median) = 3.510, m(inf) = 5.342;
- the second-order correction E[delta | Q] = delta*(Q) + n^{-4/3} H(x) with an explicit algorithm, and the point that
  conditioning on one replica's radius vs the geometric mean changes H at this order;
- the moment operators L_X - j/x of the y^j equations have spectral bottom 5/8 as well (ratio correlations have an
  n-layer slow component), and along a typical radius history a ratio displacement contracts at E[1/X]/n = 5/(2n);
- the angular cloud's participation ratio grows like n^{2/3} (four-point balance: source 8 delta^2/n, damping
  ~ n^{-1/3}), PR_w ~ 1.0865 n^{2/3}; this contradicts the numerics lane's 1/k conjecture ((log n)^2). Registered as
  competing laws in Amendment A1 before the decisive runs;
- shared-noise relevance has a floor: unequal radii make the same noise rotate replicas differently (source
  ell^2/(2Q)), which balances the contraction at delta = O(n^{-10/9}) and interrupts the algebraic decay near n^{5/9}
  layers (CONJECTURE);
- the perturbation-survival formula with dilution, and the finite/tangent crossover eps_c ~ 3 pi / t;
- input regime: the raw-a radius-surgery share (0.037, 0.31, 0.56, 0.63 at l = 0, 4, 16, 31 for 256 x 32; complementary to
  my log-amplitude share) by an exact change of measure;
- per-net vs annealed closed relevance at large age: per-net mean ~ tau^{-3}, ratio of annealed variances ~ tau^{-5};
- cautions: freeness is a hypothesis (the state direction is distinguished); directional derivatives have divergent
  annealed second moments at finite n (two active output units); conditioning on a replica's radius changes the
  sampling law.
New from C (not in A's round 1): FORMAL 1.3 response-invariance proof; the exact library and tests; the mean-field
fixed-point expansion delta* = eps(1 - 0.7 eps); the PR_M one-layer moment (p = 3); the kernel-level log-amplitude share
(1/2 + C_l)/(1/2 + C_L) at sigma = 0; the one-step measurements kappa_x = 6.0, 6.8, 7.3 (n = 64, 256, 1024; A's
a_dd ~ 8 delta^2/n is the limit) and Var(d ell) n/delta = 4.05-4.09; the registered predictions.
