"""Exact annealed three-replica chain for the frozen-gate and radial merge residuals at finite width.

Replicas sharing the future weights W_{l+1..L}: the true state h, the reference c, and the frozen vector v (h propagated
with c's gates). Given the 3 x 3 Gram matrix G of (h, c, v) at a layer, the next layer's rows w_i are iid
N(0, (2/n) I) and independent of the past, so the pre-activation triples z_i = (w_i.h, w_i.c, w_i.v) are iid
N(0, (2/n) G) over the n units, and
    h' = relu(z_h),  c' = relu(z_c),  v' = 1{z_c > 0} z_v,   G'_{ab} = sum_i s_a,i s_b,i.
This is exact in law (the weights are integrated out one layer at a time; the gram-chain lane's argument with a
tangent-type replica). Residuals at the output: frozen |h - v|^2, radial |h - (|h_0|/|c_0|) c|^2.
"""
import numpy as np


def run(n, Lp, phi, chains, rng, ratio=1.0):
    """Simulate `chains` independent futures of Lp layers for a pair at angle phi with |h|/|c| = ratio.
    Returns dict of arrays (per chain): frozen = |h_L - v_L|^2 / |h_L|^2, radial = |h_L - r c_L|^2 / |h_L|^2,
    and the raw Gram at the end."""
    G = np.zeros((chains, 3, 3))
    h2 = ratio ** 2
    hc = ratio * np.cos(phi)
    G[:, 0, 0] = h2
    G[:, 1, 1] = 1.0
    G[:, 2, 2] = h2
    G[:, 0, 1] = G[:, 1, 0] = hc
    G[:, 0, 2] = G[:, 2, 0] = h2
    G[:, 1, 2] = G[:, 2, 1] = hc
    for _ in range(Lp):
        # Cholesky of (2/n) G per chain (G is PSD; add jitter for the degenerate start where h = v)
        C = (2.0 / n) * G + 1e-15 * np.eye(3)[None, :, :] * np.maximum(G[:, 0, 0], 1e-300)[:, None, None]
        Lc = np.linalg.cholesky(C)
        Z = rng.standard_normal((chains, n, 3)) @ np.transpose(Lc, (0, 2, 1))
        zh, zc, zv = Z[..., 0], Z[..., 1], Z[..., 2]
        S = np.stack([np.maximum(zh, 0.0), np.maximum(zc, 0.0), np.where(zc > 0, zv, 0.0)], axis=-1)
        G = np.einsum('kia,kib->kab', S, S)
        # renormalise the overall scale (homogeneity) to avoid under/overflow; ratios are invariant
        s = np.maximum(G[:, 1, 1], 1e-300)
        G = G / s[:, None, None]
    hh, cc, vv = G[:, 0, 0], G[:, 1, 1], G[:, 2, 2]
    hc_, hv = G[:, 0, 1], G[:, 0, 2]
    frozen = (hh + vv - 2 * hv) / np.maximum(hh, 1e-300)
    radial = (hh + ratio ** 2 * cc - 2 * ratio * hc_) / np.maximum(hh, 1e-300)
    return {'frozen': frozen, 'radial': radial, 'G': G}


if __name__ == '__main__':
    rng = np.random.default_rng(1)
    for n in [64, 128, 1024]:
        for Lp in [1, 16]:
            for phi in [0.01, 0.1]:
                r = run(n, Lp, phi, 4000, rng)
                print(n, Lp, phi, 'frozen mean', r['frozen'].mean(), 'median', np.median(r['frozen']),
                      'MF-1layer', (2 / np.pi) * (phi - np.sin(phi) * np.cos(phi)) * (Lp if Lp == 1 else np.nan),
                      'radial mean', r['radial'].mean())
