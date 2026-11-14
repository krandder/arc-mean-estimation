"""Score the registered S11 predictions (PREREG.md, Part S11) from the lane's work dir -> results/S11_scores.json.
Written before any S11 result was seen (hashed in prereg_hashes.txt before its first run).

S11.1 feistel, Walsh: held-out share of the predictable part captured by a degree-1 threshold map,
      (ptf1 - trivial) / (bayes_bit - trivial) over (transition, b) cells with bayes_bit - trivial > 1e-3, median <= 0.5.
S11.2 feistel and tanh4, real-valued: median W1 (learned S9 transitions, all lambdas and classes) <= 0.5 on each net.
S11.3 linear: median W1 >= 0.95 and the S10 linear class within 0.01 nMSE of mlp at the last layer (every lambda).
S11.4 tanh4: R_local(0) / R_local(L/2) (gfix, nMSE 0.1, unreached = 32 bits) larger than on the ReLU 16 x 16 net.
S11.5 S10 gap (linear minus mlp, last-layer nMSE) larger for tanh4 and for feistel than for ReLU 16 x 16, every lambda.
Verdict line: if S11.1 and S11.2 both miss, the scrambling tests are blind on these controls."""
import glob
import json
import math
import os

import numpy as np


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def rate_at(rates, nmse, eps):
    pts = sorted(zip(rates, nmse))
    env, best = [], float('inf')
    for r, e in pts:
        if e < best:
            env.append((r, e))
            best = e
    for i, (r, e) in enumerate(env):
        if e <= eps:
            if i == 0:
                return r
            r0, e0 = env[i - 1]
            f = (math.log(e0) - math.log(eps)) / (math.log(e0) - math.log(max(e, 1e-30)))
            return r0 + f * (r - r0)
    return None


def ptf1_shares(posthoc):
    out = []
    for tag, ent in (posthoc or {}).items():
        for b, trs in ent.items():
            for t in trs:
                r = t['real']
                gap = r['bayes_bit'] - r['trivial'] if r.get('bayes_bit') is not None else 0.0
                if gap > 1e-3 and r.get('ptf1') is not None:
                    out.append((r['ptf1'] - r['trivial']) / gap)
    return out


def w1_values(d0):
    v = []
    for p in sorted(glob.glob(f'{d0}/R_*.json')):
        for pm in load(p)['per_model']:
            v += [t['learned']['W1_exact'] for t in pm['transitions']]
    return v


def sim(d0):
    Q = {}
    for p in glob.glob(f'{d0}/Q_n16_L16_s5000_*.json'):
        d = load(p)
        if d['n'] == 16 and d['L'] == 16:
            Q[d['kind']] = d
    return Q


def gap(Q):
    if 'mlp' not in Q or 'linear' not in Q:
        return None
    return [Q['linear']['nmse'][-1][mi] - Q['mlp']['nmse'][-1][mi] for mi in range(len(Q['mlp']['lambdas']))]


def ratio(d0):
    r = []
    for l in (0, 8):
        d = load(f'{d0}/E_n16_L16_s5000_l{l}_local.json')
        if d is None:
            return None, None
        g = d['curves']['gfix']
        x = rate_at(g['rate'], g['nmse'], 0.1)
        r.append(32.0 if x is None else x)
    return r[0] / r[1], r


S = {}
sh = ptf1_shares(load('results/S11_feistel_posthoc.json'))
sh_relu = ptf1_shares(load('results/S2_posthoc.json'))
S['S11.1'] = dict(median=(float(np.median(sh)) if sh else None), n=len(sh),
                  relu_median=(float(np.median(sh_relu)) if sh_relu else None),
                  hit=(bool(sh) and float(np.median(sh)) <= 0.5) if sh else None)
w = {k: w1_values(f'runs/S11_{k}') for k in ('feistel', 'tanh4', 'linear')}
w_relu = w1_values('runs/S_real')
med = {k: (float(np.median(v)) if v else None) for k, v in w.items()}
S['S11.2'] = dict(median_feistel=med['feistel'], median_tanh4=med['tanh4'], n_feistel=len(w['feistel']),
                  n_tanh4=len(w['tanh4']), relu_median=(float(np.median(w_relu)) if w_relu else None),
                  hit=(None if (med['feistel'] is None or med['tanh4'] is None)
                       else bool(med['feistel'] <= 0.5 and med['tanh4'] <= 0.5)))
g_lin = gap(sim('runs/S11_linear'))
S['S11.3'] = dict(median_linear=med['linear'], n=len(w['linear']), sim_gap=g_lin,
                  hit=(None if (med['linear'] is None or g_lin is None)
                       else bool(med['linear'] >= 0.95 and all(x <= 0.01 for x in g_lin))))
rt, rt_r = ratio('runs/S11_tanh4')
rr, rr_r = ratio('runs/S_ent')
S['S11.4'] = dict(tanh4_ratio=rt, tanh4_R=rt_r, relu_ratio=rr, relu_R=rr_r,
                  hit=(None if (rt is None or rr is None) else bool(rt > rr)))
g_relu, g_t, g_f = gap(sim('runs/S_sim')), gap(sim('runs/S11_tanh4')), gap(sim('runs/S11_feistel'))
S['S11.5'] = dict(gap_relu=g_relu, gap_tanh4=g_t, gap_feistel=g_f,
                  hit=(None if (g_relu is None or g_t is None or g_f is None)
                       else bool(all(a > c for a, c in zip(g_t, g_relu)) and all(b > c for b, c in zip(g_f, g_relu)))))
h1, h2 = S['S11.1']['hit'], S['S11.2']['hit']
S['verdict'] = ('incomplete' if (h1 is None or h2 is None) else
                ('tests blind on the scrambled controls: the ReLU verdict cannot be trusted' if (not h1 and not h2) else
                 ('both tests light up on the scrambled controls' if (h1 and h2) else 'one of the two tests lights up')))
os.makedirs('results', exist_ok=True)
json.dump(S, open('results/S11_scores.json', 'w'), indent=1)
for k, v in S.items():
    if k == 'verdict':
        print('verdict:', v)
        continue
    h = v['hit']
    print(k, 'HIT' if h is True else ('MISS' if h is False else 'n/a'), {kk: vv for kk, vv in v.items() if kk != 'hit'})
