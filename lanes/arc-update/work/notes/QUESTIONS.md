# arc-update: questions and hypotheses, each with how it gets checked (2 November 2026, 04:56Z)

Q1. Does ARC's final step have the form est_i = int relu(w_i . h) dQ(h) with Q independent of w_i (needed for the
    last-layer bottleneck A5 at K >= 3)? Check: read src/mlp_kprop/kprop_harmonic.py (last-layer mean); numerical
    identity: compare ARC's output with a direct Gram-Charlier quadrature at n = 8, one layer (CHECK-1).
Q2. Is the cumulant hierarchy's per-order efficiency loss ~L at fixed L (H_LAD)? Check: T-LAD, ARC variants
    k1, k2, k2a, k3 (basic), k3f, k3fa, k4f along L = n/8 (n = 32, 64, 128, 256), errors vs MC truth, ARC's flop
    counter; gain over MC and RQMC at own cost; ratio G_{K+1}/G_K.
Q3. Does the gain of each order decay with n at L = n/8 (C-LAD for ARC's variants)? Check: same runs, slope of log gain
    in log n per variant.
Q4. Does the cloud's order-3 structure factorise (B2)? Check: T-RANK, flattening Gram of kappa_3(h_l) by U-statistic on
    true samples at 256 x 32 (nets 200-204), participation ratio and top-k captured energy, l = 1..31.
Q5. Do later layers cancel earlier defects (NC)? Check: T-ATTR, per-net decomposition est - Y = a_l + b_l for ARC's
    K = 2 (and the exact Gaussian closure) at cuts l = 2, 4, 8, 16, 24, 28, 31 on nets 200-204: |b_l|^2, |a_l|^2 and
    the cosine between a_l and b_l.
Q6. How large is the single-cut Gaussian defect profile Gamma*_2(l) (moment-matched Gaussian at layer l, exact future)?
    Check: same runs (it is b_l for the oracle Gaussian); compare with ARC's total error.
Q7. Does the exact Gaussian closure (exact bivariate ReLU moments) beat RQMC at 256 x 32? Check: bits-bounds
    lib/closure.py on nets 200-204, nMSE and gain at matrix-product and implementation cost.
Q8. Where do the samplers stand at 256 x 32 on the same nets? Check: RQMC (scrambled Sobol, radius exact), plain MC
    (analytic), the two-level multilevel sampler (unrestricted lib/mlmc.py), and the arc-noisy Kerdock numbers
    (sigma = 0.001, cited, not rerun).
Q9. Is the per-neuron probe structure (A4) visible: are the next layer's per-neuron 3rd/4th cumulants spread over many
    directions (random probes of a high-rank tensor) rather than concentrated on a few modes? Check: T-RANK plus the
    per-neuron standardized cumulants gamma_3, gamma_4 of z_{l+1} and their prediction from top-k compressions.
Q10. Truth precision: nets 200-204 have 2^26-path noiseless truths (floor 1.5e-8 nMSE); fresh nets at n <= 128 get
    2^24-path truths here (floor 6e-8); errors below 10x the floor are not scored.
Q11. Kelvin's hypothesis (S1-S4 in FORMAL section 8): S2 waits for the bit-accounting phase-2 test under certified
    compression. Main (05:00Z): a "not scrambled" claim counts only if the same tests light up on the scrambled
    controls (chaotic tanh, Feistel, linear; work/bit-accounting S11, deferred to phase 2). Until the controls are
    through the pipeline, S2 is reported as "the tests found low degree", not "no scrambling".
Q11b. Positive control for my own T-RANK test: a synthetic cloud with a planted rank-r third cumulant (Gaussian plus
    r skewed independent components along random directions, n = 256) must give a flattening participation ratio
    near r; a Gaussian cloud must give a U-statistic consistent with zero. Run with the eval batch.
Q12. Certified parameters (part B): the certified per-layer bit curves at 256 x 32 (bit-accounting-arc, GPU) will land in
    work/bit-accounting-arc/results/certified_curves.json (first milestone ARC seed 4000, layers 0/16/31, both
    classes, ~06:30-07:00Z per main); uncertified cells are marked there.
