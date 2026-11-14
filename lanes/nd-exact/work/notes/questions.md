# nd-exact: assumptions and open questions (2 November 2026, 03:40Z)

Target: E[a] for plain ReLU nets, width 8, depth 256, sigma = 0, W iid N(0, 2/8), no bias, x ~ N(0, I_8)
(nd.make_weights('plain', seed)); healthy evaluation seeds 203, 216, 217, 220, 221, 223; development seeds from the
healthy dev pool (103, 110, 111, 129, 133, 137, 141, 150, 153, 154, 160, 163). nMSE = |est - truth|^2 / tr Var(a).

## Assumptions (each with its check)
A1. Homogeneity: E[a] = E|x| * mean over S^7 of f(u), E|x| = sqrt(2) Gamma(4.5)/Gamma(4) exactly. Check: identity
    (proof two lines) and a numerical check with paired samples in tests/.
A2. Downstream linearity: if all live states at cut c share one downstream activation class, then
    E[a] = J_c E[h_c] exactly, J_c = the Jacobian of layers c+1..256 on that class. Check: census of downstream classes
    at cuts 8-64 (runs/census_*.json, field cuts) and the out-of-class contribution to E[a] (rest_contrib_nmse).
A3. Truths: RQMC (scrambled Sobol, many replicates) on the full net is accurate enough to score errors down to about
    1e-10 nMSE. Check: replicate spread; agreement of two independent truth constructions (full net vs J_c E[h_c]).
A4. Per-region exactness: on a polyhedral cone where the activation pattern of layers 1..c is constant, f_c is linear,
    so the region contributes A_r E[x 1_C]. Exact Gaussian moments are closed form only for special cells (boxes in
    the Gaussian coordinates, half-spaces, wedges); a general polyhedral cone in R^8 needs 7- and 8-dimensional orthant
    probabilities. Check: implementation cost per region measured in the estimator, not assumed.
A5. Cost unit: 1 mv = one 8x8 matrix-vector product with ReLU (128 FLOPs, flopscope conventions as nd.py). Every
    operation of a deterministic method is charged, including setup (tail Jacobian, tree bookkeeping, moment formulas).

## Open questions (each with how it gets checked)
Q1. How does the sphere's mass split over the regions of layers 1..d (d = 1-32)? How many regions carry 99%, 99.9%,
    99.99% of the probability and of the output mass |a|? Check: census by pattern hashing at 2^22 inputs per net,
    with Good-Turing unseen mass, Chao1 richness and rarefaction (scratch/census.py).
Q2. Does the region count saturate with depth (synchronisation) and at which depth? Check: same census, d = 8-32.
Q3. Is exact region-by-region integration affordable at the precision where it would beat RQMC? Check: coverage curve
    (error left by the top-R regions) against R times a measured per-region cost, compared with RQMC at equal cost.
Q4. Does a deterministic code of the inputs with fewer than 40 bits beat RQMC at equal cost, and what is its slope in
    bits per halving of error (sampling: 2 for MC)? Check: adaptive dyadic box code with exact integration on boxes where
    the net is linear, on dev nets first, then registered on the six evaluation nets.
Q5. Is any measured gain hidden setup cost or bias? Check: all setup charged; truncation bias measured against the
    full-depth truth; deterministic methods scored on fixed configurations chosen on dev nets.
