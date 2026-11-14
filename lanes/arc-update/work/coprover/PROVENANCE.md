# Co-prover provenance (gpt-6-astra via codex-any; model line checked in every raw log)

## Round 1 (independent; launched 04:40:27Z from the lemma-free STATEMENT_r1.md, sha 663542c9; exit 05:00:57Z)
- My FORMAL v1 was frozen at 04:54:16Z (sha 910255ee, notes/formal_hashes.txt) before the answer existed; I first read
  the answer at about 05:27Z. The prompt told astra not to read work/arc-update beyond the statement; the read-only
  sandbox cannot prove it did not (its log shows reads only of the statement, the outbox reports, the fact sheet and
  ARC's code; checked by grep of the raw log for "arc-update/" paths: see below).
- Found by both independently: telescoping; the forward-only information object is the future-averaged kernel
  discrepancy; future-aware methods have no information obstruction (the state can be the answer); "factorises" needs a
  representational restriction; repeated exact Gaussian closure has bounded gain under H_R; any fixed-order closure
  with error n^{-p} at cost n^{K-1} passes cannot beat the multilevel sampler polynomially unless p > K.
- New from astra: E V bounds (0.4995 < E V < 20.14 at 256 x 32); row-access lower bound (tiny budgets only); a
  fixed-depth lower bound for ARC's basic K = 2 'simple' at L = 2 (liminf n^2 R >= 0.110); an explicit cancellation
  example showing forward-only access alone does not exclude cancellation; the Gram-matrix no-cancellation criterion
  (lambda_min(G) >= eta); factor-graph elimination width as the precise meaning of "factorises"; Formalization A of the
  scrambling hypothesis (exact update iff H(Z_{l+1} | Z_l) = 0; Fano; cheap transitions do not imply cheap law
  propagation; future-aware correct compression makes the transition the identity); Formalization B (moment-summary
  interface: parity pair; unknown-bias table oracle with normalised risk ~1/(q + 2), i.e. sampling-like); positive
  side: an analytic first-radial control with O(1/n) bias at O(n^3) setup, the control-variate acceptance criterion
  eta < (0.40/a)(1 - B/N), and fixed-architecture region integration at polylog(1/eps) cost (eventually wins as
  eps -> 0, constants unbounded); six predictions (E V interval; sqrt(n) E rho_1 -> 0.5625; H_R sign; one-replacement
  floor >= 1.49e-5 at 256 x 32 given sqrt(256) E rho_1 >= 0.53; radial-control accuracy Theta(n^{-3}); code transitions
  vs law propagation).
- New from me (not in astra's answer): Mehler-positive pricing with the radially normalised moment features M_d at
  every finite width (FORMAL A2); what moment matching cancels (A3); the random-probe lemma and the Frobenius pricing of
  forward compression (A4); the suffix-split bound and the exact last-layer bottleneck for Gaussian / Gram-Charlier-
  output closures, which needs no no-cancellation assumption (A5); per-net attribution (A6); correlation growth and its
  test (B2-B3); the price-ladder arithmetic (C1-C2); "frames scrambled, codes not" (S1-S4).
- Checks I made of astra's items: pending (scheduled with the round-2 audit).

## Round 2 (audit and lemma exchange; launched 05:18:20Z, exit 05:41:36Z; model line gpt-6-astra)
- Prompt hashed in statement_hashes.txt. Read by me at 05:42Z; applied as FORMAL E7.
- Audit outcome: A1, A2, A4, A5, A6, C1, C3, D, F1, F2, S4 correct (with stated conditions); A3 wrong as worded
  (counterexample accepted); B1 wrong as a computational claim (diagonal-tensor counterexample accepted); B2 HEURISTIC;
  B3 "only way" wrong; C2 ratio reversed; F3 conflated projections with test functions; CHECK-1 incomplete for
  'augment', averaged metric and the variance floor (all accepted after reading kprop_harmonic.py and wick.py myself).
- New from astra: b_0 >= 1/pi monotone in depth; the 'simple' Gaussian reconstruction and its conditional floor
  (H_{R,s,tau}); the depth-unattenuated one-replacement bound; the hypothesis-free last-row certificate; the
  conditional radial exponent table; replica form of the flattening statistics; measurement corrections; the threshold
  counting (knapsack) separation between cheap transitions and hard law propagation; the RMS-vs-squared convention for
  "bits per halving".
- My checks: the Isserlis constants (my v1 derivation agrees); the CHECK-1 corrections by reading the code
  (avg_metric path and relu_wick_coef floor); the PR-bias point (rescored both ways). Not rechecked: the finite-n decimal
  1.03e-5 (astra says it is not interval-certified) and the J_n matrix of eq. 29.

## Round 3 (the strongest positive lead and its ceiling; launched 06:15:23Z, exit 06:39:17Z; model line gpt-6-astra)
- Prompt hashed in statement_hashes.txt. Files read (from its log): FORMAL.md (v1 + E1-E8), its round-1 and round-2
  answers, logs/eval_attr_200.log, logs/hr_200.log, runs/attr_s200.json, scratch/kernel_spectrum.py, run_attr.py,
  hr_test.py, a grep of lib/au.py. It did not read PREREG.md or the report. Read by me 06:43Z; applied as FORMAL E10.
- New from astra: an implementable radial closure (projected-Gaussian direction, lognormal radius) with O(J n^3)
  fixed-accuracy cost; the oracle radius kills M_0 exactly and the lognormal fit leaves O(n^{-3/2}); the first-layer
  angular obstruction after radius correction (skewness gamma_3 = a + 2a^3; finite-width cubic price
  b_3 >= e^{-5 beta/4}/(3 pi^2 n)), giving p <= 2 for the radius-corrected single cut; the exact amplitude-propagation
  map and the radius-weighted direction measure nu_P as the minimal object for homogeneous queries; the conditional
  mid-layer p = 1 obstruction under H_cap; the correction that c_K >= c_* > 0 does not give a positive all-order floor,
  and the uniform-law bound e_best(C) >= a c_* alpha (C/d_*)^{-gamma_n} that does not need one.
- Audit outcome: E2, E4 (under its budget model), E7 correct; E1, E5, E8 narrowed; E6's mean-degree column corrected
  (truncated FFT) and its "b_1 ~ 1/t^2" / "mean ~1.3 t" readings replaced by the asymptotics 1 - b_0 ~ 9 pi^2/(2 t^2),
  b_1 = Theta(t^{-3}); my "b_0 ~ 0.7-0.9 at the early cuts" was wrong (0.97).
- My checks: gamma_3 from the raw moments of sqrt2 Z_+; a_n = 1 - 5/(8n) from Var rho_n^2 = 5/n; the cubic Hermite
  coefficient 1/sqrt(3 pi); the corrected mean degrees 17.24 and 42.27 from results/kernel_spectrum.json; the
  1 - b_0 asymptotics from the expansion of kappa_1 near 1 (slow convergence: 0.027 at t = 31 against 0.046
  asymptotic). Not rechecked: the remainder control in (42) and the H_cap scaling argument (55) beyond its counting.

## Round 4 (the radius-corrected closure as a full recursion; launched 09:33:30Z, exit 09:45:38Z; model line gpt-6-astra)
- Prompt and FORMAL (at E11) hashed in statement_hashes.txt before launch. Read by me ~09:57Z; applied as FORMAL E12.
- New from astra: the recursion's own one-step defects (not oracle single cuts) in the telescoping sum; one-step order
  n^-2 under cap/remainder/local-discrepancy hypotheses; Theta(alpha/n) under Gram bounds, hence constant gain over MC
  and a growing disadvantage to the multilevel sampler; tr M_3 = M_1; the trace sector's 3/(n+2) share; mixed cubic
  cumulants at the first layer; the transferred-ladder exponent; amplitude tolerances; sinc quadrature J = O(log^2).
- My checks: R7 (tr M_3 = M_1) from the definition; the 3/(n+2) trace share; R11's numbers (A = 20, L = 32, eps =
  1e-4 give 3.95e-4 and 6.99e-5). Not rechecked: R8's Hermite coefficient and the sinc-quadrature constants.

## GPT-6 fresh-session review (review/run_review.sh; 09:29:19Z-09:39:59Z; model line gpt-6-astra; high effort)
- Verdict major revision; 17 findings (11 major). All accepted in substance; how each was applied is in section 9 of
  the report.
