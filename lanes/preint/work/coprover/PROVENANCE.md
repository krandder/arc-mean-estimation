# Co-prover provenance (gpt-6-astra via codex-any; the "model:" line is checked in every raw log)

## Round 1 (independent; launched 13:47:44Z from the lemma-free STATEMENT_r1.md, sha 430a7b37; exit 14:37:37Z)
- Model line: "model: gpt-6-astra" (raw log line 5). Read-only sandbox, xhigh effort. The prompt forbade reading
  work/preint beyond the statement.
- My FORMAL v1 was frozen at 14:00:39Z (sha c294b301, notes/formal_hashes.txt) before the answer existed; I glimpsed
  the last two lines of the streaming log at about 14:06Z while checking that it was alive (a one-line remark that its
  lower bound needs nodes independent of the net and positive weights at high degree) and read the answer at 14:38Z.
  E1 (14:14Z) was written after that glimpse; its content (Gaussian-measure IBC results, identifiability) is not in
  astra's answer.
- Found by both independently: F1, F4 (C^{1,1}, no monotonicity), the Poisson-model spectrum, one crossing per unit
  per half circle in the wide limit, the zonal weight-averaged kernel and MMD identity, the degree-2 rank obstruction.
- New from astra: the Hessian formula and sharpness example; H^{5/2-} for a fixed fan and the N^{-1-5/(d-2)}
  constructive rate; the exact finite-width crossing law n q_n^{l-1}; the finite-width coefficient bounds and the
  proxy-free 1/(8 pi^2 N) barrier for N <= n/4; the warning that the NNGP proxy fails in the joint limit; the
  surrogate route (18) and the first-layer control.
- New from me (not in astra's answer): the exact homogeneous algorithm and its tests; the rank lemma at every even
  degree with signed weights and the line version (rank <= j + 1); the LP form of the bound; E1 (IBC adaption results
  and the identifiability caveat); the measurements.
- My checks of astra's items: E2 (a), (c), (e) re-derived (marked [checked]); (b) and the Poisson Sobolev claims
  accepted at the level of the argument given, not re-derived in full.

## Round 2 (audit; launched 14:41:50Z from STATEMENT_r2.md, hash in statement_hashes.txt; exit 15:16:02Z)
- Model line "model: gpt-6-astra" (raw log line 5). It read FORMAL v1 + E1-E2, its round-1 answer, the code and the
  partial measurements (snapshots 14:50-14:54Z, while files were being rewritten).
- Confirmed: F1-F4 (with qualifications), the signed rank lemma, the line bound (refined for a common u), the LP, the
  degree-energy formulas, E2(c)'s exact crossing law, the positive route.
- Corrections accepted (FORMAL E5): F7(f) false as stated (3d - 2 node signed rule exact on degree 4) and repaired for the
  ensemble with power-series positivity; the per-net lump barrier is not a certificate; E1(b) needs separable output
  covariance; E1(c) identifiability withdrawn (narrow-cone counterexample); the kurtosis remark; the matched-N "line
  worth" is a variance ratio and the slopes used unmatched ranges.
- My checks: the 3d - 2 node example (its fourth-moment identity sum_i w_i (x_i . z)^4 = 3 |z|^2 z_1^2 / (d + 2)
  checked numerically below), the repaired ensemble bound's structure (not re-derived in full).
