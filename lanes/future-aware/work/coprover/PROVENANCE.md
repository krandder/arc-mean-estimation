# Co-prover provenance (future-aware lane)

Co-prover: gpt-6-astra through codex-any (read-only sandbox, xhigh effort). The "model:" line of every raw log is
checked; no fallback model is accepted.

## Round 1 (independent)
- Statement: STATEMENT_r1.md and prompt_r1.md, hashed 10:36:36Z (statement_hashes.txt) and launched 10:36:38Z.
- Raw log: astra_r1.raw, "model: gpt-6-astra" (line 5), exit 0 at 10:53:27Z. Answer extracted to astra_r1_answer.md.
- My FORMAL v1 was frozen at 10:39:09Z and its header-time correction rehashed at 10:39:14Z (notes/formal_hashes.txt),
  before the answer existed; I read the answer at ~10:58Z.
- What round 1 contributed (labels are astra's): conditional pricing (PROVEN; same as my F-2); the exact eigenvalues of
  the annealed operator on a rotation-invariant reference law (PROVEN; corrects my HEURISTIC "beta_j ~ b_j" in F-3,
  and adds that on the actual anisotropic cloud spherical harmonics need not be eigenfunctions); the k-sketch Mehler
  expansion (PROVEN; same as my section 3) and a sharp risk formula for correcting a FIXED past-measurable defect,
  inf E||Z - a(S)||^2 = sum_d b_d (||M_d||^2 - ||P^{tensor d} M_d||^2), with the flattening bound
  ||P^{tensor d} T||^2 / ||T||^2 <= min(1, k / r_inf(T)) (stable rank, not participation ratio) and counterexamples
  to "(k/n)^d"; future-chosen subspaces: Haar overlap does NOT bound removed price (rank-one future counterexample),
  and for an independently Haar-oriented linear future the removed fraction is the future's top-k spectral share
  (PROVEN under that model; my H-overlap rule, which I had labelled HEURISTIC); an exact one-layer counterexample showing
  that no unconditional annealed-price extension holds for adaptive defects (any finite list of moments can be
  preserved with zero realised error); transcript lower bounds are sharp but do not apply to explicit-weight algorithms;
  the hybrid's bias-variance identity and equal-cost criterion; the optimal exactly-integrable control as an L^2
  projection, with the chaos formula; the variance-weighted mean-degree identity n / E V (PROVEN) and a counterexample
  to inferring low-degree variance from the mean degree; strongest negative (PROVEN under a fixed-defect, sketch-only
  additive-correction model) and strongest positive (CONJECTURE: a future-built control with a cheaply exact mean).

## Round 2 (independent, new questions)
- Statement: STATEMENT_r2.md (hashed 11:28:32Z with prompt_r2.md, statement_hashes.txt); launched 11:28:34Z.
- Raw log: astra_r2.raw, "model: gpt-6-astra", exit 0 at 11:50:14Z. Answer extracted to astra_r2_answer.md.
- My FORMAL v2 (E1-E6) was frozen at 11:28:22Z before launch; v3 additions (E7-E8, written 11:34-11:39Z) were frozen at
  11:50:27Z, after the round finished and before I read its answer (~11:51Z).
- Contributions (labels astra's): a precise projected-hierarchy construction and a dedicated cost bound
  F_K = O(n^3 + n^2 k + D_K [n^2 k^{K-1} + n k^K + K k^{K+1}]) per layer under contractible diagrams (HEURISTIC that
  ARC's 'simple' diagrams all contract so); the exponent log q / log k and the exact criteria sup_K C_K e_K < inf and
  e_K / e_{K+1} > C_{K+1} / C_K (PROVEN under uniform laws); q_{3,proj} = 1 / (1 - R + R / q_3): R is not the retained
  fraction of the error FACTOR (PROVEN); under k = cn, C_3 = Theta(n^2), C_4 = Theta(n^3) passes, so order 4 helps only
  if its error ratio exceeds Theta(n); in the homogeneous independent-gate model the nonlinear Jacobian energy at
  t = beta n has participation ratio Theta(n) (PROVEN under the model; limit fraction (1 - p^2)/(2 - p^2) = 3/7 at
  p = 1/2), and capturing a fixed fraction of it needs k = Omega(n) (PROVEN for that energy; the link to closure error
  is HEURISTIC); a Bakhvalov-type worst-case bound c M^{-1/k} for deterministic rules on piecewise-linear 1-Lipschitz
  integrands (PROVEN, worst case only); moment-matched laws can differ on piecewise-linear expectations (PROVEN);
  scrambled-net variance in gain coefficients and the exact condition under which control and RQMC gains multiply
  (PROVEN); a counterexample showing a full-rank nonlinear spectrum does not imply integration hardness; strongest
  negative PROVEN UNDER (k_n >= cn, bounded geometric error ratio, geometric cost base k_n): gamma_n -> 0; strongest
  positive CONJECTURE: a future-weighted order-3/4 correction at O(n^3) per layer with e_n = o(1/n).

## Round 3 (audit of FORMAL E9-E12 and the files)
- Prompt prompt_r3.md (hashed in statement_hashes.txt); launched 13:00:37Z after FORMAL v4 (E9-E12) was frozen at
  13:00:22Z; raw log astra_r3.raw, "model: gpt-6-astra", exit 0 at 13:15:46Z; answer astra_r3_answer.md, read ~13:16Z.
- Verdict (astra's): E10's projection identity survives (series-free form primary); E11 overstated; E12's random-sign
  model wrong as written (basis-dependent Hadamard tensor; counterexample; futnl uses true samples), with a correct
  conditional-covariance replacement; E9 omitted hypotheses (3/7 limit, nested scrambling, "optimistic" cost model is a
  hypothesis); E1 over-accepted section 3; E4 conflates spectra; E7's cubic cost floor unsupported as a universal
  claim; E8 mixed two retention metrics; E6's gain relation; share-law fit details (379 cells, slope 1.19); b2's
  conditional target. All accepted; applied as FORMAL E13 and in the report.

## Round 4 (20:06-20:24Z)
Statement coprover/STATEMENT_r4.md; my view FORMAL E16 frozen 20:05:58Z (v9 hash) before launch; model line gpt-6-astra checked; raw coprover/astra_r4.raw, answer astra_r4_answer.md; accepted items FORMAL E17.
