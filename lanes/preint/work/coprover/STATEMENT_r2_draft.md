# Co-prover round 2 (lane preint): audit and lemma exchange (DRAFT, finalised after reading round 1)

Read FORMAL.md in this directory (v1 frozen 14:00:39Z, written before your round-1 answer; additions E1.. after it)
and your round-1 answer coprover/astra_r1_answer.md. Then:

A. Audit, item by item, every PROVEN claim in FORMAL v1 and E1: F1 (line + radius identity), F2 (exact algorithm), F3(a)
   (exactly one sign change per first-layer unit on the half circle), F3(b) (Kac-Rice conditional on the past:
   E[#sign changes | past] = Lambda / pi with Lambda the length of the normalised curve), F4 (C^{1,1} without
   monotonicity; the Lipschitz constant; the fold argument), F7(a)-(e) (zonal weight-averaged kernel; MMD identity;
   expansion; rank lemma (tr A)^2 <= rank(A) ||A||_F^2; pi^{(j)} >= 0, even support, pi_0 = 1/N_j; the line version with
   rank <= j + 1; the theorem and its min over s), E1 (scope of the IBC citations; the identifiability caveat).
   For each: correct / correct with a stated condition / wrong (with a counterexample or the fix).
B. Reconcile with your round 1: where we differ (e.g. your positive-weight restriction vs my real weights), which is
   right and why.
C. Strengthen if you can: (1) a per-net version of F7 for rotation-randomised rules, and what per-net quantity it needs;
   (2) the hypothesis H_even for L = alpha n: is the even-degree energy above degree 2j bounded below uniformly in n
   (NNGP proxy numbers in results/kernel_bound.json; actual nets' low-degree shares in runs/deg_*.json when present);
   (3) whether the line version can be sharpened using the narrow line weight (width 1/sqrt(d)).
D. Read the scored results (results/scorecard.md, results/posthoc_matched.json) and say whether my reading in
   preint.md (draft) follows from them.
