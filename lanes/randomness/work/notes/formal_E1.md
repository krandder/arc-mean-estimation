
## E1. Additions after reading gpt-6-astra round 1 (~14:10Z; coprover/PROVENANCE.md)
E1.1 (T4, cleaner form; PROVEN [A]). With k(t) = E_W <g(u), g(v)> = sum_r b_r t^r (b_r >= 0, sum b_r = 1, by a Hermite
expansion after the first layer) and M_r(Q) = int u^{(x)r} dQ, the ensemble risk of any rule is
m_n^2 sum_r b_r ||M_r(Q) - M_r(sigma)||_F^2; for even r = 2s and positive weights the off-diagonal terms
(u_i . u_j)^{2s} are nonnegative, so risk >= (m_n^2 / (2N)) sum_{s: tau_2s <= 1/(2N)} b_2s, tau_2s = E (U . V)^{2s} =
(2s - 1)!! / (n (n + 2) ... (n + 2s - 2)). At n = 256: tau_4 = 4.5e-5, tau_6 = 8.7e-7, tau_8 = 2.3e-8, so at N = 2^16
(1/(2N) = 7.6e-6) every power from degree 6 on is paid in full; my Gegenbauer version (T4) gives the same thresholds.
E1.2 (T7, now PROVEN [A], annealed, exact). E Per_gamma{z_{l,i} > 0} = (1 - 2^-n)^{l-1} / sqrt(2 pi), dead-region
interfaces included (the literal zero set of a deep pre-activation contains open dead cones; the gate-set perimeter is
the right object); summed over the net ~ n L / sqrt(2 pi). P(gate history through l changes) ~
(sqrt 2 n / pi)(sum_{j<l} beta_n^j) sqrt(delta), beta_n = 1 - (n + 1) 2^-n (fixed n, l; delta to 0).
E1.3 (T8, now PROVEN [A] for a fixed map with transversal facets). F(delta) := V NS(delta) = D delta -
(2 J_kink / (3 sqrt pi)) delta^{3/2} + o(delta^{3/2}), D = sum_k k H_k, J_kink = sum over facets of the Gaussian
surface integral of ||[J_f]||_F^2; Hermite tail sum_{k>t} H_k = O(J_kink t^{-3/2}). Annealed: E sum_k k H_k = n
exactly, so NS_ann(delta) <= (n / E V) delta with equality as delta goes to 0. Unused gates carry no jump: gate
counts do not price output effects.
E1.4 (correction to how T6 is used; [A]). Gaussian Hermite degree and spherical harmonic degree differ: the homogeneous
extension of a degree-d harmonic occupies Hermite degrees d, d + 2, ..., so sum_{d>t} E_d <= (m_n^2 / n) T_H(t) one way
only. T6 is stated with spherical pairs (exact Funk-Hecke) and stands; the Gaussian ("gauss") NS curves of noise.py
are Hermite statements and bound spherical tails only from above.
E1.5 (new [A]). (a) Bounded independence fails in the worst case: a 127-wise independent law on R^256 (Gaussian
magnitudes, sign parity constraint on 128 coordinates) and a width-256 positively homogeneous ReLU net whose mean it
gets wrong by a factor 2 (PROVEN). (b) Smoothness tail: sum_d d(d + n - 2) a_d = m_n^2 (n - 1), so
sum_{d>t} a_d <= m_n^2 (n - 1) / ((t + 1)(t + n - 1)) (PROVEN; informative only for t of order 30 or more at n = 256).
(c) Kerdock aliasing for even d: B_d = 1/(Kn) + ((n - 1)/(Kn)) P_d(0) + ((K - 1)/K) P_d(n^{-1/2}), K = n/2 + 1
(B_2 = B_4 = 0). (d) In the infinite-width kernel model, degrees 1-2 carry O(1/L) of the angular variance and the
even tail half of it (so the ~4x ceiling is a mean-field statement); finite width is different (ladder: degrees <= 2
carry 0.4-0.75). (e) CONJECTURE [A]: Kerdock blocks give N E err^2 / V in [0.33, 0.50] on fresh 256 x 32 nets.
