"""Dev exploration (dev nets only, seeds >= 9100): relevance accounting at several layers, both regimes.

Usage:
  python dev_explore.py input n L seed layers(comma) P
  python dev_explore.py stat n s_list(comma) seed P
Writes runs/dev_<regime>_n<n>_..._seed<seed>.json and prints a table.
"""
import json
import math
import sys
import time

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402


def kgrid(n):
    ks = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
    return [k for k in ks if k <= n]


def theory_s1(theta, t):
    rho = np.linspace(0, 1, 2001)
    Jr = rel.jacobian_overlap_annealed(theta, t, rho, exact=True)
    V = np.trapezoid(Jr, rho)
    small = 1.0 / (1 + theta * t / (3 * math.pi))
    return dict(s1_exact_kernel=float(Jr[0] / V), D_exact_kernel=float(1.0 / V), s1_small=small,
                D_small=(1 + theta * t / (3 * math.pi)) ** 2)


def analyse(fut, Xtrue, rng, P, label):
    t0 = time.time()
    n = Xtrue.shape[1]
    Pc = Xtrue.shape[0]
    fr = rel.gaussian_frame(Xtrue[: Pc // 2])
    Xe = Xtrue[Pc // 2:]
    m = fr['m']
    e = m / np.linalg.norm(m)
    trS = float(np.trace(fr['C']))
    rad = float(e @ fr['C'] @ e)
    # angles between independent true samples
    A, B = Xe[: len(Xe) // 2], Xe[len(Xe) // 2: 2 * (len(Xe) // 2)]
    cosab = np.einsum('pi,pi->p', A, B) / np.linalg.norm(A, axis=1) / np.linalg.norm(B, axis=1)
    theta_pair = float(np.mean(np.arccos(np.clip(cosab, -1, 1))))
    theta_S = math.sqrt(2 * (trS - rad) / (m @ m))
    ev = fr['evals']
    pr = float(ev.sum() ** 2 / np.sum(ev ** 2))
    out = dict(label=label, n=n, t=fut.t, trSigma=trS, radial_var=rad, m2=float(m @ m), theta_pair=theta_pair,
               theta_Sigma=theta_S, cloud_PR=pr)
    # V_l true and Gaussian
    Pv = min(P, len(A))
    out['V_true'] = rel.v_l(fut, A[:Pv], B[:Pv], rng)
    Xg1, Z1 = rel.gaussian_sample(fr, P, rng)
    Xg2, _ = rel.gaussian_sample(fr, P, rng)
    out['V_gauss'] = rel.v_l(fut, Xg1, Xg2, rng)
    if fut.sigma > 0:
        out['totvar_true'] = rel.total_var(fut, A[:Pv], B[:Pv], rng)
    # means: true vs Gaussian
    a_t = fut.forward(np.stack([Xe[:P]]), rng)[0].mean(0)
    a_g = fut.forward(np.stack([Xg1]), rng)[0].mean(0)
    out['mean_gap_nmse'] = float(np.sum((a_t - a_g) ** 2) / out['V_true'][0])
    # degree-1 (Stein) shares
    V1g, se1g, Bg = rel.stein_linear(fut, Xg1, Z1, rng)
    Zt = (Xe[:P] - m) @ fr['Sm12']
    V1t, se1t, Bt = rel.stein_linear(fut, Xe[:P], Zt, rng)
    out['V1_gauss'] = (V1g, se1g)
    out['V1_true'] = (V1t, se1t)
    # gradient energy and Mehler curve (Gaussian)
    out['J1_gauss'] = rel.gradient_energy(fut, fr, P, rng)
    rhos = [-0.5, 0.0, 0.5, 0.8, 0.95]
    mc = rel.mehler_curve(fut, fr, rhos, P, rng)
    out['mehler_D'] = {str(r): mc[r] for r in rhos}
    # frozen-gate linear part at the mean and the exact identity (true law and Gaussian)
    out['parts_true'] = {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                         for k, v in rel.parts_shares(fut, Xe[:P], m, rng).items()}
    out['parts_gauss'] = {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                          for k, v in rel.parts_shares(fut, Xg1, m, rng).items()}
    # active subspace and residuals
    C, w, U = rel.active_subspace(fut, fr, P, rng, q=4)
    out['AS_evals'] = w[: min(64, n)].tolist()
    out['AS_trace'] = float(w.sum())
    ks = kgrid(n)
    res = rel.subspace_residuals(fut, fr, U, ks, P, rng, true_X=Xe[:P])
    out['res_AS_gauss'] = {str(k): res['gauss'][k] for k in ks}
    out['res_AS_true'] = {str(k): res['true'][k] for k in ks}
    # degree-1 relevance spectrum and its own basis; cloud PCA basis
    M1 = Bg.T @ Bg
    w1, U1 = np.linalg.eigh(M1)
    out['R1_evals'] = w1[::-1][: min(64, n)].tolist()
    res1 = rel.subspace_residuals(fut, fr, U1[:, ::-1], ks, P, rng)
    out['res_R1_gauss'] = {str(k): res1['gauss'][k] for k in ks}
    # cloud PCA order: in whitened coordinates the eigenvectors of Sigma (columns of evecs, eigenvalue descending)
    resp = rel.subspace_residuals(fut, fr, fr['evecs'], ks, P, rng)
    out['res_PCA_gauss'] = {str(k): resp['gauss'][k] for k in ks}
    out['theory'] = theory_s1(theta_pair, fut.t)
    out['seconds'] = time.time() - t0
    return out


def summary(o):
    V = o['V_gauss'][0]
    Vt = o['V_true'][0]
    s1 = o['V1_gauss'][0] / V
    s1t = o['V1_true'][0] / Vt
    D = o['J1_gauss'][0] / V
    pt = o['parts_true']
    lin_ratio = pt['V_lin'] / pt['V_da']
    fo_g = pt['V_fo_gate'] / pt['V_da']
    inter = pt['V_inter'] / pt['V_da']
    res = o['res_AS_gauss']

    def Nk(eps, r):
        for k in sorted(r, key=lambda s: int(s)):
            if r[k][0] <= eps * V:
                return int(k)
        return None
    Ns = [Nk(e, res) for e in (0.1, 0.01, 0.001)]
    th = o['theory']
    return (f"{o['label']:>14} t={o['t']:4d} th={o['theta_pair']:.3f} V_t/V_g={Vt / V:.3f} s1_g={s1:.3f} s1_t={s1t:.3f} "
            f"pred(s1 ex/sm)={th['s1_exact_kernel']:.3f}/{th['s1_small']:.3f} D={D:.2f} predD={th['D_exact_kernel']:.2f} "
            f"lin(J^m)/V={lin_ratio:.2f} fo_gate={fo_g:.2f} inter={inter:.2f} N(.1,.01,.001)={Ns} PR={o['cloud_PR']:.1f} "
            f"[{o['seconds']:.0f}s]")


def main():
    regime = sys.argv[1]
    rng = np.random.default_rng(12345)
    outs = []
    if regime == 'input':
        n, L, seed = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        layers = [int(x) for x in sys.argv[5].split(',')]
        P = int(sys.argv[6])
        Ws = rel.input_weights(seed, n, L)
        for l in layers:
            fut = rel.Future(Ws[l:], 0.0)
            X, _ = rel.input_cloud(Ws, l, 4 * P, rng)
            o = analyse(fut, X, rng, P, f'in l={l}')
            outs.append(o)
            print(summary(o), flush=True)
        name = f'runs/dev_input_n{n}_L{L}_seed{seed}.json'
    else:
        n, seed = int(sys.argv[2]), int(sys.argv[4])
        ss = [int(x) for x in sys.argv[3].split(',')]
        P = int(sys.argv[5])
        for s in ss:
            fut = rel.stationary_future(seed, n, s)
            X = rel.stationary_cloud(seed, n, s, 4 * P, rng)
            o = analyse(fut, X, rng, P, f'st s={s}')
            outs.append(o)
            print(summary(o), flush=True)
        name = f'runs/dev_stat_n{n}_seed{seed}.json'
    with open('/home/agent/workspaces/mats/work/relevance/' + name, 'w') as f:
        json.dump(outs, f)


if __name__ == '__main__':
    main()
