"""arc-update measurement library.

Nets: ARC's family (He-ReLU, W_l iid N(0, 2/n), no bias, x ~ N(0, I_n), z_l = W_l h_{l-1}, h_l = relu(z_l)), with the
arc-noisy lane's weight stream (anet.make_weights: numpy RandomState(1_000_003 + 7919 seed)), so nets 200-204 at
256 x 32 match that lane's noiseless 2^26-path truths (work/arc-noisy/truth/truth_256_32_s0_seed20?.npz).

Contents
- weights, forward: nets and batched passes (float32 matmuls, float64 accumulation).
- mc_moments: Monte Carlo per-layer sums S1, S2 (as arc-noisy's truth files), two independent halves.
- arc_kprop: ARC's mlp_kprop (main at 93d091a) through the arc-noisy wrapper loop, sigma = 0, with ARC's own FLOP
  counter; optionally returns the K = 2 state (mean, covariance) at chosen layers.
- gauss_push: sample N(m, S) at layer l (PSD-clipped) and push through the exact layers l+1..L.
- rqmc: scrambled-Sobol RQMC (scipy LMS + digital shift scrambling, inverse normal), R replicates.
- k3_flat_stats: U-statistics for the third cumulant of a cloud: ||kappa_3||_F^2, its mode-1 flattening Gram
  K3 = kappa_(1) kappa_(1)^T (two independent unbiased estimates), participation ratio, held-out top-k energy and
  the multilinear top-k capture E[((P d).(P d'))^3] / E[(d.d')^3].
Cost convention: one forward pass = 2 n^2 L flops; ARC's methods are charged with ARC's own counter (as arc-noisy).
"""
import math, os, sys, time
import numpy as np
import torch

ARC_NOISY = '/home/agent/workspaces/mats/work/arc-noisy'
if ARC_NOISY not in sys.path:
    sys.path.insert(0, ARC_NOISY)
import anet                                   # noqa: E402
import kprop_noisy as KN                      # noqa: E402
from kprop_noisy import KH, NamedFlopCounter, flop_name, WICK_COEF_D   # noqa: E402

torch.set_num_threads(int(os.environ.get('AU_THREADS', '1')))


def weights(seed, n, L):
    return anet.make_weights(seed, n, L)


def pass_flops(n, L):
    return 2.0 * n * n * L


@torch.no_grad()
def forward(W, h, l0=0, l1=None, dtype=torch.float32, keep=None):
    """Push a batch h (m, n) of layer-l0 states through layers l0+1..l1 (1-based layer l uses W[l-1]).
    keep: optional set of layers whose states are returned in a dict (float64)."""
    l1 = len(W) if l1 is None else l1
    h = h.to(dtype)
    out = {}
    for l in range(l0, l1):
        h = torch.relu(h @ W[l].T.to(dtype))
        if keep is not None and (l + 1) in keep:
            out[l + 1] = h.double()
    return (h, out) if keep is not None else h


@torch.no_grad()
def mc_moments(W, N, seed, chunk=1 << 14, dtype=torch.float32):
    """Per-layer sums S1[l] = sum_x h_l, S2[l] = sum_x h_l^2 (l = 1..L) over N Gaussian inputs, in two independent
    halves (A: first N/2, B: second N/2). Returns dict with S1A, S1B, S2A, S2B (L, n) float64 and N."""
    n, L = W[0].shape[0], len(W)
    gen = torch.Generator().manual_seed(int(seed))
    S1 = np.zeros((2, L, n)); S2 = np.zeros((2, L, n))
    Wt = [w.T.to(dtype).contiguous() for w in W]
    done = 0
    while done < N:
        m = min(chunk, N - done)
        half = 0 if done < N // 2 else 1
        h = torch.randn(m, n, generator=gen, dtype=torch.float32).to(dtype)
        for l in range(L):
            h = torch.relu(h @ Wt[l])
            hd = h.double()
            S1[half, l] += hd.sum(0).numpy()
            S2[half, l] += (hd * hd).sum(0).numpy()
        done += m
    return dict(S1A=S1[0], S1B=S1[1], S2A=S2[0], S2B=S2[1], N=N)


def truth_from_moments(M):
    """Mean (L, n), per-neuron variance (L, n), half-means, from mc_moments output."""
    N = M['N']; h = N / 2
    S1 = M['S1A'] + M['S1B']; S2 = M['S2A'] + M['S2B']
    mean = S1 / N
    var = S2 / N - mean ** 2
    return dict(N=N, mean=mean, var=var, meanA=M['S1A'] / h, meanB=M['S1B'] / h)


def load_arc_truth(seed, n=256, L=32):
    """arc-noisy's noiseless truth (2^26 paths) for nets 200-204 at 256 x 32."""
    p = os.path.join(ARC_NOISY, 'truth', f'truth_{n}_{L}_s0_seed{seed}.npz')
    d = np.load(p)
    N = float(d['N'])
    mean = d['S1'] / N
    var = d['S2'] / N - mean ** 2
    W = weights(seed, n, L)
    chk = float(anet.weights_checksum(W)) if hasattr(anet, 'weights_checksum') else None
    return dict(N=N, mean=mean, var=var, chk_file=float(d['chk']), chk_now=chk)


def nmse(est, mean_true, var_true):
    """ARC convention: mean_j (est_j - mu_j)^2 / mean_j Var_j (= |est - mu|^2 / tr Var)."""
    est = np.asarray(est, dtype=float)
    return float(((est - mean_true) ** 2).sum() / var_true.sum())


@torch.no_grad()
def arc_kprop(W, k_max, factor=False, kind='simple', keep_states=(), avg_metric=True, count_flops=True,
              dtype=torch.float64):
    """ARC's cumulant propagation on weights W (sigma = 0), mirroring kprop_harmonic.mlp_kprop (as kprop_noisy).
    Returns dict(mean=final mean (n,), means=list per layer, flops, secs, states={l: (m, S)} for l in keep_states
    (K = 2 only: S = full covariance core))."""
    n, L = W[0].shape[0], len(W)
    net = anet.Net(0, n=n, L=L, sigma=0.0, W=W)
    kind_e = {'simple': KH.SIMPLE, 'augment': KH.AUGMENT}[kind]
    mlp = KN.arc_mlp(net, L, dtype)
    counter = NamedFlopCounter() if count_flops else None
    t0 = time.time(); means = []; states = {}
    if counter is not None:
        counter.__enter__()
    try:
        with flop_name('kprop'):
            K_in = {1: torch.zeros(n, dtype=dtype), 2: torch.eye(n, dtype=dtype)}
            K = KH.coerce_input(K_in, k_max=k_max, kind=kind_e)
            skip_metric = not KH.metric_needed(k_max, kind_e)
            for l in range(L):
                Wl = mlp.Ws[l].weight
                metric = mlp.init_scale[l] if avg_metric else (1.0 if skip_metric else None)
                K = KH.linear_kprop(K, Wl, k_max=k_max, set_metric=metric, bias=None)
                K = KH.nonlin_kprop(K, nonlin_wick_coef=WICK_COEF_D['relu'], k_max=k_max, kind=kind_e,
                                    use_pK=True, factor=factor)
                means.append(K[1].to_tensor().clone().numpy())
                if (l + 1) in keep_states:
                    S = K[2].to_tensor().clone().numpy() if 2 in K else None
                    states[l + 1] = (means[-1].copy(), S)
    finally:
        if counter is not None:
            counter.__exit__(None, None, None)
    return dict(mean=means[-1], means=means, flops=(counter.total() if counter is not None else None),
                secs=time.time() - t0, states=states)


def psd_sqrt(S):
    """Symmetric square root factor of the PSD part of S; returns (A, clipped_fraction) with S_+ = A A^T."""
    S = 0.5 * (S + S.T)
    ev, U = np.linalg.eigh(S)
    neg = ev < 0
    clip = float(-ev[neg].sum() / max(ev[~neg].sum(), 1e-300))
    ev = np.clip(ev, 0.0, None)
    return U * np.sqrt(ev)[None, :], clip


@torch.no_grad()
def gauss_push(W, m, S, l, N, seed, chunk=1 << 14, dtype=torch.float32):
    """E over h ~ N(m, S_+) at layer l of the exact output h_L (layers l+1..L). Returns (mean (n,), clip, half
    means A, B) with two independent halves for an unbiased squared-error cross product."""
    A, clip = psd_sqrt(S)
    n = len(m)
    gen = torch.Generator().manual_seed(int(seed))
    At = torch.from_numpy(A.T.copy()).to(dtype); mt = torch.from_numpy(np.asarray(m)).to(dtype)
    sums = np.zeros((2, n)); done = 0
    while done < N:
        k = min(chunk, N - done)
        half = 0 if done < N // 2 else 1
        z = torch.randn(k, n, generator=gen, dtype=torch.float32).to(dtype)
        h = z @ At + mt
        if l == 0:
            h = h  # input layer (no relu)
        out = forward(W, h, l0=l, l1=len(W), dtype=dtype)
        sums[half] += out.double().sum(0).numpy()
        done += k
    hN = N / 2
    return sums.sum(0) / N, clip, sums[0] / hN, sums[1] / hN


@torch.no_grad()
def true_cloud(W, l, N, seed, dtype=torch.float32):
    """N samples of the true layer-l state (float64 numpy, (N, n))."""
    n = W[0].shape[0]
    gen = torch.Generator().manual_seed(int(seed))
    x = torch.randn(N, n, generator=gen, dtype=torch.float32).to(dtype)
    h = forward(W, x, l0=0, l1=l, dtype=dtype) if l > 0 else x
    return h.double().numpy()


def rqmc(W, m_pow, R, seed, chunk=1 << 13, dtype=torch.float32):
    """R scrambled-Sobol replicates of N = 2^m_pow points mapped to N(0, I_n) by the inverse normal cdf; returns
    (R, n) replicate means of h_L."""
    from scipy.stats import qmc
    from scipy.special import ndtri
    n = W[0].shape[0]
    N = 1 << m_pow
    out = np.zeros((R, n))
    for r in range(R):
        eng = qmc.Sobol(d=n, scramble=True, seed=int(seed) * 1000 + r)
        s = np.zeros(n); done = 0
        while done < N:
            k = min(chunk, N - done)
            u = eng.random(k)
            u = np.clip(u, 1e-12, 1 - 1e-12)
            x = torch.from_numpy(ndtri(u)).to(dtype)
            s += forward(W, x, dtype=dtype).double().sum(0).numpy()
            done += k
        out[r] = s / N
    return out


def k3_flat_stats(X, mean, ks=(1, 2, 4, 8, 16, 32, 64), rng=None, tile=2048):
    """Third-cumulant statistics of a cloud from samples X (N, n) with known exact mean.
    Splits X into four disjoint blocks A1, B1, A2, B2. K3_hat^(i) = A_i^T [(A_i B_i^T)^2] B_i / (|A_i||B_i|) (then
    symmetrised) is unbiased for K3 = kappa_(1) kappa_(1)^T. Reports:
      fro2      = ||kappa_3||_F^2 (= tr K3; mean of the two estimates; also E[(d.d')^3] directly),
      pr        = (tr K3)^2 / tr(K3^2) with tr(K3^2) from the cross product tr(K^(1) K^(2)) (unbiased),
      topk_flat = held-out fraction of tr K3 in the top-k eigenvectors of K^(1), evaluated on K^(2),
      capk      = held-out multilinear capture E[((P d).(P d'))^3] / E[(d . d')^3] with P = top-k projector of K^(1),
                  evaluated on blocks A2, B2 (the Frobenius energy of kappa_3 x_1 P x_2 P x_3 P).
    Computed in row tiles of A (same estimator as the untiled version; tests/test_au.py checks equality)."""
    D = X - mean[None, :]
    N = D.shape[0]; q = N // 4
    A1, B1, A2, B2 = D[:q], D[q:2 * q], D[2 * q:3 * q], D[3 * q:4 * q]

    def khat(A, B):
        K = np.zeros((A.shape[1], A.shape[1])); f = 0.0
        for i in range(0, A.shape[0], tile):
            At = A[i:i + tile]
            G = At @ B.T
            K += At.T @ ((G * G) @ B)
            f += float((G ** 3).sum())
        K /= (A.shape[0] * B.shape[0])
        return 0.5 * (K + K.T), f / (A.shape[0] * B.shape[0])

    K1, f1 = khat(A1, B1)
    K2, f2 = khat(A2, B2)
    tr1, tr2 = float(np.trace(K1)), float(np.trace(K2))
    trK2 = float(np.sum(K1 * K2))
    fro2 = 0.5 * (tr1 + tr2)
    pr = fro2 ** 2 / trK2 if trK2 > 0 else float('nan')
    ev, U = np.linalg.eigh(K1)
    U = U[:, ::-1]
    topk, capk = {}, {}
    kmax = max(ks)
    PA_all, PB_all = A2 @ U[:, :kmax], B2 @ U[:, :kmax]
    num = {k: 0.0 for k in ks}
    for i in range(0, A2.shape[0], tile):
        for k in ks:
            Gk = PA_all[i:i + tile, :k] @ PB_all[:, :k].T
            num[k] += float((Gk ** 3).sum())
    den = f2 * (A2.shape[0] * B2.shape[0])
    for k in ks:
        Uk = U[:, :k]
        topk[k] = float(np.sum((Uk.T @ K2) * Uk.T) / tr2) if tr2 != 0 else float('nan')
        capk[k] = float(num[k] / den) if den != 0 else float('nan')
    return dict(fro2=fro2, fro2_direct=0.5 * (f1 + f2), pr=pr, topk_flat=topk, capk=capk, tr1=tr1, tr2=tr2,
                trK2=trK2, N=N)
