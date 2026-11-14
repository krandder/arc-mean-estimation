"""Part B (PREREG Part B): relevance at layer l from the exact chain. Output observable: the output direction
u = a/|a|, a = relu(W_L h_{L-1}) (one exact sample of the noiseless output layer per recorded t), plus log|a|.
usage: partB.py MODE n [--P P] [--tmax T]
MODE curves (sigma = 1): R = 3 chain. A, B independent and stationary (8n burn-in from the stationary radius); at t = 0
    C := copy of A; afterwards A and B share noise (total relevance T_P(t) from pair A-B), C has independent noise
    (closed relevance V_P(t) = 1 - E|uA - uC|^2 / E|uA - uB|^2_(t=0)). Records at t = 1..tmax (t = layers to go,
    counting the output layer: the output layer is applied after t - 1 further noisy layers).
MODE pr (sigma = 1): R = 8 chain. A1..A4 independent and stationary; at t = 0 copies B_k := A_k; afterwards the A's share
    one noise stream and the B's another. Total PR(t) = E[|xA12|^2 |xA34|^2] / E[(xA12.xA34)^2];
    closed PR(t) = E[(xA12.xB12)(xA34.xB34)] / E[(xA12.xA34)(xB12.xB34)]; x = differences of output directions.
MODE pert (sigma = 1): R = 3 chain per eps: A stationary, B = A + eps u, C = A + eps v (u, v orthonormal, orthogonal to
    A, |u| = |A|), shared noise; records E|uA - uB|^2 (hidden direction, exact closed form) and the response PR
    E|dB|^2|dC|^2 / E(dB.dC)^2 at the output.
MODE input: sigma = 0 (and sigma > 0 via --sigma), replicas = 4 independent Gaussian inputs, depth L = --L: per layer
    the direction-cloud moments (x = uA1 - uA2, y = uA3 - uA4), log radii; at the output log|a|.
Output: runs/B_<mode>_n<n>[...].json"""
import sys, os, math, json, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import numpy as np
import gc2

ap = argparse.ArgumentParser()
ap.add_argument('mode')
ap.add_argument('n', type=int)
ap.add_argument('--P', type=int, default=None)
ap.add_argument('--tmax', type=int, default=None)
ap.add_argument('--L', type=int, default=32)
ap.add_argument('--sigma', type=float, default=0.0)
ap.add_argument('--tag', default='')
a = ap.parse_args()
n, mode = a.n, a.mode
mode_id = dict(curves=11, pr=12, pert=13, input=14, inputVP=15)[mode]
rng = np.random.default_rng([2027, n, mode_id, int(a.L), int(round(1e6 * a.sigma))])
t0 = time.time()
RUNS = '/home/agent/workspaces/mats/work/gram-chain/runs/'
res = dict(mode=mode, n=n)


def out_dirs(G, idx):
    """One exact sample of the noiseless output layer for the replicas idx; returns (cos matrix, log|a|)."""
    Go = gc2.step(G[:, idx][:, :, idx], n, rng, out=True)
    d = np.sqrt(np.maximum(np.einsum('pii->pi', Go), 1e-300))
    return Go / (d[:, :, None] * d[:, None, :]), np.log(d)


def tgrid(tmax):
    g = sorted(set([1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160, 192, 256, 320, 384, 512,
                    640, 768, 1024, 1280, 1536, 2048, 2560, 3072, 4096]))
    return [t for t in g if t <= tmax]


if mode == 'curves':
    P = a.P or (8000 if n <= 64 else (4000 if n <= 256 else 1000))
    tmax = a.tmax or 4 * n
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    G2 = gc2.init_identical(Q0, 2)
    for _ in range(8 * n):
        G2 = gc2.step(G2, n, rng)
    C0, L0 = out_dirs(G2, [0, 1])
    den_u = np.mean(2 * (1 - C0[:, 0, 1]))
    den_l = np.mean((L0[:, 0] - L0[:, 1]) ** 2)
    G = np.zeros((P, 3, 3))
    G[:, :2, :2] = G2
    G[:, 2, :] = G[:, 0, :]
    G[:, :, 2] = G[:, :, 0]
    G[:, 2, 2] = G[:, 0, 0]
    lab = np.array([0, 0, 1])
    grid = set(tgrid(tmax))
    rows = []
    for t in range(1, tmax + 1):
        if t in grid:
            Cc, Lc = out_dirs(G, [0, 1, 2])
            dAB, dAC = 2 * (1 - Cc[:, 0, 1]), 2 * (1 - Cc[:, 0, 2])
            lAB, lAC = (Lc[:, 0] - Lc[:, 1]) ** 2, (Lc[:, 0] - Lc[:, 2]) ** 2
            B = 100
            idx = rng.integers(0, P, (B, P))
            rows.append(dict(t=t, T_P=float(dAB.mean() / den_u), V_P=float(1 - dAC.mean() / den_u),
                             T_P_se=float(np.std([dAB[i].mean() / den_u for i in idx])),
                             V_P_se=float(np.std([dAC[i].mean() / den_u for i in idx])),
                             T_P_log=float(lAB.mean() / den_l), V_P_log=float(1 - lAC.mean() / den_l)))
        G = gc2.step(G, n, rng, labels=lab)
    res.update(P=P, den_u=float(den_u), den_log=float(den_l), rows=rows,
               Qmed_over_n=float(np.median(Q0) / n))
elif mode == 'pr':
    P = a.P or (4000 if n <= 64 else (2000 if n <= 256 else 600))
    tmax = a.tmax or min(4 * n, 256)
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    G4 = gc2.init_identical(Q0, 4)
    for _ in range(6 * n):
        G4 = gc2.step(G4, n, rng)
    G = np.zeros((P, 8, 8))
    G[:, :4, :4] = G4
    G[:, 4:, 4:] = G4
    G[:, :4, 4:] = G4
    G[:, 4:, :4] = G4
    lab = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    grid = set(tgrid(tmax))
    rows = []
    for t in range(1, tmax + 1):
        if t in grid:
            Cc, _ = out_dirs(G, list(range(8)))
            x = lambda p, q: Cc[:, p[0], q[0]] - Cc[:, p[0], q[1]] - Cc[:, p[1], q[0]] + Cc[:, p[1], q[1]]
            A12, A34, B12, B34 = (0, 1), (2, 3), (4, 5), (6, 7)
            xa11, xa22, xa12 = x(A12, A12), x(A34, A34), x(A12, A34)
            xb12 = x(B12, B34)
            xab1, xab2 = x(A12, B12), x(A34, B34)
            num_tot, den_tot = np.mean(xa11 * xa22), np.mean(xa12 ** 2)
            num_cl, den_cl = np.mean(xab1 * xab2), np.mean(xa12 * xb12)
            B = 100
            idx = rng.integers(0, P, (B, P))
            rows.append(dict(t=t, PR_tot=float(num_tot / den_tot), PR_tot_rom=float(np.mean(xa11) ** 2 / den_tot),
                             PR_closed=float(num_cl / den_cl) if den_cl > 0 else None,
                             trC_closed=float(np.mean(xab1) / 2), trC_tot=float(np.mean(xa11) / 2),
                             PR_tot_se=float(np.std([np.mean(xa11[i] * xa22[i]) / np.mean(xa12[i] ** 2) for i in idx])),
                             PR_closed_se=float(np.std([np.mean(xab1[i] * xab2[i]) / np.mean(xa12[i] * xb12[i])
                                                        for i in idx]))))
            print(rows[-1], '%.0fs' % (time.time() - t0), flush=True)
        G = gc2.step(G, n, rng, labels=lab)
    res.update(P=P, rows=rows)
elif mode == 'pert':
    P = a.P or (4000 if n <= 64 else (2000 if n <= 256 else 600))
    tmax = a.tmax or 2 * n
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    out = []
    for eps in (1e-3, 1e-2, 0.1, 0.3):
        G = gc2.surgery_perturb(Q0[:, None, None], 0, eps, n_new=2)
        lab = np.array([0, 0, 0])
        grid = set(tgrid(tmax))
        rows = []
        for t in range(0, tmax + 1):
            if t in grid or t == 0:
                d = gc2.diffs(G, n, 0, 1, out_closed=False)
                Cc, _ = out_dirs(G, [0, 1, 2])
                dB = 2 * (1 - Cc[:, 0, 1])
                dC = 2 * (1 - Cc[:, 0, 2])
                dBC = Cc[:, 1, 2] - Cc[:, 0, 1] - Cc[:, 0, 2] + 1.0
                rows.append(dict(t=t, delta_hidden=float(d['delta'].mean()), out_dsq=float(dB.mean()),
                                 PR_resp=float(np.mean(dB * dC) / np.mean(dBC ** 2))))
            G = gc2.step(G, n, rng, labels=lab)
        out.append(dict(eps=eps, rows=rows))
        print(eps, rows[:3], '%.0fs' % (time.time() - t0), flush=True)
    res.update(P=P, runs=out)
elif mode == 'input':
    L, sig = a.L, a.sigma
    P = a.P or (4000 if n <= 64 else 2000)
    G = gc2.wishart_inputs(n, P, 4, rng)
    rows = []
    LR = np.zeros((L, P, 4))
    for l in range(0, L):
        if l > 0:
            G = gc2.step(G, n, rng, sigma=sig)
        gdiag = np.einsum('pii->pi', G)
        d = np.sqrt(np.maximum(gdiag, 1e-300))
        LR[l] = np.log(d)
        alive = np.all(gdiag > 0, 1)  # bug fix 21:30Z: was d > 0 (always true after the 1e-300 floor)
        C = G / (d[:, :, None] * d[:, None, :] + 1e-300)
        x = lambda p, q: C[:, p[0], q[0]] - C[:, p[0], q[1]] - C[:, p[1], q[0]] + C[:, p[1], q[1]]
        xa, xb, xab = x((0, 1), (0, 1)), x((2, 3), (2, 3)), x((0, 1), (2, 3))
        m = alive
        lr = np.log(d[m])
        rows.append(dict(l=l, alive=float(alive.mean()), alive_rep=float((gdiag > 0).mean()), PR_4rep=float(np.mean(xa[m] * xb[m]) / np.mean(xab[m] ** 2)),
                         PR_rom=float(np.mean(xa[m]) ** 2 / np.mean(xab[m] ** 2)), ang=float(np.mean(xa[m]) / 2),
                         var_logr_within=float(np.mean((lr[:, 0] - lr[:, 1]) ** 2) / 2)))
    Co, Lo = out_dirs(G, [0, 1, 2, 3])
    ok = (Lo[:, 0] > -300) & (Lo[:, 1] > -300) & np.all(LR[:, :, :2] > -300, axis=(0, 2))
    dla = (Lo[:, 0] - Lo[:, 1])[ok]
    att = []
    for l in range(L):
        dlr = (LR[l, :, 0] - LR[l, :, 1])[ok]
        att.append(dict(l=l, V_logr=float(np.mean(dlr ** 2) / 2), V_logA=float(np.mean((dla - dlr) ** 2) / 2),
                        cov=float(np.mean(dlr * (dla - dlr)) / 2)))
    res.update(P=P, L=L, sigma=sig, rows=rows, attribution=att, frac_pairs_alive=float(ok.mean()),
               out_dir_var=float(np.mean(2 * (1 - Co[:, 0, 1])) / 2), out_log_var=float(np.mean(dla ** 2) / 2))
elif mode == 'inputVP':
    # Closed relevance of the layer-l state in the input regime with small noise (added 21:45Z, descriptive):
    # A (input x), B (independent input x'), copies C_k of A that share A's input and noise up to layer l_k and have
    # independent noise afterwards. V_P(l_k) = 1 - E|a_A - a_Ck|^2 / E|a_A - a_B|^2 (raw a and output direction).
    L, sig = a.L, a.sigma
    P = a.P or 2000
    lks = sorted(set([0, L // 8, L // 4, L // 2, (3 * L) // 4, L - 2]))
    K = len(lks)
    R = 2 + K
    G2 = gc2.wishart_inputs(n, P, 2, rng)
    G = np.zeros((P, R, R))
    idx = [0, 1] + [0] * K
    G[:] = G2[:, idx][:, :, idx]
    for l in range(1, L):
        lab = np.array([0, 1] + [0 if l <= lk else 2 + k for k, lk in enumerate(lks)])
        G = gc2.step(G, n, rng, sigma=sig, labels=lab)
    Go = gc2.step(G, n, rng, out=True)
    dg = np.sqrt(np.maximum(np.einsum('pii->pi', Go), 1e-300))
    Cc = Go / (dg[:, :, None] * dg[:, None, :])
    raw = lambda i, j: n * (Go[:, i, i] + Go[:, j, j] - 2 * Go[:, i, j])
    dirv = lambda i, j: 2 * (1 - Cc[:, i, j])
    den_raw, den_dir = raw(0, 1).mean(), dirv(0, 1).mean()
    rows = []
    for k, lk in enumerate(lks):
        rows.append(dict(l=lk, V_P_raw=float(1 - raw(0, 2 + k).mean() / den_raw), V_P_dir=float(1 - dirv(0, 2 + k).mean() / den_dir)))
    res.update(P=P, L=L, sigma=sig, rows=rows, den_raw=float(den_raw), den_dir=float(den_dir))
res['sec'] = time.time() - t0
fn = RUNS + 'B_%s_n%d%s%s.json' % (mode, n, ('_L%d_s%g' % (a.L, a.sigma)) if mode in ('input', 'inputVP') else '', a.tag)
json.dump(res, open(fn, 'w'), indent=1)
print('done', mode, n, '%.0fs' % (time.time() - t0), flush=True)
