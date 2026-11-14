"""Part A (PREREG Part A): stationary law of the normalised replica Gram, exact chain, sigma = 1.
usage: partA.py MODE n [--P P]
MODE r2: R = 2 independent; samples of (q, delta, ell) every n/8 layers over 8n recorded layers after 8n burn-in, plus
         contiguous traces (every layer, 4n layers, 200 chains) for autocorrelations.
MODE share: R = 2 under several sharing rules (Gaussian correlation, per-coordinate Bernoulli, per-layer Bernoulli,
         antithetic, independent); E delta over 4n recorded layers after 2n burn-in (each replica's radius is stationary
         from the start).
MODE r3 / r4 / r6: R independent replicas; direction-cloud statistics (angles; tr C_u^m moments, raw and normalised by
         delta*_MF(q-bar)^m per chain).
Output: runs/A_<mode>_n<n>.json and .npz (per-sample arrays with chain index)."""
import sys, os, math, json, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import numpy as np
import gc2

ap = argparse.ArgumentParser()
ap.add_argument('mode')
ap.add_argument('n', type=int)
ap.add_argument('--P', type=int, default=None)
a = ap.parse_args()
n, mode = a.n, a.mode
P_default = 8000 if n <= 64 else (4000 if n <= 128 else (2000 if n <= 256 else (1000 if n <= 512 else 500)))
P = a.P if a.P is not None else P_default
mode_id = dict(r2=1, share=2, r3=3, r4=4, r6=6)[mode]
rng = np.random.default_rng([2026, n, mode_id])
t0 = time.time()
OUT = '/home/agent/workspaces/mats/work/gram-chain/runs/A_%s_n%d' % (mode, n)
res = dict(mode=mode, n=n, P=P)


def corr(G):
    d = np.sqrt(np.einsum('pii->pi', G))
    return G / (d[:, :, None] * d[:, None, :]), d * d / n


if mode == 'r2':
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    G = gc2.init_identical(Q0, 2)
    B, T, every = 8 * n, 8 * n, max(1, n // 8)
    for _ in range(B):
        G = gc2.step(G, n, rng)
    NT = min(200, P)
    tr = dict(q=np.zeros((4 * n, NT)), delta=np.zeros((4 * n, NT)), ell=np.zeros((4 * n, NT)))
    S = dict(q=[], delta=[], ell=[], chain=[])
    for t in range(T):
        G = gc2.step(G, n, rng)
        d = gc2.diffs(G, n, out_closed=False)
        q = np.sqrt(G[:, 0, 0] * G[:, 1, 1]) / n
        if t < 4 * n:
            tr['q'][t], tr['delta'][t], tr['ell'][t] = q[:NT], d['delta'][:NT], d['ell'][:NT]
        if t % every == every - 1:
            S['q'].append(q); S['delta'].append(d['delta']); S['ell'].append(d['ell'])
            S['chain'].append(np.arange(P))
    S = {k: np.concatenate(v) for k, v in S.items()}
    S['dstar'] = gc2.mf_fixed_point(S['q'] * n)
    np.savez_compressed(OUT + '.npz', **{k: v.astype(np.float64) for k, v in S.items()},
                        tr_q=tr['q'], tr_delta=tr['delta'], tr_ell=tr['ell'])
    r = S['delta'] / S['dstar']
    res.update(E_delta=float(S['delta'].mean()), median_ratio=float(np.median(r)), mean_ratio=float(r.mean()),
               sd_ratio_n13=float(r.std() * n ** (1 / 3)), sd_ell_n13=float(S['ell'].std() * n ** (1 / 3)),
               q_quantiles=[float(np.quantile(S['q'], p)) for p in (0.1, 0.5, 0.9)])
elif mode == 'share':
    cfgs = [('indep', 0.0)]
    ts = [0.25, 0.5, 0.75, 0.9, 0.97, 0.99] if n <= 256 else [0.25, 0.5, 0.75, 0.97]
    for kind in ('corr', 'coord', 'block'):
        cfgs += [(kind, t) for t in ts]
    cfgs.append(('corr', -1.0))
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    out = []
    for kind, t in cfgs:
        G = gc2.init_identical(Q0, 2)
        acc = np.zeros(P)
        cnt = 0
        for s in range(6 * n):
            if kind == 'indep':
                G = gc2.step(G, n, rng)
            elif kind == 'corr':
                G = gc2.step(G, n, rng, S=np.array([[1.0, t], [t, 1.0]]))
            elif kind == 'coord':
                G = gc2.step(G, n, rng, coord=[(0, 1, t)])
            else:
                lab = np.zeros((P, 2), int)
                lab[:, 1] = (rng.random(P) >= t).astype(int)
                G = gc2.step(G, n, rng, labels=lab)
            if s >= 2 * n:
                acc += gc2.diffs(G, n, out_closed=False)['delta']
                cnt += 1
        m = acc / cnt
        B = 200
        idx = rng.integers(0, P, (B, P))
        out.append(dict(kind=kind, t=t, E_delta=float(m.mean()), se=float(np.std([m[i].mean() for i in idx])),
                        per_chain=m.tolist()))
        print(kind, t, out[-1]['E_delta'], '%.0fs' % (time.time() - t0), flush=True)
    res['cfgs'] = [{k: v for k, v in o.items() if k != 'per_chain'} for o in out]
    np.savez_compressed(OUT + '.npz', per_chain=np.array([o['per_chain'] for o in out]),
                        kinds=np.array([o['kind'] for o in out]), ts=np.array([o['t'] for o in out]))
else:
    R = dict(r3=3, r4=4, r6=6)[mode]
    if mode == 'r6' and a.P is None:
        P = max(500, P // 2)
        res['P'] = P
    Q0 = gc2.sample_Q_stationary(n, P, rng)
    G = gc2.init_identical(Q0, R)
    B, T, every = 6 * n, 8 * n, max(1, n // 8)
    for _ in range(B):
        G = gc2.step(G, n, rng)
    S = {}
    for t in range(T):
        G = gc2.step(G, n, rng)
        if t % every != every - 1:
            continue
        Rho, Qd = corr(G)
        qbar = np.exp(np.mean(np.log(Qd), 1))
        ds = gc2.mf_fixed_point(qbar * n)
        rec = dict(chain=np.arange(P), qbar=qbar, dstar=ds)
        if R == 3:
            rec['d01'], rec['d02'], rec['d12'] = 1 - Rho[:, 0, 1], 1 - Rho[:, 0, 2], 1 - Rho[:, 1, 2]
        else:
            x = lambda a, b: Rho[:, a[0], b[0]] - Rho[:, a[0], b[1]] - Rho[:, a[1], b[0]] + Rho[:, a[1], b[1]]
            p1, p2 = (0, 1), (2, 3)
            rec['x11'], rec['x22'], rec['x12'] = x(p1, p1), x(p2, p2), x(p1, p2)
            if R == 6:
                p3 = (4, 5)
                rec['x33'], rec['x23'], rec['x13'] = x(p3, p3), x(p2, p3), x(p1, p3)
        for k, v in rec.items():
            S.setdefault(k, []).append(v)
    S = {k: np.concatenate(v) for k, v in S.items()}
    np.savez_compressed(OUT + '.npz', **S)
    if R == 3:
        D = np.stack([S['d01'], S['d02'], S['d12']], 1)
        res.update(range_over_mean=float(np.mean((D.max(1) - D.min(1)) / D.mean(1))),
                   corr_d01_d02=float(np.corrcoef(S['d01'], S['d02'])[0, 1]))
    else:
        trC = 0.5 * S['x11']
        trC2 = 0.25 * S['x12'] ** 2
        res.update(PR_ratio_of_means=float(trC.mean() ** 2 / trC2.mean()),
                   PR_4rep=float(np.mean(0.25 * S['x11'] * S['x22']) / trC2.mean()),
                   PR_norm=float((trC / S['dstar']).mean() ** 2 / (trC2 / S['dstar'] ** 2).mean()))
        if R == 6:
            trC3 = S['x12'] * S['x23'] * S['x13'] / 8.0
            m1, m2, m3 = (trC / S['dstar']).mean(), (trC2 / S['dstar'] ** 2).mean(), (trC3 / S['dstar'] ** 3).mean()
            res.update(r3_norm=float(m3 * m1 / m2 ** 2), r3_raw=float(trC3.mean() * trC.mean() / trC2.mean() ** 2))
res['sec'] = time.time() - t0
json.dump(res, open(OUT + '.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'cfgs'}), flush=True)
