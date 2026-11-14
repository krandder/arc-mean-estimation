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
