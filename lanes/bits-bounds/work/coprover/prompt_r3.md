You are gpt-6-astra, co-prover on the bits-bounds lane (round 3: the bottleneck). Read-only sandbox; do not modify files.
Read FORMAL.md (theory v2, merged with your rounds 1-2), coprover/astra_r2_answer.md (your round 2), and, for the
measured closure behaviour, /home/agent/workspaces/mats/outbox/hardness-mean-estimation-2026-10-29.md (search for
"Fitted slopes of log nMSE_K2": ARC's K = 2 closure along L = alpha n has nMSE falling like n^{-0.41}, n^{-0.56},
n^{-0.74} at alpha = 1/8, 1/4, 1/2, at a cost of about 1.5 n forward passes).

One target, labelled PROVEN / PROVEN UNDER X / HEURISTIC / CONJECTURE throughout:

Lower-bound the error of a SPECIFIED averaging method at L = alpha n, so that C4 holds for it. The method: the
single-Gaussian recursion (state = mean m_l and covariance S_l of a Gaussian surrogate of h_l; update = the exact mean
and covariance of relu(W_l y) for y ~ N(m_{l-1}, S_{l-1}), i.e. moment matching after the exact Gaussian ReLU push-forward;
input x ~ N(0, I) so the first step is exact; estimate = m_L). Questions:
(1) Using the telescoping defect identity (FORMAL Thm 4.2), the kernel-discrepancy form of a forward-only defect (Prop
    4.4) and, if useful, your Minkowski certificate, write the annealed squared error E_W |m_L - mu(W)|^2 as a sum of
    per-layer defect terms plus cross terms. Identify the leading per-layer defect at finite width n (the non-Gaussian
    part of relu of a Gaussian vector after one random layer, tested against the future kernel K_{n,L-l}): its order in
    n, and whether defects at different layers are correlated (coherent) or nearly orthogonal under the future average.
(2) Prove, or reduce to a single clean hypothesis, a lower bound E_W |m_L - mu(W)|^2 >= c(alpha) E_W V(W) n^{-a} with
    an explicit a <= 1 at L = alpha n. With the cost of the recursion (about n passes), a <= 1 makes it at best a
    constant-factor method against Monte Carlo at its own cost, consistent with C4. If you can only do a toy, do the
    cleanest toy that keeps the mechanism (for example, one random layer between Gaussian layers, or the infinite-width
    limit with the leading 1/n correction, or the exact replica chain), and say exactly what transfers.
(3) Say whether the same argument covers order-K cumulant truncations (cost n^{K+1} per layer), and what exponent a_K
    it would give, against astra's sufficient target C_closure(n, eps = n^{-q/2}) >= n^{max(1, q) - o(1)}.
(4) If a lower bound of this kind is false (the recursion's error could fall faster than 1/n at L = alpha n), give the
    mechanism and the cheapest numerical test that would show it.

Prefer a correct weaker statement to a strong wrong one. Write everything to stdout.
