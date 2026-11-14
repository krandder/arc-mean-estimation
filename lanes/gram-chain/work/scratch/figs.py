"""Figures for the gram-chain report (plain matplotlib, the numerics lane's palette)."""
import sys, json, math, os
sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary-numerics/lib')
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import numpy as np
import plotstyle as ps
import matplotlib.pyplot as plt
import gc2
from scipy.special import gammaincc, gamma as G_

ps.setup()
R = '/home/agent/workspaces/mats/work/gram-chain/runs/'
F = '/home/agent/workspaces/mats/work/gram-chain/figs/'
A = json.load(open('/home/agent/workspaces/mats/work/gram-chain/results/partA_scores.json'))
AA = 2.2309204
beta = 0.4


def m_closed(x):
    return (24 * AA / 25) * beta ** (-2 / 3) * np.exp(beta / x) * gammaincc(2 / 3, beta / x) * G_(2 / 3)


# ---------- Fig 1: stationary law ----------
fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
ns = sorted(int(k) for k in A['r2'])
for i, n in enumerate(ns):
    f = R + 'A_r2_n%d.npz' % n
    z = np.load(f)
    r = z['delta'] / z['dstar']
    x = (r - 1) * n ** (1 / 3)
    h, e = np.histogram(x, bins=np.linspace(-4, 8, 81), density=True)
    ax[0].plot(0.5 * (e[1:] + e[:-1]), h, color=ps.seq(i, len(ns)), label='n = %d' % n)
ax[0].set_xlabel(r'$(\delta/\delta^*(Q) - 1)\, n^{1/3}$')
ax[0].set_ylabel('density')
ax[0].set_title('angle given the radius, rescaled')
ax[0].legend(fontsize=7)
sd = [A['r2'][str(n)]['sd_ell_n13'] for n in ns]
se = [A['r2'][str(n)]['sd_ell_n13_se'] for n in ns]
ax[1].errorbar(ns, sd, yerr=se, color=ps.CAT[0], marker='o', ms=4, label='exact chain')
ax[1].axhline(1.887, color=ps.CAT[1], ls='--', label='limit 1.887 (diffusion)')
ax[1].set_xscale('log', base=2)
ax[1].set_xlabel('width n')
ax[1].set_ylabel(r'SD$(\ell)\, n^{1/3}$')
ax[1].set_title('radius ratio between two replicas')
ax[1].legend(fontsize=7)
xs = np.logspace(-1.5, 1.5, 200)
ax[2].plot(xs, m_closed(xs), color=ps.CAT[1], ls='--', label='limit m(q) (closed form)')
for i, n in enumerate(ns):
    b = A['r2'][str(n)]['bins']
    qc = [math.sqrt(max(bb['lo'], 0.05) * min(bb['hi'], 40)) for bb in b]
    ax[2].plot(qc, [bb['E_ell2_n23'] for bb in b], color=ps.seq(i, len(ns)), marker='o', ms=3)
ax[2].set_xscale('log')
ax[2].set_xlabel('q = Q/n (bin centre)')
ax[2].set_ylabel(r'$E[\ell^2 \mid q]\, n^{2/3}$')
ax[2].set_title('radius ratio given the radius')
ax[2].legend(fontsize=7)
fig.tight_layout()
fig.savefig(F + 'fig1_stationary_law.png')
plt.close(fig)

# ---------- Fig 2: relevance curves ----------
pred = json.load(open('/home/agent/workspaces/mats/work/gram-chain/results/predB_meanfield.json'))
fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
k = 0
for n in (16, 64, 256, 1024):
    f = R + 'B_curves_n%d.json' % n
    if not os.path.exists(f):
        continue
    js = json.load(open(f))
    Tst = pred[str(n)]['Tstar_med']
    ts = np.array([r['t'] for r in js['rows']])
    col = ps.seq(k, 4)
    k += 1
    ax[0].plot((ts - 1) / Tst, [r['V_P'] for r in js['rows']], color=col, marker='o', ms=3, label='n = %d' % n)
    ax[1].plot((ts - 1) / Tst, [max(r['T_P'], 1e-4) for r in js['rows']], color=col, marker='o', ms=3, label='n = %d' % n)
    if n >= 64:  # n = 16: dead outputs (2^-16 per sample) make log|a| unusable
        ax[2].plot(ts / n, [r['V_P_log'] for r in js['rows']], color=col, marker='o', ms=3, label='n = %d' % n)
    rng_mf = np.random.default_rng(99)
    Qs = gc2.sample_Q_stationary(n, 2000, rng_mf)
    dsx = gc2.mf_fixed_point(Qs)
    den_mf = gc2.f_kernel(dsx).mean()
    dcl = np.zeros_like(Qs)
    vmf = []
    for tt in range(1, int(6 * Tst) + 2):
        vmf.append(1 - gc2.f_kernel(dcl).mean() / den_mf)
        dcl = (1 + Qs * gc2.f_kernel(dcl)) / (Qs + 1)
    ax[0].plot((np.arange(1, len(vmf) + 1) - 1) / Tst, vmf, color=col, ls=':', lw=1)
from scipy.integrate import solve_ivp
sol = solve_ivp(lambda s, y: [1 - max(y[0], 0) ** 1.5], (0, 8), [0.0], dense_output=True, rtol=1e-9)
ss = np.linspace(0, 6, 200)
ax[0].plot(ss, 1 - sol.sol(ss)[0], color=ps.CAT[1], ls='--', label='mean field 1 - Y, median radius')
ax[0].set_xlim(0, 5)
ax[0].set_xlabel('(t - 1)/T*,  T* = (Q+1) delta*(Q) at the median radius')
ax[0].set_ylabel('closed relevance V_P(t)')
ax[0].set_title('direction: closed relevance (dotted: radius-averaged MF)')
ax[0].legend(fontsize=7)
ax[1].plot(ss, (1 + ss / 2) ** -2, color=ps.CAT[1], ls='--', label='(1 + s/2)^-2')
ax[1].set_xscale('log')
ax[1].set_yscale('log')
ax[1].set_xlim(0.05, 300)
ax[1].set_xlabel('(t - 1)/T*')
ax[1].set_ylabel('total relevance T_P(t)')
ax[1].set_title('direction: total effect of the past')
ax[1].legend(fontsize=7)
ax[2].set_xscale('log')
ax[2].set_xlabel('t / n')
ax[2].set_ylabel('closed relevance, log|a|')
ax[2].set_title('amplitude (log|a|): memory ~ n layers')
ax[2].legend(fontsize=7)
fig.tight_layout()
fig.savefig(F + 'fig2_relevance.png')
plt.close(fig)

# ---------- Fig 3: dimension ----------
fig, ax = plt.subplots(1, 3, figsize=(13, 3.4))
n4 = sorted(int(k) for k in A['r4'])
pbr = json.load(open('/home/agent/workspaces/mats/work/gram-chain/results/pr_by_radius.json'))
kk = 0
for nk in sorted(pbr, key=int):
    rows = pbr[nk]
    col = ps.seq(kk, len(pbr))
    kk += 1
    ax[2].plot([r['q_median'] for r in rows], [r['PR'] for r in rows], color=col, marker='o', ms=3, label='n = %s' % nk)
    ax[2].plot([r['q_median'] for r in rows], [r['pred'] for r in rows], color=col, ls='--', lw=1)
ax[2].set_xscale('log')
ax[2].set_yscale('log')
ax[2].set_xlabel('q = Q/n (radius bin median)')
ax[2].set_ylabel('participation ratio')
ax[2].set_title('cloud dimension vs radius (dashed: n theta*/pi)')
ax[2].legend(fontsize=6)
ax[0].errorbar(n4, [A['r4'][str(n)]['PR_4rep'] for n in n4], yerr=[A['r4'][str(n)]['PR_4rep_se'] for n in n4],
               color=ps.CAT[0], marker='o', ms=4, label='exact chain, PR_w')
nn = np.array([16, 32, 64, 128, 256, 512, 1024, 2048])
H = np.array([sum(1 / k for k in range(2, m + 1)) for m in nn])
z2 = np.array([sum(1 / k ** 2 for k in range(2, m + 1)) for m in nn])
ax[0].plot(nn, H ** 2 / z2, color=ps.CAT[2], ls=':', label='1/k spectrum')
ax[0].plot(nn, 1.0865 * nn ** (2 / 3), color=ps.CAT[1], ls='--', label='1.0865 n^{2/3} (four-point balance)')
ax[0].set_xscale('log', base=2)
ax[0].set_yscale('log')
ax[0].set_xlabel('width n')
ax[0].set_ylabel('participation ratio of the direction cloud')
ax[0].set_title('how many directions the stationary cloud spans')
ax[0].legend(fontsize=7)
k = 0
for n in (16, 64, 256):
    f = R + 'B_pr_n%d.json' % n
    if not os.path.exists(f) or str(n) not in A['r4']:
        continue
    js = json.load(open(f))
    PRC = A['r4'][str(n)]['PR_4rep']
    ts = np.array([r['t'] for r in js['rows']])
    col = ps.seq(k, 3)
    k += 1
    ax[1].plot(ts, [r['PR_tot'] for r in js['rows']], color=col, marker='o', ms=3, label='total, n = %d' % n)
    ax[1].plot(ts, [r['PR_closed'] if (r['PR_closed'] and r['PR_closed_se'] < 0.3 * r['PR_closed']) else np.nan for r in js['rows']], color=col, marker='s', ms=3, ls=':',
               label='closed, n = %d' % n)
    tt = np.logspace(0, math.log10(ts.max()), 50)
    ax[1].plot(tt, 1 / (1 / PRC + 2 * tt / n), color=col, ls='--', lw=1)
ax[1].set_xscale('log')
ax[1].set_yscale('log')
ax[1].set_xlabel('t (layers to go)')
ax[1].set_ylabel('participation ratio at the output')
ax[1].set_title('relevant directions of layer L - t (dashed: free product; closed shown where SE < 30%)')
ax[1].legend(fontsize=6)
fig.tight_layout()
fig.savefig(F + 'fig3_dimension.png')
plt.close(fig)

# ---------- Fig 4: input regime ----------
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
th = json.load(open('/home/agent/workspaces/mats/work/gram-chain/results/theory_numbers.json'))
k = 0
for n, L in ((64, 64), (256, 128), (8, 256)):
    f = R + 'B_input_n%d_L%d_s0.json' % (n, L)
    if not os.path.exists(f):
        continue
    js = json.load(open(f))
    ls_ = np.array([r['l'] for r in js['rows']])
    col = ps.CAT[k]
    k += 1
    ax[0].plot(ls_[1:], [r['PR_4rep'] for r in js['rows']][1:], color=col, label='exact chain, n = %d' % n)
    rows = th['input_cloud_PR_over_n']
    ax[0].plot([r['l'] for r in rows if r['l'] <= L], [n * r['PR_over_n'] for r in rows if r['l'] <= L], color=col, ls='--', lw=1)
meas = {1: 159, 4: 57, 16: 17, 32: 9.6, 64: 6.1, 128: 3.6, 256: 1.9}
ax[0].plot(list(meas), list(meas.values()), 'k^', ms=5, label='input-bits nets, n = 256')
ax[0].set_xscale('log', base=2)
ax[0].set_yscale('log')
ax[0].set_xlabel('layer l')
ax[0].set_ylabel('angular participation ratio')
ax[0].set_title('input cloud dimension (dashed: vertex recursion)')
ax[0].legend(fontsize=7)
f = R + 'B_input_n256_L32_s0.json'
if os.path.exists(f):
    js = json.load(open(f))
    att = js['attribution']
    ax[1].plot([a['l'] for a in att], [a['V_logr'] / js['out_log_var'] for a in att], color=ps.CAT[0], marker='o', ms=3,
               label='exact chain, 256 x 32')

    def kap(c):
        return (math.sqrt(max(1 - c * c, 0)) + (math.pi - math.acos(c)) * c) / math.pi

    def Bf(c):
        t = math.acos(min(max(c, -1), 1))
        return 2 / math.pi * (3 * math.sin(t) * math.cos(t) + (math.pi - t) * (1 + 2 * math.cos(t) ** 2)) - 1
    c, C = 0.0, [0.0]
    for j in range(40):
        C.append(C[-1] + (5 - Bf(c)) / 4)
        c = kap(c)
    ax[1].plot(range(32), [(0.5 + C[l]) / (0.5 + C[32]) for l in range(32)], color=ps.CAT[1], ls='--', label='kernel (1/2 + C_l)/(1/2 + C_L)')
ax[1].set_xlabel('layer l')
ax[1].set_ylabel('share of Var(log|a|) carried by log|h_l|')
ax[1].set_title('what carries the input: radius vs direction')
ax[1].legend(fontsize=7)
fig.tight_layout()
fig.savefig(F + 'fig4_input.png')
plt.close(fig)
print('figures written')

# ---------- Fig 5: per-net scatter (Part C) ----------
import glob
files = sorted(glob.glob(R + 'C_n*_s5000_*.json'), key=lambda f: json.load(open(f))['n'])
if files:
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.4))
    for i, f in enumerate(files):
        js = json.load(open(f))
        n = js['n']
        col = ps.seq(i, len(files))
        qb = np.array([x['Qbar'] for x in js['nets']]) / n  # Qbar is Q; plot q = Q/n
        trc = np.array([x['trC_u'] for x in js['nets']])
        pr = np.array([x['PR_u'] for x in js['nets']])
        v8 = np.array([x['V_P'].get('8', np.nan) for x in js['nets']])
        rr = np.array([(x['logQa_var'] / 4) / (x['trC_a'] + x['logQa_var'] / 4) for x in js['nets']])
        ax[0].scatter(qb, trc * n ** (2 / 3), s=8, color=col, label='n = %d' % n)
        ax[1].scatter(qb, pr / n ** (2 / 3), s=8, color=col)
        if n >= 32:
            ax[2].scatter(qb, v8, s=8, color=col)
        ax[3].scatter(qb, rr, s=8, color=col)
    qq = np.logspace(-1.2, 1.5, 100)
    ax[0].plot(qq, AA * qq ** (-2 / 3), color=ps.CAT[1], ls='--', label='A q^-2/3')
    ax[1].plot(qq, 0.6724 * qq ** (-1 / 3), color=ps.CAT[1], ls='--', label='0.672 q^-1/3')
    ax[3].plot(qq, [m_closed(x) / (m_closed(x) + 2 * AA * x ** (-2 / 3)) for x in qq], color=ps.CAT[1], ls='--', label='rho(q)')
    for a_, yl, tl in ((ax[0], 'tr Var(u | W) n^{2/3}', 'cloud size per net'), (ax[1], 'PR(W) / n^{2/3}', 'cloud dimension per net'),
                       (ax[2], 'V_P(t = 8; W)', 'closed relevance at t = 8, per net'), (ax[3], 'radial share of output variance', 'radial share per net')):
        a_.set_xscale('log')
        a_.set_xlabel('net radius Qbar/n')
        a_.set_ylabel(yl)
        a_.set_title(tl)
    ax[0].set_yscale('log')
    ax[1].set_yscale('log')
    ax[0].legend(fontsize=6)
    ax[1].legend(fontsize=6)
    ax[3].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(F + 'fig5_per_net.png')
    plt.close(fig)
    print('fig5 written')
