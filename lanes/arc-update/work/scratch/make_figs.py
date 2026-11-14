"""Figures for the report (plain matplotlib defaults). figs/fig1_ladder.png: error vs cost at 256 x 32 for ARC variants,
the exact Gaussian recursion and the samplers (per net medians); figs/fig2_profiles.png: (a) attribution b_l^2 for ARC
K = 2 and the oracle Gaussian / radial-Gaussian single-cut defects by cut; (b) third-cumulant PR and covariance PR by
layer; (c) the gain ladder G_K along L = n/8."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RUNS = os.path.join(HERE, 'runs')
os.makedirs(os.path.join(HERE, 'figs'), exist_ok=True)
S256 = [s for s in range(200, 205) if os.path.exists(os.path.join(RUNS, f'rqmc_n256_L32_s{s}.json'))]
rows = SL.score({256: S256, 32: list(range(300, 308)), 64: list(range(300, 308)), 128: list(range(300, 308))})

# Figure 1: error vs cost at 256 x 32
fig, ax = plt.subplots(figsize=(6.4, 4.6))
Ns = np.logspace(0, 6, 50)
ax.loglog(Ns, 1.0 / Ns, 'k-', lw=1, label='plain MC (1/N)')
ax.loglog(Ns, 0.40 / Ns, 'k--', lw=1, label='Kerdock design (0.40/N, prior lane)')
rq = [json.load(open(os.path.join(RUNS, f'rqmc_n256_L32_s{s}.json'))) for s in S256]
if rq:
    Nr = [row['N'] for row in rq[0]['rows']]
    er = [np.median([r['rows'][i]['mean_nmse'] for r in rq]) for i in range(len(Nr))]
    ax.loglog(Nr, er, 'o-', color='C0', label='RQMC (scrambled Sobol), median')
for v, mk, c in (('k1', 's', 'C1'), ('k2', '^', 'C2'), ('k2a', 'v', 'C3'), ('k3f', 'D', 'C4'), ('k3', 'P', 'C5'),
                 ('k3fa', 'X', 'C6')):
    pts = [(r['passes'], r['nmse']) for (n, s, vv), r in rows.items() if n == 256 and vv == v]
    if pts:
        ax.loglog([np.median([p[0] for p in pts])], [np.median([p[1] for p in pts])], mk, color=c, ms=8,
                  label=f'ARC {v} (median of {len(pts)} nets)')
ex = []
for s in S256:
    p = os.path.join(RUNS, f'attr_s{s}.json')
    if os.path.exists(p):
        A = json.load(open(p)); m = A['models']['exact_gauss']
        ex.append((m['cost'] / (2.0 * 256 * 256 * 32), m['total']))
if ex:
    ax.loglog([np.median([e[0] for e in ex])], [np.median([e[1] for e in ex])], '*', color='C7', ms=12,
              label='exact Gaussian recursion (median)')
ax.axvline(6.5e4, color='gray', lw=0.8, ls=':')
ax.text(6.5e4 * 1.1, 2e-2, 'Phase-1 budget', rotation=90, color='gray', fontsize=8)
ax.set_xlabel('cost (forward passes at 256 x 32)'); ax.set_ylabel('nMSE (MC with N samples = 1/N)')
ax.set_title('256 x 32: deterministic estimators against samplers')
ax.legend(fontsize=7, loc='lower left')
fig.tight_layout(); fig.savefig(os.path.join(HERE, 'figs', 'fig1_cost_error_256x32.png'), dpi=140)

# Figure 2: profiles
fig, axs = plt.subplots(1, 3, figsize=(13, 4))
cuts = [1, 2, 4, 8, 16, 24, 28, 31]
for model, c, lab in (('arc_k2', 'C2', 'ARC K=2 past defect b_l^2'), ('oracle_gauss', 'C0', 'oracle Gaussian, single cut'),
                      ('oracle_radgauss', 'C3', 'oracle radial-Gaussian, single cut')):
    vals = []
    for s in S256:
        p = os.path.join(RUNS, f'attr_s{s}.json')
        if os.path.exists(p):
            A = json.load(open(p))
            vals.append([r['b2'] for r in A['models'][model]['rows']])
    if vals:
        med = np.median(np.array(vals), axis=0)
        axs[0].semilogy(cuts, np.maximum(med, 1e-7), 'o-', color=c, label=lab)
axs[0].set_xlabel('cut layer l'); axs[0].set_ylabel('nMSE'); axs[0].set_title('where the error is made (median)')
axs[0].legend(fontsize=7)
for s in S256:
    p = os.path.join(RUNS, f'rank_s{s}.json')
    if os.path.exists(p):
        R = json.load(open(p))
        ls = sorted(int(k) for k in R['layers'])
        axs[1].semilogy(ls, [R['layers'][str(l)]['pr'] for l in ls], 'o-', color='C4', alpha=0.7,
                        label='3rd-cumulant PR' if s == S256[0] else None)
        axs[1].semilogy(ls, [R['layers'][str(l)]['cov_pr'] for l in ls], 's--', color='C0', alpha=0.7,
                        label='covariance PR' if s == S256[0] else None)
axs[1].set_xlabel('layer l'); axs[1].set_ylabel('participation ratio'); axs[1].set_title('dimension of the structure')
axs[1].legend(fontsize=7)
ORD = {2: ('k2', 'k2a'), 3: ('k3', 'k3f', 'k3fa'), 4: ('k4', 'k4f')}
for K, c in ((2, 'C2'), (3, 'C4'), (4, 'C6')):
    xs, ys = [], []
    for n in (32, 64, 128, 256):
        best = []
        for v in ORD[K]:
            g = [r['gain_mc'] for (nn, s, vv), r in rows.items() if nn == n and vv == v]
            if g:
                best.append(np.median(g))
        if best:
            xs.append(n); ys.append(max(best))
    if xs:
        axs[2].loglog(xs, ys, 'o-', color=c, label=f'order K = {K}')
axs[2].axhline(1, color='k', lw=0.8)
axs[2].set_xticks([32, 64, 128, 256]); axs[2].set_xticklabels(['32', '64', '128', '256']); axs[2].minorticks_off()
axs[2].set_xlabel('width n (L = n/8)'); axs[2].set_ylabel('gain over MC at own cost')
axs[2].set_title('the price ladder'); axs[2].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(HERE, 'figs', 'fig2_profiles.png'), dpi=140)
# Figure 3: width scaling along L = n/8 (single-cut oracle defects, full ideal recursions, ARC K = 2)
fig, ax = plt.subplots(figsize=(6.4, 4.6))
SE = {32: range(300, 308), 64: range(300, 308), 128: range(300, 308), 256: range(200, 205)}
def wstat(key):
    xs, ys = [], []
    for n, seeds in SE.items():
        L = SL.CFG[n]; vals = []
        for s in seeds:
            p = os.path.join(RUNS, f'width_n{n}_L{L}_s{s}.json')
            if not os.path.exists(p):
                continue
            Rw = {r['l']: r for r in json.load(open(p))['rows']}
            mids = sorted({n // 32, n // 16, 3 * n // 32})
            vals.append(key(Rw, mids))
        if vals:
            xs.append(n); ys.append(np.median(vals))
    return xs, ys
for key, mk, c, lab in ((lambda R, m: R[1]['gauss'], 'o-', 'C0', 'single cut l = 1: oracle Gaussian'),
                        (lambda R, m: R[1]['radgauss'], 'o--', 'C3', 'single cut l = 1: oracle radial-Gaussian'),
                        (lambda R, m: np.mean([R[l]['radgauss'] for l in m]), 's--', 'C1',
                         'mid cuts (n/32, n/16, 3n/32): oracle radial-Gaussian')):
    xs, ys = wstat(key)
    if xs:
        ax.loglog(xs, np.maximum(ys, 1e-8), mk, color=c, label=lab)
for model, mk, c, lab in (('gauss', '^-', 'C0', 'full recursion: Gaussian projection (ideal)'),
                          ('radgauss', 'v-', 'C3', 'full recursion: radial-Gaussian projection (ideal)')):
    xs, ys = [], []
    for n, seeds in SE.items():
        L = SL.CFG[n]
        tag = 'ipr2'   # Amendment 6 (rank transport) at every width
        vals = [json.load(open(os.path.join(RUNS, f'{tag}_n{n}_L{L}_s{s}.json')))['models'][model]['b2']
                for s in seeds if os.path.exists(os.path.join(RUNS, f'{tag}_n{n}_L{L}_s{s}.json'))]
        if vals:
            xs.append(n); ys.append(np.median(vals))
    if xs:
        ax.loglog(xs, ys, mk, color=c, ms=7, label=lab)
for v, mk, c in (('k2', 'D:', 'C2'), ('k2a', 'P:', 'C5')):
    xs, ys = [], []
    for n in (32, 64, 128, 256):
        e = [r['nmse'] for (nn, s, vv), r in rows.items() if nn == n and vv == v]
        if e:
            xs.append(n); ys.append(np.median(e))
    if xs:
        ax.loglog(xs, ys, mk, color=c, label=f'ARC {v} (full)')
nn = np.array([32, 256.0])
ax.loglog(nn, 2e-2 / nn, 'k-', lw=0.6, label='slope -1')
ax.loglog(nn, 0.5 / nn ** 2, 'k--', lw=0.6, label='slope -2')
ax.set_xticks([32, 64, 128, 256]); ax.set_xticklabels(['32', '64', '128', '256']); ax.minorticks_off()
ax.set_xlabel('width n (depth L = n/8)'); ax.set_ylabel('nMSE (median over nets)')
ax.set_title('Width scaling of the closures\' errors')
ax.legend(fontsize=6.5, loc='lower left')
fig.tight_layout(); fig.savefig(os.path.join(HERE, 'figs', 'fig3_width_scaling.png'), dpi=140)
print('figures written')
