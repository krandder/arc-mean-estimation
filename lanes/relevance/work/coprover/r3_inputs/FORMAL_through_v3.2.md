# Relevance accounting: theory v1 (frozen 1 November 2026 before reading the co-prover's round-1 answer)

Objects and notation: DEFINITIONS.md (v1). Labels: PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL, HEURISTIC,
CONJECTURE. Provenance [C] (Claude) unless stated. "Dev" numbers come from dev nets (seeds >= 9100), never from the
evaluation nets of PREREG.

## 1. Forward-backward decoupling

Setting. F_l = the past (all weights W_k, k <= l, and the input or past-noise law), so mu_l, m = m_l, Sigma = Sigma_l are
F_l-measurable. Assume m != 0; e = m/|m|; B an F_l-measurable orthonormal basis of e^perp. Split the first future layer
W_{l+1} = g e^T + M B^T with g = W_{l+1} e (in R^n) and M = W_{l+1} B (n x (n-1)). Let G = sigma(g, W_{l+2..L}, Xi_l).

Theorem 1 (PROVEN). g and M are independent; M has iid N(0, 2/n) entries and is independent of (F_l, G). For any
orthogonal O of R^{n-1} put R_O = e e^T + B O B^T (a rotation about the mean direction). Conditionally on F_l and G, the
random function y -> F_l(m + y, Xi_l) has the same law as y -> F_l(m + R_O y, Xi_l).
Proof. F_l(m + y, .) depends on W_{l+1} only through W_{l+1}(m + y) = g(|m| + e.y) + M B^T y. Since e.(R_O y) = e.y and
B^T R_O y = O B^T y, W_{l+1}(m + R_O y) = g(|m| + e.y) + (M O) B^T y, and M O has the law of M, independent of
(F_l, G). Everything after layer l + 1 is G-measurable given the first layer's output. QED.

Corollary 1a (Haar relative orientation, PROVEN). For any functional Phi(cloud law, future map) and O Haar on O(n - 1)
independent of everything, E[Phi(mu_l, F) | F_l, G] = E[Phi(R_O mu_l, F) | F_l, G]: annealed over the angular part of
one future layer, every relevance quantity depends on the cloud only through its law modulo rotations about the mean
direction (for a Gaussian cloud: the radial variance, the radial-angular covariance norm and the angular spectrum).

Corollary 1b (no per-direction alignment, PROVEN). For the frozen Jacobian at the mean, J = J^m_{l->L}, the restriction
J B = K M (K = J^m_{l+1->L} D_{l+1}(m), G-measurable) is right-rotation invariant given G: its right singular frame on
e^perp is Haar and independent of its singular values. Hence for every F_l-measurable unit u in e^perp,
E[|J u|^2 | F_l, G] = tr(B^T J^T J B)/(n - 1): all past-measurable angular directions, including every principal axis of
the cloud and every backward-Lyapunov (Gram-Schmidt) vector of the past, receive the same expected backward
amplification. The brief's per-direction product "forward variance along CLV k (~1/k) x backward amplification
exp(-2c(k + 1/4)t/n)" does not describe the relevance spectrum: covariant Lyapunov vectors k >= 2 at layer l are
future-measurable (Ginelli's backward iteration selects, inside the span of the past's top-k Gram-Schmidt vectors, the
combination that the future contracts at rate gamma_k), whereas the cloud's axes are past-measurable.

Corollary 1c (degree-1 relevance spectrum). For a cloud small enough that the cloud-averaged Jacobian is close to a
Jacobian whose angular part is Haar-oriented (Corollary 1b), the angular block of R_1 = Sigma^{1/2} B^T B Sigma^{1/2}
has the spectrum of Lam^{1/2} O^T S O Lam^{1/2} (Lam: angular cloud eigenvalues, S: squared singular values of the
backward operator, O Haar). As n -> infinity with limiting spectral laws this is the free multiplicative convolution
mu_Lam (box-times) mu_S (PROVEN UNDER asymptotic freeness: Voiculescu's theorem for Haar-conjugated matrices with
converging spectra; the cloud-averaged Jacobian is not exactly of this form, so for it the statement is HEURISTIC).
- Consequence: the top eigenvalues of R_1 are about s_j(S) tr(Lam)/(n - 1) with relative fluctuations sqrt(2/PR(Lam)),
  so N_1 follows the backward spectrum, not the forward one. Dev check (n = 64-128): N_1 measured / free product /
  forward-only PCA count = 2 / 3 / 11 (eps 0.1) and 4 / 8 / 48 (eps 0.01) at 128 x 32, l = 16; 4 / 4 / 11 and
  8 / 12 / 50 in the stationary regime at n = 64, t = 4 (NUMERICAL, dev).
- Backward model (HEURISTIC): S = squared singular values of a product of t Gaussian blocks n -> n/2 -> ... -> n/2
  (half the units active), the half-width Fuss-Catalan law of the kstar-frames lane. For t >> 1 its log-spectrum is
  close to linear, log s_j ~ -2(t + 1) j/n, so N_S(eps) ~ (n/(2(t + 1))) ln(1/eps).

## 2. Identities (PROVEN, standard) and the frozen-Jacobian overstatement

- Mehler: K(rho) = Cov(g(X), g(X_rho)) = sum_d rho^d V_d; K'(rho) = J(rho) = E tr(grad g(X) Sigma grad g(X_rho)^T)
  (Gaussian interpolation); V = K(1), V_1 = J(0), mean degree D = J(1)/V.
- The exact identity's frozen part J^m (x - m) has variance tr(J^m Sigma J^m^T). If m's future is statistically like a
  typical cloud point's, this is about the gradient energy J(1) = D V (HEURISTIC). So the frozen-at-mean linear part
  overstates V by about D, and the per-gate flip terms carry a compensating negative cross term (a relu that switches
  off clips the linear part). Dev (64 x 16): ratio 14.7 at l = 0 against D = 15.9; 5.2 against 9.3 at l = 2; 2.4
  against 2.9 at l = 8; 1.07 against 1.10 at l = 15. The orthogonal linear part is the cloud-averaged Jacobian (Stein).

## 3. The degree spectrum

3a. Direction channel at infinite width (PROVEN UNDER: t fixed, n -> infinity, a thin cloud whose points' norms
concentrate; standard NNGP concentration of the empirical kernel). Two Gaussian-cloud points X, X_rho have cosine
c(rho) = 1 - (1 - rho)(1 - c_0), c_0 = cosine between independent cloud points. Their outputs have
a(X).a(X_rho)/n -> (|X||X_rho|/n) C_t(c(rho)), C_t = kappa^(t) the t-fold arc-cosine map (noiseless future). Hence
K_dir(rho) = R^2 [C_t(c(rho)) - C_t(c_0)] and s_d^dir = Taylor coefficients (computed by FFT on |rho| = 0.85).
- Closed form at small angles (kappa(cos theta) = cos(theta (1 - theta/(3 pi))) to this order; per-layer Jacobian
  overlap kappa'(c) = 1 - theta/pi): J_dir(rho) = J(1) (1 + x sqrt(1 - rho))^{-3}, x = theta_0 t/(3 pi), so
  s_1 = 1/(1 + x), D = (1 + x)^2, V/J(1) = (1 + x)^{-2} (PROVEN UNDER the small-angle law and 3a).
- Deep input regime: theta_l ~ 3 pi/(l + 6) from 1/theta' = 1/theta + 1/(3 pi), theta_0 = pi/2, so x = t/(l + 6) and
  s_1 ~ (l + 6)/(L + 6), D ~ ((L + 6)/(l + 6))^2 (HEURISTIC: small-angle law used at large angles).
- Stationary regime: the two copies inside K have independent future noise, so C_t is the independent-noise map
  c' = Q kappa(c)/(Q + 1) on hidden layers and kappa on the output layer (the L0 model of the numerics lane, radius Q
  frozen: HEURISTIC). The fixed point c* = 1 - delta* is the cloud itself, so K_dir(0) stays at C_t(c*) - C_t(c*) = 0
  while the excess C_t(c(rho)) - c* decays: first linearly (noise injection about 1/(Q + 1) per layer, gone after
  about Q delta* = 2.23 Q^{1/3} layers), then at rate lambda_a = -ln[(Q/(Q + 1))(1 - theta*/pi)] ~ theta*/pi + 1/Q.
  Because the excess is nearly uniform in rho, the stationary direction channel is degree-1 dominated:
  s_1 >= 0.9 at every t (dev n = 64: predicted 0.97, 0.95, 0.91, 0.94 at t = 1, 4, 8, 16; measured 0.94, 0.96, 0.93,
  0.92).

3b. Radial channel. sigma = 0: g(c x) = c g(x), so the radial coordinate enters at degree 1 (PROVEN; up to the
radial-angular product, which is degree 2 and of relative size (radial CV) x (angular share)). Stationary regime: the
noise-averaged response of the output to the layer-l radius decays like the radius chain's typical response
exp(sum log A), E log A = -5/(2n) per layer, so the radial variance channel decays at rate 5/n (HEURISTIC; dev n = 64:
overall decay of V from t = 1 to 64 at rate 0.072 against 5/n = 0.078; the early decay, t = 1..16, is slower, 0.057,
and the two-channel model underpredicts V at t = 16 by 6x: an open discrepancy in v1).

3c. Amplitude channel (input regime, finite width; HEURISTIC, from the input-bits lane's per-layer gain covariance
Cov(A(u), A(u')) = B(c)/n, B(c) = (2/pi) J_2(arccos c) - 1, B(1) = 5, B(0) = 0, J_2(theta) = 3 sin theta cos theta +
(pi - theta)(1 + 2 cos^2 theta)): the future log-amplitude of two cloud points has covariance sum_j B(c_j)/n over the
t future layers, c_j the kernel iterates from c(rho), so K_amp(rho) = (R^2/(4n)) sum_{j=1}^{t} [B(c_j(rho)) - B(c_j(0))].
The past amplitude (collected in layers 1..l) and |x| are in the radial channel. Total K = K_dir + K_amp + K_rad.
Without 3c the dev check at 128 x 32 overpredicts s_1 by 0.05-0.14 and underpredicts D by up to 2x at l <= 16.

## 4. How many directions each part needs

4a. Degree 1: free product (Corollary 1c): N_1(eps) from the cumulative spectrum of Lam^{1/2} O^T S O Lam^{1/2}.

4b. Degrees >= 2 (HEURISTIC "Haar-generic" model). By Theorem 1 the future's higher derivative tensors (sums over
straddled gates of rank-one terms along their pulled-back normals, H = sum_gates rho_g(0) u_g n_g n_g^T for degree 2)
are Haar-oriented relative to the cloud. Averaging over that orientation, the degree-d chaos of g in whitened
coordinates puts weight proportional to prod_j lam_j^{alpha_j} on multi-index alpha, so the best k-dimensional
subspace (here: the top-k cloud axes) captures c_d(k) = h_d(lam_1..lam_k)/h_d(lam_1..lam_n) of it (h_d: complete
homogeneous symmetric polynomial). Higher degrees are forward-limited: they need most of the cloud's effective
dimension. Dev check (128 x 32, PCA-basis residuals, measured against generic): l = 16: 0.51/0.56 at k = 1, 0.31/0.25 at
k = 4, 0.10/0.07 at 16, 0.008/0.005 at 64; l = 24: 0.37/0.39, 0.18/0.14, 0.04/0.03, 0.003/0.002 (NUMERICAL, dev).

4c. N(l, eps) (prediction rule): the smallest k with
  s_1 (1 - c_1^fp(k)) + sum_{d >= 2} s_d (1 - c_d(k)) <= eps,
c_1^fp the free-product capture (4a), c_d the generic capture (4b), s_d from section 3 (radial channel inside s_1 and
captured by k >= 1). Structure: if s_{>=2} > eps, N is forward-limited (most of the cloud's effective dimension); if
s_{>=2} << eps, N ~ N_1, backward-limited and small at large t.

4d. Scalar readout r.a: the degree-1 part has rank one (N_1 = 1), so N_sc(eps) = 1 when s_{>=2} <= eps and is
forward-limited otherwise.

## 5. Predicted regime structure (to be tested on evaluation nets, PREREG Part 1)

- Input regime, ARC 256 x 32: s_1 rises from about 0.2 at l = 0 to about 1 at l = 31; N(l, 0.01) is forward-limited and
  large (a sizeable fraction of n) for l <= L/2; near the output the vector N is set by the output cloud's own spectrum
  (tens of directions at eps = 0.01) and the scalar N is small (the radius / amplitude direction first).
- Narrow-deep 8 x 256: the cloud synchronises to one direction within about 8 layers (kernel contraction at n = 8), so
  for l >= 8 the radius is the whole description: N = 1 at every eps, under the true law (the Gaussian convention fails
  there: the log-radius variance about 5 l/(4n) makes the radius span orders of magnitude). At l = 0, N ~ n.
- Stationary regime: s_1 >= 0.9 for all t; for t small N is backward-compressed but forward-limited at eps = 0.001; at
  large t the radial channel dominates and N(0.1) = 1; the relevant share V_l/V decays (fast angular rate theta*/pi + 1/Q,
  slow radial rate 5/n).

## 6. Consequence for M1 (CONJECTURE until tested)

Wherever the input still matters (input regime, all l), a description that explains 1 - eps of V_l with eps <= 0.01
needs a sizeable fraction of the cloud's effective dimension, except (i) near the output for a scalar readout and (ii)
at narrow width after synchronisation, where it is the radius. In both exceptions the hard part moves to the forward
side: the law of the radius (amplitude) at layer l, a product of input-dependent gains collected over the past layers.
So the relevance accounting does not by itself open a route to a sample-free estimator that beats sampling; it locates
the obstruction: the higher-degree (gate) part is spread over Haar-random directions (Theorem 1), so it cannot be
compressed below the forward cloud's dimension.

---------------------------------------------------------------------------------------------------------------------
# Theory v2 (changes against v1; written after the co-prover's round 1 and the first evaluation cells; frozen before
# the co-prover's round 2 and before the stationary n = 128, 256 evaluation cells)

v2.1 Two-sided bounds on N (PROVEN). Lower: for every k-dimensional P, the degree-1 residual of P is at least the
eigenvalue tail sum_{j>k} lambda_j(C_1), C_1 = Sigma^{1/2} B^T B Sigma^{1/2} (Eckart-Young on the first chaos), and the
other chaoses only add nonnegative residual; so N(l, eps) >= N_lo(eps) = min{k : sum_{j>k} lambda_j(C_1) <= eps V}
[A, round 1]. Upper: every exhibited subspace (active subspace, degree-1 basis, cloud axes) gives N(l, eps) <= its count,
and the conditional Gaussian Poincare inequality gives residual(P_k) <= tr((I - P_k) C) for the gradient-energy matrix C.
Estimating lambda_j(C_1) from P samples inflates every eigenvalue by about tr Var(a)/P (sampling noise in B~); the
lower bound uses debiased eigenvalues (NUMERICAL). v1's registered N_1 used the raw cumulative eigenvalues and is biased
low (at n = 256, P = 4096 the inflation is n/P = 6% of V_1, which decides the 99% count).

v2.2 The variance budget at a layer (input regime; annealed, infinite-width kernel plus the 1/n amplitude term; the
channel totals are PROVEN UNDER the kernel and the amplitude formula of the input-bits lane, their sum is HEURISTIC).
In units of E|a|^2:
  V/E|a|^2 = [1 - kappa^(L)(0)]  (output direction; the same at every l, because kappa^(t)(c_l) = kappa^(L)(0))
           + (C_L - C_l)/n       (future amplitude: gains of layers l+1..L, a function of the layer-l direction)
           + (1/2 + C_l)/n       (radius |h_l| = |x| x past amplitude: degree 1 on the layer-l cloud),
  C_l = (1/4) sum_{j<l} [5 - B(c_j)], c_j = kappa^(j)(0). As l grows the totals do not change; what changes is where they
  sit on the layer-l cloud: the past amplitude moves into the radius (one direction, degree 1) and the direction
  channel's degree spectrum shifts to degree 1 (3a). With the measured cloud (cosine c_0 between independent points,
  radial variance) in place of the kernel values, the predicted V/E|a|^2 is within 7% of the measured value at
  l = 0, 4, 8 of the first ARC net (0.0626/0.0671, 0.0581/0.0578, 0.0558/0.0587).

v2.3 Mean degree from the gradient-energy identity (PROVEN, annealed, noiseless future): criticality gives
E_W |J(x) v|^2 = |v|^2 for every fixed x, v and every depth (one layer: the along-x and transverse parts both keep
their norm in expectation; iterate with fresh weights), hence E_W tr(grad g Sigma grad g^T) = tr Sigma and, with
E_W |a|^2 = E|X|^2, J_l(1)/E|a|^2 = tr Sigma / E|X|^2. So D_l = (tr Sigma / E|X|^2) / (V_l / E|a|^2). v1 summed a Taylor
series truncated at degree 60; the spectrum has a heavy tail (s_d ~ d^{-5/2} from the sqrt(1 - rho) singularity), so v1's
D was too low (6.77 against 16.10 at l = 0; the identity gives 15.98).

v2.4 Generic capture is exact in expectation for the first future layer (PROVEN). For a unit of layer l + 1 the
transverse part of its normal is a Gaussian vector w independent of the past (Theorem 1), and its degree-2 term in
whitened coordinates is proportional to a a^T with a = Sigma^{1/2} w. For any past-measurable projection P (for instance
the top-k cloud axes) E[(a^T P a)^2] / E[(a^T a)^2] = [(tr Sigma_P)^2 + 2 tr Sigma_P^2] / [(tr Sigma)^2 + 2 tr Sigma^2],
Sigma_P = Sigma^{1/2} P Sigma^{1/2}, which is h_2(lambda_<=k) / h_2(lambda). Later layers and higher degrees: HEURISTIC.
A future-informed P (the active subspace) can do better; how much better is what the measured N against the generic
prediction tests.

v2.5 Stationary regime: the slow mode, not the radius (MEASURED, n = 32, 64; CONJECTURE for its law). At t >= 16 one
direction explains 95-99% of V_l on most nets, but it is the future's slowest response direction (top direction of the
active subspace; its overlap with the radial direction e is 0.6-0.95 in whitened coordinates); the radial feature e.X
alone leaves 13-60%. Astra (round 1) reached the same conclusion on one n = 64 net at t = 64 (mean-gradient direction
71%, cloud-mean direction 30%). Rates: the angular part decays at theta*/pi = 0.672 Q^{-1/3} per layer [C+A]; the slow
mode at a rate of order 1/n (v1: 5/n; astra: 5/(2n) + 1/Q ~ 4.23/n; both tested on n = 128, 256).
The angular sector's degree spectrum tends to s_1 = 0.715, s_2 = 0.179, D = 3/2 at long times [A]; with the slow mode
(degree 1 dominated) on top, the total s_1 stays at 0.7-1.0 (measured 0.69-1.06 at n = 32, 64).

v2.6 Synchronisation in the narrow-deep input regime (HEURISTIC mechanism; MEASURED at n = 8). Kernel contraction
theta_l ~ 3 pi/(l + 6) brings two inputs to angle ~pi/n near l ~ 3n (then fewer than one gate per layer differs); after
that the angle decays at the Lyapunov gap rate (1/n per layer in angle, 2/n in squared angle); a layer with a single
active unit (probability about n 2^{-n} per layer) makes the state exactly one-dimensional. At n = 8 the second mechanism
wins: by l = 32 the radial description is exact to 1e-6 .. 1e-29 on all six evaluation nets. Prediction for n >= 16
(no bottlenecks): the radial residual falls like exp(-2(l - 3n)/n) after l ~ 3n (Part 2, PS2).

v2.7 Corrected N rule (theory_v2.predict_N). v1 ran the free product of the direction channel against the full cloud
spectrum, whose top eigenvalue is the radius; the direction channel lives on the angular block P_perp Sigma P_perp. v2:
the radial and amplitude degree-1 parts share the output direction of the mean output, so together they take one input
direction; the direction channel's degree-1 part takes the free product of the angular spectrum with the half-width
backward spectrum on the remaining k - 1 directions; degrees >= 2 take the generic capture of the angular spectrum.
Seen-cell check (ARC seed 4000): l = 31 measured 12/48/96 at eps = 0.1/0.01/0.001, v1 3/27/72 (below the rigorous
lower bound 7/29/45), v2 10/46/90; early layers unchanged (l = 0: 192/256/256 measured, v2 248/255/255).

v2.8 Stationary regime, one direction beyond t_1(eps) (HEURISTIC, two-channel model). With V_l(t) = V_slow(t) + V_ang(t),
the angular part decays relative to the slow mode at Delta = theta*/pi + 1/Q - lambda_slow per layer
(theta*/pi = 0.672 Q^{-1/3}, lambda_slow ~ 5/n), so the residual after the slow direction is about
A_0 e^{-Delta t}, A_0 = V_ang/V_slow at t ~ 1 (about 1 at n = 32-64), and N(t, eps) = 1 for
t >= t_1(eps) = ln(A_0 (1 - eps)/eps)/Delta ~ 1.24 n^{1/3} ln(1/eps) at large n (the gram-chain lane's estimate is
2 n^{1/3} ln(1/eps); same scaling). n = 64: t_1 = 15, 31, 46; n = 256: 19, 40, 61 for eps = 0.1, 0.01, 0.001. The single
direction is the slow mode found by the active subspace, not e. Measured on seen cells (n = 32, 64, AS basis): the
residual after one direction is 0.01-0.10 for t = 16-32 on resolved cells; at eps = 0.01 the count is limited by the
sampling error of V at small memory share (unresolved where 2 SE > 0.01 V).

---------------------------------------------------------------------------------------------------------------------
# v3 errata and additions (after the co-prover audits; open until the final report)

E1 (Corollary 1b, from gpt-6-astra's round 2 for the bits-bounds lane, relayed 21:58Z). As written, 1b equated a
conditional expectation with a random trace. Correct statements: (i) E[|J u|^2 | F_l, G] = E[tr(B^T J^T J B) | F_l, G]
/ (n - 1) = (2/n) tr(K^T K) for every F_l-measurable unit u in e^perp (given G, J B = K M with M iid N(0, 2/n));
(ii) conditionally also on the singular values of J B, the right singular frame is Haar on e^perp and independent of
them, so E[|J u|^2 | F_l, G, singular values] = tr(B^T J^T J B)/(n - 1). The conclusion (no per-direction alignment)
is unchanged. Also from that answer: for a Gaussian angular cloud and a linear future, the best past-measurable (blind)
k features leave a sum_{i>k} lambda_i(Lam) of the annealed linear variance, while future-aware features leave
sum_{i>k} lambda_i(Lam^{1/2} A^T A Lam^{1/2}): a d/r separation for an isotropic cloud and a rank-r future [A].

E2-E19 (gpt-6-astra round 2 for this lane, coprover/astra_r2_answer.md, T1; each accepted unless noted):
- E2 Theorem 1 needs m != 0 (at l = 0 the input law has m = 0 and the invariance is the full O(n)); future noise is
  independent of weights and past. Corollary 1a holds for functionals with Phi(R mu, F) = Phi(mu, F o R) (basis-free
  quantities), not "any functional"; the Gaussian orbit invariants also include the position of the radial-angular
  covariance vector b relative to the eigenspaces of the angular block C (its spectral measure b^T f(C) b).
- E3 Corollary 1c: asymptotic freeness gives the BULK spectral law of Lam^{1/2} O^T S O Lam^{1/2}, not the claimed
  top-eigenvalue formula s_j tr(Lam)/(n - 1) (counterexample S = I). The top-eigenvalue approximation holds only for a
  low-rank backward subspace whose compressed covariance concentrates. The radial-angular cross covariance must be handled
  before taking an angular block. Status: the random-congruence model is PROVEN for an independently Haar-oriented
  operator; for the cloud-averaged Jacobian HEURISTIC (measured support: the angular degree-1 participation ratio is
  within 20% of the free-position formula at every ARC layer, section v3.1 below).
- E4 Section 2: the frozen-linear variance needs a noise convention (E_Xi J^m for the noise-averaged part); the
  comparison tr(J^m Sigma J^m^T) ~ D V is HEURISTIC.
- E5 3a: the deterministic-cosine limit needs concentration of inner products, e.g. tr Sigma^2/(|m|^2 + tr Sigma)^2 -> 0
  and m^T Sigma m/(|m|^2 + tr Sigma)^2 -> 0; the small-angle closed forms are asymptotic model identities.
- E6 RETRACTED: "stationary s_1 >= 0.9 at every t" (3a) does not follow and conflicts with the angular long-time limit
  s_1 -> 0.715 [A]; measured s_1 >= 0.85 on only 73% of stationary cells (P4 missed).
- E7 3b: positive homogeneity does not put the radius in the first chaos; |X| is not a linear Gaussian coordinate. Linear
  radial dependence holds exactly on a fixed ray; for a thin cloud e.X approximates it. E log A = -5/(2n) is a
  large-width expansion (A = 0 with probability 2^-n). The radial channel statement is HEURISTIC.
- E8 3c: B(c) is right; the additive kernel K_dir + K_amp + K_rad neglects cross terms and normalisation corrections
  (HEURISTIC); the gain sum runs over j = 0..t-1 (the code does; the text said 1..t).
- E9 4b: generic capture does NOT follow from Theorem 1. Rotational invariance of a tensor's law does not fix its
  covariance across trace and traceless parts; isotropic examples give k/r (H = I), k(k + 2)/(r(r + 2)) (one Haar
  rank-one H, fixed P) and k(k + 1)/(r(r + 1)) (isotropic symmetric coefficients). The h_d capture is a MODEL (HEURISTIC),
  and neither it nor optimality of cloud axes follows from the decoupling.
- E10 v2.4 WRONG as stated: the Wick ratio [(tr Sigma_P)^2 + 2 tr Sigma_P^2]/[(tr Sigma)^2 + 2 tr Sigma^2] is not the
  h_2 ratio [(tr Sigma_P)^2 + tr Sigma_P^2]/[(tr Sigma)^2 + tr Sigma^2]; and the gate's second-chaos coefficient
  phi(b/s)/s depends on the normal, so it cannot be dropped when averaging. Withdrawn.
- E11 4c: the rule combines captures achieved in different subspaces without exhibiting a common subspace, so it is
  optimistic; s_>=2 > eps alone gives no large-dimensional lower bound (a high-degree ridge needs one direction). 4d:
  N_sc <= 1 when s_>=2 <= eps (nonzero first chaos) is PROVEN; "forward-limited otherwise" is unsupported.
- E12 v2.1: the population first-chaos lower bound and the conditional Poincare upper bound are correct; subtracting
  tr Var(a)/P from each eigenvalue is NOT a valid general correction (the noise matrix is anisotropic:
  E[B^T B]_hat = C_1 + (E(|Y|^2 Z Z^T) - C_1)/P), so the reported first-chaos counts are point estimates, not certified
  lower bounds. A certified bound needs a matrix error radius (audit T4: e.g. Chebyshev on the U-statistic kernel), which
  is vacuous at the sample sizes run. Also n/P is the noise fraction relative to V, i.e. n/(P s_1) relative to V_1
  (21% at ARC's input, not 6%).
- E13 v2.2: the channel totals are not exact facts about the Gaussianised network (the true-law total is cut-independent,
  the Gaussianised one need not be); at l = 0 the input-radius variation is degree two under the Gaussian input. Status
  HEURISTIC (a model with measured forward inputs; its agreement is reported as NUMERICAL).
- E14 v2.3: the identity gives the variance-weighted annealed mean degree E_W J(1)/E_W V, not E_W[J(1)/V] and not an
  exact quenched formula (x = 0 excluded). Its use per net is HEURISTIC (measured agreement within 3-18%).
- E15 v2.5 overstated: on the 21:58Z snapshot, 7 of 16 resolved stationary cells with t >= 16 reach 95% with one
  direction and none reaches 99%; v2.8's exponential law holds only if the slow response is a one-coordinate (ridge)
  function, otherwise a floor remains (audit T6).
- E16 v2.6: the probability n 2^-n is for one fixed input; that the whole cloud passes one bottleneck is not shown, and
  the residuals at l = 32 include 8.6e-6, 2.3e-6 and 1.9e-6 (not "1e-6 .. 1e-29 on all six nets").
- E17 v2.7 is HEURISTIC; its implementation gives the angular first chaos k - 1 directions and the higher chaoses k
  without a common subspace, and it drops chaos above degree 60 (the omitted mass is 0.055 of V at ARC's input), which
  biases the predicted residual low at eps <= 0.01 on early layers.

v3.1 Cross-lane check (NUMERICAL, post hoc). The gram-chain lane's annealed free-position formula for the dimension of
the linear relevance, 1/PR = 1/PR_C + 1/PR_M - 1/n with PR_M = n/(2t + 1), applied to the angular part (the debiased
degree-1 spectrum without its top, radial/amplitude, eigenvalue; PR_C from the measured angular cloud spectrum), matches
the quenched nets: ARC measured/predicted 4.8/4.2, 5.5/4.6, 6.4/5.4, 8.0/7.2, 8.7/8.5, 9.7/10.3 at l = 4..31 (first net);
all cells: median ratio 1.19, 37 of 53 within 1.5x. With the radial eigenvalue included the formula overstates the
dimension (median 0.60): the rank-one radial/amplitude part dominates the degree-1 spectrum.

v3.2 Conditional lower bound for the nonlinear part (PROVEN UNDER iid Haar normals, nonnegative diffuse weights fixed
independently of the normals, and an isotropic r-dimensional cloud; gpt-6-astra round 2, T5): for a scalar second-chaos
component made of G rank-one gate terms, matrix Chernoff gives, with probability >= 1 - 2r exp(-delta^2 W/(3 r beta_max)),
that ANY k-dimensional projection, future-informed or not, leaves at least (1 - k/r)((1 - delta)/(1 + delta))^2 of it, so
capturing 1 - eps' needs k >= r[1 - eps'((1 + delta)/(1 - delta))^2]. Vector output: R_2(P) >= 2 sum_{j>k}
lambda_j(S_2), S_2 = sum_o H_o^2. Whether the networks' gate tensors satisfy the needed concentration (pulled-back
normals are dependent, sensitivities signed and correlated, coefficients depend on the normals) is the missing theorem
behind the "spread nonlinear part" claim (CONJECTURE). Estimating S_2 from samples needs P >> n^2.
