"""scale-mode lane scorer (hashed in PREREG.md before any evaluation result is read).
usage: score.py LANE_ROOT OUT_JSON
Reads estimates and costs from LANE_ROOT/runs (this lane), arc-update's runs/ (ARC variants, RQMC, truths at L = n/8) and
arc-noisy's noiseless truths (nets 200-204), and the WhestBench Phase 2 public truths (downloads/hf/npz). Writes per-net
and per-set statistics and the verdict of every registered prediction.

Definitions (PREREG.md section 3):
- nMSE e = |est - Y|^2 / tr Var (E1, E2, E4: against the full truth; E3: cross-half (est - YA).(est - YB) / tr Var).
- cost C in forward passes = flops / (2 n^2 L); ARC's NamedFlopCounter (+1 per ndtr element for the claim's arms, as the
  claim counts). MC at cost C: 1/C. RQMC at cost C: log-log interpolation of the mean replicate nMSE over N, slope -1
  outside the measured range (extrapolated; flagged).
- G_MC = 1 / (C e); G_RQ = RQMC(C) / e; X_RQ = (the N at which RQMC reaches e) / C.
- ARCbest(C) = min e over ARC variants with cost <= C on the same net; R_ARC = ARCbest(C) / e.
- gamma_{2->3} = log(e2 / e3) / log(C3 / C2): scale-law ladder (LVTV2 -> SL3) and ARC (k2a -> best of k3f, k3fa, k3).
- E4 also: raw final-layer MSE |est - Y|^2 / n, MC at the full budget = avg_variance / 65536, RQMC at 2^16 points.
"""
import glob, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT, OUTP = sys.argv[1], sys.argv[2]
RUNS = os.path.join(ROOT, 'runs')
AU_RUNS = '/home/agent/workspaces/mats/work/arc-update/runs'
NOISY = '/home/agent/workspaces/mats/work/arc-noisy/truth'
HF = os.path.join(ROOT, 'downloads', 'hf', 'npz')
LV_ARMS = ('LVTV2', 'LVT', 'LVTV2f1', 'LVT0')
ARC_V = ('k1', 'k2', 'k2a', 'k3', 'k3f', 'k3fa', 'k4', 'k4f')
BUDGET_PASSES = 2.0 ** 41 / (2 * 1024 * 1024 * 16)      # 65536 (Phase 2); Phase 1: 2.72e11 / (2 * 256^2 * 32) = 64850


def jload(p):
    return json.load(open(p)) if os.path.exists(p) else None


def med(x):
    x = [v for v in x if v is not None and np.isfinite(v)]
    return float(np.median(x)) if x else None


def gmean(x):
    x = [v for v in x if v is not None and np.isfinite(v) and v > 0]
    return float(np.exp(np.mean(np.log(x)))) if x else None


# ------------------------------------------------------------------------------------------------ sets
def sets():
    S = {}
    S['E1'] = [dict(kind='au', seed=s, n=256, L=32) for s in range(200, 205)]
    for n, L in ((32, 4), (64, 8), (128, 16)):
        S[f'E2_n{n}'] = [dict(kind='au', seed=s, n=n, L=L) for s in range(300, 308)]
    for n, L, s0, k in ((64, 16, 600, 8), (128, 32, 610, 8), (256, 64, 620, 8), (512, 128, 630, 8), (1024, 256, 640, 8)):
        S[f'E3_n{n}'] = [dict(kind='au', seed=s0 + t, n=n, L=L) for t in range(k)]
    S['E4'] = [dict(kind='p2', id=i, n=1024, L=16) for i in range(12)]
    return S


def tag(net):
    return f'au{net["seed"]}_n{net["n"]}_L{net["L"]}' if net['kind'] == 'au' else f'p2_{net["id"]:02d}'


def truth(setname, net):
    """Returns dict(Y, YA, YB, var (per-neuron, final layer), avgvar, cross)."""
    n, L = net['n'], net['L']
    if setname == 'E1':
        d = np.load(os.path.join(NOISY, f'truth_256_32_s0_seed{net["seed"]}.npz'))
        N = float(d['N']); Y = d['S1'][-1] / N; var = d['S2'][-1] / N - Y ** 2
        return dict(Y=Y, var=var, cross=False)
    if setname.startswith('E2'):
        d = np.load(os.path.join(AU_RUNS, f'truth_n{n}_L{L}_s{net["seed"]}.npz'))
        N = float(d['N']); h = N / 2
        S1 = d['S1A'][-1] + d['S1B'][-1]; S2 = d['S2A'][-1] + d['S2B'][-1]
        Y = S1 / N
        return dict(Y=Y, YA=d['S1A'][-1] / h, YB=d['S1B'][-1] / h, var=S2 / N - Y ** 2, cross=False)
    if setname.startswith('E3'):
        p = os.path.join(RUNS, f'truth_{tag(net)}.npz')
        if not os.path.exists(p):
            return None
        d = np.load(p)
        N = float(d['N']); h = N / 2
        S1 = d['S1A'][-1] + d['S1B'][-1]; S2 = d['S2A'][-1] + d['S2B'][-1]
        Y = S1 / N
        return dict(Y=Y, YA=d['S1A'][-1] / h, YB=d['S1B'][-1] / h, var=S2 / N - Y ** 2, cross=True)
    if setname == 'E4':
        d = np.load(os.path.join(HF, f'p2_mlp_{net["id"]:02d}.npz'))
        Y = d['all_layer_means'][-1].astype(np.float64)
        av = float(d['avg_variance'])
        return dict(Y=Y, var=np.full(n, av), avgvar=av, cross=False)
    raise ValueError(setname)


def err(est, T):
    est = np.asarray(est, dtype=np.float64)
    if T['cross']:
        return float(((est - T['YA']) * (est - T['YB'])).sum() / T['var'].sum())
    return float(((est - T['Y']) ** 2).sum() / T['var'].sum())


def methods(setname, net):
    """dict name -> (est, passes, extra) for every available method on this net."""
    n, L = net['n'], net['L']
    pf = 2.0 * n * n * L
    out = {}
    t = tag(net)
    lv = jload(os.path.join(RUNS, f'lv_{t}.json'))
    if lv:
        for a in LV_ARMS:
            r = lv['arms'].get(a)
            if r:
                out[a] = (r['mean'], r['flops'] / pf, dict(passes_fs=r['flops_flopscope_special'] / pf, V_L=r['Vs'][-1]))
    sl = jload(os.path.join(RUNS, f'sl3_{t}.json'))
    if sl:
        out['SL3'] = (sl['mean'], sl['flops'] / pf, {})
    cv = jload(os.path.join(RUNS, f'cov_{t}.json'))
    if cv:
        out['COV'] = (cv['mean'], cv['flops'] / pf, {})
    for v in ARC_V:
        r = None
        if net['kind'] == 'au':
            r = jload(os.path.join(AU_RUNS, f'lad_n{n}_L{L}_s{net["seed"]}_{v}.json'))
        if r is None:
            r = jload(os.path.join(RUNS, f'arc_{t}_{v}.json'))
        if r:
            out['ARC-' + v] = (r['mean'], r['flops'] / pf, {})
    return out


def rqmc_curve(setname, net, T):
    """(Ns, mean nMSE per N, per-replicate lists) or None."""
    n, L = net['n'], net['L']
    if net['kind'] == 'au' and (setname == 'E1' or setname.startswith('E2')):
        r = jload(os.path.join(AU_RUNS, f'rqmc_n{n}_L{L}_s{net["seed"]}.json'))
        if r is None:
            return None
        return (np.array([row['N'] for row in r['rows']], float), np.array([row['mean_nmse'] for row in r['rows']]),
                [row['nmse'] for row in r['rows']])
    r = jload(os.path.join(RUNS, f'rqmc_{tag(net)}.json'))
    if r is None:
        return None
    Ns, es, reps = [], [], []
    for row in r['rows']:
        e = [err(x, T) for x in row['est']]
        Ns.append(row['N']); es.append(float(np.mean(e))); reps.append(e)
    return np.array(Ns, float), np.array(es), reps


def rq_at(curve, N):
    Ns, es = curve[0], curve[1]
    if N <= Ns[0]:
        return float(es[0] * Ns[0] / N), True
    if N >= Ns[-1]:
        return float(es[-1] * Ns[-1] / N), True
    return float(np.exp(np.interp(np.log(N), np.log(Ns), np.log(es)))), False


def rq_reach(curve, e):
    """N at which the RQMC curve reaches error e (monotone envelope of the log-log interpolation; slope -1 outside)."""
    Ns, es = curve[0], np.minimum.accumulate(curve[1])
    if e >= es[0]:
        return float(Ns[0] * es[0] / e), True
    if e <= es[-1]:
        return float(Ns[-1] * es[-1] / e), True
    for i in range(1, len(Ns)):
        if es[i] <= e:
            if es[i] == es[i - 1]:
                return float(Ns[i]), False
            s = math.log(e / es[i - 1]) / math.log(es[i] / es[i - 1])
            return float(math.exp(math.log(Ns[i - 1]) + s * (math.log(Ns[i]) - math.log(Ns[i - 1])))), False
    return float(Ns[-1]), True


def score_net(setname, net):
    T = truth(setname, net)
    if T is None:
        return None
    M = methods(setname, net)
    cur = rqmc_curve(setname, net, T)
    row = dict(net=tag(net), n=net['n'], L=net['L'], m={})
    arcs = {k: (err(v[0], T), v[1]) for k, v in M.items() if k.startswith('ARC-')}
    for k, (est, C, ex) in M.items():
        e = err(est, T)
        d = dict(e=e, C=C, G_MC=1.0 / (C * e) if e > 0 else None, **ex)
        if cur is not None and e > 0:
            rq, extr = rq_at(cur, C)
            d['RQ_at_C'] = rq; d['G_RQ'] = rq / e; d['G_RQ_extrap'] = extr
            N_reach, extr2 = rq_reach(cur, e)
            d['X_RQ'] = N_reach / C; d['X_RQ_extrap'] = extr2; d['RQ_reach_N'] = N_reach
        cheaper = [ea for (ea, ca) in arcs.values() if ca <= C]
        d['ARCbest_at_C'] = min(cheaper) if cheaper else None
        d['R_ARC'] = (min(cheaper) / e) if (cheaper and e > 0) else None
        if setname == 'E4':
            raw = float(((np.asarray(est) - T['Y']) ** 2).mean())
            d['raw_mse'] = raw
            d['adj_score_arc_counter'] = raw * max(0.1, C / BUDGET_PASSES)
        row['m'][k] = d
    if cur is not None:
        row['rqmc'] = dict(N=cur[0].tolist(), e=cur[1].tolist(), gain_mc=(1.0 / (cur[0] * cur[1])).tolist())
        if setname == 'E4':
            row['rqmc_full_raw'] = float(rq_at(cur, BUDGET_PASSES)[0] * T['avgvar'])
    if setname == 'E4':
        row['mc_full_raw'] = T['avgvar'] / BUDGET_PASSES
        row['avgvar'] = T['avgvar']
    # ladders
    m = row['m']
    if 'LVTV2' in m and 'SL3' in m and m['SL3']['e'] > 0 and m['LVTV2']['e'] > 0:
        row['gamma_SL'] = math.log(m['LVTV2']['e'] / m['SL3']['e']) / math.log(m['SL3']['C'] / m['LVTV2']['C'])
    k3 = [k for k in ('ARC-k3f', 'ARC-k3fa', 'ARC-k3') if k in m and m[k]['e'] > 0]
    if 'ARC-k2a' in m and k3:
        best3 = min(k3, key=lambda k: m[k]['e'])
        row['gamma_ARC'] = math.log(m['ARC-k2a']['e'] / m[best3]['e']) / math.log(m[best3]['C'] / m['ARC-k2a']['C'])
        row['gamma_ARC_k3'] = best3
    return row


def summarize(rows):
    out = {}
    names = sorted({k for r in rows for k in r['m']})
    for k in names:
        rs = [r['m'][k] for r in rows if k in r['m']]
        s = dict(nets=len(rs))
        for f in ('e', 'C', 'G_MC', 'G_RQ', 'X_RQ', 'R_ARC', 'raw_mse', 'adj_score_arc_counter', 'passes_fs', 'V_L'):
            vals = [x.get(f) for x in rs if x.get(f) is not None]
            if vals:
                s['med_' + f] = med(vals)
                s['min_' + f] = float(np.min(vals)); s['max_' + f] = float(np.max(vals))
                if f in ('e', 'raw_mse', 'adj_score_arc_counter'):
                    s['mean_' + f] = float(np.mean(vals))
        s['n_beat_MC'] = int(sum(1 for x in rs if x.get('G_MC') and x['G_MC'] > 1))
        s['n_beat_RQ'] = int(sum(1 for x in rs if x.get('G_RQ') and x['G_RQ'] > 1))
        s['any_G_RQ_extrap'] = bool(any(x.get('G_RQ_extrap') for x in rs))
        if s.get('med_C') and s.get('mean_e'):
            s['G_MC_of_mean'] = 1.0 / (np.mean([x['C'] for x in rs]) * s['mean_e'])
        out[k] = s
    for g in ('gamma_SL', 'gamma_ARC'):
        vals = [r[g] for r in rows if g in r]
        if vals:
            out[g] = dict(median=med(vals), min=float(np.min(vals)), max=float(np.max(vals)), nets=len(vals))
    # medians-based gammas (as arc-update's table)
    def mg(a, b):
        ea = [r['m'][a]['e'] for r in rows if a in r['m'] and b in r['m']]
        eb = [r['m'][b]['e'] for r in rows if a in r['m'] and b in r['m']]
        ca = [r['m'][a]['C'] for r in rows if a in r['m'] and b in r['m']]
        cb = [r['m'][b]['C'] for r in rows if a in r['m'] and b in r['m']]
        if not ea:
            return None
        return math.log(med(ea) / med(eb)) / math.log(med(cb) / med(ca))
    out['gamma_SL_of_medians'] = mg('LVTV2', 'SL3')
    for k3 in ('ARC-k3f', 'ARC-k3fa'):
        out[f'gamma_ARC_k2a_{k3}_of_medians'] = mg('ARC-k2a', k3)
    if rows and 'mc_full_raw' in rows[0]:
        out['mean_mc_full_raw'] = float(np.mean([r['mc_full_raw'] for r in rows]))
        rf = [r['rqmc_full_raw'] for r in rows if 'rqmc_full_raw' in r]
        if rf:
            out['mean_rqmc_full_raw'] = float(np.mean(rf))
        out['mean_avgvar'] = float(np.mean([r['avgvar'] for r in rows]))
    rq = [r['rqmc'] for r in rows if 'rqmc' in r]
    if rq:
        Ns = rq[0]['N']
        out['rqmc_med_gain_mc'] = {str(int(N)): med([q['gain_mc'][i] for q in rq if len(q['gain_mc']) > i]) for i, N in enumerate(Ns)}
    return out


def width_exponent(per_n, key, method, B=2000, seed=0):
    """Slope of log(median over nets of key) on log n, with a bootstrap over nets within each width."""
    ns = sorted(per_n)
    if len(ns) < 2:
        return None
    def stat(sel):
        y = [math.log(med([r['m'][method][key] for r in sel[n] if method in r['m'] and r['m'][method].get(key)])) for n in ns]
        return float(np.polyfit(np.log(ns), y, 1)[0])
    try:
        s0 = stat(per_n)
    except Exception:
        return None
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        sel = {n: [per_n[n][i] for i in rng.integers(0, len(per_n[n]), len(per_n[n]))] for n in ns}
        try:
            bs.append(stat(sel))
        except Exception:
            pass
    lo, hi = (np.percentile(bs, [2.5, 97.5]) if bs else (None, None))
    return dict(slope=s0, lo=float(lo), hi=float(hi), widths=ns)


# ------------------------------------------------------------------------------------------------ run
S = sets()
res = dict(per_net={}, per_set={})
for name, nets in S.items():
    rows = [r for r in (score_net(name, net) for net in nets) if r is not None]
    if name.startswith('E3') and len(rows) < 3:       # PREREG section 2: a cell with < 3 finished nets is not scored
        res.setdefault('not_scored', {})[name] = len(rows)
        rows = []
    res['per_net'][name] = rows
    res['per_set'][name] = summarize(rows) if rows else {}

# width exponents: L = n/8 (E2 n = 32, 64, 128 and E1 n = 256); L = n/4 (E3)
ladder8 = {32: res['per_net']['E2_n32'], 64: res['per_net']['E2_n64'], 128: res['per_net']['E2_n128'], 256: res['per_net']['E1']}
ladder8 = {k: v for k, v in ladder8.items() if v}
diag4 = {int(k.split('_n')[1]): v for k, v in res['per_net'].items() if k.startswith('E3') and v}
res['width'] = {}
for lab, per_n in (('L=n/8', ladder8), ('L=n/4', diag4)):
    for key in ('G_MC', 'G_RQ', 'e', 'C'):
        for meth in ('LVTV2', 'ARC-k2a', 'ARC-k2'):
            w = width_exponent(per_n, key, meth)
            if w:
                res['width'][f'{lab} {meth} {key}'] = w

from score_predictions import verdicts  # noqa: E402  (registered prediction checks; hashed with this file)
res['verdicts'] = verdicts(res)
json.dump(res, open(OUTP, 'w'), indent=1, default=float)
for v in res['verdicts']:
    print(f"{v['id']:5s} {v['result']:13s} {v['measured']}")
