"""Score T-LAD runs: nMSE of each ARC variant against the truth, cost in forward passes (ARC's counter), gain over plain
MC at own cost (G_MC = (1/passes)/nMSE) and over RQMC at own cost (G_RQMC = nMSE_RQMC(passes)/nMSE, RQMC
interpolated log-log in N between measured points, extrapolated with slope -1 beyond its range).
usage: score_lad.py SEEDS_n32 SEEDS_n64 SEEDS_n128 SEEDS_n256 [OUT_JSON]   (comma-separated seed lists; '-' = none)
Truth: runs/truth_n{n}_L{L}_s{seed}.npz for n <= 128; arc-noisy s0 (seeds 200-204) or s0.001 (100-111) for n = 256.
Squared error: unbiased cross product with the two truth halves where available (n <= 128), else |est - Y|^2 minus
the truth's own 1/N_truth."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
CFG = {32: 4, 64: 8, 128: 16, 256: 32}
VARIANTS = ['k1', 'k2', 'k2a', 'k3', 'k3f', 'k3fa', 'k4', 'k4f']


def truth(n, L, seed):
    p = os.path.join(RUNS, f'truth_n{n}_L{L}_s{seed}.npz')
    if os.path.exists(p):
        T = au.truth_from_moments(dict(np.load(p)))
        return T['mean'][-1], T['var'][-1].sum(), T['meanA'][-1], T['meanB'][-1], T['N']
    for tk in ('s0', 's0.001'):
        q = os.path.join(au.ARC_NOISY, 'truth', f'truth_{n}_{L}_{tk}_seed{seed}.npz')
        if os.path.exists(q):
            d = np.load(q); N = float(d['N'])
            Y = d['S1'][-1] / N
            return Y, float((d['S2'][-1] / N - Y ** 2).sum()), None, None, N
    return None


def rqmc_curve(n, L, seed):
    p = os.path.join(RUNS, f'rqmc_n{n}_L{L}_s{seed}.json')
    if not os.path.exists(p) or os.path.getsize(p) < 200:
        return None
    r = json.load(open(p))
    return np.array([row['N'] for row in r['rows']], float), np.array([row['mean_nmse'] for row in r['rows']])


def rqmc_at(curve, N):
    Ns, es = curve
    if N <= Ns[0]:
        return es[0] * Ns[0] / N
    if N >= Ns[-1]:
        return es[-1] * Ns[-1] / N
    return float(np.exp(np.interp(np.log(N), np.log(Ns), np.log(es))))


def score(seeds_by_n):
    out = {}
    for n, seeds in seeds_by_n.items():
        L = CFG[n]
        for seed in seeds:
            T = truth(n, L, seed)
            if T is None:
                continue
            Y, V, YA, YB, Nt = T
            cur = rqmc_curve(n, L, seed)
            for v in VARIANTS:
                p = os.path.join(RUNS, f'lad_n{n}_L{L}_s{seed}_{v}.json')
                if not os.path.exists(p):
                    continue
                r = json.load(open(p))
                est = np.array(r['mean'])
                if YA is not None:
                    e = float(np.dot(est - YA, est - YB) / V)
                else:
                    e = float(((est - Y) ** 2).sum() / V) - 1.0 / Nt
                passes = r['passes']
                row = dict(n=n, L=L, seed=seed, variant=v, nmse=e, passes=passes, gain_mc=(1.0 / passes) / e,
                           resolved=bool(e > 10.0 / Nt))
                if cur is not None:
                    row['gain_rqmc'] = rqmc_at(cur, passes) / e
                out[(n, seed, v)] = row
    return out


def med(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return float(np.median(xs)) if xs else float('nan')


if __name__ == '__main__':
    lists = [(a.split(',') if a != '-' else []) for a in sys.argv[1:5]]
    seeds_by_n = {n: [int(s) for s in lst] for n, lst in zip((32, 64, 128, 256), lists)}
    rows = score(seeds_by_n)
    table = {}
    for n in (32, 64, 128, 256):
        for v in VARIANTS:
            rs = [r for (nn, s, vv), r in rows.items() if nn == n and vv == v]
            if not rs:
                continue
            table[f'{n}_{v}'] = dict(n=n, variant=v, nets=len(rs), nmse=med([r['nmse'] for r in rs]),
                                     passes=med([r['passes'] for r in rs]), gain_mc=med([r['gain_mc'] for r in rs]),
                                     gain_rqmc=med([r.get('gain_rqmc') for r in rs]),
                                     resolved=sum(r['resolved'] for r in rs))
            t = table[f'{n}_{v}']
            print(f"n={n:3d} {v:5s} nets {t['nets']} nMSE {t['nmse']:.3e} passes {t['passes']:9.0f} "
                  f"G_MC {t['gain_mc']:8.3f} G_RQMC {t['gain_rqmc']:8.3f} resolved {t['resolved']}")
    if len(sys.argv) > 5:
        json.dump(dict(table=table, rows={f'{k[0]}_{k[1]}_{k[2]}': v for k, v in rows.items()}),
                  open(sys.argv[5], 'w'), indent=1)
