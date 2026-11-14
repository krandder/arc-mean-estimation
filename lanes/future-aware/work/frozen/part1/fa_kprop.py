"""ARC's cumulant propagation (mlp_kprop through the arc-update wrapper, sigma = 0, avg metric, ARC's flop counter) with
a projection hook: after each hidden layer's nonlinear step the third-cumulant core K[3] (dense n x n x n, 'simple'
kind, unfactorised) is replaced by its restriction to a k-dim feature span,
    kappa_3  <-  kappa_3 x_1 Pi x_2 Pi x_3 Pi,   Pi = S A (A^T S A)^{-1} A^T  (S = the state's covariance K[2]),
i.e. "third cumulant in the k feature directions, Gaussian elsewhere" (the cumulant form of the linear-Gaussian
conditional). Feature kinds (computed from the method's own state (K[1], K[2]) at that layer):
  pca    top-k eigenvectors of K[2] (forward);
  futmf  whitened top-k directions of Jmf^T Jmf, Jmf = the mean-field future Jacobian prod_j diag(p_j) W_j with gate
         probabilities p_j = P(z_j > 0) from the same method's own K = 2 pre-activation moments (deductive backward
         sweep: one n x n product per layer);
  futv   whitened active subspace of the true future map from VJPs at samples of N(K[1], K[2]) (sampled backward
         pass, M samples per layer);
  none   no projection (ARC's k3).
Costs: ARC's counter for the propagation; the hook's projection (6 n^3 k-ish flops, counted analytically), the
backward work (mean-field sweep 2 n^3 per layer; VJPs 3 x 2 n^2 t per sample) are returned separately."""
import os, sys, time
import numpy as np
import torch
from scipy.special import ndtr

AU_LIB = '/home/agent/workspaces/mats/work/arc-update/lib'
if AU_LIB not in sys.path:
    sys.path.insert(0, AU_LIB)
import au  # noqa: E402
from au import anet, KN, KH, NamedFlopCounter, flop_name, WICK_COEF_D  # noqa: E402
from mlp_kprop.harmonic import HTensor  # noqa: E402
from mlp_kprop.factor_k3 import FactoredTensor  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa  # noqa: E402


def whiten(A, S):
    if A.shape[1] == 0:
        return A
    Ca = A.T @ S @ A
    ev, U = np.linalg.eigh(0.5 * (Ca + Ca.T))
    ev = np.clip(ev, 1e-300, None)
    return A @ (U / np.sqrt(ev)[None, :]) @ U.T


def k2_gate_probs(W):
    """Gate probabilities p_l = P(z_l > 0) at every layer from ARC's K = 2 'simple' pre-activation moments
    (pre-activation mean W m, variance diag(W S W^T)); also returns the K = 2 states (m_l, S_l)."""
    L = len(W)
    r = au.arc_kprop(W, 2, kind='simple', keep_states=tuple(range(1, L + 1)), count_flops=True)
    probs = {}
    Wn = [w.double().numpy() for w in W]
    n = Wn[0].shape[0]
    for l in range(1, L + 1):
        m, S = r['states'][l - 1] if l > 1 else (np.zeros(n), np.eye(n))
        mu = Wn[l - 1] @ m
        s = np.sqrt(np.maximum(np.einsum('ij,jk,ik->i', Wn[l - 1], S, Wn[l - 1]), 1e-300))
        probs[l] = ndtr(mu / s)
    return probs, r


def mf_jacobians(W, probs):
    """Jmf_l = prod_{j = L..l+1} diag(p_j) W_j for l = 0..L-1 (n_out x n), one backward sweep."""
    L = len(W); Wn = [w.double().numpy() for w in W]
    J = {L: np.eye(Wn[0].shape[0])}
    for l in range(L - 1, -1, -1):
        J[l] = J[l + 1] @ (probs[l + 1][:, None] * Wn[l])
    return J


def np_vjp_R(Wn, l, H, seed):
    """E[J^T J] (n x n) of the future map from layer l over model samples H (m, n), numpy float32, random-v VJPs."""
    rng = np.random.RandomState(int(seed))
    acts = [H.astype(np.float32)]
    for j in range(l, len(Wn)):
        acts.append(np.maximum(acts[-1] @ Wn[j].T, 0.0))
    g = rng.randn(*acts[-1].shape).astype(np.float32)
    for j in range(len(Wn) - 1, l - 1, -1):
        g = (g * (acts[j - l + 1] > 0)) @ Wn[j]
    g = g.astype(np.float64)
    return g.T @ g / g.shape[0]


def project_core(core, S, A):
    """kappa_3 x_i Pi with Pi = S A A^T (A whitened under S), using the rank-k structure."""
    SA = S @ A
    T = np.tensordot(core, A, axes=([0], [0]))          # (n, n, k): contract mode 0
    T = np.tensordot(T, A, axes=([0], [0]))             # (n, k, k)
    T = np.tensordot(T, A, axes=([0], [0]))             # (k, k, k)
    T = np.tensordot(T, SA, axes=([0], [1]))            # (k, k, n)
    T = np.tensordot(T, SA, axes=([0], [1]))            # (k, n, n)
    T = np.tensordot(T, SA, axes=([0], [1]))            # (n, n, n)
    return T


def mf_relevance(W, probs):
    """Mean-field E[J^T J] of the future map at every layer with independent Bernoulli(p_j) gates:
    R_L = I, R_{l} = W_{l+1}^T [P R_{l+1} P + diag(p (1 - p) diag(R_{l+1}))] W_{l+1}, P = diag(p_{l+1}).
    Captures the gate-fluctuation (nonlinear) part at the independent-gate level; 2 n^3 flops per layer."""
    L = len(W); Wn = [w.double().numpy() for w in W]
    n = Wn[0].shape[0]
    R = {L: np.eye(n)}
    for l in range(L - 1, -1, -1):
        p = probs[l + 1]
        M = p[:, None] * R[l + 1] * p[None, :] + np.diag(p * (1 - p) * np.diag(R[l + 1]))
        R[l] = Wn[l].T @ M @ Wn[l]
    return R


@torch.no_grad()
def arc_k3_proj(W, kind='none', k=0, Jmf=None, mvjp=1 << 11, seed=0, kind_arc='simple', Rmf=None, factor=True):
    """Returns dict(mean, flops (ARC counter, propagation only), hook_flops, backward_flops, secs). The hook runs in
    numpy, so ARC's torch flop counter does not see it; its cost is counted analytically."""
    n, L = W[0].shape[0], len(W)
    Wn32 = [w.float().numpy() for w in W]
    net = anet.Net(0, n=n, L=L, sigma=0.0, W=W)
    kind_e = {'simple': KH.SIMPLE, 'augment': KH.AUGMENT}[kind_arc]
    mlp = KN.arc_mlp(net, L, torch.float64)
    counter = NamedFlopCounter()
    t0 = time.time(); hook_flops = 0.0; back_flops = 0.0
    with counter:
        with flop_name('kprop'):
            K = KH.coerce_input({1: torch.zeros(n, dtype=torch.float64), 2: torch.eye(n, dtype=torch.float64)},
                                k_max=3, kind=kind_e)
            for l in range(L):
                Wl = mlp.Ws[l].weight
                K = KH.linear_kprop(K, Wl, k_max=3, set_metric=mlp.init_scale[l], bias=None)
                K = KH.nonlin_kprop(K, nonlin_wick_coef=WICK_COEF_D['relu'], k_max=3, kind=kind_e, use_pK=True,
                                    factor=factor)
                if kind != 'none' and l < L - 1 and k > 0:
                    m = K[1].core.detach().numpy().copy(); S = K[2].core.detach().numpy().copy()
                    S = 0.5 * (S + S.T)
                    if kind == 'pca':
                        A = fa.features('pca', k, S)
                    elif kind == 'futmf':
                        A = fa.features('fut', k, S, Jmf[l + 1].T @ Jmf[l + 1])
                        back_flops += 2.0 * n ** 3
                    elif kind == 'futmf2':
                        A = fa.features('fut', k, S, Rmf[l + 1])
                        back_flops += 4.0 * n ** 3
                    elif kind == 'futv':
                        ev, U = np.linalg.eigh(S)
                        rng = np.random.RandomState(int(seed * 1000 + l))
                        H = m[None, :] + rng.randn(mvjp, n) @ (U * np.sqrt(np.clip(ev, 0, None))).T
                        A = fa.features('fut', k, S, np_vjp_R(Wn32, l + 1, H, seed * 1000 + 500 + l))
                        back_flops += mvjp * 3.0 * 2.0 * n * n * (L - l - 1)
                    else:
                        raise ValueError(kind)
                    A = whiten(A, S)
                    if isinstance(K[3], FactoredTensor):
                        Pi = S @ A @ A.T
                        fac = [f.detach().numpy() for f in K[3].factors]
                        newf = tuple(torch.from_numpy(Pi @ f) for f in fac)
                        K[3] = FactoredTensor(n=n, d=3, factors=newf)
                        hook_flops += 3 * 2.0 * n * n * fac[0].shape[1] + 2.0 * n * n * k + 10.0 * n ** 3
                    else:
                        core = K[3].core.detach().numpy()
                        core = project_core(core, S, A)
                        core = (core + core.transpose(1, 0, 2) + core.transpose(2, 1, 0) + core.transpose(0, 2, 1)
                                + core.transpose(1, 2, 0) + core.transpose(2, 0, 1)) / 6.0
                        K[3] = HTensor(torch.from_numpy(np.ascontiguousarray(core)), r=0)
                        hook_flops += 4.0 * n ** 3 * k + 10.0 * n ** 3
    mean = K[1].to_tensor().clone().numpy()
    return dict(mean=mean, flops=float(counter.total()), hook_flops=hook_flops, backward_flops=back_flops,
                secs=time.time() - t0)
