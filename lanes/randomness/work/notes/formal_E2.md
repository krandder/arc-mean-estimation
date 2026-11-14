
## E2. Audit and additions after gpt-6-astra round 2 (read ~14:50Z; coprover/astra_r2_answer.md)
E2.1 Audit of v1 (accepted). T1-T3, T6 (identity and inequalities; "pins" overstated: the lower bound can be zero) and
T9 (identity) correct. T4 correct per degree; the tail form must sum every qualifying degree; for antipodal sets the
stronger ceiling A/(2 tail) needs M |min P_d| = o(1), otherwise A/tail; power and Gegenbauer coefficients are not
interchangeable (t^r = sum_d c_{r,d} P_d with c_{r,d} >= 0). T5 WRONG as a fixed-n, eps -> 0 statement: the tail in its
lower bound depends on m and vanishes as m grows; it holds at polynomial budgets (E2.3) and log2 m is a support-index
length, not runtime randomness. T7 first layer correct; later zero sets contain open dead regions (round 1); the
small-noise asymptotic does not by itself give near-one disagreement (the measurement does). T8 constants corrected:
(1/2) E||J(X) - J(Y)||_F^2 ~ (J_kink / sqrt pi) sqrt(delta) and sum_{k>K} H_k ~ (J_kink / (3 pi)) K^{-3/2}; my 0.8 nL and
the crossover K ~ L^2 remain HEURISTIC. T10 wrong as exact redundancy (|z_i|, relu(z_i), z_i |z_i|, |h_1|^2 have higher
harmonics); the measured near-redundancy stands as HEURISTIC. T11 needs an explicit capacity hypothesis; "known PRGs
cover depth-1 structure only" and "none bears on the average-case problem" are too strong (a valid worst-case PRG with
the right normalisation would also give an average-case bound). The spectral proxies in ladder_table.py carry small
systematic aliasing errors (e.g. |e2_hat - e2| <= 3/(n + 1) x even>=4 share), negligible against replicate noise.
E2.2 (exponents at fixed width; PROVEN [A]). For positive weight-independent rules, sum_{r > D, r even} b_r ~ C D^{-3/2}
(kink tail of the downstream map of first-layer pre-activations) and tau_d ~ C_n d^{-(n-1)/2} give
risk >= c N^{-1 - 3/(n-1)} for large N, so p <= 1 + 3/(n - 1) (1.0118 at n = 256); stratifying the sphere into N
equal cells attains N^{-1 - 2/(n-1)} (1.0078 at n = 256). So "exponent exactly 1" is false at fixed n, but the black-box
exponent lies in [1 + 2/(n-1), 1 + 3/(n-1)]: indistinguishable from 1 at n = 256. A fitted slope over 2^8..2^18 is not
constrained by these asymptotic bounds. Unions of R rotated copies of a FIXED design have exponent exactly 1.
Thresholds at n = 256 (power form): even degrees >= 4 counted for N <= 11,008, >= 6 for N <= 572,416.
E2.3 (the finite-width mechanism; PROVEN [A]). For unit inputs at inner product t, with norms r_j, r'_j and cosine c_j
of the layer-j states: 1 - k_j(t) = [1 - B_j(t)] + T_j(t), B_j = E[r_j r'_j] (norm mismatch), T_j = B_j - k_j
(direction mismatch). Bounds: 0 <= 1 - a_n(c) <= (2/n)(1 - c) per layer for the norm factor; T_j <= 9 pi^2/(2 j^2);
B_j - B_{j+1} <= (2/n) T_j. Hence V_L <= n - m_n^2 + (m_n^2/n)(2 + 3 sqrt2 pi) + 9 pi^2 m_n^2/(2 L^2) = O(1 + n/L^2)
uniformly, and as n, L -> infinity with L/sqrt n -> infinity, n (1 - k_{n,L}(t)) -> S(t) = sum_{j>=0} eta(K_j(t)),
eta(c) = 3/2 - E[Z_+^2 Z'_+^2], K_j = kappa^{(j)}; E V -> S(0) + 1/2 with S(0) = 10.6505 (numerical evaluation of the
proven series). The finite-width variance is made by persistent differences in ACTIVATION NORMS accumulated over the
first layers (each O(1/n), summing to O(1)); taking width to infinity first removes exactly this term, which is why
the mean-field picture (degrees 1-2 share O(1/L)) does not describe finite width.
E2.4 (limits of the spectrum and of design gains; PROVEN formulas [A], values numerical). lambda_d -> A_d (the power
coefficients of A(t) = S(0) - S(t)); limiting shares: degree 1 0.2906, degree 2 0.2080, odd 0.5704, even 0.4296,
even >= 4 0.2215, even >= 6 0.1661; S(-1) = S(0) + 3/2 (parity). Gains over plain MC tend to (S(0) + 1/2)/(S(0) - A_1 -
A_2) = 2.09 (simplex), (S(0) + 1/2)/(S(0) - 3/2 - 2 A_2) = 2.36 (cross-polytope), (S(0) + 1/2)/(S(0) - 3/2 - 2 A_2 - 2 A_4)
= 3.15 (Kerdock, along dimensions with complete real MUBs). No positive oblivious rule has a gain diverging with n at
budgets N <= C n^p: liminf N R_N >= sum_{even r >= d} A_r > 0 for even d > 2p: Theta(1/N) in the joint wide/deep limit.
Measured at 256 x 32 (medians, 5 nets): odd 0.56, even 0.43, degrees <= 2 0.47, even >= 4 0.22, even >= 6 0.17;
simplex 1.93, cross-polytope 2.39, Kerdock 3.04. The theory accounts for the measured spectrum.
E2.5 (degree 1 = mean Jacobian; PROVEN [A]). E_1(W) = (m_n^2/n) ||E_X J_f(X)||_F^2.
E2.6 (the noise slope; PROVEN [A]). NS'_ann(0) = n / E V -> n/11.15 along L = alpha n, i.e. ~0.72 L at L = n/8: my
"1 + L/2" description of the per-layer slope is not the asymptotic law. CONJECTURE [A]: at 512 x 64, degrees <= 2 share
0.45-0.60, odd 0.55-0.59, simplex gain 1.8-2.6, cross-polytope 2.0-2.8, ensemble noise slope 35-45.
E2.7 (white-box; [A]). Signed permutations of a Kerdock set keep its flat coordinate pattern: for f = relu, the aligned
antipodal MUB rule estimates 1/2 where the Gaussian mean is 1/sqrt(2 pi) (PROVEN): the bias comes from the flat
majority of the design, not from a few axis points. W-dependent frames escape the oblivious bound; scrambling with
jointly uniform points keeps them unbiased; for fixed n they give o(1/N) under standard scrambling hypotheses with no
dimension-uniform rate. CONJECTURE: polar or SVD alignment alone will not change the exponent at L = alpha n.
E2.8 (open question, [A]). Whether a cheap weight-dependent construction can predict and integrate the persistent
scalar norm fluctuations well enough that the residual angular variance tends to zero, with all costs counted.
Cancelling degrees 1-2 explains a constant gain; exploiting the full norm profile is the plausible route past the
proven oblivious ceiling. [C] note: this is the multilevel prefix-norm idea; with the norm variance made at rate ~1/j^2
per layer j, a prefix of r layers leaves ~1/r of it (consistent with the measured best-prefix residual ~0.9 at r = 1),
and dyadic levels give a gain ~ L / (2 c log^2 L), below 1 at L = 32 and above it only for L of order several hundred
(HEURISTIC).
