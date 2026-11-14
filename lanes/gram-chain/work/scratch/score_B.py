"""Score PREREG Part B. Writes results/partB_scores.json."""
import json, math, os
import numpy as np

R = '/home/agent/workspaces/mats/work/gram-chain/runs/'
pred = json.load(open('/home/agent/workspaces/mats/work/gram-chain/results/predB_meanfield.json'))
A = json.load(open('/home/agent/workspaces/mats/work/gram-chain/results/partA_scores.json'))
S, T = {}, {}


def first_below(ts, vs, thr):
    """first grid t with v < thr (integer, as registered) and the linear interpolation."""
    for i, (t, v) in enumerate(zip(ts, vs)):
        if v < thr:
            if i == 0:
                return t, float(t)
            t0, v0 = ts[i - 1], vs[i - 1]
            return t, float(t0 + (v0 - thr) / (v0 - v) * (t - t0))
    return None, None


def interp_loglog(ts, vs, t):
    ts, vs = np.asarray(ts, float), np.asarray(vs, float)
    m = vs > 0
    return float(np.exp(np.interp(math.log(t), np.log(ts[m]), np.log(vs[m]))))


cur = {}
for n in (16, 64, 256, 1024):
    f = R + 'B_curves_n%d.json' % n
    if os.path.exists(f):
        cur[n] = json.load(open(f))
# PB1 / PB2 / PB4
pb1, pb2, pb4 = [], [], []
MFh = {16: 3, 64: 4, 256: 6, 1024: 10}
MFa = {16: 2.98, 64: 4.85, 256: 7.87, 1024: 12.74}
MFth = {16: 4, 64: 6, 256: 9, 1024: 14}
MF4 = {16: (15, 0.063), 64: (27, 0.071), 256: (45, 0.082), 1024: (73, 0.089)}
for n, js in cur.items():
    ts = [r['t'] for r in js['rows']]
    vp = [r['V_P'] for r in js['rows']]
    tp = [r['T_P'] for r in js['rows']]
    vpl = [r['V_P_log'] for r in js['rows']]
    hi, hf = first_below(ts, vp, 0.5)
    tcut = 8 * pred[str(n)]['Tstar_med']  # beyond 8 T* the mean-field V_P is below 1e-3; the chain's values there are noise
    msk = [t <= tcut for t in ts]
    tsa = [t for t, m in zip(ts, msk) if m]
    vpa = [v for v, m in zip(vp, msk) if m]
    area = float(np.trapezoid(vpa, tsa) + 0.5 * vpa[0])
    thi, thf = first_below(ts, tp, 0.5)
    t4, mf4 = MF4[n]
    tp4 = interp_loglog(ts, tp, t4)
    hint = int(math.ceil(hf - 1e-12))  # first integer t with the interpolated V_P below 0.5 (the grid skips some t)
    T[n] = dict(V_P_half_grid=hi, V_P_half_interp=hf, V_P_half_first_integer=hint, V_P_area=area, T_P_half_grid=thi,
                T_P_half_interp=thf, T_P_at_4Tstar=tp4, rows=js['rows'],
                PB1_grid_version=bool(abs(hi / MFh[n] - 1) <= 0.3))
    if n >= 64:
        pb1.append(abs(hint / MFh[n] - 1) <= 0.3 and abs(area / MFa[n] - 1) <= 0.3)
        pb2.append(abs(thf / MFth[n] - 1) <= 0.3 and 0.5 <= tp4 / mf4 <= 2)
        ok = all(r['V_P_log'] > r['V_P'] for r in js['rows'] if r['t'] >= 8)
        vl_half = interp_loglog(ts, [max(v, 1e-9) for v in vpl], n / 2)
        pb4.append(ok and vl_half > 0.2)
        T[n]['V_P_log_at_n_over_2'] = vl_half
S['PB1'] = dict(hit=bool(pb1 and all(pb1) and len(pb1) == 3), clauses=pb1)
S['PB2'] = dict(hit=bool(pb2 and all(pb2) and len(pb2) == 3), clauses=pb2)
S['PB4'] = dict(hit=bool(pb4 and all(pb4) and len(pb4) == 3), clauses=pb4)
# PB3
pb3 = []
for n in (64, 256):
    f = R + 'B_pr_n%d.json' % n
    if os.path.exists(f) and str(n) in A['r4']:
        js = json.load(open(f))
        PRC = A['r4'][str(n)]['PR_4rep']
        rows = {r['t']: r for r in js['rows']}
        T['pr_%d' % n] = dict(PR_C=PRC, rows=js['rows'],
                              formula={t: 1 / (1 / PRC + 2 * t / n) for t in rows})
        for t in (1, 2, 4):
            fpred = 1 / (1 / PRC + 2 * t / n)
            for key in ('PR_closed', 'PR_tot'):
                v = rows[t][key]
                pb3.append(v is not None and 1 / 1.5 <= v / fpred <= 1.5)
S['PB3'] = dict(hit=bool(len(pb3) == 12 and all(pb3)), clauses=pb3)
# PB5
pb5 = []
for n in (64, 256, 1024):
    f = R + 'B_pert_n%d.json' % n
    if os.path.exists(f):
        js = json.load(open(f))
        surv = pred[str(n)]['surv']
        rec = {}
        for run in js['runs']:
            eps = run['eps']
            d0 = run['rows'][0]['delta_hidden']
            s = {r['t']: r['delta_hidden'] / d0 for r in run['rows']}
            rec[eps] = s
            if eps in (0.1, 0.3):
                mf = surv[str(eps)]
                for t, v in s.items():
                    if t > 0 and t < len(mf) and mf[t] >= 0.1:
                        pb5.append(abs(v / mf[t] - 1) <= 0.3)
        tq = n // 4
        tt = min(rec[1e-3].keys(), key=lambda t: abs(t - tq))
        pb5.append(rec[1e-3][tt] >= 2 * rec[0.3][tt])
        T['pert_%d' % n] = {str(k): v for k, v in rec.items()}
S['PB5'] = dict(hit=bool(pb5 and all(pb5)), n_clauses=len(pb5), n_fail=int(sum(1 for c in pb5 if not c)))
# PB6
pb6 = []
f = R + 'B_input_n256_L128_s0.json'
if os.path.exists(f):
    rows = {r['l']: r for r in json.load(open(f))['rows']}
    for l, v in ((1, 167), (4, 62), (16, 19), (32, 10.3), (64, 5.3)):
        pb6.append((256, l, rows[l]['PR_4rep'], v, abs(rows[l]['PR_4rep'] / v - 1) <= 0.2))
f = R + 'B_input_n64_L64_s0.json'
if os.path.exists(f):
    rows = {r['l']: r for r in json.load(open(f))['rows']}
    for l, v in ((1, 41.7), (4, 15.4), (16, 4.7)):
        pb6.append((64, l, rows[l]['PR_4rep'], v, abs(rows[l]['PR_4rep'] / v - 1) <= 0.2))
S['PB6'] = dict(hit=bool(len(pb6) == 8 and all(x[4] for x in pb6)), rows=pb6)
# PB7
pb7 = []
f = R + 'B_input_n256_L32_s0.json'
if os.path.exists(f):
    js = json.load(open(f))
    att = {r['l']: r for r in js['attribution']}
    for l, v in ((1, 0.19), (2, 0.30), (4, 0.46), (8, 0.66), (16, 0.85), (24, 0.94), (31, 0.99)):
        sh = att[l]['V_logr'] / js['out_log_var']
        pb7.append((l, sh, v, abs(sh / v - 1) <= 0.25))
S['PB7'] = dict(hit=bool(len(pb7) == 7 and all(x[3] for x in pb7)), rows=pb7)
# PB8
pb8 = []
f = R + 'B_input_n8_L256_s0.json'
if os.path.exists(f):
    js = json.load(open(f))
    rows = {r['l']: r for r in js['rows']}
    P = js['P']
    for l in (64, 128, 255):
        p = (1 - 2 ** -8) ** l
        se = math.sqrt(p * (1 - p) / P)
        v = rows[l].get('alive_rep')
        pb8.append((l, v, p, v is not None and abs(v - p) <= 3 * se))
S['PB8'] = dict(hit=bool(len(pb8) == 3 and all(x[3] for x in pb8)), rows=pb8)
json.dump(dict(scores=S, tables=T), open('/home/agent/workspaces/mats/work/gram-chain/results/partB_scores.json', 'w'), indent=1,
          default=float)
for k, v in S.items():
    print(k, v)
for n in cur:
    t = T[n]
    print('n=%d V_P half grid %s interp %.2f area %.2f | T_P half %s interp %.2f, T_P(4T*) %.4f' % (
        n, t['V_P_half_grid'], t['V_P_half_interp'], t['V_P_area'], t['T_P_half_grid'], t['T_P_half_interp'], t['T_P_at_4Tstar']))
