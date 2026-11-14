# preint: assumptions and open questions, each with its check (leaf pool-ttdzrk.17.1, 2 Nov 2026)

Estimand: E_x f(x) in R^n, f = bias-free He-ReLU net (W_l iid N(0, 2/n), h_l = relu(W_l h_{l-1}), output h_L),
x ~ N(0, I_d), d = n. Score nMSE = |est - E f|^2 / tr Var f (MC with N paths: 1/N). Cost in forward passes
(1 pass = 2 n^2 L FLOPs, au.pass_flops / unrestricted nets.pass_flops); nd-exact's mv = pass / L at 8 x 256.

## Assumptions (A) and how each is checked

A1. All compared estimators are unbiased, so MSE = variance, estimable from R independent replicates without a truth.
    Check: every scored run also reports |mean of replicates - truth|^2 against the existing truths (arc-update
    runs/truth_n*_L*_s*.npz at 2^24 paths; arc-noisy truth_256_32_s0_seed20?.npz at 2^26; nd-exact runs/truth_s*.json)
    and a z-score; a bias flag if |z| > 4. MSE by replicate variance is the primary score below the truth's floor.
A2. Exact line integration costs one matvec per vertex per layer (vertices = breakpoints so far on the line),
    so a line costs mean_l B_{l-1} passes. Check: the implementation counts every matvec, sign test, interpolation
    and t/normal CDF evaluation; cost in passes is the counted FLOPs over 2 n^2 L.
A3. Positive homogeneity lets the radius be integrated exactly together with the line (2-D half-plane for the
    price of one line; weight (1+s^2)^{-(d+1)/2}, a Student-t law). Check: unit test against brute-force 2-D
    quadrature on small nets, and the full estimator against closed form at depth 1 (E relu(w.x) = |w|/sqrt(2 pi)).
A4. The RQMC exponents quoted to us ("1.03-1.27") are slopes over a finite window, not asymptotes.
    Check (done, arc-update runs/rqmc_*.json): N * nMSE_RQMC falls from 0.29 to 0.19 (n=32), 0.39 to 0.35 (n=64),
    0.58 to 0.40 (n=128), 0.80 to 0.48 (n=256) over N = 2^8..2^14/16 and is flat over the last two budgets at
    n = 32, 64 and 256 (local exponents 0.99-1.03). So at these widths RQMC looks like c(n)/N with c rising with
    width, after the low-order part is integrated: asymptote 1, not 1 + 2/d_eff. At 8 x 256 (input dim 8, nd-exact
    runs/baselines_s*.json) C * nMSE keeps falling over 4 decades (RQMC 0.4-1.2 -> 0.01-0.1): exponent above 1 there.
A5. The bottleneck at large width is effective dimension, not smoothness: pre-integrating one direction removes
    only the variance carried by Hermite terms that involve it (about D/d of it, D = mean degree 16-30 at the input of
    ARC nets per the relevance lane), at a cost of hundreds of passes per line. Check: measure Var(E[f | y]) / Var f
    and the cost per line on the ladder; fit the exponent.

## Open questions (Q), each with how it gets checked

Q1. How many pieces does a line (or the half-plane) cross, as a function of n and L? Prediction from Rice's formula
    in the wide-net Gaussian-process limit: each pre-activation along a great circle is a GP whose correlation is
    1 - theta^2/2 + O(theta^3) at every depth (critical init keeps k'(1) = 1), so about 1/pi zero crossings per radian
    per neuron; a half great circle (angle pi) then has about n L breakpoints, and the Gaussian-weighted window
    about (2/pi) T n L / sqrt(d) for |t| <= T. Check: count on ARC-family nets n = 8..256, L = 1..64 and 8 x 256.
Q2. Smoothness after pre-integration: is g(y) = int f(y + t u) phi(t) dt in C^{1,1} (W^{2,inf}) for every
    direction u that is not parallel to a facet, with Hessian jumps on the projected codimension-2 skeleton?
    In the random-kink (Poisson hyperplane) model the spectrum of f is |xi|^{-(d+3)} (H^{3/2-}), and of g in d-1
    dims also |xi|^{-(d+3)} (H^{2-}): MSE exponents 1 + 3/d (RQMC on f, asymptotic) vs 1 + 4/(d-1) (on g); k-dim
    pre-integration 1 + (k+3)/(d-k). Check: co-prover round 1 (proof or counterexample), then the measured slopes on
    nets with small d (n = 4-8, shallow) where the asymptotic regime is reachable.
Q3. Does PI-RQMC's slope beat RQMC's at 8 x 256 and on small nets, and does any gain hold along the ladder?
    Check: registered slope fits over fixed budget windows, replicate-variance MSE, per net.
Q4. Average-case limit as width grows: for GP-like integrands with the deep ReLU kernel on S^{d-1}, can any method
    using N point values (or N line integrals) beat MSE ~ c/N by more than polylog factors uniformly in d?
    Heuristic: N nodes resolve harmonic degree about log N / log d, and the kernel's energy beyond degree k decays
    only polynomially in k. Check: co-prover (proof sketch or counterexample), compared with the plateau c(n) of A4.
Q5. Which direction u: random (fresh per replicate), or net-chosen (top right singular vector of the
    cloud-averaged Jacobian, or top eigenvector of E J^T J)? Check: both on dev nets; the pilot that picks u is charged.
Q6. Does exact integration combine with the exact linear tail (RQMCJ, 8 x 256 only) and with the multilevel
    shared-trajectory sampler? Check: PI-RQMCJ (lines through layers 1..c, then J_c) on the six nets; multilevel only
    if a level difference is itself line-integrable at a lower cost (a design check before any build).
Q7. 2-D pre-integration beyond line + radius (a plane through two directions plus the radius, 3-D exact): affordable?
    Check: count regions in a random 2-plane on dev nets; cost about B^2 vertices if regions are isotropic.

## Not assumed
- That pre-integration helps: the starting idea is tested and replaced if something better appears.
- That d_eff fits 1 + 2/d_eff: A4 says the ladder plateau is c(n)/N; the fit is rechecked on our own runs.
