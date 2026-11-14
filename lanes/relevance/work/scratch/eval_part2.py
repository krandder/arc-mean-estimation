"""PREREG Part 2 runner: gate counts G(l, eps), N_>=2 along the nonlinear active subspace, unbiased N_1, on the
evaluation nets of Part 1 (subset of layers), plus synchronisation-depth runs (input regime, L >> n).
Usage:
  python eval_part2.py arc seed            (layers 8, 16, 24, 31; P = 2048)
  python eval_part2.py stat n seed s_list  (P = 2048)
  python eval_part2.py sync n L seed       (input regime, layers on a grid to L; radial true-law residual only)
"""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel, gates, accounting as acc

BASE = '/home/agent/workspaces/mats/work/relevance/'


def cell(fut, X, rng, P):
    fr = rel.gaussian_frame(X[: len(X) // 2])
    Xg1, _ = rel.gaussian_sample(fr, P, rng)
    Xg2, _ = rel.gaussian_sample(fr, P, rng)
    V = rel.v_l(fut, Xg1, Xg2, rng)
    ks = acc.kgrid(fut.n)
    gc = gates.gate_count(fut, fr, P, rng)
    nl = gates.nonlinear_part_counts(fut, fr, P, rng, ks)
    n1 = gates.n1_split(fut, fr, P, rng, ks)
    return dict(V_gauss=[float(V[0]), float(V[1])], gates=gc, nl=nl, n1=n1, n=fut.n, t=fut.t, sigma=fut.sigma)


def main():
    mode = sys.argv[1]
    outs = []
    if mode == 'arc':
        seed = int(sys.argv[2])
        rng = np.random.default_rng([4242, seed, 1])
        Ws = rel.input_weights(seed, 256, 32)
        name = f'runs/p2_arc_seed{seed}.json'
        for l in [8, 16, 24, 31]:
            t0 = time.time()
            X, _ = rel.input_cloud(Ws, l, 8192, rng)
            o = cell(rel.Future(Ws[l:], 0.0), X, rng, 2048)
            o.update(mode='arc', seed=seed, l=l)
            outs.append(o)
            json.dump(outs, open(BASE + name, 'w'), default=float)
            print(f'arc {seed} l {l} {time.time() - t0:.0f}s', flush=True)
    elif mode == 'stat':
        n, seed = int(sys.argv[2]), int(sys.argv[3])
        ss = [int(x) for x in sys.argv[4].split(',')]
        rng = np.random.default_rng([4242, seed, n, 3])
        cl = rel.stationary_clouds(seed, n, ss, 8192, rng, chunk=8192)
        name = f'runs/p2_stat_n{n}_seed{seed}.json'
        for s in sorted(ss):
            t0 = time.time()
            o = cell(rel.stationary_future(seed, n, s), cl[s], rng, 2048)
            o.update(mode='stat', seed=seed, s=s)
            outs.append(o)
            json.dump(outs, open(BASE + name, 'w'), default=float)
            print(f'stat {n} {seed} s {s} {time.time() - t0:.0f}s', flush=True)
    else:
        n, L, seed = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        rng = np.random.default_rng([4242, seed, n, L, 5])
        Ws = rel.input_weights(seed, n, L)
        name = f'runs/p2_sync_n{n}_L{L}_seed{seed}.json'
        grid = sorted(set([1, 2, 4] + list(range(n // 2, L, max(1, n // 4)))))
        P = 4096
        x = rng.standard_normal((2 * P, n))
        h = x
        lprev = 0
        for l in grid:
            for k in range(lprev, l):
                h = np.maximum(h @ Ws[k].T, 0.0)
            lprev = l
            fut = rel.Future(Ws[l:], 0.0)
            fr = rel.gaussian_frame(h[:P])
            Xe = h[P:]
            m = fr['m']
            e = m / np.linalg.norm(m)
            wdir = fr['S12'] @ e
            wdir /= np.linalg.norm(wdir)
            Q, _ = np.linalg.qr(np.concatenate([wdir[:, None], rng.standard_normal((n, n - 1))], 1))
            if Q[:, 0] @ wdir < 0:
                Q[:, 0] *= -1
            rr = rel.subspace_residuals(fut, fr, Q, [0, 1], P, rng, true_X=Xe)
            A, B = Xe[: P // 2], Xe[P // 2:]
            Vt = rel.v_l(fut, A, B, rng)
            nA, nB = np.linalg.norm(A, axis=1), np.linalg.norm(B, axis=1)
            ok = (nA > 0) & (nB > 0)
            c0 = float(np.mean(np.einsum('pi,pi->p', A[ok], B[ok]) / nA[ok] / nB[ok]))
            # number of differing gates per layer between independent inputs at layer l+1
            zA, zB = A @ Ws[l].T, B @ Ws[l].T
            ham = float(np.mean(np.sum((zA > 0) != (zB > 0), 1)))
            outs.append(dict(l=l, n=n, L=L, seed=seed, V_true=[float(Vt[0]), float(Vt[1])],
                             res_radial_true=[float(v) for v in rr['true'][1]], mean_cos=c0, hamming_next=ham,
                             dead_frac=float(np.mean(np.all(Xe == 0, axis=1)))))
            json.dump(outs, open(BASE + name, 'w'), default=float)
            print(f'sync n {n} L {L} seed {seed} l {l} c0 {c0:.5f} rad {rr["true"][1][0] / max(Vt[0], 1e-300):.2e} ham {ham}', flush=True)


if __name__ == '__main__':
    main()
