"""Exploratory (not registered): ARC's dense K = 4 'simple' propagation with the dense cores of orders 3 and 4
projected each hidden layer on a k-dim feature span. Kept apart from lib/fa_kprop.py, which is frozen by the PREREG."""
import math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fa_kprop import (au, anet, KN, KH, NamedFlopCounter, flop_name, WICK_COEF_D, HTensor, fa, whiten, np_vjp_R,
                      k2_gate_probs, mf_relevance)  # noqa: F401


def project_core_d(core, S, A):
    """Order-d symmetric core (n,)*d projected on every mode by Pi = S A A^T (A whitened), via the rank-k structure."""
    SA = S @ A
    d = core.ndim
    T = core
    for _ in range(d):                       # contract every mode with A (moves contracted mode to the end)
        T = np.tensordot(T, A, axes=([0], [0]))
    for _ in range(d):                       # expand every mode with SA
        T = np.tensordot(T, SA, axes=([0], [1]))
    return T


@torch.no_grad()
def arc_kK_proj(W, K_max=4, kind='none', k=0, Jmf=None, Rmf=None, mvjp=1 << 11, seed=0, kind_arc='simple',
                orders=(3, 4)):
    """ARC's dense K_max = 4 (or 3) 'simple' propagation with every dense core of the listed orders (r = 0 HTensors)
    projected each hidden layer on the k-dim feature span (exploratory, not registered). Returns dict as arc_k3_proj."""
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
                                k_max=K_max, kind=kind_e)
            for l in range(L):
                Wl = mlp.Ws[l].weight
                K = KH.linear_kprop(K, Wl, k_max=K_max, set_metric=mlp.init_scale[l], bias=None)
                K = KH.nonlin_kprop(K, nonlin_wick_coef=WICK_COEF_D['relu'], k_max=K_max, kind=kind_e, use_pK=True,
                                    factor=False)
                if kind != 'none' and l < L - 1 and k > 0:
                    m = K[1].core.detach().numpy().copy(); S = K[2].core.detach().numpy().copy()
                    S = 0.5 * (S + S.T)
                    if kind == 'pca':
                        A = fa.features('pca', k, S)
                    elif kind == 'futmf2':
                        A = fa.features('fut', k, S, Rmf[l + 1]); back_flops += 4.0 * n ** 3
                    elif kind == 'futv':
                        ev, U = np.linalg.eigh(S)
                        rng = np.random.RandomState(int(seed * 1000 + l))
                        H = m[None, :] + rng.randn(mvjp, n) @ (U * np.sqrt(np.clip(ev, 0, None))).T
                        A = fa.features('fut', k, S, np_vjp_R(Wn32, l + 1, H, seed * 1000 + 500 + l))
                        back_flops += mvjp * 3.0 * 2.0 * n * n * (L - l - 1)
                    else:
                        raise ValueError(kind)
                    A = whiten(A, S)
                    for dd in orders:
                        if dd in K and isinstance(K[dd], HTensor) and K[dd].r == 0 and K[dd].core.ndim == dd:
                            core = project_core_d(K[dd].core.detach().numpy(), S, A)
                            perms = __import__('itertools').permutations(range(dd))
                            core = sum(core.transpose(p) for p in perms) / math.factorial(dd)
                            K[dd] = HTensor(torch.from_numpy(np.ascontiguousarray(core)), r=0)
                            hook_flops += 2.0 * dd * n ** dd * k
    mean = K[1].to_tensor().clone().numpy()
    return dict(mean=mean, flops=float(counter.total()), hook_flops=hook_flops, backward_flops=back_flops,
                secs=time.time() - t0, tower={d: repr(v) for d, v in K.items()})
