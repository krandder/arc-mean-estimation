# future-aware lane: questions and assumptions, each with its check (written 11:03Z, 2 Nov 2026)

## Questions
Q1. At fixed k, does keeping the k FUTURE-relevant directions exact (whitened active subspace of g_l or of its
    nonlinear part, from VJPs) beat keeping k past-measurable directions (cloud PCA axes, a Haar frame)?
    Check: single-cut oracle (run_cut.py) and full stochastic recursion (run_rec.py), same k, same nets, CRN.
Q2. How does the k needed for a fixed improvement over the Gaussian / radius-corrected closure scale with width along
    L = n/8? (FORMAL F-W predicts k ~ c n.) Check: improvement factors at fixed k (4, 16) and at k = n/16, n/4, n/2
    over n = 64, 128, 256.
Q3. Is the non-Gaussian structure the future reads in those k directions captured by low-order cumulants?
    Check: order-3 Gram-Charlier (Edgeworth) oracle in the same k-dim span vs the exact k-dim marginal.
Q4. Does the radius correction (arc-update's lead) compose with the future-aware projection? Check: radg_ variants.
Q5. Can a DEDUCTIVE member reach the oracle family's accuracy at a cost, counting the backward pass, below the cost at
    which RQMC reaches the same error? Check: implement the cheapest deductive members (section 6 of FORMAL), measure
    error and cost at three widths; the window "beats RQMC by X up to precision Y" per width.
Q6. Hybrid (c): what fraction eta of Var(h_L) does a future-built control c(h_l) leave, and with what bias beta when its
    mean comes from a closure (exact only at l = 1)? Check: eta and beta per layer on true samples; RQMC on the residual
    for the best control (G_R measured, not assumed); the co-prover's equal-cost criterion.
Q7. Theory: which future-aware classes are exactly priceable (k-sketch: yes, FORMAL section 3 + astra r1), and what
    blocks a general extension (astra r1: adaptive defects with zero realised error and positive annealed price; any
    algorithm is a future-aware layer-wise estimator)? Check: co-prover rounds, frozen before reading.

## Assumptions
A1. The finite-sample bias of the stochastic recursions (2^18-2^19 particles, batch rank transport) is small next to the
    projection family's bias. Check: one net at 2^18 and 2^19; replicate noise reported.
A2. VJP-based relevance from 2^12 samples (E[J] from 64-128 samples) is accurate enough for the top-k subspaces.
    Check: subspace overlap of two independent estimates on a dev net; the nonlinear-part estimate is biased upward by
    E[J]'s noise (R_nl + (Jhat - Jbar)^T (Jhat - Jbar)), small at 64+ samples.
A3. Truths: 2^26 paths at 256 x 32 (nets 200-204, nMSE floor 1.5e-8), 2^24 at n = 64, 128 (nets 300-307, floor 6e-8);
    dev nets 100, 101 use sigma = 0.001 truths (shift ~3e-7). Values below 10x the floor are reported, not scored.
A4. The single-cut and recursion oracles keep the k-dim marginal as samples of the target (or of the model's own push):
    they are benchmarks for the family's bias, not methods; their cost is not a method's cost (Q5 handles costs).
A5. Cost units: one forward pass = 2 n^2 L flops; VJPs and matrix backward sweeps are charged as in FORMAL section 6.
