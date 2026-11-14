# Relevance accounting: definitions (v1, 1 November 2026, 21:00Z)

Lane: relevance accounting (bead pool-qxszj1.24). Owner: opus-mats-relevance. Sibling lanes that use these
definitions: bits-bounds (work/bits-bounds/), gram-chain (work/gram-chain/). Changes after v1 are appended at the end
with a date; nothing above is edited silently.

## 0. Setting

- Model S. Width n, layers h_k = relu(W_k h_{k-1}) + sigma xi_k for hidden layers k < L, output a = relu(W_L h_{L-1})
  (no noise on the output), W_k iid N(0, 2/n) entries, xi_k iid N(0, I_n), no biases.
- Regimes.
  - Noise-stationary: sigma > 0 (sigma = 1 without loss: the state for sigma is sigma times the state for 1), infinite
    past (in practice a burn-in of >= 8n layers).
  - Input: sigma = 0, h_0 = x ~ N(0, I_n). Nets: ARC's 256 x 32 and narrow-deep 8 x 256.
- Quenched: everything is for one fixed weight sequence. Annealed: averaged over the weights (E_W). A per-net ratio is
  not the ratio of annealed means; both are reported separately.
- Layer l, t = L - l weight layers to go (t = 1: only the output layer). Future noise Xi_l = (xi_{l+1}, ..., xi_{L-1}).
- Primary observable: the output vector a in R^n, errors in nMSE = |error|^2 / tr Var(a) (the earlier lanes'
  convention). Secondary: a scalar readout r.a with a fixed unit vector r (its linear part has rank one; see 4.3).

## 1. The relevant variance at layer l

- Layer-l law mu_l: the law of h_l for the fixed weights (stationary: over all past noise; input: over x and the noise
  of layers 1..l). Mean point m_l = E h_l, covariance Sigma_l = Cov h_l (the "Lyapunov covariance" of the brief).
- Value function g_l(x) = E[a | h_l = x] = E_{Xi_l} F_l(x, Xi_l), where a = F_l(h_l, Xi_l) is the future map
  (g_l = F_l when sigma = 0).
- Relevant variance V_l = tr Cov_{X ~ mu_l}(g_l(X)). Total V = tr Cov(a). Memory share M_l = V_l / V (= 1 for sigma = 0;
  in the stationary regime the rest, E tr Cov(a | h_l), is made by the future noise and no description of h_l can
  explain it).
- The mean: E a = E_{mu_l} g_l (tower property). Only V_l matters for estimating E a.

## 2. Descriptions and explained share

- A description of the layer-l state is a measurable map T of h_l. Its explained share
  S_l(T) = tr Cov(E[g_l(X) | T(X)]) / V_l, residual 1 - S_l(T) = min_G E|g_l(X) - G(T(X))|^2 / V_l.
- Mean to precision eps: if a reduced model G satisfies E|g_l - G(T)|^2 <= eps V_l, then
  |E g_l - E G(T)|^2 <= eps V_l (Jensen), i.e. the mean is right to nMSE eps * M_l. So "explains 1 - eps of the variance
  with a computable reduced model" implies "the mean to precision eps" in nMSE units; the converse fails. An estimator
  must in addition know the law of T(X) (the forward side); section 6.

## 3. The size of a description: N(l, eps)

Primary count, linear features (basis-free):

  N(l, eps) = min { k : there is P in R^{k x n} with E |g_l(X) - E[g_l(X) | P X]|^2 <= eps V_l },

with X ~ gamma_l = N(m_l, Sigma_l), the Gaussian law with the exact mean and covariance of mu_l ("Gaussian
convention", the brief's forward information). N^mu(l, eps) is the same with X ~ mu_l (true law). Reported eps: 0.1,
0.01, 0.001.
- Why the Gaussian convention is primary: under gamma_l the conditional law of the complement given P X is Gaussian and
  explicit, so S_l(P X) is measurable exactly by pick-freeze (two forward passes per sample), and it is the law a
  hybrid estimator would integrate analytically. Its fidelity is reported every time: V_l and E g_l under gamma_l
  against mu_l. Under mu_l only upper bounds on N are measurable (section 5.3).
- Measured N is an upper bound computed on a nested family of candidate subspaces (section 5.2); the true minimum over
  all subspaces can only be smaller. Lower bounds on N are theory (bits-bounds lane).
- Bits. For the Gaussian linear part (5.1, degree 1) the rate-distortion function
  R_l(eps) = sum_j max(0, (1/2) log2(lambda_j / theta)), with sum_j min(lambda_j, theta) = eps V_{l,1}, counts the bits
  of h_l needed to reproduce that part to distortion eps; reported beside N where useful.

Secondary count, gates: a future gate is a unit (k, i), k = l+1..L, with preactivation z_{k,i}. G(l, eps) is the number
of future gates whose single-gate terms (4.2) must be kept, in decreasing order of their own variance, for the
first-order gate model to come within eps V_l of the full degree >= 2 part. Reported with N; not used to define N.

## 4. The parts of V_l (the accounting)

### 4.1 Hermite (Wiener chaos) accounting under gamma_l (orthogonal; the primary table)
Write X = m_l + Sigma_l^{1/2} Z, Z ~ N(0, I_n). Then V_l = sum_{d >= 1} V_{l,d}, V_{l,d} the variance of the degree-d
chaos component of g_l(m + Sigma^{1/2} Z). Exact identities (Mehler, Stein):
- K_l(rho) = Cov(g_l(X), g_l(X_rho)) = sum_d rho^d V_{l,d}, with X_rho = m + Sigma^{1/2}(rho Z + sqrt(1 - rho^2) Z').
- Jacobian overlap J_l(rho) = E tr(grad g_l(X) Sigma grad g_l(X_rho)^T) = K_l'(rho) = sum_d d rho^{d-1} V_{l,d};
  J_l(1) = E tr(grad g Sigma grad g^T) (gradient energy), J_l(0) = V_{l,1}; mean degree D_l = J_l(1) / V_l.
- Degree 1 (linear part): V_{l,1} = |B Sigma^{1/2}|_F^2 with B = E_gamma[grad g_l(X)], the cloud-averaged Jacobian
  (Stein). Its relevance spectrum: eigenvalues lambda_1 >= lambda_2 >= ... of R_1 = Sigma^{1/2} B^T B Sigma^{1/2}.
  N_1(eps') = number of top eigenvalues holding 1 - eps' of V_{l,1}.
- Degree 2 (single gates at their boundary): V_{l,2} = (1/2) sum_o |Sigma^{1/2} H_o Sigma^{1/2}|_F^2 with
  H = E_gamma[hess g_l], and for a piecewise-linear g_l (sigma = 0, distributional derivatives)
  H_o = sum_{gates (k,i)} E[ delta(z_{k,i}(X)) u_{k,i,o} n_{k,i} n_{k,i}^T ],
  n_{k,i} = grad_x z_{k,i} (the gate's normal pulled back to layer l), u_{k,i} = d a / d h_{k,i} (its backward
  sensitivity). So each gate contributes (density of the cloud at its boundary) x (backward sensitivity) x (cloud
  spread along its normal)^2: the brief's "gate part".
- Degree >= 3: gate-gate interactions (a gate's normal, boundary or sensitivity changed by other gates) plus the higher
  Hermite tail of single gates (a lone hinge at zero margin keeps 88% of its nonlinear variance in degree 2).
- Shares s_d = V_{l,d} / V_l; the table reports s_1, s_2, s_{>=3}.

### 4.2 Exact pathwise identity (true law; attribution to individual gates)
Run the trajectory of x and of the mean point m with the same future noise. With D_k(m) the gates along m's path,
J^m_{k->L} = D_L(m) W_L ... D_{k+1}(m) W_{k+1}, and the flip vector f_k(x) = |z_k(x)| * 1[sign z_k(x) != sign z_k(m)]
(componentwise, >= 0):
  a(x, Xi) - a(m, Xi) = J^m_{l->L}(x - m) + sum_{k=l+1}^{L} J^m_{k->L} f_k(x, Xi)        (exact).
- First-order gate model: f_k computed from the linearised preactivation z_k(m) + W_k J^m_{l->k-1}(x - m), i.e. a sum
  of hinges relu(+-(z_{k,i}(m) + n_{k,i}.(x - m))) with weights J^m_{k->L} e_i. Interactions = exact - first order.
- Warning (why 4.1 is primary): J^m (the Jacobian at the mean, frozen gates) is not the best linear part when the cloud
  is wider than the Jacobian's coherence radius. Then tr(J^m Sigma J^m^T) ~ J_l(1) = D_l V_l can be far above V_l and
  the cross term between the frozen-linear part and the flips is large and negative. The orthogonal linear part is the
  cloud-averaged Jacobian B (4.1).

### 4.3 Vector versus scalar output
For a scalar readout the degree-1 part has rank one (N_1 = 1 for every eps), so all of the counting is in degrees >= 2.
For the vector output N_1 follows the singular spectrum of B.

## 5. Measurement protocols (what the numbers in the report are)

5.1 V_l, M_l: pick-freeze, E[a(X, Xi) . a(X, Xi')] - |E a|^2 with independent future noises (unbiased).
5.2 N(l, eps): candidate subspaces P_k = top-k eigenvectors (whitened) of the active-subspace matrix
    C_l = E_gamma[Sigma^{1/2} grad g^T grad g Sigma^{1/2}] (and, as checks, of R_1 and of Sigma). Residual of P_k by
    pick-freeze under gamma_l: (1/2) E |g(X) - g(X')|^2 with X' sharing P_k Z and an independent complement
    (future noises independent inside each g). Gaussian Poincare bound: residual(P_k) <= sum_{j>k} mu_j(C_l) (PROVEN,
    standard; loose by at most the residual's mean degree).
5.3 True-law upper bound: R^mu(P) = E_mu |g(X) - g(X_hat)|^2 / V_l, X_hat = m + Sigma P^T (P Sigma P^T)^{-1} P (X - m);
    R^mu(P) >= the optimal residual of P under mu_l.
5.4 Hermite shares: K_l(rho) on a grid of rho (pick-freeze) and V_{l,1} by Stein (averaged gradients).

## 6. Link to estimation (M1)

A hybrid estimator at layer l (resolve T_l, integrate the rest under a tractable forward law q_l) has error
(forward: q_l against mu_l) + (backward: residual of T_l, at most eps M_l in nMSE). N(l, eps) prices the backward side
only. The bar is the best multilevel sampler (outbox/unrestricted-estimators-2026-10-31.md).

## 7. Annealed counterparts (for the gram-chain lane)

E_W V_l, E_W V_{l,d} and E_W J_l(rho) are replica quantities (2 replicas sharing the past up to a rho-correlation,
independent future noise; tangent vectors propagate inside the same Gram chain because the weights act on them by the
same rotation-invariant rows). N(l, eps) itself is quenched; compare annealed predictions with the median over nets of
the quenched N.
