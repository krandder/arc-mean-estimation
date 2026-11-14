# Co-prover round 4: first-layer relevance scaling for the actual ReLU net

Setup. x ~ N(0, I_n). Weights W_1..W_L iid N(0, 2/n) entries, n x n, L = alpha n (alpha = 1/8 in experiments).
h_1 = relu(W_1 x); h_l = relu(W_l h_{l-1}); output h_L. Future map g(h) = h_L as a function of h_1 = h (layers 2..L).
J(h) = Dg(h) (n x n Jacobian; a.e. defined). Relevance R = E[J^T J], mean Jacobian Jbar = E[J], nonlinear relevance
R_nl = R - Jbar^T Jbar, all expectations over h ~ law of h_1 (weights fixed). S = Cov(h_1).
Whitened nonlinear relevance M = S^{1/2} R_nl S^{1/2}, eigenvalues lambda_1 >= ... >= lambda_n >= 0.
Participation ratio PR = (tr M)^2 / tr(M^2). Share s(k) = sum_{i<=k} lambda_i / tr M.

Measured (median over nets; n = 64, 128, 256, 512 with L = n/8): PR = 17.5, 33.3, 67, 127.5;
s(16) = 0.80, 0.59, 0.39, 0.25; s(n/4) = 0.80, 0.80, 0.81, 0.82.
Known (round 2, your proof): in the independent-gate mean-field model (gates of layer j replaced by independent
Bernoulli(p_j) independent of everything), PR = Theta_P(n).

Questions.
Q1. For the ACTUAL net (gates depend on the input and on each other), prove or refute: PR(M) = Theta(n) with
    probability -> 1 over the weights, for L = alpha n (or state the strongest version you can prove: e.g. PR >= c n
    for L fixed, or for L = o(n), or in expectation over weights of the traces).
Q2. Prove or refute that the normalized spectral measure of M / (tr M / n) converges (in the weights' randomness) to a
    deterministic limit as n -> inf with L/n = alpha, which would make s(k n) converge for fixed fraction k (explaining
    the constant s(n/4)). If only a conditional statement is provable, state the hypotheses exactly.
Q3. Lower bound route: is tr(M^2) <= C (tr M)^2 / n provable via tr(M^2) <= ||M||_op tr M and an operator-norm bound
    ||M||_op <= C' tr M / n? Which ingredient fails for the actual gates (e.g. the rank-one component from Jbar, the
    radial direction, gate correlations across layers)?
Give full proofs for PROVEN claims, explicit hypotheses for PROVEN UNDER, counterexamples where false, and say what is
open. Label each item PROVEN / PROVEN UNDER / OPEN / FALSE.
