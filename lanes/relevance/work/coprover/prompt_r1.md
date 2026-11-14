You are a co-prover and red team (gpt-6-astra) for a research lane on random critical ReLU networks. Work independently:
derive, compute, and say plainly what is proven, what is heuristic and what fails. Do NOT read the directory
/home/agent/workspaces/mats/work/relevance/ (it holds my own independent attempt; this round must stay independent).
You may read, as background: /home/agent/workspaces/mats/outbox/stationary-regime-2026-10-31.md,
/home/agent/workspaces/mats/outbox/stationary-numerics-2026-10-31.md, /home/agent/workspaces/mats/outbox/input-bits-2026-10-31.md,
/home/agent/workspaces/mats/outbox/kstar-frames-2026-10-30.md, and code in /home/agent/workspaces/mats/work/stationary/lib/st.py,
/home/agent/workspaces/mats/work/stationary-numerics/lib/gram_chain.py, /home/agent/workspaces/mats/work/input-bits/lib/ib.py.
You may run small numerical computations (python3, numpy, scipy) if your sandbox allows; keep them small (minutes, one
thread). Number your answers Q1..Q8 and label every claim PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL, HEURISTIC or
CONJECTURE.

## Setting
Width n. W_k (n x n) iid N(0, 2/n), no biases. Hidden layers h_k = relu(W_k h_{k-1}) + sigma xi_k, xi_k iid N(0, I_n);
output a = relu(W_L h_{L-1}) in R^n (no output noise). Two regimes:
- input regime: sigma = 0, h_0 = x ~ N(0, I_n); nets ARC 256 x 32 (n = 256, L = 32) and narrow-deep 8 x 256;
- noise-stationary regime: sigma = 1 (a pure scale), infinite past; the state h_l at a fixed layer has, for fixed weights,
  a stationary law (a thin cloud around a mean point at large n; see the stationary reports).
Fix the weights (quenched). Layer l, t = L - l weight layers to go. mu_l = law of h_l (over x, resp. past noise),
m_l = E h_l, Sigma_l = Cov h_l. Value function g_l(x) = E[a | h_l = x] (future noise averaged; g_l = future map if
sigma = 0). Relevant variance V_l = tr Cov_{mu_l} g_l(h_l).
Description: any statistic T of h_l; explained share S(T) = tr Cov(E[g_l | T]) / V_l.
Main count: N(l, eps) = min k such that some k-dimensional linear projection P h_l has S(P h_l) >= 1 - eps, computed
with h_l replaced by the Gaussian gamma_l = N(m_l, Sigma_l) ("Gaussian convention"; the true-law version is N^mu).
Hermite accounting under gamma_l: with h = m + Sigma^{1/2} Z, V_l = sum_{d>=1} V_{l,d} (Wiener chaos degrees);
Mehler: Cov(g(X), g(X_rho)) = sum_d rho^d V_{l,d} for rho-correlated Gaussian copies; V_{l,1} = |E[grad g] Sigma^{1/2}|_F^2
(the cloud-averaged Jacobian, Stein); mean degree D_l = E tr(grad g Sigma grad g^T) / V_l.
Exact pathwise identity (shared future noise, gates D_k(m) along the mean point's path, flips f_k = |z_k(x)| 1[sign
change]): a(x) - a(m) = J^m_{l->L}(x - m) + sum_k J^m_{k->L} f_k(x).
Known numbers you may use: stationary cloud angle delta* = 1 - cos ~ 2.23 Q^{-2/3}, Q = |h|^2/(n sigma^2) ~ 0.577 n;
tangent response along covariant Lyapunov vector k ~ exp(-2c(k + 1/4)t/n), c ~ 1.14; the cloud's eigenvalues spread
roughly like 1/k; kstar-frames: forward-only frames are at most chance plus one direction; the coherence radius of
downstream Jacobians is about 1.4/t radians.

## Questions
Q1 (decoupling). Given the past (all weights up to layer l and the layer-l law), what is the joint law of the future
map relative to the cloud's orientation? Is the future's angular structure (singular frame of the Jacobian at m, the
normals of future gates pulled back to layer l) Haar-distributed relative to the cloud's principal axes, apart from the
mean direction? Prove or refute, at finite n. Consequences for the linear relevance spectrum
eig(Sigma^{1/2} B^T B Sigma^{1/2}), B = E[grad g_l].
Q2 (linear part). Coordinator's route: "decompose the linearised future over covariant Lyapunov directions: forward
variance (1/k spread) times backward amplification exp(-2c(k + 1/4)t/n) per direction; predict N ~ n/(L - l) log(1/eps)".
Is that the right per-direction product? Predict the degree-1 relevance spectrum and N_1(eps) (vector output) from
n, t, eps, in both regimes.
Q3 (degree spectrum). Predict s_d = V_{l,d}/V_l, especially s_1 and D_l, as functions of l, L (input regime) and of t,
n (stationary regime, where the two copies in the Mehler covariance have independent future noise). Infinite-width
kernel first, then finite-width corrections (amplitude/radius).
Q4 (gates). Express V_{l,2} as a sum over future gates. Which future layers contribute, how many gates, how spread are
their normals in layer-l coordinates, and what fraction of V_{l,2} can a k-dimensional subspace capture?
Q5 (N). Predict N(l, eps) for eps = 0.1, 0.01, 0.001: ARC 256 x 32 at l = 0, 8, 16, 24, 31; narrow-deep 8 x 256 at
l = 0, 8, 32, 128, 255; stationary regime n = 32..256, t = 1..2n. Vector output and a scalar readout r.a. Is N small
anywhere, and where?
Q6 (stationary channels). How does V_l decay with t in the stationary regime, which part of h_l carries it at large t,
at what rates (in n), and how does N behave there?
Q7 (estimation). Where N is small, sketch a hybrid estimator (resolve the relevant part, integrate the rest) and compare
its cost with plain MC, RQMC and the multilevel shared-trajectory sampler at equal compute; where N is large, what does
that imply for ARC's problem (a sample-free estimator beating sampling at depths that grow with width)?
Q8 (red team). What is wrong or weak in this framing (linear projections, Gaussian convention, Hermite accounting,
the exact identity)? Propose a better definition of "the bits that matter at layer l" if you have one, with its
measurable counterpart.
