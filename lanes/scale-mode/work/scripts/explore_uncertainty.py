"""EXPLORATORY (after the review; not registered): uncertainty of the main comparisons.
usage: explore_uncertainty.py LANE_ROOT
1. For LVTV2 in every cell: bootstrap (2000) over nets AND over RQMC replicates (the 8 scrambles at each N resampled
   per net) of the median G_RQ; the RQMC replicate relative SE of the mean error at the measured N nearest the cost.
2. Leave-one-width-out slopes of log median G_RQ(LVTV2) on log n along L = n/4.
3. Truth-half sensitivity on E3: median LVTV2 nMSE scored against half A, half B and cross-half.
4. C1 at 512 x 128: bootstrap over nets of the claim's statistic (MC at the mean cost over the mean nMSE).
5. E4: per-MLP full-budget RQMC vs ARC k2a with a replicate bootstrap (measured 2^16 on MLPs 0-5; 6-11 from 2^14)."""
import json, math, os, sys
import numpy as np

ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
d = json.load(open(os.path.join(ROOT, 'results', 'score.json')))
AU = '/home/agent/workspaces/mats/work/arc-update/runs'
RUNS = os.path.join(ROOT, 'runs')
rng = np.random.default_rng(0)


def rep_errors(s, r):
    """per-N lists of replicate errors for a net row r of set s."""
    n, L = r['n'], r['L']
    tag = r['net']
    if s == 'E1' or s.startswith('E2'):
        seed = int(tag[2:tag.index('_')])
        q = json.load(open(os.path.join(AU, f'rqmc_n{n}_L{L}_s{seed}.json')))
        return [row['N'] for row in q['rows']], [np.array(row['nmse']) for row in q['rows']]
    if s.startswith('E3'):
        t = np.load(os.path.join(RUNS, f'truth_{tag}.npz')); N = float(t['N']); h = N / 2
        YA, YB = t['S1A'][-1] / h, t['S1B'][-1] / h
        var = (t['S2A'][-1] + t['S2B'][-1]) / N - ((YA + YB) / 2) ** 2
        q = json.load(open(os.path.join(RUNS, f'rqmc_{tag}.json')))
        return [row['N'] for row in q['rows']], [np.array([((np.array(e) - YA) * (np.array(e) - YB)).sum() / var.sum() for e in row['est']]) for row in q['rows']]
    return None


def rq_at(Ns, es, C):
    Ns = np.asarray(Ns, float); es = np.asarray(es, float)
    if np.any(es <= 0):
        es = np.maximum(es, 1e-30)
    if C <= Ns[0]:
        return es[0] * Ns[0] / C
    if C >= Ns[-1]:
        return es[-1] * Ns[-1] / C
    return float(np.exp(np.interp(math.log(C), np.log(Ns), np.log(es))))


print('1. median G_RQ(LVTV2) with a bootstrap over nets and RQMC scrambles (95%), and RQMC replicate rel. SE near the cost')
med_by = {}
for s in ['E2_n32', 'E2_n64', 'E2_n128', 'E1', 'E3_n64', 'E3_n128', 'E3_n256', 'E3_n512', 'E3_n1024']:
    rows = d['per_net'].get(s)
    if not rows:
        continue
    data = []
    ses = []
    for r in rows:
        m = r['m'].get('LVTV2')
        if not m:
            continue
        Ns, reps = rep_errors(s, r)
        data.append((m['e'], m['C'], Ns, reps))
        i = int(np.argmin([abs(math.log(N / m['C'])) for N in Ns]))
        ses.append(reps[i].std(ddof=1) / math.sqrt(len(reps[i])) / max(reps[i].mean(), 1e-30))
    point = np.median([rq_at(Ns, [x.mean() for x in reps], C) / e for e, C, Ns, reps in data])
    bs = []
    for _ in range(2000):
        idx = rng.integers(0, len(data), len(data))
        g = []
        for i in idx:
            e, C, Ns, reps = data[i]
            es = [x[rng.integers(0, len(x), len(x))].mean() for x in reps]
            g.append(rq_at(Ns, es, C) / e)
        bs.append(np.median(g))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    med_by[s] = (point, bs)
    print(f'  {s:9s} median G_RQ {point:.2f} [{lo:.2f}, {hi:.2f}]; RQMC replicate rel. SE near the cost: {np.min(ses):.0%}-{np.max(ses):.0%} (median {np.median(ses):.0%})')

print('2. leave-one-width-out slopes of log median G_RQ(LVTV2) on log n, L = n/4')
cells = [('E3_n64', 64), ('E3_n128', 128), ('E3_n256', 256), ('E3_n512', 512), ('E3_n1024', 1024)]
pts = {n: med_by[s][0] for s, n in cells if s in med_by}
ns = sorted(pts)
full = np.polyfit(np.log(ns), np.log([pts[n] for n in ns]), 1)[0]
print(f'  all five widths: {full:+.2f}; ' + '; '.join(f'without {k}: {np.polyfit(np.log([n for n in ns if n != k]), np.log([pts[n] for n in ns if n != k]), 1)[0]:+.2f}' for k in ns))

print('3. truth-half sensitivity on E3 (median LVTV2 nMSE): cross-half / against half A / against half B')
for s, n in cells:
    rows = d['per_net'].get(s)
    xa, xb, xc = [], [], []
    for r in rows:
        tag = r['net']
        t = np.load(os.path.join(RUNS, f'truth_{tag}.npz')); N = float(t['N']); h = N / 2
        YA, YB = t['S1A'][-1] / h, t['S1B'][-1] / h
        var = (t['S2A'][-1] + t['S2B'][-1]) / N - ((YA + YB) / 2) ** 2
        est = np.array(json.load(open(os.path.join(RUNS, f'lv_{tag}.json')))['arms']['LVTV2']['mean'])
        xa.append(((est - YA) ** 2).sum() / var.sum()); xb.append(((est - YB) ** 2).sum() / var.sum())
        xc.append(((est - YA) * (est - YB)).sum() / var.sum())
    print(f'  {s:9s} {np.median(xc):.2e} / {np.median(xa):.2e} / {np.median(xb):.2e}; per-net max |A - B| / cross: {max(abs(a - b) / c for a, b, c in zip(xa, xb, xc)):.0%}')

print("4. C1 at 512 x 128: the claim's statistic (MC at mean cost / mean nMSE), bootstrap over nets")
rows = d['per_net']['E3_n512']
es = np.array([r['m']['LVTV2']['e'] for r in rows]); Cs = np.array([r['m']['LVTV2']['C'] for r in rows])
bs = []
for _ in range(4000):
    i = rng.integers(0, len(es), len(es))
    bs.append(1.0 / (Cs[i].mean() * es[i].mean()))
print(f'  point {1.0 / (Cs.mean() * es.mean()):.2f}, 95% [{np.percentile(bs, 2.5):.2f}, {np.percentile(bs, 97.5):.2f}]')

print('5. E4: full-budget RQMC raw MSE vs ARC k2a raw MSE per MLP, replicate bootstrap of the ratio k2a / RQMC')
HF = os.path.join(ROOT, 'downloads', 'hf', 'npz')
for r in d['per_net']['E4']:
    tag = r['net']; i = int(tag[3:])
    Y = np.load(os.path.join(HF, f'p2_mlp_{i:02d}.npz'))['all_layer_means'][-1].astype(float)
    q = json.load(open(os.path.join(RUNS, f'rqmc_{tag}.json')))
    Ns = [row['N'] for row in q['rows']]
    reps = [np.array([((np.array(e) - Y) ** 2).mean() for e in row['est']]) for row in q['rows']]
    k2a = r['m']['ARC-k2a']['raw_mse']
    pt = k2a / rq_at(Ns, [x.mean() for x in reps], 65536)
    bs = [k2a / rq_at(Ns, [x[rng.integers(0, len(x), len(x))].mean() for x in reps], 65536) for _ in range(2000)]
    print(f'  {tag}: k2a/RQMC(2^16) {pt:.2f} [{np.percentile(bs, 2.5):.2f}, {np.percentile(bs, 97.5):.2f}]' + (' (RQMC extrapolated from 2^14)' if Ns[-1] < 65536 else ''))
