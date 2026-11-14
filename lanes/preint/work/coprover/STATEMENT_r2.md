# Co-prover round 2 (lane preint, 2 November 2026): audit and lemma exchange

You may now read this lane's files: FORMAL.md (v1 frozen 14:00:39Z, written before your round-1 answer; E1 written
14:14Z; E2 written after reading your answer), your round-1 answer coprover/astra_r1_answer.md, lib/line.py,
lib/est.py, results/pieces.md, results/kernel_bound.json, scratch/kernel_bound.py, results/posthoc_matched.json,
runs/deg_*.json and runs/nongauss_*.json when present (finite-width degree energies and non-Gaussianity, being
computed), PREREG.md. Read-only sandbox.

A. Audit each item marked PROVEN in FORMAL v1 (F1-F4, F7(a)-(f)), E1 and E2: correct / correct with a stated
   condition / wrong (counterexample or fix). Priorities:
   1. F7(d)-(e): the rank lemma at every even degree 2j with SIGNED weights: A = sum_i v_i phi(x_i) phi(x_i)^T with
      phi the degree-j harmonic feature map, (tr A)^2 <= rank(A) ||A||_F^2, hence
      sum_{k>=1} pi^{(j)}_k Q_k >= s^2 (1/N - 1/N_j) with pi^{(j)} the Gegenbauer coefficients of P_j^2. Your (17) needed
      positive weights; is the rank route right, and does it give your (17)-type statement for signed weights? The
      line version: rank <= (j + 1) per line + radius functional (restriction of Harm_j to a great circle). Check the
      LP combination over j and the min over s.
   2. E1: the scope of the IBC citations (orthogonally invariant measures; linear optimal algorithms; varying
      cardinality) and the identifiability caveat (about n L generic evaluations identify W; so no information lower
      bound for nonlinear algorithms survives beyond that under the true prior). Is the identifiability count right
      (symmetries; does each evaluation really give n independent equations; does the last ReLU destroy information)?
   3. E2(c) vs F3(b): your exact law n q_n^{l-1} and my conditional Kac-Rice statement E[#changes | past] =
      Lambda_{l-1}/pi: consistent? Does the expectation of the full-line cost hold for the homogeneous half circle
      used here (ends at +-u, curve not independent of nothing else)?
B. The finite-width H_even. Using runs/deg_*.json (per-net angular energies: degree 1, degree 2, odd, even >= 4, as
   fractions of the angular variance, n = 32..256 at L = n/8; computed by scratch/degrees.py, check its estimators),
   say what the rank lemma then gives per net for rotation-randomised rules, and whether the data support a c/N barrier
   with c bounded below along L = n/8 for N up to N(d, 2) = (d+2)(d-1)/2. If the data are not yet there, state the
   per-net theorem (what must be measured, and with what estimator) so that I can run it.
C. Your positive route (18) and the first-layer control: is there any candidate FAMILY of white-box surrogates
   (indexed by cost q) for which a width-uniform residual law trVar(f - p_q) <= C q^-b is plausible at L = n/8?
   Give the best concrete candidate and the cheapest falsification test, or say why none is plausible.
D. Anything in my reading of the measurements (results/pieces.md; results/posthoc_matched.json: at matched N a line
   is worth 0.9-2 points at n = 32-64 for 40-150 passes; at 8 x 256 a PIJ line is worth 0.6-17 points for 20-38
   passes; small nets n = 4, 6: 3-9 points, per-N slopes 1.5-2.05 vs 1.45-1.62) that does not follow.
Label every claim PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE / CHECKED-NUMERICALLY; give proofs for
PROVEN items at the level of every nontrivial step. Write everything to stdout.
