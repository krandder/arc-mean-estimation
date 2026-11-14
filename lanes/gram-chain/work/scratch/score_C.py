"""Score PREREG Part C (annealed vs quenched on real nets). Writes results/partC_scores.json."""
import json, math, os, sys, glob
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import gc2

R = '/home/agent/workspaces/mats/work/gram-chain/runs/'
A = json.load(open('/home/agent/workspaces/mats/work/gram-chain/results/partA_scores.json'))
out, S = {}, {}


def vp_mf(t, Q):
    """Mean-field closed relevance of the output direction at the net's radius Q (predB recursion)."""
    ds = float(gc2.mf_fixed_point(Q)[0])
    d = 0.0
    for _ in range(t - 1):
        d = (1 + Q * float(gc2.f_kernel(d))) / (Q + 1)
    return 1 - float(gc2.f_kernel(d)) / float(gc2.f_kernel(ds))


for f in sorted(glob.glob(R + 'C_n*_s5000_*.json')):
    js = json.load(open(f))
    n = js['n']
    nets = js['nets']
    trC = np.array([x['trC_u'] for x in nets])
    Qb = np.array([x['Qbar'] for x in nets])
    PR = np.array([x['PR_u'] for x in nets])
    ds = gc2.mf_fixed_point(Qb)  # Qbar in partC is Q = |h|^2/n (fixed 23:41Z; first version multiplied by n again)
    rec = dict(n=n, nets=len(nets), mean_trC=float(trC.mean()), se_trC=float(trC.std(ddof=1) / math.sqrt(len(trC))),
               cv_trC=float(trC.std(ddof=1) / trC.mean()), cv_trC_over_dstar=float(np.std(trC / ds, ddof=1) / np.mean(trC / ds)),
               median_PR=float(np.median(PR)), cv_PR=float(PR.std(ddof=1) / PR.mean()),
               median_Qbar_over_n=float(np.median(Qb) / n), trC_over_dstar_median=float(np.median(trC / ds)),
               spearman_PR_Q=float(spearmanr(PR, Qb).correlation),
               slope_logPR_logQ=float(np.polyfit(np.log(Qb), np.log(PR), 1)[0]))
    VP = {}
    for t in js['TG']:
        v = np.array([x['V_P'][str(t)] for x in nets])
        tp = np.array([x['T_P'][str(t)] for x in nets])
        mf = np.array([vp_mf(t, q) for q in Qb])
        VP[t] = dict(median=float(np.median(v)), mean=float(v.mean()), cv=float(v.std(ddof=1) / max(v.mean(), 1e-9)),
                     median_abs_dev_mf=float(np.median(np.abs(v - mf))), spearman_Q=float(spearmanr(Qb, v).correlation),
                     T_P_median=float(np.median(tp)))
    rec['VP'] = VP
    a4 = A['r4'].get(str(n))
    if a4:
        rec['chain_cv'] = a4['cv_chain']
        rec['chain_E_trC'] = a4['E_trC']
        rec['chain_PR_4rep'] = a4['PR_4rep']
    out[n] = rec
# chain annealed V_P (Part B curves)
curves = {}
for n in (64, 256):
    f = R + 'B_curves_n%d.json' % n
    if os.path.exists(f):
        curves[n] = {r['t']: r['V_P'] for r in json.load(open(f))['rows']}
pc1, pc2, pc3, pc4, pc5, pc6 = [], [], [], [], [], []
for n, r in out.items():
    if 'chain_cv' in r and n >= 16:
        pc1.append((n, r['cv_trC'], r['chain_cv'], abs(r['cv_trC'] / r['chain_cv'] - 1) <= 0.3))
        pc2.append((n, r['mean_trC'], r['chain_E_trC'], abs(r['mean_trC'] - r['chain_E_trC']) <= 2.5 * r['se_trC']))
        pc4.append((n, r['median_PR'], r['chain_PR_4rep'], abs(r['median_PR'] / r['chain_PR_4rep'] - 1) <= 0.25 and (n < 64 or r['cv_PR'] < 0.35)))
    if n in (64, 128, 256):
        pc3.append((n, r['cv_trC_over_dstar'], r['cv_trC'], r['cv_trC_over_dstar'] <= 0.5 * r['cv_trC']))
        sp = r['VP'][8]['spearman_Q'] if 8 in r['VP'] else None
        pc5.append((n, sp, r['VP'][4]['median_abs_dev_mf'], r['VP'][8]['median_abs_dev_mf'],
                    sp is not None and sp > 0.5 and r['VP'][4]['median_abs_dev_mf'] < 0.12 and r['VP'][8]['median_abs_dev_mf'] < 0.12))
    if n in curves:
        for t in (4, 8):
            pc6.append((n, t, curves[n][t], r['VP'][t]['median'], curves[n][t] < r['VP'][t]['median']))
from scipy.special import gammaincc, gamma as GAM
AA, BB = 2.2309204, 0.4
mq = lambda x: (24 * AA / 25) * BB ** (-2 / 3) * math.exp(BB / x) * gammaincc(2 / 3, BB / x) * GAM(2 / 3)
pc7 = []
for f in sorted(glob.glob(R + 'C_n*_s5000_*.json')):
    js = json.load(open(f))
    n = js['n']
    if n not in (64, 128, 256):
        continue
    rr, th, qq = [], [], []
    for x in js['nets']:
        vl = x['logQa_var'] / 4.0
        rr.append(vl / (x['trC_a'] + vl))
        q = x["Qbar"] / n  # q = Q/n
        th.append(mq(q) / (mq(q) + 2 * AA * q ** (-2 / 3)))
        qq.append(q)
    rr, th = np.array(rr), np.array(th)
    dev = float(np.median(np.abs(rr / th - 1)))
    sp = float(spearmanr(rr, qq).correlation)
    out[n]['rho_rad_median'] = float(np.median(rr))
    out[n]['rho_rad_theory_median'] = float(np.median(th))
    pc7.append((n, dev, sp, dev < 0.3 and sp > 0.6))
S['PC7'] = dict(hit=bool(len(pc7) == 3 and all(x[3] for x in pc7)), rows=pc7)
chain_inc = [out[n]['chain_cv'] for n in sorted(out) if 'chain_cv' in out[n] and n >= 16]
S['PC1'] = dict(hit=bool(len(pc1) == 5 and all(x[3] for x in pc1) and all(np.diff(chain_inc) > 0)), rows=pc1)
S['PC2'] = dict(hit=bool(len(pc2) == 5 and all(x[3] for x in pc2)), rows=pc2)
S['PC3'] = dict(hit=bool(len(pc3) == 3 and all(x[3] for x in pc3)), rows=pc3)
S['PC4'] = dict(hit=bool(len(pc4) == 5 and all(x[3] for x in pc4)), rows=pc4)
S['PC5'] = dict(hit=bool(len(pc5) == 3 and all(x[4] for x in pc5)), rows=pc5)
S['PC6'] = dict(hit=bool(len(pc6) == 4 and all(x[4] for x in pc6)), rows=pc6)
json.dump(dict(scores=S, nets=out), open('/home/agent/workspaces/mats/work/gram-chain/results/partC_scores.json', 'w'), indent=1, default=float)
for k, v in S.items():
    print(k, v)
for n, r in out.items():
    print(n, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != 'VP'})
    print('   VP:', {t: (round(v['median'], 3), round(v['median_abs_dev_mf'], 3), round(v['spearman_Q'], 2)) for t, v in r['VP'].items()})
